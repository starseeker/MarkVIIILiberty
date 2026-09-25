"""Close two straight SH946D rods by explicitly revising provisional receiver geometry."""
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
from rear_track_rod_parts import lever
from rear_control_fulcrum_parts import lever as horizontal_lever

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
for key in ['source_packet', 'source_review']:
    assert sha(ROOT/cfg[key]) == cfg[key+'_sha256']
packet = read(ROOT/cfg['source_packet'])
assert all(sha(ROOT/f) == digest for f, digest in packet['source_hashes'].items())
rows = {v['name']: v for v in m['occurrences']}
shapes, specs, group_frames, details = {}, {}, {}, {}


def pose(values):
    return App.Placement(App.Matrix(*values))


def definition(key):
    if key not in shapes:
        d = m['definitions'][key]
        assert sha(d['brep_path']) == d['brep_sha256']
        shape = Part.Shape()
        shape.read(d['brep_path'])
        assert shape.Placement.isIdentity()
        shapes[key] = shape
    return shapes[key].copy()


def eye(shape, center, axis, radius=6.5):
    faces = [f for f in shape.Faces if isinstance(f.Surface, Part.Cylinder) and
             abs(f.Surface.Radius-radius) < 1e-7 and f.Surface.Axis.cross(axis).Length < 1e-7
             and (f.Surface.Center-center).cross(axis).Length < 1e-6]
    assert len(faces) == 1
    values = [(v.Point-center).dot(axis) for v in faces[0].Vertexes]
    assert abs(max(values)+min(values)) < 1e-6
    assert abs(max(values)-min(values)-12.7) < 1e-6
    return dict(center_mm=list(center), axis=list(axis), diameter_mm=2*faces[0].Surface.Radius,
                width_mm=max(values)-min(values))


front_controls = H/'transmission_brake_front_study/controls.json'
oldc = read(front_controls)['controls']
oldlever = definition(c['lever_definition'])
regenerated = lever(oldc)
assert not oldlever.cut(regenerated).Faces and not regenerated.cut(oldlever).Faces
target_levels = []
for side in ['Starboard', 'Port']:
    row = rows[side+'TrackHorizontalLever']
    s = definition(row['definition'])
    eye(s, V(*c['track_arm_local_mm']), V(0, 0, 1))
    target_levels.append(pose(row['frame']).multVec(V(*c['track_arm_local_mm'])).z)
assert abs(target_levels[0]-target_levels[1]) < 1e-7
target_z = target_levels[0]
local_heights = [target_z-pose(rows[side+kind+'BrakeLever']['frame']).Base.z
                 for side in ['Starboard', 'Port'] for kind in ['Track', 'LowSpeed']]
assert max(local_heights)-min(local_heights) < 1e-7
newc = dict(oldc, lever_end_z=local_heights[0])
shapes[c['lever_definition']] = lever(newc)
eye(shapes[c['lever_definition']], V(newc['lever_end_x'], 0, newc['lever_end_z']), V(0, 1, 0))
fulcrum_controls = C/'fulcrum_controls02.json'
fc = read(fulcrum_controls)['controls']
track_key = rows['PortTrackHorizontalLever']['definition']
original_track = definition(track_key)
regenerated_track = horizontal_lever(fc['lever'], fc['lever_profiles']['track'])
assert not original_track.cut(regenerated_track).Faces and not regenerated_track.cut(original_track).Faces
arm_lengths = []
for side in ['Starboard', 'Port']:
    rear_y = pose(rows[side+'TrackBrakeLever']['frame']).Base.y
    pivot_y = pose(rows[side+'TrackHorizontalLever']['frame']).Base.y
    arm_lengths.append(abs(rear_y-pivot_y)/math.cos(math.radians(c['track_clock_deg'])))
assert max(arm_lengths)-min(arm_lengths) < 1e-7
profile = dict(fc['lever_profiles']['track'], brake=[0, -arm_lengths[0]])
shapes[track_key] = horizontal_lever(fc['lever'], profile)
details['track_lever_controls'] = fc['lever']
details['old_track_profile'] = fc['lever_profiles']['track']
details['new_track_profile'] = profile
details['new_track_arm_local_mm'] = [0, -arm_lengths[0], c['track_arm_local_mm'][2]]
for side in ['Starboard', 'Port']:
    for kind in ['Track', 'LowSpeed']:
        name = side+kind+'BrakeLever'
        specs[name] = dict(definition=c['lever_definition'], role='brake_lever',
                           owner='Receivers', frame=rows[name]['frame'])
    rear = pose(rows[side+'TrackBrakeLever']['frame']).multVec(
        V(newc['lever_end_x'], 0, newc['lever_end_z']))
    name = side+'TrackHorizontalLever'
    row = rows[name]
    before = pose(row['frame'])
    radius = arm_lengths[0]
    delta_y = rear.y-before.Base.y
    assert abs(delta_y) < radius
    angle = math.degrees(math.acos(-delta_y/radius))
    after = App.Placement(before.Base, App.Rotation(V(0, 0, 1), angle))
    front = after.multVec(V(*details['new_track_arm_local_mm']))
    assert abs(front.y-rear.y) < 1e-7 and abs(front.z-rear.z) < 1e-7
    specs[name] = dict(definition=row['definition'], role='horizontal_lever',
                       owner='Receivers', frame=list(after.toMatrix().A))
    definition(row['definition'])
    seats = {}
    for end, center in [('Brake', rear), ('Fulcrum', front)]:
        joint = side+'Track'+end+'Joint'
        old = pose(m['assemblies'][joint]['world'])
        new = App.Placement(center, old.Rotation)
        group_frames[joint] = list(new.toMatrix().A)
        seats[end] = list(new.multVec(V(c['socket_face_x_mm'], 0, 0)))
        for role in ['Fork', 'Pin', 'Cotter', 'Nut']:
            name = joint+role
            row = rows[name]
            definition(row['definition'])
            frame = new.multiply(old.inverse()).multiply(pose(row['frame']))
            specs[name] = dict(definition=row['definition'], role=role.lower(), owner=joint,
                               frame=list(frame.toMatrix().A))
    start = rear+V(c['socket_face_x_mm']-c['insertion_mm'], 0, 0)
    finish = front-V(c['socket_face_x_mm']-c['insertion_mm'], 0, 0)
    length = finish.x-start.x
    assert length > 2*c['thread_length_mm']
    if 'Def_RearTrackRod' in shapes:
        assert abs(length-details['rod_length_mm']) < 1e-7
    else:
        shapes['Def_RearTrackRod'] = Part.makeCylinder(c['rod_diameter_mm']/2, length, V(), V(1, 0, 0))
        details['rod_length_mm'] = length
    specs[side+'TrackConnectingRod'] = dict(definition='Def_RearTrackRod', role='rod',
        owner=side+'TrackShortConnection', frame=list(App.Placement(start, App.Rotation()).toMatrix().A))
    details[side] = dict(old_brake_eye=eye(oldlever, V(*c['lever_old_end_local_mm']), V(0, 1, 0)),
                         brake_eye_world_mm=list(rear), fulcrum_eye_world_mm=list(front),
                         pivot_world_mm=list(before.Base), lever_clock_deg=angle,
                         previous_lever_frame=rows[side+'TrackHorizontalLever']['frame'],
                         new_lever_frame=list(after.toMatrix().A), socket_seats_world_mm=seats,
                         rod_start_world_mm=list(start), rod_finish_world_mm=list(finish))
details.update(old_lever_controls=oldc, new_lever_controls=newc, eye_height_change_mm=newc['lever_end_z']-oldc['lever_end_z'],
               original_receiver_reproduced=True, thread_representation='Nominal cylindrical envelopes; no physical thread helix.')
assert len(shapes) == 7 and len(specs) == 24
validate_native_bindings(dict(native_file=str(native), render_occurrences=[n for n in specs if n in rows], landmarks=[]), m)
out.mkdir(parents=True)
doc = App.newDocument('RearTrackConnectingRods')
root = doc.addObject('App::Part', 'Root')
library = doc.addObject('App::Part', 'Definitions')
made = {}
for key, shape in shapes.items():
    assert shape.isValid() and len(shape.Solids) == 1
    body = doc.addObject('PartDesign::Body', key)
    library.addObject(body)
    body.newObject('PartDesign::Feature', 'ReconstructedTrackConnection').Shape = shape
    props = m['definitions'][key]['properties'] if key in m['definitions'] else dict(
        SourcePartMark='SH946D', SourceRecords=['SNL:194:024'], DefinitionKey='rear_track_connecting_rod')
    metadata(body, **props, Representation='reconstruction_trial',
             ReconstructionStatus='Straight-rod closure study; M330 lower arm and M4132 clocks estimated. No full motion or service qualification.')
    made[key] = body
    shape.exportBrep(str(out/(key+'.brep')))
groups = {}
for name in ['Receivers', 'StarboardTrackShortConnection', 'PortTrackShortConnection']:
    obj = doc.addObject('App::Part', name)
    root.addObject(obj)
    groups[name] = obj
for name, frame in group_frames.items():
    obj = doc.addObject('App::Part', name)
    groups[('Starboard' if name.startswith('Starboard') else 'Port')+'TrackShortConnection'].addObject(obj)
    obj.Placement = pose(frame)
    groups[name] = obj
for name, spec in specs.items():
    owner = groups[spec['owner']]
    link = doc.addObject('App::Link', name)
    owner.addObject(link)
    link.setLink(made[spec['definition']])
    link.LinkPlacement = owner.getGlobalPlacement().inverse().multiply(pose(spec['frame']))
    metadata(link, Coverage='reconstruction_trial', SourceRecords=['SNL:194:024'] if spec['role'] == 'rod'
             else m['definitions'][spec['definition']]['properties'].get('SourceRecords', '[]'))
for obj in [v for v in doc.Objects if v.TypeId == 'App::Part']:
    obj.Uid = str(uuid.uuid5(uuid.NAMESPACE_URL, 'markviii:track-rod:'+obj.Name))
library.Visibility = False
doc.recompute()
saved = out/'RearTrackConnectingRods.FCStd'
doc.saveAs(str(saved))
App.closeDocument(doc.Name)
inputs = [Path(__file__), H/'rear_track_rod_parts.py', H/'transmission_brake_front_parts.py',
          H/'transmission_brake_anchor_parts.py', H/'rear_control_fulcrum_parts.py', H/'rear_control_channel_mount_parts.py', H.parents[1]/'lib/cad_build.py', front_controls, fulcrum_controls,
          a.controls.resolve(), ROOT/cfg['source_packet'], ROOT/cfg['source_review'],
          parent/'report.json', parent/'isolated/manifest.json', parent/'qualification.json']
for file in inputs:
    path = out/'inputs'/file.relative_to(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(file, path)
write(out/'report.json', dict(native_file=saved.name, native_sha256=sha(saved),
      parent_native=str(native.relative_to(ROOT)), parent_native_sha256=sha(native),
      input_hashes={str(f.relative_to(ROOT)): sha(f) for f in inputs}, controls=c,
      details=details, specs=specs, joint_frames=group_frames,
      new_occurrences=[side+'TrackConnectingRod' for side in ['Starboard', 'Port']],
      changed_definitions=[c['lever_definition'], track_key], changed_occurrences=sorted(set(specs)-{side+'TrackConnectingRod' for side in ['Starboard', 'Port']}),
      prototype_physical_occurrences=24, prototype_definition_count=7,
      geometry_integrated=False, historical_geometry_qualified=False, installation_qualified=False))
print('Saved24 trial components; shared straight rod length', details['rod_length_mm'], 'mm; M330 eye raised', details['eye_height_change_mm'], 'mm.', flush=True)
