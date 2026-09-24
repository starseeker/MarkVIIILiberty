"""Build a bounded pair of M4135 guide brackets for clearance and source review."""
import argparse
from pathlib import Path
import shutil
import sys
import uuid

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path[:0] = [str(H), str(H.parents[1])]
import FreeCAD as App
import Part
from lib.evidence import read, write, sha
from lib.cad_build import metadata
from lib.camera_review import validate_native_bindings
from rear_high_spring_bracket_parts import parts

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--controls', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
out = a.output.resolve()
assert not out.exists()
packet = H / 'transmission_controls_study'
configuration = read(a.controls)
c = configuration['controls']
evidence = ROOT / configuration['source_packet']
assert sha(evidence) == configuration['source_packet_sha256']
parent = packet / c['parent']
pr = read(parent / 'report.json')
manifest = read(parent / 'isolated/manifest.json')
native = parent / pr['native_file']
assert sha(native) == pr['native_sha256'] == manifest['native_sha256']
for path, digest in read(evidence)['source_hashes'].items():
    assert sha(ROOT / path) == digest
row = next(v for v in manifest['occurrences'] if v['name'] == 'RearControlChannelStock')
validate_native_bindings(dict(native_file=str(native), render_occurrences=[row['name']], landmarks=[]), manifest)
definition = manifest['definitions'][row['definition']]
assert sha(definition['brep_path']) == definition['brep_sha256']
channel = Part.Shape()
channel.read(definition['brep_path'])
pose = App.Placement(App.Matrix(*row['frame']))
shapes, details, holes = parts(c, channel, pose)
out.mkdir(parents=True)
doc = App.newDocument('RearHighSpringBrackets')
root = doc.addObject('App::Part', 'Root')
library = doc.addObject('App::Part', 'Definitions')
records = dict(bracket=['SNL:39:008', 'SNL:63:009'], rivet=['SNL:169:011'], channel=['SNL:63:010'])
made = {}
for role, shape in shapes.items():
    body = doc.addObject('PartDesign::Body', 'Def_HighSpringGuide_' + role)
    library.addObject(body)
    body.newObject('PartDesign::Feature', 'ReconstructedHighSpringGuide').Shape = shape
    metadata(body, SourceRecords=records[role],
             SourcePartMark=dict(bracket='M4135', rivet='1/2 x 3/4 inch button-head rivet', channel='M4128')[role],
             Representation='unqualified_spring_support_trial',
             ReconstructionStatus='Bracket section, bore, attachment and station are estimates; source rivet count and stock retained.',
             ParameterUpdate='Regenerate ' + a.controls.name + ' with trial_rear_high_spring_brackets.py')
    shape.exportBrep(str(out / (role+'.brep')))
    made[role] = body
specs = {}


def install(name, role, owner, local):
    link = doc.addObject('App::Link', name)
    owner.addObject(link)
    link.setLink(made[role])
    link.LinkPlacement = local
    metadata(link, SourceRecords=records[role], Coverage='reconstruction_trial')
    specs[name] = dict(role=role, owner=owner.Name,
                      frame=list(owner.getGlobalPlacement().multiply(local).toMatrix().A))


install('RearControlChannelStock', 'channel', root, pose)
for name, point in c['stations'].items():
    group = doc.addObject('App::Part', name+'HighSpringSupport')
    root.addObject(group)
    group.Placement = App.Placement(App.Vector(*point), App.Rotation())
    install(name+'HighSpringBracket', 'bracket', group, App.Placement())
    for i, y in enumerate(c['bracket']['rivet_y'], 1):
        if c.get('mount_face') == 'rear_flange':
            rivet_pose = App.Placement(App.Vector(0, y, c['bracket']['rivet_height']),
                                      App.Rotation(App.Vector(0, 1, 0), 90))
        else:
            rivet_pose = App.Placement(App.Vector(c['bracket']['rivet_x'], y, c['bracket']['stock']),
                                      App.Rotation(App.Vector(1, 0, 0), 180))
        install(name+'HighSpringRivet'+str(i), 'rivet', group,
                rivet_pose)
for group in [root, library] + [v for v in doc.Objects if v.TypeId == 'App::Part' and v not in [root, library]]:
    group.Uid = str(uuid.uuid5(uuid.NAMESPACE_URL, 'markviii:high-spring-trial:'+group.Name))
doc.recompute()
saved = out / 'RearHighSpringBrackets.FCStd'
doc.saveAs(str(saved))
App.closeDocument(doc.Name)
inputs = [Path(__file__), H / 'rear_high_spring_bracket_parts.py',
          H / 'rear_control_channel_mount_parts.py', H / 'transmission_frame_joint_parts.py',
          H / 'transmission_brake_stop_parts.py', H.parents[1] / 'lib/cad_build.py',
          a.controls.resolve(), evidence, parent / 'qualification.json', parent / 'isolated/manifest.json']
for path in inputs:
    shutil.copy2(path, out / ('input_'+path.name))
write(out / 'report.json', dict(native_file=saved.name, native_sha256=sha(saved),
    parent_native=str(native.relative_to(ROOT)), parent_native_sha256=sha(native),
    parent_manifest_sha256=sha(parent / 'isolated/manifest.json'), controls=c, details=details,
    specs=specs, record_ids=records, input_hashes={str(path.relative_to(ROOT)): sha(path) for path in inputs},
    new_physical_occurrences=6, prototype_physical_occurrences=7, prototype_definition_count=3,
    historical_geometry_qualified=False, installation_qualified=False, geometry_integrated=False))
print('Saved7-occurrence M4135 trial. Clearance and source review pending.', flush=True)
