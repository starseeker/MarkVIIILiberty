"""Build two provisional M4136 spring anchors on the saved receiving channel."""
import argparse
from pathlib import Path
import shutil
import sys
import uuid

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path.insert(0, str(H.parents[1]))
import FreeCAD as App
import Part
from lib.evidence import read, write, sha
from lib.cad_build import metadata
from lib.camera_review import validate_native_bindings
from rear_low_spring_bracket_parts import parts

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--controls', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
out = a.output.resolve()
assert not out.exists()
config = read(a.controls)
c = config['controls']
C = H/'transmission_controls_study'
sources = ROOT/config['source_packet']
assert sha(sources) == config['source_packet_sha256']
for file, digest in read(sources)['source_hashes'].items():
    assert sha(ROOT/file) == digest
receiver = C/c['receiver']
prior = read(receiver/'report.json')
manifest = read(receiver/'isolated/manifest.json')
native = receiver/prior['native_file']
assert sha(native) == prior['native_sha256'] == manifest['native_sha256']
row = next(v for v in manifest['occurrences'] if v['name'] == 'RearControlChannelStock')
validate_native_bindings(dict(native_file=str(native), render_occurrences=[row['name']],
                             landmarks=[]), manifest)
definition = manifest['definitions'][row['definition']]
assert sha(definition['brep_path']) == definition['brep_sha256']
channel = Part.Shape()
channel.read(definition['brep_path'])
pose = App.Placement(App.Matrix(*row['frame']))
shapes, details, holes = parts(c, channel, pose)
out.mkdir(parents=True)
doc = App.newDocument('RearLowSpringBrackets')
root = doc.addObject('App::Part', 'Root')
library = doc.addObject('App::Part', 'Definitions')
records = dict(bracket=['SNL:38:001', 'SNL:63:008'], rivet=['SNL:170:005'],
               channel=['SNL:63:010'])
made, specs = {}, {}
source_rows = {v['record_id']: v for v in read(sources)['source_records']}
for role, shape in shapes.items():
    body = doc.addObject('PartDesign::Body', 'Def_LowSpringAnchor_'+role)
    library.addObject(body)
    body.newObject('PartDesign::Feature', 'ReconstructedSpringAnchor').Shape = shape
    metadata(body, SourceRecords=records[role],
             SourcePartMark=dict(bracket='M4136', rivet='1/2 x 1-7/8 inch button-head rivet',
                                 channel='M4128')[role],
             SurveyIds=sorted({pid for rid in records[role] if rid in source_rows
                               for pid in source_rows[rid]['part_ids']}),
             Representation='unqualified_spring_support_trial',
             ReconstructionStatus='U profile, section, spring holes and stations are estimates; M4129 relationship unresolved.',
             ParameterUpdate='Regenerate '+a.controls.name+' with trial_rear_low_spring_brackets.py')
    shape.exportBrep(str(out/(role+'.brep')))
    made[role] = body


def install(name, role, owner, local):
    link = doc.addObject('App::Link', name)
    owner.addObject(link)
    link.setLink(made[role])
    link.LinkPlacement = local
    metadata(link, SourceRecords=records[role], Coverage='reconstruction_trial')
    specs[name] = dict(role=role, owner=owner.Name,
                      frame=list(owner.getGlobalPlacement().multiply(local).toMatrix().A))


install('RearControlChannelStock', 'channel', root, pose)
for side, xyz in c['stations'].items():
    group = doc.addObject('App::Part', side+'LowSpringSupport')
    root.addObject(group)
    group.Placement = App.Placement(App.Vector(*xyz), App.Rotation())
    install(side+'LowSpringBracket', 'bracket', group, App.Placement())
    for i, y in enumerate(c['bracket']['rivet_y'], 1):
        install(side+'LowSpringRivet'+str(i), 'rivet', group,
                App.Placement(App.Vector(0, y, c['bracket']['stock']),
                              App.Rotation(App.Vector(1, 0, 0), 180)))
for group in [v for v in doc.Objects if v.TypeId == 'App::Part']:
    group.Uid = str(uuid.uuid5(uuid.NAMESPACE_URL, 'markviii:low-spring:'+group.Name))
doc.recompute()
saved = out/'RearLowSpringBrackets.FCStd'
doc.saveAs(str(saved))
App.closeDocument(doc.Name)
inputs = [Path(__file__), H/'rear_low_spring_bracket_parts.py',
          H/'rear_control_channel_mount_parts.py', H/'transmission_frame_joint_parts.py',
          H/'transmission_brake_stop_parts.py', H.parents[1]/'lib/cad_build.py',
          a.controls.resolve(), sources, receiver/'report.json',
          receiver/'isolated/manifest.json', C/'high_spring_study_receipt01.json',
          ROOT/config['source_review']]
for file in inputs:
    shutil.copy2(file, out/('input_'+file.name))
write(out/'report.json', dict(native_file=saved.name, native_sha256=sha(saved),
      parent_native=prior['parent_native'], parent_native_sha256=prior['parent_native_sha256'],
      receiver_native=str(native.relative_to(ROOT)), receiver_native_sha256=sha(native),
      receiver_manifest_sha256=sha(receiver/'isolated/manifest.json'),
      controls=c, details=details, specs=specs, record_ids=records,
      input_hashes={str(f.relative_to(ROOT)): sha(f) for f in inputs},
      new_physical_occurrences=6, prototype_physical_occurrences=7,
      prototype_definition_count=3, historical_geometry_qualified=False,
      installation_qualified=False, geometry_integrated=False))
print('Saved seven-occurrence M4136 trial; independent review pending.', flush=True)
