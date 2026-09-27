"""Unqualified M575/M563 axis study: actual joints plus explicitly named envelopes."""
import argparse
from pathlib import Path
from control_rebuild_io_v2 import App,Part,H,ROOT,Saved,pose,trial,read,sha
V=App.Vector;X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
a=p.parse_args();parent=Saved(H/'transmission_controls_study/redo01/intermediate_integrated01')
shapes={};props={};specs={};details={};changed=[]
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
        extra=shapes[key].cut(oldbase['left_bracket']);base=base.fuse(extra)
        bc=read(H/'clutch_brake_linkage_controls.json')['controls']
        for x in bc['mount_x']:
            base=base.fuse(Part.makeBox(30,12,dz+14,V(x-sc['main_x']-15,bc['mount_head_y']+14-sc['bracket_y'],-dz)))
    shapes[key]=base.removeSplitter();changed.append(key)
    for i in range(1,5):
        n='ClutchSupport_'+side+'Mount'+str(i);f=pose(parent.rows[n]['frame']);f.Base-=Z*dz;carry(n,f)
carry('hull_floor_7')
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
gc=read(H/'transmission_controls_study/high_spring_controls04.json')['controls'];gc['bracket']['guide_height']=reg['axis_world_mm'][2]+end.z-533.05
channelpose=pose(parent.rows['RearControlChannelStock']['frame'])
gs,_,_=guides(gc,parent.definition(parent.rows['RearControlChannelStock']['definition']),channelpose)
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
    rear=frame.Base+X*(61.9125-19.05);rodend=V(2324,frame.Base.y,frame.Base.z)
    key='Def_'+side+'HighRodAxisEnvelope'
    shapes[key]=Part.makeCylinder(9.525,rodend.x-rear.x,V(),X)
    props[key]=dict(SourcePartMark='NONPHYSICAL M575 route envelope',SourceRecords=[],Representation='analysis_only')
    specs[side+'HighRodAxisEnvelope']=dict(definition=key,frame=list(App.Placement(rear,App.Rotation()).toMatrix().A),owner='Envelopes',role='envelope')
    start=frame.Base+X*(61.9125+12.7);length=2317.45-start.x
    key='Def_'+side+'HighSpringAxisEnvelope'
    shapes[key]=Part.makeCylinder(16,length,V(),X).cut(Part.makeCylinder(12.5,length+2,-X,X))
    props[key]=dict(SourcePartMark='NONPHYSICAL M563 envelope',SourceRecords=[],Representation='analysis_only')
    specs[side+'HighSpringAxisEnvelope']=dict(definition=key,frame=list(App.Placement(start,App.Rotation()).toMatrix().A),owner='Envelopes',role='envelope')
    details[side]=dict(fork_frame=list(frame.toMatrix().A),nut_frame=list(nutframe.toMatrix().A),spring_rear_seat_world_mm=list(start),spring_length_mm=length)

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
details['scope']='Alignment/envelope study only; no springs or complete rods modeled or qualified.'
trial(a.output,parent,shapes,specs,props,details,[Path(__file__),H/'control_rebuild_io_v2.py',parent.folder/'report.json',early.folder/'isolated/manifest.json'],changed_definitions=sorted(set(changed)))
print('Saved alignment study with explicit nonphysical envelopes.',flush=True)
