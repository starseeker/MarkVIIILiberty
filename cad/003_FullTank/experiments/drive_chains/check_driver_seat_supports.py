"""Saved-material verification of the full seat-to-stay-to-plate-to-floor chain."""
import argparse
from pathlib import Path
from control_rebuild_io_v2 import *
from lib.camera_review import validate_native_bindings

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, required=True)
a = p.parse_args()
s = Saved(a.candidate)
parent = Saved((ROOT/s.report['parent_native']).parent)
report, details = s.report, s.report['details']
out = s.folder/'checks03'
out.mkdir(exist_ok=False)
validate_native_bindings(dict(native_file=str(s.native),render_occurrences=list(s.rows),landmarks=[]),s.manifest)
assert all(sha(ROOT/f)==h for f,h in report['input_hashes'].items())
V = App.Vector
X, Y, Z = V(1,0,0), V(0,1,0), V(0,0,1)
checks = []


def check(name, value, **extra):
    checks.append(dict(name=name,passed=bool(value),**extra))
    if not value:
        print('FAIL',name,extra,flush=True)


def volume(shape):
    return sum(abs(q.Volume) for q in shape.Solids)


def planes(q,p,n):
    return [f for f in q.Faces if isinstance(f.Surface,Part.Plane) and
        f.normalAt(0,0).cross(n).Length<1e-7 and abs((f.CenterOfMass-p).dot(n))<1e-6]


def contact(one,two,p,n):
    return sum(f.common(g).Area for f in planes(one,p,n) for g in planes(two,p,n))


def mating(one,two):
    area = 0.
    for f in one.Faces:
        if not isinstance(f.Surface,Part.Plane):
            continue
        p,n=f.CenterOfMass,f.normalAt(0,0)
        for g in planes(two,p,n):
            area += f.common(g).Area
    return area


def bores(q,p,n,r):
    return [f for f in q.Faces if isinstance(f.Surface,Part.Cylinder) and
        abs(f.Surface.Radius-r)<1e-7 and f.Surface.Axis.cross(n).Length<1e-7 and
        (f.Surface.Center-p).cross(n).Length<1e-6]


changed = set(report['changed_definitions'])
relocated = set(details['relocated_existing_hardware'])
check('54 additions and281 complete local occurrences',len(report['new_occurrences'])==54 and len(s.rows)==281)
check('Only bearing and two support plates revised',changed=={'Def_DriverSeat_Bearing_SH289E','Def_DriverPortSupportPlate_MountStudy','Def_DriverStarboardSupportPlate_MountStudy'})
check('24 plate fastener pieces intentionally relocated',len(relocated)==24)
for key in s.manifest['definitions']:
    q=s.definition(key)
    check(key+' valid closed canonical solid',q.Placement.isIdentity() and q.isValid() and len(q.Solids)==1 and q.Solids[0].isClosed() and q.getTolerance(1)<=1e-4)
    if key in parent.manifest['definitions'] and key not in changed:
        old=parent.definition(key)
        check(key+' all inherited material retained',volume(old.cut(q))<1e-5 and volume(q.cut(old))<1e-5)
for name,row in parent.rows.items():
    current=s.rows[name]
    check(name+' inherited definition and protected frame',current['definition']==row['definition'] and
        (name in relocated or max(abs(x-y) for x,y in zip(current['frame'],row['frame']))<1e-7))

old=parent.definition('Def_DriverSeat_Bearing_SH289E')
new=s.definition('Def_DriverSeat_Bearing_SH289E')
tool=Part.makeCylinder(9.65,32,V(0,-16,-35.5696394686906),Y)
expected=old.cut(tool)
check('Bearing change limited to source-sized receiving bore',volume(expected.cut(new))<1e-5 and volume(new.cut(expected))<1e-5 and bool(bores(new,V(0,0,-35.5696394686906),Y,9.65)))
check('Regression: old estimated bore rejects printed19.05mm bolt',volume(old.common(Part.makeCylinder(9.525,30,V(0,-15,-35.5696394686906),Y)))>100)
frame=s.world('DriverSeatFrame')
for name in [v['name'] for v in parent.report['details']['bearing_records']]:
    pose0=pose(s.rows[name]['frame'])
    area=contact(s.world(name),frame,pose0.Base,Z)
    check(name+' original flange contact retained',area>1500,contact_mm2=area)

for key,diameter,length in [('Def_DriverSupportBolt_MountStudy',12.7,31.75),
    ('Def_SeatSupport_LowerStayBolt',12.7,34.925),('Def_SeatSupport_AngleFloorBolt',12.7,41.275),
    ('Def_SeatSupport_UpperStayBolt',19.05,60.325)]:
    q=s.definition(key)
    shank=Part.makeCylinder(diameter/2,length)
    check(key+' full printed stock and actual cylinder',volume(shank.cut(q))<1e-5 and abs(q.BoundBox.ZMax-length)<1e-7 and bool(bores(q,V(),Z,diameter/2)))

joint_checks=[]
for row in details['joints']:
    stem=row['stem'];p0=V(*row['point_world_mm']);n=V(*row['axis_world'])
    grip,lock_stock=row['grip_mm'],row['lock_stock_mm']
    bolt,lock,nut=[s.world(stem+v) for v in ['Bolt','Lock','Nut']]
    first,last=[s.world(v) for v in row['hosts']]
    hole_radius=row['bolt_diameter_mm']/2+.15 if row['bolt_diameter_mm']==12.7 else 9.65
    receiving=all(bool(bores(q,p0,n,hole_radius)) for q in [first,last])
    free=all(volume(Part.makeCylinder(row['bolt_diameter_mm']/2,grip,p0,n).common(q))<1e-5 for q in [first,last])
    check(stem+' complete coaxial receiving bores',receiving and free)
    head=contact(bolt,first,p0,n)
    washer=contact(lock,last,p0+n*grip,n)
    nut_area=contact(lock,nut,p0+n*(grip+lock_stock),n)
    interface=mating(first,last)
    check(stem+' head on actual first receiver',head>70,contact_mm2=head)
    check(stem+' lock on actual final receiver',washer>70,contact_mm2=washer)
    check(stem+' nut on actual lock',nut_area>70,contact_mm2=nut_area)
    check(stem+' physically connected receiver stack',interface>70,contact_mm2=interface)
    check(stem+' full nut engagement and protruding stock',row['bolt_protrusion_mm']>.5,
        protrusion_mm=row['bolt_protrusion_mm'])
    check(stem+' no hardware or receiving-material overlap',all(volume(a.common(b))<1e-5
        for a,b in [(bolt,lock),(bolt,nut),(bolt,first),(bolt,last),(lock,nut),(lock,last),(nut,last),(first,last)]))
    joint_checks.append(dict(stem=stem,head_contact_mm2=head,lock_contact_mm2=washer,
        nut_contact_mm2=nut_area,receiver_contact_mm2=interface))

for side in ['Port','Starboard']:
    rec=details['supports'][side];plate=s.world(rec['plate']);angle=s.world(rec['angle'])
    check(side+' separate plate/angle contact',mating(plate,angle)>10000 and volume(plate.common(angle))<1e-5)
    for name,radius in [('DriverMainShaft',14.15),('DriverSwingShaft',12.15)]:
        center=pose(s.rows[name]['frame']).Base
        check(side+' retained '+name+' bore',bool(bores(plate,center,Y,radius)))
    for floor in sorted({v['floor'] for v in rec['original_floor_mounts']}):
        q=s.world(floor)
        check(side+' angle actually seated on '+floor,mating(angle,q)>1000 and volume(angle.common(q))<1e-5)
for row in details['stays']:
    q=s.world(row['name']);low,high=V(*row['lower_center_world_mm']),V(*row['upper_center_world_mm'])
    check(row['name']+' both source-sized joint bores',bool(bores(q,low,Y,6.5)) and bool(bores(q,high,Y,9.65)))

# Negative seating controls use a complete saved bolt, without changing its stock.
for row in [details['joints'][0],details['joints'][-1]]:
    moved=s.world(row['stem']+'Bolt');n=V(*row['axis_world']);p0=V(*row['point_world_mm'])
    moved.translate(-n*.5)
    check('Regression: reject lifted '+row['stem'],contact(moved,s.world(row['hosts'][0]),p0,n)<1e-7)
check('Source and historical limits remain explicit',not report['geometry_integrated'] and
    not report['historical_geometry_qualified'] and not details['installation_qualified'] and
    not details['source_camera_refitted'])
value=dict(passed=all(v['passed'] for v in checks),checks=checks,joints=joint_checks,
    native_sha256=sha(s.native),parent_native_sha256=sha(parent.native),checker_sha256=sha(Path(__file__)),
    geometry_integrated=False,historical_installation_qualified=False,
    scope='Source-sized upper/lower hardware, four stays, revised actual receiver bores, distinct side plates/angles, floor contacts and protected geometry/frames. Full context audit separate; historical topology and source placement remain conditional.')
write(out/'independent_checks.json',value)
print('Seat support checks',len(checks),'passed',value['passed'],flush=True)
assert value['passed']
