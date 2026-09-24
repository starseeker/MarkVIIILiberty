"""Add four identified suspension brackets and two stops to the saved frame."""
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
p.add_argument('--controls',type=Path,default=HERE/'transmission_brake_suspension_study/controls.json')
a=p.parse_args();parent=a.source.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
native=out/'PowertrainWithBrakeSuspension.FCStd';assert not native.exists()
pr=read(parent/'report.json');source=parent/pr['native_file'];m=read(parent/'isolated/manifest.json')
assert sha(source)==pr['native_sha256']==m['native_sha256']
assert read(parent/'independent_checks.json')['local_frame_checks_passed']
assert read(parent/'definition_preservation_checks.json')['passed']
packet=HERE/'transmission_brake_suspension_study/sources.json';sources=read(packet)
assert all(sha(ROOT/f)==digest for f,digest in sources['source_hashes'].items())
locked=[Path(__file__),a.controls.resolve(),packet,HERE/'transmission_brake_suspension_parts.py',
        HERE/'transmission_support_parts.py',STAGE/'lib/cad_build.py',STAGE/'lib/evidence.py',
        parent/'report.json',parent/'independent_checks.json',parent/'definition_preservation_checks.json']
inputs={str(v.relative_to(ROOT)):sha(v) for v in locked}
import FreeCAD as App
import Part
from lib.cad_build import metadata
from transmission_brake_suspension_parts import dimensions,parts
V=App.Vector;rows={v['name']:v for v in m['occurrences']};c=read(a.controls)['controls']
top=rows['TransmissionFrame_TopChannel']['frame'];bottom=rows['TransmissionFrame_BottomChannel']['frame']
d=dimensions(c,top[11]-bottom[11]);shapes=parts(c,d)
def shape(name):
    row=rows[name];record=m['definitions'][row['definition']];f=Path(record['brep_path']);assert sha(f)==record['brep_sha256']
    s=Part.Shape();s.read(str(f));s.Placement=App.Placement(App.Matrix(*row['frame']));return s
def friction_face(name):
    candidates=[f for f in shape(name).Faces if isinstance(f.Surface,Part.Cylinder) and abs(abs(f.Surface.Axis.y)-1)<1e-7]
    face=max(candidates,key=lambda f:(f.Surface.Radius,f.Area));b=face.BoundBox
    return dict(occurrence=name,radius_mm=face.Surface.Radius,axis_center_mm=list(face.Surface.Center),
                axial_limits_mm=[b.YMin,b.YMax],center_y_mm=(b.YMin+b.YMax)/2)
interfaces={};placements={}
for hand,sign in [('Port',1),('Starboard',-1)]:
    for role,drum in [('LowSpeed',hand+'TransmissionCore_brake_case'),('Track',hand+'TransmissionOutput_drum')]:
        key=hand+role;interface=friction_face(drum);y=interface['center_y_mm']+sign*c['axial_offset'];interfaces[key]=interface
        placements[key+'Bracket']=dict(role='bracket',group=key+'BrakeSupport',
            frame=list(App.Placement(V(top[3]+d['pin_x_relative_channel_mm'],y,top[11]-d['pin_drop_mm']),App.Rotation()).toMatrix().A))
        if role=='Track':
            placements[key+'Stop']=dict(role='stop',group=key+'BrakeSupport',
                frame=list(App.Placement(V(top[3],y,top[11]),App.Rotation()).toMatrix().A))
axis=interfaces['PortLowSpeed']['axis_center_mm'];sx=d['scale_x_mm_px'];sz=d['scale_z_mm_px']
picked=c['source_axis_px']
axis_prediction=[top[3]-(picked[0]-c['source_channel_x_px'][0])*sx,top[11]-(picked[1]-c['source_channel_web_z_px'][0])*sz]
source_residual=dict(predicted_axis_xz_mm=axis_prediction,actual_axis_xz_mm=[axis[0],axis[2]],
    residual_xz_mm=[axis_prediction[0]-axis[0],axis_prediction[1]-axis[2]],
    interpretation='Held-out source shaft center disagrees with retained model registration; no physical frame is moved to hide it.')
doc=App.openDocument(str(source));definitions={}
for role,(mark,rid) in dict(bracket=('M338','SNL:96:017'),stop=('M385','SNL:96:018')).items():
    body=doc.addObject('PartDesign::Body','Def_BrakeSuspension_'+role);doc.Definitions.addObject(body)
    body.newObject('PartDesign::Feature','ReconstructedBrakeSupport').Shape=shapes[role]
    record=next(v for v in sources['source_records'] if v['record_id']==rid)
    metadata(body,DefinitionKey='brake_suspension_'+role,SourcePartMark=mark,SourceRecords=[rid],
        SurveyIds=record['part_ids'],Representation='assembly',Coverage='partial',
        ReconstructionStatus='Source identity/count; registered side profile and estimated transverse dimensions. Receiving fasteners and brake linkage pending.',
        ParameterUpdate='Regenerate with build_transmission_brake_suspension.py')
    definitions[role]=body
def group(name,parent):
    obj=doc.addObject('App::Part',name);parent.addObject(obj)
    obj.Uid=str(uuid.uuid5(uuid.NAMESPACE_URL,'markviii:transmission-brake-suspension:'+name));return obj
root=group('TransmissionBrakeSuspension',doc.TransmissionMountingFrame);groups={};expected={}
for name,v in placements.items():
    key=v['group']
    if key not in groups:groups[key]=group(key,root)
    owner=groups[key];body=definitions[v['role']];link=doc.addObject('App::Link',name);owner.addObject(link);link.setLink(body)
    link.LinkPlacement=owner.getGlobalPlacement().inverse().multiply(App.Placement(App.Matrix(*v['frame'])))
    metadata(link,OccurrenceId=name,Subsystem='Drivetrain',SourceRecords=['SNL:96:017' if v['role']=='bracket' else 'SNL:96:018'])
    expected[name]=dict(definition=body.Name,frame=v['frame'],owners=['Root','TransmissionMountingFrame',root.Name,owner.Name])
assemblies=[root.Name]+[v.Name for v in groups.values()]
doc.Root.Label='Powertrain development — transmission brake suspension geometry'
doc.Root.RegistrationStatus='Four M338 brackets and two M385 stops provisionally seated; attachment and brake linkage incomplete'
doc.Definitions.Visibility=False;doc.recompute();doc.saveAs(str(native));App.closeDocument(doc.Name)
assert sha(source)==pr['native_sha256'] and all(sha(ROOT/f)==digest for f,digest in inputs.items())
frozen=out/'frozen_inputs';frozen.mkdir()
for f in locked:shutil.copy2(f,frozen/str(f.relative_to(ROOT)).replace('/','__'))
breps=out/'new_shapes';breps.mkdir()
for role,s in shapes.items():s.exportBrep(str(breps/('Def_BrakeSuspension_'+role+'.brep')))
write(out/'report.json',dict(native_file=native.name,native_sha256=sha(native),source_native=str(source.relative_to(ROOT)),
    source_native_sha256=sha(source),input_hashes=inputs,controls=c,dimensions=d,interfaces=interfaces,
    source_axis_residual=source_residual,changed_definitions=[],new_definitions=['Def_BrakeSuspension_bracket','Def_BrakeSuspension_stop'],
    expected_new_occurrences=expected,new_assemblies=assemblies,affected_occurrences=sorted(expected),
    expected_physical_occurrences=len(rows)+6,expected_definition_count=len(m['definitions'])+2,
    expected_assembly_count=len(m['assemblies'])+len(assemblies),historical_geometry_qualified=False,
    installation_qualified=False,fastening_pending=True,standard_assembly_modified=False))
print('Saved',len(rows)+6,'occurrences; held-out source-axis residual',source_residual['residual_xz_mm'],flush=True)
