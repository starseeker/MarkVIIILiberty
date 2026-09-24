"""Check saved integration and exact geometry/frame transfer from tested prototype."""
import argparse,sys
from pathlib import Path
H=Path(__file__).resolve().parent;STAGE=H.parents[1];ROOT=STAGE.parents[1];sys.path.insert(0,str(STAGE))
from lib.evidence import read,write,sha
from lib.camera_review import validate_native_bindings
import FreeCAD as App
import Part
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve()
r=read(out/'report.json');m=read(out/'isolated/manifest.json');source=ROOT/r['source_native'];old=read(source.parent/'isolated/manifest.json')
native=out/r['native_file'];assert sha(native)==r['native_sha256']==m['native_sha256']
assert sha(source)==r['source_native_sha256']==old['native_sha256']
rows,prior=[{v['name']:v for v in t['occurrences']} for t in [m,old]];checks=[]
def ck(name,passed,**details):checks.append(dict(name=name,passed=bool(passed),**details))
ck('Eight new occurrences, three definitions and two assembly groups',len(rows)==3173 and len(m['definitions'])==545 and len(m['assemblies'])==338 and set(rows)-set(prior)==set(r['expected_new_occurrences']))
ck('All inherited occurrence definitions, owners and frames retained',all(rows[n]['definition']==v['definition'] and rows[n]['owners']==v['owners'] and max(abs(x-y) for x,y in zip(rows[n]['frame'],v['frame']))<1e-7 for n,v in prior.items()))
ck('Inherited assembly frames and child relationships retained',all(max(abs(x-y) for x,y in zip(g['world'],m['assemblies'][n]['world']))<1e-7 and max(abs(x-y) for x,y in zip(g['local'],m['assemblies'][n]['local']))<1e-7 and set(m['assemblies'][n]['children'])==set(g['children'])|set(r['added_children'].get(n,[])) for n,g in old['assemblies'].items()))
ck('Definition set preserves parent and adds only declared roles',set(m['definitions'])==set(old['definitions'])|set(r['new_definitions']))
ck('New native frames and owners match intended hierarchy',all(rows[n]['definition']==v['definition'] and rows[n]['owners']==v['owners'] and max(abs(x-y) for x,y in zip(rows[n]['frame'],v['frame']))<1e-7 for n,v in r['expected_new_occurrences'].items()))
validate_native_bindings(dict(native_file=str(native),render_occurrences=r['affected_occurrences'],landmarks=[]),m)
prototype=ROOT/r['prototype'];pnative=prototype/read(prototype/'report.json')['native_file'];assert sha(pnative)==r['prototype_native_sha256']
doc=App.openDocument(str(pnative));pshapes={};pframes={}
try:
 for role in ['fork','pin','cotter','nut']:pshapes[role]=doc.getObject('Def_'+role).Shape.copy()
 for name,spec in read(prototype/'report.json')['specs'].items():
  link=doc.getObject(name);pframes[name]=list(doc.getObject(spec['owner']).getGlobalPlacement().multiply(link.LinkPlacement).toMatrix().A)
finally:App.closeDocument(doc.Name)
for role,one in pshapes.items():
 key=r['shared_definitions'].get(role,'Def_ControlJoint_'+role)
 d=m['definitions'][key];assert sha(d['brep_path'])==d['brep_sha256'];two=Part.Shape();two.read(d['brep_path'])
 ta,tb=one.getTolerance(1),two.getTolerance(1);fuzzy=min(1e-4,max(1e-7,ta+tb));missing,added=one.cut(two),two.cut(one)
 fm,fa=len(one.cut(two,fuzzy).Faces),len(two.cut(one,fuzzy).Faces)
 ck(role+' saved integration retains tested prototype material',one.isValid() and two.isValid() and len(one.Solids)==len(two.Solids)==1 and abs(missing.Volume)<1e-5 and abs(added.Volume)<1e-5 and not fm and not fa and tb<=max(ta,1e-7)+1e-10,
    missing_mm3=missing.Volume,added_mm3=added.Volume,fuzzy_missing_faces=fm,fuzzy_added_faces=fa,native_tolerance_mm=tb,prototype_tolerance_mm=ta)
mapping={n:v['prototype_occurrence'] for n,v in r['expected_new_occurrences'].items()}
for n,pn in mapping.items():
 error=max(abs(x-y) for x,y in zip(rows[n]['frame'],pframes[pn]));ck(n+' frame preserves tested prototype placement',error<1e-7,max_error=error)
dependencies=[]
for path in [prototype/'independent_checks.json',prototype/'exchange_checks.json']:
 report=read(path);assert report['passed'];dependencies.append(dict(path=str(path.relative_to(ROOT)),sha256=sha(path)))
write(out/'independent_checks.json',dict(passed=all(v['passed'] for v in checks),checks=checks,native_sha256=sha(native),source_native_sha256=sha(source),prototype_native_sha256=sha(pnative),checker_sha256=sha(Path(__file__)),prototype_checks=dependencies,
 scope='Saved counts/hierarchy, inherited occurrence frames, and strict material/placement transfer for the four tested prototype definitions and8 occurrences. Whole-parent definition preservation and standard-tank context remain separate gates.',
 historical_geometry_qualified=False,installation_qualified=False,packet_complete=False))
print('Saved integration checks',len(checks),'passed',all(v['passed'] for v in checks),flush=True)
assert all(v['passed'] for v in checks)
