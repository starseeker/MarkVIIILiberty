"""Quantify fixed-source handle contradictions without changing geometry or cameras."""
import argparse
import math
from pathlib import Path
import numpy as np
from control_rebuild_io_v2 import *

V = App.Vector
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, required=True)
a = p.parse_args()
s = Saved(a.candidate)
r = s.report
render = read(s.folder / 'render_receipt.json')
assert render['native_sha256'] == sha(s.native)
landmarks = H / 'transmission_controls_study/driver_redo01/operating_landmarks01.json'
picks = read(landmarks)
assert sha(landmarks) == render['operating_landmarks_sha256']
reg = read(ROOT / render['registration'])
assert sha(ROOT / render['registration']) == render['registration_sha256']
main = V(*r['details']['foundation']['shafts']['Main']['center_world_mm'])
coef = complex(*render['side_registration']['complex_scale'])
side = -complex(*(np.array(picks['side_cap_pick_px']) - [315, 322])) / coef
matrix = reg['pixels_per_mm'] * np.array([reg['world_plus_x_image_unit'], reg['world_plus_y_image_unit']]).T
standard_path = H / 'transmission_brake_front_study/trial01/standard_context_manifest.json'
standard = read(standard_path)
row = next(v for v in standard['occurrences'] if v['name'] == 'hull_front_slope')
entry = standard['definitions'][row['definition']]
assert sha(entry['brep_path']) == entry['brep_sha256']
nose = Part.Shape()
nose.read(entry['brep_path'])
nose.Placement = pose(row['frame'])
face = max((f for f in nose.Faces if isinstance(f.Surface, Part.Plane)), key=lambda f: f.Area)
normal = face.Surface.Axis
if (main - face.CenterOfMass).dot(normal) < 0:
    normal = -normal
records = {}
for side_name in ['Port', 'Starboard']:
    plan = np.linalg.solve(matrix, np.array(picks['plan_cap_picks_px'][side_name]) - reg['image_center_px'])
    measured = render['operating_handle_comparison'][side_name]
    native_tip = V(*measured['actual_tip_world_mm'])
    pivot = V(*measured['actual_pivot_world_mm'])
    # The two views disagree in X. Keep that residual; do not fit one to the other.
    source_point = main + V(side.real, float(plan[1]), side.imag)
    local = s.definition(s.rows[side_name + 'DriverOperatingHandle']['definition'])
    delta = native_tip - main
    records[side_name] = dict(
        source_plan_relative_xy_mm=list(plan), source_side_relative_xz_mm=[side.real, side.imag],
        source_view_x_disagreement_mm=float(plan[0] - side.real),
        inferred_point_using_side_xz_and_plan_y_mm=list(source_point),
        actual_cap_to_current_pivot_mm=(native_tip - pivot).Length,
        source_cap_to_current_pivot_mm=(source_point - pivot).Length,
        actual_cap_radius_from_main_in_side_plane_mm=math.hypot(delta.x, delta.z),
        source_cap_radius_from_main_in_side_plane_mm=abs(side),
        actual_side_elevation_degrees=math.degrees(math.atan2(delta.z, delta.x)),
        source_side_elevation_degrees=math.degrees(math.atan2(side.imag, side.real)),
        adopted_overall_radial_part_length_mm=local.BoundBox.XLength,
        native_cap_signed_interior_distance_to_front_plane_mm=(native_tip - face.CenterOfMass).dot(normal),
        source_cap_signed_interior_distance_to_front_plane_mm=(source_point - face.CenterOfMass).dot(normal),
        complete_handle_to_front_hull_minimum_mm=s.world(side_name + 'DriverOperatingHandle').distToShape(nose)[0],
    )
result = dict(native_sha256=sha(s.native), renderer_receipt_sha256=sha(s.folder / 'render_receipt.json'),
    landmark_sha256=sha(landmarks), standard_manifest_sha256=sha(standard_path), worker_sha256=sha(Path(__file__)),
    source_camera_refitted=False, geometry_modified=False, records=records,
    conclusion='The cap discrepancy cannot be removed by rotating the unchanged handle about its current second pivot: '
               'the inferred source cap has a substantially greater radius from that pivot. The views also disagree in '
               'fore/aft coordinate. Transferring the source cap literally to the current assembly puts it beyond the '
               'front hull plane. Diagnose the ambiguous37-inch datum, drawing scale/feature picks, source configuration '
               'and absolute driver/hull placement before any refit or global movement. The current full-stock model '
               'is a mechanically checked approximation, not a historical position qualification.')
write(s.folder / 'source_comparison_diagnosis.json', result)
print(records, flush=True)
