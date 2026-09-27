"""Independent saved stock, joints, keyseats, mounts and complete-route checks."""
import argparse,math
from pathlib import Path
from control_rebuild_io_v2 import *
from lib.camera_review import validate_native_bindings
V=App.Vector;X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args()
s=Saved(a.candidate);r=s.report;d=r['details'];parent=Saved((ROOT/r['parent_native']).parent);out=s.folder/'checks03';out.mkdir(exist_ok=False)
validate_native_bindings(dict(native_file=str(s.native),render_occurrences=list(s.rows),landmarks=[]),s.manifest)
assert all(sha(ROOT/f)==h for f,h in r['input_hashes'].items())
checks=[]
def ck(name,ok,**details):
 checks.append(dict(name=name,passed=bool(ok),**details));write(out/'progress.json',checks)
 if not ok:print('FAIL',name,details,flush=True)
def vol(q):return sum(abs(x.Volume) for x in q.Solids)
def same(one,two):return vol(one.cut(two))<1e-5 and vol(two.cut(one))<1e-5 and not one.cut(two,1e-4).Faces and not two.cut(one,1e-4).Faces
def cylinders(q,center,axis,radius):return [f for f in q.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-radius)<1e-6 and f.Surface.Axis.cross(axis).Length<1e-7 and (f.Surface.Center-center).cross(axis).Length<1e-6]
def planes(q,point,axis):return [f for f in q.Faces if isinstance(f.Surface,Part.Plane) and f.Surface.Axis.cross(axis).Length<1e-7 and abs((f.CenterOfMass-point).dot(axis))<1e-6]
def seat(one,two,point,axis):return sum(f.common(g).Area for f in planes(one,point,axis) for g in planes(two,point,axis))
def span(f,center,axis):
 values=[(v.Point-center).dot(axis) for v in f.Vertexes];return min(values),max(values)
c=d['controls'];bracket=s.world('ClutchSwingBracket');shaft=s.world('ClutchSwingShaft');floor=s.world('hull_floor_6');pivot=V(*d['pivot_world_mm']);base=pose(s.rows['ClutchSwingBracket']['frame']).Base
ck('Complete source inventory and bounded floor revision',len(r['new_occurrences'])==33 and len(r['new_definitions'])==8 and r['changed_definitions']==[parent.rows['hull_floor_6']['definition']])
for key in s.manifest['definitions']:
 q=s.definition(key);ck(key+' canonical closed valid solid',q.Placement.isIdentity() and q.isValid() and len(q.Solids)==1 and q.Solids[0].isClosed() and q.getTolerance(1)<=1e-4)
 if key not in r['new_definitions']+r['changed_definitions']:ck(key+' inherited material retained',same(q,parent.definition(key)))
for n,row in s.rows.items():ck(n+' actual saved frame',max(abs(x-y) for x,y in zip(row['frame'],r['specs'][n]['frame']))<1e-7)
ck('Real cast foot bearing on actual floor',seat(bracket,floor,base,Z)>10000 and vol(bracket.common(floor))<1e-5)
lift=bracket.copy();lift.translate(Z*.2);ck('Lifted foot loses bearing',seat(lift,floor,base,Z)<1e-6)
fs=cylinders(bracket,pivot,Y,12.85)
ck('Two coaxial full-stock journals',len(fs)==2 and abs(sum(f.Area for f in fs)-2*2*math.pi*12.85*10)<1e-5 and vol(bracket.common(shaft))<1e-5)
shaftlocal=s.definition('Def_ClutchSwingShaft_Redo');keylocal=s.definition('Def_ClutchSwingKey_Redo');nominal=Part.makeCylinder(12.7,c['shaft_length'],V(0,-c['shaft_length']/2,0),Y)
ck('Full source-hypothesis shaft envelope retained except two seats',vol(shaftlocal.cut(nominal))<1e-5)
# Woodruff shape is tested independently as a circular segment, including its
# orientation: thickness is tangential, while the arc runs along shaft length.
b=keylocal.BoundBox;radius=c['key_radius'];height=c['key_height'];area=radius**2*math.acos((radius-height)/radius)-(radius-height)*math.sqrt(2*radius*height-height**2)
ck('Woodruff segment stock and tangential thickness',abs(b.XLength-c['key_width'])<1e-7 and abs(b.ZLength-height)<1e-7 and abs(keylocal.Volume-area*c['key_width'])<1e-5)
ck('Woodruff circular edge lies in shaft-axis plane',bool(cylinders(keylocal,V(0,0,12.7+c['key_projection']-height+radius),X,radius)))
zones=[]
for i,(kind,dy,length) in enumerate(zip(['Short','Long'],c['link_y_offsets'],[c['short_arm'],c['long_arm']]),1):
 link=s.world('ClutchSwing'+kind+'Link');key=s.world('ClutchSwingKey'+str(i));center=pivot+Y*dy;eye=center-Z*length
 ck(kind+' distinct source mark and downward eye',s.manifest['definitions'][s.rows['ClutchSwing'+kind+'Link']['definition']]['properties']['SourcePartMark']==('SH944B' if kind=='Short' else 'SH944C') and len(cylinders(link,eye,Y,6.5))==1 and eye.z<pivot.z)
 ck(kind+' complete eye bore survives web unions',abs(sum(f.Area for f in cylinders(link,eye,Y,6.5))-2*math.pi*6.5*12)<1e-5)
 fs=cylinders(link,center,Y,12.825)
 ck(kind+' full-width bored hub with explicit split and keyway',bool(fs) and all(abs(span(f,center,Y)[1]-span(f,center,Y)[0]-20)<1e-6 for f in fs) and sum(f.Area for f in fs)>math.pi*12.825*20 and vol(link.common(Part.makeCylinder(12.825,20,center-Y*10,Y)))<1e-5)
 ck(kind+' real key fits both shaft and hub without intersections',vol(key.common(shaft))<1e-5 and vol(key.common(link))<1e-5 and vol(link.common(shaft))<1e-5)
 # Both inward and outward key stock must exist, rather than a floating key
 # entirely within one member's clearance hole.
 cylinder=Part.makeCylinder(12.7,30,center-Y*15,Y)
 ck(kind+' key actually bridges shaft and hub radial envelopes',vol(key.common(cylinder))>400 and vol(key.cut(cylinder))>100,in_shaft_envelope_mm3=vol(key.common(cylinder)),outside_shaft_mm3=vol(key.cut(cylinder)))
 ck(kind+' keyway has real flat drive faces',len(planes(link,center+V(c['key_width']/2+.025,0,0),X))>0 and len(planes(link,center-V(c['key_width']/2+.025,0,0),X))>0)
 localkey=keylocal.copy();localkey.translate(Y*dy);kb=localkey.BoundBox;zone=Part.makeBox(c['key_width']+.1,2*radius+.1,2*radius+1,V(-c['key_width']/2-.05,dy-radius-.05,12.7+c['key_projection']-height-1));zones.append(zone)
 for role in ['Bolt','Lock','Nut']:
  name='ClutchSwing'+kind+'Clamp'+role;q=s.world(name)
  if role=='Bolt':
   origin=pose(s.rows[name]['frame']).Base;core=Part.makeCylinder(6.35,63.5,origin,-Z)
   ck(kind+' source-length clamp bolt complete',vol(core.cut(q))<1e-5 and seat(q,link,origin,Z)>40)
 lock=s.world('ClutchSwing'+kind+'ClampLock');nut=s.world('ClutchSwing'+kind+'ClampNut');bolt=s.world('ClutchSwing'+kind+'ClampBolt')
 ck(kind+' actual clamp lock and nut seating',seat(link,lock,center+V(30,0,-20),Z)>100 and seat(lock,nut,center+V(30,0,-23.175),Z)>100)
 ck(kind+' bolt passes both ears and complete nut',all(vol(bolt.common(v))<1e-5 for v in [link,lock,nut]) and vol(Part.makeCylinder(6.35,54.2875,center+V(30,0,20),-Z).cut(bolt))<1e-5)
 ck(kind+' clamp split remains open',vol(link.common(Part.makeBox(15,22,1.8,center+V(24,-11,-.9))))<1e-5)
ck('Shaft material changes confined to two actual key neighborhoods',vol(nominal.cut(shaftlocal).cut(Part.makeCompound(zones)))<1e-5)
# Full source-sized mounting stock, true floor bores, flat head/lock/nut faces.
tools=[]
for m in d['mounts']:
 i=m['index'];head=V(*m['head_seat_world_mm']);under=V(*m['lock_seat_world_mm']);bolt=s.world('ClutchSwingMount'+str(i)+'Bolt');lock=s.world('ClutchSwingMount'+str(i)+'Lock');nut=s.world('ClutchSwingMount'+str(i)+'Nut')
 tools.append(Part.makeCylinder(6.5,8,V(head.x,head.y,526.05)))
 ck(str(i)+' source bolt and real two-sided mount seating',vol(Part.makeCylinder(6.35,44.45,head,-Z).cut(bolt))<1e-5 and seat(bolt,bracket,head,Z)>40 and seat(lock,floor,under,Z)>100 and seat(lock,nut,under-Z*3.175,Z)>100)
 ck(str(i)+' actual complete floor hole',len(cylinders(floor,under,Z,6.5))==1 and abs(sum(f.Area for f in cylinders(floor,under,Z,6.5))-2*math.pi*6.5*6)<1e-5)
 ck(str(i)+' bolt shaft clears all physical receiving stock',all(vol(bolt.common(v))<1e-5 for v in [bracket,floor,lock,nut]))
 ck(str(i)+' source bolt has full nut engagement and protrusion',44.45-(head.z-under.z)-3.175-11.1125>=3.9)
ck('Floor revised only by four declared through holes',same(floor,parent.world('hull_floor_6').cut(Part.makeCompound(tools))))
rod=s.world('ClutchRearRod')
for end in ['Rear','Forward']:
 j=d[end];stem='ClutchRearRod'+end+'Joint';frame=pose(s.rows[stem+'Fork']['frame']);center=frame.Base;axis=frame.Rotation.multVec(Y);rodaxis=frame.Rotation.multVec(X)
 receiver=s.world(j['receiver']);fork=s.world(stem+'Fork');pin=s.world(stem+'Pin');nut=s.world(stem+'Nut');cotter=s.world(stem+'Cotter');radius=8.05 if end=='Rear' else 6.5;prad=8 if end=='Rear' else 6.35
 fs=cylinders(receiver,center,axis,radius)
 ck(end+' actual receiver bore and correct distinct pin family',len(fs)==1 and bool(cylinders(pin,center,axis,prad)))
 if fs:
  lo,hi=span(fs[0],center,axis);ck(end+' pin stock spans full receiving eye',vol(Part.makeCylinder(prad,hi-lo,center+axis*lo,axis).cut(pin))<1e-5)
 face=center+rodaxis*j['fork_face_mm'];ck(end+' socket engagement and complete nut stock',vol(Part.makeCylinder(9.525,38.1,face-rodaxis*19.05,rodaxis).cut(rod))<1e-4 and seat(fork,nut,face,rodaxis)>200)
 ck(end+' all actual joint material clears',all(vol(one.common(two))<1e-5 for one,two in [(fork,receiver),(fork,pin),(fork,cotter),(pin,cotter),(nut,rod),(fork,rod)]))
doc=App.openDocument(str(s.native));wire=doc.ClutchRearRodWirePath.Shape;missing=[];curvature=[]
for e in wire.Edges:
 for i in range(1,20):
  u=e.FirstParameter+(e.LastParameter-e.FirstParameter)*i/20;point=e.valueAt(u);tangent=e.tangentAt(u);curvature.append(e.curvatureAt(u));missing.append(vol(Part.makeCylinder(9.49,.02,point-tangent*.01,tangent).cut(rod)))
ck('Complete M581 stock along every span',max(missing)<1e-5 and max(curvature)*9.525<1,maximum_missing_mm3=max(missing),minimum_sampled_radius_mm=1/max(curvature))
ck('One continuous full-diameter M581 rod',len(rod.Solids)==1 and len(wire.Wires)==1 and abs(rod.Volume/(math.pi*9.525**2*wire.Length)-1)<.01)
App.closeDocument(doc.Name)
result=dict(passed=all(v['passed'] for v in checks),checks=checks,native_sha256=sha(s.native),manifest_sha256=sha(s.folder/'isolated/manifest.json'),checker_sha256=sha(Path(__file__)),scope='Actual shaft/key/hub stock, source fastener lengths, four floor mounts, distinct rod-end families and complete continuous rod. Historical mounting and key-size interpretation remain separate.')
write(out/'independent_checks.json',result);print('FINISHED',len(checks),'checks',sum(not v['passed'] for v in checks),'failed',flush=True)
assert result['passed']
