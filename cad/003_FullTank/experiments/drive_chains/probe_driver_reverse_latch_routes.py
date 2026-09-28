"""Probe source-informed latch corridors against saved material before making parts.

The cylinders and notch tooth are nonphysical witnesses, excluded from the BOM.
No failed profile, printed stock, source camera or receiving solid is changed.
"""
import argparse
import itertools
import math
import numpy as np
from control_rebuild_io_v2 import App, Part, H, ROOT, Saved, pose, read, write, sha

V = App.Vector
Y = V(0, 1, 0)
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--controls', type=__import__('pathlib').Path, required=True)
parser.add_argument('--output', type=__import__('pathlib').Path, required=True)
args = parser.parse_args()
controls = read(args.controls)
seed = Saved(ROOT / controls['seed'])
assert sha(seed.native) == controls['native_sha256']
source = ROOT / controls['source_review']
assert sha(source) == controls['source_review_sha256']
for rel, digest in read(source)['source_hashes'].items():
    assert sha(ROOT / rel) == digest
parent = Saved((ROOT / seed.report['parent_native']).parent)
out = args.output.resolve()
out.mkdir(exist_ok=False)
standard_path = H / 'transmission_brake_front_study/trial01/standard_context_manifest.json'
standard = read(standard_path)
assert all(sha(ROOT / rel) == digest for rel, digest in standard['native_files'].items())

# Identical replacement-by-occurrence policy to the checked quadrant context.
records = {name: (row, seed.manifest) for name, row in seed.rows.items()}
for name, row in parent.rows.items():
    if name not in records:
        records[name] = row, parent.manifest
excluded = set(records) | {'PortPinion_Rotor_Casting', 'StarboardPinion_Rotor_Casting'}
for row in standard['occurrences']:
    if row['name'] not in excluded and row['representation'] == 'assembly':
        records['standard:' + row['name']] = row, standard
cache, bounds, world_cache = {}, {}, {}


def definition(row, manifest):
    entry = manifest['definitions'][row['definition']]
    digest = entry['brep_sha256']
    if digest not in cache:
        assert sha(entry['brep_path']) == digest
        shape = Part.Shape()
        shape.read(entry['brep_path'])
        assert shape.Placement.isIdentity()
        cache[digest] = shape
    return cache[digest]


def world(name):
    if name not in world_cache:
        row, manifest = records[name]
        shape = definition(row, manifest).copy()
        shape.Placement = pose(row['frame'])
        world_cache[name] = shape
    return world_cache[name]


names = list(records)
boxes = []
for name in names:
    row, manifest = records[name]
    digest = manifest['definitions'][row['definition']]['brep_sha256']
    if digest not in bounds:
        b = definition(row, manifest).BoundBox
        bounds[digest] = np.array(list(itertools.product(
            (b.XMin, b.XMax), (b.YMin, b.YMax), (b.ZMin, b.ZMax))))
    frame = np.array(row['frame']).reshape(4, 4)
    points = bounds[digest] @ frame[:3, :3].T + frame[:3, 3]
    boxes.append(np.r_[points.min(axis=0), points.max(axis=0)])
boxes = np.array(boxes)


def audit(shape):
    b = shape.BoundBox
    lo = np.array([b.XMin, b.YMin, b.ZMin])
    hi = np.array([b.XMax, b.YMax, b.ZMax])
    nearby = np.where(np.all(boxes[:, :3] <= hi + 1e-7, axis=1)
                      & np.all(boxes[:, 3:] >= lo - 1e-7, axis=1))[0]
    pairs = []
    for index in nearby:
        name = names[index]
        other = world(name)
        common = shape.common(other)
        volume = sum(abs(s.Volume) for s in common.Solids)
        valid = common.isNull() or common.isValid()
        pairs.append(dict(other=name, common_mm3=volume, common_valid=valid,
                          passed=valid and volume <= 1e-5,
                          minimum_distance_mm=shape.distToShape(other)[0]))
    return dict(passed=all(p['passed'] for p in pairs), pairs=pairs,
                findings=[p for p in pairs if not p['passed']])


lever_frame = pose(seed.rows['DriverReverseOperatingLever']['frame'])
quadrant = world('DriverReverseQuadrant')
qc = seed.report['details']['controls']
qorigin = lever_frame.inverse().multVec(pose(seed.rows['DriverReverseQuadrant']['frame']).Base)
lower = seed.report['details']['reverse_seed_details']['controls']
slope = -lower['outward_set_mm'] / math.sqrt(lower['hand_reach_mm'] ** 2 - lower['outward_set_mm'] ** 2)
radius = qc['outer_radius_mm']
floor = radius - qc['notch_depth_mm']
nose_origin = V(-controls['nose_width_mm'] / 2,
                qorigin.y - controls['nose_thickness_mm'] / 2,
                floor + controls['nose_bottom_clearance_mm'])
nose = Part.makeBox(controls['nose_width_mm'], controls['nose_thickness_mm'],
                    controls['nose_radial_height_mm'], nose_origin)
nose_world = nose.copy()
nose_world.Placement = lever_frame
nose_path = out / 'nonphysical_detent_tooth.brep'
nose_world.exportBrep(str(nose_path))
nose_audit = audit(nose_world)
negatives = []
for label, delta in [('BelowFloor', V(0, 0, -2)), ('AcrossNotchWall', V(.6, 0, 0))]:
    shape = nose.copy()
    shape.translate(delta)
    shape.Placement = lever_frame.multiply(shape.Placement)
    volume = sum(abs(s.Volume) for s in shape.common(quadrant).Solids)
    negatives.append(dict(name=label, delta_local_mm=list(delta), common_mm3=volume,
                          rejected=volume > 1e-5))

results = []
for index, x in enumerate(controls['lateral_x_candidates_mm']):
    def point(z):
        return V(x, qorigin.y + slope * (z - radius), z)

    start = point(controls['rod_start_z_mm'])
    end = point(controls['rod_end_z_mm'])
    direction = end - start
    length = direction.Length
    rod = Part.makeCylinder(controls['rod_radius_mm'], length, start, direction)
    assert abs(rod.Volume - math.pi * controls['rod_radius_mm'] ** 2 * length) < 1e-5
    rod.Placement = lever_frame
    rod_path = out / ('nonphysical_rod_%d.brep' % index)
    rod.exportBrep(str(rod_path))
    # A path witness for the pawl offset, not a proposed finished pawl profile.
    nose_end = V(0, qorigin.y, nose_origin.z + controls['nose_radial_height_mm'] - 1)
    offset_direction = start - nose_end
    offset = Part.makeCylinder(controls['route_radius_mm'], offset_direction.Length,
                              nose_end, offset_direction)
    offset.Placement = lever_frame
    offset_path = out / ('nonphysical_pawl_route_%d.brep' % index)
    offset.exportBrep(str(offset_path))
    row = dict(x_offset_mm=x, rod_start_local_mm=list(start), rod_end_local_mm=list(end),
               rod_start_world_mm=list(lever_frame.multVec(start)),
               rod_end_world_mm=list(lever_frame.multVec(end)),
               rod_length_mm=length, rod_audit=audit(rod), offset_audit=audit(offset),
               rod_brep=rod_path.name, rod_brep_sha256=sha(rod_path),
               offset_brep=offset_path.name, offset_brep_sha256=sha(offset_path),
               lower_offset_vector_mm=list(offset_direction))
    row['corridor_clear'] = row['rod_audit']['passed'] and row['offset_audit']['passed']
    results.append(row)
    print('X', x, 'rod', row['rod_audit']['passed'], 'offset', row['offset_audit']['passed'], flush=True)

inputs = [args.controls, source, seed.folder / 'report.json', seed.folder / 'isolated/manifest.json',
          seed.folder.parent / 'reverse_quadrant_study_receipt.json', parent.folder / 'report.json',
          parent.folder / 'isolated/manifest.json', standard_path]
write(out / 'report.json', dict(
    worker_sha256=sha(__file__), native_sha256=sha(seed.native), parent_native_sha256=sha(parent.native),
    input_hashes={str(p.resolve().relative_to(ROOT)): sha(p) for p in inputs},
    controls=controls, lever_frame=list(lever_frame.toMatrix().A),
    context_occurrences=len(records), no_mating_pair_exemptions=True,
    rod_y_slope_per_local_z=slope, quadrant_origin_in_lever_mm=list(qorigin),
    detent_tooth=dict(brep=nose_path.name, sha256=sha(nose_path), audit=nose_audit,
                      negative_controls=negatives), cases=results,
    geometry_integrated=False, physical_parts_created=False, latch_qualified=False,
    source_camera_refitted=False,
    scope='Saved-material route witnesses only. Clear cylinders do not qualify the pawl, guide, '
          'threaded connections, upper eye/trigger, spring or hardware. No moving mechanism is validated.',
))
assert nose_audit['passed'] and all(row['rejected'] for row in negatives)
print('Route probe complete; no physical part qualification.', flush=True)
