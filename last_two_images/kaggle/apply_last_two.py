"""Merge latest seven saved images, stage two review drafts, run damage model."""
import argparse,copy,hashlib,json,runpy,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
TARGETS=('17077','18592')

def shape(doc):
    return hashlib.sha256(json.dumps({k:[float(v) for v in b['bbox']] for k,b in doc['bounding_boxes'].items()},sort_keys=True).encode()).hexdigest()

def box_set(doc):
    return hashlib.sha256(json.dumps(sorted([float(v) for v in b['bbox']] for b in doc['bounding_boxes'].values())).encode()).hexdigest()

def known_geometry(doc, allowed, sets=()):
    # App saves coordinates as floats; 120 and 120.0 describe the same box.
    legacy={k:[int(v) if float(v).is_integer() else v for v in b['bbox']] for k,b in doc['bounding_boxes'].items()}
    return box_set(doc) in sets or shape(doc) in allowed or hashlib.sha256(json.dumps(legacy,sort_keys=True).encode()).hexdigest() in allowed

def apply(repo,images,output,predict=None):
    repo,images,output=map(Path,(repo,images,output))
    sys.path[:0]=[str(repo),str(repo/'gradio')]
    from PIL import Image
    from annotation.io import validate_source_mismatch_document, validate_document
    from annotation.text_alignment import characters
    from text_detection.fusion import fuse_localizations
    support=ROOT/'annotations/_support'
    if not (support/'launch_with_original_source.py').is_file():
        support=ROOT
    for name in ('launch_with_original_source.py','content_base.py','three_images_helper.py'):
        if not (support/name).is_file():
            raise FileNotFoundError('Dataset thiếu code hỗ trợ: '+str(support/name))
    helper=runpy.run_path(str(support/'three_images_helper.py'))
    manifest=json.loads((ROOT/'last_two_manifest.json').read_text())
    old={};fulls={};payload={}
    def remember(p):old[p]=p.read_bytes() if p.is_file() else None
    for code in TARGETS:
        for p in (output/(code+'.json'),output/'source_mismatches'/(code+'.json')):
            remember(p)
            if p.is_file() and not known_geometry(json.loads(p.read_text()),manifest['allowed_geometry'][code],manifest.get('allowed_box_sets',{}).get(code,[])):
                raise ValueError('Có box mới cho '+code+'; giữ nguyên bài hiện tại, không ghi đè.')
        fulls[code]=json.loads((ROOT/'annotations/model_reviews'/(code+'.json')).read_text())
        with Image.open(images/fulls[code]['image']) as im:
            if hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()!=fulls[code]['image_pixel_sha256']:
                raise ValueError('Ảnh khác bản dùng để vẽ box: '+code)
    registry=output/'.state/content.json';remember(registry)
    content_path=ROOT/'annotations/.state/content.json'
    if not content_path.is_file():content_path=ROOT/'inscription_content.json'
    records={r['image']:r for r in json.loads(content_path.read_text())}
    if registry.is_file():records.update({r['image']:r for r in json.loads(registry.read_text())})
    for code,full in fulls.items():
        if full['source_text']!=records[full['image']]['content']['Nguyên văn chữ Hán Nôm']:
            raise ValueError('Content đã đổi: '+code+'; cần đối chiếu lại nhãn chữ trước.')
    for folder in ('','source_mismatches'):
        for p in (ROOT/'annotations'/folder).glob('*.json'):
            if not p.stem.isdecimal() or p.stem in TARGETS:continue
            destinations=(output/p.name,output/'source_mismatches'/p.name)
            if not any(t.exists() for t in destinations):
                for target in destinations:remember(target)
                payload[(Path(folder)/p.name).as_posix()]=p.read_bytes()
    predictions=(predict or helper['predict_damage'])(repo,[images/full['image'] for full in fulls.values()])
    for code,full in fulls.items():
        fixed=[b['bbox'] for b in full['bounding_boxes'].values()]
        _,_,damaged=fuse_localizations(predictions[code],fixed)
        for i,(key,box) in enumerate(full['bounding_boxes'].items()):
            unknown=full['annotations'][key]=='□'
            box.update(status='damaged' if unknown or i in damaged else 'intact',damage_level=3 if unknown else None,unknown=unknown)
            if unknown:
                box.update(unavailable_font=False,expert_prediction=False,suspicious=False)
            if full['annotations'][key]=='MISS':
                box.update(unknown=False,unavailable_font=False,expert_prediction=False,suspicious=False)
        full['model_status']='completed_on_kaggle'
        if full.get('issue_type')==['other']:
            native={k:full[k] for k in ('image','inscription_code','issue_type','note')}
            native['bounding_boxes']={k:{'bbox':b['bbox']} for k,b in full['bounding_boxes'].items()}
        else:
            native={k:full[k] for k in ('image','bounding_boxes','annotations','crop','image_resize')}
        mismatch=full.get('issue_type')==['other']
        with Image.open(images/full['image']) as im:(validate_source_mismatch_document if mismatch else validate_document)(native,full['image'],list(im.size))
        payload[('source_mismatches/' if mismatch else '')+code+'.json']=helper['encoded'](native)
        payload['model_reviews/'+code+'.json']=helper['encoded'](full)
    if any((p.read_bytes() if p.is_file() else None)!=data for p,data in old.items()):
        raise ValueError('Bài đã đổi trong lúc model chạy; không ghi đè.')
    if registry.is_file():helper['backup_my_work'](output,output.parent/'before_last_two.zip')
    payload['.state/content.json']=helper['encoded'](list(records.values()))
    for name in ('content_base.py','launch_with_original_source.py','three_images_helper.py'):
        payload['_support/'+name]=(support/name).read_bytes()
    payload['.state/last_two.json']=helper['encoded']({'images':list(TARGETS),'model_rerun':True})
    stale=[output/'.state/source_mismatches'/(c+'.json') for c in TARGETS]+[output/(c+'.json') for c in TARGETS]+[output/'.state'/(c+'.json') for c in TARGETS]
    with helper['transaction']([output/name for name in payload]+stale):
        for name,data in payload.items():helper['atomic'](output/name,data)
        for p in stale:p.unlink(missing_ok=True)
    helper['backup_my_work'](output)
    print('Đã giữ/nạp 7 bài từ backup mới nhất và thêm 17077, 18592. Model chỉ đánh giá hỏng, không vẽ lại box. 18592 còn là bản nháp cần rà.')
    if not (output/'model_reviews/55431.json').is_file():
        print('Lưu ý: ZIP gốc của 55431 ở dạng Other chỉ có tọa độ; không chứa nhãn/trạng thái để khôi phục.')
    return output

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--images',type=Path,required=True);p.add_argument('--output',type=Path,default=Path('/kaggle/working/annotations'));a=p.parse_args();apply(a.repo,a.images,a.output)
