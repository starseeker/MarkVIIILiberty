"""Add twenty source-counted MX1 joints to the saved powertrain development model."""
import argparse
import copy
from pathlib import Path
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile

HERE=Path(__file__).resolve().parent
STAGE=HERE.parents[1]
ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib.evidence import read,write,sha

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source',type=Path,required=True,help='Saved casing trial directory')
p.add_argument('--output',type=Path,required=True)
p.add_argument('--controls',type=Path,default=HERE/'transmission_bracket_mount_controls.json')
a=p.parse_args()
parent,out=a.source.resolve(),a.output.resolve()
out.mkdir(parents=True,exist_ok=True)
native=out/'PowertrainWithBracketMounts.FCStd'
assert not native.exists(),'Use a fresh output directory.'
pr=read(parent/'report.json');source=parent/pr['native_file']
m=read(parent/'isolated/manifest.json');q=read(parent/'independent_checks.json')
assert q['local_casing_checks_passed'] and sha(source)==pr['native_sha256']==m['native_sha256']==q['native_sha256']
rows={v['name']:v for v in m['occurrences']}
c=read(a.controls)['controls']
mount_report=read(HERE/'transmission_case_mount_trial_build/report.json')
mount=mount_report['controls'];pc=mount_report['pin_controls']
support_report=read(HERE/'transmission_support_clearance_build/report.json')
frame_report=read(HERE/'transmission_frame_clearance_build/report.json')
core_report=read(HERE/'transmission_core_build/report.json')
fc={k:v['value'] for k,v in read(HERE/'transmission_frame_clearance_build/inputs/transmission_frame_controls.json')['controls'].items()}
sc={k:v['value'] for k,v in read(HERE/'transmission_frame_clearance_build/inputs/transmission_support_controls.json')['controls'].items()}
paths=[Path(__file__),a.controls.resolve(),parent/'report.json',parent/'independent_checks.json',
       HERE/'transmission_bracket_mount_parts.py',HERE/'transmission_bracket_mount_sources.json',
       HERE/'transmission_case_mount_trial_build/report.json',
       HERE/'transmission_support_clearance_build/report.json',
       HERE/'transmission_frame_clearance_build/report.json',HERE/'transmission_core_build/report.json',
       HERE/'transmission_frame_clearance_build/inputs/transmission_frame_controls.json',
       HERE/'transmission_frame_clearance_build/inputs/transmission_support_controls.json']
paths += [HERE/name for name in ['transmission_support_parts.py','transmission_frame_parts.py',
          'powertrain_frame_registration_parts.py','transmission_stud_parts.py',
          'transmission_input_installation_parts.py','transmission_input_parts.py',
          'transmission_output_parts.py','transmission_core_parts.py']]
paths += [STAGE/'lib/cad_build.py',STAGE/'lib/evidence.py']
locked={str(path.relative_to(ROOT)):sha(path) for path in paths}

import FreeCAD as App
import Part
from lib.cad_build import metadata
from transmission_frame_parts import revised_bracket
from powertrain_frame_registration_parts import replay_features
from transmission_bracket_mount_parts import parts
from transmission_stud_parts import cylinder_x

baselines=out/'baseline_shapes';baselines.mkdir(exist_ok=True)
archives={}
def archived(folder,native_name,definition,digest,label):
    path=HERE/folder/native_name;assert sha(path)==digest
    with zipfile.ZipFile(path) as z:
        tree=ET.fromstring(z.read('Document.xml'))
        prop=tree.find('./ObjectData/Object[@name="'+definition+'"]/Properties/Property[@name="Shape"]/Part')
        data=z.read(prop.get('file'))
    target=baselines/(label+'.brep');target.write_bytes(data)
    shape=Part.Shape();shape.read(str(target))
    archives[label]=dict(native=str(path.relative_to(ROOT)),native_sha256=digest,
                         definition=definition,brep_sha256=sha(target))
    return shape

def saved(name):
    d=m['definitions'][name];path=Path(d['brep_path']);assert sha(path)==d['brep_sha256']
    shape=Part.Shape();shape.read(str(path));assert shape.Placement.isIdentity()
    return shape

name='Def_FixedBearing_inner_bracket'
minimal=archived('transmission_support_clearance_build','TransmissionSupportCandidate.FCStd',
    name,support_report['native_sha256'],'inner_minimal')
old_base=archived('transmission_frame_clearance_build','TransmissionFrameCandidate.FCStd',
    name,frame_report['native_sha256'],'inner_original_base')
dimensions=copy.deepcopy(support_report['dimensions'])
original_axis=App.Vector(*core_report['shaft_axis_world_mm'])
old_regenerated,_=revised_bracket(minimal,'inner',fc,sc,dimensions,original_axis)
baseline=dict(missing_mm3=old_base.cut(old_regenerated).Volume,
              added_mm3=old_regenerated.cut(old_base).Volume)
assert abs(baseline['missing_mm3'])<1e-5 and abs(baseline['added_mm3'])<1e-5,baseline
shift=dimensions['outer']['foot_aft_x_mm']-dimensions['inner']['foot_aft_x_mm']
assert abs(shift-read(a.controls)['casting_revision']['shift_x_mm'])<1e-8
dimensions['inner']['foot_aft_x_mm']+=shift
dimensions['inner']['foot_front_x_mm']+=shift
new_base,cast_details=revised_bracket(minimal,'inner',fc,sc,dimensions,original_axis)
inner,feature_details=replay_features(old_base,new_base,saved(name))
new_base.exportBrep(str(baselines/'inner_revised_base.brep'))
inner.exportBrep(str(baselines/'inner_before_joint_bores.brep'))
brackets=dict(inner=inner,outer=saved('Def_FixedBearing_outer_bracket'))
channels={key:saved('Def_TransmissionFrame_'+key+'_channel') for key in ['top','bottom']}
defs,revised,revised_channels,details=parts(c,mount,pc,brackets,channels,dimensions)

placements={};joints=[]
for hand in ['Port','Starboard']:
    for role in ['inner','outer']:
        receiver=hand+'FixedBearing_'+role+'_bracket'
        pose=App.Placement(App.Matrix(*rows[receiver]['frame']))
        for joint in [j for j in details['joints'] if j['role']==role]:
            name=hand+role.title()+joint['end']+'MX1'+str(joint['index']+1)
            member='top' if joint['end']=='Upper' else 'bottom'
            channel_name='TransmissionFrame_'+('Top' if member=='top' else 'Bottom')+'Channel'
            channel_pose=App.Placement(App.Matrix(*rows[channel_name]['frame']))
            world={k:pose.multiply(App.Placement(App.Matrix(*v))) for k,v in joint['placements'].items()}
            channel_tool=cylinder_x(c['bolt_diameter']/2+c['receiver_radial_clearance'],
                mount['frame_front_x']-mount['flange_root_stock']-1,mount['frame_front_x']+1,
                joint['y_local_mm'],joint['z_local_mm'])
            channel_tool.Placement=channel_pose.inverse().multiply(pose)
            revised_channels[member]=revised_channels[member].cut(channel_tool)
            placements.update({name+'_'+k:v for k,v in world.items()})
            joints.append(dict(name=name,hand=hand,role=role,receiver=receiver,
                channel=channel_name,source_joint=joint,
                world_frames={k:list(v.toMatrix().A) for k,v in world.items()}))
assert len(joints)==20 and len(placements)==80
changed={**{'Def_FixedBearing_'+key+'_bracket':v for key,v in revised.items()},
         **{'Def_TransmissionFrame_'+key+'_channel':v for key,v in revised_channels.items()}}
for name,shape in changed.items():
    assert shape.isValid() and len(shape.Solids)==1,name
    shape.exportBrep(str(baselines/(name+'_rebuilt.brep')))

doc=App.openDocument(str(source))
for name,shape in changed.items():
    target=doc.getObject(name);(target.Tip if target.TypeId=='PartDesign::Body' else target).Shape=shape
references={'bolt':('MX1','P_1bb060b070d00986','SNL:28:003'),
            'cotter':('','P_1871cd216f04cd35','SNL:28:005'),
            'nut':('','P_c3bb5fc9299bfab2','SNL:28:004'),
            'washer':('MX13','P_6e5a15454080a055','SNL:267:006')}
body_names={'nut':'Def_TransmissionCap_nut','washer':'Def_CaseMount_washer'}
for key,shape in defs.items():
    body=doc.addObject('PartDesign::Body','Def_BracketMount_'+key);doc.Definitions.addObject(body)
    body.newObject('PartDesign::Feature','ReconstructedPart').Shape=shape
    mark,pid,record=references[key]
    metadata(body,DefinitionKey='transmission_bracket_mount_'+key,SourcePartMark=mark,
        SourceRecords=[record],SurveyIds=[pid],Representation='assembly',
        ReconstructionStatus='Source-counted hardware with documented estimated geometry; interface layout remains a trial',
        ParameterUpdate='Regenerate with transmission_bracket_mount_parts.py and controls')
    body_names[key]=body.Name
new_assemblies=[];groups={};expected={}
for joint in joints:
    owner_name=rows[joint['receiver']]['owners'][-1]
    owner=doc.getObject(owner_name)
    if owner_name not in groups:
        group=doc.addObject('App::Part',joint['hand']+joint['role'].title()+'BracketMounts')
        owner.addObject(group);groups[owner_name]=group
        metadata(group,Scope='MX1 bracket-to-channel joints; distribution and common casting pad plane inferred')
        new_assemblies.append(group.Name)
    assembly=doc.addObject('App::Part',joint['name']);groups[owner_name].addObject(assembly)
    metadata(assembly,SourceRecords=['SNL:28:001','SNL:96:012'],SurveyIds=['P_5ee9ff59364cc273'],
        InventoryQuantityRole='Container; four physical constituents per joint')
    new_assemblies.append(assembly.Name)
    for key in ['bolt','nut','cotter','washer']:
        name=joint['name']+'_'+key;obj=doc.addObject('App::Link',name);assembly.addObject(obj)
        obj.setLink(doc.getObject(body_names[key]))
        obj.LinkPlacement=assembly.getGlobalPlacement().inverse().multiply(placements[name])
        metadata(obj,OccurrenceId=name,Subsystem='Drivetrain',SourceRecords=[references[key][2]])
        expected[name]=dict(definition=body_names[key],frame=list(placements[name].toMatrix().A),
            owners=rows[joint['receiver']]['owners']+[groups[owner_name].Name,assembly.Name])
doc.Root.Label='Powertrain development — bracket-to-channel fastening trial'
doc.Root.RegistrationStatus='Twenty MX1 joints populated; common casting pads and hole layout remain explicit hypotheses'
doc.Definitions.Visibility=False
doc.recompute();doc.saveAs(str(native));App.closeDocument(doc.Name)
assert sha(source)==pr['native_sha256'] and all(sha(ROOT/path)==digest for path,digest in locked.items())
frozen=out/'frozen_inputs';frozen.mkdir()
for path in paths:shutil.copyfile(path,frozen/str(path.relative_to(ROOT)).replace('/','__'))
affected=sorted([name for name,row in rows.items() if row['definition'] in changed]+list(expected))
write(out/'report.json',dict(status='saved_mx1_joint_trial_pending_independent_checks',
    native_file=native.name,native_sha256=sha(native),source_native=str(source.relative_to(ROOT)),
    source_native_sha256=sha(source),input_hashes=locked,controls=c,mount_controls=mount,
    bracket_dimensions=dimensions,casting_rear_shift_mm=shift,casting_baseline_comparison=baseline,
    casting_rebuild=cast_details,later_features=feature_details,archives=archives,
    baseline_brep_hashes={path.name:sha(path) for path in baselines.glob('*.brep')},
    details=details,joints=joints,changed_definitions=sorted(changed),
    new_definitions=sorted(body_names[key] for key in defs),hardware_definitions=body_names,
    expected_new_occurrences=expected,new_assemblies=new_assemblies,affected_occurrences=affected,
    expected_physical_occurrences=len(rows)+80,expected_definition_count=len(m['definitions'])+2,
    expected_assembly_count=len(m['assemblies'])+24,source_joint_count=20,
    historical_joint_layout_qualified=False,installation_qualified=False,standard_assembly_modified=False))
print('Saved twenty MX1 joints:',len(rows)+80,'physical occurrences;',len(affected),'affected',flush=True)
