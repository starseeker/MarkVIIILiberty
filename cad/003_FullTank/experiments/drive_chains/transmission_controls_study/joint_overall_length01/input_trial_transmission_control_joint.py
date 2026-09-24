"""Build saved high-speed rear control joints without modifying the parent."""
import argparse,shutil,sys
from pathlib import Path
H=Path(__file__).resolve().parent;STAGE=H.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(H),str(STAGE)]
import FreeCAD as App
import Part
from lib.evidence import read,write,sha
from lib.cad_build import metadata
from lib.camera_review import validate_native_bindings
from transmission_control_joint_parts import parts,joint_frame
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
p.add_argument('--controls',type=Path,default=H/'transmission_controls_study/high_speed_joint_controls.json');a=p.parse_args()
out=a.output.resolve();assert not out.exists();out.mkdir(parents=True)
packet=H/'transmission_controls_study';parent=H/'transmission_high_brake_support_study/integrated_upper01'
pr=read(parent/'report.json');m=read(parent/'isolated/manifest.json');q=read(parent/'qualification.json');native=parent/pr['native_file']
assert q['local_static_checks_passed'] and sha(native)==q['native_sha256']==m['native_sha256']
probe=read(packet/'context01/report.json');assert probe['passed'] and probe['source_native_sha256']==sha(native)
assert probe['source_qualification_sha256']==sha(parent/'qualification.json')
c=read(a.controls)['controls'];d=m['definitions'][c['shared_nut_definition']]
assert sha(d['brep_path'])==d['brep_sha256'];nut=Part.Shape();nut.read(d['brep_path'])
names=[v['name'] for v in m['occurrences'] if v['definition']==c['shared_nut_definition']]
names += [h+'HighSpeedBrakeLever'+side for h in ['Port','Starboard'] for side in ['Left','Right']]
validate_native_bindings(dict(native_file=str(native),render_occurrences=names,landmarks=[]),m)
shapes,details=parts(c,nut)
inputs=[Path(__file__),H/'transmission_control_joint_parts.py',H/'transmission_input_installation_parts.py',a.controls.resolve(),
        packet/'sources.json',packet/'inventory_audit.json',packet/'context01/report.json',parent/'qualification.json',parent/'isolated/manifest.json',
        STAGE/'lib/cad_build.py',STAGE/'lib/evidence.py']
assert all(sha(ROOT/f)==v for f,v in read(packet/'sources.json')['source_hashes'].items())
doc=App.newDocument('HighSpeedControlJointTrial');root=doc.addObject('App::Part','Root');library=doc.addObject('App::Part','Definitions')
made={};marks={'fork':'M569B','pin':'M568A','cotter':'1/8 x 1 inch split pin','nut':'3/4 inch plain U.S. Std. nut'}
record_ids={'fork':['SNL:87:003'],'pin':['SNL:136:007'],'cotter':['SNL:136:008'],'nut':['SNL:195:008']}
sources=read(packet/'sources.json')['source_records']
for role,s in shapes.items():
    body=doc.addObject('PartDesign::Body','Def_'+role);library.addObject(body)
    body.newObject('PartDesign::Feature','ReconstructedControlJoint').Shape=s
    ids=sorted({pid for row in sources if row['record_id'] in record_ids[role] for pid in row['part_ids']})
    metadata(body,SourcePartMark=marks[role],SourceRecords=record_ids[role],SurveyIds=ids,Representation='unqualified_prototype',
             ParameterUpdate='Regenerate with trial_transmission_control_joint.py',ReconstructionStatus='Explicit fork/pin datum and profile hypothesis; nominal thread envelopes.')
    made[role]=body;s.exportBrep(str(out/(role+'.brep')))
specs={};joints={}
for hand in ['Port','Starboard']:
    connection=next(v for v in probe['interfaces'] if v['id']==hand+'HighSpeedBrakeControl')
    base=joint_frame(connection['center_world_mm'],hand,c['fork_pitch_deg'])
    group=doc.addObject('App::Part',hand+'ControlJoint');root.addObject(group);group.Placement=base
    joints[hand]=dict(frame=list(base.toMatrix().A),interface=connection)
    for role in shapes:
        name=hand+role.title();local=App.Placement(App.Matrix(*details['local_frames'][role]))
        link=doc.addObject('App::Link',name);group.addObject(link);link.setLink(made[role]);link.LinkPlacement=local
        metadata(link,SourceRecords=record_ids[role],Coverage='reconstruction_trial')
        specs[name]=dict(role=role,frame=list(base.multiply(local).toMatrix().A),local_frame=list(local.toMatrix().A),owner=group.Name)
library.Visibility=False;doc.recompute();saved=out/'HighSpeedControlJoints.FCStd';doc.saveAs(str(saved));App.closeDocument(doc.Name)
for f in inputs:shutil.copy2(f,out/('input_'+f.name))
write(out/'report.json',dict(native_file=saved.name,native_sha256=sha(saved),parent_native_sha256=sha(native),
    parent_manifest_sha256=sha(parent/'isolated/manifest.json'),parent_qualification_sha256=sha(parent/'qualification.json'),
    input_hashes={str(f.relative_to(ROOT)):sha(f) for f in inputs},controls=c,details=details,joints=joints,specs=specs,
    shared_definitions={'nut':c['shared_nut_definition']},record_ids=record_ids,
    runtime=dict(freecad=App.Version(),occ=Part.OCC_VERSION),geometry_integrated=False,packet_complete=False,
    limits=read(a.controls)['unprinted_estimates'],historical_geometry_qualified=False,installation_qualified=False))
print('Saved four definitions and eight installed joint components.',flush=True)
