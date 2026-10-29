# Sau các ô cài app/model và khai báo đường dẫn; lưu bài đang làm trước khi dừng web.
from pathlib import Path
import os, subprocess, runpy
items=list(Path('/kaggle/input').rglob('last_two_manifest.json'))
if len(items)!=1:
    raise RuntimeError('Gắn đúng một Dataset chứa ZIP sửa box 17077 và 18592.')
root=items[0].parent
ANNOTATION_DIR=Path('/kaggle/working/annotations')
subprocess.run([str(REPO_PYTHON),'-u',str(root/'apply_last_two.py'),
                '--repo',str(REPO_DIR),'--images',str(IMAGE_DIR),
                '--output',str(ANNOTATION_DIR)],cwd=REPO_DIR,check=True)
APP_LAUNCHER=ANNOTATION_DIR/'_support/launch_with_original_source.py'
os.environ['SINONOM_REPO_DIR']=str(Path(REPO_DIR).resolve())
backup_my_work=runpy.run_path(str(ANNOTATION_DIR/'_support/three_images_helper.py'))['backup_my_work']
