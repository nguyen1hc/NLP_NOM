# Dừng web, chạy cell này, rồi mở lại web bằng APP_LAUNCHER.
from pathlib import Path

p = Path(REPO_DIR) / 'gradio/ui/editor.py'
code = p.read_text(encoding='utf-8')
marker = '# sinonom: show restored Other labels'
old = "    other_mismatch=(source_mismatch and s['source_mismatch']['issue_type']=='other')"
new = old + """
    # sinonom: show restored Other labels
    if (step in (4, 5, 7)
            and s.get('annotations')
            and set(s['annotations']) == set(s.get('bounding_boxes', {}))
            and all(isinstance(v, str) and bool(v) for v in s['annotations'].values())):
        other_mismatch = False
"""

if marker not in code:
    if code.count(old) != 1:
        raise RuntimeError('Code giao diện khác phiên bản đã kiểm tra; chưa sửa file.')
    p.write_text(code.replace(old, new), encoding='utf-8')

print('Đã sửa hiển thị chữ trên box. Mở lại web bằng APP_LAUNCHER.')
