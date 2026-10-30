"""Make an offline box viewer; annotations remain read-only here."""
import base64
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
data = {}
for code in ('17077', '18592'):
    data[code] = {
        'image': 'data:image/jpeg;base64,' + base64.b64encode((HERE.parent / 'student_114' / (code + '.jpg')).read_bytes()).decode(),
        'rows': json.loads((HERE / 'review' / (code + '.json')).read_text()),
        'unlocated': json.loads((HERE / 'review/18592_unlocated.json').read_text()) if code == '18592' else {},
    }
html = '''<!doctype html><html lang="vi"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rà box 17077 và 18592</title>
<style>
body{margin:20px;background:#141719;color:#eee;font:16px system-ui}
button,select{font:inherit;padding:8px;margin:4px;background:#292e32;color:white;border:1px solid #666;border-radius:5px}
.tools{position:sticky;top:0;background:#141719;padding:8px;z-index:2}
.panes{display:grid;grid-template-columns:minmax(250px,1fr) minmax(300px,1fr);gap:16px}
canvas{width:100%;height:auto;background:#292e32}#detail{position:sticky;top:120px}
#unlocated{white-space:pre-line}
#note{max-width:950px;min-height:55px}.muted{color:#bec4c9;font-size:14px}
@media(max-width:700px){.panes{grid-template-columns:1fr}#detail{position:static}}
</style>
<h2>Rà vị trí box — 17077 và 18592</h2>
<p>18592 còn là bản nháp. Màu xanh: đã xem vị trí; vàng: cần rà. Màu box không biểu thị Intact/Damaged.</p>
<div class="tools"><select id="face"><option>17077</option><option>18592</option></select>
<label><input type="checkbox" id="uncertain"> Chỉ ô cần rà</label>
<button id="prev">←</button><select id="box"></select><button id="next">→</button>
<div id="note"></div></div>
<details><summary>Các vị trí nguồn chưa ghép được — vẫn giữ nguyên trong Content</summary><p id="unlocated"></p></details>
<div class="panes"><canvas id="overview"></canvas><div><canvas id="detail"></canvas></div></div>
<p class="muted">Chọn số box hoặc bấm vào ảnh tổng thể. Trang này chỉ để xem; sửa và lưu trên app Kaggle.
Giữ nguyên Content Hán Nôm ngoài chuẩn hóa dấu ngoặc và [].</p>
<script>
const data=__DATA__;
const face=document.getElementById('face'),box=document.getElementById('box'),uncertain=document.getElementById('uncertain');
const overview=document.getElementById('overview'),detail=document.getElementById('detail');
let picture=new Image(), rows=[];
function options(){
 document.getElementById('unlocated').textContent=(data[face.value].unlocated.excluded_source_positions||[]).map(r=>`${r.source_index}: ${r.character} — ${r.reason}`).join(String.fromCharCode(10));
 const prior=Number(box.value); rows=data[face.value].rows.filter(r=>!uncertain.checked||r.review_required);
 box.replaceChildren(...rows.map(r=>{let o=document.createElement('option');o.value=r.id;o.textContent=`${r.id}: ${r.character}${r.review_required?' • cần rà':''}`;return o;}));
 if(rows.some(r=>r.id===prior))box.value=prior;draw();
}
function load(){const selected=face.value;let next=new Image();next.onload=()=>{if(face.value===selected){picture=next;options();}};next.src=data[selected].image;}
function draw(){
 if(!picture.naturalWidth)return;
 overview.width=1300;overview.height=Math.round(picture.naturalHeight*1300/picture.naturalWidth);
 const ctx=overview.getContext('2d'),scale=1300/picture.naturalWidth;
 ctx.drawImage(picture,0,0,overview.width,overview.height);
 for(const r of (data[face.value].unlocated.unresolved_image_regions||[])){let [x,y,xx,yy]=r.bbox;ctx.strokeStyle='#cc66ff';ctx.setLineDash([8,5]);ctx.lineWidth=2;ctx.strokeRect(x*scale,y*scale,(xx-x)*scale,(yy-y)*scale);ctx.setLineDash([]);}
 const current=rows.find(r=>r.id===Number(box.value));
 for(const r of data[face.value].rows){let [x,y,xx,yy]=r.bbox;ctx.strokeStyle=r.id===current?.id?'#ff4173':r.review_required?'#ffb000':'#00ddff';ctx.lineWidth=r.id===current?.id?4:1;ctx.strokeRect(x*scale,y*scale,(xx-x)*scale,(yy-y)*scale);}
 detail.width=900;detail.height=900;const d=detail.getContext('2d');d.fillStyle='#292e32';d.fillRect(0,0,900,900);
 if(!current){document.getElementById('note').textContent='Không có ô cần rà trong bộ lọc này. Đây không phải xác nhận nhãn hỏng hay phiên đọc.';return;}
 const [x,y,xx,yy]=current.bbox,side=Math.max(xx-x,yy-y)+180;
 const sx=(x+xx-side)/2,sy=(y+yy-side)/2,z=900/side;
 d.drawImage(picture,sx,sy,side,side,0,0,900,900);d.strokeStyle='#ff4173';d.lineWidth=3;d.strokeRect((x-sx)*z,(y-sy)*z,(xx-x)*z,(yy-y)*z);
 document.getElementById('note').textContent=`Box ${current.id} · số cũ ${current.previous_id}`+(current.source_index?` · vị trí nguồn ${current.source_index}`:'')+` · nhãn ${current.character}`+(current.source_character?` · nguồn ${current.source_character} / ảnh dự kiến ${current.observed_character}`:'')+` — ${current.reason}`;
}
face.onchange=load;uncertain.onchange=options;box.onchange=draw;
document.getElementById('prev').onclick=()=>{box.selectedIndex=Math.max(0,box.selectedIndex-1);draw();};
document.getElementById('next').onclick=()=>{box.selectedIndex=Math.min(box.options.length-1,box.selectedIndex+1);draw();};
overview.onclick=e=>{const b=overview.getBoundingClientRect(),x=(e.clientX-b.left)/b.width*picture.naturalWidth,y=(e.clientY-b.top)/b.height*picture.naturalHeight;
 const candidates=rows.filter(r=>x>=r.bbox[0]&&x<=r.bbox[2]&&y>=r.bbox[1]&&y<=r.bbox[3]);
 candidates.sort((a,b)=>(a.bbox[2]-a.bbox[0])*(a.bbox[3]-a.bbox[1])-(b.bbox[2]-b.bbox[0])*(b.bbox[3]-b.bbox[1]));
 if(candidates.length){box.value=candidates[0].id;draw();}};
load();
</script></html>'''
(HERE / 'review.html').write_text(html.replace('__DATA__', json.dumps(data, ensure_ascii=False).replace('</', '<\\/')), encoding='utf-8')
