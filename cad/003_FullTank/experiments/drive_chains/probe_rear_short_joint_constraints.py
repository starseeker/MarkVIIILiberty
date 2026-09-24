"""Measure fork-throat collisions and the shared M568A pin/receiver conflict."""
import json
from pathlib import Path
import sys

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path.insert(0, str(H.parents[1]))
import FreeCAD as App
import Part
from lib.evidence import read, write, sha
from lib.camera_review import validate_native_bindings

C = H/'transmission_controls_study'
out = C/'short_joint_sources01'
assert not (out/'constraint_probe.json').exists()
parent = C/'support_integrated01'
r, m = read(parent/'report.json'), read(parent/'isolated/manifest.json')
native = parent/r['native_file']
assert sha(native) == r['native_sha256'] == m['native_sha256']
rows = {v['name']: v for v in m['occurrences']}
cache = {}


def shape(row, manifest):
    d = manifest['definitions'][row['definition']]
    key = d['brep_sha256']
    if key not in cache:
        assert sha(d['brep_path']) == key
        s = Part.Shape()
        s.read(d['brep_path'])
        cache[key] = s
    s = cache[key].copy()
    s.Placement = App.Placement(App.Matrix(*row['frame']))
    return s


prior = read(C/'fulcrum_integrated01/operating_interfaces.json')
receivers, selected = [], []
for eye in prior['new_rod_eyes']+prior['verified_rear_brake_eyes']:
    if 'Low' not in eye['id'] or eye.get('end', 'brake') != 'brake':
        continue
    center, axis = App.Vector(*eye['center_world_mm']), App.Vector(*eye['pin_axis_world'])
    s = shape(rows[eye['occurrence']], m)
    faces = [f for f in s.Faces if isinstance(f.Surface, Part.Cylinder) and
             f.Surface.Axis.cross(axis).Length < 1e-7 and
             (f.Surface.Center-center).cross(axis).Length < 1e-6 and abs(f.Surface.Radius-6.5) < 1e-7]
    assert len(faces) == 1
    receivers.append(dict(occurrence=eye['occurrence'], eye=eye['id'],
                          bore_diameter_mm=2*faces[0].Surface.Radius))
    selected.append(eye['occurrence'])
pin_row = next(v for v in rows.values() if v['definition'] == 'Def_ControlJoint_pin')
pin = shape(pin_row, m)
pin.Placement = App.Placement()
faces = [f for f in pin.Faces if isinstance(f.Surface, Part.Cylinder) and
         f.Surface.Axis.cross(App.Vector(0, 1, 0)).Length < 1e-7 and
         abs(f.Surface.Radius-7.9375) < 1e-7]
assert faces and json.loads(m['definitions'][pin_row['definition']]['properties']['SourceRecords']) == ['SNL:136:007']
pin_diameter = 2*faces[0].Surface.Radius
selected.append(pin_row['name'])
validate_native_bindings(dict(native_file=str(native), render_occurrences=selected, landmarks=[]), m)
trial = C/'track_joints01'
tr, tm = read(trial/'report.json'), read(trial/'isolated/manifest.json')
tnative = trial/tr['native_file']
assert sha(tnative) == tr['native_sha256'] == tm['native_sha256']
trows = {v['name']: v for v in tm['occurrences']}
collisions = []
for name, joint in tr['joints'].items():
    fork = shape(trows[name+'Fork'], tm)
    receiver = shape(rows[joint['receiver']], m)
    common = fork.common(receiver)
    common.Placement = App.Placement(App.Matrix(*joint['frame'])).inverse().multiply(common.Placement)
    b = common.BoundBox
    collisions.append(dict(joint=name, receiver=joint['receiver'], common_mm3=common.Volume,
                           common_bounds_joint_mm=[b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax]))
validate_native_bindings(dict(native_file=str(tnative), render_occurrences=list(trows), landmarks=[]), tm)
write(out/'constraint_probe.json', dict(native_sha256=sha(native), trial_native_sha256=sha(tnative),
      probe_sha256=sha(Path(__file__)), manifest_sha256=sha(parent/'isolated/manifest.json'),
      m568a_definition=pin_row['definition'], m568a_shank_diameter_mm=pin_diameter,
      low_speed_receivers=receivers, diametral_conflict_mm=pin_diameter-13.0,
      initial_track_fork_intersections=collisions,
      interpretation='Track fork throat intersects existing receiver ends. Shared M568A pin exceeds low-speed bores; same-mark diameter variants are not source-supported. Receiver/pin-family estimates require reconciliation.',
      geometry_modified=False, historical_geometry_qualified=False))
print('Measured M568A', pin_diameter, 'against four13mm low-speed bores; retained four fork collision regions.', flush=True)
