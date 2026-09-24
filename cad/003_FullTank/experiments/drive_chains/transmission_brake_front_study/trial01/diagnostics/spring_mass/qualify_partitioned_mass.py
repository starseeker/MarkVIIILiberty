"""Analytic controls and deliberate failures for partitioned mass integration."""
import sys,json,math
from pathlib import Path
import FreeCAD as App
import Part
ROOT=Path('/home/cyapp/MarkVIIILiberty');sys.path.insert(0,str(ROOT/'cad/003_FullTank'))
from lib.mass_properties import AdaptiveMass
from lib.partitioned_mass import PartitionedMass
mass=AdaptiveMass(Path('mass'));partitioned=PartitionedMass(mass,Path('partitioned'));checks=[]
box=Part.makeBox(20,30,40);cylinder=Part.makeCylinder(12,100)
pose=App.Placement(App.Vector(1234,-987,650),App.Rotation(App.Vector(1,2,3),37))
for name,s,center,volume,frame in [('box',box,App.Vector(10,15,20),24000,App.Placement()),
                                 ('placed_box',box.copy(),App.Vector(10,15,20),24000,pose),
                                 ('cylinder',cylinder,App.Vector(0,0,50),math.pi*12**2*100,App.Placement())]:
    s.Placement=frame;result=partitioned.measure(s,frame)
    dv=abs(result['volume_mm3']-volume);dc=(App.Vector(*result['centroid_mm'])-frame.multVec(center)).Length
    checks.append(dict(name=name,passed=result['converged'] and dv<1e-5 and dc<1e-6,volume_error_mm3=dv,centroid_error_mm=dc))
    print(checks[-1],flush=True)
pieces=[box.common(Part.makeBox(20,30,10,App.Vector(0,0,10*i))) for i in range(4)]
for name,selected,expected in [('intact',pieces,True),('missing_section',pieces[:-1],False),('duplicate_section',[pieces[0]]+pieces,False)]:
    result=partitioned.certificate(box,selected);checks.append(dict(name=name,passed=result['passed']==expected,certificate=result));print(checks[-1],flush=True)
displaced=[p.copy() for p in pieces];displaced[1].translate(App.Vector(.01,0,0))
result=partitioned.certificate(box,displaced);checks.append(dict(name='displaced_section',passed=not result['passed'],certificate=result));print(checks[-1],flush=True)
record=dict(passed=all(v['passed'] for v in checks),checks=checks,provenance=partitioned.provenance)
Path('report.json').write_text(json.dumps(record,indent=2)+'\n');assert record['passed']
