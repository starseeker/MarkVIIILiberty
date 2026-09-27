"""Independent saved-material, receiving-stock and continuous-route checks."""
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
def volume(shape):return sum(abs(x.Volume) for x in shape.Solids)
def same(one,two):return volume(one.cut(two))<1e-5 and volume(two.cut(one))<1e-5 and not one.cut(two,1e-4).Faces and not two.cut(one,1e-4).Faces
def planes(shape,point,axis):return [f for f in shape.Faces if isinstance(f.Surface,Part.Plane) and f.Surface.Axis.cross(axis).Length<1e-7 and abs((f.CenterOfMass-point).dot(axis))<1e-6]
def seat(one,two,point,axis):return sum(f.common(g).Area for f in planes(one,point,axis) for g in planes(two,point,axis))
def cylinders(shape,center,axis,radius):return [f for f in shape.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-radius)<1e-6 and f.Surface.Axis.cross(axis).Length<1e-7 and (f.Surface.Center-center).cross(axis).Length<1e-6]
def translated(shape,v):q=shape.copy();q.translate(v);return q

ck('Twelve physical additions, three definitions, eight bounded definition revisions',len(r['new_occurrences'])==12 and len(r['new_definitions'])==3 and len(r['changed_definitions'])==8,new_occurrences=r['new_occurrences'],changed=r['changed_definitions'])
for key in s.manifest['definitions']:
    shape=s.definition(key);ck(key+' canonical valid closed solid',shape.Placement.isIdentity() and shape.isValid() and len(shape.Solids)==1 and shape.Solids[0].isClosed() and shape.getTolerance(1)<=1e-4)
    if key not in r['new_definitions']+r['changed_definitions']:ck(key+' inherited material preserved',same(shape,parent.definition(key)))
for n,row in s.rows.items():ck(n+' saved frame',max(abs(x-y) for x,y in zip(row['frame'],r['specs'][n]['frame']))<1e-7)
floor=s.world('hull_floor_7');ft=533.05
for hand in ['Left','Right']:
    bracket=s.world('ClutchSupport_'+hand+'Bracket');area=seat(bracket,floor,V(0,0,ft),Z)
    ck(hand+' cast foot bears on actual floor',area>1000 and volume(bracket.common(floor))<1e-5,bearing_mm2=area)
    ck(hand+' lift separates floor bearing',seat(translated(bracket,Z*.2),floor,V(0,0,ft),Z)<1e-6)
    old=parent.world('ClutchSupport_'+hand+'Bracket')
    for cx,cz in [(2614.9446420457634,662.6972938764704)]+([(2354.9446420457634,687.6972938764704)] if hand=='Left' else []):
        cy=185 if hand=='Left' else -185;center=V(cx,cy,cz);faces=cylinders(bracket,center,Y,19.15)
        ck(hand+str(cx)+' actual preserved shaft journal',len(faces)==1 and abs(faces[0].Area-2*math.pi*19.15*40)<1e-4)
    for i in range(1,5):
        name='ClutchSupport_'+hand+'Mount'+str(i);bolt=s.world(name);base=pose(s.rows[name]['frame']).Base
        diameter,length=(15.875,47.625) if hand=='Left' else (12.7,44.45)
        core=Part.makeCylinder(diameter/2,length,base)
        ck(name+' full source stock and floor-head seating',abs(base.z-527.05)<1e-6 and volume(core.cut(bolt))<1e-5 and seat(bolt,floor,base,Z)>100)
        ck(name+' true floor and boss bore',len(cylinders(floor,base,Z,diameter/2+.15))==1 and len(cylinders(bracket,base,Z,diameter/2+.15))==1)
        ck(name+' stock engages actual boss',volume(bracket.common(core))<1e-5 and volume(floor.common(core))<1e-5 and length-6>=2*diameter)
# The revised paired lever preserves every upper receiving/adjustment surface.
upper=Part.makeBox(1000,200,1000,V(-400,-100,-5))
for role in ['left','right']:
    key='Def_HighBrakeMechanism_lever_'+role
    ck(key+' upper mechanism material unchanged',same(s.definition(key).common(upper),parent.definition(key).common(upper)))
reg=read(H/'transmission_controls_study/channel_local_registration01.json');scale=reg['pixels_per_mm']
interfaces=read(H/'transmission_controls_study/redo01/intermediate02/report.json')['details']['receiving_interfaces']
doc=App.openDocument(str(s.native))
for side in ['Starboard','Port']:
    fork=s.world(side+'HighSpeedBrakeControlFork');pin=s.world(side+'HighSpeedBrakeControlPin');nut=s.world(side+'HighSpeedBrakeControlNut')
    frame=pose(s.rows[side+'HighSpeedBrakeControlFork']['frame']);center=frame.Base;axis=frame.Rotation.multVec(Y)
    expected=reg['diagnostic_picks']['high_speed_control_pin'];pixel=[reg['center_px'][0]-(center.x-reg['axis_world_mm'][0])*scale,reg['center_px'][1]-(center.z-reg['axis_world_mm'][2])*scale]
    ck(side+' rear eye uses unchanged source construction pick',math.dist(pixel,expected)<1e-7,pixel=pixel,independent_holdout=False)
    ck(side+' longer fork has real coaxial pin bores',len(cylinders(fork,center,axis,15.875/2+.15))==2 and volume(fork.common(pin))<1e-5)
    for role in ['Left','Right']:
        receiver=s.world(side+'HighSpeedBrakeLever'+role)
        ck(side+role+' rear receiver drilled through',len(cylinders(receiver,center,axis,8.0875))==1 and volume(receiver.common(pin))<1e-5)
    rod=s.world(side+'RearHighRod');guide=s.world(side+'HighSpringBracket');spring=s.world(side+'HighRodSpring')
    start=V(*d[side]['spring_rear_seat_world_mm']);end=start+X*d[side]['spring_length_mm']
    backarea=seat(spring,nut,start,X);frontarea=seat(spring,guide,end,X)
    ck(side+' continuous spring has two real ground bearing patches',backarea>.1 and frontarea>.1 and volume(spring.common(nut))<1e-5 and volume(spring.common(guide))<1e-5,rear_mm2=backarea,front_mm2=frontarea)
    ck(side+' shifting spring breaks one bearing and penetrates other seat',seat(translated(spring,X*.2),nut,start,X)<1e-7 and volume(translated(spring,X*.2).common(guide))>1e-5)
    ck(side+' guide has source rod clearance in real bored stock',len(cylinders(guide,end,X,d['controls']['guide_diameter']/2))==1 and volume(guide.common(rod))<1e-5 and guide.distToShape(rod)[0]>.2)
    for side_end,point,axis_x,insertion,receiver_name in [('Rear',center,X,19.05,side+'HighSpeedBrakeControlFork'),('Forward',V(*interfaces[side+'High']['rear_pin_world_mm']),-X,19.05,side+'HighIntermediateJointFork')]:
        face=61.9125 if side_end=='Rear' else 44.45
        core=Part.makeCylinder(9.525,insertion,point+axis_x*(face-insertion),axis_x)
        receiver=s.world(receiver_name)
        ck(side+side_end+' complete socket stock insertion',volume(core.cut(rod))<1e-4 and volume(receiver.common(core))<1e-5)
    target=V(*interfaces[side+'High']['rear_pin_world_mm']);receiver=s.world(side+'HighIntermediateRocker');fpin=s.world(side+'HighIntermediateJointPin')
    ck(side+' intermediate rocker real receiver bore',len(cylinders(receiver,target,Y,6.5))==1 and volume(receiver.common(fpin))<1e-5)
    wire=doc.getObject(side+'M575WirePath').Shape;length=wire.Length;curvatures=[];samples=[]
    for edge in wire.Edges:
        for i in range(1,20):
            u=edge.FirstParameter+(edge.LastParameter-edge.FirstParameter)*i/20
            point=edge.valueAt(u);tangent=edge.tangentAt(u);curvatures.append(edge.curvatureAt(u))
            witness=Part.makeCylinder(9.49,.02,point-tangent*.01,tangent)
            samples.append(volume(witness.cut(rod)))
    ck(side+' continuous rod stock at every route span',max(samples)<1e-5 and max(curvatures)*9.525<1,maximum_missing_witness_mm3=max(samples),minimum_sampled_bend_radius_mm=1/max(curvatures),centerline_length_mm=length)
    # Curvature and witness checks supplement, not replace, full native/STEP material comparison.
    ck(side+' single complete rod without artificial segment',len(rod.Solids)==1 and len(wire.Wires)==1 and rod.Volume>math.pi*9.525**2*length*.99 and rod.Volume<math.pi*9.525**2*length*1.01)
App.closeDocument(doc.Name)
result=dict(passed=all(x['passed'] for x in checks),native_sha256=sha(s.native),manifest_sha256=sha(s.folder/'isolated/manifest.json'),checker_sha256=sha(Path(__file__)),checks=checks,scope='Saved physical receivers, stock, spring seats and actual floor mount. Source topology/profile certainty remains separate.')
write(out/'independent_checks.json',result);print('FINISHED',len(checks),'checks',sum(not x['passed'] for x in checks),'failed',flush=True)
assert result['passed']
