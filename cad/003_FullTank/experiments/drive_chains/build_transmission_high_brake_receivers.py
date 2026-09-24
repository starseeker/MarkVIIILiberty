"""Integrate reviewed receiving webs and eight anchor-mount components."""
import argparse,shutil,sys,uuid
from pathlib import Path
H=Path(__file__).resolve().parent;STAGE=H.parents[1];ROOT=STAGE.parents[1];sys.path[:0]=[str(H),str(STAGE)]
from lib.evidence import read,write,sha
import FreeCAD as App
import Part
from lib.cad_build import metadata
from transmission_high_brake_support_parts import parts

p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert not out.exists();out.mkdir(parents=True)
packet=H/'transmission_high_brake_support_study';prototype=packet/'receivers04';pr=read(prototype/'report.json')
parent=H/'transmission_high_brake_mechanism_study/trial01';r=read(parent/'report.json');m=read(parent/'isolated/manifest.json');q=read(parent/'qualification.json');source=parent/r['native_file']
assert q['local_static_checks_passed'] and sha(source)==r['native_sha256']==q['native_sha256']==m['native_sha256']==pr['parent_native_sha256']
for path in [prototype/'report.json',prototype/'receiver_interface_checks.json',prototype/'exchange_refined02/exchange_checks.json',packet/'variation02/report.json',packet/'variation02/receiver_interface_checks.json']:
 assert read(path)['passed'],path
cpath=packet/'controls.json';c=read(cpath)['controls'];assert c==pr['controls']
sources=read(packet/'sources.json');assert all(sha(ROOT/f)==v for f,v in sources['source_hashes'].items())
case_key='Def_TransmissionCore_bevel_case';d=m['definitions'][case_key];assert sha(d['brep_path'])==d['brep_sha256'];old_case=Part.Shape();old_case.read(d['brep_path'])
shapes,details,envelopes=parts(c,old_case)
locked=[Path(__file__),cpath,packet/'sources.json',packet/'source_registration.json',prototype/'report.json',prototype/'receiver_interface_checks.json',prototype/'exchange_refined02/exchange_checks.json',prototype/'ReceivingWebStudy.FCStd',packet/'variation02/report.json',packet/'variation02/receiver_interface_checks.json',parent/'report.json',parent/'qualification.json',parent/'isolated/manifest.json',STAGE/'lib/cad_build.py',STAGE/'lib/evidence.py']
locked+=sorted({Path(v.__file__).resolve() for v in list(sys.modules.values()) if getattr(v,'__file__',None) and Path(v.__file__).resolve().parent==H and str(v.__file__).endswith('.py')})
inputs={str(f.relative_to(ROOT)):sha(f) for f in sorted(set(locked))}
doc=App.openDocument(str(source));body=doc.getObject(case_key);body.Tip.Shape=shapes['case']
metadata(body,ParameterUpdate='Regenerate with build_transmission_high_brake_receivers.py',ReconstructionStatus='Original case material retained; source-reviewed diagonal side webs, transverse support seats and blind receiving holes are conditional estimates. Existing bearing and frame datums retained.')
specs=[('anchor_bracket','M362',['SNL:41:027']),('anchor_lock_plate','MX61',[]),('mount_screw','MX60',['SNL:205:006'])]
defs={};records={};added={'Definitions':[]}
for role,mark,rids in specs:
 body=doc.addObject('PartDesign::Body','Def_HighBrakeSupport_'+role);doc.Definitions.addObject(body);body.newObject('PartDesign::Feature','ReconstructedHighBrakeSupport').Shape=shapes[role]
 ids=sorted({pid for v in sources['source_records'] if v['record_id'] in rids for pid in v['part_ids']})
 assert ids or role=='anchor_lock_plate'
 metadata(body,DefinitionKey='high_brake_support_'+role,SourcePartMark=mark,SourceRecords=rids,SurveyIds=ids,Representation='assembly',Coverage='reconstruction_trial',ParameterUpdate='Regenerate with build_transmission_high_brake_receivers.py',ReconstructionStatus='Source identity/arrangement; unprinted stock, hidden transverse shape and manufactured details estimated.',SourceEvidence='HB133 shared locking-plate form; exact survey identity absent; later SNL lock-washer alternative retained separately.' if role=='anchor_lock_plate' else 'HB133 and catalogue source packet; MX60 diameter follows the SNL271 washer application.')
 defs[role]=body;records[role]=rids;added['Definitions'].append(body.Name)
rows={v['name']:v for v in m['occurrences']};expected={};assemblies=[];V=App.Vector
for hand in ['Port','Starboard']:
 prefix=hand+'HighSpeedBrake';owner=doc.getObject(prefix);name=prefix+'AnchorSupportAssembly'
 g=doc.addObject('App::Part',name);owner.addObject(g);g.Uid=str(uuid.uuid5(uuid.NAMESPACE_URL,'markviii:high-brake-support:'+name));assemblies.append(name);added.setdefault(prefix,[]).append(name)
 base=rows[prefix+'AnchorEnd']['owners'];owners=base[:base.index(prefix)+1]+[name]
 def add(suffix,role,pose):
  name=prefix+suffix;link=doc.addObject('App::Link',name);g.addObject(link);link.setLink(defs[role]);link.LinkPlacement=pose
  metadata(link,OccurrenceId=name,Subsystem='Drivetrain',SourceRecords=records[role],Coverage='reconstruction_trial')
  expected[name]=dict(definition=defs[role].Name,frame=list(g.getGlobalPlacement().multiply(pose).toMatrix().A),owners=owners);added.setdefault(g.Name,[]).append(name)
 add('AnchorBracket','anchor_bracket',App.Placement());add('AnchorLockPlate','anchor_lock_plate',App.Placement())
 for i,f in enumerate(details['mounts']['bottom']['bolt_seat_frames'],1):
  pose=App.Placement(App.Matrix(*f));pose.Base+=pose.Rotation.multVec(V(0,0,c['bracket_stock']+c['lock_plate_stock']));add('AnchorMountScrew'+str(i),'mount_screw',pose)
doc.Root.Label='Powertrain development — high-speed brake receiving webs and anchor mounts'
doc.Root.RegistrationStatus='Eight anchor-mount parts and integral receiving webs installed. Anchor pins, cotters, band stops and control rods remain pending; full standard integration is unfinished.'
native=out/'PowertrainWithHighBrakeReceivers.FCStd';doc.Definitions.Visibility=False;doc.recompute();doc.saveAs(str(native));App.closeDocument(doc.Name)
assert len(expected)==8 and len(defs)==3 and len(assemblies)==2
assert sha(source)==r['native_sha256'] and all(sha(ROOT/f)==v for f,v in inputs.items())
frozen=out/'frozen_inputs';frozen.mkdir()
for f in sorted(set(locked)):
 if f.suffix!='.FCStd':shutil.copy2(f,frozen/str(f.relative_to(ROOT)).replace('/','__'))
folder=out/'changed_shapes';folder.mkdir()
for k,s in {**{'Def_HighBrakeSupport_'+k:v for k,v in shapes.items() if k!='case'},case_key:shapes['case']}.items():s.exportBrep(str(folder/(k+'.brep')))
write(out/'report.json',dict(native_file=native.name,native_sha256=sha(native),source_native=str(source.relative_to(ROOT)),source_native_sha256=sha(source),input_hashes=inputs,controls=c,details=details,interfaces=r['interfaces'],band_controls=r['band_controls'],expected_new_occurrences=expected,new_assemblies=assemblies,added_children=added,new_definitions=['Def_HighBrakeSupport_'+k for k in ['anchor_bracket','anchor_lock_plate','mount_screw']],changed_definitions=[case_key],affected_occurrences=sorted(set(expected)|{'CenterTransmissionCore_bevel_case'}),expected_physical_occurrences=3129,expected_definition_count=532,expected_assembly_count=324,prototype=str(prototype.relative_to(ROOT)),prototype_native_sha256=pr['prototype_native_sha256'],limits=details['limitations'],historical_geometry_qualified=False,installation_qualified=False,standard_assembly_modified=False,packet_complete=False))
print('Saved integrated receiver candidate:3129 occurrences,532 definitions,324 assemblies.',flush=True)
