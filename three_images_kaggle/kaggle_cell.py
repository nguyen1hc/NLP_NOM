# Chạy sau các ô cài app/model và khai báo REPO_DIR, REPO_PYTHON, IMAGE_DIR,
# SOURCE_JSON gốc. Thay ô restore bốn bài cũ bằng ô này.
from pathlib import Path
import os
import runpy

manifests = list(Path('/kaggle/input').rglob('three_images_manifest.json'))
if len(manifests) != 1:
    raise RuntimeError('Gắn đúng một Dataset chứa three_images_kaggle.zip.')

SOURCE_JSON = Path(SOURCE_JSON)
if SOURCE_JSON.name != 'student_114.json' or not SOURCE_JSON.is_file():
    raise RuntimeError('SOURCE_JSON phải trỏ tới student_114.json gốc.')

root = manifests[0].parent
job = runpy.run_path(str(root / 'three_images_helper.py'))
ANNOTATION_DIR = job['prepare'](
    root, REPO_DIR, IMAGE_DIR,
    output='/kaggle/working/annotations',
    python=REPO_PYTHON,
)
APP_LAUNCHER = ANNOTATION_DIR / '_support/launch_with_original_source.py'
backup_my_work = job['backup_my_work']
os.environ['SINONOM_REPO_DIR'] = str(Path(REPO_DIR).resolve())
print('Dữ liệu cho web:', ANNOTATION_DIR)
print('Launcher:', APP_LAUNCHER)
