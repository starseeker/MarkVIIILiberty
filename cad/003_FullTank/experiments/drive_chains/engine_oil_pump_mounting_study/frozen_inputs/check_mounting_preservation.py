"""Bind the mounting delta to the saved 105-component checkpoint."""
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as E
import zipfile

ROOT = Path('/home/cyapp/MarkVIIILiberty')
BASE = ROOT/'cad/003_FullTank/experiments/drive_chains'
out = BASE/'engine_oil_pump_mounting_study'
sha = lambda data: hashlib.sha256(data).hexdigest()


def read(folder):
    report = json.loads((folder/'report.json').read_text())
    native = folder/report['native_file']
    assert sha(native.read_bytes()) == report['native_sha256']
    with zipfile.ZipFile(native) as z:
        assert z.testzip() is None
        tree = E.fromstring(z.read('Document.xml'))
        objects = tree.findall('./ObjectData/Object')
        props = {o.get('name'): {p.get('name'): E.tostring(p).decode()
                 for p in o.findall('./Properties/Property')} for o in objects}
        shapes = {o.get('name'): sha(z.read(p.get('file'))) for o in objects
                  for p in o.findall('./Properties/Property[@name="Shape"]/Part')
                  if p.get('file')}
    return report, props, shapes


before = read(BASE/'engine_oil_pump_relief_lock_study')
after = read(out)
changed = [k for k, v in before[2].items() if after[2].get(k) != v]
added = sorted(set(after[2])-set(before[2]))
keys = ['Placement', 'LinkPlacement', 'LinkedObject', 'SourceRecords',
        'SourcePartMark', 'DefinitionKey', 'PhysicalRole', 'Scale',
        'ScaleVector', 'Visibility']
objects = (['Def_'+k for k in before[0]['definition_order']]
           + [o['name'] for o in before[0]['occurrences']]
           + before[0]['groups'] + ['Root', 'EngineOilPump', 'Definitions',
                                    'ReliefLockCenterline'])
changed_props = []
checked_props = 0
for name in objects:
    for key in keys:
        if key in before[1][name]:
            checked_props += 1
            if before[1][name][key] != after[1].get(name, {}).get(key):
                changed_props.append([name, key])
baseline = json.loads((ROOT/'.work/engine-oil-pump/mounting_preservation_baseline.json').read_text())
altered_files = [name for name, digest in baseline.items()
                 if sha((ROOT/name).read_bytes()) != digest]
checks = dict(only_lower_casting_changed=set(changed)=={'Def_lower_body', 'ReconstructedOilPump011'},
              only_stud_and_gasket_definitions_added=set(added)=={'Def_mount_stud', 'Def_mount_gasket', 'ReconstructedOilPump038', 'ReconstructedOilPump039'},
              old_frames_and_identities_preserved=not changed_props,
              prior_occurrences_preserved=before[0]['occurrences']==after[0]['occurrences'][:105],
              added_physical_count=after[0]['physical_count']-before[0]['physical_count']==41,
              standard_and_prior_artifacts_preserved=not altered_files)
result = dict(passed=all(checks.values()), checks=checks,
              prior_native_sha256=before[0]['native_sha256'], native_sha256=after[0]['native_sha256'],
              changed_serialized_shapes=changed, added_serialized_shapes=added,
              unchanged_serialized_shapes=len(before[2])-len(changed),
              checked_frame_identity_properties=checked_props, changed_properties=changed_props,
              preserved_files=baseline, altered_files=altered_files,
              scope='Old physical frames and identity properties; generated Origin names are not treated as stable physical identities. Full fresh-rebuild equality is checked separately.')
(out/'preservation_checks.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='preserved_files'}, indent=2))
assert result['passed']
