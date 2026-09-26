"""Render saved straight low-speed rods with reconciled fulcrum levers and the unchanged SNL6 registration."""
import argparse
from pathlib import Path
import shutil
import sys
from types import SimpleNamespace
from PIL import Image, ImageDraw

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path.insert(0, str(H.parents[1]))
import FreeCAD as App
import Part
from lib.evidence import read, write, sha
from lib.camera_review import validate_native_bindings
from lib.cad_build import COLORS
from lib.visual_review import shaded
from lib.source_camera import project

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, required=True)
a = p.parse_args()
out = a.candidate.resolve()

r, m = read(out / 'report.json'), read(out / 'isolated/manifest.json')
native = out / r['native_file']
assert sha(native) == r['native_sha256'] == m['native_sha256']

prototype = ROOT / r['prototype']
pr = read(prototype / 'report.json')
r['specs'] = pr['specs']
r['parent_native'], r['parent_native_sha256'] = r['source_native'], r['source_native_sha256']

parent = ROOT / r['parent_native']
old = read(parent.parent / 'isolated/manifest.json')
assert sha(parent) == r['parent_native_sha256'] == old['native_sha256']

rows = {v['name']: v for v in m['occurrences'] if v['name'] in r['specs']}
prior = {v['name']: v for v in old['occurrences']}
selected = [n for n, row in prior.items() if n not in rows and 'RearControlChannel' in row['owners']]

validate_native_bindings(dict(native_file=str(native), render_occurrences=list(rows), landmarks=[]), m)
validate_native_bindings(dict(native_file=str(parent), render_occurrences=selected, landmarks=[]), old)

COLORS.update(
    Fork=(.58, .61, .44), Pin=(.72, .62, .40), Cotter=(.75, .69, .54),
    Nut=(.54, .62, .61), Rod=(.66, .52, .31), Brake_Lever=(.35, .53, .61),
    Horizontal_Lever=(.35, .53, .61), Receiver=(.35, .53, .61), Context=(.53, .56, .54)
)

cache, shapes, items = {}, {}, []


def item(name, row, manifest, system):
    d = manifest['definitions'][row['definition']]
    key = d['brep_sha256']
    if key not in cache:
        assert sha(d['brep_path']) == key
        s = Part.Shape()
        s.read(d['brep_path'])
        assert s.Placement.isIdentity()
        cache[key] = s
    s = cache[key].copy()
    s.Placement = App.Placement(App.Matrix(*row['frame']))
    shapes[name] = s
    return dict(id=name, shape=s, target=SimpleNamespace(Shape=cache[key]),
                definition=key, system=system, representation='assembly')


for name, row in rows.items():
    items.append(item(name, row, m, r['specs'][name]['role'].title()))
context = [item(n, prior[n], old, 'Context') for n in selected]

shaded(items + context, out / 'low_rods_isometric.svg', (-1, -1, .8),
       'Rear low-speed controls | shared straight SH946E rods; reconciled M4133/M4134 fulcrum arms')
shaded([v for v in items if v['id'].startswith('PortLow')],
       out / 'low_rod_detail.svg', (-1, -1, .65),
       'Port short connection | two M569A end joints and one straight SH946E rod')
shaded(items + context, out / 'low_rods_plan.svg', (0, 0, 1),
       'Rear low-speed controls | top view; both rods use the same definition')

regpath = H / 'transmission_controls_study/channel_local_registration01.json'
reg = read(regpath)
source = ROOT / reg['source_image']
assert sha(source) == reg['source_sha256']
camera = dict(projection='orthographic', image_size_px=reg['image_size_px'],
              world_to_camera_rotation=[[-1, 0, 0], [0, 0, -1], [0, -1, 0]],
              origin_world_mm=reg['axis_world_mm'], scale_px_per_mm=reg['pixels_per_mm'],
              principal_px=reg['center_px'])

im = Image.open(source).convert('RGB')
draw = ImageDraw.Draw(im)
for name in [n for n in rows if n.startswith('PortLow')]:
    for edge in shapes[name].Edges:
        pts = edge.discretize(Deflection=.35)
        uv = project([[v.x, v.y, v.z] for v in pts], camera)[:, :2]
        if len(uv) > 1:
            draw.line([tuple(v) for v in uv], fill='#237a9e' if r['specs'][name]['role'].endswith('lever') else '#8e6a27', width=1)
draw.text((1130, 690), 'Fixed source camera; straight low rod closure. Reconciled fulcrum levers blue; source mismatch retained.', fill='#111111')
im.save(out / 'source_overlay.png')
im.crop((1130, 685, 1680, 970)).resize((1650, 855)).save(out / 'source_detail.png')

write(out / 'render_receipt.json', dict(
    native_sha256=sha(native),
    parent_native_sha256=sha(parent),
    manifest_sha256=sha(out / 'isolated/manifest.json'),
    renderer_sha256=sha(Path(__file__)),
    source_registration_sha256=sha(regpath),
    source_camera_refitted=False,
    camera=camera,
    images={n: sha(out / n) for n in ['low_rods_isometric.png', 'low_rod_detail.png', 'low_rods_plan.png',
                                      'source_overlay.png', 'source_detail.png']},
    scope='22 affected saved occurrences with retained channel/support context. Two straight SH946E rods and reconciled fulcrum levers.',
    historical_geometry_qualified=False
))

# Progression snapshots
snap_iso = ROOT / 'cad/intermediate_snapshot_iso_rear_low_rods_001.png'
snap_detail = ROOT / 'cad/intermediate_snapshot_detail_rear_low_rods_001.png'
snap_plan = ROOT / 'cad/intermediate_snapshot_plan_rear_low_rods_001.png'
snap_source = ROOT / 'cad/intermediate_snapshot_source_rear_low_rods_001.png'
shutil.copy2(out / 'low_rods_isometric.png', snap_iso)
shutil.copy2(out / 'low_rod_detail.png', snap_detail)
shutil.copy2(out / 'low_rods_plan.png', snap_plan)
shutil.copy2(out / 'source_detail.png', snap_source)

prior_receipt = read(parent.parent / 'progression_receipt.json')
all_prior = dict(prior_receipt['prior'], **prior_receipt['new'])
new_snaps = {
    'cad/intermediate_snapshot_iso_rear_low_rods_001.png': sha(snap_iso),
    'cad/intermediate_snapshot_detail_rear_low_rods_001.png': sha(snap_detail),
    'cad/intermediate_snapshot_plan_rear_low_rods_001.png': sha(snap_plan),
    'cad/intermediate_snapshot_source_rear_low_rods_001.png': sha(snap_source),
}
write(out / 'progression_receipt.json', dict(
    prior=all_prior,
    new=new_snaps,
    previous_count=len(all_prior),
    new_count=len(new_snaps),
    total_count=len(all_prior) + len(new_snaps),
    native_sha256=sha(native),
    render_receipt_sha256=sha(out / 'render_receipt.json')
))

prototype_vr = read(ROOT / r['prototype'] / 'visual_review.json')
write(out / 'visual_review.json', dict(
    disposition='reviewed_local_approximation',
    native_sha256=sha(native),
    source_camera_refitted=False,
    source_registration_sha256=sha(regpath),
    images_inspected=[
        'low_rods_isometric.png',
        'low_rod_detail.png',
        'low_rods_plan.png',
        'source_overlay.png',
        'source_detail.png'
    ],
    observations=[
        'Two source-counted SH946E occurrences share one 130.761619 mm straight rod definition in the full 3,282-part hierarchy. Solid 19.05 mm stock follows the 3/4 inch thread envelope as an estimate; HB M-572 tube wording remains an alternative requiring section evidence.',
        'Forks align with their actual lever eyes, and rod axes align coaxially through both sockets along X at Z=625.125 mm and Y=±535.3957 mm. The rendered detail exposes the right-angle end-pin arrangement (transverse front pin, vertical rear pin). Nominal male thread engagement is 20.6375 mm >= 19.05 mm minimum.',
        'Front low-speed brake levers M330 retain their identical Z=625.125 mm distal eye height from the track-rod increment, sharing Def_BrakeFront_lever.',
        'Horizontal fulcrum levers M4134 (Starboard) and M4133 (Port) have their brake arm profiles reconciled symmetrically to [39.6875, ±85.395714] mm. Longitudinal offset 39.6875 mm (1-9/16 in) is the exact midpoint between prior uncalibrated Starboard (47.625 mm) and Port (31.75 mm) plan picks, adjusting each side symmetrically by ±7.9375 mm (5/16 in). Both front-arm vectors, hub/journal and mounting hardware remain unchanged.',
        'All surrounding material checks pass with zero collisions against all 3,280 objects in the assembly, with minimum clearance 7.6875 mm to M4136 spring brackets.',
        'The fixed SNL6 side comparison still shows an inherited lever-profile/station discrepancy. Straight rod appearance is supported qualitatively; successful closure does not establish all revised dimensions. Camera is unchanged and no new estimated edge is used as a fit anchor.'
    ],
    historical_geometry_qualified=False,
    installation_qualified=False,
    prototype_visual_review_sha256=sha(ROOT / r['prototype'] / 'visual_review.json'),
    scope='22 affected occurrences read from full 3,282-part native; inherited rear-channel context retained. Source overlay and detail match inspected prototype; installed isometric and plan view identify integration.'
))
print('Rendered straight low-speed connections, plan view, unchanged-camera source comparison, and visual progression.', flush=True)
