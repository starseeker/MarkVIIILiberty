"""Populate a source-counted subset of frame rivets on explicitly inferred joints."""
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
p.add_argument('--controls',type=Path,default=HERE/'transmission_frame_joint_study/controls.json')
a=p.parse_args();parent=a.source.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
native=out/'PowertrainWithFrameJoints.FCStd';assert not native.exists()
pr=read(parent/'report.json');source=parent/pr['native_file'];m=read(parent/'isolated/manifest.json')
assert sha(source)==pr['native_sha256']==m['native_sha256']
assert read(parent/'independent_checks.json')['local_joint_checks_passed']
assert read(parent/'definition_preservation_checks.json')['passed']
c=read(a.controls)['controls'];source_packet=HERE/'transmission_frame_joint_study/sources.json'
assert all(sha(ROOT/f)==digest for f,digest in read(source_packet)['source_hashes'].items())
locked=[Path(__file__),a.controls.resolve(),source_packet,HERE/'transmission_frame_joint_parts.py',
        HERE/'transmission_support_parts.py',STAGE/'lib/cad_build.py',STAGE/'lib/evidence.py',
        parent/'report.json',parent/'independent_checks.json',parent/'definition_preservation_checks.json']
inputs={str(p.relative_to(ROOT)):sha(p) for p in locked}
import FreeCAD as App
import Part
from transmission_frame_joint_parts import rivet,formed_gusset
from transmission_support_parts import box
from lib.cad_build import metadata
V=App.Vector;rows={r['name']:r for r in m['occurrences']}
def load(name):
    d=m['definitions'][name];p=Path(d['brep_path']);assert sha(p)==d['brep_sha256']
    s=Part.Shape();s.read(str(p));assert s.Placement.isIdentity();return s
def pose(name):return App.Placement(App.Matrix(*rows[name]['frame']))
rear=-c['channel_depth']+c['channel_stock'];t=c['gusset_stock'];s=c['channel_stock']
changed={};gusset_names=[n for n in m['definitions'] if n.startswith('Def_TransmissionFrame_') and '_gusset_' in n]
for name in gusset_names:
    sign=1 if name.endswith('_left') else -1
    shape=formed_gusset(load(name),sign,c)
    for dx,dy in c['rivet_points_from_rear']:
        shape=shape.cut(Part.makeCylinder(c['rivet_diameter']/2+c['hole_radial_clearance'],t+2,
            V(rear+dx,-sign*dy,-t-1)))
    changed[name]=shape
inner_y=abs(rows['TransmissionFrame_LeftInnerAngle']['frame'][7])
diaphragm='Def_TransmissionFrame_middle_diaphragm';old=load(diaphragm)
half=inner_y-c['angle_stock']
changed[diaphragm]=box(rear+c['angle_stock'],rear+c['angle_stock']+c['diaphragm_stock'],
    -half,half,old.BoundBox.ZMin,old.BoundBox.ZMax)
for key in ['top','bottom']:changed['Def_TransmissionFrame_'+key+'_channel']=load('Def_TransmissionFrame_'+key+'_channel')
shape,detail=rivet(c['rivet_diameter'],c['rivet_stock_length'],s+t,c['rivet_head_ratio'])
new_name='Def_FrameJoint_rivet_11_16_1_1_2';joints=[]
for name,row in rows.items():
    if row['definition'] not in gusset_names:continue
    sign=1 if row['definition'].endswith('_left') else -1;gp=pose(name)
    member='top' if 'Top' in name else 'bottom';channel='TransmissionFrame_'+member.title()+'Channel'
    key='Def_TransmissionFrame_'+member+'_channel';cp=pose(channel)
    for i,(dx,dy) in enumerate(c['rivet_points_from_rear']):
        point=V(rear+dx,-sign*dy,s)
        world=gp.multiply(App.Placement(point,App.Rotation(V(1,0,0),180)))
        tool=Part.makeCylinder(c['rivet_diameter']/2+c['hole_radial_clearance'],s+t+2,
            V(point.x,point.y,-t-1))
        tool.Placement=cp.inverse().multiply(gp);changed[key]=changed[key].cut(tool)
        joints.append(dict(name=name+'Rivet'+str(i+1),gusset=name,channel=channel,
            local_xy_mm=[point.x,point.y],frame=list(world.toMatrix().A)))
assert len(joints)==32
for name,value in changed.items():assert value.isValid() and len(value.Solids)==1,name
doc=App.openDocument(str(source))
for name,value in changed.items():
    target=doc.getObject(name);(target.Tip if target.TypeId=='PartDesign::Body' else target).Shape=value
    metadata(target,FrameJointRevision='Formed return/diaphragm overlap and rivet pattern are mechanical reconstruction hypotheses; transmission_frame_joint_study/controls.json')
body=doc.addObject('PartDesign::Body',new_name);doc.Definitions.addObject(body)
body.newObject('PartDesign::Feature','ReconstructedFrameRivet').Shape=shape
record=next(r for r in read(source_packet)['source_records'] if r['record_id']=='SNL:97:006')
metadata(body,DefinitionKey='frame_rivet_11_16_by_1_1_2',SourcePartMark='',SourceRecords=['SNL:97:006'],
    SurveyIds=record['part_ids'],Representation='assembly',
    ReconstructionStatus='Printed diameter, stock length and count; estimated upset head and joint allocation',
    ParameterUpdate='Regenerate with transmission_frame_joint_parts.py')
def assembly(name,parent):
    obj=doc.addObject('App::Part',name);parent.addObject(obj)
    obj.Uid=str(uuid.uuid5(uuid.NAMESPACE_URL,'markviii:transmission-frame-joints:'+name))
    return obj
root=assembly('FrameGussetRivets',doc.TransmissionMountingFrame);groups={};expected={}
for j in joints:
    key=j['gusset']
    if key not in groups:groups[key]=assembly(key+'Joints',root)
    group=groups[key];obj=doc.addObject('App::Link',j['name']);group.addObject(obj);obj.setLink(body)
    world=App.Placement(App.Matrix(*j['frame']));obj.LinkPlacement=group.getGlobalPlacement().inverse().multiply(world)
    metadata(obj,OccurrenceId=j['name'],Subsystem='Drivetrain',SourceRecords=['SNL:97:006'])
    expected[j['name']]=dict(definition=new_name,frame=j['frame'],owners=['Root','TransmissionMountingFrame',root.Name,group.Name])
doc.Root.Label='Powertrain development — formed frame gussets and channel riveting trial'
doc.Root.RegistrationStatus='Thirty-two frame rivets populated; gusset returns, diaphragm overlap and rivet allocation are hypotheses'
doc.Definitions.Visibility=False;doc.recompute();doc.saveAs(str(native));App.closeDocument(doc.Name)
assert sha(source)==pr['native_sha256'] and all(sha(ROOT/k)==v for k,v in inputs.items())
frozen=out/'frozen_inputs';frozen.mkdir()
for p in locked:shutil.copy2(p,frozen/str(p.relative_to(ROOT)).replace('/','__'))
definitions=out/'changed_shapes';definitions.mkdir()
for name,value in dict(changed,**{new_name:shape}).items():value.exportBrep(str(definitions/(name+'.brep')))
affected=[n for n,r in rows.items() if r['definition'] in changed]+list(expected)
write(out/'report.json',dict(native_file=native.name,native_sha256=sha(native),source_native=str(source.relative_to(ROOT)),
    source_native_sha256=sha(source),input_hashes=inputs,controls=c,rivet=detail,joints=joints,
    changed_definitions=sorted(changed),new_definitions=[new_name],expected_new_occurrences=expected,
    new_assemblies=[root.Name]+[v.Name for v in groups.values()],affected_occurrences=sorted(affected),
    expected_physical_occurrences=len(rows)+32,expected_definition_count=len(m['definitions'])+1,
    expected_assembly_count=len(m['assemblies'])+9,diaphragm_half_width_mm=half,
    source_rivet_count=78,populated_rivet_count=32,remaining_rivet_count=46,
    historical_joint_layout_qualified=False,installation_qualified=False,standard_assembly_modified=False))
print('Saved',len(rows)+32,'physical occurrences,',len(affected),'affected.',flush=True)
