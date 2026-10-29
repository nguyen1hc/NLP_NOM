import json,re,hashlib,copy,shutil,runpy
from pathlib import Path
from collections import Counter
from PIL import Image,ImageDraw
import sys
ROOT=Path(__file__).resolve().parents[1];OUT=Path(__file__).resolve().parent;PKG=OUT/'kaggle';sys.path[:0]=['/tmp/sinonom-status-inspect/gradio','/tmp/sinonom-status-inspect']
from annotation.text_alignment import characters
from annotation.io import validate_source_mismatch_document,validate_document
from crop.crop import crop_document,image_resize
helper=runpy.run_path(str(ROOT/'three_images_kaggle/three_images_helper.py'))
shutil.copytree(ROOT/'box_revision_55431_46303/kaggle/annotations',PKG/'annotations',dirs_exist_ok=True)
content=json.loads((PKG/'annotations/.state/content.json').read_text());raw=json.loads((ROOT/'student_114/student_114.json').read_text())
manifest={'version':1,'targets':['17077','18592'],'review_only_until_model_rerun':True,'allowed_geometry':{}}
reports=[]
for code in ('17077','18592'):
 image=code+'.jpg';record,face=next((r,f) for r in raw for f in r['noi_dung'] if str(f['ky_hieu'])==code)
 values={'Tên bia':record['ten_bia'],'Địa điểm':record['dia_diem'],'Niên đại':record['nien_dai'],**{s['tieu_de']:s['van_ban'] for s in face['chuyen_muc']}}
 doc={'image':image,'inscription_code':code,'content':{name:helper['normalize'](values.get(name)) for name in ('Tên bia','Địa điểm','Niên đại','Nguyên văn chữ Hán Nôm','Phiên âm Hán Việt','Toát yếu')}}
 content.append(doc);source=doc['content']['Nguyên văn chữ Hán Nôm']
 rows=json.loads((ROOT/'student_114_kaggle_review/character_review'/f'{code}.json').read_text())
 original=json.loads((ROOT/'student_114_kaggle_review/annotations/source_mismatches'/f'{code}.json').read_text())
 boxes={};labels={};review=[];im=Image.open(ROOT/'student_114'/image).convert('RGB');size=list(im.size)
 for r in rows:
  key=str(r['id']);label='□' if code=='18592' and r['label']=='MISS' else r['label'];x,y,xx,yy=r['bbox']
  # Correct column displacement visible in the enlarged rubbing, not source length.
  dx={'C_name':-145,'C_offering_main':-110,'C_offering_small':-35,'B_original_offering':-65,'B_name':-35,'A_original_offering':-30}.get(r['group'],0) if code=='18592' else 0
  x+=dx;xx+=dx;pad=6 if code=='17077' else 10
  bbox=[max(0,x-pad),max(0,y-pad),min(size[0],xx+pad),min(size[1],yy+pad)]
  if code=='18592' and r['id'] in (88,89,90):
   bbox={88:[1830,1830,2070,1995],89:[1840,1985,2060,2160],90:[1840,2145,2075,2320]}[r['id']]
  if code=='18592' and 214<=r['id']<=219:
   cy=[1650,1800,1940,2080,2220,2370][r['id']-214];bbox[1]=cy-78;bbox[3]=cy+78
  # No prior assistant condition estimates are carried forward. These fields
  # are only a placeholder for app loading until the Kaggle model is run.
  boxes[key]={'bbox':bbox,'status':'damaged' if label=='□' else 'intact','damage_level':3 if label=='□' else None,
              'unknown':label=='□','unavailable_font':label=='@','expert_prediction':bool(r.get('expert_prediction')) if label!='□' else False,
              'suspicious':bool(r.get('suspicious')) if label!='□' else False,'order':int(key)}
  labels[key]=label
  uncertain=code=='18592' or r['group'] in ('small_note_A','small_note_B','mother_memorial_date','benefactor_date_blank')
  review.append({'id':r['id'],'previous_id':r['id'],'character':label,'bbox':bbox,'group':r['group'],'review_required':uncertain,
    'reason':'Ảnh mờ/mất nét; vị trí còn là bản nháp, cần kiểm tra từng chữ.' if uncertain else 'Đã đối chiếu vị trí trên dải ảnh phóng to.'})
 excluded=list((Counter(characters(source))-Counter(v for v in labels.values() if v!='MISS')).elements())
 assert Counter(v for v in labels.values() if v!='MISS')+Counter(excluded)==Counter(characters(source)),code
 crop=original.get('crop') or crop_document(image,[700,750,size[0]-650,size[1]-1000],size)['crop']
 full={'image':image,'inscription_code':code,'source_text':source,'source_character_count':len(characters(source)), 'bounding_box_count':len(boxes),
       'bounding_boxes':boxes,'annotations':labels,'reading_order':list(range(1,len(boxes)+1)), 'excluded_characters':excluded,
       'crop':crop,'image_resize':original.get('image_resize') or image_resize(size,size),'image_pixel_sha256':hashlib.sha256(im.tobytes()).hexdigest()}
 if code=='17077':
  full.update(issue_type=['other'],note='Nguồn dư bốn 〇; ảnh có 其 tại 以廣其傳 nhưng nguồn thiếu. Nhãn đầy đủ lưu trong model_reviews/17077.json. Các ghi chú nhỏ cần rà.')
  native={k:full[k] for k in ('image','inscription_code','issue_type','note')};native['bounding_boxes']={k:{'bbox':b['bbox']} for k,b in boxes.items()}
  dest='source_mismatches/'+code+'.json';validate_source_mismatch_document(native,image,size)
 else:
  native={k:full[k] for k in ('image','bounding_boxes','annotations','crop','image_resize')};dest=code+'.json';validate_document(native,image,size)
 for folder in ('data','review'): (OUT/folder).mkdir(exist_ok=True)
 (OUT/'data'/f'{code}.json').write_text(json.dumps({**full,'model_status':'pending_real_inference','visual_review_complete':False},ensure_ascii=False,indent=2)+'\n')
 (OUT/'review'/f'{code}.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
 (PKG/'annotations/model_reviews'/f'{code}.json').write_text(json.dumps(full,ensure_ascii=False,indent=2)+'\n')
 (PKG/'annotations'/dest).write_text(json.dumps(native,ensure_ascii=False,indent=2)+'\n')
 shape=lambda d:hashlib.sha256(json.dumps({k:b['bbox'] for k,b in d['bounding_boxes'].items()},sort_keys=True).encode()).hexdigest()
 manifest['allowed_geometry'][code]=[shape(original),shape(native)]
 paint=im.copy();d=ImageDraw.Draw(paint)
 for row in review:d.rectangle(row['bbox'],outline='#ffb000' if row['review_required'] else '#00ddff',width=4)
 paint.thumbnail((1400,2100));paint.save(OUT/f'{code}_review.png')
 reports.append({'image':image,'boxes':len(boxes),'source_chars':len(characters(source)),'unknown_placeholders':sum(v=='□' for v in labels.values()),'excluded':excluded,'missing_ids':[k for k,v in labels.items() if v=='MISS'],'needs_visual_review':sum(r['review_required'] for r in review),'real_model_run':False})
(PKG/'annotations/.state/content.json').write_text(json.dumps(content,ensure_ascii=False,indent=2)+'\n');shutil.copyfile(PKG/'annotations/.state/content.json',PKG/'inscription_content.json')
(PKG/'last_two_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(OUT/'validation.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(reports,ensure_ascii=False,indent=2))
