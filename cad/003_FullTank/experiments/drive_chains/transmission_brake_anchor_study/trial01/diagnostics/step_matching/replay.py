"""Replay completed STEP pair selection using cached imported mass properties."""
from pathlib import Path
import json,time,sys,hashlib
import FreeCAD as App
import Part
ROOT=Path('/home/cyapp/MarkVIIILiberty');H=ROOT/'cad/003_FullTank/experiments/drive_chains';out=H/'transmission_brake_anchor_study/trial01'
def read(p):return json.loads(p.read_text())
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
r=read(out/'report.json');m=read(out/'isolated/manifest.json');base_bytes=(out/'exchange_checks.json').read_bytes();base=json.loads(base_bytes);assert base['passed'];records=base['checks'];rows={v['name']:v for v in m['occurrences']};cache={};results=[];stats=[]
assert sha(out/r['native_file'])==r['native_sha256']==m['native_sha256']==base['native_sha256']
sys.path.insert(0,str(H.parents[1]))
from lib.step_matching import StepSolidMatcher
def native(name,scope):
 key=name if scope=='Definitions' else rows[name]['definition']
 if key not in cache:
  entry=m['definitions'][key];assert sha(Path(entry['brep_path']))==entry['brep_sha256'];s=Part.Shape();s.read(entry['brep_path']);cache[key]=s
 s=cache[key].copy()
 if scope=='Installation':s.Placement=App.Placement(App.Matrix(*rows[name]['frame']))
 return s
for scope in ['Definitions','Installation']:
 start=time.monotonic();path=out/('BrakeAnchors'+scope+'.step');s=Part.Shape();s.read(str(path));matcher=StepSolidMatcher(s.Solids);cache_seconds=time.monotonic()-start
 requested=[row for row in records if row['scope']==scope];old_integrations=0;start=time.monotonic()
 for row in requested:
  one=native(row['name'],scope)
  old_integrations+=len(matcher)
  index,selected=matcher.pop(one);assert index==row['imported_solid_index'],row['name'];results.append(dict(scope=scope,name=row['name'],same_imported_solid_index=index))
 assert not len(matcher)
 stats.append(dict(scope=scope,step_sha256=sha(path),imported_solids=len(s.Solids),replayed_pairs=len(requested),old_imported_centroid_and_volume_evaluations_each=old_integrations,cached_imported_centroid_and_volume_evaluations_each=len(s.Solids),load_and_cache_seconds=cache_seconds,matching_seconds=time.monotonic()-start))
assert len(records)==342
result=dict(passed=True,scope='Pair-selection replay only; strict geometry acceptance remains the separate complete exchange check.',native_sha256=r['native_sha256'],exchange_report_sha256=hashlib.sha256(base_bytes).hexdigest(),matcher_sha256=sha(H.parents[1]/'lib/step_matching.py'),record_count=len(records),checks=results,stats=stats)
Path('report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,record_count=len(records),stats=stats),indent=2))
