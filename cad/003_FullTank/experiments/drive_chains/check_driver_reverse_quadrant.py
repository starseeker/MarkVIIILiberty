"""Independent saved-stock and receiving-material checks for mounted M779."""
import argparse,math,json
from control_rebuild_io_v2 import *
from lib.camera_review import validate_native_bindings
V=App.Vector;Y=V(0,1,0);Z=V(0,0,1)
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();s=Saved(a.candidate);r=s.report;d=r['details'];c=d['controls'];parent=Saved((ROOT/r['parent_native']).parent);seed=Saved(ROOT/d['reverse_seed']);out=s.folder/'checks01';out.mkdir(exist_ok=False);checks=[]
assert all(sha(ROOT/f)==v for f,v in r['input_hashes'].items());validate_native_bindings(dict(native_file=str(s.native),render_occurrences=list(s.rows),landmarks=[]),s.manifest)
def ck(name,ok,**kw):
    checks.append(dict(name=name,passed=bool(ok),**kw));write(out/'progress.json',checks)
    if not ok:print('FAIL',name,kw,flush=True)
def vol(q):return sum(abs(v.Volume) for v in q.Solids)
def same(q,t):return vol(q.cut(t))<1e-5 and vol(t.cut(q))<1e-5 and not q.cut(t,1e-4).Faces and not t.cut(q,1e-4).Faces
def cyl(q,p,axis,radius):return [f for f in q.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-radius)<1e-6 and f.Surface.Axis.cross(axis).Length<1e-7 and (f.Surface.Center-p).cross(axis).Length<1e-6]
def planes(q,p,axis):return [f for f in q.Faces if isinstance(f.Surface,Part.Plane) and f.Surface.Axis.cross(axis).Length<1e-7 and abs((f.CenterOfMass-p).dot(axis))<1e-6]
def bearing(q,t,p,axis):return sum(f.common(g).Area for f in planes(q,p,axis) for g in planes(t,p,axis))
def moved(q,v):q=q.copy();q.translate(v);return q
plate_name='DriverStarboardSupportPlate';plate_key=s.rows[plate_name]['definition'];plate=s.world(plate_name);oldplate=parent.world(plate_name)
ck('Nineteen additions versus accepted station; six new definitions and one revised plate',len(r['new_occurrences'])==19 and len(r['new_definitions'])==6 and r['changed_definitions']==[plate_key] and len(s.rows)==23)
for key in s.manifest['definitions']:
    q=s.definition(key);ck(key+' canonical closed solid',q.Placement.isIdentity() and q.isValid() and len(q.Solids)==1 and q.Solids[0].isClosed() and q.getTolerance(1)<=1e-4)
for name,row in s.rows.items():
    ck(name+' actual saved frame',max(abs(x-y) for x,y in zip(row['frame'],r['specs'][name]['frame']))<1e-7)
for name,row in seed.rows.items():
    other=s.rows[name];ck(name+' full qualified reverse seed material and placement',row['definition']==other['definition'] and max(abs(x-y) for x,y in zip(row['frame'],other['frame']))<1e-7 and same(seed.definition(row['definition']),s.definition(row['definition'])))
ck('Retained source checks bind unchanged reverse seed',sha(seed.native)==d['reverse_seed_native_sha256'] and read(seed.folder/'checks04/independent_checks.json')['passed'] and read(seed.folder/'exchange01/exchange_checks.json')['passed'])
def props(src,keys):
    doc=App.openDocument(str(src.native))
    try:return {key:{p:getattr(doc.getObject(key),p) for p in doc.getObject(key).PropertiesList if doc.getObject(key).getGroupOfProperty(p)=='Reconstruction'} for key in keys}
    finally:App.closeDocument(doc.Name)
actual=props(s,list(seed.manifest['definitions'])+[plate_key]);before=props(seed,seed.manifest['definitions'])
for key in before:ck(key+' complete seed source metadata',actual[key]==before[key])
before=props(parent,[plate_key])[plate_key];after=actual[plate_key];changes={k for k in set(before)|set(after) if before.get(k)!=after.get(k)}
ck('Support source metadata preserved with explicit revision/regeneration notes',changes=={'ReconstructionStatus','ParameterUpdate'})
ck('Support frame unchanged',s.rows[plate_name]['frame']==parent.rows[plate_name]['frame'])
main=V(*d['main_world_mm']);quad=s.world('DriverReverseQuadrant');cuts=[]
for point in d['mount_local_xz_mm']:
    p=main+V(*point);p.y=-c['support_inner_y_abs_mm']+1;cuts.append(Part.makeCylinder(4.9,c['support_stock_mm']+2,p,-Y))
expected=oldplate
for q in cuts:expected=expected.cut(q)
ck('Only two declared support bores removed',same(plate,expected) and vol(plate.cut(oldplate))<1e-5)
ck('Full support stock existed at both hole locations',abs(vol(oldplate.cut(plate))-2*math.pi*4.9**2*6.35)<1e-5)
ck('Old support with absent holes rejected',not same(plate,oldplate))
for index,joint in enumerate(d['joints']):
    stem=joint['stem'];x,z=joint['center_xz_world_mm'];ys=joint['seating_y_mm'];parts={role:s.world(stem+role) for role in ['Bolt','Nut','Lock','Distance']};p=V(x,ys['Bolt'],z);axis=-Y;bolt=parts['Bolt'];dist=parts['Distance'];lock=parts['Lock'];nut=parts['Nut']
    core=Part.makeCylinder(4.7625,57.15,p,axis)
    fs=cyl(bolt,p,axis,4.7625);extents=[(v.Point-p).dot(axis) for f in fs for v in f.Vertexes]
    ck(stem+' full source bolt diameter and under-head length',bool(fs) and abs(min(extents))<1e-7 and abs(max(extents)-57.15)<1e-7 and vol(core.cut(bolt))<1e-5)
    ck(stem+' source stock survives beyond actual full nut',ys['Bolt']-57.15 < ys['Nut']-c['nut_stock_mm']-1.5,protrusion_mm=ys['Nut']-c['nut_stock_mm']-(ys['Bolt']-57.15))
    ck(stem+' actual through bores in quadrant/spacer/support',all(bool(cyl(q,p,axis,4.9)) for q in [quad,dist,plate]))
    # Every intended planar seat must carry complete preserved physical material.
    headarea=bearing(quad,bolt,p,axis);expectedhead=math.sqrt(3)/2*c['hardware_af_mm']**2-math.pi*4.9**2
    ck(stem+' complete head bearing',abs(headarea-expectedhead)<1e-5,bearing_mm2=headarea)
    ringarea=math.pi*(c['spacer_outer_radius_mm']**2-4.9**2)
    a1=bearing(quad,dist,V(x,ys['Distance'],z),axis);a2=bearing(dist,plate,V(x,-c['support_inner_y_abs_mm'],z),axis)
    ck(stem+' both full distance-piece seats',abs(a1-ringarea)<1e-5 and abs(a2-ringarea)<1e-5,areas_mm2=[a1,a2])
    lockarea=sum(f.Area for f in planes(lock,V(x,ys['Lock'],z),axis));a3=bearing(lock,plate,V(x,ys['Lock'],z),axis);a4=bearing(lock,nut,V(x,ys['Nut'],z),axis)
    ck(stem+' full washer seat and substantial nut bearing',abs(a3-lockarea)<1e-5 and a4>170,washer_area_mm2=a3,nut_area_mm2=a4)
    ck(stem+' complete compressed washer and nut thickness',abs(lock.BoundBox.YLength-c['lock_stock_mm'])<1e-6 and abs(nut.BoundBox.YLength-c['nut_stock_mm'])<1e-6)
    ck(stem+' full distance-piece length and annular volume',abs(dist.BoundBox.YLength-joint['spacer_length_mm'])<1e-6 and abs(dist.Volume-ringarea*joint['spacer_length_mm'])<1e-5)
    allparts=[quad,plate,bolt,dist,lock,nut]
    ck(stem+' complete mounting materials do not intersect',all(vol(q.common(t))<1e-5 for i,q in enumerate(allparts) for t in allparts[i+1:]))
    ck(stem+' lifted bolt loses seating',bearing(moved(bolt,Y*.2),quad,p,axis)<1e-6)
    ck(stem+' displaced bolt enters support material',vol(moved(bolt,V(2,0,0)).common(plate))>1)
# Check real open notches and their material floors without using the builder.
for deg in c['notch_angles_degrees']:
    rad=math.radians(deg);axis=V(math.cos(rad),0,math.sin(rad));p=main+axis*(c['outer_radius_mm']-c['notch_depth_mm']+2);p.y=c['quadrant_inner_y_mm']-c['quadrant_stock_mm']/2
    ck('Detent '+str(deg)+' actual void and solid floor',vol(Part.makeSphere(1,p).common(quad))<1e-6 and vol(Part.makeSphere(1,p-axis*4).cut(quad))<1e-6)
result=dict(passed=all(v['passed'] for v in checks),checks=checks,native_sha256=sha(s.native),manifest_sha256=sha(s.folder/'isolated/manifest.json'),checker_sha256=sha(Path(__file__)),scope='Actual mounted quadrant, all source bolt stock, receiving material/seats and exact retained reverse seed. Complete latch, historical mounts and motion remain unqualified.')
write(out/'independent_checks.json',result);print(len(checks),'quadrant checks; passed',result['passed'],flush=True);assert result['passed']
