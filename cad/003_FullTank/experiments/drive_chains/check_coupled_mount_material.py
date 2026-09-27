"""Supplement the coupled audit with unique face pairs and bow-floor stock checks.

The first checker repeats a coplanar group once per member face when totaling
general mating area. This worker measures each actual face pair once instead.
"""
import argparse
from pathlib import Path
from control_rebuild_io_v2 import App, Part, H, ROOT, Saved, pose, sha, write

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, required=True)
s = Saved(p.parse_args().candidate)
parent = Saved((ROOT / s.report['parent_native']).parent)
accepted = Saved((ROOT / s.report['details']['retained_development_native']).parent)
out = s.folder / 'mount_material01'
out.mkdir(exist_ok=False)
checks = []


def volume(q):
    return sum(abs(v.Volume) for v in q.Solids)


def area(first, second):
    total = 0.
    for f in first.Faces:
        if not isinstance(f.Surface, Part.Plane):
            continue
        n, c = f.normalAt(0, 0), f.CenterOfMass
        for g in second.Faces:
            if (isinstance(g.Surface, Part.Plane)
                    and n.cross(g.normalAt(0, 0)).Length < 1e-7
                    and abs((g.CenterOfMass - c).dot(n)) < 1e-6):
                total += f.common(g).Area
    return total


def check_contact(name, first, second, minimum, direction):
    a = area(first, second)
    lifted = first.copy()
    lifted.translate(direction * .2)
    neg = area(lifted, second)
    overlap = volume(first.common(second))
    checks.append(dict(name=name, passed=a > minimum and neg < 1e-6 and overlap < 1e-5,
                       contact_mm2=a, minimum_mm2=minimum,
                       lifted_contact_mm2=neg, intersection_mm3=overlap))


d = s.report['details']
for j in d['driver_mount_joints'] + [j for j in parent.report['details']['joints'] if 'Stay' in j['stem']]:
    check_contact(j['stem'], *(s.world(n) for n in j['hosts']), 70., App.Vector(*j['axis_world']))
for side in ['Port', 'Starboard']:
    check_contact(side + ' plate/angle', s.world('Driver' + side + 'SupportPlate'),
                  s.world('DriverSeat' + side + 'SupportAngle'), 10000., App.Vector(0, 1, 0))
for floor, names in [('hull_floor_3', ['RearIntermediateSupportStrip', 'FrontIntermediateSupportStrip']),
                     ('hull_floor_6', ['ClutchSwingBracket'])]:
    for name in names:
        check_contact(name + ' floor bearing', s.world(name), s.world(floor), 10000., App.Vector(0, 0, 1))

# Start with the original complete bow floors, independently remove only the
# eight saved mounting bores, and compare both material directions. This catches
# stale holes as well as any loss outside the intended receiving stock.
bow_path = H / 'bow_reconstruction_study/trial02'
from control_rebuild_io_v2 import read
bow_report = read(bow_path / 'report.json')
native = bow_path / bow_report['native_file']
assert sha(native) == bow_report['native_sha256']
doc = App.openDocument(str(native))
for name in ['hull_floor_1', 'hull_floor_2']:
    obj = doc.getObject(name)
    stock = obj.LinkedObject.Shape.copy()
    stock.Placement = obj.LinkPlacement
    expected = stock.copy()
    holes = []
    for j in d['driver_mount_joints']:
        if name not in j['hosts']:
            continue
        point, axis = App.Vector(*j['point_world_mm']), App.Vector(*j['axis_world'])
        expected = expected.cut(Part.makeCylinder(6.5, 150., point-axis*75., axis))
        holes.append(j['stem'])
    actual = s.world(name)
    missing, extra = volume(expected.cut(actual)), volume(actual.cut(expected))
    checks.append(dict(name=name+' complete original stock minus four bores',
                       passed=len(holes)==4 and missing < 1e-5 and extra < 1e-5,
                       holes=holes, missing_mm3=missing, extra_mm3=extra))
App.closeDocument(doc.Name)

result = dict(passed=all(c['passed'] for c in checks), checks=checks,
              native_sha256=sha(s.native), checker_sha256=sha(Path(__file__)),
              bow_native_sha256=sha(native),
              scope='Unique planar face-pair contacts, displaced negative controls and complete floor1/2 stock preservation.')
write(out / 'report.json', result)
print('Supplementary mount checks:', len(checks), 'passed:', result['passed'], flush=True)
for c in checks:
    if not c['passed']:
        print(c, flush=True)
assert result['passed']
