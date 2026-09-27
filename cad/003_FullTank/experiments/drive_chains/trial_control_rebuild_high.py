"""Complete M575/M563 trial and explicitly estimated coupled receiver corrections."""
import argparse
from pathlib import Path
from control_rebuild_io_v2 import App,Part,H,ROOT,Saved,pose,trial,read,sha
V=App.Vector;X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--controls',type=Path,required=True)
a=p.parse_args();controls=read(a.controls);source=ROOT/controls['source_review'];assert sha(source)==controls['source_review_sha256'];assert all(sha(ROOT/f)==v for f,v in read(source)['source_hashes'].items());parent=Saved(H/'transmission_controls_study/redo01/intermediate_integrated01')
shapes={};props={};specs={};details={};changed=[];groups={};curves={}
def carry(name,frame=None):
    row=parent.rows[name];key=row['definition'];shapes[key]=parent.definition(key)
    props[key]=parent.manifest['definitions'][key]['properties']
    specs[name]=dict(definition=key,frame=list(frame.toMatrix().A) if frame else row['frame'],owner=row['owners'][-1],role='receiver')
    return pose(specs[name]['frame'])
# Rebuild support feet at the actual floor, leaving journals and source hardware fixed.
from clutch_support_parts import parts as support_parts
sc=read(H/'clutch_support_controls.json')['controls']
sr=read(H/'clutch_support_build/report.json');inh=sr['inherited_controls'];ft=sr['datums']['floor_top']
oldbase,_,_,_=support_parts(sc,parent.definition('Def_ClutchThrowout_shaft'),inh,ft,6)
dz=pose(parent.rows['ClutchSupport_LeftBracket']['frame']).Base.z-533.05
newbase,_,_,_=support_parts(sc,parent.definition('Def_ClutchThrowout_shaft'),inh,ft-dz,6)
for side in ['Left','Right']:
    n='ClutchSupport_'+side+'Bracket';carry(n);key=parent.rows[n]['definition'];base=newbase[side.lower()+'_bracket']
    base.translate(-Z*dz)
    if side=='Left':
        # Estimated arch casting: source journals remain fixed, source four cap
        # screws mount separated pads; the existing channel occupies the gap.
        extra=shapes[key].cut(oldbase['left_bracket'])
        rear_x=-327.45 # world2287.4946, ahead of neither channel nor guide stock
        floor=-dz;h=sc['main_z']-ft;ah=h+sc['aux_dz'];arch_z=610.0-pose(parent.rows[n]['frame']).Base.z
        base=Part.makeBox(40,110,14,V(rear_x-20,-55,floor)).fuse(Part.makeBox(160,110,14,V(-80,-55,floor)))
        # Rear vertical leg and cross-member sit above the control channel.
        base=base.fuse(Part.makeBox(32,12,arch_z+16-floor,V(rear_x-16,-6,floor)))
        base=base.fuse(Part.makeBox(-rear_x,12,16,V(rear_x,-6,arch_z)))
        for x,z,bottom in [(0,h,floor),(-260,ah,arch_z)]:
            pts=[V(x-22,-6,bottom),V(x+22,-6,bottom),V(x+22,-6,z),V(x-22,-6,z)]
            base=base.fuse(Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(Y*12)).fuse(Part.makeCylinder(31,40,V(x,-20,z),Y))
        for x in [55,rear_x]:
            for y in [-32,32]:
                base=base.fuse(Part.makeCylinder(20,48,V(x,y,floor)))
                base=base.cut(Part.makeCylinder(sc['left_cap_diameter']/2+sc['cap_hole_clearance'],sc['left_cap_length']-6+sc['blind_end_gap']+1,V(x,y,floor-1)))
        for x,z in [(0,h),(-260,ah)]:base=base.cut(Part.makeCylinder(sc['main_radius']+sc['journal_clearance'],42,V(x,-21,z),Y))
        extra=extra.cut(Part.makeBox(1000,1000,500,V(-500,-500,arch_z-500)))
        base=base.fuse(extra)
        bc=read(H/'clutch_brake_linkage_controls.json')['controls']
        for x in bc['mount_x']:
            base=base.fuse(Part.makeBox(30,32,16,V(x-sc['main_x']-15,-6,arch_z)))
    shapes[key]=base.removeSplitter();changed.append(key)
    for i in range(1,5):
        n='ClutchSupport_'+side+'Mount'+str(i);f=pose(parent.rows[n]['frame']);f.Base-=Z*dz
        if side=='Left' and i in [3,4]:f.Base.x+=rear_x+315
        carry(n,f)
carry('hull_floor_7')
floor_key=parent.rows['hull_floor_7']['definition'];fp=pose(parent.rows['hull_floor_7']['frame'])
# Restore only old mounting-hole material from the original floor; then bore the
# declared current cap axes. Other floor features remain unchanged.
sm=read(H/'transmission_brake_front_study/trial01/standard_context_manifest.json')
srow=next(x for x in sm['occurrences'] if x['name']=='hull_floor_7');src=sm['definitions'][srow['definition']]
stock=Part.Shape();stock.read(src['brep_path']);stock.Placement=pose(srow['frame'])
world=parent.world('hull_floor_7')
for side in ['Left','Right']:
    radius=sc[side.lower()+'_cap_diameter']/2+sc['cap_hole_clearance']
    for i in range(1,5):
        n='ClutchSupport_'+side+'Mount'+str(i);old=pose(parent.rows[n]['frame']).Base;old.z=526.05
        tool=Part.makeCylinder(radius+1e-5,8,old)
        world=world.fuse(stock.common(tool))
        now=pose(specs[n]['frame']).Base;now.z=526.05
        world=world.cut(Part.makeCylinder(radius,8,now))
world.Placement=fp.inverse().multiply(world.Placement);shapes[floor_key]=Part.makeCompound([world]);changed.append(floor_key)
details['floor_correction_mm']=dz
# Source pin pick is now a construction constraint, not an independent holdout.
reg=read(H/'transmission_controls_study/channel_local_registration01.json')
px=reg['diagnostic_picks']['high_speed_control_pin'];scale=reg['pixels_per_mm']
end=V((reg['center_px'][0]-px[0])/scale,0,(reg['center_px'][1]-px[1])/scale)
mc=read(H/'transmission_high_brake_mechanism_study/controls.json')['controls'];oldend=V(*mc['lever_end_center']);mc['lever_end_center']=list(end)
for i in [2,3]:
    old=V(mc['lever_rivet_centers_xz'][i][0],0,mc['lever_rivet_centers_xz'][i][1]);t=(old.z+7.5)/(oldend.z+7.5)
    new=old+(end-oldend)*t;mc['lever_rivet_centers_xz'][i]=[new.x,new.z]
from transmission_high_brake_mechanism_parts import parts as mechanism
ms,_,_=mechanism(mc,read(H/'transmission_high_brake_front_study/trial01/report.json'))
for side in ['Starboard','Port']:
    for member in ['Left','Right']:
        n=side+'HighSpeedBrakeLever'+member;carry(n);key=parent.rows[n]['definition'];shapes[key]=ms['lever_'+member.lower()];changed.append(key)
    origin=pose(parent.rows[side+'HighSpeedBrakeLeverLeft']['frame'])
    for i,(x,z) in enumerate(mc['lever_rivet_centers_xz'],1):carry(side+'HighSpeedBrakeLeverRivet'+str(i),origin.multiply(App.Placement(V(x,0,z),App.Rotation())))
from transmission_control_joint_parts import parts as joint_parts
jc=read(H/'transmission_controls_study/high_speed_joint_controls.json')['controls'];jc.update(fork_length=61.9125,throat_end=23.8125,ear_shoulder=32)
js,jd=joint_parts(jc,parent.definition('Def_ClutchBrake_rod_nut'))
from rear_high_spring_bracket_parts import parts as guides
gc=read(H/'transmission_controls_study/high_spring_controls04.json')['controls'];gc['bracket']['guide_diameter']=controls['guide_diameter'];gc['bracket']['guide_height']=reg['axis_world_mm'][2]+end.z-533.05
channelpose=pose(parent.rows['RearControlChannelStock']['frame'])
gs,_,_=guides(gc,parent.definition(parent.rows['RearControlChannelStock']['definition']),channelpose)
# Offset M4135 mounting estimate: keep the riveted rear-flange foot, set its
# bored tab aft on a raised return. Provides bend clearance before the clutch.
base=gs['bracket'].common(Part.makeBox(10,100,68,V(-1,-50,0)))
height=gc['bracket']['guide_height'];offset=38.1;stock=6.35
shelf=Part.makeBox(offset+stock,38.1,stock,V(-offset,-19.05,68-stock))
tab=Part.makeBox(stock,38.1,height-(68-stock),V(-offset,-19.05,68-stock)).fuse(Part.makeCylinder(19.05,stock,V(-offset,0,height),X))
tab=tab.cut(Part.makeCylinder(controls['guide_diameter']/2,stock+2,V(-offset-1,0,height),X))
gs['bracket']=base.fuse(shelf).fuse(tab).removeSplitter()

for side in ['Starboard','Port']:
    stem=side+'HighSpeedBrakeControl';old=pose(parent.rows[stem+'Fork']['frame'])
    old.Base=pose(parent.rows[side+'HighSpeedBrakeLeverLeft']['frame']).multVec(end)
    axis=old.Rotation.multVec(Y);frame=App.Placement(old.Base,App.Rotation(X,axis,X.cross(axis),'XYZ'))
    carry(stem+'Fork',frame);key=parent.rows[stem+'Fork']['definition'];shapes[key]=js['fork'];changed.append(key)
    # Preserve the already installed pin/cotter rotation around the same bore.
    carry(stem+'Pin',frame.multiply(pose(jd['local_frames']['pin'])));carry(stem+'Cotter',frame.multiply(pose(jd['local_frames']['cotter'])))
    oldnut=pose(parent.rows[stem+'Nut']['frame']);nutframe=frame.multiply(pose(jd['local_frames']['nut']))
    carry(stem+'Nut',nutframe)
    for label in ['HighSpringBracket','HighSpringRivet1','HighSpringRivet2']:
        f=pose(parent.rows[side+label]['frame'])
        if side=='Port':f.Base-=Y*50.8
        carry(side+label,f)
        if label=='HighSpringBracket':
            key=parent.rows[side+label]['definition'];shapes[key]=gs['bracket'];changed.append(key)
    rear=frame.Base+X*(61.9125-19.05);rodend=V(2285.7,frame.Base.y,frame.Base.z)
    key='Def_'+side+'HighRod_Redo'
    shapes[key]=Part.makeCylinder(9.525,rodend.x-rear.x,V(),X)
    props[key]=dict(SourcePartMark='NONPHYSICAL M575 route envelope',SourceRecords=[],Representation='analysis_only')
    specs[side+'RearHighRod']=dict(definition=key,frame=list(App.Placement(rear,App.Rotation()).toMatrix().A),owner='Envelopes',role='envelope')
    start=frame.Base+X*(61.9125+19.05);length=2279.35-start.x
    key='Def_HighRodSpring_Redo'
    from front_clutch_parts import spring
    sc=dict(spring_turns=14,spring_end_turns=1,spring_wire_radius=controls['spring_wire_radius'],spring_inside_radius=12.5,spring_rear_seat=0,spring_length=length,spring_transition_turns=1,spring_end_pitch=3.65,spring_end_grind_fraction=.6,spring_samples_per_turn=64)
    coil,spine,sd=spring(sc)
    if key in shapes:assert abs(shapes[key].Volume-coil.Volume)<1e-6
    shapes[key]=coil;curves[side+'M563']=spine
    props[key]=dict(SourcePartMark='M563',SourceRecords=['SNL:220'],Representation='reconstruction_trial')
    specs[side+'HighRodSpring']=dict(definition=key,frame=list(App.Placement(start,App.Rotation()).toMatrix().A),owner='Envelopes',role='envelope')
    details[side]=dict(fork_frame=list(frame.toMatrix().A),nut_frame=list(nutframe.toMatrix().A),spring_rear_seat_world_mm=list(start),spring_length_mm=length,spring_controls=sc,spring_details=sd)

# Complete M575 corridors with genuine smooth swept rods and real receiver joints.
interfaces=read(H/'transmission_controls_study/redo01/intermediate02/report.json')['details']['receiving_interfaces']
template=pose(parent.rows['PortTrackBrakeJointFork']['frame']);hardware={}
for role in ['Fork','Pin','Cotter','Nut']:
    row=parent.rows['PortTrackBrakeJoint'+role];k=row['definition'];shapes[k]=parent.definition(k);props[k]=parent.manifest['definitions'][k]['properties'];hardware[role]=(k,template.inverse().multiply(pose(row['frame'])))
for side,sign in [('Starboard',-1),('Port',1)]:
    name=side+'RearHighRod';key=specs[name]['definition'];start=pose(specs[name]['frame']).Base
    target=V(*interfaces[side+'High']['rear_pin_world_mm'])
    pts=[start,V(2285.7,sign*222.25,start.z),V(2340,sign*201,645),V(2380,sign*201,645),V(2465,sign*125,619),V(2730,sign*125,619),V(2890,sign*125,655),V(5770,sign*125,655),V(5850,sign*125,target.z),target-X*25.4]
    edges=[]
    for j,(a1,b1) in enumerate(zip(pts,pts[1:])):
        if j in [1,3,5,7]:
            cr=Part.BezierCurve();dx=(b1.x-a1.x)*(.45 if j==1 else 1/3);cr.setPoles([a1,a1+X*dx,b1-X*dx,b1]);edges.append(cr.toShape())
        else:edges.append(Part.makeLine(a1,b1))
    wire=Part.Wire(edges);profile=Part.Wire([Part.makeCircle(9.525,start,X)])
    rod=wire.makePipeShell([profile],True,False);rod.translate(-start)
    shapes[key]=Part.makeCompound([rod]);props[key].update(SourcePartMark='M575',SourceRecords=['SNL:195:007'],Representation='reconstruction_trial')
    curves[side+'M575']=wire
    details[side]['rod_points_world_mm']=[list(v) for v in pts]
    frame=App.Placement(target,App.Rotation(-X,Y,-Z,'XYZ'));carry(side+'HighIntermediateRocker')
    for role,(k,local) in hardware.items():specs[side+'HighIntermediateJoint'+role]=dict(definition=k,frame=list(frame.multiply(local).toMatrix().A),owner='Envelopes',role='joint')

channel=carry('RearControlChannelStock');key=parent.rows['RearControlChannelStock']['definition']
early=Saved(H/'transmission_controls_study/fulcrum_integrated01')
stock=early.world('RearControlChannelStock');world=parent.world('RearControlChannelStock')
fills=[];cuts=[]
for y in [254.0,292.1]:
    tool=Part.makeCylinder(6.5,8.35,V(2322.8,y,558.45),X)
    fills.append(stock.common(tool))
    cuts.append(Part.makeCylinder(6.5,8.35,V(2322.8,y-50.8,558.45),X))
world=world.fuse(Part.makeCompound(fills)).cut(Part.makeCompound(cuts))
world.Placement=channel.inverse().multiply(world.Placement)

# World BRep is translated into the original definition frame without dropping placement.
local=world.copy();matrix=local.Placement.toMatrix();local.Placement=App.Placement()
shapes[key]=Part.makeCompound([world]);changed.append(key)
details.update(scope='Complete rear high controls, ground spring seats and coupled receiver corrections; qualification pending.',controls=controls,source_review=read(source),rear_pin_local_mm=list(end),lever_controls=mc,fork_controls=jc,guide_controls=gc)
groups['RearHighControls']=dict(owner='Root',frame=list(App.Placement().toMatrix().A))
for side in ['Starboard','Port']:
    owner=side+'RearHighControl';groups[owner]=dict(owner='RearHighControls',frame=list(App.Placement().toMatrix().A))
    for suffix in ['RearHighRod','HighRodSpring']:
        specs[side+suffix].update(owner=owner,role='rod' if 'RodSpring' not in suffix else 'spring')
    joint=side+'HighIntermediateJoint';groups[joint]=dict(owner=owner,frame=details[side]['fork_frame'])
    for role in ['Fork','Pin','Cotter','Nut']:
        specs[joint+role]['owner']=joint
        if role=='Nut':specs[joint+role]['source_records']=['SNL:195:008']
for key in sorted(set(changed)):
    props[key]=dict(props[key],ReconstructionStatus='Revised explicit approximation; see high_source_review01.json',ParameterUpdate='Regenerate trial_control_rebuild_high.py')
for side in ['Starboard','Port']:specs[side+'HighSpeedBrakeControlNut']['source_records']=['SNL:195:008']
inputs=[Path(__file__),H/'control_rebuild_io_v2.py',a.controls,source,parent.folder/'report.json',parent.folder/'qualification.json',parent.folder/'isolated/manifest.json',early.folder/'isolated/manifest.json']
import sys
inputs+=sorted({Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).resolve().parent==H and str(m.__file__).endswith('.py')})
inputs += [H/f for f in ['clutch_support_controls.json','clutch_support_build/report.json','clutch_brake_linkage_controls.json','transmission_high_brake_mechanism_study/controls.json','transmission_high_brake_front_study/trial01/report.json','transmission_controls_study/high_speed_joint_controls.json','transmission_controls_study/high_spring_controls04.json','transmission_controls_study/channel_local_registration01.json','transmission_controls_study/redo01/intermediate02/report.json','transmission_brake_front_study/trial01/standard_context_manifest.json']]
trial(a.output,parent,shapes,specs,props,details,inputs,changed_definitions=sorted(set(changed)),curves=curves,assembly_groups=groups)
print('Saved complete high-control trial; qualification pending.',flush=True)
