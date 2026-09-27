"""Check saved coupled-layout material, rod closure, floor bores and mount seats."""
import argparse
import math
from pathlib import Path
from control_rebuild_io_v2 import *
from lib.camera_review import validate_native_bindings

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);a=p.parse_args()
s=Saved(a.candidate);r=s.report;d=r['details'];parent=Saved((ROOT/r['parent_native']).parent)
out=s.folder/'checks03';out.mkdir(exist_ok=False)
validate_native_bindings(dict(native_file=str(s.native),render_occurrences=list(s.rows),landmarks=[]),s.manifest)
assert all(sha(ROOT/f)==v for f,v in r['input_hashes'].items())
checks=[];V=App.Vector;Y=V(0,1,0);Z=V(0,0,1)


def ck(name,passed,**details):
    checks.append(dict(name=name,passed=bool(passed),**details))
    if not passed:print('FAILED',name,details,flush=True)


def volume(q):return sum(abs(v.Volume) for v in q.Solids)


def same(one,two):
    return volume(one.cut(two))<1e-5 and volume(two.cut(one))<1e-5 and not one.cut(two,1e-4).Faces and not two.cut(one,1e-4).Faces


def planes(q,p,n):
    return [f for f in q.Faces if isinstance(f.Surface,Part.Plane) and f.normalAt(0,0).cross(n).Length<1e-7 and abs((f.CenterOfMass-p).dot(n))<1e-6]


def bearing(q,t,p,n):return sum(f.common(g).Area for f in planes(q,p,n) for g in planes(t,p,n))


def cylinders(q,p,n,radius):
    return [f for f in q.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-radius)<1e-7 and f.Surface.Axis.cross(n).Length<1e-7 and (f.Surface.Center-p).cross(n).Length<1e-6]


ck('Complete prototype population',len(s.rows)==189 and len(s.manifest['definitions'])==81)
ck('Exactly five inherited definitions revised',set(r['changed_definitions'])=={'Def_DriverClutchFrontRod_M576','Def_DriverPortSupportPlate_MountStudy','Def_DriverStarboardSupportPlate_MountStudy','Def_DriverContext_hull_floor_1','Def_DriverContext_hull_floor_2'})
for key in s.manifest['definitions']:
    q=s.definition(key)
    ck(key+' closed valid canonical stock',q.Placement.isIdentity() and q.isValid() and len(q.Solids)==1 and q.Solids[0].isClosed() and q.getTolerance(1)<=1e-4)
    if key in parent.manifest['definitions'] and key not in r['changed_definitions']:
        ck(key+' complete inherited material',same(q,parent.definition(key)))
for name,row in s.rows.items():
    ck(name+' actual saved frame',max(abs(x-y) for x,y in zip(row['frame'],r['specs'][name]['frame']))<1e-7)
old_driver={n for n,row in parent.rows.items() if 'DriverControlFoundation' in row['owners']}
ck('Every inherited driver occurrence represented',old_driver<=set(s.rows),inherited_count=len(old_driver))
delta=V(*d['driver_translation_mm'])
rod_names=set(d['rod_records']);joint_names=set()
oldrecords={name:(parent.report['details']['low_speed']['Port' if name.startswith('Port') else 'Starboard'] if 'LowRod' in name else parent.report['details']['rods']['Front'] if name.startswith('DriverClutch') else parent.report['details']['high_controls']['Port' if name.startswith('Port') else 'Starboard']['rods']['Front']) for name in rod_names}
for rec in oldrecords.values():
    for end in rec['endpoints']:joint_names.update(end['stem']+role for role in ['Fork','Pin','Cotter','Nut'])
for name in old_driver:
    if name in rod_names|joint_names or name in d['omitted_support_and_floor_occurrences']:continue
    old=pose(parent.rows[name]['frame']);old.Base+=delta
    ck(name+' rigid relative layout retained',max(abs(x-y) for x,y in zip(old.toMatrix().A,s.rows[name]['frame']))<1e-7)

for name,rec in d['rod_records'].items():
    q=s.definition(s.rows[name]['definition']);length=q.BoundBox.XLength
    ck(name+' complete stock',abs(length-rec['stock_length_mm'])<1e-6 and (rec['mark']!='M574' or abs(length-1257.3)<1e-6),stock_length_mm=length)
    ends=oldrecords[name]['endpoints'];p0=V(*rec['fixed_pin_world_mm']);p1=V(*rec['driver_pin_world_mm'])
    ck(name+' stock and two complete fork offsets close',abs((p1-p0).Length-length-50.8)<1e-6)
    for end,point in zip(ends,[p0,p1]):
        receiver=s.world(end['receiver']);pin=s.world(end['stem']+'Pin')
        ck(end['stem']+' real receiving bore coaxial',bool(cylinders(receiver,point,Y,6.5)))
        ck(end['stem']+' full joint pin coaxial',bool(cylinders(pin,point,Y,6.35)))
ck('Three M576 applications share the same complete definition',len({s.rows[n]['definition'] for n,v in d['rod_records'].items() if v['mark']=='M576'})==1)
for name,expected in [('DriverClutchShortRod',320.675),('PortDriverHighShortRod',269.875),('StarboardDriverHighShortRod',269.875)]:
    ck(name+' full printed short stock',abs(s.definition(s.rows[name]['definition']).BoundBox.XLength-expected)<1e-6)

bow=ROOT/d['bow_source'];br=read(bow/'report.json');bn=bow/br['native_file'];assert sha(bn)==d['bow_native_sha256']
doc=App.openDocument(str(bn));original={}
for name in d['bow_occurrences']:
    link=doc.getObject(name);q=link.LinkedObject.Shape.copy();q.Placement=link.LinkPlacement;original[name]=q
App.closeDocument(doc.Name)
for name,q in original.items():
    if name not in ['hull_floor_1','hull_floor_2']:ck(name+' source bow material and frame retained',same(s.world(name),q));continue
    expected=q.copy()
    for m in d['mounts']:
        if m['floor']!=name:continue
        p0=V(*m['contact_world_mm']);n=V(*m['normal_world'])
        expected=expected.cut(Part.makeCylinder(6.5,30,p0+n*10,-n))
    ck(name+' only eight declared new mount holes',same(s.world(name),expected))
    ck(name+' no floor material added',volume(s.world(name).cut(q))<1e-5)

mount_results=[]
for m in d['mounts']:
    p0=V(*m['contact_world_mm']);n=V(*m['normal_world']);stem=m['stem']
    plate=s.world(m['plate']);floor=s.world(m['floor']);bolt=s.world(stem+'Bolt');lock=s.world(stem+'Lock');nut=s.world(stem+'Nut')
    for part,q in [('plate',plate),('floor',floor)]:ck(stem+' through '+part+' bore',bool(cylinders(q,p0,n,6.5)))
    areas=dict(plate_floor=bearing(plate,floor,p0,n),head_plate=bearing(bolt,plate,p0+n*6.35,n),
               floor_lock=bearing(floor,lock,p0-n*6,n),lock_nut=bearing(lock,nut,p0-n*9.175,n))
    for label,area in areas.items():ck(stem+' '+label+' actual seating',area>10,contact_area_mm2=area)
    ck(stem+' full bolt through bores',bool(cylinders(bolt,p0,n,6.35)))
    mount_results.append(dict(stem=stem,contact_areas_mm2=areas))
for side in ['Port','Starboard']:
    plate=s.world('Driver'+side+'SupportPlate')
    for kind,radius in [('Main',14.15),('Swing',12.15)]:
        point=V(*d['main_world_mm' if kind=='Main' else 'swing_world_mm'])
        ck(side+' '+kind+' actual journal clearance',bool(cylinders(plate,point,Y,radius)))

distances={}
for side in ['Port','Starboard']:
    name=side+'DriverOperatingHandle';handle=s.world(name);distance=handle.distToShape(s.world('hull_front_slope'))[0]
    ck(side+' complete handle bow clearance',distance>1.,distance_mm=distance)
    distances[side]=distance
result=dict(passed=all(v['passed'] for v in checks),checks=checks,mount_seating=mount_results,
            native_sha256=sha(s.native),checker_sha256=sha(Path(__file__)),parent_native_sha256=sha(parent.native),
            bow_native_sha256=sha(bn),handle_bow_clearance_mm=distances,
            geometry_integrated=False,historical_geometry_qualified=False,
            scope='Saved material/frame preservation, printed rod closure, unchanged internal driver geometry, actual receiver/pin bores and eight complete mounting stacks on the corrected floor. Historical height and control state remain provisional.')
write(out/'independent_checks.json',result);print('Independent checks',len(checks),'passed',result['passed'],flush=True)
assert result['passed']
