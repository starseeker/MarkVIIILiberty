"""Install the reviewed support-family hypothesis under the rear-channel hierarchy."""
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
prototype = C/'support_family01'
r, pm = read(prototype/'report.json'), read(prototype/'isolated/manifest.json')
source = ROOT/r['parent_native']
parent = source.parent
old, parent_q = read(parent/'isolated/manifest.json'), read(parent/'qualification.json')
trial = prototype/r['native_file']
assert sha(source) == r['parent_native_sha256'] == parent_q['native_sha256']
assert parent_q['local_static_checks_passed']
assert sha(trial) == r['native_sha256'] == pm['native_sha256']
assert all(sha(ROOT/path) == digest for path, digest in r['input_hashes'].items())
receipts = [folder/file for folder in [prototype, C/'support_family_variation01']
            for file in ['independent_checks.json', 'context_checks.json', 'exchange_checks.json']]
receipts.append(prototype/'reproduction_checks.json')
for file in receipts:
    q = read(file)
    assert q['passed'] and q['native_sha256'] == read(file.parent/'report.json')['native_sha256']
for name, candidate in [('support_family_routes01', prototype),
                         ('support_family_routes_variation01', C/'support_family_variation01')]:
    file = C/name/'route_checks.json'
    q = read(file)
    assert q['passed'] and q['trial_native_sha256'] == read(candidate/'report.json')['native_sha256']
    receipts.append(file)
assert read(prototype/'visual_review.json')['disposition'] == 'reviewed_local_approximation'
inputs = [Path(__file__), H.parents[1]/'lib/cad_build.py', prototype/'report.json',
          prototype/'isolated/manifest.json', trial, prototype/'visual_review.json',
          prototype/'render_receipt.json', parent/'qualification.json',
          parent/'isolated/manifest.json', *receipts]
hashes = {str(file.relative_to(ROOT)): sha(file) for file in inputs}
roles = ['high_bracket', 'high_rivet', 'low_bracket', 'low_rivet', 'cleat', 'bolt']
doc = App.openDocument(str(trial))
try:
    shapes = {role: doc.getObject('Def_RearSupport_'+role).Shape.copy()
              for role in roles+['channel', 'floor']}
    attrs = {role: {key: getattr(doc.getObject('Def_RearSupport_'+role), key)
                    for key in ['SourcePartMark', 'SourceRecords', 'SurveyIds']} for role in roles}
finally:
    App.closeDocument(doc.Name)
prior = {v['name']: v for v in old['occurrences']}
role_definitions = {role: prior[name]['definition'] for role, name in [
    ('channel', 'RearControlChannelStock'), ('floor', 'hull_floor_7'),
    ('lock', 'RearChannelLeftCleat1LockWasher'), ('nut', 'RearChannelLeftCleat1Nut')]}
out.mkdir(parents=True)
doc = App.openDocument(str(source))
added = {'Definitions': [], 'RearControlChannel': []}
expected, receiver_features, added_properties = {}, {}, {}
for role in roles:
    body = doc.addObject('PartDesign::Body', 'Def_RearSupport_'+role)
    doc.Definitions.addObject(body)
    body.newObject('PartDesign::Feature', 'ReconstructedRearSupport').Shape = shapes[role]
    metadata(body, **attrs[role], DefinitionKey='rear_support_'+role, Representation='assembly',
             Coverage='reconstruction_trial',
             ParameterUpdate='Regenerate support_family_controls01.json with trial_rear_support_family.py, then build_rear_support_family.py',
             ReconstructionStatus='Reviewed static approximation: M4129 outline and shared M4136 rivet attachment remain inferred; rods, springs and service routes incomplete.')
    role_definitions[role] = body.Name
    added['Definitions'].append(body.Name)
for role in ['channel', 'floor']:
    body = doc.getObject(role_definitions[role])
    assert body.Placement.isIdentity()
    receiver_features[role] = body.Tip.Name
    body.Tip.Shape = shapes[role]
    fields = dict(SupportFamilySourceRecords=['SNL:33:005'],
                  SupportFamilyUpdate='M4135/M4136/M4129 support-family receiving passages; regenerate support_family_controls01.json.')
    # Use the actual M4135 rivet record from its reviewed packet.
    if role == 'channel':
        fields['SupportFamilySourceRecords'] = sorted(set(r['record_ids']['high_rivet']+r['record_ids']['low_rivet']))
    metadata(body, **fields)
    added_properties[body.Name] = sorted(fields)
groups = sorted({spec['owner'] for spec in r['specs'].values()}-{'Root'})
for key in groups:
    group = doc.addObject('App::Part', key)
    doc.RearControlChannel.addObject(group)
    group.Uid = str(uuid.uuid5(uuid.NAMESPACE_URL, 'markviii:installed-rear-support:'+key))
    group.Placement = doc.RearControlChannel.getGlobalPlacement().inverse().multiply(
        App.Placement(App.Matrix(*pm['assemblies'][key]['world'])))
    metadata(group, Coverage='reconstruction_trial',
             ReconstructionStatus='Static support-family approximation; complete rods, springs and service remain pending.')
    added['RearControlChannel'].append(key)
for row in pm['occurrences']:
    name = row['name']
    spec = r['specs'][name]
    role = spec['role']
    if role in ['channel', 'floor']:
        continue
    group = doc.getObject(spec['owner'])
    link = doc.addObject('App::Link', name)
    group.addObject(link)
    link.setLink(doc.getObject(role_definitions[role]))
    link.LinkPlacement = group.getGlobalPlacement().inverse().multiply(App.Placement(App.Matrix(*row['frame'])))
    metadata(link, OccurrenceId=name, Subsystem='Drivetrain',
             SourceRecords=r['record_ids'][role], Coverage='reconstruction_trial')
    expected[name] = dict(definition=role_definitions[role], role=role, frame=row['frame'],
                          owners=['Root', 'RearControlChannel', spec['owner']], prototype_occurrence=name)
    added.setdefault(group.Name, []).append(name)
doc.Root.Label = 'Powertrain development — rear control support family'
doc.Root.RegistrationStatus = 'M4135/M4136 spring supports and two estimated M4129 right-cleat attachments installed. Complete rods, springs, service paths and standard integration remain open.'
doc.Definitions.Visibility = False
doc.recompute()
native = out/'PowertrainWithRearControlSupports.FCStd'
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
      new_definitions=added['Definitions'],
      shared_definitions={k: role_definitions[k] for k in ['lock', 'nut']},
      role_definitions=role_definitions, added_inherited_properties=added_properties,
      changed_definitions=[role_definitions[k] for k in ['channel', 'floor']],
      changed_receiver_features=receiver_features,
      affected_occurrences=sorted(expected)+['RearControlChannelStock', 'hull_floor_7'],
      expected_physical_occurrences=3246, expected_definition_count=564, expected_assembly_count=353,
      historical_geometry_qualified=False, installation_qualified=False,
      standard_assembly_modified=False, channel_complete=False, packet_complete=False))
print('Saved3246 occurrences/564 used definitions/353 groups; qualification pending.', flush=True)
