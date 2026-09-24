"""Verify saved track-rod joints against actual receiver material and full context."""
import argparse,itertools,sys
from pathlib import Path
H=Path(__file__).resolve().parent;STAGE=H.parents[1];ROOT=H.parents[3];sys.path.insert(0,str(STAGE))
import FreeCAD as App
import Part
import numpy as np
from lib.evidence import read,write,sha
from lib.camera_review import validate_native_bindings
V=App.Vector;X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve()
r=read(out/'report.json');native=out/r['native_file'];assert sha(native)==r['native_sha256']
parent=(ROOT/r['parent_native']).parent;m=read(parent/'isolated/manifest.json');pr=read(parent/'report.json');pnative=parent/pr['native_file']
assert sha(pnative)==r['parent_native_sha256']==m['native_sha256'];assert sha(parent/'qualification.json')==r['input_hashes'][str((parent/'qualification.json').relative_to(ROOT))]
rows={v['name']:v for v in m['occurrences']};cache={};checks=[]
def ck(name,passed,**kw):checks.append(dict(name=name,passed=bool(passed),**kw))
def definition(key):
    if key not in cache:
        d=m['definitions'][key];assert sha(d['brep_path'])==d['brep_sha256'];s=Part.Shape();s.read(d['brep_path']);cache[key]=s
    return cache[key].copy()
def prior(name):
    v=rows[name];s=definition(v['definition']);s.Placement=App.Placement(App.Matrix(*v['frame']));return s
def empty(s):return not s.Faces and not s.Solids
def planes(s,q,n):return [f for f in s.Faces if isinstance(f.Surface,Part.Plane) and f.normalAt(0,0).cross(n).Length<1e-7 and abs((f.CenterOfMass-q).dot(n))<1e-6]
def bearing(a,b,q,n):return sum(f.common(g).Area for f in planes(a,q,n) for g in planes(b,q,n))
selected=[v['receiver'] for v in r['joints'].values()]
validate_native_bindings(dict(native_file=str(pnative),render_occurrences=selected,landmarks=[]),m)
doc=App.openDocument(str(native));definitions={};shapes={};frames={}
try:
    ck('Four definitions and four four-component linked assemblies',len(doc.Definitions.Group)==4 and len(doc.Root.Group)==4 and all(len(g.Group)==4 for g in doc.Root.Group))
    for body in doc.Definitions.Group:
        s=body.Shape.copy();key=body.Name.removeprefix('Def_TrackJoint_');definitions[key]=s
        ck(key+' saved closed identity-frame solid',s.isValid() and len(s.Solids)==1 and s.Solids[0].isClosed() and s.Placement.isIdentity() and body.Placement.isIdentity() and s.getTolerance(1)<=1e-4,tolerance_mm=s.getTolerance(1))
    for name,spec in r['specs'].items():
        link=doc.getObject(name);owner=doc.getObject(spec['owner']);pose=owner.getGlobalPlacement().multiply(link.LinkPlacement)
        ck(name+' native target and composed frame',link.TypeId=='App::Link' and link.LinkedObject.Name=='Def_TrackJoint_'+spec['role'] and link.Scale==1 and tuple(link.ScaleVector)==(1.,1.,1.) and max(abs(x-y) for x,y in zip(pose.toMatrix().A,spec['frame']))<1e-7)
        s=link.LinkedObject.Shape.copy();s.Placement=pose;shapes[name]=s;frames[name]=pose
finally:App.closeDocument(doc.Name)
c=r['controls'];fork=definitions['fork'];pin=definitions['pin'];nut=definitions['nut'];oldnut=definition(r['shared_definitions']['nut'])
ck('Shared nut complete material retained',empty(nut.cut(oldnut)) and empty(oldnut.cut(nut)))
ck('Cotter preserves listed25.4mm under-eye leg length',abs(r['details']['cotter']['total_leg_centerline_mm']-25.4)<1e-7)
for hand, joint in r['joints'].items():
    base=frames[hand+'Fork'];inv=base.inverse()
    def local(name):
        s=shapes[hand+name].copy();s.Placement=inv.multiply(s.Placement);return s
    pin=local('Pin');cotter=local('Cotter');nut=local('Nut');eye=[]
    s=prior(joint['receiver']);s.Placement=inv.multiply(s.Placement);eye.append(s)
    eye=Part.makeCompound(eye)
    cylinders=[f for f in eye.Faces if isinstance(f.Surface,Part.Cylinder) and f.Surface.Axis.cross(Y).Length<1e-7 and f.Surface.Center.cross(Y).Length<1e-6 and abs(f.Surface.Radius-6.5)<1e-6]
    ck(hand+' saved eye and pin coaxial',len(cylinders)==1 and all(abs(f.Surface.Radius-6.5)<1e-6 for f in cylinders),faces=len(cylinders))
    forkbores=[f for f in fork.Faces if isinstance(f.Surface,Part.Cylinder) and f.Surface.Axis.cross(Y).Length<1e-7 and f.Surface.Center.cross(Y).Length<1e-6 and abs(f.Surface.Radius-6.5)<1e-6]
    ck(hand+' two actual fork bearing ears',len(forkbores)==2 and all(abs(f.Surface.Radius-6.5)<1e-6 for f in forkbores),faces=len(forkbores))
    low=min(v.Point.y for f in forkbores for v in f.Vertexes);high=max(v.Point.y for f in forkbores for v in f.Vertexes)
    ck(hand+' full fork axial pin engagement',empty(Part.makeCylinder(c['pin_diameter']/2-.01,high-low-.02,V(0,low+.01,0),Y).cut(pin)))
    measured=pin.BoundBox.YMax-low
    ck(hand+' source39.6875mm underhead pin hypothesis',abs(measured-c['pin_length'])<1e-6,measured_mm=measured)
    contact=bearing(fork,pin,V(0,low,0),Y);ck(hand+' pin head bears on fork',contact>150,area_mm2=contact)
    moved=pin.copy();moved.translate(Y*.2);ck(hand+' pin head prevents forward withdrawal',moved.common(fork).Volume>1)
    moved=cotter.copy();moved.translate(-Y*3);ck(hand+' spread cotter prevents reverse withdrawal',moved.common(fork).Volume>1e-3)
    moved=cotter.copy();moved.translate(Y*3);ck(hand+' displaced cotter no longer fits cross bore',moved.common(pin).Volume>1e-3)
    face=r['details']['rod_seat_x_mm'];threadfaces=[f for f in fork.Faces if isinstance(f.Surface,Part.Cylinder) and f.Surface.Axis.cross(X).Length<1e-7 and abs(f.Surface.Radius-9.625)<1e-6]
    intervals=[(min(v.Point.x for v in f.Vertexes),max(v.Point.x for v in f.Vertexes)) for f in threadfaces]
    engagement=sum(b-a for a,b in intervals);ck(hand+' actual threaded socket has one diameter engagement',engagement>=c['minimum_thread_engagement']-1e-6,measured_mm=engagement,intervals_mm=intervals)
    start=face-min(engagement,c['minimum_thread_engagement'])+.01
    witness=Part.makeCylinder(19.05/2,face+c['shared_nut_height']-start,V(start,0,0),X)
    ck(hand+' nominal future rod clears complete socket and nut',empty(witness.common(fork)) and empty(witness.common(nut)))
    wall=Part.makeCylinder(c['socket_radius']-.01,face-c['throat_end']-.02,V(c['throat_end']+.01,0,0),X).cut(Part.makeCylinder(9.635,face-c['throat_end']+2,V(c['throat_end']-1,0,0),X))
    ck(hand+' socket surrounds thread passage with retained material',empty(wall.cut(fork)))
    contact=bearing(fork,nut,V(face,0,0),X);ck(hand+' plain nut bears on socket end',contact>200,area_mm2=contact)
    moved=nut.copy();moved.translate(X*.1);ck(hand+' lifted nut loses seating',bearing(fork,moved,V(face,0,0),X)<1e-5)
pairs=[]
def compare(n,s,k,t):
    common=s.common(t);volume=sum(abs(v.Volume) for v in common.Solids);valid=common.isNull() or common.isValid()
    pairs.append(dict(first=n,second=k,common_mm3=volume,passed=valid and volume<1e-5))
for hand, joint in r['joints'].items():
    for role in ['Fork','Pin','Cotter','Nut']:
        name=hand+role;compare(name,shapes[name],joint['receiver'],prior(joint['receiver']))
for one,two in itertools.combinations(shapes,2):
    if shapes[one].BoundBox.intersect(shapes[two].BoundBox):compare(one,shapes[one],two,shapes[two])
ck('All proposed parts clear their own receiver and each other',all(v['passed'] for v in pairs),pairs=len(pairs),failed=[v for v in pairs if not v['passed']])
write(out/'independent_checks.json',dict(passed=all(v['passed'] for v in checks),checks=checks,pairs=pairs,native_sha256=sha(native),parent_native_sha256=sha(pnative),checker_sha256=sha(Path(__file__)),scope='Saved link/frame/material, receiving pin and ear axes, actual head/nut seating, selected retention negative controls, socket engagement and own receiver and local interference; whole development/standard context checked separately. Rod is a nonphysical witness; full rod routes and service remain open.'))
print(len(checks),'joint checks;',len(pairs),'material pairs; passed',all(v['passed'] for v in checks),flush=True)
for row in checks:
    if not row['passed']:print(row,flush=True)
assert all(v['passed'] for v in checks)
