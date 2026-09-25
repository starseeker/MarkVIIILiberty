"""Measure actual saved interfaces and confine the pin-family changes to their declared material."""
import argparse
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
assert all(sha(ROOT/f) == h for f, h in r['input_hashes'].items())
rows, prior = [{v['name']: v for v in data['occurrences']} for data in (m, old)]
validate_native_bindings(dict(native_file=str(native), render_occurrences=list(rows), landmarks=[]), m)
cache, checks, interfaces = {}, [], []


def ck(name, passed, **detail):
    checks.append(dict(name=name, passed=bool(passed), **detail))


def definition(key, data=m):
    d = data['definitions'][key]
    digest = d['brep_sha256']
    if digest not in cache:
        assert sha(d['brep_path']) == digest
        s = Part.Shape()
        s.read(d['brep_path'])
        cache[digest] = s
    return cache[digest].copy()


def placed(name, data=m):
    row = next(v for v in data['occurrences'] if v['name'] == name)
    s = definition(row['definition'], data)
    s.Placement = App.Placement(App.Matrix(*row['frame']))
    return s


def empty(shape):
    return not shape.Faces and not shape.Solids


def same(one, two):
    return empty(one.cut(two)) and empty(two.cut(one))


def cylinders(shape, center, axis, radius):
    return [f for f in shape.Faces if isinstance(f.Surface, Part.Cylinder)
            and abs(f.Surface.Radius-radius) < 1e-7
            and f.Surface.Axis.cross(axis).Length < 1e-7
            and (f.Surface.Center-center).cross(axis).Length < 1e-6]


def radial_stock(center, lo, hi, outer, inner):
    base = center+Y*lo
    return Part.makeCylinder(outer, hi-lo, base, Y).cut(
        Part.makeCylinder(inner, hi-lo+2, base-Y, Y))


ck('16 installed components and9 shared definitions', len(rows) == 16 and len(m['definitions']) == 9)
for key in m['definitions']:
    s = definition(key)
    ck(key+' canonical valid closed single solid', s.Placement.isIdentity() and s.isValid()
       and len(s.Solids) == 1 and s.Solids[0].isClosed() and s.getTolerance(1) <= 1e-4)
    if key not in r['changed_definitions']:
        ck(key+' entire previous material retained', same(s, definition(key, old)))
doc = App.openDocument(str(native))
try:
    for name, row in rows.items():
        link = doc.getObject(name)
        ck(name+' unscaled shared link and previous world frame retained',
           link.TypeId == 'App::Link' and link.LinkedObject.Name == prior[name]['definition']
           and link.Scale == 1 and tuple(link.ScaleVector) == (1., 1., 1.)
           and max(abs(a-b) for a, b in zip(row['frame'], prior[name]['frame'])) < 1e-7)
    ck('Existing M568A source identity retained', doc.Def_ControlJoint_pin.SourcePartMark == 'M568A')
finally:
    App.closeDocument(doc.Name)
radius = r['controls']['pin_diameter_mm']/2
bore = radius+r['controls']['high_radial_gap_mm']
pin = definition('Def_ControlJoint_pin')
oldpin = definition('Def_ControlJoint_pin', old)
shank = cylinders(pin, V(), Y, radius)
ck('Actual pin shank cylinder is selected common diameter', len(shank) >= 1,
   diameter_mm=2*radius)
ends = [v.Point.y for f in shank for v in f.Vertexes]
ck('Printed1 5/8inch length retained under head', abs(max(ends)-min(ends)-41.275) < 1e-7
   and abs(min(ends)+17.7125) < 1e-7)
head_region = Part.makeBox(40, 3.175, 40, V(-20, -20.8875, -20))
ck('Complete pin head and seating face retained', same(pin.common(head_region), oldpin.common(head_region)))
ck('Actual3.375mm cross-hole remains on original axis and station',
   bool(cylinders(pin, V(0, 20.0125, 0), X, 1.6875)))
removed = oldpin.cut(pin)
allowed = radial_stock(V(), -17.7125, 23.5625, 7.9375, radius).common(oldpin)
ck('Only declared shank annulus removed; no added pin material', same(removed, allowed)
   and empty(pin.cut(oldpin)), removed_mm3=removed.Volume)
for key, spans, center in [
        ('Def_ControlJoint_fork', [(-17.7125, -12.95), (12.95, 17.7125)], V()),
        ('Def_HighBrakeMechanism_lever_left', [(-12.7, 0)], V(238.45, 0, -293.675)),
        ('Def_HighBrakeMechanism_lever_right', [(0, 12.7)], V(238.45, 0, -293.675))]:
    before, after = definition(key, old), definition(key)
    add = Part.makeCompound([radial_stock(center, lo, hi, 8.0875, bore) for lo, hi in spans])
    ck(key+' added material equals only distal-bore annuli', same(after.cut(before), add)
       and empty(before.cut(after)))
    faces = cylinders(after, center, Y, bore)
    ck(key+' actual revised cylindrical bearing stock',
       len(faces) == len(spans) and abs(sum(f.Area for f in faces)-
       2*math.pi*bore*sum(hi-lo for lo, hi in spans)) < 1e-5)
    ck(key+' original oversized distal bore removed', not cylinders(after, center, Y, 8.0875))
for side in ['Port', 'Starboard']:
    fork_name = side+'HighSpeedBrakeControlFork'
    pose = App.Placement(App.Matrix(*rows[fork_name]['frame']))
    center, axis = pose.Base, pose.Rotation.multVec(Y)
    for member in ['Left', 'Right']:
        s = placed(side+'HighSpeedBrakeLever'+member)
        ck(side+member+' real receiver bore coaxial with fork',
           len(cylinders(s, center, axis, bore)) == 1)
    pin_world = placed(side+'HighSpeedBrakeControlPin')
    fork_world = placed(fork_name)
    cotter = placed(side+'HighSpeedBrakeControlCotter')
    ck(side+' pin clears fork and unchanged cotter',
       empty(pin_world.common(fork_world)) and empty(pin_world.common(cotter)))
    # Geometric retention controls: a head cannot pass the ear, and the fitted
    # split pin cannot pass axially through the outgoing fork ear.
    stop = pin_world.copy()
    stop.translate(axis*1)
    ck(side+' pin head arrests axial travel', stop.common(fork_world).Volume > 1)
    stop = cotter.copy()
    stop.translate(-axis*4)
    ck(side+' unchanged cotter arrests reverse axial travel', stop.common(fork_world).Volume > 1)
    interfaces.append(dict(id=side+'HighSpeedBrakeControl',
        occurrences=[side+'HighSpeedBrakeLeverLeft', side+'HighSpeedBrakeLeverRight'],
        center_world_mm=list(center), pin_axis_world=list(axis),
        bore_diameter_mm=2*bore, bearing_width_mm=25.4,
        definition_names=['Def_HighBrakeMechanism_lever_left', 'Def_HighBrakeMechanism_lever_right']))
neweyes = read(parent.parent/'operating_interfaces.json')['interfaces']
older = read(H/'transmission_controls_study/fulcrum_integrated01/operating_interfaces.json')
for side in ['Port', 'Starboard']:
    cases = [(side+'LowSpeedBrakeLever', next(v for v in neweyes if v['occurrence'] == side+'LowSpeedBrakeLever')),
             (side+'LowHorizontalLever', next(v for v in older['new_rod_eyes'] if v['id'] == side+'LowBrakeRodEye'))]
    for name, eye in cases:
        center, axis = V(*eye['center_world_mm']), V(*eye['pin_axis_world'])
        shape = placed(name)
        faces = cylinders(shape, center, axis, 6.5)
        ck(name+' actual unchanged13mm eye and12.7mm stock rebound', len(faces) == 1 and
           abs(faces[0].Area-2*math.pi*6.5*12.7) < 1e-5)
        rotation = App.Rotation(Y, axis)
        tool, bad = pin.copy(), oldpin.copy()
        tool.Placement = bad.Placement = App.Placement(center, rotation)
        ck(name+' same complete M568A pin fits the existing receiver', empty(tool.common(shape)))
        conflict = bad.common(shape).Volume
        ck(name+' former15.875mm pin rejected by actual receiver', conflict > 1, common_mm3=conflict)
        tool.translate(rotation.multVec(X)*.3)
        ck(name+' eccentric pin negative rejected', tool.common(shape).Volume > .001)
        interfaces.append(dict(id=side+('LowSpeedBrakeControl' if 'Speed' in name else 'LowBrakeRodEye'),
            occurrences=[name], center_world_mm=list(center), pin_axis_world=list(axis),
            bore_diameter_mm=13., bearing_width_mm=12.7, definition_names=[rows[name]['definition']]))
diag = read(out/'diagnostics/low_fork_one_inch/report.json')
dd = App.openDocument(str(out/'diagnostics/low_fork_one_inch/LowForkDatumDiagnostic.FCStd'))
try:
    s = dd.RejectedLowForkLengthInterpretation.Shape
    threadfaces = cylinders(s, V(), X, 9.625)
    axial = [v.Point.x for f in threadfaces for v in f.Vertexes]
    # The cutter overhang also opens partial patches in the ears for1mm.
    # Bound the whole axial bearing extent, which remains far below19.05mm;
    # do not mistake the total patch extent for a full circular socket.
    ck('Saved one-inch low-fork diagnostic cannot provide required engagement',
       bool(threadfaces) and abs(max(axial)-min(axial)-4.175) < 1e-6
       and max(axial)-min(axial) < diag['chosen_minimum_engagement_mm'],
       full_socket_length_mm=3.175, total_cylindrical_patch_extent_mm=max(axial)-min(axial))
finally:
    App.closeDocument(dd.Name)
write(out/'operating_interfaces.json', dict(native_sha256=sha(native), interfaces=interfaces,
      checker_sha256=sha(Path(__file__)),
      scope='Two revised high-speed receiver diameters and four unchanged low-speed eyes. Pin compatibility is checked; low-speed forks, rods and their poses are not qualified. Track-rod eye coordinates remain unchanged.'))
result = dict(passed=all(v['passed'] for v in checks), checks=checks, native_sha256=sha(native),
              parent_native_sha256=sha(parent), checker_sha256=sha(Path(__file__)),
              historical_geometry_qualified=False, installation_qualified=False)
write(out/'independent_checks.json', result)
print(len(checks), 'saved native checks;', result['passed'], flush=True)
for v in checks:
    if not v['passed']:
        print(v, flush=True)
assert result['passed']
