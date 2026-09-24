"""Add the tested rear high-speed control joints to the qualified support assembly."""
import argparse,shutil,sys,uuid
from pathlib import Path
H=Path(__file__).resolve().parent;STAGE=H.parents[1];ROOT=STAGE.parents[1];sys.path[:0]=[str(H),str(STAGE)]
import FreeCAD as App
from lib.evidence import read,write,sha
from lib.cad_build import metadata
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert not out.exists();out.mkdir(parents=True)
packet=H/'transmission_controls_study';parent=H/'transmission_high_brake_support_study/integrated_upper01';pr=read(parent/'report.json');q=read(parent/'qualification.json')
source=parent/pr['native_file'];assert q['local_static_checks_passed'] and sha(source)==q['native_sha256']
prototype=packet/'joint01';r=read(prototype/'report.json');pnative=prototype/r['native_file'];assert sha(pnative)==r['native_sha256'] and r['parent_native_sha256']==sha(source)
receipts=[folder/file for folder in [prototype,packet/'joint_stock_variation01'] for file in ['independent_checks.json','exchange_checks.json']]
for f in receipts:assert read(f)['passed'] and read(f)['native_sha256']==read(f.parent/'report.json')['native_sha256']
assert read(prototype/'visual_review.json')['disposition']=='reviewed_local_approximation'
inputs=[Path(__file__),prototype/'report.json',pnative,prototype/'visual_review.json',prototype/'render_receipt.json',
        packet/'sources.json',packet/'high_speed_joint_controls.json',parent/'qualification.json',parent/'isolated/manifest.json',*receipts,STAGE/'lib/cad_build.py']
assert all(sha(ROOT/f)==v for f,v in r['input_hashes'].items())
inputs_hash={str(f.relative_to(ROOT)):sha(f) for f in inputs}
doc=App.openDocument(str(pnative));shapes={};attributes={}
try:
    for role in ['fork','pin','cotter']:
        body=doc.getObject('Def_'+role);shapes[role]=body.Shape.copy()
        attributes[role]={k:getattr(body,k) for k in ['SourcePartMark','SourceRecords','SurveyIds']}
finally:App.closeDocument(doc.Name)
doc=App.openDocument(str(source));made={'nut':doc.getObject(r['shared_definitions']['nut'])};added={'Definitions':[]};expected={};groups=[]
for role,s in shapes.items():
    body=doc.addObject('PartDesign::Body','Def_ControlJoint_'+role);doc.Definitions.addObject(body);body.newObject('PartDesign::Feature','ReconstructedControlJoint').Shape=s
    metadata(body,**attributes[role],DefinitionKey='control_joint_'+role,Representation='assembly',Coverage='reconstruction_trial',
        ParameterUpdate='Regenerate trial_transmission_control_joint.py then build_transmission_control_joints.py',
        ReconstructionStatus='Reviewed local M569B/M568A joint approximation; fork length datum, stock, pitch and nominal thread details remain inferred.')
    made[role]=body;added['Definitions'].append(body.Name)
for hand in ['Port','Starboard']:
    owner=doc.getObject(hand+'HighSpeedBrake');name=hand+'HighSpeedBrakeControlJoint';group=doc.addObject('App::Part',name);owner.addObject(group)
    group.Uid=str(uuid.uuid5(uuid.NAMESPACE_URL,'markviii:rear-control-joint:'+name))
    group.Placement=owner.getGlobalPlacement().inverse().multiply(App.Placement(App.Matrix(*r['joints'][hand]['frame'])))
    metadata(group,Coverage='reconstruction_trial',ReconstructionStatus='Rear M575 rod connection; rod and forward joint remain pending.')
    added.setdefault(owner.Name,[]).append(name);groups.append(name)
    for role in ['fork','pin','cotter','nut']:
        pn=hand+role.title();spec=r['specs'][pn];name=hand+'HighSpeedBrakeControl'+role.title()
        link=doc.addObject('App::Link',name);group.addObject(link);link.setLink(made[role]);link.LinkPlacement=App.Placement(App.Matrix(*spec['local_frame']))
        metadata(link,OccurrenceId=name,Subsystem='Drivetrain',SourceRecords=r['record_ids'][role],Coverage='reconstruction_trial')
        owners=[];node=group
        while node is not None:
            owners.append(node.Name);parents=[x for x in node.InList if x.TypeId=='App::Part'];assert len(parents)<=1;node=parents[0] if parents else None
        expected[name]=dict(definition=made[role].Name,frame=list(group.getGlobalPlacement().multiply(link.LinkPlacement).toMatrix().A),owners=list(reversed(owners)),prototype_occurrence=pn)
        added.setdefault(group.Name,[]).append(name)
doc.Root.Label='Powertrain development — rear high-speed control joints'
doc.Root.RegistrationStatus='Paired rear M569B/M568A fork, pin and cotter joints with shared3/4inch plain nuts. Full operating rods, support channel, springs and standard-tank integration remain pending.'
doc.Definitions.Visibility=False;doc.recompute();native=out/'PowertrainWithRearControlJoints.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
assert sha(source)==q['native_sha256'] and all(sha(ROOT/f)==v for f,v in inputs_hash.items())
frozen=out/'frozen_inputs';frozen.mkdir()
for f in inputs:
    if f.suffix!='.FCStd':shutil.copy2(f,frozen/str(f.relative_to(ROOT)).replace('/','__'))
write(out/'report.json',dict(native_file=native.name,native_sha256=sha(native),source_native=str(source.relative_to(ROOT)),source_native_sha256=sha(source),
    prototype=str(prototype.relative_to(ROOT)),prototype_native_sha256=sha(pnative),input_hashes=inputs_hash,controls=r['controls'],details=r['details'],
    expected_new_occurrences=expected,new_assemblies=groups,added_children=added,new_definitions=['Def_ControlJoint_'+k for k in shapes],
    shared_definitions=r['shared_definitions'],changed_definitions=[],affected_occurrences=sorted(expected),
    expected_physical_occurrences=3173,expected_definition_count=545,expected_assembly_count=338,
    historical_geometry_qualified=False,installation_qualified=False,standard_assembly_modified=False,packet_complete=False))
print('Saved3173 physical occurrences /545 definitions /338 assembly groups.',flush=True)
