"""Populate source-counted high-speed levers, free-end pins and adjustment units."""
import argparse,shutil,sys,uuid
from pathlib import Path
H=Path(__file__).resolve().parent;STAGE=H.parents[1];ROOT=STAGE.parents[1];sys.path[:0]=[str(H),str(STAGE)]
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--controls',type=Path,default=H/'transmission_high_brake_mechanism_study/controls.json');a=p.parse_args()
out=a.output.resolve();out.mkdir(parents=True,exist_ok=True);parent=H/'transmission_high_brake_front_study/trial01'
r=read(parent/'report.json');m=read(parent/'isolated/manifest.json');q=read(parent/'qualification.json');source=parent/r['native_file']
assert q['local_static_checks_passed'] and sha(source)==r['native_sha256']==m['native_sha256']==q['native_sha256']
packet=H/'transmission_high_brake_mechanism_study/sources.json';sources=read(packet);assert all(sha(ROOT/f)==v for f,v in sources['source_hashes'].items());c=read(a.controls)['controls']
import FreeCAD as App
import Part
from lib.cad_build import metadata
from transmission_high_brake_mechanism_parts import parts
new,details,curves=parts(c,r);native=out/'PowertrainWithHighBrakeMechanism.FCStd';assert not native.exists()
locked=[Path(__file__),a.controls.resolve(),packet,parent/'report.json',parent/'qualification.json',parent/'isolated/manifest.json',STAGE/'lib/cad_build.py',STAGE/'lib/evidence.py']
locked+=sorted({Path(module.__file__).resolve() for module in list(sys.modules.values()) if getattr(module,'__file__',None) and Path(module.__file__).resolve().parent==H and str(module.__file__).endswith('.py')})
inputs={str(f.relative_to(ROOT)):sha(f) for f in sorted(set(locked))};doc=App.openDocument(str(source));defs={};rows={v['name']:v for v in m['occurrences']}
specs=[('pin','M356',['SNL:137:005']),('cotter','',[]),('lever_left','M355B',['SNL:118:027']),('lever_right','M355A',['SNL:118:028']),('rivet','',['SNL:118:029']),('nut','M357',['SNL:253:023']),('screw','M358',['SNL:253:024']),('spring','M369',['SNL:253:025']),('washer_a','MX78A',['SNL:253:026']),('washer_b','MX78B',['SNL:253:027'])]
records={}
for role,mark,rids in specs:
 body=doc.addObject('PartDesign::Body','Def_HighBrakeMechanism_'+role);doc.Definitions.addObject(body);body.newObject('PartDesign::Feature','ReconstructedHighBrakeMechanismPart').Shape=new[role]
 ids=sorted({pid for v in sources['source_records'] if v['record_id'] in rids for pid in v['part_ids']})
 assert ids or role=='cotter'
 metadata(body,DefinitionKey='high_brake_mechanism_'+role,SourcePartMark=mark,SourceRecords=rids,SurveyIds=ids,Representation='assembly',Coverage='reconstruction_trial',ParameterUpdate='Regenerate with build_transmission_high_brake_mechanism.py',ReconstructionStatus='Source identity/count and handbook arrangement; unprinted profiles, stock and hidden sections estimated. Nominal thread envelopes.',SourceEvidence='Handbook printed pages 151 and 154; free-end cotter stock estimated independently of M363 anchor cotter.' if role=='cotter' else 'SNL source rows and HB133/HB100. Printed joining-rivet stock and washer bores retained; see sources.json and controls.json.')
 defs[role]=body;records[role]=rids
nonphysical=[]
for role,s in curves.items():
 obj=doc.addObject('PartDesign::Feature','HighBrakeMechanism_'+role);doc.Definitions.addObject(obj);obj.Shape=s;obj.Visibility=False
 metadata(obj,NonPhysical=True,Role='Estimated construction curve; excluded from physical definitions and occurrences.',ParameterUpdate='Regenerate with build_transmission_high_brake_mechanism.py');nonphysical.append(obj.Name)
assemblies=[];expected={};added={'Definitions':[v.Name for v in defs.values()]+nonphysical};V=App.Vector
def group(name,parent,pose):
 g=doc.addObject('App::Part',name);parent.addObject(g);g.Uid=str(uuid.uuid5(uuid.NAMESPACE_URL,'markviii:high-brake-mechanism:'+name));g.Placement=pose;assemblies.append(name);added.setdefault(parent.Name,[]).append(name);return g
for hand in ['Port','Starboard']:
 prefix=hand+'HighSpeedBrake';owner=doc.getObject(prefix)
 old_owners=next(v['owners'] for v in rows.values() if prefix in v['owners']);base_owners=old_owners[:old_owners.index(prefix)+1]
 def add(suffix,role,g,pose):
  name=prefix+suffix;obj=doc.addObject('App::Link',name);g.addObject(obj);obj.setLink(defs[role]);obj.LinkPlacement=pose
  metadata(obj,OccurrenceId=name,Subsystem='Drivetrain',SourceRecords=records[role],Coverage='reconstruction_trial')
  expected[name]=dict(definition=defs[role].Name,frame=list(g.getGlobalPlacement().multiply(pose).toMatrix().A),owners=base_owners+[g.Name]);added.setdefault(g.Name,[]).append(name)
 lever=group(prefix+'OperatingLeverAssembly',owner,App.Placement())
 metadata(lever,SourceRecords=['SNL:118:025'],SourceEvidence='Two complete levers; each has both M355 members and four joining rivets. Assembly identity is not another physical leaf.')
 for side in ['left','right']:add('Lever'+side.title(),'lever_'+side,lever,App.Placement())
 for i,(x,z) in enumerate(c['lever_rivet_centers_xz'],1):add('LeverRivet'+str(i),'rivet',lever,App.Placement(V(x,0,z),App.Rotation()))
 adjust=group(prefix+'AdjustingAssembly',owner,App.Placement(App.Matrix(*details['screw_frame'])))
 for suffix,role,z in [('AdjustingScrew','screw',0),('LowerSpringWasher','washer_b',details['washer_b_distance_mm']),('AdjustingSpring','spring',details['spring_base_distance_mm']),('UpperSpringWasher','washer_a',details['washer_a_distance_mm']),('AdjustingNut','nut',details['lever_upper_seat_distance_mm'])]:add(suffix,role,adjust,App.Placement(V(0,0,z),App.Rotation()))
 orient=App.Rotation() if hand=='Port' else App.Rotation(V(1,0,0),180)
 for joint in ['upper','lower']:
  g=group(prefix+joint.title()+'PinJoint',owner,App.Placement(V(*details[joint+'_pin_mm']),orient))
  add(joint.title()+'FreeEndPin','pin',g,App.Placement());add(joint.title()+'FreeEndCotter','cotter',g,App.Placement(V(0,details['cotter_station_y_mm'],0),App.Rotation()))
doc.Root.Label='Powertrain development — high-speed operating mechanisms'
doc.Root.RegistrationStatus='Paired levers, retained free-end pins and spring adjustment installed as documented estimates. External anchor supports, high-speed stops and control rods pending.'
doc.Definitions.Visibility=False;doc.recompute();doc.saveAs(str(native));App.closeDocument(doc.Name)
assert len(expected)==30 and len(new)==10 and len(assemblies)==8
assert sha(source)==r['native_sha256'] and all(sha(ROOT/f)==v for f,v in inputs.items())
frozen=out/'frozen_inputs';frozen.mkdir()
for f in sorted(set(locked)):shutil.copy2(f,frozen/str(f.relative_to(ROOT)).replace('/','__'))
folder=out/'changed_shapes';folder.mkdir()
for k,s in {**{'Def_HighBrakeMechanism_'+k:v for k,v in new.items()},**{'HighBrakeMechanism_'+k:v for k,v in curves.items()}}.items():s.exportBrep(str(folder/(k+'.brep')))
write(out/'report.json',dict(native_file=native.name,native_sha256=sha(native),source_native=str(source.relative_to(ROOT)),source_native_sha256=sha(source),input_hashes=inputs,controls=c,front_controls=r['controls'],band_controls=r['band_controls'],interfaces=r['interfaces'],details=details,expected_new_occurrences=expected,new_assemblies=assemblies,added_children=added,nonphysical_features=nonphysical,new_definitions=['Def_HighBrakeMechanism_'+k for k in new],changed_definitions=[],affected_occurrences=sorted(expected),expected_physical_occurrences=len(rows)+30,expected_definition_count=len(m['definitions'])+10,expected_assembly_count=len(m['assemblies'])+8,limits=details['limits'],historical_geometry_qualified=False,installation_qualified=False,standard_assembly_modified=False,packet_complete=False))
print('Saved',len(rows)+30,'physical occurrences; high-speed operating mechanism populated.',flush=True)
