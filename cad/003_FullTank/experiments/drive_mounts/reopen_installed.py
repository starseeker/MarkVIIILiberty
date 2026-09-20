"""Fresh-native checks for the separate installed mounting hypothesis."""
from pathlib import Path
import sys,subprocess,math
ROOT=Path(__file__).resolve().parent;STAGE=ROOT.parents[1]
sys.path.insert(0,str(STAGE))
from lib.runtime import environment
OUT=ROOT/'installed_build'
if '--worker' not in sys.argv:
    sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=environment(OUT)).returncode)
import FreeCAD as App
import Part
from lib.evidence import read,write,sha,fingerprint
from lib.model import load
from lib.cad_build import frame,leaves
from lib.roller_validation import bearing_face
from lib.lower_support_validation import validate as validate_lower_supports
report=read(OUT/'report.json');assert report['passed']
native=OUT/'InstalledDriveMountStudy.FCStd';assert sha(native)==report['native_sha256']
assert fingerprint()==report['authored_fingerprint']
doc=App.openDocument(str(native));data=load();items={o.Name:o.Shape for o in doc.Study.Group}
assert len(items)==68
assert all(s.isValid() and len(s.Solids)==1 for s in items.values())
seats=[]
for row in report['hull_seats']:
    gap,area=bearing_face(items[row['a']],items[row['b']]);assert gap<1e-5 and area>1e-4,row
    seats.append(dict(a=row['a'],b=row['b'],gap_mm=gap,area_mm2=area))
a=read(ROOT/'hypotheses.json')['values_mm']
bolts=[(a['bearing_bolt_radius']*math.sin(math.radians(30+n*60)),a['bearing_bolt_radius']*math.cos(math.radians(30+n*60))) for n in range(6)]
rivets=[(a['backing_rivet_radius']*math.sin(math.radians(45+n*90)),a['backing_rivet_radius']*math.cos(math.radians(45+n*90))) for n in range(4)]
bores=[]
for hand,sign in [('port',1),('starboard',-1)]:
    center=frame(hand+'_drive',data).Base
    pose=App.Placement(center,App.Rotation(App.Vector(0,0,1),0 if sign==1 else 180))
    for role,points,diameter in [('inner_fuel_side',bolts,a['bearing_screw_diameter']+a['fastener_hole_clearance']),
                               ('rear_end',bolts,a['bearing_screw_diameter']+a['fastener_hole_clearance']),
                               ('rear_end',rivets,a['backing_rivet_diameter']+a['fastener_hole_clearance'])]:
        ident='hull_'+hand+'_'+role;shape=items[ident]
        for n,(x,z) in enumerate(points):
            centerline=pose.multVec(App.Vector(x,0,z));r=diameter/2;faces=[]
            for f in shape.Faces:
                if not isinstance(f.Surface,Part.Cylinder):continue
                s=f.Surface
                if abs(s.Radius-r)>1e-6 or abs(abs(s.Axis.y)-1)>1e-6:continue
                if math.hypot(s.Center.x-centerline.x,s.Center.z-centerline.z)>1e-5:continue
                faces.append(f)
            length=sum(f.Area for f in faces)/(2*math.pi*r)
            assert abs(length-data['values']['hull_side_thickness'].value)<1e-5,(ident,n,length)
            bores.append(dict(part=ident,index=n,diameter_mm=diameter,full_cylinder_length_mm=length))
    assert list(doc.getObject('hull_'+hand+'_inner_fuel_side').SurveyIdentities)==data['definitions']['hull_'+hand+'_inner_fuel_side']['survey_ids']
    # Moving the inner rivet into open space must lose its receiving seat.
    negative=items[hand+'_InnerRivet0'].copy();negative.translate(App.Vector(0,-sign*.2,0))
    gap,area=bearing_face(negative,items['hull_'+hand+'_inner_fuel_side'])
    assert area<1e-4
main=App.openDocument(str(STAGE/'build/native/MarkVIII.FCStd'));context=leaves(main.Root)
for n,item in enumerate(context):
    if item['id'] in items:
        context[n]={**item,'shape':items[item['id']],'target':doc.getObject(item['id'])}
lower=validate_lower_supports(data,context,OUT/'retained_interfaces')
assert lower['implemented_checks_passed']
write(OUT/'reopened.json',dict(passed=True,native_sha256=sha(native),single_solid_occurrences=len(items),
    hull_seats=seats,receiving_cylinders=bores,negative_rivet_displacement_mm=.2,
    source_identities_retained=True,lower_supports_retained=True,
    lower_bearing_faces=len(lower['bearing_faces']),lower_hull_seats=len(lower['hull_seats']),
    lower_receiving_bores=len(lower['receiving_hull_bores']),
    limitation='Only the separate installed hypothesis is checked. Main authored hull and drive mount geometry remain unchanged.'))
assert fingerprint()==report['authored_fingerprint']
for name in list(App.listDocuments()):App.closeDocument(name)
print('Reopened installed drive mounts:',len(seats),'seats,',len(bores),'full receiving cylinders; lower supports retained',flush=True)
