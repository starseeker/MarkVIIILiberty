"""Rebuild washer/return-spring trial with explicit attachments and source binding."""
import argparse
from pathlib import Path
from control_rebuild_io import App,Part,H,ROOT,C,Saved,pose,trial,read,sha
from control_rebuild_spring_parts_v3 import washer,spring

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--controls',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args();cfg=read(a.controls)
source=ROOT/cfg['source_review'];assert sha(source)==cfg['source_review_sha256']
evidence=read(source)
assert all(sha(ROOT/f)==h for f,h in evidence['source_hashes'].items())
parent=Saved(C/'low_rods_integrated01')
assert parent.report['native_sha256']==cfg['parent_native_sha256']
shapes={};specs={};properties={};details={};curves={}

def receiver(name):
    if name in specs:return
    r=parent.rows[name];key=r['definition']
    shapes[key]=parent.definition(key)
    properties[key]=parent.manifest['definitions'][key]['properties']
    specs[name]=dict(definition=key,frame=r['frame'],owner=r['owners'][-1],role='receiver')

wk='Def_ControlSpringWasher_Redo'
shapes[wk]=washer(**cfg['washer'])
properties[wk]=dict(SourcePartMark='M567',SourceRecords=['SNL:267:009'],
    DefinitionKey='control_spring_washer',Representation='reconstruction_trial',
    ReconstructionStatus='Estimated compressed spring-washer envelope; free form and placement application remain inferred.',
    ParameterUpdate='Regenerate with trial_control_rebuild_springs_v3.py and '+str(a.controls.relative_to(ROOT)))

for side,sign in [('Port',1),('Starboard',-1)]:
    for kind,ay,near in [('Low',495.3,sign),('Track',806.45,-sign)]:
        base=side+kind;connection=base+'ShortConnection'
        receiver(side+('LowSpeed' if kind=='Low' else 'Track')+'BrakeLever')
        receiver(side+kind+'HorizontalLever');receiver(base+'ConnectingRod')
        receiver(side+'LowSpringBracket')
        for joint in ['Brake','Fulcrum']:
            stem=base+joint+'Joint'
            for role in ['Fork','Pin','Cotter','Nut']:receiver(stem+role)
            wp=pose(parent.rows[stem+'Pin']['frame']).multiply(
                App.Placement(App.Vector(0,17.7125 if kind=='Low' else 16.125,0),App.Rotation()))
            specs[stem+'Washer']=dict(definition=wk,frame=list(wp.toMatrix().A),owner=stem,role='washer')
        fork=base+'BrakeJointFork';socket=pose(parent.rows[fork]['frame']).Base
        seat=socket.x+(49.2125 if kind=='Low' else 44.45)
        sk='Def_ControlReturnSpring_'+base+'_Redo'
        s,path,info=spring(socket,seat,App.Vector(2368,sign*ay,694.975),near,**cfg['spring'])
        shapes[sk]=s;curves[sk]=path;details[base+'ReturnSpring']=info
        properties[sk]=dict(SourcePartMark='M564',SourceRecords=['SNL:220:023','HB:nomenclature:188:052'],
            DefinitionKey='control_return_spring',Representation='reconstruction_trial',
            InstalledState=base,ReconstructionStatus='Estimated installed extension state; hook attachment hypothesis explicit in source review.',
            ParameterUpdate='Regenerate with trial_control_rebuild_springs_v3.py and '+str(a.controls.relative_to(ROOT)))
        specs[base+'ReturnSpring']=dict(definition=sk,frame=list(App.Placement(socket,App.Rotation()).toMatrix().A),
               owner=connection,role='spring')

details['controls']=cfg
native=trial(a.output,parent,shapes,specs,properties,details,
    [Path(__file__),H/'control_rebuild_io.py',H/'control_rebuild_spring_parts_v3.py',a.controls,source,
     parent.folder/'qualification.json',parent.folder/'isolated/manifest.json',parent.folder/'report.json'],curves)
print('Saved',len(specs),'occurrences;',native,flush=True)
