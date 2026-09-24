"""Test local M575 route envelopes through saved forks and candidate spring guides.

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
for name, point in r['controls']['stations'].items():
    fork_name = name+'HighSpeedBrakeControlFork'
    fork_row = prior[fork_name]
    fork = world(fork_row, old)
    pose = App.Placement(App.Matrix(*fork_row['frame']))
    direction = pose.Rotation.multVec(V(1, 0, 0))
    socket = [f for f in fork.Faces if isinstance(f.Surface, Part.Cylinder) and
              abs(f.Surface.Radius-9.625) < 1e-7 and
              abs(abs(f.Surface.Axis.dot(direction))-1) < 1e-7]
    assert len(socket) == 1
    start = pose.multVec(V(19.05, 0, 0))
    first = pose.multVec(V(70, 0, 0))
    guide = V(*point)+V(0, 0, r['controls']['bracket']['guide_height'])
    straight_start = V(2250., guide.y, guide.z)
    poles = [first, first+direction*45., straight_start-V(45., 0, 0), straight_start]
    curve = Part.BezierCurve()
    curve.setPoles(poles)
    end = guide+V(150., 0, 0)
    spine = Part.Wire([Part.makeLine(start, first), curve.toShape(), Part.makeLine(straight_start, end)])
    profile = Part.Wire([Part.makeCircle(19.05/2, start, direction)])
    rod = spine.makePipeShell([profile], True, False)
    assert rod.isValid() and len(rod.Solids) == 1 and rod.Solids[0].isClosed()
    spring = Part.makeCylinder(16., guide.x-straight_start.x, straight_start, V(1, 0, 0))
    radii = []
    for u in np.linspace(0, 1, 1001):
        derivative = (poles[1]-poles[0])*(3*(1-u)**2)+(poles[2]-poles[1])*(6*u*(1-u))+(poles[3]-poles[2])*(3*u*u)
        second = (poles[2]-poles[1]*2+poles[0])*(6*(1-u))+(poles[3]-poles[2]*2+poles[1])*(6*u)
        cross = derivative.cross(second).Length
        if cross > 1e-10:
            radii.append(derivative.Length**3/cross)
    assert min(radii) > 19.05/2
    for suffix, shape in [('RodEnvelope', rod), ('SpringEnvelope', spring)]:
        key = name+suffix
        shape.exportBrep(str(out/(key+'.brep')))
        envelopes[key] = shape
    routes[name] = dict(fork_occurrence=fork_name, fork_definition_sha256=old['definitions'][fork_row['definition']]['brep_sha256'],
                        rod_start_world_mm=list(start), initial_tangent=list(direction),
                        bezier_poles_world_mm=[list(v) for v in poles], guide_center_world_mm=list(guide),
                        forward_limit_world_mm=list(end), diameter_mm=19.05,
                        sampled_minimum_centerline_radius_mm=min(radii),
                        radius_sample_count=1001, spring_envelope_radius_mm=16.,
                        spring_envelope_length_mm=guide.x-straight_start.x,
                        scope='Local route witness only; sampled radius is not a rigorous minimum or forming limit. '
                              'Spring envelope dimensions are clearance hypotheses, not source dimensions.')
    selected_parent.append(fork_name)

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
        if n != 'RearControlChannelStock' and overlaps(box, other):
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
validate_native_bindings(dict(native_file=str(parent), render_occurrences=sorted(set(selected_parent)), landmarks=[]), old)
validate_native_bindings(dict(native_file=str(native), render_occurrences=list(rows), landmarks=[]), m)
write(out/'route_checks.json', dict(passed=all(v['passed'] for v in pairs), routes=routes, pairs=pairs,
    trial_native_sha256=sha(native), parent_native_sha256=sha(parent),
    standard_manifest_sha256=sha(standard_path), probe_sha256=sha(Path(__file__)),
    geometry_hashes={p.name: sha(p) for p in out.glob('*.brep')}, geometry_integrated=False,
    historical_geometry_qualified=False,
    scope='Four local clearance envelopes against all retained parent/standard solids and the guide trial. '
          'Does not establish complete M575 rods, spring design, remote control connections or operation.'))
print('Local rod/spring envelope checks:', len(pairs), 'pairs;', all(v['passed'] for v in pairs), flush=True)
print([v for v in pairs if not v['passed']], flush=True)
assert all(v['passed'] for v in pairs)
