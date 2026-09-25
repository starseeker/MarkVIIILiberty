"""Bind the integrated control-pin family to the tested prototype and preserve inherited frames and metadata."""
import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path.insert(0, str(H.parents[1]))
import FreeCAD as App
import Part
from lib.evidence import read, write, sha
from lib.camera_review import validate_native_bindings

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, required=True)
a = p.parse_args()
out = a.candidate.resolve()
r = read(out / 'report.json')
native = out / r['native_file']
source = ROOT / r['source_native']
prototype = ROOT / r['prototype']
pr = read(prototype / 'report.json')
m, old, pm = [read(path / 'isolated/manifest.json') for path in [out, source.parent, prototype]]
assert sha(native) == r['native_sha256'] == m['native_sha256']
assert sha(source) == r['source_native_sha256'] == old['native_sha256']
assert sha(prototype / pr['native_file']) == r['prototype_native_sha256'] == pm['native_sha256']
assert all(sha(ROOT / f) == digest for f, digest in r['input_hashes'].items())
rows, prior, trial = [{v['name']: v for v in data['occurrences']} for data in [m, old, pm]]
checks = []
def ck(name, passed, **detail):
    checks.append(dict(name=name, passed=bool(passed), **detail))
def close(a, b):
    return len(a) == len(b) and max(abs(x-y) for x, y in zip(a, b)) < 1e-7

ck('3264 occurrences,568 definitions,359 groups; no additions',
   len(rows) == 3264 and len(m['definitions']) == 568 and len(m['assemblies']) == 359
   and set(rows) == set(prior) and set(m['definitions']) == set(old['definitions']))
ck('All3264 inherited targets, owners and world frames retained',
   all(rows[n]['definition'] == v['definition'] and rows[n]['owners'] == v['owners']
       and close(rows[n]['frame'], r['expected_affected_occurrences'].get(n, v)['frame']) for n, v in prior.items()))
ck('All inherited group members retained',
   set(m['assemblies']) == set(old['assemblies']) and
   all(set(m['assemblies'][n]['children']) == set(g['children']) | set(r['added_children'].get(n, []))
       for n, g in old['assemblies'].items()))
for n, g in old['assemblies'].items():
    if n in r['changed_group_frames']:
        ck(n+' matches reviewed world frame', close(m['assemblies'][n]['world'], r['changed_group_frames'][n]))
    else:
        assert close(g['world'], m['assemblies'][n]['world']) and close(g['local'], m['assemblies'][n]['local']), n
ck('All16 checked frames, definitions and owners match saved prototype',
   all(rows[n]['definition'] == spec['definition'] and rows[n]['owners'] == spec['owners']
       and close(rows[n]['frame'], trial[n]['frame']) for n, spec in r['expected_affected_occurrences'].items()))
with tempfile.TemporaryDirectory(prefix='relocated_mounts_', dir=out) as directory:
    relocated = Path(directory) / native.name
    shutil.copy2(native, relocated)
    validate_native_bindings(dict(native_file=str(relocated), render_occurrences=list(rows), landmarks=[]), m)
    doc = App.openDocument(str(relocated))
    try:
        ck('All3264 installed links reopen with local identity definitions',
           all(doc.getObject(v['object']).LinkedObject.Document == doc
               and doc.getObject(v['object']).LinkedObject.Placement.isIdentity() for v in rows.values()))
        ck('Both high-speed joints reuse one source-identified M568A definition',
           sum(v['definition'] == 'Def_ControlJoint_pin' for v in rows.values()) == 2
           and doc.Def_ControlJoint_pin.SourcePartMark == 'M568A')
    finally:
        App.closeDocument(doc.Name)
cache = {}
def definition(key, manifest):
    d = manifest['definitions'][key]
    digest = d['brep_sha256']
    if digest not in cache:
        assert sha(d['brep_path']) == digest
        s = Part.Shape()
        s.read(d['brep_path'])
        assert s.Placement.isIdentity()
        cache[digest] = s
    return cache[digest].copy()
def material(s):
    return sum(abs(v.Volume) for v in s.Solids)
def same_material(one, two):
    missing, added = one.cut(two), two.cut(one)
    fuzzy = one.cut(two, 1e-4), two.cut(one, 1e-4)
    return dict(passed=one.isValid() and two.isValid()
                and len(one.Solids) == len(two.Solids) == 1
                and one.Solids[0].isClosed() and two.Solids[0].isClosed()
                and one.getTolerance(1) <= 1e-4 and two.getTolerance(1) <= 1e-4
                and material(missing) < 1e-5 and material(added) < 1e-5
                and all(not d.Faces for d in fuzzy),
                missing_mm3=material(missing), added_mm3=material(added))
for key in pm['definitions']:
    result = same_material(definition(key, pm), definition(key, m))
    ck(key + ' definition retains tested prototype material', **result)
for name in trial:
    one = definition(trial[name]['definition'], pm)
    one.Placement = App.Placement(App.Matrix(*trial[name]['frame']))
    two = definition(rows[name]['definition'], m)
    two.Placement = App.Placement(App.Matrix(*rows[name]['frame']))
    ck(name + ' retains tested installed material', **same_material(one, two))

# Inspect all persistent inherited properties, including metadata not exposed by
# the physical manifest. Geometric serialization noise is bounded independently.
def properties(path):
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read('Document.xml'))
    types = {o.get('name'): o.get('type') for o in root.findall('Objects/Object')}
    props = {(o.get('name'), p.get('name')): p for o in root.findall('ObjectData/Object')
             for p in o.findall('Properties/Property')}
    return types, props
ot, op = properties(source)
nt, np = properties(native)
ck('All inherited object types survive', all(nt.get(n) == t for n, t in ot.items()))
def numeric_equal(a, b):
    if a.tag != b.tag or a.attrib.keys() != b.attrib.keys() or len(a) != len(b):
        return False
    for key, value in a.attrib.items():
        if value == b.get(key):
            continue
        try:
            if abs(float(value) - float(b.get(key))) > 1e-12:
                return False
        except ValueError:
            return False
    return all(numeric_equal(x, y) for x, y in zip(a, b))
changed_tips = {op[(name, 'Tip')].find('Link').get('value') for name in r['changed_definitions']}
changed = []
for key, before in op.items():
    after = np.get(key)
    if after is not None and ET.tostring(before) == ET.tostring(after):
        continue
    name, prop = key
    if prop == 'Group' and name in r['added_children'] and after is not None:
        old_children = [v.get('value') for v in before.findall('LinkList/Link')]
        new_children = [v.get('value') for v in after.findall('LinkList/Link')]
        passed = new_children == old_children + r['added_children'][name]
        reason = 'Declared new members appended'
    elif name == 'Root' and prop in ['Label', 'RegistrationStatus'] and after is not None:
        passed, reason = True, 'Current checkpoint description'
    elif name in changed_tips and prop == 'Shape' and after is not None:
        before_part, after_part = before.find('Part'), after.find('Part')
        passed = (before.attrib == after.attrib and before_part is not None and after_part is not None
                  and before_part.get('file') == after_part.get('file')
                  and all(v.tag in ['Part', 'ElementMap', 'ElementMap2'] for v in after))
        reason = 'Element naming metadata on an explicitly revised receiver tip; complete definition/installed material verified above'
    elif name in r['placement_changed_objects'] and prop in ['Placement', 'LinkPlacement'] and after is not None:
        passed, reason = True, 'Declared joint or lever frame; independently bound to reviewed prototype above'
    elif prop in ['Geometry', 'Placement', 'LinkPlacement'] and after is not None:
        passed, reason = numeric_equal(before, after), 'All numeric attributes within1e-12; identical XML structure'
    else:
        passed, reason = False, 'Unexpected inherited property change'
    changed.append(dict(object=name, property=prop, passed=passed, reason=reason))
new_inherited = [key for key in np if key[0] in ot and key not in op]
allowed = {(name, prop) for name, props in r['added_inherited_properties'].items() for prop in props}
ck('Persistent inherited properties preserved except four revision notes, declared tip shape metadata and root status',
   all(v['passed'] for v in changed) and set(new_inherited) == allowed,
   changed=changed, added_inherited_properties=sorted(new_inherited), compared=len(op))
receipts = ['independent_checks.json', 'context_checks.json', 'exchange_checks.json', 'reproduction_checks.json']
for file in receipts:
    q = read(prototype / file)
    ck('Transferred prototype ' + file, q['passed'] and q['native_sha256'] == pm['native_sha256'])
result = dict(passed=all(v['passed'] for v in checks), checks=checks,
              native_sha256=sha(native), source_native_sha256=sha(source),
              prototype_native_sha256=pm['native_sha256'], checker_sha256=sha(Path(__file__)),
              transferred_receipts={f: sha(prototype / f) for f in receipts},
              scope='All links/frames/owners and persistent inherited properties; strict nine-definition and16-installed-shape transfer from the tested prototype. Whole inherited definition preservation is checked separately.',
              historical_geometry_qualified=False, installation_qualified=False)
write(out / 'independent_checks.json', result)
interfaces = read(prototype / 'operating_interfaces.json')
interfaces['prototype_native_sha256'] = interfaces['native_sha256']
interfaces['native_sha256'] = sha(native)
interfaces['integration_checker_sha256'] = sha(Path(__file__))
interfaces['scope'] = 'Two revised high-speed bore diameters and four unchanged low-speed eyes rebound to the integrated native; all frames retained. Earlier track-rod interfaces are unchanged. Low-speed forks and full routes pending.'
for v in interfaces['interfaces']:
    v['definition_hashes'] = {key: m['definitions'][key]['brep_sha256'] for key in v['definition_names']}
interfaces['inherited_track_interfaces'] = str((source.parent/'operating_interfaces.json').relative_to(ROOT))
interfaces['inherited_track_interfaces_sha256'] = sha(source.parent/'operating_interfaces.json')
write(out / 'operating_interfaces.json', interfaces)
print(len(checks), 'integrated joint checks;', result['passed'], flush=True)
for v in checks:
    if not v['passed']:
        print(v, flush=True)
assert result['passed']
