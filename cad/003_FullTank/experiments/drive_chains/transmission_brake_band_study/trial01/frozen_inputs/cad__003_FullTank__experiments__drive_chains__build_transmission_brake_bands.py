"""Install the handbook segmented brake variant in the qualified transmission."""
import argparse
from pathlib import Path
import shutil
import sys
import uuid

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--controls',type=Path,default=HERE/'transmission_brake_band_study/controls.json')
a=p.parse_args();parent=a.source.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
native=out/'PowertrainWithBrakeBands.FCStd';assert not native.exists()
pr=read(parent/'report.json');source=parent/pr['native_file'];m=read(parent/'isolated/manifest.json')
assert sha(source)==pr['native_sha256']==m['native_sha256']
assert read(parent/'independent_checks.json')['local_suspension_checks_passed']
assert read(parent/'definition_preservation_checks.json')['passed']
packet=HERE/'transmission_brake_band_study/sources.json';sources=read(packet)
assert all(sha(ROOT/f)==digest for f,digest in sources['source_hashes'].items())
locked=[Path(__file__),a.controls.resolve(),packet,HERE/'transmission_brake_band_parts.py',
    HERE/'transmission_frame_joint_parts.py',STAGE/'lib/cad_build.py',STAGE/'lib/evidence.py',
    parent/'report.json',parent/'independent_checks.json',parent/'definition_preservation_checks.json']
inputs={str(v.relative_to(ROOT)):sha(v) for v in locked}
import FreeCAD as App
import Part
from lib.cad_build import metadata
from transmission_brake_band_parts import parts,revised_land,rotate_theta
V=App.Vector;rows={v['name']:v for v in m['occurrences']};c=read(a.controls)['controls']
shapes,details,curves=parts(c);changed={};additions={};lands={}
for role,name in [('low','Def_TransmissionCore_brake_case'),('track','Def_Output_drum')]:
    record=m['definitions'][name];f=Path(record['brep_path']);assert sha(f)==record['brep_sha256']
    s=Part.Shape();s.read(str(f))
    changed[name],additions[name],lands[role]=revised_land(s,c[role]['inner_radius'],c[role]['width'],c)
    lands[role]['definition']=name
doc=App.openDocument(str(source))
for name,s in changed.items():
    body=doc.getObject(name);body.Tip.Shape=s
    metadata(body,BrakeLandRevision='Printed HB97/98 lining radius; added outer land with estimated shoulders. Original interior and end strips retained.',
        BrakeLandUpdate='Regenerate with build_transmission_brake_bands.py')
definitions={};records={}
for role,mark,rid in [
    ('low_band','M344','HB:nomenclature:207:043'),('low_lining','M346','HB:nomenclature:207:044'),
    ('track_band','M349','HB:nomenclature:207:046'),('track_lining','M351','HB:nomenclature:207:047'),
    ('copper_rivet','Copper lining rivet','SNL:192:010')]:
    body=doc.addObject('PartDesign::Body','Def_BrakeBand_'+role);doc.Definitions.addObject(body)
    body.newObject('PartDesign::Feature','ReconstructedBrakeComponent').Shape=shapes[role]
    record=next(v for v in sources['source_records'] if v['record_id']==rid);records[role]=rid
    metadata(body,DefinitionKey='brake_band_'+role,SourcePartMark=mark,SourceRecords=[rid],SurveyIds=record['part_ids'],
        Representation='assembly',Coverage='partial' if role.endswith('band') else 'reconstruction',
        ReconstructionStatus='HB segmented lining variant. Printed lining dimensions; estimated steel stock, joints and rivet stock. Band ears and linkage pending.',
        ParameterUpdate='Regenerate with build_transmission_brake_bands.py')
    definitions[role]=body
assemblies=[]
def group(name,parent,pose=None):
    obj=doc.addObject('App::Part',name);parent.addObject(obj)
    obj.Uid=str(uuid.uuid5(uuid.NAMESPACE_URL,'markviii:transmission-brake-bands:'+name))
    if pose is not None:obj.Placement=pose
    assemblies.append(obj.Name);return obj
root=group('TransmissionBrakeBands',doc.Root);expected={};interfaces={}
def link(name,role,parent,local,owners):
    obj=doc.addObject('App::Link',name);parent.addObject(obj);obj.setLink(definitions[role]);obj.LinkPlacement=local
    metadata(obj,OccurrenceId=name,Subsystem='Drivetrain',SourceRecords=[records[role]])
    expected[name]=dict(definition=definitions[role].Name,
        frame=list(parent.getGlobalPlacement().multiply(local).toMatrix().A),owners=owners)
for hand in ['Port','Starboard']:
    for role,label,receiver in [('low','LowSpeed',hand+'TransmissionCore_brake_case'),('track','Track',hand+'TransmissionOutput_drum')]:
        row=rows[receiver];world=App.Placement(App.Matrix(*row['frame']))
        center=world.multVec(V(0,lands[role]['axial_center_mm'],0))
        name=hand+label+'Brake';brake=group(name,root,App.Placement(center,App.Rotation()))
        interfaces[name]=dict(role=role,receiver=receiver,center_mm=list(center),radius_mm=c[role]['inner_radius'])
        for half,rotation in [('Upper',App.Rotation()),('Lower',App.Rotation(V(1,0,0),180))]:
            hg=group(name+half,brake,App.Placement(V(),rotation))
            owners=['Root',root.Name,brake.Name,hg.Name]
            link(hg.Name+'Band',role+'_band',hg,App.Placement(),owners)
            for n,angle in enumerate(details['brakes'][role]['segment_angles_rad'],1):
                sg=group(hg.Name+'Segment'+str(n),hg,App.Placement(V(),rotate_theta(angle)))
                so=owners+[sg.Name];link(sg.Name+'Lining',role+'_lining',sg,App.Placement(),so)
                for index,hole in enumerate(details['brakes'][role]['holes'],1):
                    link(sg.Name+'Rivet'+str(index),'copper_rivet',sg,App.Placement(App.Matrix(*hole['frame'])),so)
doc.Root.Label='Powertrain development — segmented transmission brake bands'
doc.Root.RegistrationStatus='HB segmented brake linings and riveted steel bands; end ears, anchors, linkage and support fastening incomplete'
doc.Definitions.Visibility=False;doc.recompute();doc.saveAs(str(native));App.closeDocument(doc.Name)
assert len(expected)==248 and len(assemblies)==37
assert sha(source)==pr['native_sha256'] and all(sha(ROOT/f)==digest for f,digest in inputs.items())
frozen=out/'frozen_inputs';frozen.mkdir()
for f in locked:shutil.copy2(f,frozen/str(f.relative_to(ROOT)).replace('/','__'))
breps=out/'changed_shapes';breps.mkdir()
for name,s in dict(changed,**{'Def_BrakeBand_'+k:v for k,v in shapes.items()}).items():s.exportBrep(str(breps/(name+'.brep')))
for name,s in additions.items():s.exportBrep(str(breps/(name+'_added_land.brep')))
for role,s in curves.items():s.exportBrep(str(breps/(role+'_lining_neutral_curve.brep')))
affected=[n for n,v in rows.items() if v['definition'] in changed]+list(expected)
write(out/'report.json',dict(native_file=native.name,native_sha256=sha(native),source_native=str(source.relative_to(ROOT)),
    source_native_sha256=sha(source),input_hashes=inputs,controls=c,details=details,lands=lands,interfaces=interfaces,
    changed_definitions=sorted(changed),new_definitions=sorted('Def_BrakeBand_'+k for k in shapes),
    expected_new_occurrences=expected,new_assemblies=assemblies,affected_occurrences=sorted(affected),
    expected_physical_occurrences=len(rows)+len(expected),expected_definition_count=len(m['definitions'])+len(shapes),
    expected_assembly_count=len(m['assemblies'])+len(assemblies),historical_geometry_qualified=False,
    installation_qualified=False,ears_and_linkage_pending=True,standard_assembly_modified=False))
print('Saved',len(rows)+len(expected),'physical occurrences;',len(affected),'affected.',flush=True)
