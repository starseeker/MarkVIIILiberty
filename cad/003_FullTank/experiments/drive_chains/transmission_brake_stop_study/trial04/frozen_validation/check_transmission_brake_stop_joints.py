"""Check actual saved stop joints, original band material and assembly ownership.

Historical identity, strength and rivet stock-length convention remain separate
from these geometric checks. No builder geometry functions are imported.
"""
import argparse
import math
from pathlib import Path
import sys

import FreeCAD as App
import Part

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path.insert(0, str(H.parents[1]))
from lib.evidence import read, write, sha

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, required=True)
a = p.parse_args()
out = a.candidate.resolve()
r = read(out / 'report.json')
m = read(out / 'isolated/manifest.json')
source = ROOT / r['source_native']
old = read(source.parent / 'isolated/manifest.json')
assert sha(out / r['native_file']) == r['native_sha256'] == m['native_sha256']
assert sha(source) == r['source_native_sha256'] == old['native_sha256']
assert all(sha(ROOT / f) == digest for f, digest in r['input_hashes'].items())
rows, prior = [{row['name']: row for row in data['occurrences']} for data in (m, old)]
V = App.Vector
cache, checks = {}, []

def ck(name, passed, **detail):
    checks.append(dict(name=name, passed=bool(passed), **detail))
    write(out / 'joint_check_progress.json', checks)
    print(name, bool(passed), flush=True)

def definition(name, previous=False):
    rec = (old if previous else m)['definitions'][name]
    f = Path(rec['brep_path'])
    assert sha(f) == rec['brep_sha256']
    if rec['brep_sha256'] not in cache:
        s = Part.Shape(); s.read(str(f))
        assert s.Placement.isIdentity()
        cache[rec['brep_sha256']] = s
    return cache[rec['brep_sha256']].copy()

def pose(name, previous=False):
    return App.Placement(App.Matrix(*(prior if previous else rows)[name]['frame']))

def shape(name, previous=False):
    s = definition((prior if previous else rows)[name]['definition'], previous)
    s.Placement = pose(name, previous)
    return s

def empty(s):
    return (s.isNull() or s.isValid()) and not s.Faces and not s.Solids

def cylinders(s, radius):
    return [f for f in s.Faces if isinstance(f.Surface, Part.Cylinder)
            and abs(f.Surface.Radius-radius) < 1e-7]

def coverage(faces, supports):
    missing = []
    for f in faces:
        patches = [g for g in supports if abs(f.Surface.Radius-g.Surface.Radius) < 1e-7
                   and f.Surface.Axis.cross(g.Surface.Axis).Length < 1e-7
                   and (f.Surface.Center-g.Surface.Center).cross(g.Surface.Axis).Length < 1e-7]
        miss = f.cut(Part.makeCompound(patches)) if patches else f
        missing.append(dict(faces=len(miss.Faces), area_mm2=miss.Area,
                            passed=empty(miss) and abs(miss.Area) < 1e-5))
    return bool(faces) and all(v['passed'] for v in missing), missing

def planar_contact(one, two):
    area = 0.
    for f in one.Faces:
        if not isinstance(f.Surface, Part.Plane): continue
        for g in two.Faces:
            if not isinstance(g.Surface, Part.Plane): continue
            if f.normalAt(0, 0).cross(g.normalAt(0, 0)).Length < 1e-7 and f.distToShape(g)[0] < 1e-7:
                area += f.common(g).Area
    return area

def retained_by_motion(rivet, receiver, direction):
    moved = rivet.copy(); moved.translate(direction)
    common = moved.common(receiver)
    return common.isValid() and bool(common.Solids) and common.Volume > 1e-3, common.Volume

expected = r['expected_new_occurrences']
revised = r['expected_revised_occurrences']
ck('44 source-counted new occurrences', len(expected) == 44 and
   sum('StopLugRivet' in n for n in expected) == 12 and
   sum('StopBarRivet' in n for n in expected) == 8 and
   sum(n.endswith('StopLug') for n in expected) == 4 and
   sum(n.endswith('Screw') for n in expected) == 8 and
   sum(n.endswith('Nut') for n in expected) == 8 and
   sum(n.endswith('BrakeStopBar') or n.endswith('BrakeStopBracket') for n in expected) == 4)
ck('Exact inherited and new inventory', rows.keys() == prior.keys() | expected.keys()
   and len(rows) == 3001 and set(r['affected_occurrences']) == set(expected) | set(revised))
frame_checks = []
for name, row in rows.items():
    target = expected.get(name, revised.get(name, prior.get(name)))
    err = max(abs(x-y) for x, y in zip(row['frame'], target['frame']))
    frame_checks.append(dict(name=name, error=err, passed=err < 1e-7 and
                            row['definition'] == target['definition'] and row['owners'] == target['owners']))
ck('Every occurrence keeps its declared definition frame and owner', all(v['passed'] for v in frame_checks))
added_children = {'Root': {'TransmissionBrakeStops'}, 'Definitions': set(r['new_definitions'])}
for hand in ('Port', 'Starboard'):
    for label in ('LowSpeed', 'Track'):
        name = hand+label+'BrakeLower'
        added_children[name] = {name+'StopJoint'}
assembly_checks = []
for name, before in old['assemblies'].items():
    after = m['assemblies'][name]
    ok = all(max(abs(x-y) for x, y in zip(before[k], after[k])) < 1e-7 for k in ('local', 'world'))
    ok = ok and set(after['children']) == set(before['children']) | added_children.get(name, set())
    assembly_checks.append(dict(name=name, passed=ok))
ck('Inherited assembly frames and child ownership preserved', all(v['passed'] for v in assembly_checks)
   and m['assemblies'].keys() == old['assemblies'].keys() | set(r['new_assemblies']))

# Test the formed rivet stock under the builder's EXPLICIT provisional datum.
# No historical countersunk-length convention is inferred from a volume match.
stock_checks = []
for role, length in [('lug_rivet', 30.1625), ('bar_rivet', 31.75)]:
    s = definition('Def_BrakeStop_'+role)
    if role == 'lug_rivet':
        z0 = r['details']['lug_rivet']['head_depth_mm']
    else:
        z0 = 0.
    under_head = s.common(Part.makeBox(60, 60, 80, V(-30, -30, z0)))
    target = math.pi*(6.35/2)**2*length
    delta = abs(under_head.Volume-target)
    stock_checks.append(dict(role=role, datum_z_mm=z0, measured_mm3=under_head.Volume,
                             stock_mm3=target, error_mm3=delta, passed=delta < 1e-5))
ck('Rivet material conserves provisional under-head stock', all(v['passed'] for v in stock_checks),
   details=stock_checks, historical_countersunk_length_datum_resolved=False)

joint_checks = []
for hand in ('Port', 'Starboard'):
    for role, label in [('low', 'LowSpeed'), ('track', 'Track')]:
        prefix = hand+label+'Brake'
        lug = shape(prefix+'StopLug')
        band = shape(prefix+'LowerBand')
        old_band = shape(prefix+'LowerBand', True)
        radius = r['details']['brakes'][role]['outer_radius_mm']
        passed, missing = coverage(cylinders(lug, radius), cylinders(band, radius))
        ck(prefix+' complete curved foot support', passed, coverage=missing)
        shifted = lug.copy(); shifted.translate(pose(prefix+'StopLug').Rotation.multVec(V(0, 0, .05)))
        neg, _ = coverage(cylinders(shifted, radius), cylinders(band, radius))
        ck(prefix+' lifted-foot negative rejected', not neg)
        tools = []
        for i in range(1, 4):
            name = prefix+'StopLugRivet'+str(i)
            rivet = shape(name); frame = pose(name)
            axis = frame.Rotation.multVec(V(0, 0, 1))
            # Independent receiver tool: source quarter-inch nominal shaft plus
            # declared radial fit, and a90-degree countersink at the saved head.
            bore = 3.175+r['controls']['hole_clearance']
            head = r['controls']['lug_rivet_head_radius']
            depth = head-bore
            tool = Part.makeCylinder(bore, 45, V(0, 0, -5)).fuse(
                Part.makeCone(head+5, bore, depth+5, V(0, 0, -5)))
            tool.Placement = frame; tools.append(tool)
            probe = Part.makeCylinder(3.175, 10, V(0, 0, depth))
            probe.Placement = frame
            ck(name+' nominal through-shank passage', empty(probe.common(band)) and empty(probe.common(lug)))
            area = planar_contact(rivet, lug)
            outward, vo = retained_by_motion(rivet, band, axis*.1)
            inward, vi = retained_by_motion(rivet, lug, axis*-.1)
            ck(name+' formed head and upset retain the joint', area > 10 and outward and inward,
               upset_seat_area_mm2=area, outward_overlap_mm3=vo, inward_overlap_mm3=vi)
            lifted = rivet.copy(); lifted.translate(axis*.1)
            ck(name+' lifted-upset negative loses planar seat', planar_contact(lifted, lug) < 1e-5)
            joint_checks.append(dict(name=name, upset_contact_mm2=area))
        removed, added = old_band.cut(band), band.cut(old_band)
        remainder = removed.cut(Part.makeCompound(tools)) if removed.Faces else removed
        ck(prefix+' only three specified holes remove original band material', empty(remainder) and empty(added)
           and removed.Volume > 1, removed_mm3=removed.Volume, extra_mm3=added.Volume,
           unexplained_faces=len(remainder.Faces))
    bracket, bar = shape(hand+'BrakeStopBracket'), shape(hand+'BrakeStopBar')
    area = planar_contact(bracket, bar)
    ck(hand+' bracket foot bears on crossbar', area > 100, area_mm2=area)
    for i in range(1, 5):
        name = hand+'BrakeStopBarRivet'+str(i)
        rivet = shape(name); axis = pose(name).Rotation.multVec(V(0, 0, 1))
        areas = [planar_contact(rivet, s) for s in (bracket, bar)]
        front, vf = retained_by_motion(rivet, bracket, axis*.1)
        back, vb = retained_by_motion(rivet, bar, axis*-.1)
        ck(name+' both heads bear and prevent axial withdrawal', min(areas) > 10 and front and back,
           bearing_areas_mm2=areas, outward_overlap_mm3=vf, inward_overlap_mm3=vb)
        lifted = rivet.copy(); lifted.translate(axis*.1)
        ck(name+' lifted-head negative loses bracket seat', planar_contact(lifted, bracket) < 1e-5)

result = dict(passed=all(v['passed'] for v in checks), checks=checks, occurrence_frames=frame_checks,
              assembly_checks=assembly_checks, joints=joint_checks,
              native_sha256=r['native_sha256'], source_native_sha256=r['source_native_sha256'],
              checker_sha256=sha(Path(__file__)), historical_geometry_qualified=False, installation_qualified=False,
              scope='Saved joint support/retention, band material and hierarchy. Rivet length datum remains provisional; no full unchanged-definition, standard-context, strength or historical qualification.')
write(out / 'joint_checks.json', result)
assert result['passed'], 'Retain failed checks and diagnose the actual joint.'
