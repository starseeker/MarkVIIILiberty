"""Check actual saved low-selector stock, diagonal receiving joints and retained context."""
import argparse,math,json
from pathlib import Path
from control_rebuild_io_v2 import *
from lib.camera_review import validate_native_bindings
V=App.Vector;X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();s=Saved(a.candidate);r=s.report;d=r['details'];c=d['selector_controls'];parent=Saved((ROOT/r['parent_native']).parent);out=s.folder/'checks03';out.mkdir(exist_ok=False)
validate_native_bindings(dict(native_file=str(s.native),render_occurrences=list(s.rows),landmarks=[]),s.manifest)
assert all(sha(ROOT/f)==h for f,h in r['input_hashes'].items())
checks=[]
def ck(name,ok,**detail):
    checks.append(dict(name=name,passed=bool(ok),**detail));write(out/'progress.json',checks)
    if not ok:print('FAIL',name,detail,flush=True)
def vol(q):return sum(abs(v.Volume) for v in q.Solids)
def same(q,t):return vol(q.cut(t))<1e-5 and vol(t.cut(q))<1e-5 and not q.cut(t,1e-4).Faces and not t.cut(q,1e-4).Faces
def cyl(q,p,axis,radius):return [f for f in q.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-radius)<1e-6 and f.Surface.Axis.cross(axis).Length<1e-7 and (f.Surface.Center-p).cross(axis).Length<1e-6]
def planes(q,p,axis):return [f for f in q.Faces if isinstance(f.Surface,Part.Plane) and f.Surface.Axis.cross(axis).Length<1e-7 and abs((f.CenterOfMass-p).dot(axis))<1e-6]
def bearing(q,t,p,axis):return sum(f.common(g).Area for f in planes(q,p,axis) for g in planes(t,p,axis))
def moved(q,v):z=q.copy();z.translate(v);return z
def block(a,b,halfwidth,stock):
    axis=b-a;axis.normalize();n=V(-axis.z,0,axis.x)*halfwidth
    vs=[a+n-Y*stock/2,b+n-Y*stock/2,b-n-Y*stock/2,a-n-Y*stock/2]
    return Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(Y*stock)
ck('Six real additions, three definitions, only shared M762 changed',len(r['new_occurrences'])==6 and len(r['new_definitions'])==3 and r['changed_definitions']==['Def_DriverLowConnecting_M762'] and len(s.rows)==100)
for key in s.manifest['definitions']:
    q=s.definition(key);ck(key+' closed canonical solid',q.Placement.isIdentity() and q.isValid() and len(q.Solids)==1 and q.Solids[0].isClosed() and q.getTolerance(1)<=1e-4)
    if key in parent.manifest['definitions'] and key not in r['changed_definitions']:ck(key+' inherited material preserved',same(q,parent.definition(key)))
for name,row in s.rows.items():
    ck(name+' saved frame',max(abs(a-b) for a,b in zip(row['frame'],r['specs'][name]['frame']))<1e-7)
    if name in parent.rows:ck(name+' retained identity and world frame',row['definition']==parent.rows[name]['definition'] and max(abs(a-b) for a,b in zip(row['frame'],parent.rows[name]['frame']))<1e-7)
ck('Correct M790 source and reused source-sized keeper',json.loads(s.manifest['definitions']['Def_DriverLowSelectorJointPin_M790']['properties']['SourceRecords'])==['SNL:137:009','HB:113'] and s.rows['PortDriverLowSelectorKeeper']['definition']==s.rows['PortDriverLowKeeper']['definition'])
shaft=s.world('DriverMainShaft');kc=d['controls']['low_keeper'];main=V(*d['foundation']['shafts']['Main']['center_world_mm']);pick=read(ROOT/'cad/003_FullTank/experiments/drive_chains/transmission_controls_study/driver_redo01/selector_landmarks01.json')
ck('Upper M790 eye uses distinct reviewed source pick',(V(*c['front_relative_to_main'])-V(*pick['inferred_offset_from_main_mm'])).Length<2,construction_not_holdout=True)
for side,sign,mark,rowid in [('Port',1,'M756','SNL:117:029'),('Starboard',-1,'M757','SNL:117:030')]:
    stem=side+'DriverLowSelector';v=d['low_selectors'][side];pivot=V(*v['pivot_world_mm']);point=V(*v['pin_world_mm']);eye=V(*v['connecting_eye_world_mm']);head=V(*v['pin_head_seat_world_mm']);kp=V(*v['pin_keeper_world_mm'])
    lever=s.world(stem);conn=s.world(side+'DriverLowConnecting');pin=s.world(stem+'Pin');keeper=s.world(stem+'Keeper');susp=s.world(side+'DriverLowSuspension');brake=s.world(side+'DriverLowBrake');oldpin=s.world(side+'DriverLowPin');washer=s.world(side+'DriverLowWasher')
    sources=json.loads(s.manifest['definitions'][s.rows[stem]['definition']]['properties']['SourceRecords']);ck(stem+' selected handed identity',s.manifest['definitions'][s.rows[stem]['definition']]['properties']['SourcePartMark']==mark and rowid in sources)
    fs=cyl(lever,pivot,Y,19.1619)
    ck(stem+' full actual shaft and24mm bearing span',bool(fs) and all(abs(max((v.Point-pivot).y for v in f.Vertexes)-min((v.Point-pivot).y for v in f.Vertexes)-24)<1e-6 for f in fs) and vol(Part.makeCylinder(19.0119,24,pivot-Y*12,Y).cut(shaft))<1e-5 and vol(lever.common(shaft))<1e-5)
    hub=Part.makeCylinder(32,24,pivot-Y*12,Y).cut(Part.makeCylinder(19.1619,26,pivot-Y*13,Y)).cut(Part.makeCylinder(1.5,34,pivot,-X))
    ck(stem+' complete journal hub with real oil passage',vol(hub.cut(lever))<1e-5 and bool(cyl(lever,pivot,X,1.5)))
    upper=pivot+V(*c['front_relative_to_main']);knee=V(*d['low_speed'][side]['knee_world_mm'])+Y*c['connecting_y'];axis=eye-knee;length=axis.Length;axis.normalize()
    for label,q,p,width in [('selector',lever,upper,12.7),('front_link',conn,eye,10.),('rear_link',conn,knee,10.)]:
        fs=cyl(q,p,Y,9.625);ck(stem+' '+label+' complete coaxial receiving bore',len(fs)==1 and abs(fs[0].Area-2*math.pi*9.625*width)<1e-5)
        annulus=Part.makeCylinder(20,width,p-Y*width/2,Y).cut(Part.makeCylinder(9.625,width+2,p-Y*(width/2+1),Y));ck(stem+' '+label+' full annular bearing stock',vol(annulus.cut(q))<1e-5)
    # Independently constructed middle strap verifies the actual diagonal load path.
    strap=block(knee+axis*27,eye-axis*27,14,10)
    ck(stem+' complete straight diagonal web',vol(strap.cut(conn))<1e-5,eye_distance_mm=length)
    ck(stem+' source topology is above main shaft and aft',point.z>main.z+90 and point.x<main.x-89 and knee.z<main.z-140)
    ck(stem+' complete M790 stock through both eyes',vol(Part.makeCylinder(9.525,31.75,head,-Y).cut(pin).cut(Part.makeCylinder(2.5,21.05,kp-X*10.525,X)))<1e-5 and bool(cyl(pin,head,Y,9.525)))
    # Check full stock against independent head/shank minus transverse drilling.
    expected=Part.makeCylinder(9.525,31.75,head,-Y).fuse(Part.makeCylinder(14,4.5,head,Y)).cut(Part.makeCylinder(2.5,21.05,kp-X*10.525,X));ck(stem+' exact complete selected pin material',same(pin,expected))
    area=bearing(pin,lever,head,Y);ck(stem+' actual pin-head seating',abs(area-math.pi*(14**2-9.625**2))<1e-5,bearing_mm2=area)
    ck(stem+' true cross drilling and retained cotter',bool(cyl(pin,kp,X,2.5)) and vol(pin.common(keeper))<1e-5 and kp.y+4.7625/2<eye.y-5)
    # The inherited split pin is read as material, with both complete source legs.
    half=kc['cotter_center_spacing']/2;wire=(4.7625-kc['cotter_center_spacing'])/2;start=-kc['crown_radius']-kc['cotter_head_gap'];bend=kc['crown_radius']+kc['cotter_exit_gap'];angle=math.radians(kc['cotter_bend_angle']);straight=bend-start;tail=31.75-straight-kc['cotter_bend_radius']*angle
    for hand in [-1,1]:
        a=kp+X*start+Z*(hand*half);b=kp+X*(bend+kc['cotter_bend_radius']*math.sin(angle))+Z*(hand*(half+kc['cotter_bend_radius']*(1-math.cos(angle))));direction=X*math.cos(angle)+Z*(hand*math.sin(angle))
        ck(stem+' complete source keeper leg '+str(hand),tail>0 and vol(Part.makeCylinder(wire,straight,a,X).cut(keeper))<1e-5 and vol(Part.makeCylinder(wire,tail,b,direction).cut(keeper))<1e-5)
    ck(stem+' keeper blocks pin withdrawal',vol(moved(pin,Y*5).common(keeper))>1)
    ck(stem+' displaced pin is rejected',vol(moved(pin,X*3).common(lever))>1)
    ck(stem+' lifted head loses bearing',bearing(moved(pin,Y*.2),lever,head,Y)<1e-6)
    # Existing rear three-link knee and washer contacts must survive the new web.
    oldhead=V(*d['low_speed'][side]['knee_world_mm'])+Y*d['controls']['pin_head_seat_y'];ws=V(*d['low_speed'][side]['knee_world_mm'])+Y*d['controls']['washer_seat_y']
    ck(stem+' retained rear pin and washer seating',abs(bearing(oldpin,conn,oldhead,Y)-math.pi*(14**2-9.625**2))<1e-5 and abs(bearing(washer,conn,ws,Y)-math.pi*(15**2-9.625**2))<1e-5)
    parts=[lever,conn,pin,keeper,susp,brake,oldpin,washer,s.world(side+'DriverLowKeeper')]
    ck(stem+' all front and rear joint materials clear',all(vol(q.common(t))<1e-5 for i,q in enumerate(parts) for t in parts[i+1:]))
    # A physical side-opening gate, with full two lips and empty lever slot.
    direct=V(*c['selector_gate_direction']);n=V(-direct.z,0,direct.x);inside=-sign*c['selector_gate_inward_depth'];outer=-sign*(c['selector_web_stock']/2+.5);a1,a2=sorted([inside+sign*.5,outer]);rad0=c['selector_gate_lower_radius']+c['selector_gate_lip_stock']+.5;rad1=c['selector_gate_upper_radius']-c['selector_gate_lip_stock']-.5
    gate=block(pivot+direct*rad0+Y*((a1+a2)/2),pivot+direct*rad1+Y*((a1+a2)/2),15.5,a2-a1)
    ck(stem+' actual open side gate',vol(gate.common(lever))<1e-5 and gate.Volume>20000)
    for a,b in [(215.5,227.2),(272.8,284.5)]:
        lip=block(pivot+direct*a+Y*((a1+a2)/2),pivot+direct*b+Y*((a1+a2)/2),15.5,a2-a1);ck(stem+' full gate lip '+str(a),vol(lip.cut(lever))<1e-5)
result=dict(passed=all(v['passed'] for v in checks),checks=checks,native_sha256=sha(s.native),manifest_sha256=sha(s.folder/'isolated/manifest.json'),checker_sha256=sha(Path(__file__)),scope='Actual saved stock, bores, bearing faces, source-sized cotters, retained knees and negative controls. Historical form and motion remain unqualified.')
write(out/'independent_checks.json',result);print('Selector checks',len(checks),'passed',result['passed'],flush=True);assert result['passed']
