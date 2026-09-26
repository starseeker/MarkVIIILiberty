"""Install reviewed M569A/M568A low-speed end joints, preserving all inherited geometry."""
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
prototype = C/'low_joints01'
r, pm = read(prototype/'report.json'), read(prototype/'isolated/manifest.json')
source = ROOT/r['parent_native']
parent = source.parent
old, parent_q = read(parent/'isolated/manifest.json'), read(parent/'qualification.json')
trial = prototype/r['native_file']
assert sha(source) == r['parent_native_sha256'] == parent_q['native_sha256']
assert parent_q['local_static_checks_passed']
assert sha(trial) == r['native_sha256'] == pm['native_sha256']
assert all(sha(ROOT/path) == digest for path, digest in r['input_hashes'].items())
receipts = [folder/file for folder in [prototype, C/'low_joints_variation01']
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

doc = App.openDocument(str(trial))
try:
    fork_shape = doc.getObject('Def_LowJoint_fork').Shape.copy()
    fork_attrs = {key: getattr(doc.getObject('Def_LowJoint_fork'), key)
                  for key in ['SourcePartMark', 'SourceRecords', 'SurveyIds']}
finally:
    App.closeDocument(doc.Name)

role_definitions = dict(fork='Def_LowJoint_fork',
                        pin='Def_ControlJoint_pin',
                        cotter='Def_ControlJoint_cotter',
                        nut='Def_USStdControlNut')
assert all(role_definitions[k] in old['definitions'] for k in ['pin', 'cotter', 'nut'])
records = dict(fork=['SNL:87:002'], pin=['SNL:136:007'], cotter=['SNL:136:008'], nut=['SNL:194:025'])

out.mkdir(parents=True)
doc = App.openDocument(str(source))
added = {'Definitions': [], 'RearControlChannel': []}
expected, groups = {}, []

body = doc.addObject('PartDesign::Body', 'Def_LowJoint_fork')
doc.Definitions.addObject(body)
body.newObject('PartDesign::Feature', 'ReconstructedLowJoint').Shape = fork_shape
metadata(body, **fork_attrs, DefinitionKey='rear_low_joint_fork',
         Representation='assembly', Coverage='reconstruction_trial',
         ParameterUpdate='Regenerate low_joint_controls01.json with trial_rear_low_joints.py, then build_rear_low_joints.py',
         ReconstructionStatus='Reviewed static approximation; M569A fork profile (throat_to_rod_seat datum), common M568A pin. SH946E rods and final closure pending.')
added['Definitions'].append(body.Name)

for side in ['Starboard', 'Port']:
    name = side+'LowShortConnection'
    connection = doc.addObject('App::Part', name)
    doc.RearControlChannel.addObject(connection)
    connection.Uid = str(uuid.uuid5(uuid.NAMESPACE_URL, 'markviii:low-short-connection:'+name))
    metadata(connection, SourcePartMark='SH946E', SourceRecords=['SNL:195:019'],
             Coverage='reconstruction_trial',
             ReconstructionStatus='Two installed end joints only; shared physical connecting rod pending.')
    groups.append(name)
    added['RearControlChannel'].append(name)
    added[name] = []
    for end in ['Brake', 'Fulcrum']:
        key = side+'Low'+end+'Joint'
        group = doc.addObject('App::Part', key)
        connection.addObject(group)
        group.Uid = str(uuid.uuid5(uuid.NAMESPACE_URL, 'markviii:installed-low-joint:'+key))
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
             SourceRecords=records[role], Coverage='reconstruction_trial')
    expected[name] = dict(definition=role_definitions[role], role=role, frame=row['frame'],
                          owners=['Root', 'RearControlChannel', side+'LowShortConnection', owner],
                          prototype_occurrence=name)
    added[owner].append(name)

doc.Root.Label = 'Powertrain development — rear low-speed end joints'
doc.Root.RegistrationStatus = 'Four M569A/M568A fork joints installed. Physical SH946E rods, springs, long rods, center/front controls and standard integration remain open.'
doc.Definitions.Visibility = False
doc.recompute()
native = out/'PowertrainWithRearLowJoints.FCStd'
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
      input_hashes=hashes, controls=r['controls'], details=r['joint_details'],
      expected_new_occurrences=expected, new_assemblies=groups, added_children=added,
      new_definitions=added['Definitions'],
      shared_definitions=dict(nut=role_definitions['nut'], pin=role_definitions['pin'], cotter=role_definitions['cotter']),
      role_definitions=role_definitions, record_ids=records,
      added_inherited_properties={}, changed_definitions=[],
      affected_occurrences=sorted(expected), expected_physical_occurrences=3280,
      expected_definition_count=569, expected_assembly_count=365,
      historical_geometry_qualified=False, installation_qualified=False,
      standard_assembly_modified=False, channel_complete=False, packet_complete=False))
print('Saved 3280 occurrences/569 definitions/365 groups; qualification pending.', flush=True)
