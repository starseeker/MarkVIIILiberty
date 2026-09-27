"""Independent saved-material checks of driver shafts and sloped floor mounts."""
import argparse,math
from pathlib import Path
from control_rebuild_io_v2 import *
from lib.camera_review import validate_native_bindings
V=App.Vector;X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();s=Saved(a.candidate);r=s.report;d=r['details'];c=d['controls'];parent=Saved((ROOT/r['parent_native']).parent)
out=s.folder/'checks03';out.mkdir(exist_ok=False);checks=[]
validate_native_bindings(dict(native_file=str(s.native),render_occurrences=list(s.rows),landmarks=[]),s.manifest)
assert all(sha(ROOT/f)==h for f,h in r['input_hashes'].items())
def ck(n,ok,**kw):checks.append(dict(name=n,passed=bool(ok),**kw))
def vol(q):return sum(abs(v.Volume) for v in q.Solids)
def same(q,t):return vol(q.cut(t))<1e-5 and vol(t.cut(q))<1e-5 and not q.cut(t,1e-4).Faces and not t.cut(q,1e-4).Faces
def moved(q,v):t=q.copy();t.translate(v);return t
def cyl(q,point,axis,radius):
    return [f for f in q.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-radius)<1e-6 and f.Surface.Axis.cross(axis).Length<1e-7 and (f.Surface.Center-point).cross(axis).Length<1e-6]
def span(f,point,axis):
    v=[(q.Point-point).dot(axis) for q in f.Vertexes];return min(v),max(v)
def planes(q,point,axis):
    return [f for f in q.Faces if isinstance(f.Surface,Part.Plane) and f.Surface.Axis.cross(axis).Length<1e-7 and abs((f.CenterOfMass-point).dot(axis))<1e-6]
def bearing(q,t,point,axis):return sum(f.common(g).Area for f in planes(q,point,axis) for g in planes(t,point,axis))
ck('38 components, nine new and four reused definitions; additive parent',len(s.rows)==38 and len(r['new_occurrences'])==38 and len(r['new_definitions'])==9 and len(s.manifest['definitions'])==13 and not r['changed_definitions'])
for key in s.manifest['definitions']:
    q=s.definition(key);ck(key+' closed canonical solid',q.Placement.isIdentity() and q.isValid() and len(q.Solids)==1 and q.Solids[0].isClosed() and q.getTolerance(1)<=1e-4)
    if key in parent.manifest['definitions']:ck(key+' inherited material unchanged',same(q,parent.definition(key)))
for n,row in s.rows.items():ck(n+' saved world frame',max(abs(x-y) for x,y in zip(row['frame'],r['specs'][n]['frame']))<1e-7)
normal=V(*d['floor_normal']);probe=read(ROOT/c['floor_probe']);t=c['plate_stock']
for floorname,old in probe['floors'].items():
    original=Part.Shape();original.read(str(ROOT/old['brep']));floor=s.world(floorname);holes=[]
    for m in d['mounts']:
        if m['floor']!=floorname:continue
        base=V(*m['floor_contact_world_mm']);holes.append(Part.makeCylinder(6.5,8,base+normal,-normal));faces=cyl(floor,base,normal,6.5)
        ck(m['stem']+' actual six-mm floor bore',len(faces)==1 and abs(span(faces[0],base,normal)[0]+6)<1e-6 and abs(span(faces[0],base,normal)[1])<1e-6)
    ck(floorname+' exactly four new bores and all other material retained',len(holes)==4 and same(floor,original.cut(Part.makeCompound(holes))) and abs(original.Volume-floor.Volume-4*math.pi*6.5**2*6)<1e-5)
for side in ['Port','Starboard']:
    plate=s.world('Driver'+side+'SupportPlate');base=V(*d['mounts'][0 if side=='Port' else 4]['floor_contact_world_mm']);floor=Part.makeCompound([s.world(n) for n in probe['floors']]);area=bearing(plate,floor,base,normal)
    ck(side+' full foot seated on original sloping floor',area>20000 and vol(plate.common(floor))<1e-5 and bearing(moved(plate,normal*.2),floor,base,normal)<1e-6,bearing_mm2=area)
for m in d['mounts']:
    stem=m['stem'];head=V(*m['head_seat_world_mm']);lockseat=V(*m['lock_seat_world_mm']);nutseat=V(*m['nut_seat_world_mm']);axis=-normal
    bolt=s.world(stem+'Bolt');lock=s.world(stem+'Lock');nut=s.world(stem+'Nut');plate=s.world(m['plate']);floor=s.world(m['floor'])
    core=Part.makeCylinder(6.35,31.75,head,axis);faces=cyl(plate,head,normal,6.5)
    ck(stem+' complete printed half-inch by1-1/4in stock',vol(core.cut(bolt))<1e-5 and 31.75-t-6-3.175-11.1125>3.9)
    ck(stem+' uninterrupted plate bore through full foot',len(faces)==1 and abs(span(faces[0],head,normal)[0]+t)<1e-6 and abs(span(faces[0],head,normal)[1])<1e-6)
    for label,q,w,point,minarea in [('head',bolt,plate,head,150),('lock',lock,floor,lockseat,150),('nut',nut,lock,nutseat,100)]:
        area=bearing(q,w,point,normal);ck(stem+' '+label+' actual seat',area>minarea and vol(q.common(w))<1e-5 and bearing(moved(q,normal*.2),w,point,normal)<1e-6,bearing_mm2=area)
    # Moving one complete bolt off its real receiving bore must be rejected.
    ck(stem+' displaced bolt intersects mounting material',vol(moved(bolt,Y*8).common(plate))>10)
for kind,radius,endradius,total in [('Main',19.0119,14,628.65),('Swing',12.7,12,c['swing_length'])]:
    info=d['shafts'][kind];center=V(*info['center_world_mm']);shaft=s.world('Driver'+kind+'Shaft');shoulder=info['shoulder_station_mm'];faces=cyl(shaft,center,Y,radius)
    ck(kind+' full central cylindrical journal and total stock',len(faces)==1 and abs(faces[0].Area-2*math.pi*radius*2*shoulder)<1e-5 and abs(shaft.BoundBox.YLength-total)<1e-6)
    for side,sign in [('Port',1),('Starboard',-1)]:
        plate=s.world('Driver'+side+'SupportPlate');nut=s.world('Driver'+kind+side+'Nut');keeper=s.world('Driver'+kind+side+'Keeper');seat=center+Y*(sign*info['nut_seat_station_mm']);inner=center+Y*(sign*shoulder);pin=center+Y*(sign*info['keeper_station_mm'])
        faces=cyl(plate,center,Y,endradius+.15)
        ck(kind+side+' real bearing with full reduced shaft stock',len(faces)==1 and abs(span(faces[0],center,Y)[1]-span(faces[0],center,Y)[0]-t)<1e-6 and vol(Part.makeCylinder(endradius,t,inner,Y*sign).cut(shaft))<1e-5 and vol(shaft.common(plate))<1e-5)
        a1=bearing(shaft,plate,inner,Y);a2=bearing(nut,plate,seat,Y)
        ck(kind+side+' shaft shoulder and complete nut seat capture plate',a1>20 and a2>150 and vol(nut.common(plate))<1e-5,shoulder_bearing_mm2=a1,nut_bearing_mm2=a2)
        # M783 keeper crosses the outer three mm of threaded stock, so test
        # only the complete unpierced nut base here, then the declared bore.
        baseheight=7 if kind=='Swing' else 14
        ck(kind+side+' complete nut engagement and declared transverse bore',vol(Part.makeCylinder(endradius,baseheight,seat,Y*sign).cut(shaft))<1e-5 and bool(cyl(shaft,pin,X,2.5)) and vol(shaft.common(Part.makeCylinder(2.5,2*endradius+2,pin-X*(endradius+1),X)))<1e-5)
        ck(kind+side+' retained pin without material overlaps',all(vol(q.common(w))<1e-5 for q,w in [(shaft,nut),(shaft,keeper),(nut,keeper)]))
        ck(kind+side+' displaced keeper rejected',vol(moved(keeper,Y*5).common(shaft))>1)
        if kind=='Swing':
            ck(kind+side+' keeper lies within castle depth',7<info['keeper_station_mm']-info['nut_seat_station_mm']<13 and vol(moved(nut,Y*(sign*4)).common(keeper))>1)
        else:ck(kind+side+' short keeper blocks nut escape with declared axial play',vol(moved(nut,Y*(sign*4)).common(keeper))>1)
    # Source-length keeper legs: independent interior samples through straight,
    # curved and tail stock, instead of trusting the builder's reported length.
    pc=c[kind.lower()+'_keeper'];length=38.1 if kind=='Main' else 50.8;k=s.definition('Def_Driver'+kind+'Keeper_MountStudy')
    half=pc['cotter_center_spacing']/2;wire=(4.7625-pc['cotter_center_spacing'])/2;head=-pc['crown_radius']-pc['cotter_head_gap'];bend=pc['crown_radius']+pc['cotter_exit_gap'];rad=pc['cotter_bend_radius'];angle=math.radians(pc['cotter_bend_angle']);straight=bend-head;tail=length-straight-rad*angle;missing=[]
    for sign in [-1,1]:
        for j in range(1,15):
            point=V(0,head+straight*j/15,sign*half);missing.append(vol(Part.makeCylinder(wire-.01,.02,point-Y*.01,Y).cut(k)))
            theta=angle*j/15;point=V(0,bend+rad*math.sin(theta),sign*(half+rad*(1-math.cos(theta))));tangent=V(0,math.cos(theta),sign*math.sin(theta));missing.append(vol(Part.makeCylinder(wire-.01,.02,point-tangent*.01,tangent).cut(k)))
            point=V(0,bend+rad*math.sin(angle),sign*(half+rad*(1-math.cos(angle))));tangent=V(0,math.cos(angle),sign*math.sin(angle));point+=tangent*(tail*j/15);missing.append(vol(Part.makeCylinder(wire-.01,.02,point-tangent*.01,tangent).cut(k)))
    ck(kind+' complete source-sized keeper legs',abs(pc['cotter_length']-length)<1e-9 and abs(pc['cotter_diameter']-4.7625)<1e-9 and tail>0 and max(missing)<1e-5,maximum_missing_mm3=max(missing))
result=dict(passed=all(v['passed'] for v in checks),checks=checks,native_sha256=sha(s.native),manifest_sha256=sha(s.folder/'isolated/manifest.json'),checker_sha256=sha(Path(__file__)),scope='Local static support-interface hypothesis. Complete seat mounts, controls, motion and historical plate geometry remain unqualified.')
write(out/'independent_checks.json',result);print(len(checks),'checks;',result['passed'],flush=True)
for v in checks:
    if not v['passed']:print(v,flush=True)
assert result['passed']
