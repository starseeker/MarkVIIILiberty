"""Inferred crest rounding, with a native subset check against the clear study."""
from pathlib import Path
import sys,subprocess,math
ROOT=Path(__file__).resolve().parent;STAGE=ROOT.parents[1]
sys.path.insert(0,str(STAGE))
from lib.runtime import environment
OUT=ROOT/'rounded_teeth_build'
if '--worker' not in sys.argv:
    sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=environment(OUT)).returncode)

import FreeCAD as App
import Part
from lib.evidence import read,write,sha,fingerprint
from lib.visual_review import shaded
from lib.roller_validation import bearing_face

lock=fingerprint();assert lock==read(ROOT/'authored_input_fingerprint.json')
path=ROOT/'common_fit_refined_build/CommonWheelInterfaceStudy.FCStd'
assert sha(path)==read(path.parent/'report.json')['native_sha256']
doc=App.openDocument(str(path));target=doc.getObject('DriveRimHypothesis')
original=target.Shape.copy();outer=39.237*25.4/2
edges=[]
for edge in original.Edges:
    b=edge.BoundBox
    if abs(b.YLength-50.8)<1e-6 and b.XLength<1e-6 and b.ZLength<1e-6:
        p=edge.Vertexes[0].Point
        if abs(math.hypot(p.x,p.z)-outer)<1e-5:edges.append(edge)
assert len(edges)==70,len(edges)
rounded=original.makeFillet(3.0,edges)
assert rounded.isValid() and len(rounded.Solids)==1
added=rounded.cut(original).Volume
assert added<1e-5,'Rounding added material; previous clearance proof cannot be inherited'
assert any(isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-outer)<1e-6 for f in rounded.Faces)
target.Shape=rounded;doc.recompute()
target.addProperty('App::PropertyLength','InferredCrestRadius');target.InferredCrestRadius=3
group=doc.getObject('DriveFixture');items=[]
for link in group.Group:
    shape=link.LinkedObject.Shape.copy()
    shape.Placement=group.Placement.multiply(link.Placement).multiply(shape.Placement)
    items.append(dict(id=link.Name,definition=link.LinkedObject.Name,shape=shape,target=link.LinkedObject,
                      system='RunningGear',representation='assembly'))
by_id={i['id']:i for i in items};seats=[]
for suffix in ['A','B']:
    gap,area=bearing_face(by_id['drive_Rim'+suffix]['shape'],by_id['drive_Disk'+suffix]['shape'])
    assert gap<1e-6 and area>1
    seats.append(dict(side=suffix,gap_mm=gap,area_mm2=area))
shaded(items,OUT/'drive.svg',(1,1,.6),'Drive-wheel hypothesis | inferred 3 mm crest rounding | unintegrated')
native=OUT/'RoundedWheelInterfaceStudy.FCStd';doc.saveAs(str(native))
assert fingerprint()==lock
write(OUT/'report.json',dict(complete=True,integrated=False,source_fixture_sha256=sha(path),
    native_sha256=sha(native),executed_script_sha256=sha(Path(__file__)),authored_fingerprint=lock,
    teeth=35,inferred_radius_mm=3,rounded_edges=len(edges),added_material_mm3=added,
    removed_material_mm3=original.Volume-rounded.Volume,outer_cylindrical_radius_preserved_mm=outer,
    rim_disk_bearing_faces=seats,source_profile_qualified=False,
    limitation='Crest radius and underlying tooth relief remain inferred; the 35/37 source conflict is unresolved.'))
App.closeDocument(doc.Name)
print('ROUNDED TOOTH STUDY COMPLETE',flush=True,file=sys.stderr)
