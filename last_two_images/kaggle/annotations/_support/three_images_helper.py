"""Read manual boxes, run only damage inference, and merge into existing work."""
from collections import Counter
from contextlib import contextmanager
import argparse
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
import zipfile

BRACKETS = '[]{}()［］｛｝（）〈〉《》'
TARGETS = ('55431', '46303', '46302')


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def semantic(value):
    return digest(json.dumps(value, ensure_ascii=False, sort_keys=True).encode())


def normalize(value):
    if not isinstance(value, str):
        return value
    return re.sub(r'\[\s*\]|［\s*］', '□', value).translate(str.maketrans('', '', BRACKETS))


def atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.pending')
    try:
        temporary.write_bytes(data)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


@contextmanager
def transaction(paths):
    before = {p: p.read_bytes() if p.is_file() else None for p in paths}
    try:
        yield
    except Exception:
        for path, data in before.items():
            if data is None:
                path.unlink(missing_ok=True)
            else:
                atomic(path, data)
        raise


def support_payload(root):
    return {'_support/' + name: (root / name).read_bytes() for name in (
        'content_base.py', 'launch_with_original_source.py', 'three_images_helper.py')}


def backup_my_work(output='/kaggle/working/annotations', archive=None):
    """Full progress backup, including mixed-source labels and model results."""
    output = Path(output)
    archive = Path(archive) if archive else output.parent / 'my_annotations_backup.zip'
    payload = {p.relative_to(output).as_posix(): p.read_bytes()
               for p in output.rglob('*') if p.is_file()
               and p.suffix.lower() != '.zip' and '.pending' not in p.name
               and '__pycache__' not in p.parts}
    if '.state/content.json' not in payload:
        raise ValueError('Chưa có Content đã lưu để sao lưu.')
    images = []
    for folder in (output, output / 'source_mismatches'):
        for path in folder.glob('*.json'):
            if path.stem.isdecimal():
                images.append(json.loads(path.read_text(encoding='utf-8'))['image'])
    if len(images) != len(set(images)):
        raise ValueError('Một ảnh có cả JSON normal và mismatch.')
    manifest = dict(version=2, images=sorted(images),
                    original_source_unchanged=True,
                    files={name: dict(sha256=digest(data)) for name, data in payload.items()})
    restore_source = '''from pathlib import Path
import runpy

def restore_my_work(input_root, output='/kaggle/working/annotations'):
    root=Path(input_root)
    helper=runpy.run_path(str(root/'annotations/_support/three_images_helper.py'))
    return helper['restore_backup'](root, output)

def backup_my_work(output='/kaggle/working/annotations', archive=None):
    helper=runpy.run_path(str(Path(output)/'_support/three_images_helper.py'))
    return helper['backup_my_work'](output, archive)
'''
    pending = archive.with_suffix('.pending.zip')
    with zipfile.ZipFile(pending, 'w', zipfile.ZIP_DEFLATED) as bundle:
        for name, data in payload.items():
            bundle.writestr('annotations/' + name, data)
        bundle.writestr('user_work_manifest.json', encoded(manifest))
        bundle.writestr('inscription_content.json', payload['.state/content.json'])
        bundle.writestr('restore_my_work.py', restore_source)
    with zipfile.ZipFile(pending) as bundle:
        if bundle.testzip() is not None:
            raise ValueError('Backup ZIP verification failed.')
    pending.replace(archive)
    print('Backup:', archive, '|', len(images), 'ảnh', flush=True)
    return archive


def restore_backup(root, output='/kaggle/working/annotations'):
    """Merge a folder backup without deleting or replacing newer saved images."""
    root, output = Path(root), Path(output)
    manifest = json.loads((root / 'user_work_manifest.json').read_text(encoding='utf-8'))
    payload = {}
    for name, info in manifest['files'].items():
        path = PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts or '\\' in name:
            raise ValueError('Unsafe backup path.')
        source = root / 'annotations' / name
        if name == '.state/content.json' and not source.is_file():
            source = root / 'inscription_content.json'
        data = source.read_bytes()
        if digest(data) != info['sha256']:
            raise ValueError('Backup checksum failed: ' + name)
        payload[name] = data
    registry = output / '.state/content.json'
    existing = json.loads(registry.read_text()) if registry.is_file() else []
    records = {r['image']: r for r in json.loads(payload['.state/content.json'])}
    records.update({r['image']: r for r in existing})
    for name, data in payload.items():
        if name == '.state/content.json':
            continue
        target = output / name
        # Do not introduce a stale normal/mismatch companion for a current image.
        is_native = (len(Path(name).parts) == 1 or (
            len(Path(name).parts) == 2 and Path(name).parts[0] == 'source_mismatches'))
        if Path(name).stem.isdecimal() and is_native:
            stem = Path(name).stem
            if (output / (stem + '.json')).exists() or (output / 'source_mismatches' / (stem + '.json')).exists():
                continue
        if name.startswith('model_reviews/') and Path(name).stem.isdecimal():
            stem = Path(name).stem
            for native_name in (stem + '.json', 'source_mismatches/' + stem + '.json'):
                native = output / native_name
                if native.is_file() and payload.get(native_name) != native.read_bytes():
                    break
            else:
                native = None
            if native is not None:
                continue
        if name.startswith('.state/') and name.endswith('.json') and Path(name).stem.isdecimal():
            native = output / name.removeprefix('.state/')
            backup_native = payload.get(name.removeprefix('.state/'))
            if native.is_file() and backup_native != native.read_bytes():
                continue
        if not target.exists():
            atomic(target, data)
    atomic(registry, encoded(list(records.values())))
    return output


def predict_damage(repo, images):
    """Same damage model and preprocessing as the app; no OCR box detection."""
    from PIL import Image, ImageOps
    import numpy as np
    import torch
    from mmdet.apis import init_detector, inference_detector
    from text_detection.pipeline import _damage_boxes_from_prediction
    config = repo / 'text_detection/models/ckpts/damage_detect.py'
    weights = repo / 'text_detection/models/ckpts/damage_detect.pth'
    for asset in (config, weights):
        if not asset.is_file():
            raise FileNotFoundError(asset)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print('Model:', device, flush=True)
    model = init_detector(str(config), str(weights), device=device, palette='random')
    results = {}
    try:
        with tempfile.TemporaryDirectory() as temporary:
            for image in images:
                print('Đánh giá Intact/Damaged:', image.name, flush=True)
                prepared = Path(temporary) / 'inverted.jpg'
                with Image.open(image) as opened:
                    ImageOps.invert(opened.convert('RGB')).save(prepared)
                with Image.open(prepared) as opened:
                    pixels = np.array(opened.convert('L').convert('RGB'))
                with torch.inference_mode():
                    prediction = inference_detector(model, pixels)
                results[image.stem] = _damage_boxes_from_prediction(prediction, score_threshold=0.3)
    finally:
        del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    return results


def process(input_root, repo_dir, image_dir, output='/kaggle/working/annotations'):
    root, repo, image_dir, output = map(Path, (input_root, repo_dir, image_dir, output))
    sys.path[:0] = [str(repo), str(repo / 'gradio')]
    from PIL import Image
    from annotation.io import validate_source_mismatch_document
    from annotation.text_alignment import characters
    from text_detection.fusion import fuse_localizations
    manifest = json.loads((root / 'three_images_manifest.json').read_text())
    for name, info in manifest['files'].items():
        if digest((root / name).read_bytes()) != info['sha256']:
            raise ValueError('Input checksum failed: ' + name)
    inputs = [json.loads((root / 'data' / (code + '.json')).read_text()) for code in TARGETS]
    signature = semantic(inputs)
    images = []
    for item in inputs:
        image = image_dir / item['image']
        with Image.open(image) as opened:
            rgb = opened.convert('RGB')
            if list(rgb.size) != item['image_size'] or digest(rgb.tobytes()) != item['image_pixel_sha256']:
                raise ValueError('Ảnh khác ảnh dùng để vẽ box: ' + str(image))
        images.append(image)
    marker_path = output / '.state/three_images_job.json'
    marker = json.loads(marker_path.read_text()) if marker_path.is_file() else {}
    native_paths = [output / 'source_mismatches' / (code + '.json') for code in TARGETS]
    if marker.get('data_signature') == signature and all(path.is_file() for path in native_paths):
        for name, data in support_payload(root).items():
            atomic(output / name, data)
        print('Đã có ba bài; giữ nguyên các chỉnh sửa hiện tại.', flush=True)
        backup_my_work(output)
        return output
    native_before = {}
    for code in TARGETS:
        present = [p for p in (output / (code + '.json'), output / 'source_mismatches' / (code + '.json')) if p.exists()]
        if present:
            if len(present) != 1 or semantic(json.loads(present[0].read_text())) not in manifest['replaceable_assistant_drafts'].get(code, []):
                raise ValueError('Đã có bài khác/chỉnh sửa mới cho ' + code + '; không ghi đè.')
        for path in (output / (code + '.json'), output / 'source_mismatches' / (code + '.json')):
            native_before[path] = path.read_bytes() if path.is_file() else None
    registry = output / '.state/content.json'
    registry_before = registry.read_bytes() if registry.is_file() else None
    own_payload = {}
    own_records = {r['image']: r for r in json.loads((root / 'inscription_content.json').read_text())}
    for path in (root / 'existing_user_annotations').rglob('*.json'):
        relative = path.relative_to(root / 'existing_user_annotations').as_posix()
        stem = path.stem
        if not (output / (stem + '.json')).exists() and not (output / 'source_mismatches' / (stem + '.json')).exists():
            own_payload[relative] = path.read_bytes()
            for target in (output / (stem + '.json'), output / 'source_mismatches' / (stem + '.json')):
                native_before[target] = None
    if registry_before is not None:
        own_records.update({r['image']: r for r in json.loads(registry_before)})
    normalized = []
    for record in own_records.values():
        record = copy.deepcopy(record)
        if Path(record['image']).stem in {'17390', '18591', '31962', '55432', *TARGETS}:
            record['content'] = {name: normalize(value) for name, value in record['content'].items()}
        normalized.append(record)
    new_content = {r['image']: r for r in normalized}
    predictions = predict_damage(repo, images)
    payload = dict(own_payload)
    report = []
    for item in inputs:
        code, image = item['inscription_code'], item['image']
        source = new_content[image]['content']['Nguyên văn chữ Hán Nôm']
        labels = list(item['annotations'].values())
        expected = [c for c in characters(source) if c not in item['excluded_characters']]
        if [c for c in labels if c != 'MISS'] != expected:
            raise ValueError('Source/label alignment mismatch: ' + code)
        fixed = [box['bbox'] for box in item['bounding_boxes'].values()]
        _, _, damaged = fuse_localizations(predictions[code], fixed)
        boxes = copy.deepcopy(item['bounding_boxes'])
        for index, (key, box) in enumerate(boxes.items()):
            unknown = item['annotations'][key] == '□'
            box.update(status='damaged' if unknown or index in damaged else 'intact',
                       damage_level=3 if unknown else None, unknown=unknown, order=int(key))
            if item['annotations'][key] == 'MISS':
                for flag in ('unknown', 'unavailable_font', 'expert_prediction', 'suspicious'):
                    box[flag] = False
        full = dict(image=image, inscription_code=code, source_text=source,
                    image_pixel_sha256=item['image_pixel_sha256'],
                    bounding_boxes=boxes, annotations=copy.deepcopy(item['annotations']),
                    excluded_characters=item['excluded_characters'],
                    reading_order=item['reading_order'],
                    crop=item['crop'], image_resize=item['image_resize'])
        if code == '46302':
            note='Đồng thời thiếu 蓋 (MISS #35) và dư 〇, chú thích 1. Nhãn/trạng thái đầy đủ lưu kèm model_reviews/46302.json.'
            native = dict(image=image, inscription_code=code, issue_type=['other'], note=note,
                          bounding_boxes={key:dict(bbox=box['bbox']) for key, box in boxes.items()})
        else:
            kind = 'missing_text' if code == '55431' else 'extra_text'
            native = dict(image=image, inscription_code=code, issue_type=[kind], note=(
                'MISS #131: ảnh có 祭, nguồn không có.' if code == '55431' else 'Dấu 〇 không khắc trên ảnh; đưa vào Excluded.'),
                source_text=source, source_character_count=len(characters(source)),
                bounding_box_count=len(boxes), bounding_boxes=boxes, annotations=full['annotations'],
                crop=item['crop'], image_resize=item['image_resize'])
            if kind == 'extra_text':
                native.update(text_sequence=labels + item['excluded_characters'], excluded_characters=item['excluded_characters'])
        validate_source_mismatch_document(native, image, item['image_size'])
        assert [box['bbox'] for box in native['bounding_boxes'].values()] == fixed
        payload['source_mismatches/' + code + '.json'] = encoded(native)
        payload['model_reviews/' + code + '.json'] = encoded(full)
        report.append(dict(image=image, boxes=len(boxes),
                           statuses=dict(Counter(box['status'] for box in boxes.values())),
                           missing=item['missing_box_ids'], excluded=item['excluded_characters']))
    if (registry.read_bytes() if registry.is_file() else None) != registry_before:
        raise ValueError('Content đã đổi trong lúc model chạy; không ghi đè. Chạy lại khi web đã dừng.')
    if any((path.read_bytes() if path.is_file() else None) != data for path, data in native_before.items()):
        raise ValueError('Bài làm đã đổi trong lúc model chạy; không ghi đè. Chạy lại khi web đã dừng.')
    payload['.state/content.json'] = encoded(normalized)
    payload.update(support_payload(root))
    payload['.state/three_images_job.json'] = encoded(dict(data_signature=signature,
        status_source='app_damage_model', report=report,
        damage_levels_require_review=True, original_source_unchanged=True))
    paths = [output / name for name in payload]
    with transaction(paths):
        for name, data in payload.items():
            atomic(output / name, data)
    for code in TARGETS:
        # Generated files deliberately omit old Review fingerprints.
        (output / '.state/source_mismatches' / (code + '.json')).unlink(missing_ok=True)
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
    backup_my_work(output)
    return output


def prepare(input_root, repo_dir, image_dir, output='/kaggle/working/annotations', python=None):
    subprocess.run([str(python or sys.executable), '-u', str(Path(__file__).resolve()),
                    '--input-root', str(input_root), '--repo', str(repo_dir),
                    '--images', str(image_dir), '--output', str(output)],
                   cwd=repo_dir, check=True)
    return Path(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-root', type=Path, required=True)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--images', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('/kaggle/working/annotations'))
    args = parser.parse_args()
    process(args.input_root, args.repo, args.images, args.output)
