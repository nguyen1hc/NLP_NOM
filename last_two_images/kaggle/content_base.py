"""Launch the upstream app while restoring saved Content from its output folder.

Only the selected record in memory is extended with sections already present in
the saved Content registry. The source JSON and upstream checkout stay unchanged.
"""
from copy import deepcopy
from functools import wraps
import json
import os
from pathlib import Path
import runpy
import sys


def enable_saved_content_sections(repo_dir):
    gradio_dir = Path(repo_dir).resolve() / 'gradio'
    if str(gradio_dir) not in sys.path:
        sys.path.insert(0, str(gradio_dir))
    from annotation.workflow import Workflow
    from annotation.text_extraction import validate_content_document

    original = Workflow._saved_content_for
    if getattr(original, '_restores_missing_content_sections', False):
        return Workflow

    @wraps(original)
    def restore_content(self, image_name, code, source_record):
        restored = deepcopy(original(self, image_name, code, source_record))
        registry = self.output / '.state' / 'content.json'
        if not registry.exists():
            return restored
        documents = json.loads(registry.read_text(encoding='utf-8'))
        matches = [item for item in documents
                   if isinstance(item, dict) and item.get('image') == image_name]
        if not matches:
            return restored
        # The upstream method has already checked uniqueness and schema.
        saved = validate_content_document(matches[0], image_name)
        faces = [face for face in restored.get('noi_dung', [])
                 if str(face.get('ky_hieu')) == str(code)]
        if not faces and str(code).isdigit():
            faces = [face for face in restored.get('noi_dung', [])
                     if str(face.get('ky_hieu')) == str(int(code))]
        if len(faces) != 1:
            raise ValueError('Exactly one face must match the restored Content.')
        face = faces[0]
        sections = face.setdefault('chuyen_muc', [])
        existing = {section.get('tieu_de') for section in sections}
        for title in self.content_titles:
            value = saved['content'].get(title)
            if title not in existing and isinstance(value, str):
                sections.append({'tieu_de': title, 'van_ban': value})
                existing.add(title)
        return restored

    restore_content._restores_missing_content_sections = True
    Workflow._saved_content_for = restore_content
    return Workflow


def main():
    repo = Path(os.environ.get('SINONOM_REPO_DIR',
                               '/kaggle/working/SinoNom-Annotation'))
    app = repo / 'gradio/app.py'
    if not app.is_file():
        raise FileNotFoundError(f'Annotation app not found: {app}')
    enable_saved_content_sections(repo)
    sys.argv[0] = str(app)
    runpy.run_path(str(app), run_name='__main__')


if __name__ == '__main__':
    main()
