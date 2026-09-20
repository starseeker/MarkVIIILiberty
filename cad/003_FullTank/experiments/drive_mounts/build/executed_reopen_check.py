from pathlib import Path
import sys,subprocess
sys.path.insert(0,'/home/cyapp/MarkVIIILiberty/cad/003_FullTank')
from lib.runtime import environment
from lib.evidence import STAGE,read,write,sha
root=STAGE/'experiments/drive_mounts';out=root/'build'
if '--worker' not in sys.argv:sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=environment(out)).returncode)
import FreeCAD as App
from lib.roller_validation import bearing_face
report=read(out/'report.json');assert report['passed']
p=out/'DriveMountStudy.FCStd';assert sha(p)==report['native_sha256']
doc=App.openDocument(str(p));doc.recompute();items={};valid=set()
for link in doc.Fixture.Group:
 target=link.LinkedObject
 if target.Name not in valid:
  assert target.Shape.isValid() and len(target.Shape.Solids)==1;valid.add(target.Name)
 shape=target.Shape.copy();shape.Placement=link.Placement.multiply(shape.Placement);items[link.Name]=shape
assert len(items)==151
seats=[]
for pair in report['bearing_faces']:
 gap,area=bearing_face(items[pair['a']],items[pair['b']]);assert gap<1e-5 and area>1e-4,pair
 seats.append(dict(a=pair['a'],b=pair['b'],gap_mm=gap,area_mm2=area))
a=read(root/'hypotheses.json')['values_mm'];dims=[]
for name,axis,wanted in [('Shaft','Y',a['shaft_length']),('Shaft','X',a['shaft_diameter']),
 ('Key','X',a['key_width']),('Key','Y',a['key_length']),('Key','Z',a['key_height'])]:
 actual=getattr(items[name].optimalBoundingBox(False),axis+'Length');assert abs(actual-wanted)<1e-5
 dims.append(dict(part=name,axis=axis,actual_mm=actual,expected_mm=wanted))
nut=items['NutOuter'].copy();nut.translate(App.Vector(0,.2,0))
gap,area=bearing_face(nut,items['BearingOuter']);assert gap>.19 and area<1e-4
write(out/'reopened.json',dict(passed=True,native_sha256=sha(p),valid_definitions=len(valid),occurrences=len(items),
 bearing_faces=seats,printed_dimensions=dims,negative_nut_displacement_mm=.2,negative_gap_mm=gap,
 limitation='Isolated mounting fixture with two proxy receiver coupons; actual hull identity/fit remains unqualified.'))
App.closeDocument(doc.Name);print('REOPENED MOUNT FIXTURE PASSED',len(seats),'seats',flush=True)
