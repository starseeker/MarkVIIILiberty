"""Independently inspect saved low-speed rod material, revised fulcrum levers and mating cylindrical interfaces."""
import argparse
import itertools
import math
from pathlib import Path
import sys

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path.insert(0, str(H.parents[1]))
sys.path.insert(0, str(H))
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


ck('Exactly 22 components and 8 definitions; two new low rod occurrences',
   len(rows) == 22 and len(m['definitions']) == 8 and
   set(rows)-set(prior) == {'PortLowConnectingRod', 'StarboardLowConnectingRod'})

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
    if key not in ['Def_RearLowRod', *r['changed_definitions']]:
        ck(key+' complete previous material retained', same(definition(key), definition(key, old)))

# Fulcrum levers journal and front arm retention
for def_key, front_vector in [
    ('Def_RearControlFulcrum_lever_low_right', V(-114.3, 171.45, 25.4)),
    ('Def_RearControlFulcrum_lever_low_left', V(-107.95, -158.75, 25.4))
]:
    oldlever = definition(def_key, old)
    newlever = definition(def_key)
    # Journal bearing cylinder
    j_old = cylinders(oldlever, V(), Z, 16.025)
    j_new = cylinders(newlever, V(), Z, 16.025)
    ck(def_key+' journal bearing cylinder retained',
       bool(j_old) and len(j_old) == len(j_new) and same(Part.makeCompound(j_old), Part.makeCompound(j_new)))
    # Front arm eye cylinder
    f_old = cylinders(oldlever, front_vector, Z, 6.5)
    f_new = cylinders(newlever, front_vector, Z, 6.5)
    ck(def_key+' front arm eye retained',
       bool(f_old) and len(f_old) == len(f_new) and same(Part.makeCompound(f_old), Part.makeCompound(f_new)))

c = r['controls']
rod = definition('Def_RearLowRod')
endfaces = [f for f in rod.Faces if isinstance(f.Surface, Part.Plane) and f.normalAt(0, 0).cross(X).Length < 1e-7]
xs = sorted(f.CenterOfMass.x for f in endfaces)
ck('Rod is one solid cylinder with two actual flat ends', len(rod.Faces) == 3 and len(xs) == 2
   and len(cylinders(rod, V(), X, 9.525)) == 1)
length = xs[-1]-xs[0]
ck('Rod material equals full nominal solid stock',
   abs(rod.Volume-math.pi*9.525**2*length) < 1e-5, length_mm=length, volume_mm3=rod.Volume)
ck('Both sides reuse one physical rod definition',
   all(rows[side+'LowConnectingRod']['definition'] == 'Def_RearLowRod' for side in ['Port', 'Starboard']))

for name in rows:
    shapes[name] = placed(rows[name])

for side in ['Starboard', 'Port']:
    eyes = {}
    sign = -1 if side == 'Starboard' else 1
    # Front brake lever eye
    name_brake = side+'LowSpeedBrakeLever'
    eyes['Brake'] = measured_eye(name_brake, V(-25, 0, -205.4779411764705), Y)
    ck(name_brake+' frame retained', max(abs(a-b) for a, b in zip(rows[name_brake]['frame'], prior[name_brake]['frame'])) < 1e-7)

    # Fulcrum lever brake eye
    name_fulcrum = side+'LowHorizontalLever'
    arm_x = c['lever_brake_arm_x_mm']
    arm_y = sign * 85.3957142857142
    eyes['Fulcrum'] = measured_eye(name_fulcrum, V(arm_x, arm_y, 31.75), Z)

    # Front long rod eye
    front_v = V(-114.3, 171.45, 31.75) if side == 'Starboard' else V(-107.95, -158.75, 31.75)
    measured_eye(name_fulcrum, front_v, Z)

    oldpose = App.Placement(App.Matrix(*prior[name_fulcrum]['frame']))
    newpose = App.Placement(App.Matrix(*rows[name_fulcrum]['frame']))
    ck(side+' horizontal lever retained journal axis and seat',
       (oldpose.Base-newpose.Base).Length < 1e-7 and
       oldpose.Rotation.multVec(Z).cross(newpose.Rotation.multVec(Z)).Length < 1e-7)

    rod_world = shapes[side+'LowConnectingRod']
    rodpose = App.Placement(App.Matrix(*rows[side+'LowConnectingRod']['frame']))
    rod_ends = [rodpose.multVec(V(x, 0, 0)) for x in xs]

    for end, (point, axis) in eyes.items():
        joint = side+'Low'+end+'Joint'
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

        # Shifted rod check
        shifted = rod_world.copy()
        shifted.translate(forkpose.Rotation.multVec(Z)*.3)
        ck(joint+' offset rod is rejected by receiving thread envelope', shifted.common(fork).Volume > 1e-3)

        # Withdrawn rod check
        withdrawn = rod_world.copy()
        withdrawn.translate(forkpose.Rotation.multVec(X)*3.5)
        withdrawn_ends = [inv.multVec(f.CenterOfMass).x for f in withdrawn.Faces
                          if isinstance(f.Surface, Part.Plane)]
        ck(joint+' withdrawn rod fails required engagement',
           seat-min(withdrawn_ends) < c['minimum_insertion_mm'])

    ck(side+' both actual pin centers collinear with straight rod',
       all((center-rodpose.Base).cross(rodpose.Rotation.multVec(X)).Length < 1e-6 for center, axis in eyes.values()))
    ck(side+' thread stock extends through both nuts',
       c['thread_length_mm'] >= c['insertion_mm']+c['nut_height_mm'])

write(out/'operating_interfaces.json', dict(
    native_sha256=sha(native),
    checker_sha256=sha(Path(__file__)),
    interfaces=interfaces,
    scope='Actual saved low-speed brake receiver eyes and M4133/M4134 fulcrum eyes.'
))

result = dict(
    passed=all(v['passed'] for v in checks),
    checks=checks,
    native_sha256=sha(native),
    parent_native_sha256=sha(parent),
    checker_sha256=sha(Path(__file__)),
    scope='Saved native identity, material, shared rod stock, real eyes/axes, lever preservation, thread engagement, full nut passage and displaced-rod negative.',
    historical_geometry_qualified=False,
    installation_qualified=False
)
write(out/'independent_checks.json', result)
print(len(checks), 'saved rod/interface checks;', result['passed'], flush=True)
for row in checks:
    if not row['passed']:
        print(row, flush=True)
assert result['passed']
