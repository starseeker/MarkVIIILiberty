"""Unqualified M575/M563 axis study: actual joints plus explicitly named envelopes."""
import argparse
from pathlib import Path
from control_rebuild_io_v2 import App,Part,H,ROOT,Saved,pose,trial,read,sha
V=App.Vector;X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
a=p.parse_args();parent=Saved(H/'transmission_controls_study/redo01/intermediate_integrated01')
shapes={};props={};specs={};details={}
def carry(name,frame=None):
    row=parent.rows[name];key=row['definition'];shapes[key]=parent.definition(key)
    props[key]=parent.manifest['definitions'][key]['properties']
    specs[name]=dict(definition=key,frame=list(frame.toMatrix().A) if frame else row['frame'],owner=row['owners'][-1],role='receiver')
    return pose(specs[name]['frame'])
for side in ['Starboard','Port']:
    stem=side+'HighSpeedBrakeControl';old=pose(parent.rows[stem+'Fork']['frame'])
    axis=old.Rotation.multVec(Y);frame=App.Placement(old.Base,App.Rotation(X,axis,X.cross(axis),'XYZ'))
    carry(stem+'Fork',frame)
    # Preserve the already installed pin/cotter rotation around the same bore.
    carry(stem+'Pin');carry(stem+'Cotter')
    oldnut=pose(parent.rows[stem+'Nut']['frame']);nutframe=frame.multiply(old.inverse().multiply(oldnut))
    carry(stem+'Nut',nutframe)
    for label in ['HighSpringBracket','HighSpringRivet1','HighSpringRivet2']:
        f=pose(parent.rows[side+label]['frame'])
        if side=='Port':f.Base-=Y*50.8
        carry(side+label,f)
    rear=frame.Base+X*19.05;end=V(2420,frame.Base.y,frame.Base.z)
    key='Def_'+side+'HighRodAxisEnvelope'
    shapes[key]=Part.makeCylinder(9.525,end.x-rear.x,V(),X)
    props[key]=dict(SourcePartMark='NONPHYSICAL M575 route envelope',SourceRecords=[],Representation='analysis_only')
    specs[side+'HighRodAxisEnvelope']=dict(definition=key,frame=list(App.Placement(rear,App.Rotation()).toMatrix().A),owner='Envelopes',role='envelope')
    start=frame.Base+X*(38.1+19.05);length=2317.45-start.x
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
shapes[key]=local.transformGeometry(matrix)
details['scope']='Alignment/envelope study only; no springs or complete rods modeled or qualified.'
trial(a.output,parent,shapes,specs,props,details,[Path(__file__),H/'control_rebuild_io_v2.py',parent.folder/'report.json',early.folder/'isolated/manifest.json'],changed_definitions=[key])
print('Saved alignment study with explicit nonphysical envelopes.',flush=True)
