"""Measure saved complete handle alternatives against source and retained stock."""
import argparse
import math
from pathlib import Path
from control_rebuild_io_v2 import *
from lib.camera_review import validate_native_bindings

V = App.Vector
Y = V(0, 1, 0)
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, required=True)
a = p.parse_args()
s = Saved(a.candidate)
parent = Saved((ROOT / s.report['parent_native']).parent)
out = s.folder / 'profile_checks'
out.mkdir(exist_ok=False)
validate_native_bindings(dict(native_file=str(s.native), render_occurrences=list(s.rows), landmarks=[]), s.manifest)
assert all(sha(ROOT / f) == digest for f, digest in s.report['input_hashes'].items())
checks = []


def ck(name, passed, **details):
    checks.append(dict(name=name, passed=bool(passed), **details))
    if not passed:
        print('FAIL', name, details, flush=True)


def volume(shape):
    return sum(abs(v.Volume) for v in shape.Solids)


def same(one, two):
    return (volume(one.cut(two)) < 1e-5 and volume(two.cut(one)) < 1e-5
            and not one.cut(two, 1e-4).Faces and not two.cut(one, 1e-4).Faces)


changed = s.report['changed_definitions']
ck('Only the two existing handle definitions changed', len(changed) == 2
   and all('OperatingHandle_' in key for key in changed)
   and not s.report['new_occurrences'] and not s.report['new_definitions'])
for key in s.manifest['definitions']:
    q = s.definition(key)
    ck(key + ' saved closed valid solid', q.isValid() and len(q.Solids) == 1
       and q.Solids[0].isClosed() and q.Placement.isIdentity() and q.getTolerance(1) <= 1e-4)
    if key not in changed:
        ck(key + ' retained material', same(q, parent.definition(key)))
for name, row in s.rows.items():
    old = parent.rows[name]
    ck(name + ' retained identity and frame', row['definition'] == old['definition']
       and max(abs(x-y) for x,y in zip(row['frame'], old['frame'])) < 1e-7)

old_render = read(parent.folder / 'render_receipt.json')
reg = read(ROOT / old_render['registration'])
assert sha(ROOT / old_render['registration']) == old_render['registration_sha256']
landmark_path = H / 'transmission_controls_study/driver_redo01/operating_landmarks01.json'
picks = read(landmark_path)
assert sha(landmark_path) == old_render['operating_landmarks_sha256']
main = V(*s.report['details']['foundation']['shafts']['Main']['center_world_mm'])
coef = complex(*old_render['side_registration']['complex_scale'])
anchor = reg['construction_picks']
pa, pb = [complex(*anchor[k]) for k in ['main_shaft_starboard_tip_px', 'main_shaft_port_tip_px']]
span = reg['printed_main_shaft_length_mm']
standard_path = H / 'transmission_brake_front_study/trial01/standard_context_manifest.json'
standard = read(standard_path)
row = next(v for v in standard['occurrences'] if v['name'] == 'hull_front_slope')
entry = standard['definitions'][row['definition']]
assert sha(entry['brep_path']) == entry['brep_sha256']
nose = Part.Shape()
nose.read(entry['brep_path'])
nose.Placement = pose(row['frame'])
face = max((f for f in nose.Faces if isinstance(f.Surface, Part.Plane)), key=lambda f:f.Area)
normal = face.Surface.Axis
if (main-face.CenterOfMass).dot(normal) < 0:
    normal = -normal

lower = Part.makeBox(475, 1000, 600, V(-100, -500, -300))
records = {}
choice = s.report['details']['handle_profile_hypothesis']
for side in ['Port', 'Starboard']:
    name = side + 'DriverOperatingHandle'
    row = s.rows[name]
    local = s.definition(row['definition'])
    old = parent.definition(row['definition'])
    ck(side + ' all lower stock through X375 preserved', same(local.common(lower), old.common(lower)))
    if choice['name'] == 'overall_control':
        ck(side + ' complete original handle reproduced', same(local, old))
    caps = [f.Surface for f in local.Faces if isinstance(f.Surface, Part.Sphere)]
    ck(side + ' one full-sized grip cap', len(caps) == 1 and abs(caps[0].Radius-10.5) < 1e-7)
    cap = caps[0]
    pole_local = cap.Center + V(cap.Radius, 0, 0)
    tip = pose(row['frame']).multVec(pole_local)
    delta = tip - main
    datum = choice['controls']['length_datum']
    measured = (pole_local.x + 25 if datum == 'overall_radial_extent' else
                pole_local.Length if datum == 'second_pivot_to_grip_pole' else
                math.hypot(delta.x, delta.z))
    ck(side + ' stated 37-inch interpretation retained in saved solid', abs(measured-939.8) < 1e-7,
       datum=datum, measured_mm=measured)
    bore = [f for f in local.Faces if isinstance(f.Surface, Part.Cylinder)
            and abs(f.Surface.Radius-11.2125) < 1e-7]
    ck(side + ' actual pivot bore retained', len(bore) == 1)
    full = s.world(name)
    common = full.common(nose)
    planar = (pa+pb)/2 + complex(delta.y, delta.x)*(pb-pa)/span
    side_px = complex(315,322) - coef*complex(delta.x,delta.z)
    records[side] = dict(
        actual_tip_world_mm=list(tip), actual_tip_local_mm=list(pole_local),
        measured_length_mm=measured, length_datum=datum,
        canonical_radial_extent_mm=pole_local.x+25,
        plan_tip_px=[planar.real,planar.imag], side_tip_px=[side_px.real,side_px.imag],
        plan_residual_px=abs(planar-complex(*picks['plan_cap_picks_px'][side])),
        side_residual_px=abs(side_px-complex(*picks['side_cap_pick_px'])),
        complete_handle_front_hull_intersection_mm3=volume(common),
        complete_handle_front_hull_distance_mm=full.distToShape(nose)[0],
        grip_pole_signed_interior_plane_distance_mm=(tip-face.CenterOfMass).dot(normal),
        front_hull_clear=volume(common)<1e-5 and (common.isNull() or common.isValid()),
    )

result = dict(passed=all(v['passed'] for v in checks), checks=checks, records=records,
              native_sha256=sha(s.native), parent_native_sha256=sha(parent.native),
              checker_sha256=sha(Path(__file__)), registration_sha256=sha(ROOT / old_render['registration']),
              landmarks_sha256=sha(landmark_path), standard_manifest_sha256=sha(standard_path),
              front_plane=dict(center_mm=list(face.CenterOfMass), inward_normal=list(normal),
                               main_shaft_interior_distance_mm=(main-face.CenterOfMass).dot(normal)),
              source_camera_refitted=False, integration_accepted=False,
              scope='Saved shape, lower-stock/frame preservation and stated-datum checks. Front-hull fit and source residuals are separately reported; a passing construction result does not qualify installation.')
write(out / 'report.json', result)
print(choice['name'], 'construction checks',len(checks),'passed',result['passed'],'measurements',records,flush=True)
assert result['passed']
