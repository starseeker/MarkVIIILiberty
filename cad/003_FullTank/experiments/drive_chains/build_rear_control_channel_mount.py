"""Install the reviewed M4130 mounting increment in a new powertrain document."""
import argparse
from pathlib import Path
import shutil
import sys
import uuid

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path.insert(0, str(H.parents[1]))
import FreeCAD as App
from lib.evidence import read, write, sha
from lib.cad_build import metadata

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
out = a.output.resolve()
assert not out.exists()
packet = H / 'transmission_controls_study'
prototype = packet / 'channel_mount02'
parent = packet / 'us_nuts01'
r = read(prototype / 'report.json')
pm = read(prototype / 'isolated/manifest.json')
q = read(parent / 'qualification.json')
source = parent / read(parent / 'report.json')['native_file']
native_trial = prototype / r['native_file']
assert q['local_static_checks_passed'] and sha(source) == q['native_sha256'] == r['parent_native_sha256']
assert sha(native_trial) == r['native_sha256'] == pm['native_sha256']
assert all(sha(ROOT / f) == v for f, v in r['input_hashes'].items())
receipts = [directory / file for directory in [prototype, packet / 'channel_mount_variation02']
            for file in ['independent_checks.json', 'context_checks.json', 'exchange_checks.json']]
receipts += [prototype / 'reproduction_checks.json']
for path in receipts:
    receipt = read(path)
    assert receipt['passed'] and receipt['native_sha256'] == read(path.parent / 'report.json')['native_sha256']
assert read(prototype / 'visual_review.json')['disposition'] == 'reviewed_local_approximation'
inputs = [Path(__file__), H.parents[1] / 'lib/cad_build.py', prototype / 'report.json',
          prototype / 'isolated/manifest.json', native_trial, prototype / 'visual_review.json',
          prototype / 'render_receipt.json', parent / 'qualification.json',
          parent / 'isolated/manifest.json', *receipts]
inputs_hash = {str(f.relative_to(ROOT)): sha(f) for f in inputs}
doc = App.openDocument(str(native_trial))
try:
    shapes = {role: doc.getObject('Def_ChannelMount_' + role).Shape.copy()
              for role in ['channel', 'cleat', 'bolt', 'lock', 'rivet', 'floor']}
    attrs = {role: {key: getattr(doc.getObject('Def_ChannelMount_' + role), key)
                    for key in ['SourcePartMark', 'SourceRecords', 'SurveyIds']}
             for role in shapes if role != 'floor'}
finally:
    App.closeDocument(doc.Name)
out.mkdir(parents=True)
doc = App.openDocument(str(source))
added = {'Definitions': [], 'Root': ['RearControlChannel']}
definitions = {'nut': doc.getObject(r['shared_nut_definition']),
               'floor': doc.getObject(r['source_floor_definition'])}
new_definitions = []
for role in ['channel', 'cleat', 'bolt', 'lock', 'rivet']:
    body = doc.addObject('PartDesign::Body', 'Def_RearControlMount_' + role)
    doc.Definitions.addObject(body)
    body.newObject('PartDesign::Feature', 'ReconstructedRearControlMount').Shape = shapes[role]
    metadata(body, **attrs[role], DefinitionKey='rear_control_mount_' + role,
             Representation='assembly', Coverage='reconstruction_trial',
             ParameterUpdate='Regenerate channel_mount_controls02.json with trial_rear_control_channel_mount.py, then build_rear_control_channel_mount.py',
             ReconstructionStatus='Reviewed M4130 local mounting approximation; cleat stations/hand/profile and rivet stock datum remain inferred.')
    definitions[role] = body
    new_definitions.append(body.Name)
    added['Definitions'].append(body.Name)
floor = definitions['floor']
assert floor.Placement.isIdentity() and floor.Tip is not None
floor_feature = floor.Tip.Name
floor.Tip.Shape = shapes['floor']
metadata(floor, RearChannelMountSourceRecords=['SNL:33:007'],
         RearChannelMountUpdate='Four additional M4130 floor bolt passages; regenerate channel_mount_controls02.json after the inherited clutch/engine receiving floor.')
groups = ['RearControlChannel'] + ['RearChannelLeftCleat' + str(i) + 'Mount' for i in range(1, 5)]
for name in groups:
    owner = doc.Root if name == 'RearControlChannel' else doc.RearControlChannel
    group = doc.addObject('App::Part', name)
    owner.addObject(group)
    group.Uid = str(uuid.uuid5(uuid.NAMESPACE_URL, 'markviii:rear-control-channel:' + name))
    group.Placement = owner.getGlobalPlacement().inverse().multiply(App.Placement(App.Matrix(*pm['assemblies'][name]['world'])))
    metadata(group, Coverage='reconstruction_trial', ReconstructionStatus='Four M4130 mounts; M4129, fulcrums, springs and control routes remain pending.')
    if name != 'RearControlChannel':
        added.setdefault(owner.Name, []).append(name)
rows = {v['name']: v for v in pm['occurrences']}
expected = {}
for name, spec in r['specs'].items():
    if spec['role'] == 'floor':
        continue
    owner = doc.getObject(spec['owner'])
    link = doc.addObject('App::Link', name)
    owner.addObject(link)
    link.setLink(definitions[spec['role']])
    link.LinkPlacement = owner.getGlobalPlacement().inverse().multiply(App.Placement(App.Matrix(*rows[name]['frame'])))
    metadata(link, OccurrenceId=name, Subsystem='Drivetrain',
             SourceRecords=r['record_ids'][spec['role']], Coverage='reconstruction_trial')
    added.setdefault(owner.Name, []).append(name)
    expected[name] = dict(definition=definitions[spec['role']].Name, role=spec['role'],
                          frame=rows[name]['frame'], owners=rows[name]['owners'], prototype_occurrence=name)
doc.Root.Label = 'Powertrain development — rear control channel mounts'
doc.Root.RegistrationStatus = 'M4128 channel and four M4130 cleats with floor bolt sets and twelve rivets. M4129 attachment, fulcrums, springs, control routes and standard integration remain open.'
doc.Definitions.Visibility = False
doc.recompute()
native = out / 'PowertrainWithRearChannelMounts.FCStd'
doc.saveAs(str(native))
App.closeDocument(doc.Name)
assert sha(source) == q['native_sha256'] and all(sha(ROOT / f) == v for f, v in inputs_hash.items())
frozen = out / 'frozen_inputs'
frozen.mkdir()
for f in inputs:
    if f.suffix != '.FCStd':
        shutil.copy2(f, frozen / str(f.relative_to(ROOT)).replace('/', '__'))
write(out / 'report.json', dict(
    native_file=native.name, native_sha256=sha(native), source_native=str(source.relative_to(ROOT)),
    source_native_sha256=sha(source), prototype=str(prototype.relative_to(ROOT)),
    prototype_native_sha256=sha(native_trial), input_hashes=inputs_hash,
    controls=r['controls'], details=r['details'], expected_new_occurrences=expected,
    new_assemblies=groups, added_children=added, new_definitions=new_definitions,
    shared_definitions={'nut': r['shared_nut_definition']},
    changed_definitions=[r['source_floor_definition']], changed_floor_feature=floor_feature,
    affected_occurrences=sorted(expected) + ['hull_floor_7'],
    expected_physical_occurrences=3202, expected_definition_count=551, expected_assembly_count=343,
    historical_geometry_qualified=False, installation_qualified=False,
    standard_assembly_modified=False, channel_complete=False, packet_complete=False))
print('Saved3202 physical occurrences /551 definitions /343 groups; qualification pending.', flush=True)
