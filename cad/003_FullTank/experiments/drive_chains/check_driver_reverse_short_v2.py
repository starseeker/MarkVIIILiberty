"""Independently check saved reverse-body dimensions and complete short-rod joints."""
import argparse,math,json
from control_rebuild_io_v2 import *
from lib.camera_review import validate_native_bindings
V=App.Vector;X=V(1,0,0);Y=V(0,1,0)
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args()
s=Saved(a.candidate);r=s.report;d=r['details'];c=d['controls'];parent=Saved((ROOT/r['parent_native']).parent)
out=s.folder/'checks04';out.mkdir(exist_ok=False);checks=[]
validate_native_bindings(dict(native_file=str(s.native),render_occurrences=list(s.rows),landmarks=[]),s.manifest)
assert all(sha(ROOT/f)==h for f,h in r['input_hashes'].items())
def ck(name,ok,**kw):
    checks.append(dict(name=name,passed=bool(ok),**kw));write(out/'progress.json',checks)
    if not ok:print('FAIL',name,kw,flush=True)
def vol(q):return sum(abs(v.Volume) for v in q.Solids)
def same(q,t):return vol(q.cut(t))<1e-5 and vol(t.cut(q))<1e-5 and not q.cut(t,1e-4).Faces and not t.cut(q,1e-4).Faces
def cyl(q,p,axis,radius):return [f for f in q.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-radius)<1e-6 and f.Surface.Axis.cross(axis).Length<1e-7 and (f.Surface.Center-p).cross(axis).Length<1e-6]
def planes(q,p,axis):return [f for f in q.Faces if isinstance(f.Surface,Part.Plane) and f.Surface.Axis.cross(axis).Length<1e-7 and abs((f.CenterOfMass-p).dot(axis))<1e-6]
def bearing(q,t,p,axis):return sum(f.common(g).Area for f in planes(q,p,axis) for g in planes(t,p,axis))
def moved(q,v):t=q.copy();t.translate(v);return t
ck('Ten additions, one new definition, three exact receivers',len(r['new_occurrences'])==10 and len(r['new_definitions'])==1 and not r['changed_definitions'] and len(s.rows)==13)
for key in s.manifest['definitions']:
    q=s.definition(key);ck(key+' canonical closed solid',q.Placement.isIdentity() and q.isValid() and len(q.Solids)==1 and q.Solids[0].isClosed() and q.getTolerance(1)<=1e-4)
    if key in parent.manifest['definitions']:ck(key+' complete inherited material',same(q,parent.definition(key)))
for name,row in s.rows.items():
    ck(name+' actual saved frame',max(abs(a-b) for a,b in zip(row['frame'],r['specs'][name]['frame']))<1e-7)
    if name in parent.rows:ck(name+' retained frame and identity',row['definition']==parent.rows[name]['definition'] and max(abs(a-b) for a,b in zip(row['frame'],parent.rows[name]['frame']))<1e-7)
def props(path,keys):
    doc=App.openDocument(str(path))
    try:return {key:{k:getattr(doc.getObject(key),k) for k in doc.getObject(key).PropertiesList if doc.getObject(key).getGroupOfProperty(k)=='Reconstruction'} for key in keys}
    finally:App.closeDocument(doc.Name)
keys=set(s.manifest['definitions']) & set(parent.manifest['definitions']);before=props(parent.native,keys);after=props(s.native,keys)
for key in keys:
    changes={k for k in set(before[key])|set(after[key]) if before[key].get(k)!=after[key].get(k)}
    ck(key+' full source/approximation metadata preservation',changes==set(d['metadata_revisions'].get(key,[])),revised_fields=sorted(changes))
rodkey=s.rows['DriverReverseShortRod']['definition'];ck('Third M789A uses existing shared definition and source row',rodkey=='Def_DriverFrontShortRod_M789A' and json.loads(s.manifest['definitions'][rodkey]['properties']['SourceRecords'])==['SNL:194:028'])
lever=s.world('DriverReverseOperatingLever');pivot=V(*d['pivot_world_mm']);front=V(*d['front_pin_world_mm']);rear=V(*d['rear_pin_world_mm']);shaft=s.world('DriverMainShaft');thick=c['blade_stock_mm']
fs=cyl(lever,pivot,Y,19.1619)
ck('Actual oil-fed journal, full bore and full hub span on retained shaft',len(fs)==1 and abs(max((v.Point-pivot).y for v in fs[0].Vertexes)-min((v.Point-pivot).y for v in fs[0].Vertexes)-24)<1e-6 and vol(Part.makeCylinder(19.1619,24,pivot-Y*12,Y).common(lever))<1e-5 and vol(Part.makeCylinder(19.0119,24,pivot-Y*12,Y).cut(shaft))<1e-5 and vol(lever.common(shaft))<1e-5)
fs=cyl(lever,front,Y,6.5)
ck('Six-inch bell measured between actual journal and eye',len(fs)==1 and abs((fs[0].Surface.Center-pivot).cross(Y).Length-152.4)<1e-7 and abs(fs[0].Area-2*math.pi*6.5*thick)<1e-5)
eye=Part.makeCylinder(17,thick,front-Y*thick/2,Y).cut(Part.makeCylinder(6.5,thick+2,front-Y*(thick/2+1),Y))
ck('Complete bell-eye stock',vol(eye.cut(lever))<1e-5)
spheres=[f.Surface for f in lever.Faces if isinstance(f.Surface,Part.Sphere) and abs(f.Surface.Radius-10.5)<1e-7]
ck('Rounded hand end present',len(spheres)==1)
if spheres:
    center=spheres[0].Center;radial=center-pivot;radial.normalize();tip=center+radial*10.5
    ck('27.968-inch hand reach from saved sphere and actual end',abs((center-pivot).Length+10.5-27.968*25.4)<1e-7 and lever.distToShape(Part.Vertex(tip))[0]<1e-7,reach_mm=(center-pivot).Length+10.5)
    ck('Full rounded grip end material',vol(Part.makeSphere(.4,tip-radial*.8).cut(lever))<1e-6)
    ck('Shortened grip negative control rejected',abs((center-pivot).Length+9.5-27.968*25.4)>0.9)
rod=s.world('DriverReverseShortRod');axis=front-rear;span=axis.Length;axis.normalize();start=rear+axis*25.4
core=Part.makeCylinder(9.525,269.875,start,axis)
ck('Full printed M789A stock and diameter',same(rod,core))
ck('Pin-span closure preserves full rod and fork offsets',abs(span-269.875-50.8)<1e-7)
ck('Shortened rod negative control rejected',not same(Part.makeCylinder(9.525,268.875,start,axis),rod))
for joint in d['joints']:
    stem=joint['stem'];receiver=s.world(joint['receiver']);fork=s.world(stem+'Fork');pin=s.world(stem+'Pin');cotter=s.world(stem+'Cotter');nut=s.world(stem+'Nut')
    frame=pose(s.rows[stem+'Fork']['frame']);point=frame.Base;rodaxis=frame.Rotation.multVec(X);pinaxis=frame.Rotation.multVec(Y);fs=cyl(receiver,point,pinaxis,6.5)
    ck(stem+' actual receiving bore and M568C pin',len(fs)==1 and bool(cyl(pin,point,pinaxis,6.35)) and s.manifest['definitions'][s.rows[stem+'Pin']['definition']]['properties']['SourcePartMark']=='M568C')
    if fs:
        vals=[(v.Point-point).dot(pinaxis) for v in fs[0].Vertexes];lo,hi=min(vals),max(vals)
        ck(stem+' complete pin spans receiver',vol(Part.makeCylinder(6.35,hi-lo,point+pinaxis*lo,pinaxis).cut(pin))<1e-5)
    for role in ['Fork','Pin','Cotter','Nut']:ck(stem+role+' complete inherited definition',s.rows[stem+role]['definition']==parent.rows['PortTrackBrakeJoint'+role]['definition'])
    face=point+rodaxis*44.45;area=bearing(fork,nut,face,rodaxis)
    ck(stem+' full nut/socket bearing',abs(area-math.pi*(12.7**2-9.625**2))<1e-5,bearing_mm2=area)
    ck(stem+' complete rod insertion and nut coverage',vol(Part.makeCylinder(9.525,38.1,face-rodaxis*19.05,rodaxis).cut(rod))<1e-4 and bool(cyl(fork,face,rodaxis,9.625)))
    ck(stem+' complete joint material clear',all(vol(q.common(t))<1e-5 for q,t in [(fork,receiver),(fork,pin),(fork,cotter),(pin,cotter),(nut,rod),(fork,rod),(pin,receiver),(nut,pin),(nut,cotter)]))
    ck(stem+' lifted nut loses seating',bearing(moved(nut,rodaxis*.2),fork,face,rodaxis)<1e-6)
    ck(stem+' displaced pin intersects receiver',vol(moved(pin,X*3).common(receiver))>1)
result=dict(passed=all(v['passed'] for v in checks),checks=checks,native_sha256=sha(s.native),manifest_sha256=sha(s.folder/'isolated/manifest.json'),checker_sha256=sha(Path(__file__)),scope='Saved reverse body and complete third short rod. Historical blade shape, complete reverse mechanism, motion and service remain unqualified.')
write(out/'independent_checks.json',result);print('Reverse short',len(checks),'checks; passed',result['passed'],flush=True);assert result['passed']
