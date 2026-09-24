"""Replay adaptive-mass qualification directly from the retained native and STEP."""
import argparse,json,math,sys
from pathlib import Path
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'cad/003_FullTank/lib').is_dir())
sys.path.insert(0,str(ROOT/'cad/003_FullTank'))
from lib.evidence import read,write,sha
from lib.mass_properties import AdaptiveMass
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,default=Path(__file__).resolve().parents[2])
p.add_argument('--output',type=Path,required=True)
a=p.parse_args();candidate=a.candidate.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
r=read(candidate/'report.json');ex=read(candidate/'exchange_checks.json')
assert sha(candidate/r['native_file'])==r['native_sha256']==ex['native_sha256']
assert all(sha(candidate/f)==v for f,v in ex['step_hashes'].items())
import FreeCAD as App
import Part
mass=AdaptiveMass(out/'runtime');checks=[]
doc=App.openDocument(str(candidate/r['native_file']))
names=['Def_BrakeBand_'+n for n in ['low_lining','track_lining','low_band','track_band']]
native={n:doc.getObject(n).Shape.copy() for n in names};App.closeDocument(doc.Name)
step=Part.Shape();step.read(str(candidate/'BrakeBandsDefinitions.step'))
indices={v['name']:v['imported_solid_index'] for v in ex['checks'] if v['scope']=='Definitions'}
s=Part.makeCylinder(12,40).cut(Part.makeCylinder(8,42,App.Vector(0,0,-1)))
pose=App.Placement(App.Vector(400,-600,1200),App.Rotation(App.Vector(1,2,3),33));s.Placement=pose
d=mass.measure(s);point=pose.multVec(App.Vector(0,0,20))
checks.append(dict(name='analytic sleeve',passed=d['converged'] and abs(d['volume_mm3']-math.pi*80*40)<1e-5
    and math.dist(d['centroid_mm'],list(point))<1e-6,measurement=d))
for name in names:
    one=native[name];two=step.Solids[indices[name]];ma,mb=mass.measure(one),mass.measure(two)
    dv=abs(ma['volume_mm3']-mb['volume_mm3']);dc=math.dist(ma['centroid_mm'],mb['centroid_mm'])
    checks.append(dict(name=name,passed=ma['converged'] and mb['converged'] and dv<1e-5 and dc<1e-5,
        volume_error_mm3=dv,centroid_error_mm=dc,native=ma,step=mb))
    moved=two.copy();moved.translate(App.Vector(.01,0,0));negative=mass.measure(moved)
    checks.append(dict(name=name+' displaced negative control',passed=math.dist(ma['centroid_mm'],negative['centroid_mm'])>.009))
result=dict(passed=all(v['passed'] for v in checks),checks=checks,provenance=mass.provenance,replay_sha256=sha(Path(__file__)))
write(out/'replay_checks.json',result);print('Adaptive replay:',len(checks),'checks, passed',result['passed'],flush=True)
assert result['passed']
