"""Fresh native composition and owned-interface checks for the mounting fixture."""
from pathlib import Path
from collections import Counter
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parent;STAGE=ROOT.parents[1];OUT=ROOT/'mounted_build'
sys.path.insert(0,str(STAGE))
from lib.runtime import environment
if '--worker' not in sys.argv:
    sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=environment(OUT)).returncode)
import FreeCAD as App
from lib.evidence import read,write,sha,database
from lib.model import load
from lib.drive_mount_geometry import values,bearing_points,backing_points
from lib.track_parts import cylinder_y
from lib.roller_validation import bearing_face

report=read(OUT/'report.json');path=OUT/'MountedPinionStudy.FCStd'
assert report['passed'] and sha(path)==report['native_sha256']
doc=App.openDocument(str(path));doc.recompute()
links=[o for o in doc.Objects if o.TypeId=='App::Link'];assert len(links)==98
defs=[o for o in doc.Objects if o.TypeId=='PartDesign::Body' and 'SurveyId' in o.PropertiesList]
assert len(defs)==16,len(defs)
for obj in defs:
    assert obj.Shape.isValid() and len(obj.Shape.Solids)==1,obj.Name
    with database() as connection:
        assert connection.execute('SELECT 1 FROM part_evidence WHERE part_id=? AND record_id=?',
                                  (obj.SurveyId,obj.SourceRecord)).fetchone(),obj.Name
counts=Counter(o.LinkedObject.SurveyId for o in links)
assert dict(counts)==report['source_identity_counts']
assert len(doc.ShaftAssembly.Group)==4
assert len([o for o in doc.Objects if o.TypeId=='App::Part' and o.Name.startswith('PinAssembly')])==18
items={}
for link in links:
    shape=link.LinkedObject.Shape.copy();shape.Placement=link.Placement.multiply(shape.Placement)
    assert shape.isValid() and len(shape.Solids)==1
    items[link.Name]=shape
a=values(load());p=read(OUT/'hypotheses.json')['values_mm']
holes=[]
for side,key in [(-1,'hull_port_inner_rear_end'),(1,'hull_port_rear_wing')]:
    plate=doc.getObject('Receiver_'+key).Shape
    specs=[('bearing',bearing_points(a),a['bearing_screw_diameter']+a['fastener_hole_clearance'])]
    if side==1:specs.append(('backing',backing_points(a),a['backing_rivet_diameter']+a['fastener_hole_clearance']))
    for role,points,diameter in specs:
        for n,(x,z) in enumerate(points):
            witness=cylinder_y(diameter/2,a['hull_side_thickness'],x=x,y=side*(a['shell']+a['hull_side_thickness']/2),z=z)
            volume=witness.common(plate).Volume
            assert volume<1e-5,(key,role,n,volume)
            holes.append(dict(receiver=key,role=role,index=n,material_in_bore_mm3=volume,depth_mm=a['hull_side_thickness']))
    witness=cylinder_y(a['barrel_radius'],a['hull_side_thickness'],y=side*(a['shell']+a['hull_side_thickness']/2))
    assert witness.common(plate).Volume<1e-5
seats=[]
for first,second in [('OuterBearing','hull_port_rear_wing'),('BackingPlate','hull_port_rear_wing'),('InnerBearing','hull_port_inner_rear_end')]:
    gap,area=bearing_face(items[first],doc.getObject('Receiver_'+second).Shape)
    assert gap<1e-5 and area>1;seats.append(dict(a=first,b=second,gap_mm=gap,area_mm2=area))
for second in ['OuterBearing','InnerBearing']:
    gap,area=bearing_face(items['FixedShaft'],items[second]);assert gap<1e-5 and area>1
    seats.append(dict(a='FixedShaft',b=second,gap_mm=gap,area_mm2=area))
# A shaft translated along its axis loses one of the two locating shoulders.
shift=items['FixedShaft'].copy();shift.translate(App.Vector(0,.2,0))
gap,area=bearing_face(shift,items['InnerBearing']);assert area<1
assert abs(items['ShaftInnerPlug'].BoundBox.YMin+p['shaft_end'])<1e-5
assert abs(items['ShaftOuterPlug'].BoundBox.YMax-p['shaft_end']-p['plug_head_stock'])<1e-5
assert not doc.Def_Shaft.Shape.isInside(App.Vector(0,0,0),1e-7,True)
assert doc.Def_Shaft.Shape.isInside(App.Vector(20,0,0),1e-7,True)
write(OUT/'reopened.json',dict(passed=True,native_sha256=sha(path),script_sha256=sha(__file__),
    physical_occurrences=98,source_definitions=16,hull_context_bodies=4,
    canonical_identity_counts=dict(counts),owned_full_depth_fastener_bores=holes,bearing_seats=seats,
    moved_shaft_loses_inner_seat=True,flush_and_headed_plug_envelopes_checked=True,
    oil_gallery_witnesses_checked=True,thread_and_seal_qualification=False))
shutil.copy2(__file__,OUT/'executed_reopen.py');App.closeDocument(doc.Name)
print('PASS fresh 98 links,16 source definitions,16 full-depth bores,5 seats and shaft displacement rejection')
