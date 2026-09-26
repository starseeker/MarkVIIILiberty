"""Install two reviewed straight low-speed rods and explicitly propagate fulcrum lever revisions."""
import argparse
from pathlib import Path
import shutil
import sys

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

C = H/'transmission_controls_study'
prototype = C/'low_rods01'
r, pm = read(prototype/'report.json'), read(prototype/'isolated/manifest.json')
source = ROOT/r['parent_native']
parent = source.parent
old, parent_q = read(parent/'isolated/manifest.json'), read(parent/'qualification.json')
trial = prototype/r['native_file']
assert sha(source) == r['parent_native_sha256'] == parent_q['native_sha256'] == old['native_sha256']
assert parent_q['local_static_checks_passed']
assert sha(trial) == r['native_sha256'] == pm['native_sha256']
assert all(sha(ROOT/f) == h for f, h in r['input_hashes'].items())

receipts = [folder/file for folder in [prototype, C/'low_rods_variation01']
            for file in ['independent_checks.json', 'context_checks.json', 'exchange_checks.json']]
receipts.append(prototype/'reproduction_checks.json')
for file in receipts:
    q = read(file)
    assert q['passed'] and q['native_sha256'] == read(file.parent/'report.json')['native_sha256']
assert read(prototype/'visual_review.json')['disposition'] == 'reviewed_local_approximation'

inputs = [
    Path(__file__), H.parents[1]/'lib/cad_build.py', prototype/'report.json',
    prototype/'isolated/manifest.json', prototype/'operating_interfaces.json', trial,
    prototype/'visual_review.json', prototype/'render_receipt.json',
    parent/'qualification.json', parent/'isolated/manifest.json', *receipts
]
hashes = {str(f.relative_to(ROOT)): sha(f) for f in inputs}

doc = App.openDocument(str(trial))
try:
    shapes = {key: doc.getObject(key).Shape.copy() for key in [*r['changed_definitions'], 'Def_RearLowRod']}
finally:
    App.closeDocument(doc.Name)

prior = {v['name']: v for v in old['occurrences']}
out.mkdir(parents=True)
doc = App.openDocument(str(source))
added = {'Definitions': ['Def_RearLowRod']}
added_properties = {}

for key in r['changed_definitions']:
    body = doc.getObject(key)
    assert body.Placement.isIdentity() and not hasattr(body, 'LowRodClosureUpdate')
    body.Tip.Shape = shapes[key]
    metadata(body, LowRodClosureUpdate='Regenerate low_rod_controls01.json with trial_rear_low_rods.py, then build_rear_low_rods.py. This reconciles M4133/M4134 fulcrum lever brake arms for straight-rod closure; source interfaces and remaining estimates are in low_rods_integrated01/qualification.json.')
    added_properties[key] = ['LowRodClosureUpdate']

body = doc.addObject('PartDesign::Body', 'Def_RearLowRod')
doc.Definitions.addObject(body)
body.newObject('PartDesign::Feature', 'ReconstructedLowRod').Shape = shapes[body.Name]
metadata(body, SourcePartMark='SH946E', SourceRecords=['SNL:195:019'],
         SurveyIds=['P_03d872e5ff732c91'], DefinitionKey='rear_low_connecting_rod',
         Representation='assembly', Coverage='reconstruction_trial',
         ParameterUpdate='Regenerate low_rod_controls01.json with trial_rear_low_rods.py, then build_rear_low_rods.py',
         ReconstructionStatus='Straight solid rod with nominal male threads; length, section and receiver profiles inferred. No full motion/service qualification.')

for name, frame in r['joint_frames'].items():
    group = doc.getObject(name)
    side = 'Starboard' if name.startswith('Starboard') else 'Port'
    owner = doc.getObject(side+'LowShortConnection')
    group.Placement = owner.getGlobalPlacement().inverse().multiply(App.Placement(App.Matrix(*frame)))

for side in ['Starboard', 'Port']:
    name = side+'LowHorizontalLever'
    link = doc.getObject(name)
    owner = doc.getObject(prior[name]['owners'][-1])
    link.LinkPlacement = owner.getGlobalPlacement().inverse().multiply(
        App.Placement(App.Matrix(*r['specs'][name]['frame'])))

expected, expected_new = {}, {}
for name, spec in r['specs'].items():
    if name in r['new_occurrences']:
        owner = doc.getObject(spec['owner'])
        link = doc.addObject('App::Link', name)
        owner.addObject(link)
        link.setLink(body)
        link.LinkPlacement = owner.getGlobalPlacement().inverse().multiply(App.Placement(App.Matrix(*spec['frame'])))
        metadata(link, OccurrenceId=name, Subsystem='Drivetrain', SourceRecords=['SNL:195:019'], Coverage='reconstruction_trial')
        added.setdefault(owner.Name, []).append(name)
        owners = ['Root', 'RearControlChannel', owner.Name]
    else:
        owners = prior[name]['owners']
    expected[name] = dict(definition=spec['definition'], role=spec['role'], frame=spec['frame'],
                          owners=owners, prototype_occurrence=name)
    if name in r['new_occurrences']:
        expected_new[name] = expected[name]

doc.Root.Label = 'Powertrain development — straight rear low-speed connections'
doc.Root.RegistrationStatus = 'Two SH946E rods installed. M4133/M4134 fulcrum lever brake arms reconciled for straight-rod closure. Return springs, long controls, service and standard integration remain open.'
doc.Definitions.Visibility = False
doc.recompute()
native = out/'PowertrainWithRearLowRods.FCStd'
doc.saveAs(str(native))
App.closeDocument(doc.Name)

assert sha(source) == r['parent_native_sha256']
assert all(sha(ROOT/f) == h for f, h in hashes.items())
frozen = out/'frozen_inputs'
frozen.mkdir()
for file in inputs:
    if file.suffix != '.FCStd':
        shutil.copy2(file, frozen/str(file.relative_to(ROOT)).replace('/', '__'))

write(out/'report.json', dict(
    native_file=native.name, native_sha256=sha(native),
    source_native=str(source.relative_to(ROOT)), source_native_sha256=sha(source),
    prototype=str(prototype.relative_to(ROOT)), prototype_native_sha256=sha(trial),
    input_hashes=hashes, controls=r['controls'], details=r['details'],
    expected_new_occurrences=expected_new, expected_affected_occurrences=expected,
    affected_occurrences=sorted(expected), changed_definitions=r['changed_definitions'],
    new_definitions=['Def_RearLowRod'], new_assemblies=[], added_children=added,
    added_inherited_properties=added_properties, changed_group_frames=r['joint_frames'],
    changed_link_frames={side+'LowHorizontalLever': r['specs'][side+'LowHorizontalLever']['frame']
                         for side in ['Starboard', 'Port']},
    placement_changed_objects=sorted(r['joint_frames'])+[side+'LowHorizontalLever' for side in ['Starboard', 'Port']],
    expected_physical_occurrences=3282, expected_definition_count=570, expected_assembly_count=365,
    historical_geometry_qualified=False, installation_qualified=False,
    standard_assembly_modified=False, channel_complete=False, packet_complete=False
))
print('Saved 3282 occurrences / 570 definitions / 365 groups; qualification pending.', flush=True)
