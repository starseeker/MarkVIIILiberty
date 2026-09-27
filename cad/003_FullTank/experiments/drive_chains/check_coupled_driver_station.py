"""Check saved source stock, rigid mechanisms, real joints and relocated mounts."""
import argparse
import math
from pathlib import Path
from control_rebuild_io_v2 import *
from lib.camera_review import validate_native_bindings

V=App.Vector;X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True)
s=Saved(p.parse_args().candidate);r=s.report;d=r['details']
parent=Saved((ROOT/r['parent_native']).parent)
accepted=Saved((ROOT/d['retained_development_native']).parent)
out=s.folder/'checks01';out.mkdir(exist_ok=False);checks=[]
validate_native_bindings(dict(native_file=str(s.native),render_occurrences=list(s.rows),landmarks=[]),s.manifest)
assert all(sha(ROOT/f)==h for f,h in r['input_hashes'].items())


def ck(name,ok,**extra):
    checks.append(dict(name=name,passed=bool(ok),**extra))
    if not ok:print('FAIL',name,extra,flush=True)


def vol(q):return sum(abs(v.Volume) for v in q.Solids)
def same(q,t):return vol(q.cut(t))<1e-5 and vol(t.cut(q))<1e-5
def world(name):return s.world(name) if name in s.rows else accepted.world(name)
def planes(q,p,n):return [f for f in q.Faces if isinstance(f.Surface,Part.Plane) and f.normalAt(0,0).cross(n).Length<1e-7 and abs((f.CenterOfMass-p).dot(n))<1e-6]
def contact(q,t,p,n):return sum(f.common(g).Area for f in planes(q,p,n) for g in planes(t,p,n))
def bores(q,p,n,radius):return [f for f in q.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-radius)<1e-6 and f.Surface.Axis.cross(n).Length<1e-7 and (f.Surface.Center-p).cross(n).Length<1e-6]
def mating(q,t):return sum(contact(q,t,f.CenterOfMass,f.normalAt(0,0)) for f in q.Faces if isinstance(f.Surface,Part.Plane))


ck('Complete394-occurrence coupled prototype',len(s.rows)==394 and len(s.manifest['definitions'])==125)
for key in s.manifest['definitions']:
    q=s.definition(key)
    ck(key+' valid closed canonical stock',q.Placement.isIdentity() and q.isValid() and len(q.Solids)==1 and q.Solids[0].isClosed() and q.getTolerance(1)<=1e-4)
    src=parent if key in parent.manifest['definitions'] else accepted
    if key not in r['changed_definitions']:ck(key+' inherited material retained',same(q,src.definition(key)))
for name,row in s.rows.items():
    ck(name+' saved transform matches declared transform',max(abs(x-y) for x,y in zip(row['frame'],r['specs'][name]['frame']))<1e-7)
for group,item in d['rigid_groups'].items():
    delta=V(*item['delta_mm'])
    for name in item['names']:
        expected=pose(accepted.rows[name]['frame']);expected.Base+=delta
        ck(name+' complete rigid '+group,max(abs(x-y) for x,y in zip(s.rows[name]['frame'],expected.toMatrix().A))<1e-7)
for name in parent.rows:
    if name.startswith('DriverSeat') and not any(v in name for v in ['AngleFloor','SupportAngle']):
        ck(name+' seat/stay frame retained',max(abs(x-y) for x,y in zip(s.rows[name]['frame'],parent.rows[name]['frame']))<1e-7)

# Test preserved physical source stock independently of endpoint records.
for name in ['PortDriverLowRod','StarboardDriverLowRod']:
    q=s.world(name);f=pose(s.rows[name]['frame']);axis=f.Rotation.multVec(X)
    core=Part.makeCylinder(9.525,1257.3,f.Base,axis)
    ck(name+' complete49.5in M574 solid and proper stock ends',same(q,core))
    rec=d['rods'][name]
    ck(name+' actual receiver span preserves full printed rod',abs(math.dist(rec['rear_pin_world_mm'],rec['front_pin_world_mm'])-1308.1)<1e-7)
center=s.world('ClutchCenterRod');expected=accepted.world('ClutchCenterRod');expected.translate(V(*d['intermediate_translation_mm']))
ck('SH229A entire printed rod translated without deformation',same(center,expected))

if 'clutch_blade_profile' in d:
    key=s.rows['DriverClutchOperatingLever']['definition'];q=s.definition(key);old=accepted.definition(key)
    for label,zone in [('hub/bell',Part.makeBox(400,400,1040,V(-200,-200,-1000))),('grip',Part.makeBox(400,400,1000,V(-200,-200,600)))]:
        ck('M772 complete '+label+' material retained',same(q.common(zone),old.common(zone)))
    caps=[f.Surface for f in q.Faces if isinstance(f.Surface,Part.Sphere)]
    ck('M772 actual723.9mm hand reach',bool(caps) and all(abs(c.Center.Length+c.Radius-723.9)<1e-7 for c in caps))
    bell=pose(s.rows['DriverClutchOperatingLever']['frame']).inverse().multVec(V(*accepted.report['details']['clutch_bell_pin_world_mm'])+V(*d['driver_translation_from_accepted_mm']))
    ck('M772 actual127mm bell arm and receiving bore',abs(bell.Length-127)<1e-7 and bool(bores(q,bell,Y,6.5)))

# Changed fork frames are checked against actual saved receiver cylinders, pin
# stock, socket insertion and nut bearing. Fixed rear parts come from the bound
# retained development native, as in the separate full-context audit.
joints=[];ad=accepted.report['details']
fronts={'DriverClutchFrontRod':ad['rods']['Front']}
for side in ['Port','Starboard']:
    fronts[side+'DriverLowRod']=ad['low_speed'][side]
    fronts[side+'DriverHighFrontRod']=ad['high_controls'][side]['rods']['Front']
for rod,record in fronts.items():
    for end in record['endpoints']:joints.append((end['stem'],end['receiver'],rod,44.45,6.5,6.35))
longs=read(C/'redo01/long_rods_integrated01/report.json')['details']
for stem,j in longs['joints'].items():joints.append((stem,j['receiver'],j['rod'],44.45,6.5,6.35))
clutch=read(C/'redo01/clutch_swing_integrated02/report.json')['details']
for end in ['Rear','Forward']:
    j=clutch[end];joints.append(('ClutchRearRod'+end+'Joint',j['receiver'],'ClutchRearRod',j['fork_face_mm'],8.05 if end=='Rear' else 6.5,8. if end=='Rear' else 6.35))
for end,j in clutch['center_rod']['joints'].items():joints.append(('ClutchCenterRod'+end+'Joint',j['receiver'],'ClutchCenterRod',44.45,6.5,6.35))
for side in ['Port','Starboard']:
    joints.append((side+'HighIntermediateJoint',side+'HighIntermediateRocker',side+'RearHighRod',44.45,6.5,6.35))
    # Rear high fork/pin remain fixed and retain their earlier qualification;
    # check their actual rod socket directly, without assuming a new pin size.
    stem=side+'HighSpeedBrakeControl';fork=world(stem+'Fork');nut=world(stem+'Nut');rod=world(side+'RearHighRod')
    f=pose(accepted.rows[stem+'Fork']['frame']);axis=f.Rotation.multVec(X);face=f.Base+axis*61.9125
    ck(stem+' retained rear socket and full rod insertion',contact(fork,nut,face,axis)>70 and vol(Part.makeCylinder(9.525,38.1,face-axis*19.05,axis).cut(rod))<1e-4)
for stem,receiver,rodname,face_length,hole_radius,pin_radius in joints:
    fork,pin,nut,rod=world(stem+'Fork'),world(stem+'Pin'),world(stem+'Nut'),world(rodname)
    row=s.rows[stem+'Fork'] if stem+'Fork' in s.rows else accepted.rows[stem+'Fork'];frame=pose(row['frame'])
    point=frame.Base;axis=frame.Rotation.multVec(Y);along=frame.Rotation.multVec(X);host=world(receiver)
    fs=bores(host,point,axis,hole_radius)
    ck(stem+' actual coaxial receiver and pin',bool(fs) and bool(bores(pin,point,axis,pin_radius)))
    if fs:
        vv=[(v.Point-point).dot(axis) for f in fs for v in f.Vertexes];lo,hi=min(vv),max(vv)
        ck(stem+' pin spans full receiving material',vol(Part.makeCylinder(pin_radius,hi-lo,point+axis*lo,axis).cut(pin))<1e-5 and vol(pin.common(host))<1e-5)
    face=point+along*face_length
    ck(stem+' actual socket/nut bearing and full insertion',contact(fork,nut,face,along)>70 and vol(Part.makeCylinder(9.525,38.1,face-along*19.05,along).cut(rod))<1e-4)
    lifted=nut.copy();lifted.translate(along*.2)
    ck(stem+' lifted nut rejected',contact(fork,lifted,face,along)<1e-6)

# Driver plate/angle/floor joints, plus unchanged stay joints into revised webs.
mounts=d['driver_mount_joints']+[j for j in parent.report['details']['joints'] if 'Stay' in j['stem']]
for j in mounts:
    stem=j['stem'];point=V(*j['point_world_mm']);axis=V(*j['axis_world']);grip=j['grip_mm']
    bolt,lock,nut=[s.world(stem+v) for v in ['Bolt','Lock','Nut']];first,last=[s.world(n) for n in j['hosts']]
    radius=6.5 if j['bolt_diameter_mm']==12.7 else 9.65
    ck(stem+' actual receiving bores and complete bolt',all(bores(q,point,axis,radius) for q in [first,last]) and vol(Part.makeCylinder(j['bolt_diameter_mm']/2,j['bolt_length_mm'],point,axis).cut(bolt))<1e-5)
    ck(stem+' actual head/lock/nut contacts',contact(bolt,first,point,axis)>70 and contact(lock,last,point+axis*grip,axis)>70 and contact(lock,nut,point+axis*(grip+j['lock_stock_mm']),axis)>70)
    ck(stem+' connected receiving stack',mating(first,last)>70 and vol(first.common(last))<1e-5)
    lifted=bolt.copy();lifted.translate(-axis*.2)
    ck(stem+' lifted bolt rejected',contact(lifted,first,point,axis)<1e-6)

for side in ['Port','Starboard']:
    plate=s.world('Driver'+side+'SupportPlate');angle=s.world('DriverSeat'+side+'SupportAngle')
    for name,radius in [('DriverMainShaft',14.15),('DriverSwingShaft',12.15)]:
        ck(side+name+' real support bore',bool(bores(plate,pose(s.rows[name]['frame']).Base,Y,radius)))
    ck(side+' plate and angle physically joined',mating(plate,angle)>10000)

for floor,groups in [('hull_floor_3',['RearIntermediateSupportStrip','FrontIntermediateSupportStrip']),('hull_floor_6',['ClutchSwingBracket'])]:
    q=s.world(floor)
    for name in groups:
        item=s.world(name);ck(name+' actual relocated floor bearing',mating(item,q)>10000 and vol(item.common(q))<1e-5)
for j in d['floor_hole_changes']:
    floor=s.world(j['floor']);old=accepted.world(j['floor']);zones=[]
    for hole in j['holes']:
        name=hole['fastener'];base=pose(s.rows[name]['frame']).Base;radius=hole['radius_mm']
        ck(name+' actual relocated floor bore',bool(bores(floor,base,Z,radius)))
        for xy in [hole['old_xy'],hole['new_xy']]:zones.append(Part.makeCylinder(radius+.001,100,V(*xy,500),Z))
        if name.endswith('CapScrew'):
            screw=s.world(name);ck(name+' complete50.8mm stock and real head bearing',vol(Part.makeCylinder(6.35,50.8,base,Z).cut(screw))<1e-5 and contact(screw,floor,base,Z)>250)
        else:
            stem=name[:-4];bolt,lock,nut=[s.world(stem+v) for v in ['Bolt','Lock','Nut']]
            under=pose(s.rows[stem+'Lock']['frame']).Base
            ck(stem+' complete44.45mm bolt and seated nut stack',vol(Part.makeCylinder(6.35,44.45,base,-Z).cut(bolt))<1e-5 and contact(bolt,s.world('ClutchSwingBracket'),base,Z)>40 and contact(lock,floor,under,Z)>100 and contact(lock,nut,under-Z*3.175,Z)>100)
    zone=Part.makeCompound(zones)
    ck(j['floor']+' all non-mounting material protected',vol(old.cut(floor).cut(zone))<1e-5 and vol(floor.cut(old).cut(zone))<1e-5)

doc=App.openDocument(str(s.native))
for name,rec in d['rods'].items():
    obj=doc.getObject(name+'WirePath')
    if obj is None:continue
    wire=obj.Shape;rod=s.world(name);missing=[];curvature=[]
    for edge in wire.Edges:
        for i in range(1,8):
            u=edge.FirstParameter+(edge.LastParameter-edge.FirstParameter)*i/8
            point=edge.valueAt(u);tangent=edge.tangentAt(u);curvature.append(edge.curvatureAt(u))
            missing.append(vol(Part.makeCylinder(9.49,.02,point-tangent*.01,tangent).cut(rod)))
    ck(name+' continuous full-diameter material along saved path',max(missing)<1e-5 and max(curvature)*9.525<1,
        maximum_missing_mm3=max(missing),maximum_sampled_curvature=max(curvature))
    ck(name+' complete single rod volume sanity',len(wire.Wires)==1 and abs(rod.Volume/(math.pi*9.525**2*wire.Length)-1)<.01)
    if name=='ClutchCenterRod':ck('Saved SH229A93in centerline length',abs(wire.Length-2362.2)<1e-5)
App.closeDocument(doc.Name)
ck('No automatic historical or installation acceptance',not r['geometry_integrated'] and not r['installation_qualified'] and not d['source_camera_refitted'])
result=dict(passed=all(v['passed'] for v in checks),checks=checks,native_sha256=sha(s.native),
    checker_sha256=sha(Path(__file__)),manifest_sha256=sha(s.folder/'isolated/manifest.json'),
    scope='Saved canonical material, rigid groups, complete printed rods, physical fork/pin/socket interfaces and floor/seat mounts. Route sampling is a material diagnostic, not STEP acceptance. Full context separate.')
write(out/'independent_checks.json',result)
print('Coupled station checks:',len(checks),'checks;',sum(not v['passed'] for v in checks),'failed',flush=True)
assert result['passed']
