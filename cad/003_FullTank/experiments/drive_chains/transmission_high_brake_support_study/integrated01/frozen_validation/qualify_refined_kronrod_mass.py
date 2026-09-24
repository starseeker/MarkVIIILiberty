"""Analytic controls for tighter quadrature, including a tank-scale curved solid."""
import argparse,math,sys
from pathlib import Path
import FreeCAD as A
import Part
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'cad/003_FullTank'))
from lib.refined_kronrod_mass import RefinedKronrodMass
from lib.evidence import write,sha
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert not out.exists();out.mkdir(parents=True)
mass=RefinedKronrodMass(out/'runtime');V=A.Vector;checks=[]
def prism(scale):
 curve=Part.BSplineCurve();curve.buildFromPolesMultsKnots([V(),V(scale,0,0),V(2*scale,0,4*scale)],[3,3],[0.,1.],False,2)
 wire=Part.Wire([curve.toShape(),Part.makeLine(V(2*scale,0,4*scale),V(2*scale,0,0)),Part.makeLine(V(2*scale,0,0),V())])
 return Part.Face(wire).extrude(V(0,5*scale,0)),Part.Face(wire)
small,face=prism(1);large,_=prism(100)
for label,s,volume,center in [('box',Part.makeBox(13,17,23),13*17*23,V(6.5,8.5,11.5)),
 ('annulus',Part.makeCylinder(12,27).cut(Part.makeCylinder(5,27)),math.pi*(144-25)*27,V(0,0,13.5)),
 ('quadratic_prism',small,40/3,V(1.5,2.5,1.2)),('large_quadratic_prism',large,40e6/3,V(150,250,120))]:
 for moved in [False,True]:
  frame=A.Placement(V(100,-170,250),A.Rotation(V(1,2,3),37)) if moved else A.Placement()
  shape=s.copy();shape.Placement=frame;expected=frame.multVec(center);path=out/(label+str(moved)+'.brep');shape.exportBrep(str(path));before=sha(path)
  result=mass.measure(shape);shape.exportBrep(str(path));error=math.dist(result['centroid_mm'],list(expected))
  passed=result['converged'] and abs(result['volume_mm3']-volume)<1e-5 and error<1e-6 and sha(path)==before
  checks.append(dict(label=label,transformed=moved,passed=passed,expected_volume_mm3=volume,expected_centroid_mm=list(expected),result=result));print(label,moved,passed,flush=True)
try:mass.measure(face);rejected=False
except AssertionError:rejected=True
checks.append(dict(label='open face rejected',passed=rejected))
write(out/'qualification.json',dict(passed=all(v['passed'] for v in checks),checks=checks,provenance=mass.provenance,
 scope='Eight independent analytic mass/centroid and rigid-frame controls through 13.33 million mm3, unchanged input BReps, and open-face rejection. Actual receiver case exchange is separate.'))
assert all(v['passed'] for v in checks)
