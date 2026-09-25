"""Independently inspect saved rod material, revised eyes and mating cylindrical interfaces."""
import argparse
import itertools
import math
from pathlib import Path
import sys

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path.insert(0, str(H.parents[1]))
import FreeCAD as App
import Part
from lib.evidence import read, write, sha
from lib.camera_review import validate_native_bindings

V = App.Vector
X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, required=True)
a = p.parse_args()
out = a.candidate.resolve()
r, m = read(out/'report.json'), read(out/'isolated/manifest.json')
native = out/r['native_file']
parent = ROOT/r['parent_native']
old = read(parent.parent/'isolated/manifest.json')
assert sha(native) == r['native_sha256'] == m['native_sha256']
assert sha(parent) == r['parent_native_sha256'] == old['native_sha256']
assert all(sha(ROOT/f) == d for f, d in r['input_hashes'].items())
rows, prior = [{v['name']: v for v in data['occurrences']} for data in [m, old]]
validate_native_bindings(dict(native_file=str(native), render_occurrences=list(rows), landmarks=[]), m)
validate_native_bindings(dict(native_file=str(parent), render_occurrences=[n for n in rows if n in prior], landmarks=[]), old)
cache, shapes, checks, interfaces = {}, {}, [], []


def ck(name, passed, **kw):
    checks.append(dict(name=name, passed=bool(passed), **kw))


def definition(key, data=m):
    d = data['definitions'][key]
    digest = d['brep_sha256']
    if digest not in cache:
        assert sha(d['brep_path']) == digest
        s = Part.Shape()
        s.read(d['brep_path'])
        cache[digest] = s
    return cache[digest].copy()


def placed(row, data=m):
    s = definition(row['definition'], data)
    s.Placement = App.Placement(App.Matrix(*row['frame']))
    return s


def empty(shape):
    return not shape.Faces and not shape.Solids


def same(a, b):
    return empty(a.cut(b)) and empty(b.cut(a))


def cylinders(shape, center, axis, radius):
    return [f for f in shape.Faces if isinstance(f.Surface, Part.Cylinder) and
            abs(f.Surface.Radius-radius) < 1e-6 and f.Surface.Axis.cross(axis).Length < 1e-7
            and (f.Surface.Center-center).cross(axis).Length < 1e-6]


def measured_eye(name, local_center, local_axis, radius=6.5):
    row = rows[name]
    s = definition(row['definition'])
    faces = cylinders(s, local_center, local_axis, radius)
    ck(name+' actual cylindrical eye', len(faces) == 1)
    assert len(faces) == 1
    values = [v.Point.dot(local_axis) for v in faces[0].Vertexes]
    midpoint = (max(values)+min(values))/2
    center = local_center+local_axis*(midpoint-local_center.dot(local_axis))
    pose = App.Placement(App.Matrix(*row['frame']))
    point, axis = pose.multVec(center), pose.Rotation.multVec(local_axis)
    interfaces.append(dict(occurrence=name, local_center_mm=list(center), center_world_mm=list(point),
                           pin_axis_world=list(axis), bore_diameter_mm=2*faces[0].Surface.Radius,
                           bearing_width_mm=max(values)-min(values), definition=row['definition'],
                           definition_sha256=m['definitions'][row['definition']]['brep_sha256']))
    return point, axis


ck('Exactly24 components and seven definitions; two new rod occurrences',
   len(rows) == 24 and len(m['definitions']) == 7 and
   set(rows)-set(prior) == {'PortTrackConnectingRod', 'StarboardTrackConnectingRod'})
doc = App.openDocument(str(native))
try:
    for key in m['definitions']:
        body = doc.getObject(key)
        s = body.Shape
        ck(key+' closed canonical single solid', body.Placement.isIdentity() and s.Placement.isIdentity()
           and s.isValid() and len(s.Solids) == 1 and s.Solids[0].isClosed() and s.getTolerance(1) <= 1e-4)
    for name, row in rows.items():
        obj = doc.getObject(name)
        ck(name+' source-bound unscaled local link', obj.TypeId == 'App::Link' and
           obj.LinkedObject.Name == r['specs'][name]['definition'] and obj.Scale == 1 and
           tuple(obj.ScaleVector) == (1., 1., 1.) and
           max(abs(x-y) for x, y in zip(row['frame'], r['specs'][name]['frame'])) < 1e-7)
finally:
    App.closeDocument(doc.Name)
for key in m['definitions']:
    if key not in ['Def_RearTrackRod', *r['changed_definitions']]:
        ck(key+' complete previous material retained', same(definition(key), definition(key, old)))
before, after = definition('Def_BrakeFront_lever', old), definition('Def_BrakeFront_lever')
for center, radius, label in [(V(), 12.15, 'pivot'), (V(75, 0, 0), 22.375, 'swivel')]:
    one, two = cylinders(before, center, Y, radius), cylinders(after, center, Y, radius)
    ck('M330 '+label+' complete cylindrical bearing faces retained',
       bool(one) and len(one) == len(two) and same(Part.makeCompound(one), Part.makeCompound(two)))
oldtrack = definition('Def_RearControlFulcrum_lever_track', old)
newtrack = definition('Def_RearControlFulcrum_lever_track')
# The journal and entire front-arm half-space must be retained, independently
# of the shortened rear arm and its recomputed rod-eye position.
front_half = Part.makeBox(100, 260, 60, V(-50, 0, -1))
ck('M4132 entire front arm and upper/lower hub half retained',
   same(oldtrack.common(front_half), newtrack.common(front_half)))
one = cylinders(oldtrack, V(), Z, 16.025)
two = cylinders(newtrack, V(), Z, 16.025)
ck('M4132 complete cylindrical journal bearing retained', bool(one) and len(one) == len(two)
   and same(Part.makeCompound(one), Part.makeCompound(two)))
ck('M330 eye changed, old distal bore no longer exists',
   len(cylinders(before, V(-25, 0, -220), Y, 6.5)) == 1 and
   not cylinders(after, V(-25, 0, -220), Y, 6.5))
c = r['controls']
rod = definition('Def_RearTrackRod')
endfaces = [f for f in rod.Faces if isinstance(f.Surface, Part.Plane) and f.normalAt(0, 0).cross(X).Length < 1e-7]
xs = sorted(f.CenterOfMass.x for f in endfaces)
ck('Rod is one solid cylinder with two actual flat ends', len(rod.Faces) == 3 and len(xs) == 2
   and len(cylinders(rod, V(), X, 9.525)) == 1)
length = xs[-1]-xs[0]
ck('Rod material equals full nominal solid stock',
   abs(rod.Volume-math.pi*9.525**2*length) < 1e-5, length_mm=length, volume_mm3=rod.Volume)
ck('Both sides reuse one physical rod definition',
   all(rows[side+'TrackConnectingRod']['definition'] == 'Def_RearTrackRod' for side in ['Port', 'Starboard']))
for name in rows:
    shapes[name] = placed(rows[name])
for side in ['Starboard', 'Port']:
    eyes = {}
    for kind in ['Track', 'LowSpeed']:
        name = side+kind+'BrakeLever'
        center, axis = measured_eye(name, V(-25, 0, r['details']['new_lever_controls']['lever_end_z']), Y)
        ck(name+' upper pivot frame retained', max(abs(a-b) for a, b in zip(rows[name]['frame'], prior[name]['frame'])) < 1e-7)
        if kind == 'Track':
            eyes['Brake'] = (center, axis)
    name = side+'TrackHorizontalLever'
    eyes['Fulcrum'] = measured_eye(name, V(*r['details']['new_track_arm_local_mm']), Z)
    measured_eye(name, V(0, 203.2, 31.75), Z)
    oldpose = App.Placement(App.Matrix(*prior[name]['frame']))
    newpose = App.Placement(App.Matrix(*rows[name]['frame']))
    ck(side+' horizontal lever retained journal axis and seat',
       (oldpose.Base-newpose.Base).Length < 1e-7 and
       oldpose.Rotation.multVec(Z).cross(newpose.Rotation.multVec(Z)).Length < 1e-7)
    rod_world = shapes[side+'TrackConnectingRod']
    rodpose = App.Placement(App.Matrix(*rows[side+'TrackConnectingRod']['frame']))
    rod_ends = [rodpose.multVec(V(x, 0, 0)) for x in xs]
    for end, (point, axis) in eyes.items():
        joint = side+'Track'+end+'Joint'
        forkpose = App.Placement(App.Matrix(*rows[joint+'Fork']['frame']))
        ck(joint+' true receiver bore coaxial and centered in fork',
           (point-forkpose.Base).Length < 1e-6 and axis.cross(forkpose.Rotation.multVec(Y)).Length < 1e-7)
        fork, nut = shapes[joint+'Fork'], shapes[joint+'Nut']
        inv = forkpose.inverse()
        tips = sorted((inv.multVec(v) for v in rod_ends), key=lambda v: v.x)
        planes = [f for f in definition(rows[joint+'Fork']['definition']).Faces
                  if isinstance(f.Surface, Part.Plane) and f.normalAt(0, 0).cross(X).Length < 1e-7]
        seat = max(f.CenterOfMass.x for f in planes)
        insertion = seat-tips[0].x
        ck(joint+' actual rod axis and full thread engagement',
           max(abs(v.y)+abs(v.z) for v in tips) < 1e-6 and
           c['minimum_insertion_mm'] <= insertion <= c['socket_length_mm'], insertion_mm=insertion)
        ck(joint+' rod fills whole nut axial passage',
           tips[0].x < seat and tips[1].x > seat+c['nut_height_mm'] and
           empty(rod_world.common(nut)))
        ck(joint+' rod clears fork and pin material',
           empty(rod_world.common(fork)) and empty(rod_world.common(shapes[joint+'Pin'])))
        shifted = rod_world.copy()
        shifted.translate(forkpose.Rotation.multVec(Z)*.3)
        ck(joint+' offset rod is rejected by receiving thread envelope', shifted.common(fork).Volume > 1e-3)
        withdrawn = rod_world.copy()
        withdrawn.translate(forkpose.Rotation.multVec(X)*3.5)
        withdrawn_ends = [inv.multVec(f.CenterOfMass).x for f in withdrawn.Faces
                          if isinstance(f.Surface, Part.Plane)]
        ck(joint+' withdrawn rod fails required engagement',
           seat-min(withdrawn_ends) < c['minimum_insertion_mm'])
        local_frames = {}
        parent_group = App.Placement(App.Matrix(*old['assemblies'][joint]['world']))
        for suffix in ['Fork', 'Pin', 'Cotter', 'Nut']:
            oldlocal = parent_group.inverse().multiply(App.Placement(App.Matrix(*prior[joint+suffix]['frame'])))
            newlocal = forkpose.inverse().multiply(App.Placement(App.Matrix(*rows[joint+suffix]['frame'])))
            local_frames[suffix] = max(abs(x-y) for x, y in zip(oldlocal.toMatrix().A, newlocal.toMatrix().A))
        ck(joint+' complete previously tested pin/cotter/nut stack retained', max(local_frames.values()) < 1e-7)
    ck(side+' both actual pin centers collinear with straight rod',
       all((center-rodpose.Base).cross(rodpose.Rotation.multVec(X)).Length < 1e-6 for center, axis in eyes.values()))
    ck(side+' thread stock extends through both nuts',
       c['thread_length_mm'] >= c['insertion_mm']+c['nut_height_mm'])
write(out/'operating_interfaces.json', dict(native_sha256=sha(native), checker_sha256=sha(Path(__file__)),
      interfaces=interfaces, scope='Actual saved revised M330 distal eyes and both M4132 rod eyes. Earlier eye receipts remain immutable but these eight coordinates supersede them for this trial.'))
result = dict(passed=all(v['passed'] for v in checks), checks=checks, native_sha256=sha(native),
              parent_native_sha256=sha(parent), checker_sha256=sha(Path(__file__)),
              scope='Saved native identity, material, shared rod stock, real eyes/axes, pivot/swivel preservation, thread engagement, full nut passage and displaced-rod negative. Whole surrounding interference checked separately.',
              historical_geometry_qualified=False, installation_qualified=False)
write(out/'independent_checks.json', result)
print(len(checks), 'saved rod/interface checks;', result['passed'], flush=True)
for row in checks:
    if not row['passed']:
        print(row, flush=True)
assert result['passed']
