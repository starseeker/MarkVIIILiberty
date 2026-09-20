"""Fresh native placement, count and bearing checks for the pinion rotor study."""
from pathlib import Path
from collections import Counter
import sys,subprocess,math,shutil
ROOT=Path(__file__).resolve().parent;STAGE=ROOT.parents[1];OUT=ROOT/'pin_build';sys.path.insert(0,str(STAGE))
from lib.runtime import environment
if '--worker' not in sys.argv:sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=environment(OUT)).returncode)
import FreeCAD as App
from lib.evidence import read,write,sha
from lib.roller_validation import bearing_face
from lib.visual_review import shaded
report=read(OUT/'report.json');native=OUT/'PinionWithPins.FCStd';assert report['passed'] and sha(native)==report['native_sha256']
a=read(ROOT/'rotor_build/hypotheses.json')['values_mm'];p=read(OUT/'hypotheses.json')['values_mm']
doc=App.openDocument(str(native));doc.recompute();items={};counts=Counter();source_counts=Counter()
for obj in doc.Objects:
 if obj.TypeId!='App::Link':continue
 target=obj.LinkedObject;shape=target.Shape.copy();shape.Placement=obj.Placement.multiply(shape.Placement)
 assert shape.isValid() and len(shape.Solids)==1
 role=target.Name.removeprefix('Def_');counts[role]+=1;source_counts[target.SurveyId]+=1
 items[obj.Name]=dict(id=obj.Name,definition=target.Name,target=target,shape=shape,system='RunningGear',representation='assembly')
assert dict(counts)==report['source_leaf_counts'] and len(items)==73
poses=[];seats=[];gaps=[];drill=[]
for side,label in [(1,'A'),(-1,'B')]:
 for n in range(9):
  name=label+str(n);t=2*math.pi*n/9;x=a['roller_circle']*math.sin(t);z=a['roller_circle']*math.cos(t)
  rot=App.Rotation(App.Vector(0,1,0),n*40).multiply(App.Rotation(App.Vector(0,0,1),0 if side==1 else 180))
  pose=App.Placement(App.Vector(x,side*p['pin_start'],z),rot)
  wanted={'Pin':pose,'Cotter':pose.multiply(App.Placement(App.Vector(0,p['cotter_from_inner_end'],0),App.Rotation())),
          'Plug':pose.multiply(App.Placement(App.Vector(0,p['pin_length'],0),App.Rotation())),
          'Roller':App.Placement(App.Vector(x,side*a['bank_center'],z),App.Rotation())}
  for role,expected in wanted.items():
   actual=doc.getObject(role+name).Placement;err=(actual.Base-expected.Base).Length
   assert err<1e-6 and actual.Rotation.isSame(expected.Rotation,1e-7),(name,role,err)
   poses.append(dict(part=role+name,translation_error_mm=err))
  pin=items['Pin'+name]['shape'];gap,area=bearing_face(pin,items['Casting']['shape']);assert gap<1e-5 and area>1
  seats.append(dict(pin=name,gap_mm=gap,area_mm2=area))
  gap=pin.distToShape(items['Roller'+name]['shape'])[0];assert abs(gap-.1)<1e-5;gaps.append(gap)
  target=doc.Def_Pin.Shape
  # The axial gallery and radial lead must intersect at the roller station;
  # witness material away from those bores prevents an empty-shape false pass.
  for point in [(0,p['pin_length']-4,0),(0,p['roller_axis_on_pin'],0),(p['pin_diameter']/2-1,p['roller_axis_on_pin'],0)]:
   assert not target.isInside(App.Vector(*point),1e-7,True)
  assert target.isInside(App.Vector(10,40,0),1e-7,True)
  drill.append(name)
# Regression witness: axial movement of a pin destroys its factory-head seat.
shifted=items['PinA0']['shape'].copy();shifted.translate(App.Vector(0,.2,0));gap,area=bearing_face(shifted,items['Casting']['shape']);assert area<1
for name,direction in [('oblique',(1,1,.6)),('axial',(0,1,0))]:
 shaded(list(items.values()),OUT/(name+'.svg'),direction,'Pinion rotor fixture |73 source leaves |shaft/mounts and installed cotter forming pending')
write(OUT/'reopened.json',dict(passed=True,native_sha256=sha(native),script_sha256=sha(__file__),physical_occurrences=73,
 source_identity_counts=dict(source_counts),rigid_placements=poses,pin_head_seats=seats,roller_pin_gaps=gaps,oil_leads_open=drill,
 displaced_pin_loses_seat=True,render_sha256={name+'.png':sha(OUT/(name+'.png')) for name in ['oblique','axial']},visual_review_status='pending'))
shutil.copy2(__file__,OUT/'executed_reopen.py');App.closeDocument(doc.Name)
print('PASS fresh73 leaves,72 independently reconstructed placements,18 seats/gaps/oil leads and displaced-pin rejection')
