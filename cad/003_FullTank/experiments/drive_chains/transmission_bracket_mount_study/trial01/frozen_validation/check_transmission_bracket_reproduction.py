"""Compare two independently built, saved bracket-mount trials, accounting for newly generated assembly UUIDs."""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
import uuid


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def archive(path):
    with zipfile.ZipFile(path) as source:
        root = ET.fromstring(source.read('Document.xml'))
        shapes = {name: hashlib.sha256(source.read(name)).hexdigest()
                  for name in source.namelist() if name.endswith('.brp')}
    types = {obj.get('name'): obj.get('type') for obj in root.findall('Objects/Object')}
    properties = {(obj.get('name'), prop.get('name')): ET.tostring(prop)
                  for obj in root.findall('ObjectData/Object')
                  for prop in obj.findall('Properties/Property')}
    return shapes, types, properties


p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, required=True)
p.add_argument('--reproduction', type=Path, required=True)
a = p.parse_args()
roots = [a.candidate.resolve(), a.reproduction.resolve()]
assert roots[0] != roots[1]
manifests, natives, archives = [], [], []
for root in roots:
    report = json.loads((root / 'report.json').read_text())
    native = root / report['native_file']
    manifest = json.loads((root / 'isolated/manifest.json').read_text())
    assert sha(native) == report['native_sha256'] == manifest['native_sha256']
    natives.append(native)
    manifests.append(manifest)
    archives.append(archive(native))

def definitions(manifest):
    return {name: {key: value for key, value in row.items() if key != 'brep_path'}
            for name, row in manifest['definitions'].items()}

left, right = manifests
reports = [json.loads((root / 'report.json').read_text()) for root in roots]
assert reports[0]['input_hashes'] == reports[1]['input_hashes']
assert reports[0]['source_native_sha256'] == reports[1]['source_native_sha256']
assert reports[0]['new_assemblies'] == reports[1]['new_assemblies']
new_assemblies = set(reports[0]['new_assemblies'])
assert len(new_assemblies) == 24
variable_keys = {(name, 'Uid') for name in new_assemblies}
uuid_records = []
for native_index, data in enumerate(archives):
    values = {}
    for (name, prop), raw in data[2].items():
        if prop != 'Uid':
            continue
        element = ET.fromstring(raw)
        assert element.get('type') == 'App::PropertyUUID'
        value = element.find('Uuid').get('value')
        parsed = uuid.UUID(value)
        assert str(parsed) == value.lower()
        values[name] = value
    assert new_assemblies <= values.keys()
    assert len(set(values.values())) == len(values), 'Duplicate assembly UUID'
    assert all(data[1][name] == 'App::Part' for name in new_assemblies)
    uuid_records.append(dict(native_index=native_index, new_assembly_uuids={name:values[name] for name in sorted(new_assemblies)},
                             all_document_uuids_unique=True))
fixed_properties = [{key:value for key,value in data[2].items() if key not in variable_keys}
                    for data in archives]
changed_property_keys = {key for key in archives[0][2] if archives[0][2][key] != archives[1][2].get(key)}

checks = {
    'all_definition_shapes_frames_and_extracted_properties': definitions(left) == definitions(right),
    'all_occurrence_frames_identities_and_owners': left['occurrences'] == right['occurrences'],
    'all_assembly_frames_and_children': left['assemblies'] == right['assemblies'],
    'all_archive_brep_bytes': archives[0][0] == archives[1][0],
    'all_object_types': archives[0][1] == archives[1][1],
    'all_property_keys_retained': archives[0][2].keys() == archives[1][2].keys(),
    'all_persistent_properties_except_new_assembly_uuids': fixed_properties[0] == fixed_properties[1],
    'only_declared_new_assembly_uuids_may_differ': changed_property_keys <= variable_keys,
    'new_assembly_uuids_valid_and_document_wide_unique': all(v['all_document_uuids_unique'] for v in uuid_records),
}
result = dict(
    passed=all(checks.values()), checks=checks,
    native_sha256=sha(natives[0]), reproduction_native_sha256=sha(natives[1]),
    source_native_sha256=json.loads((roots[0] / 'report.json').read_text())['source_native_sha256'],
    checker_sha256=sha(Path(__file__)),
    manifest_sha256=[sha(root / 'isolated/manifest.json') for root in roots],
    definition_count=len(left['definitions']), occurrence_count=len(left['occurrences']),
    assembly_count=len(left['assemblies']), archive_brep_count=len(archives[0][0]),
    object_type_count=len(archives[0][1]), persistent_object_property_count=len(archives[0][2]),
    scope='Fresh nominal bracket-mount rebuild. All geometry, frames, hierarchy, and stable properties must reproduce. Only generated UUID values on the 24 newly created App::Part containers may vary; inherited UUIDs remain exact. No historical qualification.',
    stable_property_count=len(fixed_properties[0]),
    generated_uuid_property_count=len(variable_keys),
    raw_all_property_equality=archives[0][2] == archives[1][2],
    changed_property_keys=sorted(changed_property_keys), uuid_checks=uuid_records,
    installation_qualified=False,
)
(roots[0] / 'reproduction_checks.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
assert result['passed']
