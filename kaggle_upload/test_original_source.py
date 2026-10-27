"""Exercise real Workflow reload and save using unchanged student_114.json."""
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import runpy
import tempfile
from types import SimpleNamespace
import unittest


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = Path(os.environ.get('SINONOM_REPO_DIR', '/tmp/sinonom-inspect'))
HELPER = runpy.run_path(str(HERE / 'restore_in_kaggle.py'))
ENABLE = runpy.run_path(str(HERE / 'launch_with_original_source.py'))['enable_saved_content_sections']
Workflow = ENABLE(REPO)
from annotation.text_extraction import content_fields, content_document
from annotation.export import collect_content_documents


class OriginalSourceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.input = self.root / 'input'
        self.input.mkdir()
        self.source = self.input / 'student_114.json'
        self.original = (ROOT / 'student_114/student_114.json').read_bytes()
        self.source.write_bytes(self.original)
        (self.input / 'student_114_kaggle_restore.zip').write_bytes(
            (HERE / 'student_114_kaggle_restore.zip').read_bytes())
        with redirect_stdout(io.StringIO()):
            self.output = HELPER['restore_student_114'](
                input_root=self.input, output=self.root / 'annotations')
        self.options = SimpleNamespace(
            output_dir=self.output, source_json=self.source,
            content_titles=('Nguyên văn chữ Hán Nôm', 'Phiên âm Hán Việt', 'Toát yếu'),
            annotation_title='Nguyên văn chữ Hán Nôm',
            metadata_fields=(('Tên bia', 'ten_bia'), ('Địa điểm', 'dia_diem'), ('Niên đại', 'nien_dai')))
        self.engine = Workflow(self.options)
        self.addCleanup(self.engine._preview_cache.cleanup)
        self.saved = json.loads((self.output / '.state/content.json').read_text())

    def content(self, state):
        return content_document(state['image'], state['code'], state['draft_content'],
                                self.options.content_titles, self.options.metadata_fields)

    def test_all_nine_reload_content_without_changing_source_or_tool(self):
        tool = REPO / 'gradio/annotation/workflow.py'
        original_tool = tool.read_bytes()
        regions = 0
        for document in self.saved:
            state = self.engine.open_image(ROOT / 'student_114' / document['image'])
            self.assertEqual(self.content(state), document, document['image'])
            regions += len(state['regions'])
        self.assertEqual(regions, 1940)
        self.assertEqual(self.source.read_bytes(), self.original)
        self.assertEqual(tool.read_bytes(), original_tool)

    def test_new_toat_yeu_remains_editable_and_round_trips_through_review_save(self):
        image = ROOT / 'student_114/55432.png'
        state = self.engine.open_image(image)
        native_before = json.loads((self.output / '55432.json').read_text())
        field = next(field for field in content_fields(
            state['draft_content'], state['code'], self.options.content_titles)
                     if field['title'] == 'Toát yếu')
        text = 'Toát yếu sửa trên web: kiểm tra lưu vào Content, nguồn giữ nguyên.'
        state = self.engine.apply(state, 'field', {'path': field['path'], 'value': text})
        state = self.engine.apply(state, 'save_content')
        for _ in range(6):
            if state['current_step'] == 7:
                break
            state = self.engine.apply(state, 'next')
        self.assertEqual(state['current_step'], 7)
        state = self.engine.apply(state, 'save')
        self.assertTrue(state['saved'])
        reopened = self.engine.open_image(image)
        self.assertEqual(self.content(reopened)['content']['Toát yếu'], text)
        self.assertEqual(self.source.read_bytes(), self.original)
        self.assertEqual(json.loads((self.output / '55432.json').read_text()), native_before)
        exported = collect_content_documents([image], self.output)
        self.assertEqual(exported[0]['content']['Toát yếu'], text)

    def test_only_selected_face_is_extended(self):
        state = self.engine.open_image(ROOT / 'student_114/55432.png')
        records = json.loads(self.original)
        original_face = next(face for record in records for face in record['noi_dung']
                             if str(face['ky_hieu']) == '55431')
        other_face = next(face for face in state['draft_content']['noi_dung']
                          if str(face['ky_hieu']) == '55431')
        self.assertEqual(other_face, original_face)

    def test_null_phonetic_content_stays_absent(self):
        state = self.engine.open_image(ROOT / 'student_114/55431.png')
        self.assertIsNone(self.content(state)['content']['Phiên âm Hán Việt'])
        self.assertFalse(any(field['title'] == 'Phiên âm Hán Việt' for field in content_fields(
            state['draft_content'], state['code'], self.options.content_titles)))

    def test_no_registry_does_not_invent_sections(self):
        (self.output / '.state/content.json').unlink()
        records = json.loads(self.original)
        record = next(record for record in records if any(
            str(face['ky_hieu']) == '55432' for face in record['noi_dung']))
        restored = self.engine._saved_content_for('55432.png', '55432', record)
        self.assertEqual(restored, record)

    def test_launcher_uses_original_path_and_can_be_enabled_twice(self):
        with redirect_stdout(io.StringIO()):
            source, launcher = HELPER['prepare_original_source'](
                self.output, input_root=self.input)
        self.assertEqual(source, self.source)
        self.assertEqual(launcher.read_bytes(), (HERE / 'launch_with_original_source.py').read_bytes())
        before = Workflow._saved_content_for
        ENABLE(REPO)
        self.assertIs(Workflow._saved_content_for, before)
        self.assertEqual(self.source.read_bytes(), self.original)

    def test_source_selection_requires_unique_original_or_explicit_path(self):
        duplicate = self.input / 'copy/student_114.json'
        duplicate.parent.mkdir()
        duplicate.write_bytes(self.original)
        with self.assertRaisesRegex(RuntimeError, 'Expected one original'):
            HELPER['find_original_source'](self.input)
        self.assertEqual(HELPER['find_original_source'](self.input, self.source), self.source)


if __name__ == '__main__':
    unittest.main()
