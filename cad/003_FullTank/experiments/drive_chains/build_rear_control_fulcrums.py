"""Install four locally reviewed retained fulcrum units in the rear-channel hierarchy."""
import argparse
from pathlib import Path
import shutil
import sys
import uuid
H=Path(__file__).resolve().parent;ROOT=H.parents[3];sys.path.insert(0,str(H.parents[1]))
import FreeCAD as App
from lib.evidence import read,write,sha
from lib.cad_build import metadata

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert not out.exists()
packet=H/'transmission_controls_study';prototype=packet/'fulcrum02';r=read(prototype/'report.json');pm=read(prototype/'isolated/manifest.json')
source=ROOT/r['parent_native'];parent=source.parent;parent_q=read(parent/'qualification.json');trial=prototype/r['native_file']
assert sha(source)==r['parent_native_sha256']==parent_q['native_sha256'] and parent_q['local_static_checks_passed']
assert sha(trial)==r['native_sha256']==pm['native_sha256']
assert all(sha(ROOT/path)==digest for path,digest in r['input_hashes'].items())
receipts=[folder/file for folder in [prototype,packet/'fulcrum_variation02'] for file in ['independent_checks.json','context_checks.json','exchange_checks.json']]+[prototype/'reproduction_checks.json']
for path in receipts:
    q=read(path);assert q['passed'] and q['native_sha256']==read(path.parent/'report.json')['native_sha256']
assert read(prototype/'visual_review.json')['disposition']=='reviewed_local_approximation'
inputs=[Path(__file__),H.parents[1]/'lib/cad_build.py',prototype/'report.json',prototype/'isolated/manifest.json',trial,
        prototype/'visual_review.json',prototype/'render_receipt.json',parent/'qualification.json',parent/'isolated/manifest.json',*receipts]
hashes={str(path.relative_to(ROOT)):sha(path) for path in inputs}
doc=App.openDocument(str(trial))
roles=['bracket','washer','cotter','rivet','lever_track','lever_low_left','lever_low_right']
try:
    shapes={role:doc.getObject('Def_ControlFulcrum_'+role).Shape.copy() for role in roles+['channel']}
    attrs={role:{key:getattr(doc.getObject('Def_ControlFulcrum_'+role),key) for key in ['SourcePartMark','SourceRecords','SurveyIds']} for role in roles}
finally:App.closeDocument(doc.Name)
out.mkdir(parents=True);doc=App.openDocument(str(source));made={};added={'Definitions':[],'RearControlChannel':[]};groups=[];expected={}
for role in roles:
    body=doc.addObject('PartDesign::Body','Def_RearControlFulcrum_'+role);doc.Definitions.addObject(body)
    body.newObject('PartDesign::Feature','ReconstructedRearControlFulcrum').Shape=shapes[role]
    metadata(body,**attrs[role],DefinitionKey='rear_control_fulcrum_'+role,Representation='assembly',Coverage='reconstruction_trial',
             ParameterUpdate='Regenerate fulcrum_controls02.json with trial_rear_control_fulcrums.py, then build_rear_control_fulcrums.py',
             ReconstructionStatus='Reviewed local M4131/retained-lever approximation; mounting topology, bearing and washer profiles, and rod-end dimensions remain inferred.')
    made[role]=body;added['Definitions'].append(body.Name)
channel=doc.getObject(r['controls']['channel_definition']);assert channel.Placement.isIdentity()
receiver_feature=channel.Tip.Name;channel.Tip.Shape=shapes['channel']
metadata(channel,FulcrumMountSourceRecords=['SNL:170:007'],FulcrumMountUpdate='Eight vertical passages for four M4131 cast-foot mounting hypotheses; regenerate fulcrum_controls02.json after the M4130 mounting increment.')
for name,station in r['controls']['stations'].items():
    key=name+'ControlFulcrum';group=doc.addObject('App::Part',key);doc.RearControlChannel.addObject(group)
    group.Uid=str(uuid.uuid5(uuid.NAMESPACE_URL,'markviii:installed-control-fulcrum:'+key))
    group.Placement=doc.RearControlChannel.getGlobalPlacement().inverse().multiply(App.Placement(App.Matrix(*pm['assemblies'][key]['world'])))
    metadata(group,Coverage='reconstruction_trial',ReconstructionStatus='Retained horizontal brake lever; connected rods and complete service remain pending.')
    groups.append(key);added['RearControlChannel'].append(key)
for row in pm['occurrences']:
    name=row['name'];spec=r['specs'][name];role=spec['role']
    if role=='channel':continue
    group=doc.getObject(spec['owner']);link=doc.addObject('App::Link',name);group.addObject(link);link.setLink(made[role])
    link.LinkPlacement=group.getGlobalPlacement().inverse().multiply(App.Placement(App.Matrix(*row['frame'])))
    metadata(link,OccurrenceId=name,Subsystem='Drivetrain',SourceRecords=r['record_ids'][role],Coverage='reconstruction_trial')
    expected[name]=dict(definition=made[role].Name,role=role,frame=row['frame'],owners=['Root','RearControlChannel',spec['owner']],prototype_occurrence=name)
    added.setdefault(group.Name,[]).append(name)
doc.Root.Label='Powertrain development — retained rear control fulcrums'
doc.Root.RegistrationStatus='Four M4131 fulcrums and retained M4132/M4133/M4134 horizontal levers on the rear channel. M4129, spring brackets, rod connections and standard integration remain open.'
doc.Definitions.Visibility=False;doc.recompute();native=out/'PowertrainWithRearControlFulcrums.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
assert sha(source)==r['parent_native_sha256'] and all(sha(ROOT/path)==digest for path,digest in hashes.items())
frozen=out/'frozen_inputs';frozen.mkdir()
for path in inputs:
    if path.suffix!='.FCStd':shutil.copy2(path,frozen/str(path.relative_to(ROOT)).replace('/','__'))
write(out/'report.json',dict(native_file=native.name,native_sha256=sha(native),source_native=str(source.relative_to(ROOT)),source_native_sha256=sha(source),
      prototype=str(prototype.relative_to(ROOT)),prototype_native_sha256=sha(trial),input_hashes=hashes,controls=r['controls'],details=r['details'],
      expected_new_occurrences=expected,new_assemblies=groups,added_children=added,new_definitions=added['Definitions'],shared_definitions={},
      changed_definitions=[r['controls']['channel_definition']],changed_receiver_feature=receiver_feature,
      affected_occurrences=sorted(expected)+[r['controls']['channel_occurrence']],expected_physical_occurrences=3226,
      expected_definition_count=558,expected_assembly_count=347,historical_geometry_qualified=False,installation_qualified=False,
      standard_assembly_modified=False,channel_complete=False,packet_complete=False))
print('Saved3226 physical occurrences /558 used definitions /347 groups; qualification pending.',flush=True)
