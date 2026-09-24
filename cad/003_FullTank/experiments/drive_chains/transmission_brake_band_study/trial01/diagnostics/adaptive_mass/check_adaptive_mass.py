import sys,json,math
from pathlib import Path
ROOT=Path('/home/cyapp/MarkVIIILiberty');sys.path.insert(0,str(ROOT/'cad/003_FullTank'))
import FreeCAD as App
import Part
from lib.mass_properties import AdaptiveMass
m=AdaptiveMass(Path.cwd()/'runtime');checks=[]
# Off-origin holed cylinder: analytic volume and centroid are independent of
# the helper implementation, including a nontrivial installation transform.
s=Part.makeCylinder(12,40).cut(Part.makeCylinder(8,42,App.Vector(0,0,-1)))
pose=App.Placement(App.Vector(400,-600,1200),App.Rotation(App.Vector(1,2,3),33));s.Placement=pose
d=m.measure(s);expected=pose.multVec(App.Vector(0,0,20))
checks.append(dict(name='analytic sleeve',passed=d['converged'] and abs(d['volume_mm3']-math.pi*(144-64)*40)<1e-5
 and math.dist(d['centroid_mm'],list(expected))<1e-6,measurement=d))
for name in ['low_lining','track_lining','low_band','track_band']:
 a=Part.Shape();a.read(str(ROOT/'.work/transmission-brake-bands/probe01'/(name+'.brep')))
 b=Part.Shape();b.read(str(ROOT/'.work/transmission-brake-bands/probe01'/(name+'.step')))
 one,two=m.measure(a),m.measure(b);dv=abs(one['volume_mm3']-two['volume_mm3']);dc=math.dist(one['centroid_mm'],two['centroid_mm'])
 checks.append(dict(name=name,passed=one['converged'] and two['converged'] and dv<1e-5 and dc<1e-5,
  volume_error_mm3=dv,centroid_error_mm=dc,native=one,step=two))
 moved=b.copy();moved.translate(App.Vector(.01,0,0));shift=m.measure(moved)
 checks.append(dict(name=name+' displaced negative control',passed=math.dist(one['centroid_mm'],shift['centroid_mm'])>0.009))
 print(name,checks[-2]['passed'],dv,dc,flush=True)
result=dict(passed=all(v['passed'] for v in checks),checks=checks,provenance=m.provenance)
Path('adaptive_checks.json').write_text(json.dumps(result,indent=2));assert result['passed']
