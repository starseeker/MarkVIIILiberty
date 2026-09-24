"""Saved-material and attachment checks for the estimated M4129 support stack."""
import argparse
from collections import Counter
import itertools
import math
from pathlib import Path
import shutil
import sys
import tempfile

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path.insert(0, str(H.parents[1]))
import FreeCAD as App
import Part
from lib.evidence import read, write, sha
from lib.camera_review import validate_native_bindings

V = App.Vector
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, required=True)
a = p.parse_args()
out = a.candidate.resolve()
assert not (out/'independent_checks.json').exists()
r, m = read(out/'report.json'), read(out/'isolated/manifest.json')
native = out/r['native_file']
assert sha(native) == r['native_sha256'] == m['native_sha256']
c = r['controls']
cl, bolt, ri = c['cleat'], c['bolt'], c['rivet']
rows = {v['name']: v for v in m['occurrences']}
old = {}
for key, path, digest in [('parent', r['parent_native'], r['parent_native_sha256'])]+[
        (key, v['native'], v['native_sha256']) for key, v in r['prototype_inputs'].items()]:
    path = ROOT/path
    old[key] = read(path.parent/'isolated/manifest.json')
    assert sha(path) == digest == old[key]['native_sha256']
checks, cache = [], {}


def ck(name, passed, **details):
    checks.append(dict(name=name, passed=bool(passed), **details))


def volume(s):
    return sum(abs(v.Volume) for v in s.Solids)


def world(name, manifest=m):
    row = next(v for v in manifest['occurrences'] if v['name'] == name)
    d = manifest['definitions'][row['definition']]
    digest = d['brep_sha256']
    if digest not in cache:
        assert sha(d['brep_path']) == digest
        s = Part.Shape()
        s.read(d['brep_path'])
        assert s.Placement.isIdentity()
        cache[digest] = s
    s = cache[digest].copy()
    s.Placement = App.Placement(App.Matrix(*row['frame']))
    return s


def same(one, two):
    return volume(one.cut(two)) < 1e-5 and volume(two.cut(one)) < 1e-5


def faces(s, z):
    return [f for f in s.Faces if isinstance(f.Surface, Part.Plane) and
            abs(abs(f.normalAt(0, 0).z)-1) < 1e-7 and abs(f.CenterOfMass.z-z) < 1e-6]


def contact(one, two, z):
    return Part.makeCompound([f.common(g) for f in faces(one, z) for g in faces(two, z)])


def annulus(axis, radius, bore):
    return Part.Face(Part.Wire([Part.makeCircle(radius, axis)])).cut(
        Part.Face(Part.Wire([Part.makeCircle(bore, axis)])))


def supported(patch, support):
    return not patch.cut(support).Faces


with tempfile.TemporaryDirectory(prefix='relocated_support_', dir=out) as temp:
    copied = Path(temp)/native.name
    shutil.copy2(native, copied)
    validate_native_bindings(dict(native_file=str(copied), render_occurrences=list(rows), landmarks=[]), m)
    doc = App.openDocument(str(copied))
    try:
        ck('22 saved occurrences have local identity-frame definitions', len(rows) == 22 and all(
            doc.getObject(v['object']).LinkedObject.Document == doc and
            doc.getObject(v['object']).LinkedObject.Placement.isIdentity() for v in rows.values()))
        for side in c['stations']:
            for suffix, number in [('HighSpringSupport', 3), ('LowSpringSupport', 3), ('RightChannelCleatMount', 4)]:
                g = doc.getObject(side+suffix)
                ck(side+suffix+' retains its physical children', len(g.Group) == number and
                   all(v.TypeId == 'App::Link' for v in g.Group))
        ck('Right cleat and short bolt preserve source identity',
           doc.getObject('Def_RearSupport_cleat').SourcePartMark == 'M4129' and
           'SNL:33:005' in doc.getObject('Def_RearSupport_bolt').SourceRecords)
    finally:
        App.closeDocument(doc.Name)
ck('Source-counted support family uses ten definitions', len(m['definitions']) == 10 and
   Counter(r['specs'][n]['role'] for n in rows) == dict(channel=1, floor=1, high_bracket=2,
   high_rivet=4, low_bracket=2, low_rivet=4, cleat=2, bolt=2, lock=2, nut=2))
shapes = {n: world(n) for n in rows}
for role in {s['role'] for s in r['specs'].values()}:
    s = shapes[next(n for n in rows if r['specs'][n]['role'] == role)]
    ck(role+' is one valid closed solid within the tolerance limit',
       s.isValid() and len(s.Solids) == 1 and s.Solids[0].isClosed() and s.getTolerance(1) <= 1e-4,
       tolerance_mm=s.getTolerance(1))
channel, floor = shapes['RearControlChannelStock'], shapes['hull_floor_7']
ck('Already-drilled channel material and frame are retained',
   same(channel, world('RearControlChannelStock', old['low'])) and
   rows['RearControlChannelStock']['frame'] == next(v['frame'] for v in old['low']['occurrences']
                                                  if v['name'] == 'RearControlChannelStock'))
holes = [Part.makeCylinder(19.35/2, 8, V(*xyz)+V(cl['bolt_x'], cl['bolt_y'], -7))
         for xyz in c['stations'].values()]
original_floor = world('hull_floor_7', old['parent'])
expected = original_floor.common(Part.makeCompound(holes))
removed = original_floor.cut(floor)
ck('Floor gains no material and loses exactly two complete source-bolt passages',
   volume(floor.cut(original_floor)) < 1e-5 and same(removed, expected) and
   abs(volume(removed)-2*math.pi*(19.35/2)**2*6) < 1e-5,
   removed_mm3=volume(removed))
ck('Floor frame is retained', rows['hull_floor_7']['frame'] == next(
    v['frame'] for v in old['parent']['occurrences'] if v['name'] == 'hull_floor_7'))
for name in rows:
    if r['specs'][name]['role'].startswith('high_'):
        ck(name+' preserves previously checked high support material and frame',
           same(shapes[name], world(name, old['high'])) and rows[name]['frame'] == next(
               v['frame'] for v in old['high']['occurrences'] if v['name'] == name))
for side, xyz in c['stations'].items():
    origin = V(*xyz)
    name = side+'RightChannelCleat'
    cleat, screw = shapes[name], shapes[name+'Bolt']
    lock, nut = shapes[name+'LockWasher'], shapes[name+'Nut']
    bracket = shapes[side+'LowSpringBracket']
    previous = world(side+'LowSpringBracket', old['low'])
    previous.translate(V(0, 0, cl['stock']))
    ck(side+' reuses the complete low bracket with only the declared lift', same(previous, bracket))
    for suffix, parent_name in [('LockWasher', 'RearChannelLeftCleat1LockWasher'),
                                ('Nut', 'RearChannelLeftCleat1Nut')]:
        one = world(name+suffix)
        two = world(parent_name, old['parent'])
        one.Placement = App.Placement()
        two.Placement = App.Placement()
        ck(side+suffix+' reuses existing hardware material', same(one, two))
    foot_contact = contact(cleat, floor, origin.z)
    ck(side+' complete foot underside bears on saved floor', all(
        supported(f, foot_contact) for f in faces(cleat, origin.z)), bearing_area_mm2=foot_contact.Area)
    axis = origin+V(cl['bolt_x'], cl['bolt_y'], 0)
    bore = Part.makeCylinder(19.05/2, cl['stock']+8, axis-V(0, 0, 7))
    ck(side+' source bolt shank passes through cleat and floor',
       volume(bore.common(cleat)) < 1e-5 and volume(bore.common(floor)) < 1e-5)
    underhead = axis+V(0, 0, cl['stock'])
    cyl = [f for f in screw.Faces if isinstance(f.Surface, Part.Cylinder) and
           abs(f.Surface.Radius-19.05/2) < 1e-7 and abs(abs(f.Surface.Axis.z)-1) < 1e-7]
    ck(side+' bolt retains source diameter and 1-5/8 inch under-head length',
       len(cyl) == 1 and abs(cyl[0].BoundBox.ZLength-41.275) < 1e-6 and
       abs(cyl[0].BoundBox.ZMax-underhead.z) < 1e-6)
    head_contact = contact(screw, cleat, underhead.z)
    # The hole is slightly larger than the shank; remove that intentional clearance.
    head_faces = Part.makeCompound(faces(screw, underhead.z))
    head_patch = head_faces.cut(Part.Face(Part.Wire([Part.makeCircle(19.35/2, underhead)])))
    ck(side+' bolt head has complete available bearing', supported(head_patch, head_contact),
       bearing_area_mm2=head_contact.Area)
    top = origin.z-c['floor_thickness']
    washer_contact = contact(lock, floor, top)
    ck(side+' complete lock washer top bears on floor',
       all(supported(f, washer_contact) for f in faces(lock, top)), bearing_area_mm2=washer_contact.Area)
    lower = top-c['lock_thickness']
    washer_contact = contact(lock, nut, lower)
    old_lock = world('RearChannelLeftCleat1LockWasher', old['parent'])
    old_nut = world('RearChannelLeftCleat1Nut', old['parent'])
    expected_contact = contact(old_lock, old_nut, old_nut.BoundBox.ZMax).Area
    ck(side+' nut retains the checked M4130 washer bearing area',
       expected_contact > 400 and abs(washer_contact.Area-expected_contact) < 1e-5,
       bearing_area_mm2=washer_contact.Area, inherited_bearing_area_mm2=expected_contact)
    lifted = nut.copy()
    lifted.translate(V(0, 0, -.1))
    ck(side+' displaced nut loses washer bearing', contact(lock, lifted, lower).Area < 1e-5)
    projection = nut.BoundBox.ZMin-screw.BoundBox.ZMin
    ck(side+' bolt spans full nut height with an exposed tip', projection > 2.54,
       tip_projection_mm=projection, scope='Simplified thread envelopes; no thread strength or pitch qualification.')
    roof = origin.z+c['channel_height']
    for i, y in enumerate(cl['rivet_y'], 1):
        rivet = shapes[side+'LowSpringRivet'+str(i)]
        axis = origin+V(cl['head_center_x'], y, c['channel_height'])
        ck(side+' rivet'+str(i)+' supports complete annuli at both cleat interfaces',
           supported(annulus(axis, 12.7, 6.5), contact(cleat, channel, roof)) and
           supported(annulus(axis+V(0, 0, cl['stock']), 12.7, 6.5),
                     contact(cleat, bracket, roof+cl['stock'])))
        top = roof+cl['stock']+c['low_bracket_stock']
        tail = roof-c['channel_stock']
        fa = contact(rivet, bracket, top).Area
        ta = contact(rivet, channel, tail).Area
        ck(side+' rivet'+str(i)+' retains full head and tail bearing',
           abs(fa-math.pi*((12.7/2*ri['factory_ratio'])**2-6.5**2)) < 1e-5 and
           abs(ta-math.pi*((12.7/2*ri['upset_ratio'])**2-6.5**2)) < 1e-5,
           factory_bearing_mm2=fa, tail_bearing_mm2=ta)
        witness = Part.makeCylinder(12.7/2, top-tail, V(axis.x, axis.y, tail))
        ck(side+' rivet'+str(i)+' clears all three stock layers',
           all(volume(witness.common(s)) < 1e-5 for s in [cleat, bracket, channel]))
        h = 12.7*ri['factory_height_ratio']
        stock_volume = math.pi*(12.7/2)**2*47.625+math.pi*h*(3*(12.7/2*ri['factory_ratio'])**2+h*h)/6
        ck(side+' rivet'+str(i)+' conserves source unformed stock',
           abs(rivet.Volume-stock_volume) < 1e-5, actual_mm3=rivet.Volume)
pairs = []
for first, second in itertools.combinations(rows, 2):
    one, two = shapes[first], shapes[second]
    if not one.BoundBox.intersect(two.BoundBox):
        continue
    common = one.common(two)
    occupied = volume(common)
    pairs.append(dict(first=first, second=second, common_mm3=occupied,
                      passed=(common.isNull() or common.isValid()) and occupied < 1e-5))
ck('All overlapping local bounding boxes have no material interference', all(v['passed'] for v in pairs))
result = dict(passed=all(v['passed'] for v in checks), checks=checks, material_pairs=pairs,
              native_sha256=sha(native), manifest_sha256=sha(out/'isolated/manifest.json'),
              checker_sha256=sha(Path(__file__)), prototype_inputs=r['prototype_inputs'],
              parent_native_sha256=r['parent_native_sha256'],
              scope='Static support stack and receiving material. Source shape, spring hooks, full rods and service installation remain unresolved.',
              historical_geometry_qualified=False, installation_qualified=False)
write(out/'independent_checks.json', result)
print(len(checks), 'saved support checks;', len(pairs), 'local material pairs;', result['passed'], flush=True)
if not result['passed']:
    print([v for v in checks if not v['passed']], flush=True)
    print([v for v in pairs if not v['passed']], flush=True)
assert result['passed']
