"""Render saved M569C joints with receivers and the unchanged SNL6 registration."""
import argparse
from pathlib import Path
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
parent = ROOT/r['parent_native']
old = read(parent.parent/'isolated/manifest.json')
assert sha(parent) == r['parent_native_sha256'] == old['native_sha256']
rows = {v['name']: v for v in m['occurrences']}
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
shaded(items+context, out/'track_joints_isometric.svg', (-1, -1, .8),
       'Rear track controls | four fork / pin / cotter / nut joints; rods pending')
shaded([v for v in items if v['id'].startswith('PortTrackBrakeJoint')],
       out/'track_joint_detail.svg', (-1, -1, .65),
       'M569C / M568C | source-counted joint; receiver and rod omitted')
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
for name in [n for n in rows if n.startswith('Port')]+['PortTrackBrakeLever', 'PortTrackHorizontalLever']:
    for edge in shapes[name].Edges:
        pts = edge.discretize(Deflection=.35)
        uv = project([[v.x, v.y, v.z] for v in pts], camera)[:, :2]
        if len(uv) > 1:
            draw.line([tuple(v) for v in uv], fill='#8e6a27' if name in rows else '#237a9e', width=1)
draw.text((1130, 690), 'Fixed source camera; port track end joints. Physical rod still pending.', fill='#111111')
im.save(out/'source_overlay.png')
im.crop((1130, 685, 1680, 970)).resize((1650, 855)).save(out/'source_detail.png')
write(out/'render_receipt.json', dict(native_sha256=sha(native), parent_native_sha256=sha(parent),
      manifest_sha256=sha(out/'isolated/manifest.json'), renderer_sha256=sha(Path(__file__)),
      source_registration_sha256=sha(regpath), source_camera_refitted=False, camera=camera,
      images={n: sha(out/n) for n in ['track_joints_isometric.png', 'track_joint_detail.png',
                                    'source_overlay.png', 'source_detail.png']},
      scope='Saved16 joint components, saved receiver/channel/support context, fixed side projection. No completed rods, spring attachments or historical photographic fit.',
      historical_geometry_qualified=False))
print('Rendered track end joints and unchanged-camera source comparison.', flush=True)
