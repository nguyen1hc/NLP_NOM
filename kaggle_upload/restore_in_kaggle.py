"""Copy this cell into the SAME Kaggle notebook as the annotation app."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import shutil
import tempfile
import zipfile


def restore_student_114(input_root='/kaggle/input', output='/kaggle/working/annotations'):
    input_root, output = Path(input_root), Path(output)
    manifest_name='student_114_manifest.json'
    archives=sorted(input_root.rglob('student_114_kaggle_restore*.zip'))
    manifests=sorted(input_root.rglob(manifest_name))
    if len(archives)>1 or (not archives and len(manifests)!=1):
        raise RuntimeError('Add exactly one student_114_kaggle_restore.zip Dataset to Input.')
    bundle=None
    try:
        if archives:
            bundle=zipfile.ZipFile(archives[0])
            manifest=json.loads(bundle.read(manifest_name))
            read=lambda name: bundle.read(name)
        else:
            root=manifests[0].parent
            manifest=json.loads(manifests[0].read_text(encoding='utf-8'))
            read=lambda name: (root/name).read_bytes()
        payload={}
        for relative,metadata in manifest['files'].items():
            path=PurePosixPath(relative)
            if path.is_absolute() or '..' in path.parts or '\\' in relative:
                raise ValueError('Unsafe path in backup manifest.')
            if relative=='_review/student_114_for_review.json':
                # Legacy replacement sources are no longer used or restored.
                continue
            try:
                data=read('annotations/'+relative)
            except (FileNotFoundError,KeyError):
                if relative=='.state/content.json':
                    data=read('inscription_content.json')
                elif relative=='annotations.zip' and bundle is None:
                    # Kaggle may extract nested archives and remove the ZIP.
                    # This generated export is not used to reopen native work.
                    print('Skipping absent generated export: annotations.zip')
                    continue
                else:
                    raise
            if hashlib.sha256(data).hexdigest()!=metadata['sha256']:
                raise ValueError('Backup file checksum failed: '+relative)
            payload[relative]=data
    finally:
        if bundle is not None:bundle.close()
    if output.exists() and any(output.iterdir()):
        if all((output/name).is_file() and (output/name).read_bytes()==data
               for name,data in payload.items()):
            print('This bundle is already restored. Existing work kept:',output)
            return output
        raise RuntimeError(str(output)+' already contains data. No overwrite performed. '
                           'Choose a new output folder or back up your current work first.')
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as temporary:
        stage=Path(temporary)/'annotations'
        for name,data in payload.items():
            target=stage/name
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(data)
        if output.exists():output.rmdir()
        shutil.move(str(stage),str(output))
    print('Restored 9 images / 1940 boxes, including edited Content.')
    print('Bundle revision:',manifest.get('revision','initial_review'))
    print('Two mixed mismatches (17077 and 46302) load as Other; see _review/README.md.')
    print('Keep SOURCE_JSON pointing to the original student_114.json in Input.')
    print('Use ANNOTATION_DIR =',output)
    return output


def find_original_source(input_root='/kaggle/input', source_json=None):
    if source_json is not None:
        source = Path(source_json)
        if source.name != 'student_114.json' or not source.is_file():
            raise FileNotFoundError('SOURCE_JSON must point to the original student_114.json in Input.')
        return source
    matches = sorted(Path(input_root).rglob('student_114.json'))
    if len(matches) != 1:
        raise RuntimeError('Expected one original student_114.json in Input. '
                           'Pass its path as source_json if multiple copies are attached.')
    return matches[0]


# EMBEDDED_LAUNCHER_START
ORIGINAL_SOURCE_LAUNCHER = '"""Launch the upstream app while restoring saved Content from its output folder.\n\nOnly the selected record in memory is extended with sections already present in\nthe saved Content registry. The source JSON and upstream checkout stay unchanged.\n"""\nfrom copy import deepcopy\nfrom functools import wraps\nimport json\nimport os\nfrom pathlib import Path\nimport runpy\nimport sys\n\n\ndef enable_saved_content_sections(repo_dir):\n    gradio_dir = Path(repo_dir).resolve() / \'gradio\'\n    if str(gradio_dir) not in sys.path:\n        sys.path.insert(0, str(gradio_dir))\n    from annotation.workflow import Workflow\n    from annotation.text_extraction import validate_content_document\n\n    original = Workflow._saved_content_for\n    if getattr(original, \'_restores_missing_content_sections\', False):\n        return Workflow\n\n    @wraps(original)\n    def restore_content(self, image_name, code, source_record):\n        restored = deepcopy(original(self, image_name, code, source_record))\n        registry = self.output / \'.state\' / \'content.json\'\n        if not registry.exists():\n            return restored\n        documents = json.loads(registry.read_text(encoding=\'utf-8\'))\n        matches = [item for item in documents\n                   if isinstance(item, dict) and item.get(\'image\') == image_name]\n        if not matches:\n            return restored\n        # The upstream method has already checked uniqueness and schema.\n        saved = validate_content_document(matches[0], image_name)\n        faces = [face for face in restored.get(\'noi_dung\', [])\n                 if str(face.get(\'ky_hieu\')) == str(code)]\n        if not faces and str(code).isdigit():\n            faces = [face for face in restored.get(\'noi_dung\', [])\n                     if str(face.get(\'ky_hieu\')) == str(int(code))]\n        if len(faces) != 1:\n            raise ValueError(\'Exactly one face must match the restored Content.\')\n        face = faces[0]\n        sections = face.setdefault(\'chuyen_muc\', [])\n        existing = {section.get(\'tieu_de\') for section in sections}\n        for title in self.content_titles:\n            value = saved[\'content\'].get(title)\n            if title not in existing and isinstance(value, str):\n                sections.append({\'tieu_de\': title, \'van_ban\': value})\n                existing.add(title)\n        return restored\n\n    restore_content._restores_missing_content_sections = True\n    Workflow._saved_content_for = restore_content\n    return Workflow\n\n\ndef main():\n    repo = Path(os.environ.get(\'SINONOM_REPO_DIR\',\n                               \'/kaggle/working/SinoNom-Annotation\'))\n    app = repo / \'gradio/app.py\'\n    if not app.is_file():\n        raise FileNotFoundError(f\'Annotation app not found: {app}\')\n    enable_saved_content_sections(repo)\n    sys.argv[0] = str(app)\n    runpy.run_path(str(app), run_name=\'__main__\')\n\n\nif __name__ == \'__main__\':\n    main()\n'
# EMBEDDED_LAUNCHER_END


def prepare_original_source(output, input_root='/kaggle/input', source_json=None):
    source = find_original_source(input_root, source_json)
    launcher = Path(output) / '_support/launch_with_original_source.py'
    launcher.parent.mkdir(parents=True, exist_ok=True)
    compile(ORIGINAL_SOURCE_LAUNCHER, str(launcher), 'exec')
    launcher.write_text(ORIGINAL_SOURCE_LAUNCHER, encoding='utf-8')
    print('Original source (read only):', source)
    print('Saved Content:', Path(output) / '.state/content.json')
    return source, launcher


if __name__=='__main__':
    SOURCE_JSON=find_original_source()
    ANNOTATION_DIR=restore_student_114()
    SOURCE_JSON,APP_LAUNCHER=prepare_original_source(
        ANNOTATION_DIR,source_json=SOURCE_JSON)
