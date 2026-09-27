"""Saved-material checks for M641 support, M640 journals and complete M578 rods."""
import argparse,math
from pathlib import Path
from control_rebuild_io_v2 import App,Part,H,ROOT,Saved,pose,read,write,sha
from lib.camera_review import validate_native_bindings
V=App.Vector;X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True)
a=p.parse_args();current=Saved(a.candidate);r=current.report;c=r['details']['controls']
parent=Saved((ROOT/r['parent_native']).parent);out=current.folder/'checks02';out.mkdir(exist_ok=False)
assert all(sha(ROOT/f)==h for f,h in r['input_hashes'].items())
validate_native_bindings(dict(native_file=str(current.native),render_occurrences=list(current.rows),landmarks=[]),current.manifest)
checks=[]
def ck(name,passed,**detail):
    checks.append(dict(name=name,passed=bool(passed),**detail));write(out/'progress.json',checks)
def material(s):return sum(abs(v.Volume) for v in s.Solids)
def no_material(a,b):return material(a.common(b))<1e-5
def same(a,b):return material(a.cut(b))<1e-5 and material(b.cut(a))<1e-5 and not a.cut(b,1e-4).Faces and not b.cut(a,1e-4).Faces
def moved(s,v):
    t=s.copy();t.translate(v);return t
def cylinders(s,center,axis,radius):
    return [f for f in s.Faces if isinstance(f.Surface,Part.Cylinder)
            and abs(f.Surface.Radius-radius)<1e-6 and f.Surface.Axis.cross(axis).Length<1e-7
            and (f.Surface.Center-center).cross(axis).Length<1e-6]
def axial_span(f,center,axis):
    ps=[(v.Point-center).dot(axis) for v in f.Vertexes];return min(ps),max(ps)
def planes(s,point,axis):
    return [f for f in s.Faces if isinstance(f.Surface,Part.Plane) and
            f.Surface.Axis.cross(axis).Length<1e-7 and abs((f.CenterOfMass-point).dot(axis))<1e-6]
def bearing(a,b,point,axis):
    return sum(x.common(y).Area for x in planes(a,point,axis) for y in planes(b,point,axis))

ck('Thirty additions, two retained lever receivers and one revised floor',
   len(current.rows)==33 and len(r['new_occurrences'])==30 and len(r['new_definitions'])==5
   and r['changed_definitions']==[parent.rows['hull_floor_6']['definition']])
for key in current.manifest['definitions']:
    s=current.definition(key)
    ck(key+' canonical complete solid',s.Placement.isIdentity() and s.isValid() and len(s.Solids)==1
       and s.Solids[0].isClosed() and s.getTolerance(1)<=1e-4)
    if key in parent.manifest['definitions'] and key not in r['changed_definitions']:
        ck(key+' complete inherited material retained',same(s,parent.definition(key)))
for n,row in current.rows.items():
    ck(n+' composed frame matches specification',max(abs(x-y) for x,y in zip(row['frame'],r['specs'][n]['frame']))<1e-7)

floor=current.world('hull_floor_6');oldfloor=parent.world('hull_floor_6');tools=[]
for m in r['details']['mounts']:
    base=V(*m['center_world_mm']);radius=c['rivet']['hole_diameter']/2
    tool=Part.makeCylinder(radius,c['floor_stock']+2,base-Z);tools.append(tool)
    faces=cylinders(floor,base,Z,radius)
    spans=[axial_span(f,base,Z) for f in faces]
    ck(m['side']+' floor bore '+str(m['index']),len(faces)==1 and abs(spans[0][0])<1e-6
       and abs(spans[0][1]-c['floor_stock'])<1e-6 and no_material(floor,tool),spans_mm=spans)
tool=Part.makeCompound(tools);expected=oldfloor.cut(tool)
ck('Floor receiver changed only by six declared clearance holes',same(floor,expected)
   and material(floor.cut(oldfloor))<1e-5
   and abs((oldfloor.Volume-floor.Volume)-6*math.pi*(c['rivet']['hole_diameter']/2)**2*c['floor_stock'])<1e-5)

for side in ['Starboard','Port']:
    d=r['details'][side];frame=pose(d['support_frame']);origin=frame.Base
    axis=frame.Rotation.multVec(Y);pivot=frame.multVec(V(0,0,c['pivot_height']))
    bracket=current.world(side+'CenterFootBracket');rocker=current.world(side+'CenterFootRocker')
    keeper=current.world(side+'CenterFootKeeper')
    contact=bearing(bracket,floor,origin,Z)
    ck(side+' complete mounted foot contact',contact>2000 and no_material(bracket,floor)
       and bearing(moved(bracket,Z*.25),floor,origin,Z)<1e-6,bearing_area_mm2=contact)
    faces=cylinders(rocker,pivot,axis,c['journal_bore']/2)
    ck(side+' actual full-width journal bore',len(faces)==1 and
       abs(axial_span(faces[0],pivot,axis)[1]-axial_span(faces[0],pivot,axis)[0]-c['hub_width'])<1e-6)
    core=Part.makeCylinder(c['journal_diameter']/2,c['hub_width'],pivot-axis*c['hub_width']/2,axis)
    ck(side+' journal stock spans entire rocker bearing',material(core.cut(bracket))<1e-5 and no_material(core,rocker))
    shoulder=pivot-axis*c['hub_width']/2
    ck(side+' real shoulder stop and clearance',bearing(bracket,rocker,shoulder,axis)>800
       and no_material(bracket,rocker) and material(moved(rocker,-axis*.2).common(bracket))>1)
    hole_center=frame.multVec(V(0,c['keeper_station_y'],c['pivot_height']))
    hole=Part.makeCylinder(c['keeper_hole_diameter']/2,c['journal_diameter']+2,hole_center-Z*(c['journal_diameter']/2+1),Z)
    ck(side+' actual keeper hole and retained rocker',len(cylinders(bracket,hole_center,Z,c['keeper_hole_diameter']/2))==1
       and no_material(bracket,hole) and no_material(bracket,keeper) and no_material(rocker,keeper)
       and material(moved(rocker,axis*2).common(keeper))>1e-5)
    spacing=c['keeper']['cotter_center_spacing'];wire=(c['keeper']['cotter_diameter']-spacing)/2
    for sign in [-1,1]:
        center=hole_center+frame.Rotation.multVec(X)*(sign*spacing/2)
        leg=Part.makeCylinder(wire,c['journal_diameter'],center-Z*c['journal_diameter']/2,Z)
        ck(side+' keeper leg '+str(sign)+' continuous through shaft',material(leg.cut(keeper))<1e-5)
    for sign in [-1,1]:
        center=pivot+Z*(sign*c['arm_radius']);bore=Part.makeCylinder(c['eye_bore']/2,c['eye_width']+2,center-axis*(c['eye_width']/2+1),axis)
        faces=cylinders(rocker,center,axis,c['eye_bore']/2)
        ck(side+' rocker eye '+str(sign)+' cut through all web unions',len(faces)==1 and no_material(rocker,bore)
           and abs(axial_span(faces[0],center,axis)[1]-axial_span(faces[0],center,axis)[0]-c['eye_width'])<1e-6)
    for m in [v for v in r['details']['mounts'] if v['side']==side]:
        base=V(*m['center_world_mm']);name=side+'CenterFootRivet'+str(m['index']);riv=current.world(name)
        grip=c['floor_stock']+c['base_stock'];top=base+Z*grip
        shaft=Part.makeCylinder(c['rivet']['diameter']/2,grip,base,Z)
        a0=bearing(riv,floor,base,Z);a1=bearing(riv,bracket,top,Z)
        ck(name+' real shank/grip and two bearing faces',material(shaft.cut(riv))<1e-5 and
           no_material(riv,floor) and no_material(riv,bracket) and a0>200 and a1>350,
           floor_bearing_mm2=a0,bracket_bearing_mm2=a1,grip_mm=grip)
        ck(name+' lifted negative loses bearing',bearing(moved(riv,Z*.2),floor,base,Z)<1e-6)
    rod=current.world(side+'RearFootRod');start=V(*d['rear_pin_world_mm'])+X*(44.45-c['rod_insertion'])
    expected=Part.makeCylinder(c['rod_diameter']/2,d['rod_length_mm'],start,X)
    ck(side+' M578 complete straight core',same(rod,expected) and
       abs(rod.Volume-math.pi*(c['rod_diameter']/2)**2*d['rod_length_mm'])<1e-5)

for stem,j in r['details']['joints'].items():
    center=V(*j['center_world_mm']);axis=V(*j['pin_axis_world']);rod_axis=V(*j['rod_axis_world'])
    receiver=current.world(j['receiver']);fork=current.world(stem+'Fork');pin=current.world(stem+'Pin')
    cotter=current.world(stem+'Cotter');nut=current.world(stem+'Nut');rod=current.world(j['rod'])
    faces=cylinders(receiver,center,axis,6.5)
    ck(stem+' actual receiving eye and M568C pin',len(faces)==1 and
       current.manifest['definitions'][current.rows[stem+'Pin']['definition']]['properties']['SourcePartMark']=='M568C'
       and bool(cylinders(pin,center,axis,6.35)))
    span=axial_span(faces[0],center,axis)
    witness=Part.makeCylinder(6.35,span[1]-span[0],center+axis*span[0],axis)
    ck(stem+' pin covers full receiver bearing',material(witness.cut(pin))<1e-5 and no_material(pin,receiver))
    ck(stem+' full mating material clearance',all(no_material(a,b) for a,b in
       [(fork,receiver),(fork,pin),(fork,cotter),(pin,cotter),(nut,rod),(fork,rod)]))
    seat=center+rod_axis*44.45
    area=bearing(fork,nut,seat,rod_axis);expected_area=math.pi*(12.7**2-9.625**2)
    ck(stem+' nut bears on complete socket annulus',abs(area-expected_area)<1e-5
       and bearing(moved(nut,rod_axis*.2),fork,seat,rod_axis)<1e-6,area_mm2=area,expected_area_mm2=expected_area)
    ck(stem+' complete nominal thread engagement and nut coverage',
       material(Part.makeCylinder(9.525,c['rod_insertion']+19.05,seat-rod_axis*c['rod_insertion'],rod_axis).cut(rod))<1e-5
       and c['rod_insertion']>=19.05 and c['rod_insertion']<22.225)
    ck(stem+' actual socket axis',bool(cylinders(fork,seat,rod_axis,9.625)))

result=dict(passed=all(v['passed'] for v in checks),checks=checks,native_sha256=sha(current.native),
 parent_native_sha256=sha(parent.native),checker_sha256=sha(Path(__file__)),
 scope='Actual saved receiver bores, complete journals/rod stock, retention, rivet grip/bearing and scoped floor revision. Separate all-context and STEP checks required.',
 historical_geometry_qualified=False,installation_qualified=False)
write(out/'independent_checks.json',result)
print(len(checks),'checks;',result['passed'],flush=True)
for v in checks:
    if not v['passed']:print(v,flush=True)
assert result['passed']
