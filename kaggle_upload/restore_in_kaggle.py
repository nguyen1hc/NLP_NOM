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
    print('Use SOURCE_JSON =',output/'_review/student_114_for_review.json')
    print('Use ANNOTATION_DIR =',output)
    return output


if __name__=='__main__':
    ANNOTATION_DIR=restore_student_114()
    SOURCE_JSON=ANNOTATION_DIR/'_review/student_114_for_review.json'
