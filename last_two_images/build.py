import json,re,hashlib,copy,shutil,runpy,zipfile,os
from pathlib import Path
from collections import Counter
from PIL import Image,ImageDraw
import sys
ROOT=Path(__file__).resolve().parents[1];OUT=Path(__file__).resolve().parent;PKG=OUT/'kaggle'
REPO=Path(os.environ.get('SINONOM_REPO_DIR','/tmp/sinonom-status-inspect'));sys.path[:0]=[str(REPO/'gradio'),str(REPO)]
from annotation.text_alignment import characters
from annotation.io import validate_source_mismatch_document,validate_document
from crop.crop import crop_document,image_resize
helper=runpy.run_path(str(ROOT/'three_images_kaggle/three_images_helper.py'))
previous=json.loads((PKG/'last_two_manifest.json').read_text())
# Rebuild only generated package data, never a user's working annotation folder.
shutil.rmtree(PKG/'annotations')
for folder in ('_support','.state','model_reviews','source_mismatches'):(PKG/'annotations'/folder).mkdir(parents=True)
for name in ('content_base.py','launch_with_original_source.py','three_images_helper.py'):
 shutil.copyfile(ROOT/'box_revision_55431_46303/kaggle/annotations/_support'/name,PKG/'annotations/_support'/name)
backup=OUT/'input/user_seven_annotations.zip'
with zipfile.ZipFile(backup) as z:
 content=json.loads(z.read('inscription_content.json'))
 preserved=[]
 for member,folder in [('text_annotations.json',''),('source_mismatches.json','source_mismatches')]:
  for saved in json.loads(z.read(member)):
   code=Path(saved['image']).stem;preserved.append(code)
   (PKG/'annotations'/folder/(code+'.json')).write_text(json.dumps(saved,ensure_ascii=False,indent=2)+'\n')
assert sorted(preserved)==sorted(['17390','18591','31962','55432','46302','55431','46303'])
raw=json.loads((ROOT/'student_114/student_114.json').read_text())
corrections=json.loads((OUT/'manual_box_corrections.json').read_text())
manifest={'version':2,'targets':['17077','18592'],'review_only_until_model_rerun':True,'allowed_geometry':{},
 'preserved_user_images':sorted(preserved),'user_backup_sha256':hashlib.sha256(backup.read_bytes()).hexdigest(),
 'limitations':['55431: user ZIP has only coordinates in Other; no recovered status/labels.', '18592: uncertain geometry and proposed alignment still require review.']}
reports=[]
for code in ('17077','18592'):
 image=code+'.jpg';record,face=next((r,f) for r in raw for f in r['noi_dung'] if str(f['ky_hieu'])==code)
 values={'Tên bia':record['ten_bia'],'Địa điểm':record['dia_diem'],'Niên đại':record['nien_dai'],**{s['tieu_de']:s['van_ban'] for s in face['chuyen_muc']}}
 doc={'image':image,'inscription_code':code,'content':{name:helper['normalize'](values.get(name)) for name in ('Tên bia','Địa điểm','Niên đại','Nguyên văn chữ Hán Nôm','Phiên âm Hán Việt','Toát yếu')}}
 content.append(doc);source=doc['content']['Nguyên văn chữ Hán Nôm']
 seed=json.loads((OUT/'input'/f'{code}_seed.json').read_text());rows=seed['rows'];original=seed['original']
 boxes={};labels={};review=[];im=Image.open(ROOT/'student_114'/image).convert('RGB');size=list(im.size)
 for r in rows:
  key=str(r['id']);label='□' if code=='18592' and r['label']=='MISS' else r['label'];x,y,xx,yy=r['bbox']
  # Correct column displacement visible in the enlarged rubbing, not source length.
  dx={'C_name':-145,'C_offering_main':-110,'C_offering_small':-35,'B_original_offering':-65,'B_name':-35,'A_original_offering':-30,'A_note_right':30,'A_note_left':25,'B_offering_note_right':-65,'B_offering_note_left':-35}.get(r['group'],0) if code=='18592' else 0
  x+=dx;xx+=dx;pad=6 if code=='17077' else 10
  bbox=[max(0,x-pad),max(0,y-pad),min(size[0],xx+pad),min(size[1],yy+pad)]
  if code=='18592' and r['id'] in (88,89,90):
   bbox={88:[1830,1830,2070,1995],89:[1840,1985,2060,2160],90:[1840,2145,2075,2320]}[r['id']]
  if code=='18592' and 214<=r['id']<=219:
   cy=[1650,1800,1940,2080,2220,2370][r['id']-214];bbox[1]=cy-78;bbox[3]=cy+78
  correction=corrections[code].get(key,{})
  bbox=correction.get('bbox',bbox);label=correction.get('annotation',label)
  # No prior assistant condition estimates are carried forward. These fields
  # are only a placeholder for app loading until the Kaggle model is run.
  boxes[key]={'bbox':bbox,'status':'damaged' if label=='□' else 'intact','damage_level':3 if label=='□' else None,
              'unknown':label=='□','unavailable_font':label=='@','expert_prediction':False,
              'suspicious':False,'order':int(key)}
  labels[key]=label
  uncertain=correction.get('review_required',code=='18592')
  review.append({'id':r['id'],'previous_id':r['id'],'character':label,'bbox':bbox,'group':r['group'],'review_required':uncertain,
    'reason':correction.get('reason','Ảnh mờ/mất nét; vị trí còn là bản nháp, cần kiểm tra từng chữ.' if uncertain else 'Đã đối chiếu vị trí trên dải ảnh phóng to; chưa đánh giá Intact/Damaged.'),
    **{k:correction[k] for k in ('source_character','observed_character') if k in correction}})
 excluded=list((Counter(characters(source))-Counter(v for v in labels.values() if v!='MISS')).elements())
 assert Counter(v for v in labels.values() if v!='MISS')+Counter(excluded)==Counter(characters(source)),code
 crop=original.get('crop') or crop_document(image,[700,750,size[0]-650,size[1]-1000],size)['crop']
 full={'image':image,'inscription_code':code,'source_text':source,'source_character_count':len(characters(source)), 'bounding_box_count':len(boxes),
       'bounding_boxes':boxes,'annotations':labels,'reading_order':list(range(1,len(boxes)+1)), 'excluded_characters':excluded,
       'crop':crop,'image_resize':original.get('image_resize') or image_resize(size,size),'image_pixel_sha256':hashlib.sha256(im.tobytes()).hexdigest(),
       'model_status':'pending_real_inference','geometry_review_complete':code=='17077','visual_review_complete':False}
 note=('Nguồn dư bốn 〇; ảnh có 其 tại 以廣其傳 nhưng nguồn thiếu.' if code=='17077' else 'Bản nháp cần rà. Đề xuất tại box 213: nguồn 月, ảnh dạng 日; dùng MISS và Excluded một 月. Ghi chú nhỏ có vùng không xác định được.')
 full.update(issue_type=['other'],note=note+' Nhãn đầy đủ lưu trong model_reviews/'+code+'.json.')
 native={k:full[k] for k in ('image','inscription_code','issue_type','note')};native['bounding_boxes']={k:{'bbox':b['bbox']} for k,b in boxes.items()}
 dest='source_mismatches/'+code+'.json';validate_source_mismatch_document(native,image,size)
 for folder in ('data','review'): (OUT/folder).mkdir(exist_ok=True)
 (OUT/'data'/f'{code}.json').write_text(json.dumps({**full,'model_status':'pending_real_inference','geometry_review_complete':code=='17077','visual_review_complete':False},ensure_ascii=False,indent=2)+'\n')
 (OUT/'review'/f'{code}.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
 (PKG/'annotations/model_reviews'/f'{code}.json').write_text(json.dumps(full,ensure_ascii=False,indent=2)+'\n')
 (PKG/'annotations'/dest).write_text(json.dumps(native,ensure_ascii=False,indent=2)+'\n')
 shape=lambda d:hashlib.sha256(json.dumps({k:b['bbox'] for k,b in d['bounding_boxes'].items()},sort_keys=True).encode()).hexdigest()
 manifest['allowed_geometry'][code]=list(dict.fromkeys(previous['allowed_geometry'][code]+[shape(original),shape(native)]))
 paint=im.copy();d=ImageDraw.Draw(paint)
 for row in review:d.rectangle(row['bbox'],outline='#ffb000' if row['review_required'] else '#00ddff',width=4)
 paint.thumbnail((1400,2100));paint.save(OUT/f'{code}_review.png')
 reports.append({'image':image,'boxes':len(boxes),'source_chars':len(characters(source)),'unknown_placeholders':sum(v=='□' for v in labels.values()),'excluded':excluded,'missing_ids':[k for k,v in labels.items() if v=='MISS'],'needs_visual_review':sum(r['review_required'] for r in review),'real_model_run':False})
(PKG/'annotations/.state/content.json').write_text(json.dumps(content,ensure_ascii=False,indent=2)+'\n');shutil.copyfile(PKG/'annotations/.state/content.json',PKG/'inscription_content.json')
(PKG/'last_two_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(OUT/'validation.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(reports,ensure_ascii=False,indent=2))
