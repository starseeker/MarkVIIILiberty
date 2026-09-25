"""Install two reviewed straight rods and explicitly propagate receiver revisions."""
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
prototype = C/'track_rods02'
r, pm = read(prototype/'report.json'), read(prototype/'isolated/manifest.json')
source = ROOT/r['parent_native']
parent = source.parent
old, parent_q = read(parent/'isolated/manifest.json'), read(parent/'qualification.json')
trial = prototype/r['native_file']
assert sha(source) == r['parent_native_sha256'] == parent_q['native_sha256'] == old['native_sha256']
assert parent_q['local_static_checks_passed']
assert sha(trial) == r['native_sha256'] == pm['native_sha256']
assert all(sha(ROOT/f) == h for f, h in r['input_hashes'].items())
receipts = [folder/file for folder in [prototype, C/'track_rods_variation02']
            for file in ['independent_checks.json', 'context_checks.json', 'exchange_checks.json']]
receipts.append(prototype/'reproduction_checks.json')
for file in receipts:
    q = read(file)
    assert q['passed'] and q['native_sha256'] == read(file.parent/'report.json')['native_sha256']
assert read(prototype/'visual_review.json')['disposition'] == 'reviewed_local_approximation'
inputs = [Path(__file__), H.parents[1]/'lib/cad_build.py', prototype/'report.json',
          prototype/'isolated/manifest.json', prototype/'operating_interfaces.json', trial,
          prototype/'visual_review.json', prototype/'render_receipt.json',
          parent/'qualification.json', parent/'isolated/manifest.json', *receipts]
hashes = {str(f.relative_to(ROOT)): sha(f) for f in inputs}
doc = App.openDocument(str(trial))
try:
    shapes = {key: doc.getObject(key).Shape.copy() for key in [*r['changed_definitions'], 'Def_RearTrackRod']}
finally:
    App.closeDocument(doc.Name)
prior = {v['name']: v for v in old['occurrences']}
out.mkdir(parents=True)
doc = App.openDocument(str(source))
added = {'Definitions': ['Def_RearTrackRod']}
added_properties = {}
for key in r['changed_definitions']:
    body = doc.getObject(key)
    assert body.Placement.isIdentity() and not hasattr(body, 'TrackRodClosureUpdate')
    body.Tip.Shape = shapes[key]
    metadata(body, TrackRodClosureUpdate='Regenerate track_rod_controls02.json with trial_rear_track_rods_aligned.py, then build_rear_track_rods.py. This supersedes the earlier lower-arm profile; source interfaces and remaining estimates are in track_rods_integrated01/qualification.json.')
    added_properties[key] = ['TrackRodClosureUpdate']
body = doc.addObject('PartDesign::Body', 'Def_RearTrackRod')
doc.Definitions.addObject(body)
body.newObject('PartDesign::Feature', 'ReconstructedTrackRod').Shape = shapes[body.Name]
metadata(body, SourcePartMark='SH946D', SourceRecords=['SNL:194:024'],
         SurveyIds=['P_d5273914c505d2bc'], DefinitionKey='rear_track_connecting_rod',
         Representation='assembly', Coverage='reconstruction_trial',
         ParameterUpdate='Regenerate track_rod_controls02.json with trial_rear_track_rods_aligned.py, then build_rear_track_rods.py',
         ReconstructionStatus='Straight solid rod with nominal male threads; length, section and receiver profiles inferred. No full motion/service qualification.')
for name, frame in r['joint_frames'].items():
    group = doc.getObject(name)
    side = 'Starboard' if name.startswith('Starboard') else 'Port'
    owner = doc.getObject(side+'TrackShortConnection')
    group.Placement = owner.getGlobalPlacement().inverse().multiply(App.Placement(App.Matrix(*frame)))
for side in ['Starboard', 'Port']:
    name = side+'TrackHorizontalLever'
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
        metadata(link, OccurrenceId=name, Subsystem='Drivetrain', SourceRecords=['SNL:194:024'], Coverage='reconstruction_trial')
        added.setdefault(owner.Name, []).append(name)
        owners = ['Root', 'RearControlChannel', owner.Name]
    else:
        owners = prior[name]['owners']
    expected[name] = dict(definition=spec['definition'], role=spec['role'], frame=spec['frame'],
                          owners=owners, prototype_occurrence=name)
    if name in r['new_occurrences']:
        expected_new[name] = expected[name]
doc.Root.Label = 'Powertrain development — straight rear track connections'
doc.Root.RegistrationStatus = 'Two SH946D rods installed. Shared M330 lower arms and M4132 short arms/clocks revised for straight-rod closure. Low-speed shared-pin conflict, return springs, long controls, service and standard integration remain open.'
doc.Definitions.Visibility = False
doc.recompute()
native = out/'PowertrainWithRearTrackRods.FCStd'
doc.saveAs(str(native))
App.closeDocument(doc.Name)
assert sha(source) == r['parent_native_sha256']
assert all(sha(ROOT/f) == h for f, h in hashes.items())
frozen = out/'frozen_inputs'
frozen.mkdir()
for file in inputs:
    if file.suffix != '.FCStd':
        shutil.copy2(file, frozen/str(file.relative_to(ROOT)).replace('/', '__'))
write(out/'report.json', dict(native_file=native.name, native_sha256=sha(native),
      source_native=str(source.relative_to(ROOT)), source_native_sha256=sha(source),
      prototype=str(prototype.relative_to(ROOT)), prototype_native_sha256=sha(trial),
      input_hashes=hashes, controls=r['controls'], details=r['details'],
      expected_new_occurrences=expected_new, expected_affected_occurrences=expected,
      affected_occurrences=sorted(expected), changed_definitions=r['changed_definitions'],
      new_definitions=['Def_RearTrackRod'], new_assemblies=[], added_children=added,
      added_inherited_properties=added_properties, changed_group_frames=r['joint_frames'],
      changed_link_frames={side+'TrackHorizontalLever': r['specs'][side+'TrackHorizontalLever']['frame']
                           for side in ['Starboard', 'Port']},
      placement_changed_objects=sorted(r['joint_frames'])+[side+'TrackHorizontalLever' for side in ['Starboard', 'Port']],
      expected_physical_occurrences=3264, expected_definition_count=568, expected_assembly_count=359,
      historical_geometry_qualified=False, installation_qualified=False,
      standard_assembly_modified=False, channel_complete=False, packet_complete=False))
print('Saved3264 occurrences/568 definitions/359 groups; qualification pending.', flush=True)
