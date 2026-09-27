"""Saved-material interface checks; through-stems are diagnostic tools, not handles."""
import argparse
import math
from pathlib import Path
from control_rebuild_io_v2 import *
from lib.camera_review import validate_native_bindings

V = App.Vector
Y = V(0, 1, 0)
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, required=True)
a = p.parse_args()
s = Saved(a.candidate)
r = s.report
parent = Saved((ROOT / r['parent_native']).parent)
out = s.folder / 'checks03'
out.mkdir(exist_ok=False)
validate_native_bindings(dict(native_file=str(s.native), render_occurrences=list(s.rows), landmarks=[]), s.manifest)
assert all(sha(ROOT / file) == digest for file, digest in r['input_hashes'].items())
checks, measurements = [], {}


def ck(name, passed, **detail):
    checks.append(dict(name=name, passed=bool(passed), **detail))
    write(out / 'progress.json', checks)
    if not passed:
        print('FAIL', name, detail, flush=True)


def volume(shape):
    return sum(abs(solid.Volume) for solid in shape.Solids)


def same(first, second):
    return (volume(first.cut(second)) < 1e-5 and volume(second.cut(first)) < 1e-5
            and not first.cut(second, 1e-4).Faces and not second.cut(first, 1e-4).Faces)


def box(d, n, radial0, radial1, y0, y1, normal0, normal1):
    shape = Part.makeBox(radial1 - radial0, y1 - y0, normal1 - normal0)
    shape.Placement = App.Placement(d * radial0 + Y * y0 + n * normal0, App.Rotation(d, Y, n, 'XYZ'))
    return shape


def plane_faces(shape, point, normal):
    return [f for f in shape.Faces if isinstance(f.Surface, Part.Plane)
            and f.Surface.Axis.cross(normal).Length < 1e-7
            and abs((f.CenterOfMass - point).dot(normal)) < 1e-6]


def bearing(first, second, point, normal):
    return sum(f.common(g).Area for f in plane_faces(first, point, normal)
               for g in plane_faces(second, point, normal))


def shifted(shape, offset):
    q = shape.copy()
    q.translate(offset)
    return q


ck('four changed definitions and no new tank parts', len(r['changed_definitions']) == 4
   and not r['new_definitions'] and not r['new_occurrences'] and len(s.rows) == 140)
for key in s.manifest['definitions']:
    q = s.definition(key)
    ck(key + ' canonical complete solid', q.Placement.isIdentity() and q.isValid()
       and len(q.Solids) == 1 and q.Solids[0].isClosed() and q.getTolerance(1) <= 1e-4)
    if key not in r['changed_definitions']:
        ck(key + ' complete inherited material', same(q, parent.definition(key)))
for name, row in s.rows.items():
    old = parent.rows[name]
    ck(name + ' inherited definition and world frame', row['definition'] == old['definition']
       and max(abs(x - y) for x, y in zip(row['frame'], old['frame'])) < 1e-7)

c = r['details']['handle_gate_controls']
ck('bounded proposed wall variant', c['jaw_wall_mm'] in [12.7, 13.]
   and c['jaw_radial_halfspan_mm'] == 16. and c['jaw_tangential_halfspan_mm'] == 35.)
for side, sign in [('Port', 1), ('Starboard', -1)]:
    for kind, key in [('High', 'high_selector_controls'), ('Low', 'selector_controls')]:
        name = side + 'Driver' + kind + 'Selector'
        definition = s.rows[name]['definition']
        q, old = s.definition(definition), parent.definition(definition)
        prior = r['details'][key]
        d = V(*prior['selector_gate_direction'])
        n = V(-d.z, 0, d.x)
        # The old lower-jaw radius delimits the allowed edit region; the entire
        # rest of the solid is compared, including journal, oilway and bell eye.
        threshold = 140. if kind == 'High' else 215.
        lower = box(d, n, -1000, threshold - .001, -300, 300, -500, 500)
        ck(name + ' unchanged entire lower mechanism', same(q.common(lower), old.common(lower)))

        center = 175. if kind == 'High' else 250.
        y = sign * (21.35 if kind == 'High' else -21.35)
        probe = box(d, n, threshold - 10, threshold + 80, y - 6.35, y + 6.35, -6.35, 6.35)
        overlap = volume(probe.common(old))
        ck(name + ' old radial lips obstruct diagnostic stem', overlap > 4000,
           old_overlap_mm3=overlap, diagnostic_only=True)
        ck(name + ' proposed radial passage clears complete diagnostic stem', volume(probe.common(q)) < 1e-5)
        probe.exportBrep(str(out / (name + '_nonphysical_through_stem.brep')))
        inside = 35. - c['jaw_wall_mm']
        for direction in [-1, 1]:
            seat = n * direction * inside
            contact = shifted(probe, n * direction * (inside - 6.35))
            area = bearing(contact, q, seat, n)
            ck(name + ' tangential drive-face contact ' + str(direction), abs(area - 32 * 12.7) < 1e-5
               and volume(contact.common(q)) < 1e-5, contact_mm2=area)
            ck(name + ' relieved stem loses contact ' + str(direction),
               bearing(shifted(contact, n * (-direction * .01)), q, seat, n) < 1e-6)
            ck(name + ' displaced stem enters wall ' + str(direction),
               volume(shifted(contact, n * (direction * .25)).common(q)) > 100)
        for direction in [-1, 1]:
            a, b = sorted([direction * (inside + .01), direction * (35 - .01)])
            y0, y1 = sorted([sign * (6.36 if kind == 'High' else -6.36),
                              sign * (40.99 if kind == 'High' else -44.99)])
            wall = box(d, n, center - 15.99, center + 15.99, y0, y1, a, b)
            ck(name + ' complete drive wall ' + str(direction), volume(wall.cut(q)) < 1e-5)
        measurements[name] = dict(old_through_stem_overlap_mm3=overlap,
                                  proposed_through_stem_overlap_mm3=volume(probe.common(q)),
                                  drive_face_mm2=32 * 12.7, actual_handle_built=False)

result = dict(passed=all(v['passed'] for v in checks), checks=checks, measurements=measurements,
              native_sha256=sha(s.native), manifest_sha256=sha(s.folder / 'isolated/manifest.json'),
              checker_sha256=sha(Path(__file__)), historical_geometry_qualified=False,
              handle_engagement_qualified=False, geometry_integrated=False,
              scope='Conditional upper-jaw topology. Complete lower material and all frames preserved; '
                    'nonphysical through-stems test passage and tangential drive faces. '
                    'Full handles, pivot hardware and selected operating state remain unbuilt.')
write(out / 'independent_checks.json', result)
print(len(checks), 'conditional gate checks; passed', result['passed'], flush=True)
assert result['passed']
