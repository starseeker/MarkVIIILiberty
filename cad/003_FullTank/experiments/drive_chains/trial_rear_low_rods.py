"""Close two straight SH946E low-speed rods by explicitly reconciling fulcrum lever brake arms."""
import argparse
import math
from pathlib import Path
import shutil
import sys
import uuid

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path.insert(0, str(H.parents[1]))
sys.path.insert(0, str(H))
import FreeCAD as App
import Part
from lib.evidence import read, write, sha
from lib.cad_build import metadata
from lib.camera_review import validate_native_bindings
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


# Load fulcrum controls for lever reconstruction
fulcrum_controls_file = C/'fulcrum_controls02.json'
fc = read(fulcrum_controls_file)['controls']

# Inherit existing front brake lever (unchanged)
front_brake_lever_def = 'Def_BrakeFront_lever'
definition(front_brake_lever_def)

# Symmetrical reconciliation of M4134 and M4133 brake arm profiles
x_b = c['lever_brake_arm_x_mm']
sb_profile = dict(fc['lever_profiles']['low_right'], brake=[x_b, -85.3957142857142])
pt_profile = dict(fc['lever_profiles']['low_left'], brake=[x_b, 85.3957142857142])

shapes[c['lever_definition_starboard']] = horizontal_lever(fc['lever'], sb_profile)
shapes[c['lever_definition_port']] = horizontal_lever(fc['lever'], pt_profile)

details['old_sb_profile'] = fc['lever_profiles']['low_right']
details['new_sb_profile'] = sb_profile
details['old_pt_profile'] = fc['lever_profiles']['low_left']
details['new_pt_profile'] = pt_profile
details['lever_controls'] = fc['lever']

rot_rear = App.Rotation(V(-1, 0, 0), V(0, 0, 1), V(0, 1, 0), 'XYZ')

for side, sign, def_key in [('Starboard', -1, c['lever_definition_starboard']),
                            ('Port', 1, c['lever_definition_port'])]:
    # Brake lever receiver
    name_brake_lever = side+'LowSpeedBrakeLever'
    specs[name_brake_lever] = dict(definition=front_brake_lever_def, role='brake_lever',
                                   owner='Receivers', frame=rows[name_brake_lever]['frame'])

    # Horizontal fulcrum lever receiver (identity rotation, placed at pivot)
    name_lever = side+'LowHorizontalLever'
    specs[name_lever] = dict(definition=def_key, role='horizontal_lever',
                             owner='Receivers', frame=rows[name_lever]['frame'])

    # Front brake eye from joint or brake lever
    front_center = V(2150.1758808503428, sign * 535.3957142857142, 625.125)
    rear_center = V(2298.4 + x_b, sign * 535.3957142857142, 625.125)

    assert abs(front_center.y - rear_center.y) < 1e-7
    assert abs(front_center.z - rear_center.z) < 1e-7

    # Front joint (unchanged position, group frame preserved)
    brake_joint = side+'LowBrakeJoint'
    old_brake_pose = pose(m['assemblies'][brake_joint]['world'])
    group_frames[brake_joint] = list(old_brake_pose.toMatrix().A)
    for role in ['Fork', 'Pin', 'Cotter', 'Nut']:
        rname = brake_joint+role
        definition(rows[rname]['definition'])
        specs[rname] = dict(definition=rows[rname]['definition'], role=role.lower(),
                            owner=brake_joint, frame=rows[rname]['frame'])

    # Rear fulcrum joint (re-posed to coaxial rear eye center)
    fulcrum_joint = side+'LowFulcrumJoint'
    old_fulcrum_pose = pose(m['assemblies'][fulcrum_joint]['world'])
    new_fulcrum_pose = App.Placement(rear_center, rot_rear)
    group_frames[fulcrum_joint] = list(new_fulcrum_pose.toMatrix().A)

    for role in ['Fork', 'Pin', 'Cotter', 'Nut']:
        rname = fulcrum_joint+role
        definition(rows[rname]['definition'])
        # compute new world frame from new joint pose and local joint transform
        local_frame = old_fulcrum_pose.inverse().multiply(pose(rows[rname]['frame']))
        new_frame = new_fulcrum_pose.multiply(local_frame)
        specs[rname] = dict(definition=rows[rname]['definition'], role=role.lower(),
                            owner=fulcrum_joint, frame=list(new_frame.toMatrix().A))

    # Socket seats
    front_seat = front_center + V(c['socket_face_x_mm'], 0, 0)
    rear_seat = rear_center - V(c['socket_face_x_mm'], 0, 0)
    span = rear_seat.x - front_seat.x
    assert span > 0

    start = front_seat - V(c['insertion_mm'], 0, 0)
    finish = rear_seat + V(c['insertion_mm'], 0, 0)
    length = finish.x - start.x
    assert length > 2 * c['minimum_insertion_mm']

    if 'Def_RearLowRod' in shapes:
        assert abs(length - details['rod_length_mm']) < 1e-7
    else:
        shapes['Def_RearLowRod'] = Part.makeCylinder(c['rod_diameter_mm']/2, length, V(), V(1, 0, 0))
        details['rod_length_mm'] = length

    specs[side+'LowConnectingRod'] = dict(
        definition='Def_RearLowRod', role='rod',
        owner=side+'LowShortConnection',
        frame=list(App.Placement(start, App.Rotation()).toMatrix().A)
    )

    details[side] = dict(
        front_eye_world_mm=list(front_center),
        rear_eye_world_mm=list(rear_center),
        socket_seats_world_mm=dict(Brake=list(front_seat), Fulcrum=list(rear_seat)),
        rod_start_world_mm=list(start),
        rod_finish_world_mm=list(finish),
        span_between_socket_faces_mm=span,
        thread_engagement_mm=c['insertion_mm']
    )

details.update(
    controls=c,
    insertion_mm=c['insertion_mm'],
    minimum_insertion_mm=c['minimum_insertion_mm'],
    thread_representation='Nominal cylindrical envelopes; no physical thread helix.'
)

# Validate native bindings for rendering occurrences
validate_native_bindings(dict(
    native_file=str(native),
    render_occurrences=[n for n in specs if n in rows],
    landmarks=[]
), m)

out.mkdir(parents=True)
doc = App.newDocument('RearLowConnectingRods')
root = doc.addObject('App::Part', 'Root')
library = doc.addObject('App::Part', 'Definitions')
made = {}

marks = {
    c['lever_definition_starboard']: 'M4134',
    c['lever_definition_port']: 'M4133',
    'Def_BrakeFront_lever': 'M330',
    'Def_LowJoint_fork': 'M569A',
    'Def_ControlJoint_pin': 'M568A',
    'Def_ControlJoint_cotter': '1/8 x 1 inch split pin',
    'Def_USStdControlNut': '3/4 inch U.S. Standard plain nut',
    'Def_RearLowRod': 'SH946E'
}
records = {
    c['lever_definition_starboard']: ['SNL:73:003'],
    c['lever_definition_port']: ['SNL:73:002'],
    'Def_BrakeFront_lever': ['SNL:118:024'],
    'Def_LowJoint_fork': ['SNL:87:002'],
    'Def_ControlJoint_pin': ['SNL:136:007'],
    'Def_ControlJoint_cotter': ['SNL:136:008'],
    'Def_USStdControlNut': ['SNL:194:025'],
    'Def_RearLowRod': ['SNL:195:019']
}
survey_ids = {
    'Def_RearLowRod': ['P_03d872e5ff732c91']
}

for key, shape in shapes.items():
    assert shape.isValid() and len(shape.Solids) == 1
    body = doc.addObject('PartDesign::Body', key)
    library.addObject(body)
    body.newObject('PartDesign::Feature', 'ReconstructedLowRodConnection').Shape = shape
    props = m['definitions'][key]['properties'] if key in m['definitions'] else dict(
        SourcePartMark=marks[key],
        SourceRecords=records[key],
        SurveyIds=survey_ids.get(key, []),
        DefinitionKey='rear_low_connecting_rod'
    )
    metadata(body, **props, Representation='reconstruction_trial',
             ReconstructionStatus='Straight-rod closure study; M4133/M4134 lever brake arms reconciled. No full motion or service qualification.',
             ParameterUpdate='Regenerate '+a.controls.name+' with trial_rear_low_rods.py')
    made[key] = body
    shape.exportBrep(str(out/(key+'.brep')))

groups = {}
for name in ['Receivers', 'StarboardLowShortConnection', 'PortLowShortConnection']:
    obj = doc.addObject('App::Part', name)
    root.addObject(obj)
    groups[name] = obj

for name, frame in group_frames.items():
    obj = doc.addObject('App::Part', name)
    side = 'Starboard' if name.startswith('Starboard') else 'Port'
    groups[side+'LowShortConnection'].addObject(obj)
    obj.Placement = pose(frame)
    groups[name] = obj

for name, spec in specs.items():
    owner = groups[spec['owner']]
    link = doc.addObject('App::Link', name)
    owner.addObject(link)
    link.setLink(made[spec['definition']])
    link.LinkPlacement = owner.getGlobalPlacement().inverse().multiply(pose(spec['frame']))
    metadata(link, Coverage='reconstruction_trial',
             SourceRecords=records.get(spec['definition'], ['SNL:195:019']))

for obj in [v for v in doc.Objects if v.TypeId == 'App::Part']:
    obj.Uid = str(uuid.uuid5(uuid.NAMESPACE_URL, 'markviii:low-rod:'+obj.Name))

library.Visibility = False
doc.recompute()
saved = out/'RearLowConnectingRods.FCStd'
doc.saveAs(str(saved))
App.closeDocument(doc.Name)

inputs = [
    Path(__file__),
    H/'rear_control_fulcrum_parts.py',
    H/'rear_control_channel_mount_parts.py',
    H/'transmission_input_installation_parts.py',
    H.parents[1]/'lib/cad_build.py',
    fulcrum_controls_file,
    a.controls.resolve(),
    ROOT/cfg['source_packet'],
    ROOT/cfg['source_review'],
    parent/'report.json',
    parent/'isolated/manifest.json',
    parent/'qualification.json'
]

for file in inputs:
    path = out/'inputs'/file.relative_to(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(file, path)

write(out/'report.json', dict(
    native_file=saved.name,
    native_sha256=sha(saved),
    parent_native=str(native.relative_to(ROOT)),
    parent_native_sha256=sha(native),
    parent_manifest_sha256=sha(parent/'isolated/manifest.json'),
    input_hashes={str(f.relative_to(ROOT)): sha(f) for f in inputs},
    controls=c,
    details=details,
    specs=specs,
    joint_frames=group_frames,
    new_occurrences=['StarboardLowConnectingRod', 'PortLowConnectingRod'],
    changed_definitions=[c['lever_definition_starboard'], c['lever_definition_port']],
    changed_occurrences=sorted(set(specs) - {'StarboardLowConnectingRod', 'PortLowConnectingRod'}),
    prototype_physical_occurrences=len(specs),
    prototype_definition_count=len(shapes),
    geometry_integrated=False,
    historical_geometry_qualified=False,
    installation_qualified=False
))

print(f"Saved {len(specs)} trial components; shared straight rod length {details['rod_length_mm']:.4f} mm to {saved.name}", flush=True)
