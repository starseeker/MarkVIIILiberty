"""Independent analytic mass controls, including an exact quadratic B-spline prism."""
import argparse,math,sys
from pathlib import Path
import FreeCAD as A
import Part
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'cad/003_FullTank'))
from lib.kronrod_mass import KronrodMass
from lib.evidence import write,sha
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
out=args.output.resolve();out.mkdir(parents=True);mass=KronrodMass(out/'runtime');V=A.Vector;checks=[]
curve=Part.BSplineCurve();curve.buildFromPolesMultsKnots([V(0,0,0),V(1,0,0),V(2,0,4)],[3,3],[0.,1.],False,2)
wire=Part.Wire([curve.toShape(),Part.makeLine(V(2,0,4),V(2,0,0)),Part.makeLine(V(2,0,0),V())]);prism=Part.Face(wire).extrude(V(0,5,0))
for label,s,volume,center in [('box',Part.makeBox(13,17,23),13*17*23,V(6.5,8.5,11.5)),('annulus',Part.makeCylinder(12,27).cut(Part.makeCylinder(5,27)),math.pi*(144-25)*27,V(0,0,13.5)),('quadratic_prism',prism,40/3,V(1.5,2.5,1.2))]:
 for moved in [False,True]:
  frame=A.Placement(V(100,-170,250),A.Rotation(V(1,2,3),37)) if moved else A.Placement();shape=s.copy();shape.Placement=frame;expected=frame.multVec(center);before=out/(label+str(moved)+'.brep');shape.exportBrep(str(before));digest=sha(before)
  result=mass.measure(shape);shape.exportBrep(str(before));error=math.dist(result['centroid_mm'],list(expected));row=dict(label=label,transformed=moved,passed=result['converged'] and abs(result['volume_mm3']-volume)<1e-5 and error<1e-6 and sha(before)==digest,expected_volume_mm3=volume,expected_centroid_mm=list(expected),result=result);checks.append(row);print(label,moved,row['passed'],flush=True)
try:mass.measure(Part.Face(wire));rejected=False
except AssertionError:rejected=True
checks.append(dict(label='open face rejected',passed=rejected))
write(out/'qualification.json',dict(passed=all(v['passed'] for v in checks),checks=checks,provenance=mass.provenance,scope='Known analytic and exact B-spline prism mass/centroid controls, rigid transforms, unchanged BReps and open-face rejection. Actual lever exchange remains separate.'))
print('Kronrod controls:',len(checks),all(v['passed'] for v in checks),flush=True);assert all(v['passed'] for v in checks)
