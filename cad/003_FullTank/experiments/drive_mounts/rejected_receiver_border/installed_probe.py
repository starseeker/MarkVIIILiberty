"""Separate trial of source-correct drive receivers at both fixed drive axes."""
from pathlib import Path
import sys,subprocess,types,math
ROOT=Path(__file__).resolve().parent;STAGE=ROOT.parents[1]
sys.path.insert(0,str(STAGE))
from lib.runtime import environment
OUT=ROOT/'installed_build'
if '--worker' not in sys.argv:
    sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=environment(OUT)).returncode)
import FreeCAD as App
import Part
import numpy as np
from lib.evidence import read,write,sha,fingerprint
from lib.model import load
from lib.cad_build import leaves,frame
from lib.hull_geometry import arguments
from lib.roller_validation import bearing_face
from lib.visual_review import shaded

lock=read(ROOT/'authored_input_fingerprint.json');assert fingerprint()==lock
fixture_path=ROOT/'build/DriveMountStudy.FCStd'
assert sha(fixture_path)==read(ROOT/'build/report.json')['native_sha256']
main=App.openDocument(str(STAGE/'build/native/MarkVIII.FCStd'));data=load()
existing=leaves(main.Root);original={i['id']:i for i in existing}
fixture=App.openDocument(str(fixture_path))
doc=App.newDocument('InstalledDriveMountStudy');root=doc.addObject('App::Part','Study')
added=[];changed=[];seats=[];bore_checks=[]
def record(ident,shape,system,source_ids=()):
    assert shape.isValid() and len(shape.Solids)==1,ident
    obj=doc.addObject('PartDesign::Feature',ident);obj.Shape=shape;root.addObject(obj)
    obj.addProperty('App::PropertyStringList','SurveyIdentities');obj.SurveyIdentities=list(source_ids)
    obj.addProperty('App::PropertyString','Qualification');obj.Qualification='Installed reconstruction hypothesis; historical profile and fit unqualified'
    return dict(id=ident,definition=ident,shape=shape,target=obj,representation='assembly',system=system)
# Preserve the exact experimental hull builder separately from main authored code.
source=(STAGE/'lib/hull_parts.py').read_text()
old='(X(1630),Z(500)),(X(1800),Z(430))]'
assert source.count(old)==1
source=source.replace(old,'(X(1630),Z(500)),(X(1750),Z(500)),(X(1800),Z(430))]')
(OUT/'executed_hull_parts.py').write_text(source)
module=types.ModuleType('lib.drive_receiver_trial_hull');module.__package__='lib'
exec(compile(source,str(OUT/'executed_hull_parts.py'),'exec'),module.__dict__)
a=read(ROOT/'hypotheses.json')['values_mm']
bolts=[(a['bearing_bolt_radius']*math.sin(math.radians(30+n*60)),a['bearing_bolt_radius']*math.cos(math.radians(30+n*60))) for n in range(6)]
rivets=[(a['backing_rivet_radius']*math.sin(math.radians(45+n*90)),a['backing_rivet_radius']*math.cos(math.radians(45+n*90))) for n in range(4)]
for hand,sign in [('port',1),('starboard',-1)]:
    center=frame(hand+'_drive',data).Base
    pose=App.Placement(center,App.Rotation(App.Vector(0,0,1),0 if sign==1 else 180))
    named={}
    for link in fixture.Fixture.Group:
        if link.Name.startswith(('Wheel_','ShaftAssembly_','Receiver')):continue
        shape=link.LinkedObject.Shape.copy();shape.Placement=pose.multiply(link.Placement).multiply(shape.Placement)
        item=record(hand+'_'+link.Name,shape,'RunningGear',link.LinkedObject.SurveyIdentities)
        added.append(item);named[link.Name]=item
    for role in ['rear_wing','rear_end','inner_fuel_side','inner_rear_end','inner_skirt_rear','outer_skirt_rear']:
        ident='hull_'+hand+'_'+role;arg=arguments(data['definitions'][ident],data)
        # Correct inferred geometry roles while preserving each part's source identity.
        arg['role']={'inner_fuel_side':'inner_rear_end','inner_rear_end':'inner_fuel_side'}.get(role,role)
        body=module.build(doc,'Trial_'+ident,arg);shape=body.Shape.copy()
        doc.removeObject(body.Name)
        if role in ['rear_end','inner_fuel_side']:
            # Owned through-bores use the installed shaft/fastener datums.
            tools=[]
            for points,diameter in [(bolts,a['bearing_screw_diameter']+a['fastener_hole_clearance'])]+(
                    [(rivets,a['backing_rivet_diameter']+a['fastener_hole_clearance'])] if role=='rear_end' else []):
                for x,z in points:
                    point=pose.multVec(App.Vector(x,0,z))
                    tools.append(Part.makeCylinder(diameter/2,6000,App.Vector(point.x,-3000,point.z),App.Vector(0,1,0)))
            shape=shape.cut(Part.makeCompound(tools)).removeSplitter()
        item=record(ident,shape,'HullStructure',data['definitions'][ident]['survey_ids'])
        changed.append(item);named[role]=item
    for left,right in [('BearingInner','inner_fuel_side'),('BearingOuter','rear_end'),('BackingPlate','rear_end')]:
        gap,area=bearing_face(named[left]['shape'],named[right]['shape'])
        seats.append(dict(a=named[left]['id'],b=named[right]['id'],gap_mm=gap,area_mm2=area,passed=gap<1e-5 and area>1e-4))
    for n in range(6):
        gap,area=bearing_face(named['InnerRivet'+str(n)]['shape'],named['inner_fuel_side']['shape'])
        seats.append(dict(a=named['InnerRivet'+str(n)]['id'],b=named['inner_fuel_side']['id'],gap_mm=gap,area_mm2=area,passed=gap<1e-5 and area>1e-4))
    for n in range(4):
        gap,area=bearing_face(named['BackingRivet'+str(n)]['shape'],named['rear_end']['shape'])
        seats.append(dict(a=named['BackingRivet'+str(n)]['id'],b=named['rear_end']['id'],gap_mm=gap,area_mm2=area,passed=gap<1e-5 and area>1e-4))
    # Each hole must have the full receiving thickness, not merely empty space.
    shell=data['values']['hull_frame_clear'].value/2;wall=data['values']['hull_side_thickness'].value
    for role,points,d in [('inner_fuel_side',bolts,a['bearing_screw_diameter']+a['fastener_hole_clearance']),
                          ('rear_end',bolts,a['bearing_screw_diameter']+a['fastener_hole_clearance']),
                          ('rear_end',rivets,a['backing_rivet_diameter']+a['fastener_hole_clearance'])]:
        y=-(shell+wall/2) if role=='inner_fuel_side' else shell+wall/2
        for n,(x,z) in enumerate(points):
            shape=named[role]['shape'];samples=[]
            for angle in range(0,360,45):
                q=pose.multVec(App.Vector(x+(d/2+.2)*math.cos(math.radians(angle)),y,z+(d/2+.2)*math.sin(math.radians(angle))))
                samples.append(shape.isInside(q,1e-7,True))
            bore_checks.append(dict(part=named[role]['id'],diameter_mm=d,index=n,receiving_ring_samples=samples,passed=all(samples)))
    print('Built',hand,'trial mounts and receivers',flush=True)
changed_ids={i['id'] for i in changed}
context=[i for i in existing if i['representation']=='assembly' and i['id'] not in changed_ids]
physical=context+added+changed
def box(s):
    b=s.optimalBoundingBox(False);return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
boxes=np.array([box(i['shape']) for i in physical]);tested=set();overlaps=[]
for n in range(len(context),len(physical)):
    item=physical[n];b=boxes[n]
    near=np.where(np.all(boxes[:,:3]<=b[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=b[:3]-1e-7,axis=1))[0]
    for m in near:
        if m==n:continue
        pair=tuple(sorted([n,int(m)]))
        if pair in tested:continue
        tested.add(pair);volume=item['shape'].common(physical[m]['shape']).Volume
        if volume>1e-5:overlaps.append(dict(a=item['id'],b=physical[m]['id'],volume_mm3=volume))
doc.recompute();native=OUT/'InstalledDriveMountStudy.FCStd';doc.saveAs(str(native))
report=dict(passed=not overlaps and all(s['passed'] for s in seats+bore_checks),
    integrated=False,new_occurrences=len(added),reconstructed_receivers=len(changed),
    candidate_pairs=len(tested),overlaps=overlaps,hull_seats=seats,receiving_bores=bore_checks,
    native_sha256=sha(native),authored_fingerprint=lock,script_sha256=sha(Path(__file__)),
    hull_builder_sha256=sha(OUT/'executed_hull_parts.py'),
    hypothesis='Swap initial inner M1977/M1978 fore/aft geometric slots to agree with bearing/cross-member source allocations; add inferred lower-border control [1750,500] without changing source calibration or shaft axes.',
    limitation='Partial installation hypothesis; exact seams/profiles, M1552 additional rivets, threads, retention strength and historical fit unresolved.')
write(OUT/'report.json',report)
print('Installed receiver trial',len(tested),'pairs',len(overlaps),'overlaps',flush=True)
# Diagnostic rear slice; the native file retains all reconstructed receiver plates.
crop=Part.makeBox(1700,1800,1500,App.Vector(-600,frame('port_drive',data).Base.y-900,300))
review=[]
for item in added+changed:
    if not item['id'].startswith(('port_','hull_port_')):continue
    shape=item['shape'].common(crop) if item in changed else item['shape']
    if shape.isNull():continue
    obj=doc.addObject('PartDesign::Feature','View_'+item['id']);obj.Shape=shape
    review.append({**item,'shape':shape,'target':obj})
shaded(review,OUT/'receivers.svg',(1,1,.7),'Drive mounts in reconstructed receivers | source assignments corrected; seam hypothesis')
assert fingerprint()==lock
for name in list(App.listDocuments()):App.closeDocument(name)
