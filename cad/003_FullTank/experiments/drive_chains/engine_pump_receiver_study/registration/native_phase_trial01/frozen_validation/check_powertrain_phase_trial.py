"""Check coupled planetary registration from saved frames, gears and neighbors."""
import argparse
import itertools
import math
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
source_manifest = source.parent / 'isolated/manifest.json'
assert sha(source_manifest) == r['source_manifest_sha256']
old = read(source_manifest)
new = read(out / 'isolated/manifest.json')
assert old['native_sha256'] == r['source_native_sha256']
assert new['native_sha256'] == r['native_sha256']
assert old['extractor_sha256'] == new['extractor_sha256'] == sha(HERE / 'pump_integration_worker.py')
rows = {v['name']: v for v in new['occurrences']}
before = {v['name']: v for v in old['occurrences']}
checks, frame_rows, meshes, interfaces, material = [], [], [], [], []

def ck(name, passed, **details):
    checks.append(dict(name=name, passed=bool(passed), **details))
    write(out / 'check_progress.json', dict(checks=checks, meshes=meshes, interfaces=interfaces))
    print(name, bool(passed), flush=True)

def mat(values):
    return np.asarray(values, dtype=float).reshape(4, 4)

def ry(degrees):
    theta = math.radians(degrees)
    c, s = math.cos(theta), math.sin(theta)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])

def turn(center, degrees):
    result = np.eye(4)
    result[:3, :3] = ry(degrees)
    result[:3, 3] = center - result[:3, :3] @ center
    return result

def error(one, two):
    points = np.array([[0, 0, 0, 1], [13, 0, 0, 1], [0, 17, 5, 1]]).T
    return float(np.linalg.norm(((one - two) @ points)[:3], axis=0).max())

center = mat(old['assemblies']['TransmissionCore']['world'])[:3, 3]
# Infer the required rotation from the actual shaft-to-carrier mismatch in the
# saved predecessor, independently of the builder's angle table.
carrier_pose = mat(before['PortTransmissionCore_planet_disk']['frame'])
shaft_pose = mat(before['PortTransmissionOutput_shaft']['frame'])
rotation = shaft_pose[:3, :3] @ carrier_pose[:3, :3].T
required = math.degrees(math.atan2(rotation[0, 2], rotation[0, 0]))
assert np.linalg.norm(rotation - ry(required)) < 1e-10
ns, np_, nr = [read(HERE / 'transmission_planet_controls.json')['controls']['teeth_' + k]['value']
               for k in ['sun', 'planet', 'ring']]
ss, sp, sr = [read(HERE / 'transmission_small_controls.json')['controls']['teeth_' + k]['value']
               for k in ['sun', 'planet', 'ring']]
case = required * (ns + nr) / nr
high = case * (ss + sr) / ss
spin_large = required * (ns + np_) / np_
spin_small = case * (ss + sp) / sp - high * ss / sp
expected_changes = {}
for hand in ['Port', 'Starboard']:
    for name, row in before.items():
        if hand + 'PlanetSupports' in row['owners']:
            expected_changes[name] = required, required
        if hand + 'SmallPlanetSupports' in row['owners']:
            expected_changes[name] = case, case
    expected_changes[hand + 'TransmissionCore_planet_disk'] = required, required
    for suffix in ['brake_case', 'plain_case']:
        expected_changes[hand + 'TransmissionCore_' + suffix] = case, case
    for suffix in ['ring', 'gasket0', 'gasket1']:
        expected_changes[hand + 'PlanetTrain_' + suffix] = case, case
    for name in [hand + 'SmallPlanetTrain_sun', hand + 'TransmissionCore_high_drum', hand + 'SunRetention_ring']:
        expected_changes[name] = high, high
    for n in range(3):
        expected_changes[hand + 'PlanetTrain_planet' + str(n)] = required, spin_large
        expected_changes[hand + 'SmallPlanetTrain_planet' + str(n)] = case, spin_small

ck('Exact 2393 occurrence coverage and 142 coupled phase changes',
   rows.keys() == before.keys() and len(rows) == 2393 and
   set(expected_changes) == set(r['changed_occurrences']) and len(expected_changes) == 142)
for name, row in rows.items():
    previous = before[name]
    expected = mat(previous['frame'])
    if name in expected_changes:
        orbit, spin = expected_changes[name]
        expected = turn(center, orbit) @ expected
        expected = turn(expected[:3, 3], spin - orbit) @ expected
    diff = error(mat(row['frame']), expected)
    frame_rows.append(dict(name=name, error_mm=diff, passed=diff < 1e-7 and
                           row['owners'] == previous['owners'] and row['definition'] == previous['definition']))
ck('Saved phase frames, handedness and retained occurrence frames',
   all(v['passed'] for v in frame_rows), maximum_error_mm=max(v['error_mm'] for v in frame_rows),
   failures=[v for v in frame_rows if not v['passed']])

def phase_delta(name):
    rotation = mat(rows[name]['frame'])[:3, :3] @ mat(before[name]['frame'])[:3, :3].T
    angle = math.degrees(math.atan2(rotation[0, 2], rotation[0, 0]))
    assert np.linalg.norm(rotation - ry(angle)) < 1e-9
    return angle

laws = []
for hand in ['Port', 'Starboard']:
    sun = phase_delta(hand + 'PlanetTrain_sun')
    ring = phase_delta(hand + 'PlanetTrain_ring')
    carrier = phase_delta(hand + 'TransmissionCore_planet_disk')
    smallsun = phase_delta(hand + 'SmallPlanetTrain_sun')
    smallring = phase_delta(hand + 'SmallPlanetTrain_ring')
    smallcarrier = phase_delta(hand + 'TransmissionCore_plain_case')
    laws.append(dict(hand=hand, large_residual_tooth_degrees=ns * sun + nr * ring - (ns + nr) * carrier,
                     small_residual_tooth_degrees=ss * smallsun + sr * smallring - (ss + sr) * smallcarrier,
                     coupled_case_residual_degrees=smallcarrier - ring))
ck('Both saved epicyclic phase equations and shared case coupling',
   all(abs(v[k]) < 1e-7 for v in laws for k in ['large_residual_tooth_degrees',
       'small_residual_tooth_degrees', 'coupled_case_residual_degrees']), measured=laws)
preservation = []
for name, definition in new['definitions'].items():
    original = old['definitions'][name]
    preservation.append(dict(name=name, exact_brep=definition['brep_sha256'] == original['brep_sha256'],
                             metadata_equal=definition['properties'] == original['properties']))
ck('All definition identities and source metadata retained',
   new['definitions'].keys() == old['definitions'].keys() and all(v['metadata_equal'] for v in preservation))
assert all(v['passed'] for v in checks), 'Resolve frame/source errors before expensive solid comparisons.'

import FreeCAD as App
import Part
shapes = {}
verified_files = set()

def read_definition(manifest, key):
    definition = manifest['definitions'][key]
    f = Path(definition['brep_path'])
    if str(f) not in verified_files:
        assert sha(f) == definition['brep_sha256']
        verified_files.add(str(f))
    s = Part.Shape()
    s.read(str(f))
    assert s.Placement.isIdentity()
    return s

def shape(name, original=False):
    key = name, original
    if key not in shapes:
        row = (before if original else rows)[name]
        s = read_definition(old if original else new, row['definition'])
        s.Placement = App.Placement(App.Matrix(*row['frame']))
        shapes[key] = s
    return shapes[key]

def common(one, two):
    return one.common(two).Volume if one.BoundBox.intersect(two.BoundBox) else 0.0

for hand in ['Port', 'Starboard']:
    for prefix, pitch_radius in [('PlanetTrain_', (ns + np_) * 25.4 / (2 * 4)),
                                 ('SmallPlanetTrain_', (ss + sp) * 25.4 / (2 * 5))]:
        for n in range(3):
            name = hand + prefix + 'planet' + str(n)
            actual_center = mat(rows[name]['frame'])[:3, 3]
            radius = float(np.linalg.norm((actual_center - center)[[0, 2]]))
            gaps = {key: shape(name).distToShape(shape(hand + prefix + key))[0] for key in ['sun', 'ring']}
            overlaps = {key: common(shape(name), shape(hand + prefix + key)) for key in ['sun', 'ring']}
            meshes.append(dict(name=name, center_radius_mm=radius, gaps_mm=gaps, common_mm3=overlaps,
                               passed=abs(radius - pitch_radius) < 1e-6 and all(.001 < v < .5 for v in gaps.values()) and
                               all(v < 1e-5 for v in overlaps.values())))
            write(out / 'mesh_progress.json', meshes)
    for first, second, expected in [
        (hand + 'TransmissionOutput_shaft', hand + 'TransmissionCore_planet_disk', .1),
        (hand + 'SmallPlanetTrain_sun', hand + 'TransmissionCore_high_drum', .1),
    ]:
        one, two = shape(first), shape(second)
        gap, volume = one.distToShape(two)[0], common(one, two)
        interfaces.append(dict(first=first, second=second, gap_mm=gap, common_mm3=volume,
                               passed=abs(gap - expected) < 1e-5 and volume < 1e-5))
    print('Saved gear meshes measured', hand, flush=True)
ck('All twelve actual planetary meshes retain backlash and pitch centers', all(v['passed'] for v in meshes), count=len(meshes))
ck('Output/carrier and high-drum/sun splines fit', all(v['passed'] for v in interfaces), interfaces=interfaces)
wrong = shape('PortPlanetTrain_planet0').copy()
wrong.rotate(wrong.Placement.Base, App.Vector(0, 1, 0), 180 / np_)
bad_mesh = common(wrong, shape('PortPlanetTrain_sun'))
ck('Negative control rejects a half-tooth planet misclock', bad_mesh > 1e-5, common_mm3=bad_mesh)
old_disk = shape('PortTransmissionCore_planet_disk', original=True)
bad_spline = common(old_disk, shape('PortTransmissionOutput_shaft'))
ck('Negative control retains predecessor carrier/shaft interference', bad_spline > 1e-5, common_mm3=bad_spline)

# Construct conservative world bounds from local saved BRep bounds one definition
# at a time, avoiding resident copies of unrelated dense engine components.
local_bounds = {}
for name in new['definitions']:
    s = read_definition(new, name)
    b = s.BoundBox
    local_bounds[name] = list(itertools.product([b.XMin, b.XMax], [b.YMin, b.YMax], [b.ZMin, b.ZMax]))
del s
bounds = {}
for name, row in rows.items():
    f = mat(row['frame'])
    corners = np.asarray(local_bounds[row['definition']]) @ f[:3, :3].T + f[:3, 3]
    bounds[name] = np.r_[corners.min(axis=0), corners.max(axis=0)]
names = list(rows)
boxes = np.asarray([bounds[name] for name in names])
pairs = set()
for first in expected_changes:
    bb = bounds[first]
    nearby = np.flatnonzero(np.all(boxes[:, :3] <= bb[3:] + 1e-7, axis=1) &
                            np.all(boxes[:, 3:] >= bb[:3] - 1e-7, axis=1))
    for index in nearby:
        second = names[index]
        if first != second:
            pairs.add(tuple(sorted([first, second])))
write(out / 'material_pair_plan.json', dict(native_sha256=r['native_sha256'], pairs=sorted(pairs)))
print('Checking affected solids against complete 2393-occurrence context:', len(pairs), 'pairs', flush=True)
for first, second in sorted(pairs):
    volume = common(shape(first), shape(second))
    material.append(dict(first=first, second=second, common_mm3=volume, passed=volume < 1e-5))
    write(out / 'material_progress.json', material)
    if len(material) % 50 == 0:
        print('material progress', len(material), 'failures', sum(not v['passed'] for v in material), flush=True)
ck('All changed planetary components clear their complete assembly neighbors',
   all(v['passed'] for v in material), pairs=len(material), failures=[v for v in material if not v['passed']])
write(out / 'independent_checks.json', dict(
    local_phase_checks_passed=all(v['passed'] for v in checks), native_sha256=sha(native),
    source_native_sha256=sha(source), checker_sha256=sha(Path(__file__)),
    candidate_manifest_sha256=sha(out / 'isolated/manifest.json'), checks=checks,
    occurrence_frames=frame_rows, meshes=meshes, interfaces=interfaces, material_pairs=material,
    definition_preservation=preservation,
    pending_definition_material=[v['name'] for v in preservation if not v['exact_brep']],
    all_definitions_qualified=all(v['exact_brep'] for v in preservation) and
                              read(source.parent / 'independent_checks.json')['all_definitions_qualified'],
    installation_qualified=False, historical_station_qualified=False,
    continuous_motion_qualified=False, standard_assembly_modified=False,
))
assert all(v['passed'] for v in checks), 'Retain failures; do not promote this phase trial.'
