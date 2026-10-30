"""Correct only the known 18592 label/note; preserve boxes and model results."""
from collections import Counter
from pathlib import Path
import json
import runpy

ROOT = Path(__file__).resolve().parent


def fix_18592(output='/kaggle/working/annotations'):
    output = Path(output)
    helper = runpy.run_path(str(ROOT / 'three_images_helper.py'))
    reference = json.loads((ROOT / 'annotations/model_reviews/18592.json').read_text())
    sidecar = output / 'model_reviews/18592.json'
    native = output / 'source_mismatches/18592.json'
    full = json.loads(sidecar.read_text())
    doc = json.loads(native.read_text())
    expected = reference['bounding_boxes']['184']['bbox']
    matches = [k for k, box in full['bounding_boxes'].items() if box['bbox'] == expected]
    if len(matches) != 1 or full['source_text'] != reference['source_text']:
        raise ValueError('Vị trí hoặc Content 18592 đã đổi; giữ nguyên bài hiện tại.')
    key = matches[0]
    if full['annotations'].get(key) not in ('MISS', '月'):
        raise ValueError('Nhãn vị trí 月 đã được sửa; không ghi đè.')
    unassigned = reference['unassigned_source_characters']
    excluded = Counter(full.get('excluded_characters', []))
    if excluded and excluded not in (Counter(unassigned), Counter(unassigned + ['月'])):
        raise ValueError('Danh sách Excluded đã đổi; không ghi đè.')
    if doc.get('issue_type') != ['other']:
        raise ValueError('Loại mismatch đã đổi; không ghi đè.')
    helper['backup_my_work'](output, output.parent / 'before_18592_fix.zip')
    full['annotations'][key] = '月'
    full['bounding_boxes'][key]['suspicious'] = True
    full['bounding_boxes'][key]['unknown'] = False
    full['excluded_characters'] = []
    full['unassigned_source_characters'] = unassigned
    full['mismatch_classification_verified'] = False
    full['note'] = doc['note'] = reference['note']
    # Remove the stale document fingerprint so next open reads the updated files.
    meta = output / '.state/source_mismatches/18592.json'
    with helper['transaction']([sidecar, native, meta]):
        helper['atomic'](sidecar, helper['encoded'](full))
        helper['atomic'](native, helper['encoded'](doc))
        meta.unlink(missing_ok=True)
    helper['backup_my_work'](output)
    print('Đã sửa riêng 18592. Giữ box và trạng thái model. Note:', full['note'])
    return output
