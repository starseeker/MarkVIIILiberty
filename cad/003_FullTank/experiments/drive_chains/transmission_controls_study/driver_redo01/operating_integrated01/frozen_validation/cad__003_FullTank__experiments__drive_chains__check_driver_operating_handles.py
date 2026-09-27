"""Saved complete handles, journals, crown joints and selector contact checks."""
import argparse
import json
import math
from pathlib import Path
from control_rebuild_io_v2 import *
from lib.camera_review import validate_native_bindings

V = App.Vector
X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, required=True)
a = p.parse_args()
s = Saved(a.candidate)
r, details = s.report, s.report['details']
c = details['operating_controls']
parent = Saved((ROOT / r['parent_native']).parent)
out = s.folder / 'checks03'
out.mkdir(exist_ok=False)
validate_native_bindings(dict(native_file=str(s.native), render_occurrences=list(s.rows), landmarks=[]), s.manifest)
assert all(sha(ROOT / file) == digest for file, digest in r['input_hashes'].items())
checks = []


def ck(name, passed, **detail):
    checks.append(dict(name=name, passed=bool(passed), **detail))
    write(out / 'progress.json', checks)
    if not passed:
        print('FAIL', name, detail, flush=True)


def volume(shape):
    return sum(abs(q.Volume) for q in shape.Solids)


def same(first, second):
    return (volume(first.cut(second)) < 1e-5 and volume(second.cut(first)) < 1e-5
            and not first.cut(second, 1e-4).Faces and not second.cut(first, 1e-4).Faces)


def cylinders(q, point, axis, radius):
    return [f for f in q.Faces if isinstance(f.Surface, Part.Cylinder)
            and abs(f.Surface.Radius - radius) < 1e-7
            and f.Surface.Axis.cross(axis).Length < 1e-7
            and (f.Surface.Center - point).cross(axis).Length < 1e-6]


def span(face, axis):
    values = [vertex.Point.dot(axis) for vertex in face.Vertexes]
    return max(values) - min(values)


def planes(q, point, axis):
    return [f for f in q.Faces if isinstance(f.Surface, Part.Plane)
            and f.Surface.Axis.cross(axis).Length < 1e-7
            and abs((f.CenterOfMass - point).dot(axis)) < 1e-6]


def bearing(first, second, point, normal):
    return sum(f.common(g).Area for f in planes(first, point, normal)
               for g in planes(second, point, normal))


def shifted(q, delta):
    result = q.copy()
    result.translate(delta)
    return result


ck('ten additions, seven definitions and four bounded revisions', len(r['new_occurrences']) == 10
   and len(r['new_definitions']) == 7 and len(r['changed_definitions']) == 4 and len(s.rows) == 150)
for key in s.manifest['definitions']:
    q = s.definition(key)
    ck(key + ' canonical closed solid', q.Placement.isIdentity() and q.isValid()
       and len(q.Solids) == 1 and q.Solids[0].isClosed() and q.getTolerance(1) <= 1e-4)
    if key in parent.manifest['definitions'] and key not in r['changed_definitions']:
        ck(key + ' complete inherited material', same(q, parent.definition(key)))
for name, row in s.rows.items():
    ck(name + ' saved frame', max(abs(x-y) for x, y in zip(row['frame'], r['specs'][name]['frame'])) < 1e-7)
    if name in parent.rows:
        old = parent.rows[name]
        ck(name + ' inherited identity and frame', old['definition'] == row['definition']
           and max(abs(x-y) for x, y in zip(row['frame'], old['frame'])) < 1e-7)

radial = V(*details['high_selector_controls']['selector_gate_direction'])
normal = radial.cross(Y)
main = V(*details['foundation']['shafts']['Main']['center_world_mm'])
edit = Part.makeBox(300, 600, 70)
edit.Placement = App.Placement(radial * 32 - Y * 300 - normal * 35, App.Rotation(radial, Y, normal, 'XYZ'))
for key in r['changed_definitions']:
    q, old = s.definition(key), parent.definition(key)
    ck(key + ' all material outside upper-arm envelope unchanged', same(q.cut(edit), old.cut(edit)))

ck('specific M776 source cotter retained', json.loads(s.manifest['definitions']['Def_DriverOperatingCotter']['properties']['SourceRecords'])
   == ['SNL:23:029', 'SNL:141:008'])
cotter_local = s.definition('Def_DriverOperatingCotter')
wire = 1.17125
leg_faces = [f for f in cotter_local.Faces if isinstance(f.Surface, Part.Cylinder)
             and abs(f.Surface.Radius - wire) < 1e-7]
straight = sorted(span(f, X) for f in leg_faces if f.Surface.Axis.cross(X).Length < 1e-7 and span(f, X) > 1)
arcs = [f for f in cotter_local.Faces if isinstance(f.Surface, Part.Toroid)
        and abs(f.Surface.MajorRadius - 2.5) < 1e-7]
tails = [f for f in leg_faces if abs(abs(f.Surface.Axis.dot(X)) - math.cos(math.radians(20))) < 1e-7]
ck('cotter retains both measured straight legs, bends and tails', len(straight) == len(arcs) == len(tails) == 2)
if len(straight) == len(arcs) == len(tails) == 2:
    for i in range(2):
        arc = arcs[i].Surface.MajorRadius * (arcs[i].ParameterRange[1] - arcs[i].ParameterRange[0])
        tail = span(tails[i], tails[i].Surface.Axis)
        length = straight[i] + arc + tail
        ck('actual source one-inch leg centerline ' + str(i), abs(length - 25.4) < 1e-7
           and tail > 1, measured_mm=length, straight_mm=straight[i], arc_mm=arc, tail_mm=tail)
    centers = sorted(f.Surface.Center.z for f in leg_faces if f.Surface.Axis.cross(X).Length < 1e-7 and span(f, X) > 1)
    ck('actual source3/16-inch split-pin envelope and separated legs',
       abs(centers[1] - centers[0] + 2 * wire - 4.7625) < 1e-7 and centers[1] - centers[0] > 2 * wire)

shaft = s.world('DriverMainShaft')
joint_measurements = {}
for side, sign, fm, hm in [('Port', 1, 'M747', 'M738B'), ('Starboard', -1, 'M746', 'M738A')]:
    stem = side + 'DriverOperating'
    record = details['operating_handles'][side]
    fulcrum, hand, bolt, nut, cotter = [s.world(stem + role) for role in ['Fulcrum', 'Handle', 'Bolt', 'Nut', 'Cotter']]
    origin = V(*record['fulcrum_origin_world_mm'])
    pivot = V(*record['handle_pivot_world_mm'])
    head = V(*record['bolt_head_seat_world_mm'])
    stock = c['handle_stock_mm']
    ck(stem + ' source handed identity', s.manifest['definitions'][s.rows[stem + 'Fulcrum']['definition']]['properties']['SourcePartMark'] == fm
       and s.manifest['definitions'][s.rows[stem + 'Handle']['definition']]['properties']['SourcePartMark'] == hm)
    fs = cylinders(fulcrum, origin, Y, 19.1619)
    ck(stem + ' actual24mm journal and real shaft support', len(fs) == 1 and abs(span(fs[0], Y) - 24) < 1e-7
       and volume(Part.makeCylinder(19.0119, 24, origin - Y * 12, Y).cut(shaft)) < 1e-5
       and volume(fulcrum.common(shaft)) < 1e-5)
    for label, q, thickness in [('Fulcrum', fulcrum, 12.7), ('Handle', hand, stock)]:
        fs = cylinders(q, pivot, normal, 11.2125)
        ck(stem + label + ' complete real pivot bore', len(fs) == 1 and abs(span(fs[0], normal) - thickness) < 1e-7)
    local = s.definition(s.rows[stem + 'Handle']['definition'])
    ck(stem + ' complete37-inch overall radial extent', abs(local.BoundBox.XMax - local.BoundBox.XMin - 939.8) < 1e-7,
       measured_mm=local.BoundBox.XMax - local.BoundBox.XMin, datum='Canonical radial extent, an explicitly estimated interpretation of HB148.')
    ck(stem + ' shaft and journal wrap clears without cutting', volume(hand.common(shaft)) < 1e-5
       and volume(hand.common(fulcrum)) < 1e-5)
    fs = cylinders(bolt, head, normal, 11.1125)
    ck(stem + ' full7/8-inch pivot bolt stock', bool(fs) and abs(max(span(f, normal) for f in fs) - 42.5) < 1e-7)
    nut_seat = head + normal * record['joint']['nut_seat_mm']
    local_nut = s.definition('Def_DriverOperatingNut')
    ck(stem + ' sourcehalf-inch crown nut thickness and7/8 nominal bore',
       abs(local_nut.BoundBox.ZLength - 12.7) < 1e-7 and bool(cylinders(local_nut, V(), Z, 11.2125)))
    expected = math.sqrt(3) / 2 * 36.5125 ** 2 - math.pi * 11.2125 ** 2
    head_area, nut_area = bearing(bolt, fulcrum, head, normal), bearing(nut, hand, nut_seat, normal)
    ck(stem + ' full bolt-head bearing', abs(head_area - expected) < 1e-5, area_mm2=head_area)
    ck(stem + ' full crown-nut bearing', abs(nut_area - expected) < 1e-5, area_mm2=nut_area)
    ck(stem + ' lifted nut loses bearing', bearing(shifted(nut, normal * .1), hand, nut_seat, normal) < 1e-6)
    pin_axis = head + normal * record['joint']['cotter_axis_mm']
    ck(stem + ' actual cotter cross-drill', bool(cylinders(bolt, pin_axis, radial, 2.48125)))
    ck(stem + ' complete joint materials clear', all(volume(a.common(b)) < 1e-5 for a, b in
       [(bolt, hand), (bolt, fulcrum), (bolt, nut), (bolt, cotter), (nut, cotter), (hand, nut), (hand, cotter), (fulcrum, cotter)]))
    withdrawal = volume(shifted(cotter, -radial * 4).common(bolt))
    ck(stem + ' splayed source-length cotter resists withdrawal', withdrawal > .01, collision_mm3=withdrawal)
    turned = nut.copy()
    turned.rotate(nut_seat, normal, 30)
    rotation_overlap = volume(turned.common(cotter))
    ck(stem + ' cotter restrains crown-nut rotation', rotation_overlap > .01, collision_mm3=rotation_overlap)

    low, high = s.world(side + 'DriverLowSelector'), s.world(side + 'DriverHighSelector')
    high_gap = hand.distToShape(high)[0]
    ck(stem + ' clears unselected high selector', high_gap > .1 and volume(hand.common(high)) < 1e-5, minimum_mm=high_gap)
    ck(stem + ' selected low selector clear in static state', volume(hand.common(low)) < 1e-5)
    areas = []
    for direction in [-1, 1]:
        face = main + normal * direction * (stock / 2 + .45)
        contact = shifted(hand, normal * direction * .45)
        area = bearing(contact, low, face, normal)
        areas.append(area)
        ck(stem + ' actual selected drive-face engagement ' + str(direction), area > 250
           and volume(contact.common(low)) < 1e-5, contact_mm2=area)
        ck(stem + ' released drive face separates ' + str(direction),
           bearing(shifted(contact, normal * (-direction * .01)), low, face, normal) < 1e-6)
        ck(stem + ' excess drive-face approach intersects ' + str(direction),
           volume(shifted(contact, normal * (direction * .1)).common(low)) > 1)
    joint_measurements[side] = dict(head_bearing_mm2=head_area, nut_bearing_mm2=nut_area,
        high_selector_clearance_mm=high_gap, low_drive_face_areas_mm2=areas,
        withdrawal_collision_mm3=withdrawal, crown_rotation_collision_mm3=rotation_overlap)

result = dict(passed=all(v['passed'] for v in checks), checks=checks, measurements=joint_measurements,
              native_sha256=sha(s.native), manifest_sha256=sha(s.folder / 'isolated/manifest.json'),
              checker_sha256=sha(Path(__file__)), historical_geometry_qualified=False, motion_qualified=False,
              scope='Actual complete saved handles, full pivot stock and crown joints; measured source cotter legs, '
                    'bores, bearings, selector engagement, preserved lower mechanisms and displaced negatives. '
                    'Source shape/length datum, neutral control state and motion remain estimates.')
write(out / 'independent_checks.json', result)
print('Operating handles:', len(checks), 'checks; passed', result['passed'], flush=True)
assert result['passed']
