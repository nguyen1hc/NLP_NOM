"""Coordinates reviewed against enlarged source images. No OCR/status inference."""
import json,copy,math,zipfile,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np
ROOT=Path(__file__).resolve().parents[1]; OUT=Path(__file__).resolve().parent
FONT=ImageFont.truetype('/tmp/sinonom-status-inspect/fonts/NomNaTong.ttf',18)
SMALL=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)
coords={}; groups={}; uncertain={}; removed={'55431':[76], '46303':[60,94,133,153]}
oldrows={code:json.loads((ROOT/'three_images_work/box_review'/f'{code}.json').read_text()) for code in ('55431','46303')}
# Trace the slant of the actual columns; each glyph has an independent vertical span.
tracks={'column_1':(765,783,46),'column_2':(716,736,46),'column_3':(672,690,46),
'column_4':(628,643,48),'column_5':(582,595,52),'column_6':(536,549,50),
'column_7':(489,504,50),'date':(357,369,49),'field_1':(328,335,42),'field_2':(288,287,39)}
coords['55431']={};groups['55431']={};uncertain['55431']={}
for row in oldrows['55431']:
 box=row['bbox'];group=row['group']; top,bottom=box[1],box[3]
 start,end,width=tracks[group]
 y0,y1=((465,815) if group=='date' else (915,1165) if group.startswith('field') else (470,1230))
 cx=float(np.interp((top+bottom)/2,[y0,y1],[start,end]))
 coords['55431'][row['id']]=[math.floor(cx-width/2),top,math.ceil(cx+width/2),bottom]
 groups['55431'][row['id']]=group
# 設 is one character, not two boxes; 上 and 表 are two separate characters.
spans=[(456,495),(495,530),(530,559),(560,597),(598,631),(632,654),(653,675),(674,697),
(696,719),(720,756),(756,792),(791,826),(825,853),(853,879),(879,907),(908,931),(932,958),
(961,990),(988,1024),(1021,1053),(1052,1091),(1091,1123),(1125,1157),(1157,1184),(1186,1225),(1224,1254)]
for oldid,(top,bottom) in enumerate(spans,70):
 box=coords['55431'][oldid];box[1]=top;box[3]=bottom
# 表 includes the upper component; the source's 上 has no separate visible glyph.
coords['55431'][77][1]=653
# Literal notes below the date remain in their own columns.
# 46303 has nine physical text columns, in addition to the horizontal heading.
coords['46303']={};groups['46303']={};uncertain['46303']={}
for row in oldrows['46303'][:13]:
 coords['46303'][row['id']]=row['bbox'];groups['46303'][row['id']]='title'
def column(ids,ys,cx0,cx1,width,name,outer=None):
 assert len(ids)==len(ys),(name,len(ids),len(ys))
 for i,(oldid,y) in enumerate(zip(ids,ys)):
  before=(y+ys[i-1])/2 if i else y-(ys[1]-y)/2
  after=(y+ys[i+1])/2 if i+1<len(ys) else y+(y-ys[i-1])/2
  before=max(before,y-19);after=min(after,y+19)
  cx=float(np.interp(y,[ys[0],ys[-1]],[cx0,cx1]))
  coords['46303'][oldid]=[math.floor(cx-width/2),math.floor(before)-1,math.ceil(cx+width/2),math.ceil(after)+1]
  groups['46303'][oldid]=name
column(list(range(14,31)),[334,354,374,393,414,436,457,478,495,517,539,561,583,607,634,656,678],577,573,31,'physical_1')
column(list(range(31,61)),[324,343,362,384,406,428,451,483,505,526,538,550,567,588,628,641,652,674,697,720,738,754,772,786,804,822,843,863,879,892],544,544,32,'physical_2')
column(list(range(61,94)),[337,351,369,386,403,419,430,443,461,479,498,518,539,556,569,581,601,623,642,658,675,695,714,735,753,772,786,803,821,837,854,866,880],511,511,32,'physical_3')
# The visible fourth column starts 地處; the source's preceding 墳 is excluded for review.
column(list(range(95,119)),[331,350,366,381,400,413,426,442,455,477,492,510,530,549,568,585,600,620,640,657,676,698,716,731],478,472,32,'physical_4')
column(list(range(119,132)),[333,359,383,409,427,445,466,491,512,531,551,572,587],451,448,33,'physical_5')
column(list(range(132,152)),[326,336,348,374,406,440,468,494,515,539,564,597,626,652,680,749,777,801,824,850],418,419,33,'physical_6')
column(list(range(152,177)),[326,337,354,377,400,419,443,461,478,490,506,525,550,574,597,619,636,652,676,699,720,739,759,781,804],390,390,32,'physical_7')
column(list(range(177,193)),[330,354,377,403,429,453,475,496,518,537,555,572,590,610,630,646],363,363,32,'physical_8')
column(list(range(193,213)),[338,361,385,404,426,447,460,477,491,509,535,562,578,597,618,640,665,685,706,727],334,334,31,'physical_9')
for ids,reason in [([60],'Vị trí □ cuối cột sát mép bia; chưa xác định chắc phần chữ.'),
([132,133,134,152,153,154],'Đầu cột bị nếp gấp che; ranh giới các chữ chưa chắc.'),
([150,207],'Vị trí □ bị mất nét.'),([77,101,111,145,166,191],'Chữ nằm trên nếp gấp; cần kiểm tra biên và trạng thái.')]:
 for oldid in ids:uncertain['46303'][oldid]=reason
# At the heads of columns 6/7, keep each visible complex glyph whole.
coords['46303'][134][1:4:2]=[330,362]
coords['46303'][154][1:4:2]=[332,366]
for oldid in removed['46303']:uncertain['46303'].pop(oldid,None)
latest=Path('/workspace/attachments/076aa476-4c52-432c-958b-6ad2f5182f70/annotations (3).zip')
with zipfile.ZipFile(latest) as z: saved={Path(r['image']).stem:r for r in json.loads(z.read('source_mismatches.json'))}
report={}
for code in ('55431','46303'):
 data=json.loads((ROOT/'three_images_kaggle/data'/f'{code}.json').read_text());native=copy.deepcopy(saved[code]);original=copy.deepcopy(data)
 input_boxes={};annotations={};mapping={};review=[]
 for oldid in range(1,len(original['bounding_boxes'])+1):
  if oldid in removed[code]:continue
  newid=str(len(input_boxes)+1);oldkey=str(oldid);box=copy.deepcopy(original['bounding_boxes'][oldkey]);box['bbox']=coords[code][oldid];box['order']=int(newid)
  input_boxes[newid]=box;annotations[newid]=original['annotations'][oldkey];mapping[newid]=oldkey
  review.append({'id':int(newid),'previous_id':oldid,'character':annotations[newid],'bbox':box['bbox'],'group':groups[code][oldid],
                 'review_required':oldid in uncertain[code],'reason':uncertain[code].get(oldid,'')})
 data.update(bounding_boxes=input_boxes,annotations=annotations,reading_order=list(range(1,len(input_boxes)+1)),previous_id_by_id=mapping,missing_box_ids=[int(k) for k,v in annotations.items() if v=='MISS'])
 data['excluded_characters']=['〇','□','墳','所','所'] if code=='46303' else ['上']
 data['geometry_review_notes']=['Coordinates revised from enlarged image columns. See review_required in review JSON.']
 data['model_status']='pending_rerun_after_geometry_changes'
 data['source_exclusions']=[{'character':c,'reason':'Source-only marker or unlocated character; see review notes.'} for c in data['excluded_characters']]
 (OUT/'data').mkdir(exist_ok=True);(OUT/'review').mkdir(exist_ok=True)
 (OUT/'data'/f'{code}.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 (OUT/'review'/f'{code}.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
 # Review-only native JSON. Preserve the last actual saved model/user status by its old character ID.
 native['bounding_boxes']={k:{**copy.deepcopy(saved[code]['bounding_boxes'][old]),'bbox':input_boxes[k]['bbox'],'order':int(k)} for k,old in mapping.items()}
 native['annotations']=annotations;native['bounding_box_count']=len(input_boxes)
 if code=='46303':
  native['excluded_characters']=data['excluded_characters'];native['text_sequence']=list(annotations.values())+data['excluded_characters']
  native['note']='Bản rà box: tách 9 cột thực tế. Đề xuất Excluded 〇, □ cuối cột 2, 墳 trước 地處, và hai 所 ở đầu cột 6/7; cần đối chiếu lại các vị trí mờ này. Trạng thái cần chạy lại model sau khi sửa box.'
 else:
  native['note']='Bản rà box: 設 và 表 mỗi chữ một box. Ảnh đọc 所以表; nguồn có thêm 上. MISS tại chữ 祭 trong 以供丁祭之需. Cần chạy lại model sau khi sửa box.'
  native['issue_type']=['other']
  native['excluded_characters']=['上']
 (OUT/'review_native').mkdir(exist_ok=True);(OUT/'review_full').mkdir(exist_ok=True)
 native['image_pixel_sha256']=data['image_pixel_sha256']
 native['reading_order']=data['reading_order']
 (OUT/'review_full'/f'{code}.json').write_text(json.dumps(native,ensure_ascii=False,indent=2)+'\n')
 if code=='55431': native={k:native[k] for k in ('image','inscription_code','issue_type','note','bounding_boxes')};native['bounding_boxes']={k:{'bbox':b['bbox']} for k,b in native['bounding_boxes'].items()}
 else:native.pop('image_pixel_sha256');native.pop('reading_order')
 (OUT/'review_native'/f'{code}.json').write_text(json.dumps(native,ensure_ascii=False,indent=2)+'\n')
 report[code]={'old_boxes':len(original['bounding_boxes']),'new_boxes':len(input_boxes),'changed_geometry':sum(coords[code][int(old)]!=original['bounding_boxes'][old]['bbox'] for old in mapping.values()),
 'source_only_for_review':[{'previous_id':i,'character':original['annotations'][str(i)]} for i in removed[code]],'review_required_previous_ids':sorted(uncertain[code]),'real_model_rerun':False}
 im=Image.open(ROOT/'student_114'/f'{code}.png').convert('RGB');paint=im.copy();draw=ImageDraw.Draw(paint)
 for row in review:
  col='#ffb000' if row['review_required'] else '#00e5ff';x,y,xx,yy=row['bbox']
  draw.rectangle((x,y,xx,yy),outline=col,width=1)
  # Keep the inscription legible; IDs are available in the interactive review.
 paint.save(OUT/f'{code}_revised.png')
 # Side-by-side evidence for problematic columns, at legible magnification.
 rect=(595,530,672,720) if code=='55431' else (318,310,470,880)
 before=im.copy();bd=ImageDraw.Draw(before)
 for b in original['bounding_boxes'].values():bd.rectangle(b['bbox'],outline='#ff5050',width=1)
 scale=4 if code=='55431' else 2
 a=before.crop(rect);b=paint.crop(rect);a=a.resize((a.width*scale,a.height*scale));b=b.resize(a.size)
 sheet=Image.new('RGB',(a.width*2+20,a.height+35),'white');sd=ImageDraw.Draw(sheet);sd.text((10,8),'BEFORE',font=SMALL,fill='black');sd.text((a.width+30,8),'REVISED',font=SMALL,fill='black');sheet.paste(a,(0,35));sheet.paste(b,(a.width+20,35));sheet.save(OUT/f'{code}_comparison.png')
(OUT/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
