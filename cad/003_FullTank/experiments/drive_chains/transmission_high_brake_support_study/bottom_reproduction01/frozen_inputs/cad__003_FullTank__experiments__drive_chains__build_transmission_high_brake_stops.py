"""Install tested M363 retention and M366 bottom stops in the development assembly."""
import argparse,shutil,sys,uuid
from pathlib import Path
H=Path(__file__).resolve().parent;STAGE=H.parents[1];ROOT=STAGE.parents[1];sys.path[:0]=[str(H),str(STAGE)]
from lib.evidence import read,write,sha
from lib.cad_build import metadata
import FreeCAD as App
import Part
from transmission_high_brake_stop_parts import parts
V=App.Vector
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert not out.exists();out.mkdir(parents=True)
packet=H/'transmission_high_brake_support_study';parent=packet/'integrated01';r=read(parent/'report.json');m=read(parent/'isolated/manifest.json');source=parent/r['native_file'];prototype=packet/'bottom_stops03';pr=read(prototype/'report.json')
assert sha(source)==r['native_sha256']==m['native_sha256']==pr['parent_native_sha256'];checkpoint=read(parent/'development_checkpoint.json')
assert all(sha(packet/f)==v for f,v in checkpoint['completed_receipts'].items())
for f in [prototype/'report.json',prototype/'independent_checks.json',prototype/'exchange_checks.json',packet/'bottom_variation01/report.json',packet/'bottom_variation01/independent_checks.json']:assert read(f)['passed'],f
cpath=packet/'stop_controls.json';c=read(cpath)['controls'];assert c==pr['controls'];rows={v['name']:v for v in m['occurrences']}
def shape(key):
 d=m['definitions'][key];assert sha(d['brep_path'])==d['brep_sha256'];s=Part.Shape();s.read(d['brep_path']);return s
base=App.Placement(V(*r['interfaces']['PortHighSpeedBrake']['center_world_mm']),App.Rotation());targets=[]
for suffix in ['LongBand','ShortBand','AnchorEnd']:
 row=rows['PortHighSpeedBrake'+suffix];s=shape(row['definition']);s.Placement=base.inverse().multiply(App.Placement(App.Matrix(*row['frame'])));targets.append(s)
shapes,details,envelopes=parts(c,r['controls'],shape('Def_HighBrakeSupport_anchor_bracket'),targets)
assert details==pr['details'];sources=read(packet/'sources.json');assert all(sha(ROOT/f)==v for f,v in sources['source_hashes'].items())
locked=[Path(__file__),cpath,packet/'sources.json',packet/'source_registration.json',parent/'report.json',parent/'development_checkpoint.json',parent/'isolated/manifest.json',prototype/'report.json',prototype/'independent_checks.json',prototype/'exchange_checks.json',prototype/pr['native_file'],packet/'bottom_variation01/report.json',packet/'bottom_variation01/independent_checks.json',STAGE/'lib/cad_build.py',STAGE/'lib/evidence.py']
locked+=sorted({Path(v.__file__).resolve() for v in list(sys.modules.values()) if getattr(v,'__file__',None) and Path(v.__file__).resolve().parent==H and str(v.__file__).endswith('.py')})
inputs={str(f.relative_to(ROOT)):sha(f) for f in sorted(set(locked))};doc=App.openDocument(str(source))
body=doc.getObject('Def_HighBrakeSupport_anchor_bracket');body.Tip.Shape=shapes['anchor_bracket'];metadata(body,ParameterUpdate='Regenerate with build_transmission_high_brake_stops.py',ReconstructionStatus='Retained fork and MX60 mounting foot; estimated lower receiving shelf and connecting ribs added for the M366 stop and paired transverse MX76 screws.')
roles={'anchor_pin':('M363',['SNL:137:003']),'anchor_cotter':('',['SNL:137:004']),'bottom_stop':('M366',['SNL:223:004']),'bottom_lock_plate':('MX77',[]),'mount_screw':('MX76',['SNL:205:009']),'stop_screw':('M400',['SNL:205:022']),'stop_nut':('',['SNL:205:023'])}
def ids(rids):return sorted({pid for row in sources['source_records'] if row['record_id'] in rids for pid in row['part_ids']})
made={};added={'Definitions':[]};expected={};groups=[]
for role,(mark,rids) in roles.items():
 body=doc.addObject('PartDesign::Body','Def_HighBrakeStops_'+role);doc.Definitions.addObject(body);body.newObject('PartDesign::Feature','ReconstructedBrakeStop').Shape=shapes[role]
 metadata(body,DefinitionKey='high_brake_stops_'+role,SourcePartMark=mark,SourceRecords=rids,SurveyIds=ids(rids),Representation='assembly',Coverage='reconstruction_trial',ParameterUpdate='Regenerate with build_transmission_high_brake_stops.py',ReconstructionStatus='Source identity and interface-constrained reconstruction; unprinted dimensions and formed details estimated.',SourceEvidence='3/16x2inch cotter stock; installed formed variant with two round legs. See developed-length datum and eye-overlap limitation.' if role=='anchor_cotter' else 'HB133/HB154 and the source-linked support packet. MX77 handbook plate differs from later catalogue lock washers.' if role=='bottom_lock_plate' else 'See bottom-stop controls and physical catalogue identity.')
 made[role]=body;added['Definitions'].append(body.Name)
def group(name,parent,rids):
 g=doc.addObject('App::Part',name);parent.addObject(g);g.Uid=str(uuid.uuid5(uuid.NAMESPACE_URL,'markviii:high-brake-stop:'+name));metadata(g,SourceRecords=rids,SurveyIds=ids(rids),Coverage='reconstruction_trial');groups.append(name);added.setdefault(parent.Name,[]).append(name);return g
for hand in ['Port','Starboard']:
 prefix=hand+'HighSpeedBrake';brake=doc.getObject(prefix);support=doc.getObject(prefix+'AnchorSupportAssembly')
 pin=group(prefix+'AnchorPinAssembly',support,['SNL:137:001']);bottom=group(prefix+'BottomStopAssembly',brake,[])
 sets={i:group(prefix+'BottomStopSetScrewAssembly'+str(i),bottom,['SNL:205:020']) for i in [1,2]}
 for pn,v in pr['specs'].items():
  if not pn.startswith(hand) or v['role']=='anchor_bracket':continue
  suffix=pn[len(hand):];name=prefix+suffix;role=v['role'];owner=pin if role in ['anchor_pin','anchor_cotter'] else sets[int(suffix[-1])] if role in ['stop_screw','stop_nut'] else bottom
  link=doc.addObject('App::Link',name);owner.addObject(link);link.setLink(made[role]);link.LinkPlacement=App.Placement(App.Matrix(*v['local_frame']));metadata(link,OccurrenceId=name,Subsystem='Drivetrain',SourceRecords=roles[role][1],Coverage='reconstruction_trial')
  ancestors=[];node=owner
  while node is not None:
   ancestors.append(node.Name);parents=[x for x in node.InList if x.TypeId=='App::Part'];assert len(parents)<=1;node=parents[0] if parents else None
  expected[name]=dict(definition=made[role].Name,frame=list(owner.getGlobalPlacement().multiply(link.LinkPlacement).toMatrix().A),owners=list(reversed(ancestors)),prototype_occurrence=pn)
  added.setdefault(owner.Name,[]).append(name)
doc.Root.Label='Powertrain development — high-speed anchor retention and bottom stops'
doc.Root.RegistrationStatus='M363 pins/cotters and M366 bottom stops with mounting and adjustment hardware. Top/back stops, M365 clips, service paths and full support-packet qualification remain pending.'
native=out/'PowertrainWithHighBrakeBottomStops.FCStd';doc.Definitions.Visibility=False;doc.recompute();doc.saveAs(str(native));App.closeDocument(doc.Name)
assert len(expected)==20 and len(made)==7 and len(groups)==8 and sha(source)==r['native_sha256'] and all(sha(ROOT/f)==v for f,v in inputs.items())
frozen=out/'frozen_inputs';frozen.mkdir()
for f in sorted(set(locked)):
 if f.suffix!='.FCStd':shutil.copy2(f,frozen/str(f.relative_to(ROOT)).replace('/','__'))
write(out/'report.json',dict(native_file=native.name,native_sha256=sha(native),source_native=str(source.relative_to(ROOT)),source_native_sha256=sha(source),input_hashes=inputs,controls=c,receiver_controls=r['controls'],details=details,interfaces=r['interfaces'],band_controls=r['band_controls'],expected_new_occurrences=expected,new_assemblies=groups,added_children=added,new_definitions=['Def_HighBrakeStops_'+k for k in roles],changed_definitions=['Def_HighBrakeSupport_anchor_bracket'],affected_occurrences=sorted(set(expected)|{h+'HighSpeedBrakeAnchorBracket' for h in ['Port','Starboard']}),expected_physical_occurrences=3149,expected_definition_count=539,expected_assembly_count=332,prototype=str(prototype.relative_to(ROOT)),prototype_native_sha256=pr['prototype_native_sha256'],limits=details['limits'],historical_geometry_qualified=False,installation_qualified=False,standard_assembly_modified=False,packet_complete=False))
print('Saved bottom-stop integration:3149 occurrences/539 definitions/332 assemblies.',flush=True)
