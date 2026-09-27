"""Freeze a checked uninstalled part study without promoting it as an assembly."""
import argparse,json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[3]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--variation',type=Path,required=True);a=p.parse_args();candidate=a.candidate.resolve();variation=a.variation.resolve();deps={};counts={}
def add(f,expected=None):
 f=Path(f);f=f if f.is_absolute() else ROOT/f;digest=sha(f);assert expected is None or digest==expected,str(f);deps[str(f.relative_to(ROOT))]=digest
for folder in [candidate,variation]:
 r=read(folder/'report.json');assert sha(folder/r['native_file'])==r['native_sha256'];counts[folder.name]={}
 for name,key in [('checks03/independent_checks.json','checks'),('context_audit/report.json','pairs'),('exchange01/exchange_checks.json','checks')]:
  q=read(folder/name);assert q['passed'] and q['native_sha256']==r['native_sha256'];counts[folder.name][name]=len(q[key])
 for f,h in r['input_hashes'].items():add(f,h)
 source=ROOT/r['details']['controls']['source_review']
 for f,h in read(source)['source_hashes'].items():add(f,h)
 for f in folder.rglob('*'):
  if f.is_file() and not any(v.endswith('_runtime') or v in ['runtime','__pycache__'] for v in f.parts):add(f)
for file in ['check_driver_fulcrum_shaft.py','render_driver_fulcrum_shaft.py','qualify_driver_fulcrum_shaft.py','check_control_rebuild_context.py','exchange_control_rebuild_clutch_swing.py','check_control_rebuild_reproduction.py','verify_driver_fulcrum_shaft.py']:add(H/file)
r=read(candidate/'report.json');visual=read(candidate/'visual_review.json');repro=read(candidate/'reproduction_checks.json');assert visual['disposition']=='reviewed_uninstalled_part_hypothesis' and visual['native_sha256']==r['native_sha256'];assert repro['passed'] and repro['native_sha256']==r['native_sha256']
q=dict(local_part_checks_passed=True,native_sha256=r['native_sha256'],physical_occurrences=5,new_definitions=2,reused_definitions=['Def_TransmissionPin_nut'],variation=str(variation.relative_to(ROOT)),checks=counts,geometry_integrated=False,installation_qualified=False,historical_geometry_qualified=False,standard_assembly_modified=False,dependencies=deps,open_issues=['M746/M747 support grip, complete mounting on actual sloping floor and M783 second-shaft layout still required.','Reduced ends, thread envelopes, nut seating and outboard short-cotter retention are explicit hypotheses. The existing estimated M313 castle form is reused, not newly historically qualified.','This part study does not establish final driver lever, selector, bridle, connecting-rod or operating geometry.'])
path=candidate/'part_qualification.json';assert not path.exists();path.write_text(json.dumps(q,indent=2)+'\n');print('Uninstalled part study frozen:',len(deps),'dependencies',flush=True)
