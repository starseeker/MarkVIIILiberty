"""Measure pinion interfaces against the frozen, shared native definitions.

This is an isolated fit study. Intentional failing initial hypotheses are
recorded; no main definitions, stations or receiving plates are changed.
"""
from pathlib import Path
import math
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
STAGE = ROOT.parents[1]
OUT = ROOT / 'interface_build'
sys.path.insert(0, str(STAGE))
from lib.runtime import environment

if '--worker' not in sys.argv:
    sys.exit(subprocess.run([sys.executable, __file__, '--worker'],
                            env=environment(OUT)).returncode)

import FreeCAD as App
import Part
from lib.evidence import read, write, sha, fingerprint
from lib.model import load, point, datum_values
from lib.drive_mount_geometry import values, bearing_points, backing_points
from lib.track_parts import cylinder_y
from lib.visual_review import shaded

lock = fingerprint()
data = load()
a = values(data)
rotor_file = ROOT / 'pin_build/PinionWithPins.FCStd'
assert sha(rotor_file) == read(ROOT / 'pin_build/report.json')['native_sha256']
library_file = STAGE / 'build/native/library/RunningGear.FCStd'
hull_file = STAGE / 'build/native/library/HullStructure.FCStd'
inputs = {str(p.relative_to(STAGE)): sha(p) for p in
          [rotor_file, library_file, hull_file]}
rotor = App.openDocument(str(rotor_file))
library = App.openDocument(str(library_file))
hull = App.openDocument(str(hull_file))
casting = rotor.Def_Casting.Shape.copy()
bearing = library.Def_drive_outer_bearing.Shape.copy()
bush = library.Def_wheel_bush.Shape.copy()
key = library.Def_drive_key.Shape.copy()
assert all(s.isValid() and len(s.Solids) == 1 for s in [casting, bearing, bush, key])

# Both end treatments are hypotheses; the M1407 native shape is immutable.
initial_overlap = casting.common(bearing).Volume
initial_expected = math.pi * (80**2 - 65.2**2) * 2.15
assert abs(initial_overlap - initial_expected) < 1e-4
counterbore_radius = a['barrel_radius'] + .2
counterbore_bottom = a['shoulder'] - .2
casting_end = 495.3 / 2
counterbore_depth = casting_end - counterbore_bottom
tools = [cylinder_y(counterbore_radius, counterbore_depth + 1,
                    y=side*(counterbore_bottom+(counterbore_depth+1)/2))
         for side in [-1, 1]]
counterbored = casting.cut(Part.makeCompound(tools)).removeSplitter()
assert counterbored.isValid() and len(counterbored.Solids) == 1
resolved_overlap = counterbored.common(bearing).Volume
barrel_gap = counterbored.distToShape(bearing)[0]
assert resolved_overlap < 1e-5 and abs(barrel_gap-.2) < 1e-5

# Add real shared bushes to the trial section, leaving a documented small gap
# to the inferred casting bore. This is not a press fit or bearing-seat claim.
bush_end = counterbore_bottom - .3
bush_center = bush_end - data['values']['wheel_bush_length'].value/2
bushes = []
for side in [-1, 1]:
    s = bush.copy()
    s.translate(App.Vector(0, side*bush_center, 0))
    bushes.append(s)
    assert s.common(counterbored).Volume < 1e-5
bush_gap = bushes[0].distToShape(counterbored)[0]
expected_bush_gap = 65.2-data['values']['wheel_bush_od'].value/2
assert abs(bush_gap-expected_bush_gap) < 1e-5

sx, sz = point(data, 'snl_2', [1614, 422])
drive = datum_values('port_drive', data)['translation']
center = App.Vector(sx, drive[1], sz)
receivers = {}
items = []

def item(name, shape, system='RunningGear'):
    obj = doc.addObject('PartDesign::Body', name)
    f = obj.newObject('PartDesign::Feature', 'Measured'+name)
    f.Shape = shape
    items.append(dict(id=name, definition=name, target=obj, shape=shape,
                      system=system, representation='assembly'))
    return obj

doc = App.newDocument('PinionInterfaceStudy')
item('CounterboredCasting', counterbored)
item('CommonOuterBearing', bearing)
item('CommonKey', key)
for n, shape in enumerate(bushes):
    item('CommonBush'+str(n), shape)

for role, target, side in [
    ('inner', 'hull_port_inner_rear_end', -1),
    ('outer', 'hull_port_rear_wing', 1),
]:
    shape = hull.getObject('Def_'+target).Shape.copy()
    shape.translate(-center)
    # Nominal unbored stock containment at the required bolt and barrel holes.
    # Missing material cannot be fixed by simply drilling the proposed holes.
    checks = []
    points = [('bearing', bearing_points(a),
               a['bearing_screw_diameter']+a['fastener_hole_clearance'])]
    if role == 'outer':
        points.append(('backing', backing_points(a),
                       a['backing_rivet_diameter']+a['fastener_hole_clearance']))
    for kind, positions, diameter in points:
        for n, (x, z) in enumerate(positions):
            witness = cylinder_y(diameter/2, a['hull_side_thickness'],
                                 x=x, y=side*(a['shell']+a['hull_side_thickness']/2), z=z)
            fraction = witness.common(shape).Volume/witness.Volume
            checks.append(dict(kind=kind, index=n, x_mm=x, z_mm=z,
                               receiving_stock_fraction=fraction,
                               contained=abs(fraction-1)<1e-6))
    receivers[role] = dict(definition=target, checks=checks,
                           all_contained=all(c['contained'] for c in checks))

doc.recompute()
native = OUT / 'PinionInterfaceStudy.FCStd'
doc.saveAs(str(native))
shaded(items, OUT/'section_context.svg', (1, 1, .4),
       'Pinion interface hypothesis | counterbored casting and unchanged shared parts')
report = dict(
    status='measured_unaccepted_pinion_interfaces', checks_passed=True,
    main_model_changed=False, authored_fingerprint=lock, input_sha256=inputs,
    script_sha256=sha(__file__), native_sha256=sha(native),
    rejected_initial_casting_bearing_overlap_mm3=initial_overlap,
    analytical_overlap_mm3=initial_expected,
    counterbore=dict(radius_mm=counterbore_radius, depth_mm=counterbore_depth,
                     bottom_y_mm=counterbore_bottom, inferred=True,
                     revised_overlap_mm3=resolved_overlap, barrel_gap_mm=barrel_gap),
    bush=dict(end_mm=bush_end, center_mm=bush_center,
              casting_radial_gap_mm=bush_gap, press_fit_qualified=False),
    shaft_end_mm=25.25*25.4/2,
    shaft_recess_inside_common_bearing_mm=a['face']-25.25*25.4/2,
    common_key_end_mm=a['key_end'],
    key_end_to_shaft_end_mm=25.25*25.4/2-a['key_end'],
    global_provisional_axis_mm=list(center), receivers=receivers,
    visual_review_status='pending',
    render_sha256=sha(OUT/'section_context.png'),
    unresolved=['Counterbore is inferred, not historically dimensioned.',
                'Casting-to-bush fit is an inferred clearance, not a seat.',
                'The distinct M1546 inner bearing has not yet been built.',
                'Receiver containment is measured before proposed drilling.',
                'Shaft/keyway/plug details and gear engagement remain unqualified.'])
write(OUT/'report.json', report)
shutil.copy2(__file__, OUT/'executed_probe.py')
assert fingerprint() == lock
for path, digest in inputs.items():
    assert sha(STAGE/path) == digest
for name in list(App.listDocuments()):
    App.closeDocument(name)
print('PASS measured initial interference, counterbore hypothesis, bush gap and receiver stock')
