"""Integration checks against the real app; damage inference is mocked."""
import io
import importlib
from copy import deepcopy
import json
import os
import runpy
import shutil
import sys
import tempfile
import zipfile
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = Path(__file__).resolve().parent / 'kaggle'
REPO = Path(os.environ.get('SINONOM_REPO_DIR', '/tmp/sinonom-status-inspect'))
sys.path[:0] = [str(REPO), str(REPO / 'gradio')]
runpy.run_path(str(PACKAGE / 'annotations/_support/content_base.py'))['enable_saved_content_sections'](REPO)
Workflow = runpy.run_path(str(PACKAGE / 'annotations/_support/launch_with_original_source.py'))['install_mixed_review'](REPO)
ui_fix = runpy.run_path(str(PACKAGE / 'annotations/_support/launch_with_original_source.py'))['enable_mixed_labels_ui']
ui_fix(REPO)
ui_fix(REPO)  # Idempotent across web restarts.
from ui import editor
importlib.reload(editor)
source = ROOT / 'student_114/student_114.json'
original_source = source.read_bytes()

with zipfile.ZipFile(PACKAGE.parent / 'input/user_seven_annotations.zip') as z:
    saved = {}
    for name, folder in [('text_annotations.json', ''), ('source_mismatches.json', 'source_mismatches')]:
        for doc in json.loads(z.read(name)):
            saved[str(Path(folder) / (Path(doc['image']).stem + '.json'))] = doc
    saved_content = {d['image']: d for d in json.loads(z.read('inscription_content.json'))}

with tempfile.TemporaryDirectory() as temp:
    temp = Path(temp)
    staged = temp / 'input'
    shutil.copytree(PACKAGE, staged)
    shutil.rmtree(staged / 'annotations/.state')  # Kaggle may omit hidden paths.
    shutil.rmtree(staged / 'annotations/_support')  # Root support-code fallback.
    job = runpy.run_path(str(staged / 'apply_last_two.py'))
    output = temp / 'annotations'

    def predict(repo, images):
        assert {p.stem for p in images} == {'17077', '18592'}
        return {p.stem: [json.loads((staged / 'annotations/model_reviews' / (p.stem + '.json')).read_text())['bounding_boxes']['1']['bbox']] for p in images}

    with redirect_stdout(io.StringIO()):
        job['apply'](REPO, ROOT / 'student_114', output, predict=predict)
    for name, doc in saved.items():
        assert json.loads((output / name).read_text()) == doc, name
    assert not (output / 'model_reviews/55431.json').exists(), 'Never attach a stale sidecar to newly edited boxes.'
    content = {d['image']: d for d in json.loads((output / '.state/content.json').read_text())}
    assert len(content) == 9
    assert all(content[name] == record for name, record in saved_content.items())
    opts = SimpleNamespace(output_dir=output, source_json=source,
        content_titles=('Nguyên văn chữ Hán Nôm', 'Phiên âm Hán Việt', 'Toát yếu'),
        annotation_title='Nguyên văn chữ Hán Nôm', skip_detection=True,
        metadata_fields=(('Tên bia', 'ten_bia'), ('Địa điểm', 'dia_diem'), ('Niên đại', 'nien_dai')))
    engine = Workflow(opts)
    for code in ('17077', '18592'):
        full = json.loads((output / 'model_reviews' / (code + '.json')).read_text())
        seed = json.loads((staged / 'annotations/model_reviews' / (code + '.json')).read_text())
        assert full['bounding_boxes']['1']['status'] == 'damaged'
        assert full['bounding_boxes']['2']['status'] == 'intact'
        assert full['annotations'] == seed['annotations']
        if code == '18592':
            assert full['annotations']['184'] == '月'
            assert full['bounding_boxes']['184']['suspicious'] is True
            assert full['excluded_characters'] == []
            assert len(full['unassigned_source_characters']) == 36
            assert 'MISS' not in full['annotations'].values()
        assert {k: b['bbox'] for k, b in full['bounding_boxes'].items()} == {k: b['bbox'] for k, b in seed['bounding_boxes'].items()}
        assert not (output / (code + '.json')).exists()
        state = engine.open_image(ROOT / 'student_114' / full['image'])
        assert state['annotations'] == full['annotations']
        state = engine.apply(state, 'next')
        assert state['annotations'] == full['annotations']
        state = engine.apply(state, 'next')
        assert state['current_step'] == 4
        assert state['annotations'] == full['annotations']
        before_render = deepcopy(state)
        markup = editor.snapshot(state)['markup']
        assert markup.count('data-box-order-label="1"') == len(full['annotations'])
        assert '>1 ' + full['annotations']['1'] + '</text>' in markup
        assert 'stroke="#ef4444"' in markup  # Model-damaged box is visible.
        assert state == before_render, 'Rendering must not change labels or mismatch type.'
        # Other without restored labels retains the app's coordinate-only display.
        bare = deepcopy(state)
        bare['annotations'] = {}
        bare['text_sequence'] = []
        assert 'data-box-order-label="1"' not in editor.snapshot(bare)['markup']
        # Saving/reopening Other must retain the companion labels and geometry.
        state['current_step'] = 7
        with redirect_stdout(io.StringIO()):
            state = engine.apply(state, 'save')
        reopened = engine.open_image(ROOT / 'student_114' / full['image'])
        reopened = engine.apply(reopened, 'next')
        reopened = engine.apply(reopened, 'next')
        assert reopened['current_step'] == 4
        assert reopened['annotations'] == full['annotations']
        assert editor.snapshot(reopened)['markup'].count('data-box-order-label="1"') == len(full['annotations'])
    engine._preview_cache.cleanup()
    # Upgrade a v3 sidecar without rerunning the model or replacing any boxes.
    sidecar = output / 'model_reviews/18592.json'
    native = output / 'source_mismatches/18592.json'
    legacy = json.loads(sidecar.read_text())
    legacy['annotations']['184'] = 'MISS'
    legacy['bounding_boxes']['184']['suspicious'] = False
    legacy['excluded_characters'] = legacy.pop('unassigned_source_characters') + ['月']
    sidecar.write_text(json.dumps(legacy))
    current_native = json.loads(native.read_text())
    current_native['note'] = 'old draft note'
    native.write_text(json.dumps(current_native))
    protected = {p: p.read_bytes() for p in output.rglob('*') if p.is_file()
                 and p not in (sidecar, native, output / '.state/source_mismatches/18592.json')}
    patch = runpy.run_path(str(PACKAGE / 'fix_18592.py'))
    with redirect_stdout(io.StringIO()):
        patch['fix_18592'](output)
    updated = json.loads(sidecar.read_text())
    assert updated['annotations']['184'] == '月'
    assert updated['bounding_boxes']['184']['suspicious']
    assert updated['excluded_characters'] == []
    for key, box in legacy['bounding_boxes'].items():
        for field in ('bbox', 'status', 'damage_level', 'order'):
            assert updated['bounding_boxes'][key].get(field) == box.get(field)
    assert all(path.read_bytes() == value for path, value in protected.items())
    with zipfile.ZipFile(output.parent / 'my_annotations_backup.zip') as z:
        assert z.testzip() is None
        assert len(json.loads(z.read('user_work_manifest.json'))['images']) == 9

    # A newer manual edit to any of the seven stays byte-for-byte unchanged.
    changed = output / 'source_mismatches/46303.json'
    doc = json.loads(changed.read_text())
    doc['bounding_boxes']['1']['bbox'][0] += 2
    changed.write_text(json.dumps(doc))
    snapshot = {name: (output / name).read_bytes() for name in saved}
    with redirect_stdout(io.StringIO()):
        job['apply'](REPO, ROOT / 'student_114', output, predict=predict)
    assert snapshot == {name: (output / name).read_bytes() for name in saved}

    # New manual geometry on a target image blocks replacement before inference.
    target = output / 'source_mismatches/18592.json'
    doc = json.loads(target.read_text())
    doc['bounding_boxes']['1']['bbox'][0] += 1
    target.write_text(json.dumps(doc))
    snapshot = {p.relative_to(output): p.read_bytes() for p in output.rglob('*') if p.is_file()}
    try:
        job['apply'](REPO, ROOT / 'student_114', output, predict=lambda *_: (_ for _ in ()).throw(AssertionError('Inference must not run')))
    except ValueError as error:
        assert 'Có box mới' in str(error)
    else:
        raise AssertionError('New manual geometry was overwritten')
    assert snapshot == {p.relative_to(output): p.read_bytes() for p in output.rglob('*') if p.is_file()}
assert source.read_bytes() == original_source
print('PASS: fresh nine-image restore, latest seven and newer edits preserved, real Workflow reload/alignment, fixed geometry, backup, overwrite guard. Damage inference MOCKED.')
