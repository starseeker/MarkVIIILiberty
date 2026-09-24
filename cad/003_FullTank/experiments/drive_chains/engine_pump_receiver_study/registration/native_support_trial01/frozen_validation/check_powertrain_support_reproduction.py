"""Compare two independently built, saved support trials without loading FreeCAD."""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile


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
checks = {
    'all_definition_shapes_frames_and_extracted_properties': definitions(left) == definitions(right),
    'all_occurrence_frames_identities_and_owners': left['occurrences'] == right['occurrences'],
    'all_assembly_frames_and_children': left['assemblies'] == right['assemblies'],
    'all_archive_brep_bytes': archives[0][0] == archives[1][0],
    'all_object_types': archives[0][1] == archives[1][1],
    'all_persistent_object_properties': archives[0][2] == archives[1][2],
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
    scope='Fresh nominal support rebuild from the same frozen phase trial; no new parameter variation or historical qualification.',
    installation_qualified=False,
)
(roots[0] / 'reproduction_checks.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
assert result['passed']
