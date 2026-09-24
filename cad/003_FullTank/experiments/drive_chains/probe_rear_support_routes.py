"""Test provisional short-brake rod cores and M564 spring corridors near the combined rear supports.

These are clearance witnesses, not complete rods or reconstructed springs.
"""
import argparse
import itertools
import math
from pathlib import Path
import sys
import numpy as np
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
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
trial = a.candidate.resolve()
out = a.output.resolve()
assert not out.exists()
r = read(trial/'report.json')
m = read(trial/'isolated/manifest.json')
native = trial/r['native_file']
assert sha(native) == r['native_sha256'] == m['native_sha256']
parent = ROOT/r['parent_native']
old = read(parent.parent/'isolated/manifest.json')
assert sha(parent) == r['parent_native_sha256'] == old['native_sha256']
standard_path = H/'transmission_brake_front_study/trial01/standard_context_manifest.json'
standard = read(standard_path)
assert all(sha(ROOT/f) == digest for f, digest in standard['native_files'].items())
rows, prior, tank = [{v['name']: v for v in data['occurrences']} for data in [m, old, standard]]
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
    return cache[digest]


def world(row, manifest):
    s = definition(row['definition'], manifest).copy()
    s.Placement = App.Placement(App.Matrix(*row['frame']))
    return s


def bounds(s):
    b = s.BoundBox
    return np.array([b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax])


def overlaps(a, b):
    return np.all(a[:3] <= b[3:]+1e-7) and np.all(b[:3] <= a[3:]+1e-7)


out.mkdir(parents=True)
routes = {}
envelopes = {}
selected_parent = []
C = H/'transmission_controls_study'
packet = read(C/'spring_sources01/sources.json')
interfaces = read(parent.parent/'operating_interfaces.json')
assert packet['previous_interface_probe_sha256'] == sha(parent.parent/'operating_interfaces.json')
assert interfaces['native_sha256'] == sha(parent)
eyes = {v['id']: v for v in interfaces['new_rod_eyes']+interfaces['verified_rear_brake_eyes']}
for route in packet['corrected_route_identities']:
    first, last = eyes[route['rear_brake_eye']], eyes[route['fulcrum_eye']]
    name = route['fulcrum_eye'].removesuffix('BrakeRodEye')
    sign = 1 if name.startswith('Port') else -1
    side = 'Port' if sign > 0 else 'Starboard'
    track = 'Track' in name
    start = V(*first['center_world_mm'])+V(38.1, 0, 0)
    end = V(*last['center_world_mm'])-V(38.1, 0, 0)
    # Horizontal tangents are perpendicular to both inherited Y and new Z pin axes.
    # End trim remains a fork/socket hypothesis; these cores are not complete rods.
    length = end.x-start.x
    assert length > 40
    poles = [start, start+V(length/3, 0, 0), end-V(length/3, 0, 0), end]
    curve = Part.BezierCurve();curve.setPoles(poles)
    spine = Part.Wire([curve.toShape()])
    rod = spine.makePipeShell([Part.Wire([Part.makeCircle(19.05/2, start, V(1, 0, 0))])], True, False)
    low_source = ROOT/r['prototype_inputs']['low']['native']
    inherited = read(low_source.parent/'report.json')['controls']
    b = inherited['bracket']
    base = V(*inherited['stations'][side])+V(0, 0, r['controls']['cleat']['stock'])
    leg_sign = sign if track else -sign
    anchor = base+V(0, leg_sign*(b['outer_span_y']/2-b['stock']/2), b['anchor_height'])
    bracket = world(rows[side+'LowSpringBracket'], m)
    anchor_faces = [f for f in bracket.Faces if isinstance(f.Surface, Part.Cylinder) and
                    abs(f.Surface.Radius-b['anchor_hole_diameter']/2) < 1e-7 and
                    abs(abs(f.Surface.Axis.y)-1) < 1e-7 and
                    math.hypot(f.Surface.Center.x-anchor.x, f.Surface.Center.z-anchor.z) < 1e-6 and
                    abs(f.CenterOfMass.y-anchor.y) < 1e-6]
    assert len(anchor_faces) == 1
    target = V(*first['center_world_mm'])+V(0, sign*(25. if track else -25.), 0)
    line = target-anchor
    direction = line/line.Length
    spring = Part.makeCylinder(9.525, line.Length-50.8, anchor+direction*25.4, direction)
    radii = []
    for u in np.linspace(0, 1, 1001):
        derivative = (poles[1]-poles[0])*(3*(1-u)**2)+(poles[2]-poles[1])*(6*u*(1-u))+(poles[3]-poles[2])*(3*u*u)
        second = (poles[2]-poles[1]*2+poles[0])*(6*(1-u))+(poles[3]-poles[2]*2+poles[1])*(6*u)
        cross = derivative.cross(second).Length
        if cross > 1e-10:radii.append(derivative.Length**3/cross)
    assert min(radii) > 19.05/2
    for suffix, shape in [('RodCore', rod), ('SpringCore', spring)]:
        assert shape.isValid() and len(shape.Solids) == 1 and shape.Solids[0].isClosed()
        key = name+suffix
        shape.exportBrep(str(out/(key+'.brep')));envelopes[key] = shape
    routes[name] = dict(rod_mark=route['selected_snl_mark'],end_fork_mark=route['end_fork_mark'],
        source_endpoint_ids=[first['id'],last['id']],pin_axes=[first['pin_axis_world'],last['pin_axis_world']],
        bezier_poles_world_mm=[list(v) for v in poles],rod_diameter_mm=19.05,
        end_trim_from_pin_centers_mm=38.1,sampled_minimum_centerline_radius_mm=min(radii),radius_sample_count=1001,
        spring_anchor_world_mm=list(anchor),provisional_pin_washer_target_world_mm=list(target),
        spring_envelope_radius_mm=9.525,spring_hook_exclusion_each_mm=25.4,
        spring_core_length_mm=line.Length-50.8,
        scope='Rod midspan and spring core clearance hypotheses only. Forks, threaded engagement, washers, hooks and complete physical springs remain unqualified. Sampled radius is not a forming limit.')
    selected_parent.extend([first['occurrence'],last['occurrence']])

local_boxes = {}
for key in old['definitions']:
    box = bounds(definition(key, old))
    local_boxes[key] = np.array(list(itertools.product(*[(box[i], box[i+3]) for i in range(3)])))
boxes = {}
for name, row in prior.items():
    f = np.array(row['frame']).reshape(4, 4)
    points = local_boxes[row['definition']]@f[:3, :3].T+f[:3, 3]
    boxes[name] = np.r_[points.min(axis=0), points.max(axis=0)]
excluded = (set(prior)&set(tank)) | {'PortPinion_Rotor_Casting', 'StarboardPinion_Rotor_Casting'}
pairs = []
for name, one in envelopes.items():
    candidates = []
    box = bounds(one)
    for n, other in boxes.items():
        if n not in {'RearControlChannelStock','hull_floor_7'} and overlaps(box, other):
            candidates.append((n, 'development', world(prior[n], old)))
            selected_parent.append(n)
    for n, row in tank.items():
        if n not in excluded and row['representation'] == 'assembly' and overlaps(box, np.array(row['bounds_mm'])):
            candidates.append((n, 'retained_standard', world(row, standard)))
    for n, row in rows.items():
        shape = world(row, m)
        if overlaps(box, bounds(shape)):
            candidates.append((n, 'guide_trial', shape))
    for n, origin, two in candidates:
        common = one.common(two)
        occupied = sum(abs(s.Volume) for s in common.Solids)
        pairs.append(dict(first=name, second=n, origin=origin, common_mm3=occupied,
                          passed=(common.isNull() or common.isValid()) and occupied < 1e-5))
        write(out/'progress.json', dict(pairs=pairs))
# Distinct rod and spring corridors must also clear one another.
for (name, one), (other, two) in itertools.combinations(envelopes.items(), 2):
    if not overlaps(bounds(one), bounds(two)):continue
    common = one.common(two);occupied = sum(abs(v.Volume) for v in common.Solids)
    pairs.append(dict(first=name,second=other,origin='other_corridor',common_mm3=occupied,
                      passed=(common.isNull() or common.isValid()) and occupied < 1e-5))
validate_native_bindings(dict(native_file=str(parent), render_occurrences=sorted(set(selected_parent)), landmarks=[]), old)
validate_native_bindings(dict(native_file=str(native), render_occurrences=list(rows), landmarks=[]), m)
write(out/'route_checks.json', dict(passed=all(v['passed'] for v in pairs), routes=routes, pairs=pairs,
    trial_native_sha256=sha(native), parent_native_sha256=sha(parent),
    standard_manifest_sha256=sha(standard_path), probe_sha256=sha(Path(__file__)),source_packet_sha256=sha(C/'spring_sources01/sources.json'),interface_probe_sha256=sha(parent.parent/'operating_interfaces.json'),
    geometry_hashes={p.name: sha(p) for p in out.glob('*.brep')}, geometry_integrated=False,
    historical_geometry_qualified=False,
    scope='Eight provisional midspan/core clearance envelopes against all retained parent/standard solids and the guide trial. '
          'Does not qualify full SH946D/SH946E rods, forks, spring hooks, washer targets, movement or service.'))
print('Local rod/spring envelope checks:', len(pairs), 'pairs;', all(v['passed'] for v in pairs), flush=True)
print([v for v in pairs if not v['passed']], flush=True)
assert all(v['passed'] for v in pairs)
