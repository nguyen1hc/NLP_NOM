"""Restore the user's Download All export without inventing absent Other labels."""
from pathlib import Path
from datetime import datetime, timezone
import json
import hashlib
import shutil
import tempfile
import zipfile


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def geometry(doc):
    return sorted(tuple(b['bbox']) for b in doc['bounding_boxes'].values())


def backup(output, archive):
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted(output.rglob('*')):
            if p.is_file() and p.suffix != '.zip' and '__pycache__' not in p.parts:
                z.write(p, 'annotations/' + p.relative_to(output).as_posix())
    return archive


def restore_latest_work(root, output='/kaggle/working/annotations'):
    root, output = Path(root), Path(output)
    incoming = {}
    for file, folder in [('text_annotations.json', ''), ('source_mismatches.json', 'source_mismatches')]:
        for doc in read(root / 'payload' / file):
            code = Path(doc['image']).stem
            if not code.isdecimal() or code in incoming:
                raise ValueError('Invalid or duplicate image: ' + code)
            incoming[code] = (Path(folder) / (code + '.json'), doc)
    content = {d['image']: d for d in read(root / 'payload/inscription_content.json')}
    import_id = hashlib.sha256(b''.join((root / 'payload' / name).read_bytes() for name in
        ('text_annotations.json', 'source_mismatches.json', 'inscription_content.json'))).hexdigest()
    output.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')
    old_folder = output.with_name('annotations_before_import_' + stamp)
    with tempfile.TemporaryDirectory(dir=output.parent) as temp:
        stage = Path(temp) / 'annotations'
        if output.exists():
            shutil.copytree(output, stage)
        else:
            stage.mkdir()
        registry = stage / '.state/content.json'
        current_content = {d['image']: d for d in read(registry)} if registry.exists() else {}
        receipt = stage / '.state/latest_user_import.json'
        already_imported = receipt.exists() and read(receipt).get('sha256') == import_id
        for code, (relative, doc) in incoming.items():
            candidates = [stage / (code + '.json'), stage / 'source_mismatches' / (code + '.json')]
            existing = [p for p in candidates if p.exists()]
            if len(existing) > 1:
                raise ValueError('Duplicate saved image: ' + code)
            current = read(existing[0]) if existing else None
            # The user's latest upload is authoritative on first import.
            # Re-running the same cell must preserve subsequent web edits.
            use_upload = not already_imported or current is None
            if not use_upload:
                print(code + ': đã nhập ZIP này; giữ chỉnh sửa hiện tại.')
                current_content.setdefault(doc['image'], content[doc['image']])
                continue
            changed = current != doc
            for p in candidates:
                p.unlink(missing_ok=True)
            write(stage / relative, doc)
            current_content[doc['image']] = content[doc['image']]
            if changed:
                for rel in [Path(code + '.json'), Path('source_mismatches') / (code + '.json')]:
                    (stage / '.state' / rel).unlink(missing_ok=True)
            companion = stage / 'model_reviews' / (code + '.json')
            if companion.exists() and geometry(read(companion)) != geometry(doc):
                companion.unlink()  # Original remains in the pre-import folder.
                print(code + ': bỏ nhãn phụ có box cũ; bản trước được giữ riêng.')
            print(f'{code}: {len(doc["bounding_boxes"])} box từ bản đã gửi.')
        write(registry, list(current_content.values()))
        write(receipt, {'sha256': import_id})
        launcher = stage / '_support/launch_with_original_source.py'
        if not launcher.exists():
            launcher.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / 'content_launcher.py', launcher)
        # Prepare and validate everything before replacing the active directory.
        if output.exists():
            output.rename(old_folder)
        try:
            shutil.move(str(stage), str(output))
        except Exception:
            if old_folder.exists() and not output.exists():
                old_folder.rename(output)
            raise
    if old_folder.exists():
        print('Bản trước khi nhập:', old_folder)
    archive = backup(output, output.parent / 'latest_work_full_backup.zip')
    print('Backup đầy đủ:', archive)
    print('ZIP Download All không chứa nhãn/trạng thái của Other; không tự tạo lại chúng.')
    return output
