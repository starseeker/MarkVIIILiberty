"""Build four retained M4131/lever assemblies and their drilled receiving channel."""
import argparse
from pathlib import Path
import shutil
import sys
import uuid
H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path[:0] = [str(H),str(H.parents[1])]
import FreeCAD as App
import Part
from lib.evidence import read,write,sha
from lib.cad_build import metadata
from lib.camera_review import validate_native_bindings
from rear_control_fulcrum_parts import parts

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--controls',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a = p.parse_args()
out = a.output.resolve()
assert not out.exists()
packet = H/'transmission_controls_study'
configuration = read(a.controls)
c = configuration['controls']
review = packet/'fulcrum_source_review01.json'
assert configuration['source_review_sha256']==sha(review)
sr = read(review)
for path,digest in sr['source_packets'].items() | sr['additional_source'].items():
    assert sha(ROOT/path)==digest
parent = packet/c['parent']
pr = read(parent/'report.json')
m = read(parent/'isolated/manifest.json')
source = parent/pr['native_file']
assert sha(source)==pr['native_sha256']==sr['parent_native_sha256']==m['native_sha256']
row = next(v for v in m['occurrences'] if v['name']==c['channel_occurrence'])
assert row['definition']==c['channel_definition']
validate_native_bindings(dict(native_file=str(source),render_occurrences=[row['name']],landmarks=[]),m)
d = m['definitions'][row['definition']]
assert sha(d['brep_path'])==d['brep_sha256']
shape = Part.Shape()
shape.read(d['brep_path'])
pose = App.Placement(App.Matrix(*row['frame']))
shapes,details,tools = parts(c,shape,pose)
out.mkdir(parents=True)
doc = App.newDocument('RearControlFulcrums')
root = doc.addObject('App::Part','Root')
library = doc.addObject('App::Part','Definitions')
for group in [root,library]:
    group.Uid = str(uuid.uuid5(uuid.NAMESPACE_URL,'markviii:fulcrum-trial:'+group.Name))
records = dict(bracket=['SNL:36:017'],cotter=['SNL:36:018','SNL:141:016'],
               washer=['SNL:72:026','SNL:267:008'],rivet=['SNL:170:007'],channel=['SNL:63:010'],
               lever_track=['SNL:116:025','SNL:73:001'],lever_low_left=['SNL:117:027','SNL:73:002'],
               lever_low_right=['SNL:117:028','SNL:73:003'])
marks = dict(bracket='M4131',cotter='1/4 x 2 inch split pin',washer='M4137',rivet='1/2 x 2-1/8 inch button-head rivet',
             channel='M4128',lever_track='M4132',lever_low_left='M4133',lever_low_right='M4134')
source_rows = read(packet/'channel_sources01/sources.json')['source_records'] + read(packet/'sources.json')['source_records']
made = {}
for role,s in shapes.items():
    body = doc.addObject('PartDesign::Body','Def_ControlFulcrum_'+role)
    library.addObject(body)
    body.newObject('PartDesign::Feature','ReconstructedControlFulcrum').Shape = s
    ids = sorted({pid for row in source_rows if row['record_id'] in records[role] for pid in row['part_ids']})
    metadata(body,SourcePartMark=marks[role],SourceRecords=records[role],SurveyIds=ids,
             Representation='unqualified_fulcrum_prototype',ParameterUpdate='Regenerate '+a.controls.name+' with trial_rear_control_fulcrums.py',
             ReconstructionStatus='Cast foot, rivet orientation, pivot/lever profile and washer form are explicit estimates; source counts and hardware lengths retained.')
    made[role]=body
    s.exportBrep(str(out/(role+'.brep')))
specs = {}
def occurrence(name,role,owner,local):
    link = doc.addObject('App::Link',name)
    owner.addObject(link)
    link.setLink(made[role])
    link.LinkPlacement = local
    metadata(link,SourceRecords=records[role],Coverage='reconstruction_trial')
    specs[name]=dict(role=role,owner=owner.Name,frame=list(owner.getGlobalPlacement().multiply(local).toMatrix().A),local_frame=list(local.toMatrix().A))
occurrence(c['channel_occurrence'],'channel',root,pose)
for name,station in c['stations'].items():
    group=doc.addObject('App::Part',name+'ControlFulcrum')
    root.addObject(group)
    group.Uid=str(uuid.uuid5(uuid.NAMESPACE_URL,'markviii:fulcrum-trial:'+group.Name))
    group.Placement=App.Placement(App.Vector(*station['pivot']),App.Rotation(App.Vector(0,0,1),station['inboard_clock']))
    occurrence(name+'FulcrumBracket','bracket',group,App.Placement())
    rotation=App.Rotation(App.Vector(0,0,1),station['lever_clock']-station['inboard_clock'])
    occurrence(name+'HorizontalLever','lever_'+station['lever_profile'],group,App.Placement(App.Vector(0,0,details['lever_bearing_z_mm']),rotation))
    occurrence(name+'FulcrumSpringWasher','washer',group,App.Placement(App.Vector(0,0,details['washer_bottom_z_mm']),App.Rotation()))
    occurrence(name+'FulcrumCotter','cotter',group,App.Placement(App.Vector(0,0,details['cotter_center_z_mm']),App.Rotation()))
    for i,y in enumerate(c['bracket']['rivet_y'],1):
        occurrence(name+'FulcrumRivet'+str(i),'rivet',group,
                   App.Placement(App.Vector(c['bracket']['rivet_x'],y,c['bracket']['foot_stock']),App.Rotation(App.Vector(1,0,0),180)))
library.Visibility=False
doc.recompute()
native=out/'RearControlFulcrums.FCStd'
doc.saveAs(str(native))
App.closeDocument(doc.Name)
for name,s in tools.items():
    s.exportBrep(str(out/(name+'.brep')))
inputs=[Path(__file__),H/'rear_control_fulcrum_parts.py',H/'rear_control_channel_mount_parts.py',
        H/'transmission_input_installation_parts.py',H/'transmission_frame_joint_parts.py',
        a.controls.resolve(),review,packet/'sources.json',packet/'channel_sources01/sources.json',parent/'qualification.json']
for path in inputs:
    shutil.copy2(path,out/('input_'+path.name))
write(out/'report.json',dict(native_file=native.name,native_sha256=sha(native),parent_native=str(source.relative_to(ROOT)),
      parent_native_sha256=sha(source),parent_manifest_sha256=sha(parent/'isolated/manifest.json'),controls=c,details=details,
      specs=specs,record_ids=records,input_hashes={str(path.relative_to(ROOT)):sha(path) for path in inputs},
      new_physical_occurrences=24,prototype_physical_occurrences=25,prototype_definition_count=8,
      geometry_integrated=False,historical_geometry_qualified=False,installation_qualified=False))
print('Saved four retained fulcrum/lever units, eight rivets and the receiving channel.',flush=True)
