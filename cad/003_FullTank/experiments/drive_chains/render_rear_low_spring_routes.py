"""Show checked local route witnesses with their actual saved interfaces and fixed source camera."""
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
p.add_argument('--routes', type=Path, required=True)
a = p.parse_args()
trial, out = a.candidate.resolve(), a.routes.resolve()
r = read(trial/'report.json')
m = read(trial/'isolated/manifest.json')
native = trial/r['native_file']
parent = ROOT/r['parent_native']
old = read(parent.parent/'isolated/manifest.json')
route = read(out/'route_checks.json')
assert route['passed'] and sha(native) == m['native_sha256'] == route['trial_native_sha256']
assert sha(parent) == old['native_sha256'] == route['parent_native_sha256']
rows, prior = [{v['name']: v for v in data['occurrences']} for data in [m, old]]
selected = [n for n in prior if n.endswith(('LowSpeedBrakeLever','TrackBrakeLever')) or any(v.endswith('ControlFulcrum') for v in prior[n].get('owners',[]))]
validate_native_bindings(dict(native_file=str(parent), render_occurrences=selected, landmarks=[]), old)
validate_native_bindings(dict(native_file=str(native), render_occurrences=list(rows), landmarks=[]), m)
COLORS.update(Guide=(.57,.59,.47), Channel=(.69,.48,.28), Context=(.43,.52,.56),
              RodWitness=(.77,.62,.24), Hardware=(.73,.67,.50))
cache, items, outlines, shapes = {}, [], [], {}


def item(name, row, manifest, system):
    d = manifest['definitions'][row['definition']]
    key = d['brep_sha256']
    if key not in cache:
        assert sha(d['brep_path']) == key
        shape = Part.Shape()
        shape.read(d['brep_path'])
        assert shape.Placement.isIdentity()
        cache[key] = shape
    shape = cache[key].copy()
    shape.Placement = App.Placement(App.Matrix(*row['frame']))
    shapes[name] = shape
    return dict(id=name, shape=shape, target=SimpleNamespace(Shape=cache[key]),
                definition=key, system=system, representation='assembly')


for name, row in rows.items():
    role = r['specs'][name]['role']
    items.append(item(name, row, m, dict(channel='Channel', bracket='Guide', rivet='Hardware')[role]))
for name in selected:
    items.append(item(name, prior[name], old, 'Context'))
for file, digest in route['geometry_hashes'].items():
    assert sha(out/file) == digest
    shape = Part.Shape()
    shape.read(str(out/file))
    name = Path(file).stem
    shapes[name] = shape
    record = dict(id=name, shape=shape, target=SimpleNamespace(Shape=shape), definition=digest,
                  system='RodWitness', representation='assembly')
    (outlines if 'Spring' in name else items).append(record)
shaded(items, out/'route_isometric.svg', (-1,-1,.8),
       'Clearance study | short brake-rod cores; M564 spring corridors in outline', context=outlines)
detail = [v for v in items if v['id'].startswith(('Port',))]
shaded(detail, out/'route_detail.svg', (-1,-1,.6),
       'Port short connections | rod cores and provisional spring corridors',
       context=[v for v in outlines if v['id'].startswith('Port')])
regpath = H/'transmission_controls_study/channel_local_registration01.json'
reg = read(regpath)
source = ROOT/reg['source_image']
assert sha(source) == reg['source_sha256']
camera = dict(projection='orthographic', image_size_px=reg['image_size_px'],
              world_to_camera_rotation=[[-1,0,0],[0,0,-1],[0,-1,0]],
              origin_world_mm=reg['axis_world_mm'], scale_px_per_mm=reg['pixels_per_mm'],
              principal_px=reg['center_px'])
im = Image.open(source).convert('RGB')
draw = ImageDraw.Draw(im)
for name in ['RearControlChannelStock', 'PortLowSpringBracket', 'PortTrackRodCore', 'PortLowRodCore', 'PortTrackSpringCore', 'PortLowSpringCore']:
    color = '#d26e19' if name == 'RearControlChannelStock' else '#1d7ea3' if 'Rod' in name else '#74794d'
    for edge in shapes[name].Edges:
        uv = project([list(v) for v in edge.discretize(Deflection=.35)], camera)[:, :2]
        if len(uv) > 1:
            draw.line([tuple(v) for v in uv], fill=color, width=1)
draw.text((1130,690), 'Local route witnesses only; fixed source registration; source disagreement retained.', fill='#111111')
im.save(out/'route_source_overlay.png')
im.crop((1130,685,1680,970)).resize((1650,855)).save(out/'route_source_detail.png')
write(out/'render_receipt.json', dict(trial_native_sha256=sha(native), parent_native_sha256=sha(parent),
    route_checks_sha256=sha(out/'route_checks.json'), renderer_sha256=sha(Path(__file__)),
    source_registration_sha256=sha(regpath), source_camera_refitted=False,
    images={n:sha(out/n) for n in ['route_isometric.png','route_detail.png','route_source_overlay.png','route_source_detail.png']},
    scope='Clearance witnesses in saved neighboring geometry; these are not completed SH946D/SH946E rods or M564 spring models.'))
print('Rendered checked route witnesses and fixed-source comparison.', flush=True)
