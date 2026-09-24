"""Build four M569C/M568C track-rod end joints from saved lever-eye interfaces."""
import argparse
import math
from pathlib import Path
import shutil
import sys
import uuid

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path.insert(0, str(H.parents[1]))
import FreeCAD as App
import Part
from lib.evidence import read, write, sha
from lib.cad_build import metadata
from lib.camera_review import validate_native_bindings
from transmission_control_joint_parts import parts

V = App.Vector
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--controls', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
out = a.output.resolve()
assert not out.exists()
cfg = read(a.controls)
c = cfg['controls']
C = H/'transmission_controls_study'
parent = C/cfg['parent']
pr, m = read(parent/'report.json'), read(parent/'isolated/manifest.json')
native = parent/pr['native_file']
assert sha(native) == pr['native_sha256'] == m['native_sha256']
assert read(parent/'qualification.json')['local_static_checks_passed']
for key in ['source_packet', 'source_review', 'interface_source']:
    assert sha(ROOT/cfg[key]) == cfg[key+'_sha256']
packet = read(ROOT/cfg['source_packet'])
assert all(sha(ROOT/f) == digest for f, digest in packet['source_hashes'].items())
interfaces = read(ROOT/cfg['interface_source'])
prior_native = (ROOT/cfg['interface_source']).parent/'PowertrainWithRearControlFulcrums.FCStd'
assert sha(prior_native) == interfaces['native_sha256']
rows = {v['name']: v for v in m['occurrences']}
cache = {}


def definition(name):
    d = m['definitions'][name]
    if name not in cache:
        assert sha(d['brep_path']) == d['brep_sha256']
        s = Part.Shape()
        s.read(d['brep_path'])
        assert s.Placement.isIdentity()
        cache[name] = s
    return cache[name].copy()


joints = {}
for side in ['Starboard', 'Port']:
    for end, pool, eye_id in [('Brake', 'verified_rear_brake_eyes', side+'TrackBrakeControl'),
                               ('Fulcrum', 'new_rod_eyes', side+'TrackBrakeRodEye')]:
        old = next(v for v in interfaces[pool] if v['id'] == eye_id)
        row = rows[old['occurrence']]
        shape = definition(row['definition'])
        shape.Placement = App.Placement(App.Matrix(*row['frame']))
        center, axis = V(*old['center_world_mm']), V(*old['pin_axis_world'])
        faces = [f for f in shape.Faces if isinstance(f.Surface, Part.Cylinder) and
                 abs(f.Surface.Radius-6.5) < 1e-7 and f.Surface.Axis.cross(axis).Length < 1e-7 and
                 (f.Surface.Center-center).cross(axis).Length < 1e-6]
        assert len(faces) == 1
        f = faces[0]
        projections = [(v.Point-center).dot(axis) for v in f.Vertexes]
        assert abs(max(projections)-min(projections)-12.7) < 1e-6
        assert abs(max(projections)+min(projections)) < 1e-6
        x = V(1 if end == 'Brake' else -1, 0, 0)
        y = V(0, 1 if side == 'Port' else -1, 0) if end == 'Brake' else V(0, 0, 1)
        pose = App.Placement(center, App.Rotation(x, y, x.cross(y), 'XYZ'))
        name = side+'Track'+end+'Joint'
        joints[name] = dict(frame=list(pose.toMatrix().A), receiver=old['occurrence'],
                            interface_id=eye_id, center_world_mm=list(center),
                            pin_axis_world=list(y), rod_axis_world=list(x),
                            bore_diameter_mm=2*f.Surface.Radius, bearing_width_mm=12.7,
                            receiver_definition=row['definition'],
                            receiver_definition_sha256=m['definitions'][row['definition']]['brep_sha256'])
selected = [v['receiver'] for v in joints.values()]
selected.append('RearChannelLeftCleat1Nut')
validate_native_bindings(dict(native_file=str(native), render_occurrences=selected, landmarks=[]), m)
shapes, details = parts(c, definition(c['shared_nut_definition']))
out.mkdir(parents=True)
doc = App.newDocument('RearTrackRodJoints')
root = doc.addObject('App::Part', 'Root')
library = doc.addObject('App::Part', 'Definitions')
marks = dict(fork='M569C', pin='M568C', cotter='1/8 x 1 inch split pin',
             nut='3/4 inch U.S. Standard plain nut')
records = dict(fork=['SNL:86:022'], pin=['SNL:136:003'], cotter=['SNL:136:004'],
               nut=['SNL:194:025'])
sources = {v['record_id']: v for v in packet['source_records']}
made, specs = {}, {}
for role, shape in shapes.items():
    body = doc.addObject('PartDesign::Body', 'Def_TrackJoint_'+role)
    library.addObject(body)
    body.newObject('PartDesign::Feature', 'ReconstructedTrackJoint').Shape = shape
    metadata(body, SourcePartMark=marks[role], SourceRecords=records[role],
             SurveyIds=sorted({pid for rid in records[role] for pid in sources[rid]['part_ids']}),
             Representation='unqualified_track_joint_trial',
             ReconstructionStatus='Estimated fork profile, pin diameter and static rod-axis pose; full rod and spring pending.',
             ParameterUpdate='Regenerate '+a.controls.name+' with trial_rear_track_joints.py')
    made[role] = body
    shape.exportBrep(str(out/(role+'.brep')))
for name, joint in joints.items():
    group = doc.addObject('App::Part', name)
    root.addObject(group)
    group.Placement = App.Placement(App.Matrix(*joint['frame']))
    for role in shapes:
        key = name+role.title()
        local = App.Placement(App.Matrix(*details['local_frames'][role]))
        link = doc.addObject('App::Link', key)
        group.addObject(link)
        link.setLink(made[role])
        link.LinkPlacement = local
        metadata(link, SourceRecords=records[role], Coverage='reconstruction_trial')
        specs[key] = dict(role=role, owner=name, local_frame=list(local.toMatrix().A),
                          frame=list(group.Placement.multiply(local).toMatrix().A))
for obj in [v for v in doc.Objects if v.TypeId == 'App::Part']:
    obj.Uid = str(uuid.uuid5(uuid.NAMESPACE_URL, 'markviii:track-joint:'+obj.Name))
library.Visibility = False
doc.recompute()
saved = out/'RearTrackRodJoints.FCStd'
doc.saveAs(str(saved))
App.closeDocument(doc.Name)
inputs = [Path(__file__), H/'transmission_control_joint_parts.py',
          H/'transmission_input_installation_parts.py', H.parents[1]/'lib/cad_build.py',
          a.controls.resolve(), *[ROOT/cfg[k] for k in ['source_packet', 'source_review', 'interface_source']],
          parent/'report.json', parent/'isolated/manifest.json', parent/'qualification.json']
for file in inputs:
    path = out/'inputs'/file.relative_to(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(file, path)
write(out/'report.json', dict(native_file=saved.name, native_sha256=sha(saved),
      parent_native=str(native.relative_to(ROOT)), parent_native_sha256=sha(native),
      parent_manifest_sha256=sha(parent/'isolated/manifest.json'),
      input_hashes={str(f.relative_to(ROOT)): sha(f) for f in inputs},
      controls=c, details=details, joints=joints, specs=specs, record_ids=records,
      shared_definitions={'nut': c['shared_nut_definition']},
      prototype_physical_occurrences=16, prototype_definition_count=4,
      geometry_integrated=False, complete_rods_or_springs_qualified=False,
      historical_geometry_qualified=False, installation_qualified=False))
print('Saved16 track-joint components in four groups; current receiver eyes remeasured.', flush=True)
