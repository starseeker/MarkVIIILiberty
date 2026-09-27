"""Append a qualified additive control prototype without changing inherited parts."""
import argparse
from pathlib import Path
import shutil, uuid
from control_rebuild_io_v2 import App, ROOT, H, Saved, pose, read, write, sha
from lib.cad_build import metadata

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--prototype', type=Path, required=True)
p.add_argument('--variation', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
prototype, variation = Saved(a.prototype), Saved(a.variation)
r = prototype.report
assert not r['changed_definitions']
parent = Saved((ROOT/r['parent_native']).parent)
assert sha(parent.native) == r['parent_native_sha256']
assert read(parent.folder/'qualification.json')['local_static_checks_passed']
assert all(sha(ROOT/f) == h for f, h in r['input_hashes'].items())
receipts = []
for trial in [prototype, variation]:
    for name in ['checks03/independent_checks.json', 'context_audit/report.json', 'exchange01/exchange_checks.json']:
        receipt = trial.folder/name
        q = read(receipt)
        assert q['passed'] and q['native_sha256'] == sha(trial.native)
        receipts.append(receipt)
repro = prototype.folder/'reproduction_checks.json'
assert read(repro)['passed'] and read(repro)['native_sha256'] == sha(prototype.native)
visual = prototype.folder/'visual_review.json'
assert read(visual)['disposition'] == 'reviewed_local_approximation'
assert read(visual)['native_sha256'] == sha(prototype.native)
inputs = [Path(__file__), H/'control_rebuild_io_v2.py', H.parents[1]/'lib/cad_build.py',
          prototype.folder/'report.json', prototype.folder/'isolated/manifest.json',
          prototype.native, variation.folder/'report.json', parent.folder/'qualification.json',
          parent.folder/'isolated/manifest.json', visual, prototype.folder/'render_receipt.json',
          repro, *receipts]
hashes = {str(f.relative_to(ROOT)): sha(f) for f in inputs}
doc = App.openDocument(str(prototype.native))
try:
    properties = {key: {k: getattr(doc.getObject(key), k) for k in doc.getObject(key).PropertiesList
                       if doc.getObject(key).getGroupOfProperty(k) == 'Reconstruction'}
                  for key in r['new_definitions']}
finally:
    App.closeDocument(doc.Name)

out = a.output.resolve()
out.mkdir(parents=True, exist_ok=False)
doc = App.openDocument(str(parent.native))
added = {'Definitions': []}
for key in r['new_definitions']:
    assert doc.getObject(key) is None
    body = doc.addObject('PartDesign::Body', key)
    doc.Definitions.addObject(body)
    body.newObject('PartDesign::Feature', 'ReconstructedControlPart').Shape = prototype.definition(key)
    metadata(body, **properties[key])
    added['Definitions'].append(key)
for name, spec in r['new_assembly_specs'].items():
    assert doc.getObject(name) is None
    owner = doc.getObject(spec['owner'])
    group = doc.addObject('App::Part', name)
    owner.addObject(group)
    group.Uid = str(uuid.uuid5(uuid.NAMESPACE_URL, 'markviii:driver-control-foundation:'+name))
    group.Placement = owner.getGlobalPlacement().inverse().multiply(pose(spec['frame']))
    metadata(group, Coverage='reconstruction_trial', Subsystem='Drivetrain')
    added.setdefault(owner.Name, []).append(name)
expected = {}
for name in r['new_occurrences']:
    assert name not in parent.rows and doc.getObject(name) is None
    spec = r['specs'][name]
    owner = doc.getObject(spec['owner'])
    assert owner is not None and owner.TypeId == 'App::Part'
    link = doc.addObject('App::Link', name)
    owner.addObject(link)
    link.setLink(doc.getObject(spec['definition']))
    link.LinkPlacement = owner.getGlobalPlacement().inverse().multiply(pose(spec['frame']))
    metadata(link, OccurrenceId=name, Subsystem='HullStructure' if name.startswith('hull_floor_') else 'Drivetrain', Coverage='reconstruction_trial',
             SourceRecords=spec.get('source_records', prototype.manifest['definitions'][spec['definition']]['properties'].get('SourceRecords', [])))
    added.setdefault(owner.Name, []).append(name)
    # Recover the existing hierarchy from the parent's assembly graph.
    owners = [owner.Name]
    while owners[0] != 'Root':
        ancestors = ([r['new_assembly_specs'][owners[0]]['owner']] if owners[0] in r['new_assembly_specs'] else [n for n, g in parent.manifest['assemblies'].items() if owners[0] in g['children']])
        assert len(ancestors) == 1, (name, ancestors)
        owners.insert(0, ancestors[0])
    expected[name] = dict(definition=spec['definition'], frame=spec['frame'], owners=owners)

doc.Root.Label = 'Powertrain development — driver support foundation'
doc.Root.RegistrationStatus = 'Two source-counted driver shafts/retainers, partial M786/M787 side plates and eight source-length floor bolt sets. Static mounting-interface hypothesis; seat attachments, controls and actual front rod receivers remain pending.'
doc.Definitions.Visibility = False
doc.recompute()
native = out/'PowertrainControlRebuild.FCStd'
doc.saveAs(str(native))
App.closeDocument(doc.Name)
assert sha(parent.native) == r['parent_native_sha256']
assert all(sha(ROOT/f) == h for f, h in hashes.items())
frozen = out/'frozen_inputs'
frozen.mkdir()
for file in inputs:
    if file.suffix != '.FCStd':
        shutil.copy2(file, frozen/str(file.relative_to(ROOT)).replace('/', '__'))
write(out/'report.json', dict(native_file=native.name, native_sha256=sha(native),
      source_native=str(parent.native.relative_to(ROOT)), source_native_sha256=sha(parent.native),
      parent_native=str(parent.native.relative_to(ROOT)), parent_native_sha256=sha(parent.native),
      prototype=str(prototype.folder.relative_to(ROOT)), prototype_native_sha256=sha(prototype.native),
      variation=str(variation.folder.relative_to(ROOT)), input_hashes=hashes, details=r['details'],
      expected_new_occurrences=expected, new_occurrences=r['new_occurrences'],
      new_definitions=r['new_definitions'], changed_definitions=r['changed_definitions'], added_children=added, new_assembly_specs=r['new_assembly_specs'],
      expected_physical_occurrences=len(parent.rows)+len(expected),
      expected_definition_count=len(parent.manifest['definitions'])+len(r['new_definitions']),
      expected_assembly_count=len(parent.manifest['assemblies'])+len(r['new_assembly_specs']),
      historical_geometry_qualified=False, installation_qualified=False,
      standard_assembly_modified=False, packet_complete=False))
print('Saved additive development checkpoint; validation pending.', flush=True)
