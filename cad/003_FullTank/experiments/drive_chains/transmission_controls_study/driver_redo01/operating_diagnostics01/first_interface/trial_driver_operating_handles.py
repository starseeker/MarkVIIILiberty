"""Complete operating handles and pivot joints, with four upper-jaw refinements."""
import argparse
import copy
import sys
from pathlib import Path
from control_rebuild_io_v2 import *
from driver_handle_gate_parts import selector
from driver_operating_handle_parts import fulcrum, handle, hardware

V = App.Vector
X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--controls', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
c = read(a.controls)
parent = Saved(ROOT / c['parent'])
assert sha(parent.native) == c['parent_native_sha256']
assert read(parent.folder / 'qualification.json')['local_static_checks_passed']
source = ROOT / c['source_review']
assert sha(source) == c['source_review_sha256']
assert all(sha(ROOT / file) == digest for file, digest in read(source)['source_hashes'].items())
assert read(ROOT / c['gate_study'])['local_interface_checks_passed']
prior = read(ROOT / c['context_prototype'] / 'report.json')
d = copy.deepcopy(parent.report['details'])
shapes, specs, props = {}, {}, {}
for name, spec in prior['specs'].items():
    row = parent.rows[name]
    key = row['definition']
    if key not in shapes:
        shapes[key] = parent.definition(key)
        props[key] = copy.deepcopy(parent.manifest['definitions'][key]['properties'])
    specs[name] = dict(definition=key, frame=row['frame'], owner=row['owners'][-1], role=spec['role'])

gate = dict(jaw_radial_halfspan_mm=c['jaw_radial_halfspan_mm'], jaw_wall_mm=c['jaw_wall_mm'],
            jaw_tangential_halfspan_mm=c['handle_stock_mm'] / 2 + c['jaw_face_clearance_mm'] + c['jaw_wall_mm'])
changed = []
for side in ['Port', 'Starboard']:
    for kind, key in [('High', 'high_selector_controls'), ('Low', 'selector_controls')]:
        name = side + 'Driver' + kind + 'Selector'
        definition = specs[name]['definition']
        shapes[definition] = selector(d[key], gate, side, kind)
        props[definition]['ReconstructionStatus'] = ('Upper radial passage with tangential walls fitted to complete '
            'operating-handle stock; 0.45 mm nominal face clearance. Journal and lower linkage preserved. '
            'Exact profile, standard control state and historical geometry remain estimates.')
        props[definition]['ParameterUpdate'] = 'Regenerate trial_driver_operating_handles.py'
        changed.append(definition)

def add_definition(key, shape, mark, records, status):
    shapes[key] = shape
    props[key] = dict(SourcePartMark=mark, SourceRecords=records, Representation='reconstruction_trial',
                      ReconstructionStatus=status, ParameterUpdate='Regenerate trial_driver_operating_handles.py from operating_controls01.json')


def put(name, key, frame, owner, role):
    specs[name] = dict(definition=key, frame=list(frame.toMatrix().A), owner=owner, role=role)


parts, joint = hardware(c)
for role, mark, records in [('bolt', 'M776', ['SNL:23:027']), ('nut', 'M768', ['SNL:23:028', 'SNL:129:021']),
                             ('cotter', '3/16 x 1-inch split pin', ['SNL:23:029', 'SNL:141:008'])]:
    key = 'Def_DriverOperating' + role.title()
    add_definition(key, parts[role], mark, records,
        'Complete estimated M776 joint; source-sized M768 thread/thickness and specific 1-inch cotter. '
        'Nominal threads, bolt stock/head, nut exterior/slots and pin eye/formed state are estimates. '
        'Generic SNL141 1-1/2-inch cotter conflict retained in source review.')

main = V(*d['foundation']['shafts']['Main']['center_world_mm'])
radial = V(*d['high_selector_controls']['selector_gate_direction'])
normal = radial.cross(Y)
rotation = App.Rotation(radial, Y, normal, 'XYZ')
identity = list(App.Placement().toMatrix().A)
groups = {'DriverOperatingHandles': dict(owner='DriverControlFoundation', frame=identity)}
records = {}
for side, sign, fm, hm, fr, hr in [('Port', 1, 'M747', 'M738B', 'SNL:97:011', 'SNL:117:002'),
                                   ('Starboard', -1, 'M746', 'M738A', 'SNL:97:012', 'SNL:117:016')]:
    stem = side + 'DriverOperating'
    owner = stem + 'Assembly'
    groups[owner] = dict(owner='DriverOperatingHandles', frame=identity)
    origin = main + Y * (sign * c['journal_lane_mm'])
    base = App.Placement(origin, rotation)
    key = 'Def_DriverOperatingFulcrum_' + fm
    add_definition(key, fulcrum(c), fm, [fr, 'HB:93', 'HB:113'],
        'Complete inboard journal, offset arm and lateral-pivot eye. Geometry/stock/stations inferred; '
        'same symmetric local casting envelope for the two catalogued hands.')
    put(stem + 'Fulcrum', key, base, owner, 'fulcrum')
    hand, detail = handle(c, side)
    key = 'Def_DriverOperatingHandle_' + hm
    add_definition(key, hand, hm, [hr, 'HB:148', 'HB:93', 'HB:113'],
        'Complete cranked steel handle and integral grip. Source 37-inch length interpreted as overall radial '
        'extent in its unrotated definition. Heel, stock, bend transitions and selected lateral angle inferred; '
        'trigger, pawl and separate fittings remain unbuilt.')
    tangent = -detail['selector_plane_rise_mm']
    hinge_local = V(c['pivot_radial_mm'], 0, tangent)
    hinge = base.multVec(hinge_local)
    frame = App.Placement(hinge, rotation.multiply(App.Rotation(Z, sign * c['handle_lateral_angle_deg'])))
    put(stem + 'Handle', key, frame, owner, 'handle')
    head_seat = base.multVec(V(c['pivot_radial_mm'], 0, c['fulcrum_ear_tangent_mm'] - c['fulcrum_stock_mm'] / 2))
    bolt_frame = App.Placement(head_seat, rotation)
    put(stem + 'Bolt', 'Def_DriverOperatingBolt', bolt_frame, owner, 'bolt')
    put(stem + 'Nut', 'Def_DriverOperatingNut', App.Placement(head_seat + normal * joint['nut_seat_mm'], rotation), owner, 'nut')
    put(stem + 'Cotter', 'Def_DriverOperatingCotter', App.Placement(head_seat + normal * joint['cotter_axis_mm'], rotation), owner, 'cotter')
    records[side] = dict(fulcrum_origin_world_mm=list(origin), handle_pivot_world_mm=list(hinge),
        radial_world=list(radial), tangent_world=list(normal), bolt_head_seat_world_mm=list(head_seat),
        handle=detail, joint=joint, nominal_selected_selector='Low', physical_occurrences=5)

d['operating_controls'] = c
d['operating_gates'] = gate
d['operating_handles'] = records
d['scope'] = ('Ten additions: two complete handles, two inboard fulcrums and two complete bolt/nut/cotter joints; '
              'four upper jaws revised to actual handle stock. Historical form, trigger fittings and motion remain open.')
inputs = [Path(__file__), a.controls, source, ROOT / c['gate_study'], ROOT / c['context_prototype'] / 'report.json',
          parent.folder / 'report.json', parent.folder / 'isolated/manifest.json']
inputs += sorted({Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m, '__file__', None)
                  and Path(m.__file__).resolve().parent == H and str(m.__file__).endswith('.py')})
trial(a.output, parent, shapes, specs, props, d, inputs, changed_definitions=changed, assembly_groups=groups)
print('Saved full operating handles, fulcrums and pivot joints; validation pending.', flush=True)
