"""Verify rebuilt engine suspension against saved hardware, floor and engine."""
import argparse
from collections import Counter
import itertools
from pathlib import Path
import sys
import numpy as np

HERE = Path(__file__).resolve().parent
STAGE = HERE.parents[1]
ROOT = STAGE.parents[1]
sys.path[:0] = [str(HERE), str(STAGE)]
from lib.evidence import read, write, sha

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, required=True)
a = p.parse_args()
out = a.candidate.resolve()
r = read(out / 'report.json')
native = out / r['native_file']
source = ROOT / r['source_native']
assert sha(native) == r['native_sha256'] and sha(source) == r['source_native_sha256']
for rel, digest in r['input_hashes'].items():
    assert sha(ROOT / rel) == digest, rel
old = read(source.parent / 'isolated/manifest.json')
m = read(out / 'isolated/manifest.json')
assert old['native_sha256'] == r['source_native_sha256'] and m['native_sha256'] == r['native_sha256']
assert old['extractor_sha256'] == m['extractor_sha256'] == sha(HERE / 'pump_integration_worker.py')
rows = {v['name']: v for v in m['occurrences']}
before = {v['name']: v for v in old['occurrences']}
checks, material, frame_rows = [], [], []
c, cc, datums = r['controls'], r['crossmember_controls'], r['datums']

def ck(name, passed, **details):
    checks.append(dict(name=name, passed=bool(passed), **details))
    write(out / 'check_progress.json', checks)
    print(name, bool(passed), flush=True)

def near(name, actual, expected, tol=1e-6):
    ck(name, abs(actual - expected) < tol, actual=actual, expected=expected, tolerance=tol)

import FreeCAD as App
import Part
V = App.Vector
cache, verified = {}, set()

def definition(key, original=False):
    d = (old if original else m)['definitions'][key]
    path = Path(d['brep_path'])
    if str(path) not in verified:
        assert sha(path) == d['brep_sha256']
        verified.add(str(path))
    s = Part.Shape()
    s.read(str(path))
    assert s.Placement.isIdentity()
    return s

def shape(name, original=False):
    key = name, original
    if key not in cache:
        row = (before if original else rows)[name]
        s = definition(row['definition'], original)
        s.Placement = App.Placement(App.Matrix(*row['frame']))
        cache[key] = s
    return cache[key]

def inst(name):
    return shape('EngineSuspension_' + name)

def gap(name, left, right):
    near(name, left.distToShape(right)[0], 0)

def frame_error(one, two):
    points = np.array([[0, 0, 0, 1], [13, 0, 0, 1], [0, 17, 5, 1]]).T
    return float(np.linalg.norm(((one - two) @ points)[:3], axis=0).max())

ck('All 2393 physical occurrence identities retained', rows.keys() == before.keys() and len(rows) == 2393)
expected = {}
for v in r['support_occurrences']:
    pose = App.Placement(V(*v['xyz']), App.Rotation(*v['rotation']))
    expected[v['name']] = np.asarray(pose.toMatrix().A).reshape(4, 4)
ck('Exactly 61 support occurrences and three rebuilt casting definitions',
   len(expected) == 61 and set(r['replacement_definitions']) == {
       'EngineSuspension_LeftBracket', 'EngineSuspension_RightBracket', 'EngineSuspension_FrontBracket'})
affected = set(r['replacement_definitions'])
for name, row in rows.items():
    previous = before[name]
    target = expected.get(name, np.asarray(previous['frame']).reshape(4, 4))
    current = np.asarray(row['frame']).reshape(4, 4)
    err = frame_error(current, target)
    frame_rows.append(dict(name=name, error_mm=err, passed=err < 1e-7 and
                           row['definition'] == previous['definition'] and row['owners'] == previous['owners']))
    if frame_error(current, np.asarray(previous['frame']).reshape(4, 4)) > 1e-7:
        affected.add(name)
ck('Saved support placements and all retained planetary/hull frames', all(v['passed'] for v in frame_rows),
   affected_occurrences=len(affected), maximum_error_mm=max(v['error_mm'] for v in frame_rows))
for group, count in [('FrontSuspension', 15), ('LeftRearSuspension', 22), ('RightRearSuspension', 22), ('LongitudinalSupports', 2)]:
    ck(group + ' source allocation', sum(group in row['owners'] for row in rows.values()) == count)
ck('All 86 engine mount pieces including 14 floor rivets retained',
   sum('EngineMounts' in row['owners'] for row in rows.values()) == 86 and
   sum('FloorAttachments' in row['owners'] for row in rows.values()) == 14)
for key, diam, length in [('half_bolt', 12.7, 44.45), ('rear_bolt', 15.875, 63.5), ('pivot_bolt', 19.05, 63.5), ('cap', 12.7, 38.1)]:
    s = definition('Def_EngineSuspension_' + key)
    witness = Part.makeCylinder(diam / 2, length)
    near(key + ' complete printed shaft material', witness.cut(s).Volume, 0, 1e-5)
    ck(key + ' printed cylindrical length and diameter', any(type(f.Surface).__name__ == 'Cylinder' and
       abs(f.Surface.Radius - diam / 2) < 1e-6 and abs(f.BoundBox.ZLength - length) < 1e-6 for f in s.Faces))
    near(key + ' original head height', s.BoundBox.ZMin, -c['head_height_ratio'] * diam)

axis = np.asarray(m['assemblies']['TankLibertyEngine']['world']).reshape(4, 4)[2, 3]
near('Source-derived engine height', axis, r['crankshaft_axis_z'])
for side, sign in [('Left', 1), ('Right', -1)]:
    rail = inst(side + 'Rail')
    near(side + ' rail aft station retained', rail.BoundBox.XMin, 2940)
    near(side + ' rail front station retained', rail.BoundBox.XMax, 4120)
    near(side + ' rail height stock retained', rail.BoundBox.ZLength, 76.2)
    near(side + ' rail width retained', rail.BoundBox.YLength, 50.8)
    near(side + ' conditional engine row center', (rail.BoundBox.YMin + rail.BoundBox.YMax) / 2, sign * 215.9)
    near(side + ' rail engine mounting plane', rail.BoundBox.ZMax, axis)
    for bracket in [side + 'Bracket', 'FrontBracket']:
        gap(side + ' rail on ' + bracket, rail, inst(bracket))
        near(side + ' rail/bracket zero overlap ' + bracket, rail.common(inst(bracket)).Volume, 0, 1e-5)
    gap(side + ' packing against bracket', inst(side + 'Packing'), inst(side + 'Bracket'))
    gap(side + ' packing against unchanged crossmember', inst(side + 'Packing'), shape('EngineFrame_RearChannel'))
    gap(side + ' engine flange on rail', rail, shape('EngineCase_upper'))
    common = rail.common(shape('EngineCase_upper'))
    ck(side + ' actual flange bearing contact', common.Area > 1000 and abs(common.Volume) < 1e-5,
       contact_area_mm2=common.Area, common_mm3=common.Volume)
gap('Front yoke on unchanged cleat', inst('FrontBracket'), shape('EngineFrame_FrontCleat'))
gap('Front packing on yoke', inst('FrontPacking'), inst('FrontBracket'))
gap('Front packing on cleat', inst('FrontPacking'), shape('EngineFrame_FrontCleat'))

receiver_keys = dict(left_rail='LeftRail', right_rail='RightRail', left_bracket='LeftBracket',
                     right_bracket='RightBracket', front_bracket='FrontBracket')

def receiver(key, joint):
    if key.startswith('EngineFrame_'):
        return shape(key)
    if key == 'rear_packing':
        return inst(('Left' if joint['name'].startswith('Left') else 'Right') + 'Packing')
    return inst(receiver_keys[key])

for j in datums['joints']:
    name, key = j['name'], j['hardware']
    base, axis_v = V(*j['base']), V(*j['axis'])
    if key == 'cap':
        side = 'Left' if name.startswith('Left') else 'Right'
        witness = Part.makeCylinder(12.7 / 2, 38.1, base, axis_v)
        for recv in j['receiver_keys']:
            near(name + ' nominal envelope in ' + recv, receiver(recv, j).common(witness).Volume, 0, 1e-7)
        near(name + ' complete shaft material', witness.cut(inst(name)).Volume, 0, 1e-5)
        gap(name + ' head on lock', inst(name), inst(side + 'CapLock'))
        gap(name + ' lock on rail', inst(side + 'CapLock'), inst(side + 'Rail'))
        point = V(base.x, base.y, datums['cap_boss_bottom_world_z'] + 1)
        ck(name + ' blind boss floor retained', inst('FrontBracket').isInside(point, 1e-7, False) and j['blind_floor'] > 3)
        continue
    diameter = {'half': 12.7, 'rear': 15.875, 'pivot': 19.05}[key]
    length = {'half': 44.45, 'rear': 63.5, 'pivot': 63.5}[key]
    witness = Part.makeCylinder(diameter / 2, j['grip'], base, axis_v)
    for recv in j['receiver_keys']:
        near(name + ' through bore in ' + recv, receiver(recv, j).common(witness).Volume, 0, 1e-7)
    near(name + ' clamped shaft material', witness.cut(inst(name + 'Bolt')).Volume, 0, 1e-5)
    gap(name + ' head seating', inst(name + 'Bolt'), receiver(j['receiver_keys'][0], j))
    gap(name + ' nut on lock', inst(name + 'Nut'), inst(name + 'Lock'))
    protrusion = length - j['grip'] - diameter * (c['lock_stock_ratio'] + c['nut_height_ratio'])
    ck(name + ' positive nut engagement', protrusion > 0, protrusion_mm=protrusion)
    if key == 'rear':
        bevel = name.replace('Base', 'Bevel')
        gap(name + ' bevel on unchanged channel', inst(bevel), shape('EngineFrame_RearChannel'))
        gap(name + ' lock on bevel', inst(name + 'Lock'), inst(bevel))
    else:
        gap(name + ' lock on receiver', inst(name + 'Lock'), receiver(j['receiver_keys'][-1], j))

for name in r['replacement_definitions']:
    s = shape(name)
    ck(name + ' valid single casting', s.isValid() and len(s.Solids) == 1 and s.getTolerance(1) <= 1e-4,
       tolerance_mm=s.getTolerance(1))
    if name.endswith('FrontBracket'):
        region = Part.makeBox(200, 70, 500, V(cc['front_x'] - 50, -35, cc['floor_top']))
    else:
        y = 215.9 if 'Left' in name else -215.9
        region = Part.makeBox(200, 200, cc['channel_height'] + c['packing_stock'] + c['rear_base_stock'],
                              V(cc['rear_x'] - 100, y - 100, cc['floor_top']))
    one, two = shape(name, True).common(region), s.common(region)
    near(name + ' preserved floor receiver material', one.cut(two).Volume, 0, 1e-5)
    near(name + ' no extra floor receiver material', two.cut(one).Volume, 0, 1e-5)
old_gap = inst('LeftRail').distToShape(shape('EngineSuspension_LeftBracket', True))[0]
ck('Negative control rejects the previous short bracket', old_gap > 50, gap_mm=old_gap)

preserved_definitions = []
changed_defs = set(r['replacement_definitions'].values())
for name, d in m['definitions'].items():
    if name not in changed_defs:
        preserved_definitions.append(dict(name=name, exact_brep=d['brep_sha256'] == old['definitions'][name]['brep_sha256'],
                                         metadata_equal=d['properties'] == old['definitions'][name]['properties']))
ck('All other definition identities and source metadata retained',
   m['definitions'].keys() == old['definitions'].keys() and all(v['metadata_equal'] for v in preserved_definitions))

# Broad phase covers every physical occurrence, including inherited components.
local = {}
for name in m['definitions']:
    s = definition(name)
    b = s.BoundBox
    local[name] = np.asarray(list(itertools.product([b.XMin, b.XMax], [b.YMin, b.YMax], [b.ZMin, b.ZMax])))
del s
names, bounds = list(rows), []
for name in names:
    row = rows[name]
    f = np.asarray(row['frame']).reshape(4, 4)
    points = local[row['definition']] @ f[:3, :3].T + f[:3, 3]
    bounds.append(np.r_[points.min(axis=0), points.max(axis=0)])
boxes = np.asarray(bounds)
pairs = set()
for name in affected:
    b = boxes[names.index(name)]
    near_indices = np.flatnonzero(np.all(boxes[:, :3] <= b[3:] + 1e-7, axis=1) &
                                  np.all(boxes[:, 3:] >= b[:3] - 1e-7, axis=1))
    for index in near_indices:
        if name != names[index]:
            pairs.add(tuple(sorted([name, names[index]])))
print('Affected support/context pairs', len(pairs), flush=True)
for first, second in sorted(pairs):
    one, two = shape(first), shape(second)
    volume = one.common(two).Volume if one.BoundBox.intersect(two.BoundBox) else 0.0
    material.append(dict(first=first, second=second, common_mm3=volume, passed=abs(volume) < 1e-5))
    write(out / 'material_progress.json', material)
ck('Changed supports clear all saved assembly neighbors', all(v['passed'] for v in material),
   pairs=len(material), failures=[v for v in material if not v['passed']])
write(out / 'independent_checks.json', dict(
    local_support_checks_passed=all(v['passed'] for v in checks), native_sha256=sha(native),
    checker_sha256=sha(Path(__file__)), source_native_sha256=sha(source),
    checks=checks, occurrence_frames=frame_rows, affected_occurrences=sorted(affected),
    material_pairs=material, preserved_definitions=preserved_definitions,
    pending_definition_material=[v['name'] for v in preserved_definitions if not v['exact_brep']],
    installation_qualified=False, historical_station_qualified=False,
    engine_mount_holes_complete=False, standard_assembly_modified=False))
assert all(v['passed'] for v in checks), 'Retain failed support interfaces before revising.'
