"""Render installed channel mounts beside their saved floor and clutch-control context."""
import argparse
from pathlib import Path
import sys
from types import SimpleNamespace
H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path.insert(0, str(H.parents[1]))
import FreeCAD as App
import Part
from lib.evidence import read, write, sha
from lib.camera_review import validate_native_bindings
from lib.visual_review import shaded
from lib.cad_build import COLORS

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, required=True)
a = p.parse_args()
out = a.candidate.resolve()
r = read(out / 'report.json')
m = read(out / 'isolated/manifest.json')
native = out / r['native_file']
assert sha(native) == m['native_sha256'] == r['native_sha256']
rows = {v['name']: v for v in m['occurrences']}
selection_path = H / 'transmission_controls_study/channel_context01/report.json'
selection = read(selection_path)
nearby = [n for n in selection['rendered_development']
          if n.startswith(('ClutchSupport_', 'EngineFrame_')) or n == 'hull_floor_7']
names = list(r['expected_new_occurrences']) + nearby
validate_native_bindings(dict(native_file=str(native), render_occurrences=names, landmarks=[]), m)
COLORS.update(Channel=(.69,.48,.28), Cleat=(.44,.53,.56), Bolt=(.69,.70,.69),
              Rivet=(.75,.64,.44), Structure=(.50,.59,.64), Control=(.64,.59,.39), Floor=(.48,.54,.52))
cache, items, context = {}, [], []
for name in names:
    row = rows[name]
    d = m['definitions'][row['definition']]
    key = d['brep_sha256']
    if key not in cache:
        assert sha(d['brep_path']) == key
        s = Part.Shape()
        s.read(d['brep_path'])
        assert s.Placement.isIdentity()
        cache[key] = s
    s = cache[key].copy()
    s.Placement = App.Placement(App.Matrix(*row['frame']))
    role = r['expected_new_occurrences'].get(name, {}).get('role')
    system = {'channel':'Channel', 'cleat':'Cleat', 'rivet':'Rivet', 'bolt':'Bolt', 'lock':'Bolt', 'nut':'Bolt'}.get(role, 'Control' if name.startswith('ClutchSupport_') else 'Structure')
    item = dict(id=name, shape=s, target=SimpleNamespace(Shape=cache[key]), definition=key,
                system=system, representation='assembly')
    (context if name == 'hull_floor_7' else items).append(item)
shaded(items, out / 'channel_installed_isometric.svg', (-1,-1,.65),
       'Rear control channel | installed mounts, clutch controls and floor context', context=context)
shaded([v for v in items if v['id'] in r['expected_new_occurrences']],
       out / 'channel_mount_isometric.svg', (-1,-1,.65),
       'Rear control channel | installed four-cleat mounting increment', context=context)
images = ['channel_installed_isometric.png', 'channel_mount_isometric.png']
write(out / 'render_receipt.json', dict(native_sha256=sha(native),
      manifest_sha256=sha(out / 'isolated/manifest.json'), renderer_sha256=sha(Path(__file__)),
      selected_occurrences=names, context_selection_sha256=sha(selection_path),
      images={name: sha(out / name) for name in images}, source_camera_refitted=False,
      scope='Saved development selection with floor in outline. The first view adds the nearby clutch supports/controls and rear engine frame; neither view claims the entire tank or complete operating controls.',
      historical_geometry_qualified=False))
print('Rendered installed mounting increment with', len(nearby), 'context occurrences.', flush=True)
