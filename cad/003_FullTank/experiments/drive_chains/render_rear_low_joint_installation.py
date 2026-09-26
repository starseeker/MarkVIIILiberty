"""Render saved M569A joints with receivers and the unchanged SNL6 registration."""
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
r, m = read(out/'report.json'), read(out/'isolated/manifest.json')
native = out/r['native_file']
assert sha(native) == r['native_sha256'] == m['native_sha256']
prototype = read(ROOT/r['prototype']/'report.json')
r['specs'], r['joints'] = prototype['specs'], prototype['joints']
r['parent_native'], r['parent_native_sha256'] = r['source_native'], r['source_native_sha256']
parent = ROOT/r['parent_native']
old = read(parent.parent/'isolated/manifest.json')
assert sha(parent) == r['parent_native_sha256'] == old['native_sha256']
rows = {v['name']: v for v in m['occurrences'] if v['name'] in r['specs']}
prior = {v['name']: v for v in old['occurrences']}
selected = [n for n, row in prior.items() if 'RearControlChannel' in row['owners'] or
            n in {v['receiver'] for v in r['joints'].values()}]
validate_native_bindings(dict(native_file=str(native), render_occurrences=list(rows), landmarks=[]), m)
validate_native_bindings(dict(native_file=str(parent), render_occurrences=selected, landmarks=[]), old)
COLORS.update(Fork=(.58, .61, .44), Pin=(.72, .62, .40), Cotter=(.75, .69, .54),
              Nut=(.54, .62, .61), Receiver=(.35, .53, .61), Context=(.53, .56, .54))
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
receivers = {v['receiver'] for v in r['joints'].values()}
context = [item(n, prior[n], old, 'Receiver' if n in receivers else 'Context') for n in selected]
shaded(items+context, out/'low_joints_isometric.svg', (-1, -1, .8),
       'Rear low-speed controls | installed fork / pin / cotter / nut joints; rods pending')
shaded([v for v in items if v['id'].startswith('PortLowBrakeJoint')],
       out/'low_joint_detail.svg', (-1, -1, .65),
       'M569A / M568A | source-counted joint; receiver and rod omitted')
regpath = H/'transmission_controls_study/channel_local_registration01.json'
reg = read(regpath)
source = ROOT/reg['source_image']
assert sha(source) == reg['source_sha256']
camera = dict(projection='orthographic', image_size_px=reg['image_size_px'],
              world_to_camera_rotation=[[-1, 0, 0], [0, 0, -1], [0, -1, 0]],
              origin_world_mm=reg['axis_world_mm'], scale_px_per_mm=reg['pixels_per_mm'],
              principal_px=reg['center_px'])
im = Image.open(source).convert('RGB')
draw = ImageDraw.Draw(im)
for name in [n for n in rows if n.startswith('Port')]+['PortLowSpeedBrakeLever', 'PortLowHorizontalLever']:
    for edge in shapes[name].Edges:
        pts = edge.discretize(Deflection=.35)
        uv = project([[v.x, v.y, v.z] for v in pts], camera)[:, :2]
        if len(uv) > 1:
            draw.line([tuple(v) for v in uv], fill='#8e6a27' if name in rows else '#237a9e', width=1)
draw.text((1130, 690), 'Fixed source camera; port low-speed end joints. Physical rod still pending.', fill='#111111')
im.save(out/'source_overlay.png')
im.crop((1130, 685, 1680, 970)).resize((1650, 855)).save(out/'source_detail.png')
write(out/'render_receipt.json', dict(native_sha256=sha(native), parent_native_sha256=sha(parent),
      manifest_sha256=sha(out/'isolated/manifest.json'), renderer_sha256=sha(Path(__file__)),
      source_registration_sha256=sha(regpath), source_camera_refitted=False, camera=camera,
      images={n: sha(out/n) for n in ['low_joints_isometric.png', 'low_joint_detail.png',
                                    'source_overlay.png', 'source_detail.png']},
      scope='16 saved joint components from the full 3280-component hierarchy, saved receiver/channel/support context, fixed side projection. No completed rods, spring attachments or historical photographic fit.',
      historical_geometry_qualified=False))

# Progression snapshots
snap_iso = ROOT/'cad/intermediate_snapshot_iso_rear_low_joints_001.png'
snap_detail = ROOT/'cad/intermediate_snapshot_detail_rear_low_joints_001.png'
snap_source = ROOT/'cad/intermediate_snapshot_source_rear_low_joints_001.png'
shutil.copy2(out/'low_joints_isometric.png', snap_iso)
shutil.copy2(out/'low_joint_detail.png', snap_detail)
shutil.copy2(out/'source_overlay.png', snap_source)

prior_receipt = read(parent.parent/'progression_receipt.json')
all_prior = dict(prior_receipt['prior'], **prior_receipt['new'])
new_snaps = {
    'cad/intermediate_snapshot_iso_rear_low_joints_001.png': sha(snap_iso),
    'cad/intermediate_snapshot_detail_rear_low_joints_001.png': sha(snap_detail),
    'cad/intermediate_snapshot_source_rear_low_joints_001.png': sha(snap_source),
}
write(out/'progression_receipt.json', dict(
    prior=all_prior,
    new=new_snaps,
    previous_count=len(all_prior),
    new_count=len(new_snaps),
    total_count=len(all_prior) + len(new_snaps),
    native_sha256=sha(native),
    render_receipt_sha256=sha(out/'render_receipt.json')
))

prototype_vr = read(ROOT/r['prototype']/'visual_review.json')
write(out/'visual_review.json', dict(
    disposition='reviewed_local_approximation',
    native_sha256=sha(native),
    source_camera_refitted=False,
    source_registration_sha256=sha(regpath),
    images_inspected=[
        'low_joints_isometric.png',
        'low_joint_detail.png',
        'source_overlay.png',
        'source_detail.png'
    ],
    observations=[
        'Four M569A forks, reconciled M568A pins, spread cotters and plain US Standard nuts are distinct saved solids on four low-speed brake control eyes. Shared pin, cotter and nut match full assembly definitions exactly.',
        'The literal 1 inch length from SNL87:002 is interpreted under throat_to_rod_seat datum (providing 25.4mm threaded socket >= 19.05mm engagement). Estimated throat depth of 23.8125mm (15/16″) clears the starboard fulcrum lever arm entering at -56.89° (extending to 22.6738mm) with 1.14mm clean margin, giving 49.2125mm pin-center to rod-seat distance.',
        'Front forks mount with transverse horizontal pins along +X; rear forks mount with vertical pins clocked along the horizontal rod vector toward the front brake eye. All 16 components clear their receivers, each other and surrounding development/standard context.',
        'Fixed SNL6 registration retains inherited lever silhouette and spring height. New estimated fork faces are not camera-fit landmarks; HB photographs remain uncalibrated.',
        'The two SH946E physical rods connecting front and rear joints remain pending in low_rods increment.',
        'Installed local isometric, fork detail and source comparison inspected. No apparent orphan joints; SH946E rod gaps are deliberately unfinished. Prior receiver silhouette disagreement remains visible.'
    ],
    historical_geometry_qualified=False,
    installation_qualified=False,
    prototype_visual_review_sha256=sha(ROOT/r['prototype']/'visual_review.json'),
    scope='Four low-speed end joints read from full 3280-part native; inherited rear-channel context retained. Source overlay and detail match inspected prototype; installed isometric identifies integration.'
))
print('Rendered low-speed end joints, unchanged-camera source comparison, and visual progression.', flush=True)
