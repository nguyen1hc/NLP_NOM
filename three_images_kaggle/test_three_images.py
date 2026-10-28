"""Use the upstream Workflow; inference is mocked because weights are on Kaggle."""
from contextlib import redirect_stdout
from copy import deepcopy
import importlib.util
import io
import json
import os
from pathlib import Path
import runpy
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = Path(os.environ.get('SINONOM_REPO_DIR', '/tmp/sinonom-status-inspect'))
sys.path[:0] = [str(REPO), str(REPO / 'gradio')]
spec = importlib.util.spec_from_file_location('three_helper', HERE / 'three_images_helper.py')
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
runpy.run_path(str(HERE / 'content_base.py'))['enable_saved_content_sections'](REPO)
Workflow = runpy.run_path(str(HERE / 'launch_with_original_source.py'))['install_mixed_review'](REPO)
from annotation.state import source_mismatch_confirmed
from annotation.text_extraction import content_document


class ThreeImageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.output = self.base / 'annotations'
        self.source = ROOT / 'student_114/student_114.json'
        self.original_source = self.source.read_bytes()
        self.inputs = {code: json.loads((HERE / 'data' / (code + '.json')).read_text())
                       for code in helper.TARGETS}
        self.damage = {code: [row['bounding_boxes']['1']['bbox']] for code, row in self.inputs.items()}

    def process(self):
        with patch.object(helper, 'predict_damage', return_value=self.damage) as model, redirect_stdout(io.StringIO()):
            helper.process(HERE, REPO, ROOT / 'student_114', self.output)
        return model

    def engine(self):
        options = SimpleNamespace(output_dir=self.output, source_json=self.source,
            content_titles=('Nguyên văn chữ Hán Nôm', 'Phiên âm Hán Việt', 'Toát yếu'),
            annotation_title='Nguyên văn chữ Hán Nôm', skip_detection=True,
            metadata_fields=(('Tên bia','ten_bia'), ('Địa điểm','dia_diem'), ('Niên đại','nien_dai')))
        engine = Workflow(options)
        self.addCleanup(engine._preview_cache.cleanup)
        return engine

    def snapshot(self):
        return {str(p.relative_to(self.output)): p.read_bytes()
                for p in self.output.rglob('*') if p.is_file()}

    def test_real_workflow_loads_all_seven_with_exact_geometry_and_labels(self):
        self.process()
        engine = self.engine()
        count = 0
        for document in json.loads((self.output / '.state/content.json').read_text()):
            state = engine.open_image(ROOT / 'student_114' / document['image'])
            actual = content_document(state['image'], state['code'], state['draft_content'],
                                      engine.content_titles, engine.metadata_fields)
            expected_content = deepcopy(document)
            # Current upstream completes absent optional fields as empty strings.
            expected_content['content'] = {k: ('' if v is None else v)
                                           for k, v in expected_content['content'].items()}
            self.assertEqual(actual, expected_content)
            count += len(state['regions'])
            code = Path(document['image']).stem
            if code in self.inputs:
                expected = self.inputs[code]
                self.assertEqual(state['annotations'], expected['annotations'])
                self.assertEqual([b['bbox'] for b in state['bounding_boxes'].values()],
                                 [b['bbox'] for b in expected['bounding_boxes'].values()])
                self.assertEqual(state['bounding_boxes']['1']['status'], 'damaged')
                state = engine.apply(state, 'next')
                self.assertTrue(source_mismatch_confirmed(state))
                self.assertEqual(state['annotations'], expected['annotations'])
                self.assertEqual(state['bounding_boxes']['1']['status'], 'damaged')
                state = engine.apply(state, 'next')
                self.assertEqual(state['current_step'], 4)
        self.assertEqual(count, 1427)
        self.assertEqual(self.source.read_bytes(), self.original_source)

    def test_original_four_native_objects_unchanged_and_existing_edits_preserved(self):
        self.process()
        for p in (HERE / 'existing_user_annotations').rglob('*.json'):
            self.assertEqual(json.loads((self.output / p.relative_to(HERE / 'existing_user_annotations')).read_text()),
                             json.loads(p.read_text()))
        own = self.output / 'source_mismatches/17390.json'
        value = json.loads(own.read_text()); value['note'] = 'Newer user edit'
        own.write_bytes(helper.encoded(value)); before = own.read_bytes()
        (self.output / '.state/three_images_job.json').unlink()
        for code in helper.TARGETS:
            (self.output / 'source_mismatches' / (code + '.json')).unlink()
        self.process()
        self.assertEqual(own.read_bytes(), before)

    def test_repeated_run_does_not_run_model_or_overwrite_user_status(self):
        self.process()
        p = self.output / 'source_mismatches/55431.json'
        value = json.loads(p.read_text()); value['note'] = 'Manually reviewed'
        p.write_bytes(helper.encoded(value)); before = p.read_bytes()
        model = self.process()
        model.assert_not_called()
        self.assertEqual(p.read_bytes(), before)

    def test_unknown_existing_annotation_is_not_overwritten(self):
        p = self.output / 'source_mismatches/55431.json'
        p.parent.mkdir(parents=True)
        p.write_text('{"note":"User unfinished saved work"}')
        before = self.snapshot()
        with patch.object(helper, 'predict_damage') as model:
            with self.assertRaisesRegex(ValueError, 'không ghi đè'):
                helper.process(HERE, REPO, ROOT / 'student_114', self.output)
            model.assert_not_called()
        self.assertEqual(self.snapshot(), before)

    def test_model_failure_has_no_partial_outputs(self):
        with patch.object(helper, 'predict_damage', side_effect=RuntimeError('model unavailable')):
            with self.assertRaisesRegex(RuntimeError, 'model unavailable'):
                helper.process(HERE, REPO, ROOT / 'student_114', self.output)
        self.assertFalse(self.output.exists())

    def test_mixed_review_save_and_backup_reopen_preserve_status_labels_and_order(self):
        self.process(); engine = self.engine()
        state = engine.open_image(ROOT / 'student_114/46302.png')
        state = engine.apply(state, 'next')
        state = engine.apply(state, 'next')
        self.assertEqual(state['current_step'], 4)
        with self.assertRaisesRegex(ValueError, 'damage level'):
            engine.apply(state, 'next')
        for uid, box in state['regions'].items():
            if box['status'] == 'damaged' and box['damage_level'] is None:
                box['damage_level'] = 2  # Test input, not a model-generated severity.
                state['bounding_boxes'][state['box_id_by_region'][uid]]['damage_level'] = 2
        while state['current_step'] != 7:
            state = engine.apply(state, 'next')
        before = deepcopy(state['bounding_boxes'])
        with redirect_stdout(io.StringIO()):
            engine.apply(state, 'save')
        reopened = engine.open_image(ROOT / 'student_114/46302.png')
        self.assertEqual(reopened['annotations'], self.inputs['46302']['annotations'])
        self.assertEqual(reopened['bounding_boxes'], before)
        reopened = engine.apply(reopened, 'next')
        self.assertEqual(reopened['bounding_boxes'], before)
        with zipfile.ZipFile(self.base / 'my_annotations_backup.zip') as bundle:
            self.assertIsNone(bundle.testzip())
            bundle.extractall(self.base / 'backup_input')
        manifest_path = self.base / 'backup_input/user_work_manifest.json'
        manifest = json.loads(manifest_path.read_text())
        manifest['files'] = dict(sorted(manifest['files'].items()))
        manifest_path.write_bytes(helper.encoded(manifest))
        # Kaggle may hide dotfiles in an unpacked Dataset: visible fallback.
        (self.base / 'backup_input/annotations/.state/content.json').unlink()
        new_output = self.base / 'restored'
        helper.restore_backup(self.base / 'backup_input', new_output)
        self.output = new_output
        restored = self.engine().open_image(ROOT / 'student_114/46302.png')
        self.assertEqual(restored['annotations'], self.inputs['46302']['annotations'])
        self.assertEqual(restored['bounding_boxes'], before)
        self.assertEqual(self.source.read_bytes(), self.original_source)

    def test_image_mismatch_is_rejected_before_model_runs(self):
        images = self.base / 'wrong_images'; images.mkdir()
        from PIL import Image
        Image.new('RGB', (1056, 1483)).save(images / '55431.png')
        with patch.object(helper, 'predict_damage') as model:
            with self.assertRaisesRegex(ValueError, 'Ảnh khác'):
                helper.process(HERE, REPO, images, self.output)
            model.assert_not_called()
        self.assertFalse(self.output.exists())

    def test_normalization_preserves_letters_and_existing_unknowns(self):
        self.assertEqual(helper.normalize('甲[]乙[ ]丙(丁){戊}[己]□'), '甲□乙□丙丁戊己□')
        for row in json.loads((HERE / 'inscription_content.json').read_text()):
            for text in row['content'].values():
                if isinstance(text, str):
                    self.assertFalse(set(text) & set(helper.BRACKETS))


if __name__ == '__main__':
    unittest.main()
