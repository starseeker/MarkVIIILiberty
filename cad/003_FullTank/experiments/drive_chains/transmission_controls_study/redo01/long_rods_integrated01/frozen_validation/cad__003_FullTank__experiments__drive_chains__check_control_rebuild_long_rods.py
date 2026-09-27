"""Independent saved stock, joints, receiver preservation and complete-route checks."""
import argparse,math
from pathlib import Path
from control_rebuild_io_v2 import *
from lib.camera_review import validate_native_bindings
V=App.Vector;X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args()
s=Saved(a.candidate);r=s.report;d=r['details'];parent=Saved((ROOT/r['parent_native']).parent);out=s.folder/'checks02';out.mkdir(exist_ok=False)
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
ck('Four complete rods and eight complete four-part joints',len(r['new_occurrences'])==36 and len(r['new_definitions'])==4 and len(d['joints'])==8)
for key in s.manifest['definitions']:
 q=s.definition(key);ck(key+' canonical closed valid solid',q.Placement.isIdentity() and q.isValid() and len(q.Solids)==1 and q.Solids[0].isClosed() and q.getTolerance(1)<=1e-4)
 if key not in r['new_definitions']+r['changed_definitions']:ck(key+' retained material',same(q,parent.definition(key)))
for n,row in s.rows.items():
 ck(n+' actual saved frame',max(abs(x-y) for x,y in zip(row['frame'],r['specs'][n]['frame']))<1e-7)
 if n in parent.rows:ck(n+' inherited frame unchanged',max(abs(x-y) for x,y in zip(row['frame'],parent.rows[n]['frame']))<1e-7)
rocker=s.definition('Def_ControlRocker_Redo');old=parent.definition('Def_ControlRocker_Redo');inner=d['controls']['inner_arm_radius']
zone=Part.makeCompound([Part.makeCylinder(13,14,V(0,-7,z),Y) for z in [76.2,inner]])
ck('Shared M640 revision confined to inner-eye stock and bore',vol(rocker.cut(old).cut(zone))<1e-5 and vol(old.cut(rocker).cut(zone))<1e-5)
for z,rad,width in [(0,12.825,34),(inner,6.5,12),(101.6,6.5,12)]:
 fs=cylinders(rocker,V(0,0,z),Y,rad);ck('Actual rocker bore '+str(z),len(fs)==1 and abs(sum(f.Area for f in fs)-2*math.pi*rad*width)<1e-5)
ck('All ten shared rocker occurrences included',sum(v['definition']=='Def_ControlRocker_Redo' for v in s.rows.values())==10)
for stem,j in d['joints'].items():
 frame=pose(s.rows[stem+'Fork']['frame']);center=frame.Base;axis=frame.Rotation.multVec(Y);rodaxis=frame.Rotation.multVec(X)
 receiver=s.world(j['receiver']);fork=s.world(stem+'Fork');pin=s.world(stem+'Pin');cotter=s.world(stem+'Cotter');nut=s.world(stem+'Nut');rod=s.world(j['rod'])
 fs=cylinders(receiver,center,axis,6.5)
 ck(stem+' actual receiver and correct pin',len(fs)==1 and s.manifest['definitions'][s.rows[stem+'Pin']['definition']]['properties']['SourcePartMark']=='M568C' and bool(cylinders(pin,center,axis,6.35)))
 if fs:
  lo,hi=span(fs[0],center,axis);witness=Part.makeCylinder(6.35,hi-lo,center+axis*lo,axis)
  ck(stem+' complete pin stock through receiver',vol(witness.cut(pin))<1e-5 and vol(pin.common(receiver))<1e-5)
 ck(stem+' complete joint material clearance',all(vol(one.common(two))<1e-5 for one,two in [(fork,receiver),(fork,pin),(fork,cotter),(pin,cotter),(nut,rod),(fork,rod)]))
 face=center+rodaxis*44.45;area=seat(fork,nut,face,rodaxis)
 ck(stem+' complete real socket/nut bearing',abs(area-math.pi*(12.7**2-9.625**2))<1e-5,bearing_mm2=area)
 witness=Part.makeCylinder(9.525,38.1,face-rodaxis*19.05,rodaxis)
 ck(stem+' full insertion and nut stock coverage',vol(witness.cut(rod))<1e-4 and bool(cylinders(fork,face,rodaxis,9.625)))
 lifted=nut.copy();lifted.translate(rodaxis*.2)
 ck(stem+' bearing separates under negative perturbation',seat(lifted,fork,face,rodaxis)<1e-6)
# Witness future front forks against actual occupied outer receivers. These
# temporary solids do not enter the physical assembly or BOM.
template=s.definition(s.rows['PortLowLongIntermediateJointFork']['definition'])
for n,row in s.rows.items():
 if 'IntermediateRocker' not in n:continue
 frame=pose(row['frame']);center=frame.multVec(V(0,0,inner));axis=frame.Rotation.multVec(Y)
 f=template.copy();f.Placement=App.Placement(center,App.Rotation(X,axis,X.cross(axis),'XYZ'))
 neighbors=[s.world(n)]
 side='Port' if n.startswith('Port') else 'Starboard' if n.startswith('Starboard') else None
 if side:
  if 'High' in n:neighbors += [parent.world(side+'HighIntermediateJoint'+role) for role in ['Fork','Pin','Cotter','Nut']]
  elif 'Low' in n or 'Foot' in n:
   kind='Low' if 'Low' in n else 'Foot';neighbors += [s.world(side+kind+'LongIntermediateJoint'+role) for role in ['Fork','Pin','Cotter','Nut']]
 ck(n+' future inner fork fits actual occupied outer joint',all(vol(f.common(v))<1e-5 for v in neighbors))
 low=s.world('PortLowIntermediateRocker')
front=pose(s.rows['PortLowIntermediateRocker']['frame']).multVec(V(0,0,inner));driver=V(*d['provisional_driver_low_port_pin_mm'])
ck('Printed M574 length retained against revised provisional driver datum',abs((driver-front).Length-1308.1)<1e-7 and driver.y==180 and driver.z==890)
doc=App.openDocument(str(s.native))
for name in [n for n in r['new_occurrences'] if r['specs'][n]['role']=='rod']:
 wire=doc.getObject(name+'WirePath').Shape;rod=s.world(name);length=wire.Length;missing=[];curvature=[]
 for e in wire.Edges:
  for i in range(1,20):
   u=e.FirstParameter+(e.LastParameter-e.FirstParameter)*i/20;point=e.valueAt(u);tangent=e.tangentAt(u);curvature.append(e.curvatureAt(u))
   missing.append(vol(Part.makeCylinder(9.49,.02,point-tangent*.01,tangent).cut(rod)))
 ck(name+' continuous full-diameter stock through every route span',max(missing)<1e-5 and max(curvature)*9.525<1,minimum_sampled_bend_radius_mm=1/max(curvature),maximum_missing_mm3=max(missing))
 ck(name+' single complete source rod',len(wire.Wires)==1 and len(rod.Solids)==1 and abs(rod.Volume/(math.pi*9.525**2*length)-1)<.01,length_mm=length)
 for j in [v for v in d['joints'].values() if v['rod']==name]:
  center=V(*j['center_world_mm']);axis=V(*j['rod_axis_world']);point=center+axis*25.4
  ck(name+j['receiver']+' centerline reaches actual socket',wire.distToShape(Part.Vertex(point))[0]<1e-7)
App.closeDocument(doc.Name)
result=dict(passed=all(v['passed'] for v in checks),checks=checks,native_sha256=sha(s.native),manifest_sha256=sha(s.folder/'isolated/manifest.json'),checker_sha256=sha(Path(__file__)),scope='Complete saved routes, inherited material/frames, eight physical joints and receiver stock; prospective front forks are nonphysical witnesses. Historical geometry remains approximate.')
write(out/'independent_checks.json',result);print('FINISHED',len(checks),'checks',sum(not v['passed'] for v in checks),'failed',flush=True)
assert result['passed']
