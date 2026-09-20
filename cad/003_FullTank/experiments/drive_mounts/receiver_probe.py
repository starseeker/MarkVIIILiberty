"""Read-only diagnostic of the revised fixture against current installed hull."""
from pathlib import Path
import sys, subprocess
ROOT=Path(__file__).resolve().parent;STAGE=ROOT.parents[1]
sys.path.insert(0,str(STAGE))
from lib.runtime import environment
OUT=ROOT/'receiver_build'
if '--worker' not in sys.argv:
    sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=environment(OUT)).returncode)
import FreeCAD as App
import Part
import numpy as np
from lib.evidence import read,write,sha,fingerprint
from lib.model import load,point
from lib.cad_build import leaves,frame
from lib.roller_validation import bearing_face
from lib.visual_review import shaded

lock=read(ROOT/'authored_input_fingerprint.json');assert fingerprint()==lock
fixture_path=ROOT/'build/DriveMountStudy.FCStd'
assert sha(fixture_path)==read(ROOT/'build/report.json')['native_sha256']
main=App.openDocument(str(STAGE/'build/native/MarkVIII.FCStd'))
data=load();items=leaves(main.Root);by_id={i['id']:i for i in items}
placement=frame('port_drive',data)
fixture=App.openDocument(str(fixture_path));mounts=[]
for link in fixture.Fixture.Group:
    if link.Name.startswith(('Wheel_','ShaftAssembly_','Receiver')):continue
    shape=link.LinkedObject.Shape.copy()
    shape.Placement=placement.multiply(link.Placement).multiply(shape.Placement)
    mounts.append(dict(id='Study_'+link.Name,definition=link.LinkedObject.Name,
                       shape=shape,representation='assembly',system='RunningGear'))
assert len(mounts)==28,len(mounts)
actual={i['id']:i['shape'] for i in mounts}
def box(shape):
    b=shape.optimalBoundingBox(False);return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
physical=[i for i in items if i['representation']=='assembly']
boxes=np.array([box(i['shape']) for i in physical]);collisions=[];tested=0
for item in mounts:
    b=np.array(box(item['shape']))
    near=np.where(np.all(boxes[:,:3]<=b[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=b[:3]-1e-7,axis=1))[0]
    for n in near:
        other=physical[n];tested+=1
        volume=item['shape'].common(other['shape']).Volume
        if volume>1e-5:collisions.append(dict(a=item['id'],b=other['id'],volume_mm3=volume))
seats=[]
for mount,receiver in [('BearingInner','inner_rear_end'),('BearingInner','inner_fuel_side'),
                       ('BearingOuter','rear_end'),('BackingPlate','rear_end')]:
    target='hull_port_'+receiver
    gap,area=bearing_face(actual['Study_'+mount],by_id[target]['shape'])
    seats.append(dict(a=mount,b=target,gap_mm=gap,area_mm2=area,
                      receiver_label=data['definitions'][target]['label']))
selected=[i for i in items if i['id'] in ['hull_port_'+s for s in
          ['rear_wing','rear_end','inner_fuel_side','inner_rear_end','inner_skirt_rear','outer_skirt_rear']]]
# Keep an actual local section for diagnostic viewing without changing sources.
crop=Part.makeBox(1700,1800,1500,App.Vector(-600,placement.Base.y-900,300))
review=[]
doc=App.newDocument('CurrentDriveReceiverDiagnostic');root=doc.addObject('App::Part','Diagnostic')
for item in selected+mounts:
    shape=item['shape'].common(crop) if item in selected else item['shape']
    if shape.isNull():continue
    obj=doc.addObject('PartDesign::Feature',item['id']);obj.Shape=shape;root.addObject(obj)
    obj.addProperty('App::PropertyString','Qualification');obj.Qualification='Diagnostic only; unresolved source mapping and undrilled receivers'
    # Each direct target contains an installed shape; do not share mesh-cache keys.
    review.append({**item,'definition':item['id'],'shape':shape,'target':obj})
doc.recompute();doc.saveAs(str(OUT/'CurrentDriveReceiverDiagnostic.FCStd'))
shaded(review,OUT/'current_receivers.svg',(1,1,.7),'Current rear hull and drive mount diagnostic | undrilled receivers; source mapping unresolved')
write(OUT/'current_report.json',dict(candidate_pairs=tested,overlaps=collisions,bearing_faces=seats,
      drive_axis=list(placement.Base),source_points={str(p):point(data,'snl_2',p) for p in [[1630,500],[1715,453],[1800,430]]},
      installed_hull_bounds={i['id']:box(i['shape']) for i in selected},authored_fingerprint=lock,
      limitation='Diagnostic only. Material overlaps with uncut receiving bores are expected; source-correct receivers still required.'))
assert fingerprint()==lock
for name in list(App.listDocuments()):App.closeDocument(name)
print('CURRENT RECEIVER DIAGNOSTIC',tested,'pairs',len(collisions),'overlaps',flush=True)
