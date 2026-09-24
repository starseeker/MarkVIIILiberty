"""Install tested upper stops and clips with shared hardware in the development assembly."""
import argparse,shutil,sys,uuid
from pathlib import Path
H=Path(__file__).resolve().parent;STAGE=H.parents[1];ROOT=STAGE.parents[1];sys.path[:0]=[str(H),str(STAGE)]
from lib.evidence import read,write,sha
from lib.cad_build import metadata
import FreeCAD as App
import Part
from transmission_high_brake_upper_parts import parts
V=App.Vector
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert not out.exists();out.mkdir(parents=True)
packet=H/'transmission_high_brake_support_study';parent=packet/'integrated_bottom01';r=read(parent/'report.json');m=read(parent/'isolated/manifest.json');source=parent/r['native_file'];prototype=packet/'upper02';pr=read(prototype/'report.json')
assert sha(source)==r['native_sha256']==m['native_sha256']==pr['parent_native_sha256'];checkpoint=read(parent/'development_checkpoint.json')
assert all(sha(packet/f)==v for f,v in checkpoint['completed_receipts'].items())
receipts=[prototype/f for f in ['report.json','independent_checks.json','exchange_checks.json']]+[packet/'upper_variation01'/f for f in ['report.json','independent_checks.json','exchange_checks.json']]
for f in receipts:assert read(f)['passed'],f
cpath=packet/'upper_controls.json';c=read(cpath)['controls'];assert c==pr['controls'];rows={v['name']:v for v in m['occurrences']}
def shape(key,manifest=m):
 d=manifest['definitions'][key];assert sha(d['brep_path'])==d['brep_sha256'];s=Part.Shape();s.read(d['brep_path']);return s
base=App.Placement(V(*r['interfaces']['PortHighSpeedBrake']['center_world_mm']),App.Rotation());targets=[]
for suffix in ['LongBand','ShortBand','AnchorEnd','LongFrontEnd','ShortFrontEnd']:
 row=rows['PortHighSpeedBrake'+suffix];s=shape(row['definition']);s.Placement=base.inverse().multiply(App.Placement(App.Matrix(*row['frame'])));targets.append(s)
original=H/'transmission_high_brake_mechanism_study/trial01';om=read(original/'isolated/manifest.json');casekey='Def_TransmissionCore_bevel_case';assert om['native_sha256']==pr['original_case_parent_sha256']
shared={role:shape(key) for role,key in pr['shared_definitions'].items()};shared['stop_screw_radius']=r['controls']['stop_screw_diameter']/2
shapes,details,envelopes=parts(c,r['receiver_controls'],shape(casekey,om),shared,targets);assert details==pr['details']
sources=read(packet/'sources.json');assert all(sha(ROOT/f)==v for f,v in sources['source_hashes'].items())
locked=[Path(__file__),cpath,packet/'sources.json',packet/'source_registration.json',parent/'report.json',parent/'development_checkpoint.json',parent/'isolated/manifest.json',original/'isolated/manifest.json',prototype/pr['native_file'],*receipts,STAGE/'lib/cad_build.py',STAGE/'lib/evidence.py']
locked+=sorted({Path(v.__file__).resolve() for v in list(sys.modules.values()) if getattr(v,'__file__',None) and Path(v.__file__).resolve().parent==H and str(v.__file__).endswith('.py')})
inputs={str(f.relative_to(ROOT)):sha(f) for f in sorted(set(locked))};doc=App.openDocument(str(source))
body=doc.getObject(casekey);body.Tip.Shape=shapes['case'];metadata(body,ParameterUpdate='Regenerate with build_transmission_high_brake_upper.py',ReconstructionStatus='Retained case and receiving webs; upper bolt pitch revised from65 to60mm to share the handbook MX61 locking plate. Material change bounded to the old and new upper drill envelopes.')
roles={'top_stop':('M399',['SNL:223:005']),'back_stop':('M398',['SNL:223:003']),'clip':('M365',['SNL:66:022'])}
records={**{k:v[1] for k,v in roles.items()},'lock_plate':[],'mount_screw':['SNL:205:006'],'stop_screw':['SNL:205:022'],'stop_nut':['SNL:205:023']}
def ids(rids):return sorted({pid for row in sources['source_records'] if row['record_id'] in rids for pid in row['part_ids']})
made={role:doc.getObject(key) for role,key in pr['shared_definitions'].items()};added={'Definitions':[]};expected={};groups=[]
for role,(mark,rids) in roles.items():
 body=doc.addObject('PartDesign::Body','Def_HighBrakeUpper_'+role);doc.Definitions.addObject(body);body.newObject('PartDesign::Feature','ReconstructedUpperBrakeStop').Shape=shapes[role]
 metadata(body,DefinitionKey='high_brake_upper_'+role,SourcePartMark=mark,SourceRecords=rids,SurveyIds=ids(rids),Representation='assembly',Coverage='reconstruction_trial',ParameterUpdate='Regenerate with build_transmission_high_brake_upper.py',ReconstructionStatus='Source identity and arrangement; unprinted stock, bends, widths and hidden retaining details estimated.',SourceEvidence='HB133 fixed diagnostic registration and SNL catalogue identity; independent saved-interface and exchange checks. Clip wrap and pierced tongue are explicit reconstruction hypotheses.')
 made[role]=body;added['Definitions'].append(body.Name)
def group(name,parent,rids):
 g=doc.addObject('App::Part',name);parent.addObject(g);g.Uid=str(uuid.uuid5(uuid.NAMESPACE_URL,'markviii:high-brake-upper:'+name));metadata(g,SourceRecords=rids,SurveyIds=ids(rids),Coverage='reconstruction_trial');groups.append(name);added.setdefault(parent.Name,[]).append(name);return g
for hand in ['Port','Starboard']:
 prefix=hand+'HighSpeedBrake';brake=doc.getObject(prefix);upper=group(prefix+'UpperStopAssembly',brake,[]);adjust=group(prefix+'UpperStopSetScrewAssembly',upper,['SNL:205:020'])
 for pn,v in pr['specs'].items():
  if not pn.startswith(hand):continue
  suffix=pn[len(hand):];name=prefix+('Upper'+suffix if suffix in ['StopScrew','StopNut'] else suffix);role=v['role'];owner=adjust if role in ['stop_screw','stop_nut'] else upper
  link=doc.addObject('App::Link',name);owner.addObject(link);link.setLink(made[role]);link.LinkPlacement=App.Placement(App.Matrix(*v['local_frame']));metadata(link,OccurrenceId=name,Subsystem='Drivetrain',SourceRecords=records[role],Coverage='reconstruction_trial')
  ancestors=[];node=owner
  while node is not None:
   ancestors.append(node.Name);parents=[x for x in node.InList if x.TypeId=='App::Part'];assert len(parents)<=1;node=parents[0] if parents else None
  expected[name]=dict(definition=made[role].Name,frame=list(owner.getGlobalPlacement().multiply(link.LinkPlacement).toMatrix().A),owners=list(reversed(ancestors)),prototype_occurrence=pn);added.setdefault(owner.Name,[]).append(name)
doc.Root.Label='Powertrain development — high-speed brake supports, stops and clips'
doc.Root.RegistrationStatus='M399/M398 stops and M365 clips installed with shared MX60, MX61 and M400/nut definitions. Standard view static geometry; controls, full service paths and complete support-packet qualification remain pending.'
native=out/'PowertrainWithHighBrakeUpperStops.FCStd';doc.Definitions.Visibility=False;doc.recompute();doc.saveAs(str(native));App.closeDocument(doc.Name)
assert len(expected)==16 and len(groups)==4 and sha(source)==r['native_sha256'] and all(sha(ROOT/f)==v for f,v in inputs.items())
frozen=out/'frozen_inputs';frozen.mkdir()
for f in sorted(set(locked)):
 if f.suffix!='.FCStd':shutil.copy2(f,frozen/str(f.relative_to(ROOT)).replace('/','__'))
write(out/'report.json',dict(native_file=native.name,native_sha256=sha(native),source_native=str(source.relative_to(ROOT)),source_native_sha256=sha(source),input_hashes=inputs,controls=c,receiver_controls=r['receiver_controls'],details=details,interfaces=r['interfaces'],band_controls=r['band_controls'],expected_new_occurrences=expected,new_assemblies=groups,added_children=added,new_definitions=['Def_HighBrakeUpper_'+k for k in roles],shared_definitions=pr['shared_definitions'],changed_definitions=[casekey],affected_occurrences=sorted(set(expected)|{'CenterTransmissionCore_bevel_case'}),expected_physical_occurrences=3165,expected_definition_count=542,expected_assembly_count=336,prototype=str(prototype.relative_to(ROOT)),prototype_native_sha256=pr['prototype_native_sha256'],limits=details['limits'],historical_geometry_qualified=False,installation_qualified=False,standard_assembly_modified=False,packet_complete=False))
print('Saved upper-stop integration:3165 occurrences/542 definitions/336 assemblies.',flush=True)
