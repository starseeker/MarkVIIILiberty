"""Install reviewed M569C/M568C end joints, preserving all inherited geometry."""
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
C = H/'transmission_controls_study'
prototype = C/'track_joints02'
r, pm = read(prototype/'report.json'), read(prototype/'isolated/manifest.json')
source = ROOT/r['parent_native']
parent = source.parent
old, parent_q = read(parent/'isolated/manifest.json'), read(parent/'qualification.json')
trial = prototype/r['native_file']
assert sha(source) == r['parent_native_sha256'] == parent_q['native_sha256']
assert parent_q['local_static_checks_passed']
assert sha(trial) == r['native_sha256'] == pm['native_sha256']
assert all(sha(ROOT/path) == digest for path, digest in r['input_hashes'].items())
receipts = [folder/file for folder in [prototype, C/'track_joints_variation02']
            for file in ['independent_checks.json', 'context_checks.json', 'exchange_checks.json']]
receipts.append(prototype/'reproduction_checks.json')
for file in receipts:
    q = read(file)
    assert q['passed'] and q['native_sha256'] == read(file.parent/'report.json')['native_sha256']
assert read(prototype/'visual_review.json')['disposition'] == 'reviewed_local_approximation'
inputs = [Path(__file__), H.parents[1]/'lib/cad_build.py', prototype/'report.json',
          prototype/'isolated/manifest.json', trial, prototype/'visual_review.json',
          prototype/'render_receipt.json', parent/'qualification.json',
          parent/'isolated/manifest.json', *receipts]
hashes = {str(file.relative_to(ROOT)): sha(file) for file in inputs}
roles = ['fork', 'pin', 'cotter']
doc = App.openDocument(str(trial))
try:
    shapes = {role: doc.getObject('Def_TrackJoint_'+role).Shape.copy() for role in roles}
    attrs = {role: {key: getattr(doc.getObject('Def_TrackJoint_'+role), key)
                    for key in ['SourcePartMark', 'SourceRecords', 'SurveyIds']} for role in roles}
finally:
    App.closeDocument(doc.Name)
role_definitions = dict(nut=r['shared_definitions']['nut'])
assert role_definitions['nut'] in old['definitions']
out.mkdir(parents=True)
doc = App.openDocument(str(source))
added = {'Definitions': [], 'RearControlChannel': []}
expected, groups = {}, []
for role in roles:
    body = doc.addObject('PartDesign::Body', 'Def_TrackJoint_'+role)
    doc.Definitions.addObject(body)
    body.newObject('PartDesign::Feature', 'ReconstructedTrackJoint').Shape = shapes[role]
    metadata(body, **attrs[role], DefinitionKey='rear_track_joint_'+role,
             Representation='assembly', Coverage='reconstruction_trial',
             ParameterUpdate='Regenerate track_joint_controls02.json with trial_rear_track_joints.py, then build_rear_track_joints.py',
             ReconstructionStatus='Reviewed static approximation; M569C throat/socket and M568C diameter estimated. SH946D rods and final fork angles pending.')
    role_definitions[role] = body.Name
    added['Definitions'].append(body.Name)
for side in ['Starboard', 'Port']:
    name = side+'TrackShortConnection'
    connection = doc.addObject('App::Part', name)
    doc.RearControlChannel.addObject(connection)
    connection.Uid = str(uuid.uuid5(uuid.NAMESPACE_URL, 'markviii:track-short-connection:'+name))
    metadata(connection, SourcePartMark='SH946D', SourceRecords=['SNL:194:023'],
             Coverage='reconstruction_trial',
             ReconstructionStatus='Two installed end joints only; shared physical connecting rod and final angular closure pending.')
    groups.append(name)
    added['RearControlChannel'].append(name)
    added[name] = []
    for end in ['Brake', 'Fulcrum']:
        key = side+'Track'+end+'Joint'
        group = doc.addObject('App::Part', key)
        connection.addObject(group)
        group.Uid = str(uuid.uuid5(uuid.NAMESPACE_URL, 'markviii:installed-track-joint:'+key))
        group.Placement = connection.getGlobalPlacement().inverse().multiply(
            App.Placement(App.Matrix(*pm['assemblies'][key]['world'])))
        metadata(group, Coverage='reconstruction_trial',
                 ReconstructionStatus='Static pin-centered joint; horizontal socket axis provisional pending rod closure.')
        groups.append(key)
        added[name].append(key)
        added[key] = []
for row in pm['occurrences']:
    name = row['name']
    spec = r['specs'][name]
    role, owner = spec['role'], spec['owner']
    side = 'Starboard' if name.startswith('Starboard') else 'Port'
    group = doc.getObject(owner)
    link = doc.addObject('App::Link', name)
    group.addObject(link)
    link.setLink(doc.getObject(role_definitions[role]))
    link.LinkPlacement = group.getGlobalPlacement().inverse().multiply(App.Placement(App.Matrix(*row['frame'])))
    metadata(link, OccurrenceId=name, Subsystem='Drivetrain',
             SourceRecords=r['record_ids'][role], Coverage='reconstruction_trial')
    expected[name] = dict(definition=role_definitions[role], role=role, frame=row['frame'],
                          owners=['Root', 'RearControlChannel', side+'TrackShortConnection', owner],
                          prototype_occurrence=name)
    added[owner].append(name)
doc.Root.Label = 'Powertrain development — rear track-control end joints'
doc.Root.RegistrationStatus = 'Four M569C/M568C fork joints installed. Physical SH946D rods, low-speed shared-pin reconciliation, springs, service and standard integration remain open.'
doc.Definitions.Visibility = False
doc.recompute()
native = out/'PowertrainWithRearTrackJoints.FCStd'
doc.saveAs(str(native))
App.closeDocument(doc.Name)
assert sha(source) == r['parent_native_sha256']
assert all(sha(ROOT/file) == digest for file, digest in hashes.items())
frozen = out/'frozen_inputs'
frozen.mkdir()
for file in inputs:
    if file.suffix != '.FCStd':
        shutil.copy2(file, frozen/str(file.relative_to(ROOT)).replace('/', '__'))
write(out/'report.json', dict(native_file=native.name, native_sha256=sha(native),
      source_native=str(source.relative_to(ROOT)), source_native_sha256=sha(source),
      prototype=str(prototype.relative_to(ROOT)), prototype_native_sha256=sha(trial),
      input_hashes=hashes, controls=r['controls'], details=r['details'],
      expected_new_occurrences=expected, new_assemblies=groups, added_children=added,
      new_definitions=added['Definitions'], shared_definitions={'nut': role_definitions['nut']},
      role_definitions=role_definitions, added_inherited_properties={}, changed_definitions=[],
      affected_occurrences=sorted(expected), expected_physical_occurrences=3262,
      expected_definition_count=567, expected_assembly_count=359,
      historical_geometry_qualified=False, installation_qualified=False,
      standard_assembly_modified=False, channel_complete=False, packet_complete=False))
print('Saved3262 occurrences/567 definitions/359 groups; qualification pending.', flush=True)
