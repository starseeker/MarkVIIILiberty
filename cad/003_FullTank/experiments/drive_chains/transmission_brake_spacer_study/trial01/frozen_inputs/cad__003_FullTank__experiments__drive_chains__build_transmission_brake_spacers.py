"""Populate four conditional SH687A spacers and revise the estimated M335 spring."""
import argparse
from pathlib import Path
import shutil
import sys
H=Path(__file__).resolve().parent;STAGE=H.parents[1];ROOT=STAGE.parents[1];sys.path[:0]=[str(H),str(STAGE)]
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source',type=Path,default=H/'transmission_brake_stop_study/trial04')
p.add_argument('--controls',type=Path,default=H/'transmission_brake_spacer_study/controls.json')
p.add_argument('--output',type=Path,required=True)
a=p.parse_args();parent=a.source.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
native=out/'PowertrainWithBrakeSpacers.FCStd';assert not native.exists()
prior=read(parent/'report.json');m=read(parent/'isolated/manifest.json');source=parent/prior['native_file']
assert sha(source)==prior['native_sha256']==m['native_sha256']
q=read(parent/'qualification.json');assert q['local_static_checks_passed'] and q['native_sha256']==sha(source)
packet=H/'transmission_brake_spacer_study/sources.json';sources=read(packet);c=read(a.controls)['controls']
assert all(sha(ROOT/f)==digest for f,digest in sources['source_hashes'].items())
import FreeCAD as App
import Part
from lib.cad_build import metadata
from transmission_brake_front_parts import coil
rows={r['name']:r for r in m['occurrences']};sr=m['definitions']['Def_BrakeFront_spring']
assert sha(Path(sr['brep_path']))==sr['brep_sha256']
s=Part.Shape();s.read(sr['brep_path']);box=s.optimalBoundingBox(False,False)
assert abs(box.ZMin)<1e-5
old_height=box.ZMax # bounded kernel uncertainty removed by comparison to retained construction datum below
front=read(H/'transmission_brake_front_study/trial01/report.json');fc=front['controls']
assert abs(old_height-front['details']['spring']['installed_height_mm'])<1e-5
old_height=front['details']['spring']['installed_height_mm'];height=old_height-c['spacer_length']
assert c['spacer_bore_radius']>fc['screw_radius'] and c['spacer_outer_diameter']/2>c['spacer_bore_radius']
spring,curve,details=coil(height,fc)
spacer=Part.makeCylinder(c['spacer_outer_diameter']/2,c['spacer_length']).cut(Part.makeCylinder(c['spacer_bore_radius'],c['spacer_length']))
assert all(v.isValid() and len(v.Solids)==1 and v.Solids[0].isClosed() for v in [spring,spacer])
locked=[Path(__file__),H/'transmission_brake_front_parts.py',H/'transmission_brake_front_study/trial01/report.json',
 a.controls.resolve(),packet,parent/'report.json',parent/'qualification.json',parent/'isolated/manifest.json',Path(sr['brep_path']),STAGE/'lib/cad_build.py',STAGE/'lib/evidence.py']
inputs={str(f.relative_to(ROOT)):sha(f) for f in locked}
doc=App.openDocument(str(source));body=doc.Def_BrakeFront_spring;body.Tip.Shape=spring
metadata(body,SpacerRevision='Shortened estimated spring for conditional SH687A spacer at swivel end; printed stock-length assignment unproved.',ParameterUpdate='Regenerate with build_transmission_brake_spacers.py')
doc.BrakeFrontSpringCenterline.Shape=curve
metadata(doc.BrakeFrontSpringCenterline,SpacerRevision='Updated sweep centreline for shortened estimated spring.')
definition=doc.addObject('PartDesign::Body','Def_BrakeSpringSpacer');doc.Definitions.addObject(definition)
definition.newObject('PartDesign::Feature','ReconstructedSpringSpacer').Shape=spacer
metadata(definition,DefinitionKey='transmission_brake_adjusting_spring_spacer',SourcePartMark='SH687A',SourceRecords=['SNL:218:013','SNL:252:026'],SurveyIds=['P_612e0e94ea39e728'],Representation='assembly',Coverage='reconstruction_trial',
 ParameterUpdate='Regenerate with build_transmission_brake_spacers.py',ReconstructionStatus='Four source-identified spacers; annular stock dimensions, bore and swivel-side location are a documented conditional hypothesis.')
new={};revised={};children={}
for hand in ['Port','Starboard']:
 for role in ['LowSpeed','Track']:
  prefix=hand+role+'Brake';old=rows[prefix+'AdjustingSpring'];owner=doc.getObject(old['owners'][-1]);pose=App.Placement(App.Matrix(*old['frame'])).multiply(App.Placement(App.Vector(0,0,height),App.Rotation()))
  name=prefix+'AdjustingSpringSpacer';obj=doc.addObject('App::Link',name);owner.addObject(obj);obj.setLink(definition)
  obj.LinkPlacement=owner.getGlobalPlacement().inverse().multiply(pose)
  metadata(obj,OccurrenceId=name,Subsystem='Drivetrain',SourceRecords=['SNL:218:013','SNL:252:026'],ReconstructionStatus='Conditional position at swivel end; spring shortened, shoulder and external mechanism retained.')
  new[name]=dict(definition=definition.Name,frame=list(pose.toMatrix().A),owners=old['owners'])
  revised[old['name']]={k:old[k] for k in ['definition','frame','owners']};children.setdefault(owner.Name,[]).append(name)
doc.Root.Label='Powertrain development — conditional brake spring spacers'
doc.Root.RegistrationStatus='Four SH687A spacers represented; bore/stock interpretation and swivel-side position estimated. Inherited source and service limitations retained.'
doc.Definitions.Visibility=False;doc.recompute();doc.saveAs(str(native));App.closeDocument(doc.Name)
assert sha(source)==prior['native_sha256'] and all(sha(ROOT/f)==digest for f,digest in inputs.items())
frozen=out/'frozen_inputs';frozen.mkdir()
for f in locked:shutil.copy2(f,frozen/str(f.relative_to(ROOT)).replace('/','__'))
folder=out/'changed_shapes';folder.mkdir()
for name,shape in [('Def_BrakeSpringSpacer',spacer),('Def_BrakeFront_spring',spring),('BrakeFrontSpringCenterline',curve)]:shape.exportBrep(str(folder/(name+'.brep')))
write(out/'report.json',dict(native_file=native.name,native_sha256=sha(native),source_native=str(source.relative_to(ROOT)),source_native_sha256=sha(source),input_hashes=inputs,controls=c,spring_controls=fc,
 details=dict(old_spring_height_mm=old_height,new_spring_height_mm=height,spring=details),
 changed_definitions=['Def_BrakeFront_spring'],new_definitions=['Def_BrakeSpringSpacer'],nonphysical_features=['BrakeFrontSpringCenterline'],
 expected_new_occurrences=new,expected_revised_occurrences=revised,added_children=children,new_assemblies=[],
 affected_occurrences=sorted(set(new)|set(revised)),expected_physical_occurrences=len(m['occurrences'])+4,
 expected_definition_count=len(m['definitions'])+1,expected_assembly_count=len(m['assemblies']),
 historical_geometry_qualified=False,installation_qualified=False,standard_assembly_modified=False,
 inherited_limits=q['open_issues']))
print('Saved four SH687A spacer occurrences and shortened four estimated springs; historical placement remains conditional.',flush=True)
