"""Populate forward high-speed brake fittings and all source-counted lining fasteners."""
import argparse,shutil,sys,uuid
from pathlib import Path
H=Path(__file__).resolve().parent;STAGE=H.parents[1];ROOT=STAGE.parents[1];sys.path[:0]=[str(H),str(STAGE)]
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--controls',type=Path,default=H/'transmission_high_brake_front_study/controls.json');a=p.parse_args()
out=a.output.resolve();out.mkdir(parents=True,exist_ok=True);parent=H/'transmission_high_brake_joint_study/trial01'
r=read(parent/'report.json');m=read(parent/'isolated/manifest.json');q=read(parent/'qualification.json');source=parent/r['native_file']
assert q['local_static_checks_passed'] and sha(source)==r['native_sha256']==m['native_sha256']==q['native_sha256']
packet=H/'transmission_high_brake_front_study/sources.json';sources=read(packet);assert all(sha(ROOT/f)==v for f,v in sources['source_hashes'].items());c=read(a.controls)['controls']
import FreeCAD as App
import Part
from lib.cad_build import metadata
from transmission_high_brake_front_parts import parts,rotate_theta,relieve_case
bands={}
for role in ['long','short']:
 d=m['definitions']['Def_HighBrake_'+role+'_band'];assert sha(d['brep_path'])==d['brep_sha256'];s=Part.Shape();s.read(d['brep_path']);bands[role]=s
new,changed,details=parts(c,r,bands);native=out/'PowertrainWithHighBrakeFront.FCStd';assert not native.exists()
rows={v['name']:v for v in m['occurrences']};case_row=rows['CenterTransmissionCore_bevel_case'];case_key=case_row['definition']
d=m['definitions'][case_key];assert sha(d['brep_path'])==d['brep_sha256'];case=Part.Shape();case.read(d['brep_path'])
inverse=App.Placement(App.Matrix(*case_row['frame'])).inverse()
centers=[inverse.multVec(App.Vector(*v['center_world_mm'])) for v in r['interfaces'].values()]
changed[case_key],details['case_relief']=relieve_case(c,case,centers,r['band_controls']['width'])
details['limitations'].append('M263 rear bridge clearance is an interface-driven estimate; casting shape and strength are not recovered from the source.')
locked=[Path(__file__),a.controls.resolve(),packet,parent/'report.json',parent/'qualification.json',parent/'isolated/manifest.json',STAGE/'lib/cad_build.py',STAGE/'lib/evidence.py']
locked+=sorted({Path(module.__file__).resolve() for module in list(sys.modules.values()) if getattr(module,'__file__',None) and Path(module.__file__).resolve().parent==H and str(module.__file__).endswith('.py')})
inputs={str(f.relative_to(ROOT)):sha(f) for f in sorted(set(locked))};doc=App.openDocument(str(source));defs={};rows={v['name']:v for v in m['occurrences']}
for key,s in changed.items():
 body=doc.getObject(key);target=body.Tip if body.TypeId=='PartDesign::Body' else body;target.Shape=s
 metadata(body,ParameterUpdate='Regenerate with build_transmission_high_brake_front.py',ReconstructionStatus='Estimated rear bridge relieved for source-sized lining hardware; bearing receivers retained.' if key==case_key else 'Rear joints retained; forward fitting and source-counted lining hardware receiving holes installed. Estimated terminal profiles remain conditional.')
records={'long_end':['SNL:8:029','SNL:9:001'],'short_end':['SNL:9:007','SNL:9:010'],'steel_rivet':['SNL:191:009'],'lining_normal_075':['SNL:9:002'],'lining_normal_1':['SNL:9:003','SNL:9:011'],'lining_front_1':['SNL:9:003','SNL:9:011'],'lining_anchor_125':['SNL:9:012'],'lining_brass':['SNL:9:013','SNL:203:020']}
for role,s in new.items():
 body=doc.addObject('PartDesign::Body','Def_HighBrakeFront_'+role);doc.Definitions.addObject(body);body.newObject('PartDesign::Feature','ReconstructedBrakeComponent').Shape=s
 ids=[] if role.endswith('_end') else sorted({pid for v in sources['source_records'] if v['record_id'] in records[role] for pid in v['part_ids']})
 metadata(body,DefinitionKey='high_brake_front_'+role,SourcePartMark='',SourceRecords=records[role],SurveyIds=ids,Representation='assembly',Coverage='reconstruction_trial',ParameterUpdate='Regenerate with build_transmission_high_brake_front.py',ReconstructionStatus='Inferred unnumbered forward fitting, part of the catalogue band identity.' if role.endswith('_end') else 'Catalogue fastener stock and allocation with estimated manufactured/formed head details. Brass source aliases retained in metadata.')
 defs[role]=body
assemblies=[];expected={}
def group(name,parent,pose):
 g=doc.addObject('App::Part',name);parent.addObject(g);g.Uid=str(uuid.uuid5(uuid.NAMESPACE_URL,'markviii:high-brake-front:'+name));g.Placement=pose;assemblies.append(name);return g
for hand in ['Port','Starboard']:
 prefix=hand+'HighSpeedBrake'
 for role in ['long','short']:
  parent_group=doc.getObject(prefix+role.title()+'Assembly');owners=rows[prefix+role.title()+'Band']['owners'];angle=r['details']['placement_angles_rad'][role]
  end=group(prefix+role.title()+'FrontJoint',parent_group,App.Placement(App.Vector(),rotate_theta(angle)).inverse())
  lining=group(prefix+role.title()+'LiningFasteners',parent_group,App.Placement())
  def add(name,role,g,local):
   obj=doc.addObject('App::Link',name);g.addObject(obj);obj.setLink(defs[role]);obj.LinkPlacement=local
   metadata(obj,OccurrenceId=name,Subsystem='Drivetrain',SourceRecords=records[role],Coverage='reconstruction_trial')
   expected[name]=dict(definition=defs[role].Name,frame=list(g.getGlobalPlacement().multiply(local).toMatrix().A),owners=owners+[g.Name])
  add(prefix+role.title()+'FrontEnd',role+'_end',end,App.Placement())
  for n,j in enumerate(details['ends'][role]['steel_joints'],1):add(prefix+role.title()+'FrontSteelRivet'+str(n),'steel_rivet',end,App.Placement(App.Matrix(*j['frame'])))
  for j in details['lining_joints'][role]:add(prefix+role.title()+'LiningFastener'+str(j['index']),j['definition_role'],lining,App.Placement(App.Matrix(*j['local_frame'])))
doc.Root.Label='Powertrain development — high-speed forward fittings and lining fasteners'
doc.Root.RegistrationStatus='Source-counted high-speed lining hardware and inferred forward fittings installed. Free-end pins, levers, adjustment, external anchor supports and stops pending.'
doc.Definitions.Visibility=False;doc.recompute();doc.saveAs(str(native));App.closeDocument(doc.Name)
assert len(expected)==52 and len(new)==8 and len(assemblies)==8
assert sha(source)==r['native_sha256'] and all(sha(ROOT/f)==v for f,v in inputs.items())
frozen=out/'frozen_inputs';frozen.mkdir()
for f in sorted(set(locked)):shutil.copy2(f,frozen/str(f.relative_to(ROOT)).replace('/','__'))
folder=out/'changed_shapes';folder.mkdir()
for k,s in {**{'Def_HighBrakeFront_'+k:v for k,v in new.items()},**changed}.items():s.exportBrep(str(folder/(k+'.brep')))
affected=sorted(set(expected)|{v['name'] for v in m['occurrences'] if v['definition'] in changed})
write(out/'report.json',dict(native_file=native.name,native_sha256=sha(native),source_native=str(source.relative_to(ROOT)),source_native_sha256=sha(source),input_hashes=inputs,controls=c,band_controls=r['band_controls'],rear_controls=r['controls'],rear_details=r['details'],interfaces=r['interfaces'],details=details,expected_new_occurrences=expected,new_assemblies=assemblies,new_definitions=['Def_HighBrakeFront_'+k for k in new],changed_definitions=list(changed),affected_occurrences=affected,expected_physical_occurrences=len(rows)+52,expected_definition_count=len(m['definitions'])+8,expected_assembly_count=len(m['assemblies'])+8,limits=details['limitations'],historical_geometry_qualified=False,installation_qualified=False,standard_assembly_modified=False,packet_complete=False))
print('Saved',len(rows)+52,'physical occurrences; forward fittings and lining hardware populated.',flush=True)
