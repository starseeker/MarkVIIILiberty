"""Compare fresh mounting prototypes, allowing only generated App::Part UUIDs."""
import argparse
import hashlib
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile

H = Path(__file__).resolve().parent
sys.path.insert(0, str(H.parents[1]))
from lib.evidence import read, write, sha

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, required=True)
p.add_argument('--reproduction', type=Path, required=True)
a = p.parse_args()
roots = [a.candidate.resolve(), a.reproduction.resolve()]
assert roots[0] != roots[1]
data = []
for root in roots:
    report = read(root / 'report.json')
    manifest = read(root / 'isolated/manifest.json')
    native = root / report['native_file']
    assert sha(native) == report['native_sha256'] == manifest['native_sha256']
    with zipfile.ZipFile(native) as archive:
        xml = ET.fromstring(archive.read('Document.xml'))
        shapes = {n: hashlib.sha256(archive.read(n)).hexdigest()
                  for n in archive.namelist() if n.endswith('.brp')}
    types = {v.get('name'): v.get('type') for v in xml.findall('Objects/Object')}
    props = {(v.get('name'), q.get('name')): ET.tostring(q)
             for v in xml.findall('ObjectData/Object') for q in v.findall('Properties/Property')}
    definitions = {n: {k: v for k, v in d.items() if k != 'brep_path'}
                   for n, d in manifest['definitions'].items()}
    data.append((report, manifest, shapes, types, props, definitions))
left, right = data
changed = [key for key in left[4].keys() | right[4].keys()
           if left[4].get(key) != right[4].get(key)]
checks = dict(
    same_controls_and_source=left[0]['controls'] == right[0]['controls']
        and left[0]['parent_native_sha256'] == right[0]['parent_native_sha256']
        and left[0]['input_hashes'] == right[0]['input_hashes'],
    all_definition_shapes_properties_and_frames=left[5] == right[5],
    all_occurrences=left[1]['occurrences'] == right[1]['occurrences'],
    all_assembly_frames_and_children=left[1]['assemblies'] == right[1]['assemblies'],
    all_archive_brep_bytes=left[2] == right[2],
    all_object_types=left[3] == right[3],
    all_stable_persistent_properties=all(prop == 'Uid' and left[3].get(name) == 'App::Part'
                                         for name, prop in changed),
)
result = dict(passed=all(checks.values()), checks=checks,
              native_sha256=left[0]['native_sha256'], reproduction_native_sha256=right[0]['native_sha256'],
              checker_sha256=sha(Path(__file__)), allowed_property_differences=sorted(changed),
              archive_brep_count=len(left[2]), persistent_property_count=len(left[4]),
              reproduction_archive_brep_hashes=right[2],
              scope='Fresh generator run; only generated App::Part Uid values may differ. Geometry, all frames, source metadata and every other persistent property must agree.')
write(roots[0] / 'reproduction_checks.json', result)
print(result)
assert result['passed']
