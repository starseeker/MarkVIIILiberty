"""Inspect saved placement diagnostics against source frames and actual solids.

This checker distinguishes chain/placement integrity from unresolved installation
interfaces. It never promotes a trial because its selected measurements pass.
Run the existing pump_integration_worker extractor first, then this script via
the headless launcher. Both manifests remain bound to their native files.
"""
import argparse
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
p.add_argument('--chain-material', action='store_true')
a = p.parse_args()
out = a.candidate.resolve()
r = read(out / 'report.json')
native = out / r['native_file']
assert sha(native) == r['native_sha256']
assert sha(ROOT / r['source_native']) == r['source_native_sha256']
for rel, digest in r['input_hashes'].items():
    assert sha(ROOT / rel) == digest, rel
old = read(HERE / 'installed_pitch_route_report.json')
stations = read(HERE / 'engine_pump_receiver_study/registration/station_candidates.json')
station = stations['candidates'][r['station']]
source_path = HERE / 'engine_pump_receiver_study/assembly_trial02/isolated/candidate/manifest.json'
candidate_path = out / 'isolated/manifest.json'
manifests = dict(source=read(source_path), candidate=read(candidate_path))
assert manifests['source']['native_sha256'] == r['source_native_sha256']
assert manifests['candidate']['native_sha256'] == r['native_sha256']
for m in manifests.values():
    assert m['extractor_sha256'] == sha(HERE / 'pump_integration_worker.py')
items = {k: {v['name']: v for v in m['occurrences']} for k, m in manifests.items()}
checks = []
frames = []
interfaces = []

def ck(name, passed, **detail):
    checks.append(dict(name=name, passed=bool(passed), **detail))
    write(out / 'check_progress.json', dict(checks=checks, interfaces=interfaces))
    print(name, bool(passed), flush=True)

def matrix(row):
    return np.array(row, dtype=float).reshape(4, 4)

def translate(v):
    result = np.eye(4)
    result[:3, 3] = v
    return result

def rotation_y(angle):
    t = math.radians(angle)
    c, s = math.cos(t), math.sin(t)
    return np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]])

def error(one, two):
    witnesses = np.array([[0, 0, 0, 1], [13, 0, 0, 1], [0, 17, 5, 1]]).T
    return float(np.linalg.norm(((one - two) @ witnesses)[:3], axis=0).max())

ck('All 2393 source occurrence identities retained',
   items['source'].keys() == items['candidate'].keys() and len(items['candidate']) == 2393)
delta = translate(station['rigid_powertrain_translation_mm'])
shifted = {'TransmissionCore', 'FuelPressureInstallation', 'EngineFlywheelAssembly',
           'TankLibertyEngine', 'PortTransmissionOutput', 'StarboardTransmissionOutput',
           'FixedTransmissionBearings', 'LongitudinalSupports'}
old_axis = old['candidate_transmission_axis_xz_mm']
axis = translate([old_axis[0], 0, old_axis[1]])
phase_change = station['small_pinion_phase_deg'] - old['small_pinion_candidate_phase_deg']
phase = axis @ rotation_y(phase_change) @ np.linalg.inv(axis)
points = station['vertices_world_xz_mm']
old_points = old['vertices_world_xz_mm']

def route_frame(vertices, n, joint):
    v = np.asarray(vertices[n])
    ahead = np.asarray(vertices[(n + 1) % 50])
    behind = np.asarray(vertices[(n - 1) % 50]) if joint else v
    direction = ahead - behind
    angle = -math.degrees(math.atan2(direction[1], direction[0])) + (180 if joint else 0)
    return translate([v[0], 0, v[1]]) @ rotation_y(angle)

definitions = []
for name, now in items['candidate'].items():
    before = items['source'][name]
    expected = matrix(before['frame'])
    moving_parents = shifted.intersection(before['owners'])
    assert len(moving_parents) <= 1, name
    if moving_parents:
        expected = delta @ expected
    if name.endswith(('TransmissionOutput_shaft', 'TransmissionOutput_drum')):
        expected = delta @ phase @ matrix(before['frame'])
    if name.startswith(('PortChain_', 'StarboardChain_')):
        part = name.split('_', 1)[1]
        if part.startswith(('Link', 'Joint')):
            joint = part.startswith('Joint')
            n = int(part[5:7] if joint else part[4:6])
            expected = route_frame(points, n, joint) @ np.linalg.inv(route_frame(old_points, n, joint)) @ expected
        elif part == 'TransmissionPinion':
            expected = delta @ phase @ expected
        else:
            assert part == 'RollerPinion', name
    diff = error(matrix(now['frame']), expected)
    frames.append(dict(name=name, error_mm=diff, passed=diff < 1e-7 and
                       now['definition'] == before['definition'] and now['owners'] == before['owners']))
ck('Saved parentage and all composed frames match declared trial',
   all(v['passed'] for v in frames), maximum_frame_error_mm=max(v['error_mm'] for v in frames),
   failures=[v for v in frames if not v['passed']])
for name, definition in manifests['candidate']['definitions'].items():
    previous = manifests['source']['definitions'][name]
    same = definition['brep_sha256'] == previous['brep_sha256']
    definitions.append(dict(name=name, exact_brep=same, metadata_equal=definition['properties'] == previous['properties']))
ck('All definition identities and source metadata retained',
   manifests['candidate']['definitions'].keys() == manifests['source']['definitions'].keys() and
   all(v['metadata_equal'] for v in definitions), definitions=len(definitions))
# Byte differences after an ordinary save do not establish changed material.
# Preserve them as pending strict comparisons, outside these placement checks.
# This diagnostic must not claim that every physical definition is qualified.
pending_material = [v['name'] for v in definitions if not v['exact_brep']]
write(out / 'definition_preservation.json', dict(
    exact_brep_count=sum(v['exact_brep'] for v in definitions),
    pending_strict_material_comparisons=pending_material,
    all_definitions_qualified=not pending_material, definitions=definitions))

# Direct geometric witnesses on the saved occurrence frames: each bar has its
# two local bore axes at X=0 and X=76.2 mm; joints have a local Y axis at X=Z=0.
errors = []
for side in ['Port', 'Starboard']:
    for n in range(50):
        for suffix in ['Inboard', 'Outboard']:
            pose = matrix(items['candidate']['%sChain_Link%02d_%s' % (side, n, suffix)]['frame'])
            for local_x, endpoint in [(0, points[n]), (76.2, points[(n + 1) % 50])]:
                actual = pose @ [local_x, 0, 0, 1]
                errors.append(float(np.linalg.norm(actual[[0, 2]] - endpoint)))
        for suffix in ['Bush', 'Pin', 'Cotter']:
            pose = matrix(items['candidate']['%sChain_Joint%02d_%s' % (side, n, suffix)]['frame'])
            errors.append(float(np.linalg.norm(pose[[0, 2], 3] - points[n])))
ck('Both saved chains retain every pitch and joint axis', max(errors) < 1e-7,
   witnesses=len(errors), maximum_error_mm=max(errors))
ck('Frame negative control rejects a 1 mm vertical shift', error(np.eye(4), translate([0, 0, 1])) > 1e-7)

import FreeCAD as App
import Part
cache = {}

def shape(name, scope='candidate'):
    key = scope, name
    if key not in cache:
        row = items[scope][name]
        d = manifests[scope]['definitions'][row['definition']]
        f = Path(d['brep_path'])
        assert sha(f) == d['brep_sha256']
        s = Part.Shape()
        s.read(str(f))
        assert s.Placement.isIdentity(), name
        s.Placement = App.Placement(App.Matrix(*row['frame']))
        cache[key] = s
    return cache[key]

def overlap(one, two):
    if not one.BoundBox.intersect(two.BoundBox):
        return 0.0
    return one.common(two).Volume

output_pairs = []
for side in ['Port', 'Starboard']:
    shaft = shape(side + 'TransmissionOutput_shaft')
    for other in [side + 'TransmissionOutput_drum', side + 'Chain_TransmissionPinion']:
        volume = overlap(shaft, shape(other))
        output_pairs.append(dict(shaft=side + 'TransmissionOutput_shaft', neighbor=other,
                                 common_mm3=volume, passed=volume < 1e-5))
ck('Rephased output shaft retains drum and pinion spline clearance',
   all(v['passed'] for v in output_pairs), pairs=output_pairs)
negative = shape('PortTransmissionOutput_shaft', 'source').copy()
negative.translate(App.Vector(*station['rigid_powertrain_translation_mm']))
wrong_phase_overlap = overlap(negative, shape('PortChain_TransmissionPinion'))
ck('Negative control rejects translation without output spline rephasing',
   wrong_phase_overlap > 1e-5, common_mm3=wrong_phase_overlap)

oil = [name for name in items['candidate'] if name.startswith('EngineOilPump_')]
floor = ['hull_floor_5', 'hull_floor_6', 'hull_floor_7']
floor_rows = []
for scope in ['source', 'candidate']:
    floor_top = max(shape(name, scope).BoundBox.ZMax for name in floor)
    bottom = min(shape(name, scope).BoundBox.ZMin for name in oil)
    floor_rows.append(dict(scope=scope, floor_top_z_mm=floor_top,
                           pump_bottom_z_mm=bottom, envelope_gap_mm=bottom - floor_top))
gap = floor_rows[-1]['envelope_gap_mm']
ck('Saved oil pump envelope clears the unchanged floor',
   gap > 0 and abs(gap - station['proposed_floor_envelope_gap_mm']) < 1e-7,
   measurements=floor_rows, historical_height_uncertainty_mm=stations['pixel_only_height_bound_mm'])

# These are diagnostic measurements, not relaxed acceptance criteria. A positive
# distance can expose lost support contact; a common volume exposes interference.
pair_list = [
    ('EngineSuspension_LeftRail', 'EngineSuspension_LeftPacking'),
    ('EngineSuspension_RightRail', 'EngineSuspension_RightPacking'),
    ('EngineSuspension_LeftRail', 'EngineSuspension_FrontPacking'),
    ('PortFixedBearing_inner_bracket', 'TransmissionFrame_TopChannel'),
    ('PortFixedBearing_outer_bracket', 'TransmissionFrame_TopChannel'),
    ('PortTransmissionOutput_shaft', 'PortTransmissionCore_planet_disk'),
    ('StarboardTransmissionOutput_shaft', 'StarboardTransmissionCore_planet_disk'),
]
for first, second in pair_list:
    row = dict(first=first, second=second, measurements=[])
    for scope in ['source', 'candidate']:
        one, two = shape(first, scope), shape(second, scope)
        row['measurements'].append(dict(scope=scope, gap_mm=one.distToShape(two)[0],
                                       common_mm3=overlap(one, two)))
    interfaces.append(row)
    write(out / 'interface_progress.json', interfaces)
    print('interface measured', first, second, flush=True)

chain_pairs = []
casing_pairs = []
if a.chain_material:
    for side in ['Port', 'Starboard']:
        names = [name for name in items['candidate'] if name.startswith(side + 'Chain_')]
        assert len(names) == 252
        for i, left in enumerate(names):
            one = shape(left)
            for right in names[i + 1:]:
                two = shape(right)
                if not one.BoundBox.intersect(two.BoundBox):
                    continue
                volume = overlap(one, two)
                chain_pairs.append(dict(first=left, second=right, common_mm3=volume, passed=volume < 1e-5))
            for right in [side + 'Casing_Body', side + 'Casing_Cap']:
                two = shape(right)
                if one.BoundBox.intersect(two.BoundBox):
                    casing_pairs.append(dict(first=left, second=right, common_mm3=overlap(one, two)))
            write(out / 'chain_material_progress.json', dict(pairs=chain_pairs, old_casing_pairs=casing_pairs))
        print('chain solid comparisons complete', side, flush=True)
    ck('Actual saved chain solids have no internal overlap', all(v['passed'] for v in chain_pairs),
       pair_count=len(chain_pairs), failures=[v for v in chain_pairs if not v['passed']])

write(out / 'independent_checks.json', dict(
    placement_and_selected_interface_checks_passed=all(v['passed'] for v in checks),
    native_sha256=sha(native), checker_sha256=sha(Path(__file__)),
    source_manifest_sha256=sha(source_path), candidate_manifest_sha256=sha(candidate_path),
    checks=checks, occurrence_frames=frames, definitions=definitions,
    pending_strict_material_comparisons=pending_material,
    all_definitions_qualified=not pending_material,
    unresolved_interface_measurements=interfaces, chain_material_checked=a.chain_material,
    chain_material_pairs=chain_pairs, old_casing_pairs=casing_pairs,
    pending_interfaces=r['pending_interfaces'], installation_qualified=False,
    historical_station_qualified=False, standard_assembly_modified=False,
))
assert all(v['passed'] for v in checks), 'See separate failed criterion; installation remains unqualified regardless.'
