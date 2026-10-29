from pathlib import Path
from contextlib import redirect_stdout
from types import SimpleNamespace
from collections import Counter
import json,runpy,sys,tempfile,zipfile,io,os
repo=Path(os.environ.get('SINONOM_REPO_DIR','/tmp/sinonom-status-inspect'));root=Path(__file__).resolve().parents[1];package=Path(__file__).resolve().parent/'kaggle';sys.path[:0]=[str(repo),str(repo/'gradio')]
job=runpy.run_path(str(package/'apply_revision.py'))
runpy.run_path(str(package/'annotations/_support/content_base.py'))['enable_saved_content_sections'](repo)
Workflow=runpy.run_path(str(package/'annotations/_support/launch_with_original_source.py'))['install_mixed_review'](repo)
source=root/'student_114/student_114.json';before=source.read_bytes()
with tempfile.TemporaryDirectory() as temporary:
 output=Path(temporary)/'annotations'
 with redirect_stdout(io.StringIO()):job['apply'](repo,root/'student_114',output,predict=lambda r,ims:{p.stem:[] for p in ims})
 opts=SimpleNamespace(output_dir=output,source_json=source,content_titles=('Nguyên văn chữ Hán Nôm','Phiên âm Hán Việt','Toát yếu'),annotation_title='Nguyên văn chữ Hán Nôm',skip_detection=True,metadata_fields=(('Tên bia','ten_bia'),('Địa điểm','dia_diem'),('Niên đại','nien_dai')))
 engine=Workflow(opts)
 count=0
 for p in list(output.glob('*.json'))+list((output/'source_mismatches').glob('*.json')):
  d=json.loads(p.read_text());state=engine.open_image(root/'student_114'/d['image']);count+=len(state['regions'])
  if p.stem in ('55431','46303'):
   full=json.loads((output/'model_reviews'/p.name).read_text())
   assert state['annotations']==full['annotations']
   state=engine.apply(state,'next');assert state['annotations']==full['annotations']
   state=engine.apply(state,'next');assert state['current_step']==4
  else:
   assert d==json.loads((package/'annotations'/p.relative_to(output)).read_text())
 assert count==1421,count
 with zipfile.ZipFile(output.parent/'my_annotations_backup.zip') as z:
  assert z.testzip() is None
  assert len(json.loads(z.read('user_work_manifest.json'))['images'])==7
 engine._preview_cache.cleanup()
 assert source.read_bytes()==before
 # A novel hand-adjusted box must be rejected before inference.
 path=output/'source_mismatches/46303.json';doc=json.loads(path.read_text());doc['bounding_boxes']['1']['bbox'][0]+=1;path.write_text(json.dumps(doc))
 snapshot={p.relative_to(output):p.read_bytes() for p in output.rglob('*') if p.is_file()}
 try:job['apply'](repo,root/'student_114',output,predict=lambda *_: (_ for _ in ()).throw(AssertionError('should not run')))
 except ValueError as e:assert 'Có box mới' in str(e)
 else:raise AssertionError('should reject')
 assert snapshot=={p.relative_to(output):p.read_bytes() for p in output.rglob('*') if p.is_file()}
print('PASS: seven-image native reload, both revised mappings, original source and other five preserved, backup and overwrite protection. Inference MOCKED only.')
