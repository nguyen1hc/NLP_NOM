from pathlib import Path
import runpy

scripts = list(Path('/kaggle/input').rglob('restore_latest_work.py'))
if len(scripts) != 1:
    raise RuntimeError('Gắn đúng một Dataset chứa user_work_latest_kaggle.zip.')

script = scripts[0]
ANNOTATION_DIR = runpy.run_path(str(script))['restore_latest_work'](script.parent)
APP_LAUNCHER = ANNOTATION_DIR / '_support/launch_with_original_source.py'
print('Giờ chạy lại cell mở web cũ. SOURCE_JSON giữ nguyên student_114.json.')
