"""Keep mixed-source labels/status in a companion file; never edit input source."""
from copy import deepcopy
import hashlib
import json
import logging
import os
from pathlib import Path
import runpy
import sys


def install_mixed_review(repo):
    sys.path.insert(0, str(Path(repo) / 'gradio'))
    from annotation.workflow import Workflow
    from annotation.text_alignment import characters
    from annotation.text_extraction import annotation_text
    from crop.crop import crop_bbox, crop_document, image_resize
    from PIL import Image
    if getattr(Workflow.open_image, '_mixed_sidecar', False):
        return Workflow
    original_open, original_apply = Workflow.open_image, Workflow.apply

    def hydrate(engine, state, first=False):
        sidecar = engine.output / 'model_reviews' / (Path(state['image']).stem + '.json')
        issue = state.get('source_mismatch') or {}
        if not sidecar.is_file() or issue.get('issue_type') != 'other':
            return state
        full = json.loads(sidecar.read_text(encoding='utf-8'))
        if first:
            with Image.open(state['image_path']) as image:
                actual = hashlib.sha256(image.convert('RGB').tobytes()).hexdigest()
            if actual != full['image_pixel_sha256']:
                raise ValueError('Ảnh không khớp bản box thủ công đã lưu.')
        known = {tuple(box['bbox']): (key, box) for key, box in full['bounding_boxes'].items()}
        order = sorted(state['regions'], key=lambda uid: (
            int(known[tuple(state['regions'][uid]['bbox'])][0])
            if tuple(state['regions'][uid]['bbox']) in known else 10**9))
        state['bounding_boxes'], state['annotations'] = {}, {}
        state['box_id_by_region'], state['region_uid_by_box_id'] = {}, {}
        for index, uid in enumerate(order, 1):
            key = str(index)
            box = state['regions'][uid]
            match = known.get(tuple(box['bbox']))
            label = full['annotations'][match[0]] if match else 'MISS'
            if first and match:
                for field in ('status', 'damage_level', 'unknown', 'unavailable_font', 'expert_prediction', 'suspicious'):
                    box[field] = match[1].get(field)
            box['order'] = index
            state['bounding_boxes'][key] = deepcopy(box)
            state['annotations'][key] = label
            state['box_id_by_region'][uid] = key
            state['region_uid_by_box_id'][key] = uid
        state['reading_order'] = list(range(1, len(order) + 1))
        state['text_sequence'] = list(state['annotations'].values())
        state['text_token_ids'] = [str(i) for i in range(1, len(state['text_sequence']) + 1)]
        state['loaded_region_uid_by_box_id'] = deepcopy(state['region_uid_by_box_id'])
        state['selected_box_id'] = state['box_id_by_region'].get(state.get('selected_region_uid'))
        state['workflow']['alignment_valid'] = True
        if first:
            resized = full['image_resize']['output_size']
            cropped = crop_bbox(full['crop'], resized)
            width, height = state['image_size']
            state['crop'] = [cropped[0]*width/resized[0], cropped[1]*height/resized[1],
                             cropped[2]*width/resized[0], cropped[3]*height/resized[1]]
            state['resized_image_size'] = list(resized)
        return state

    def open_image(self, path):
        return hydrate(self, original_open(self, path), first=True)

    def apply(self, state, action, payload=None):
        result = original_apply(self, state, action, payload)
        sidecar = self.output / 'model_reviews' / (Path(result['image']).stem + '.json')
        mixed = sidecar.is_file() and (state.get('source_mismatch') or {}).get('issue_type') == 'other'
        if action == 'save_content' and mixed:
            full = json.loads(sidecar.read_text(encoding='utf-8'))
            if result['annotation_text'] == full['source_text']:
                result['source_mismatch'] = dict(
                    source_text=result['annotation_text'],
                    source_character_count=len(characters(result['annotation_text'])),
                    bounding_box_count=len(result['regions']), issue_type='other',
                    note=state['source_mismatch']['note'])
        if action in ('save_content', 'sort_boxes'):
            result = hydrate(self, result)
        if action == 'next' and state['current_step'] == 3 and mixed and result['current_step'] == 7:
            # The stock Other path skips status review. Our sidecar carries
            # complete labels, so these images can use the usual status screen.
            result['current_step'] = 4
        if action == 'save':
            if sidecar.is_file() and (result.get('source_mismatch') or {}).get('issue_type') == 'other':
                full = json.loads(sidecar.read_text(encoding='utf-8'))
                full.update(bounding_boxes=deepcopy(result['bounding_boxes']),
                            annotations=deepcopy(result['annotations']), reading_order=result['reading_order'],
                            source_text=result['annotation_text'])
                # Store the mixed case's crop outside the stock coordinate-only schema.
                full['crop'] = crop_document(result['image'], result['crop'], result['image_size'])['crop']
                full['image_resize'] = image_resize(result['image_size'], result['image_size'])
                temp = sidecar.with_suffix('.pending')
                temp.write_text(json.dumps(full, ensure_ascii=False, indent=2), encoding='utf-8')
                temp.replace(sidecar)
            try:
                helper = runpy.run_path(str(self.output / '_support/three_images_helper.py'))
                helper['backup_my_work'](self.output)
            except Exception:
                logging.exception('Annotation saved, but automatic backup failed; run backup_my_work manually.')
        return result

    open_image._mixed_sidecar = True
    Workflow.open_image, Workflow.apply = open_image, apply
    return Workflow


if __name__ == '__main__':
    repo = Path(os.environ.get('SINONOM_REPO_DIR', '/kaggle/working/SinoNom-Annotation'))
    base = runpy.run_path(str(Path(__file__).with_name('content_base.py')))
    base['enable_saved_content_sections'](repo)
    install_mixed_review(repo)
    runpy.run_path(str(repo / 'gradio/app.py'), run_name='__main__')
