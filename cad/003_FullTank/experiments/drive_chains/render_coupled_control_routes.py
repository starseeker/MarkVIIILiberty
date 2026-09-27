"""Render complete saved control routes, with local meshes and explicit frames."""
import argparse
from pathlib import Path
from types import SimpleNamespace
from control_rebuild_io_v2 import H, ROOT, Saved, sha, write
from lib.camera_review import validate_native_bindings
from lib.visual_review import COLORS, shaded

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, required=True)
s = Saved(p.parse_args().candidate)
out = s.folder / 'routes_visual01'
out.mkdir(exist_ok=False)
validate_native_bindings(dict(native_file=str(s.native), render_occurrences=list(s.rows), landmarks=[]), s.manifest)
COLORS.update(RouteStock=(.68, .45, .25), RouteControl=(.36, .48, .65),
              RouteSeat=(.42, .31, .22), RouteMount=(.50, .58, .49))
names = [n for n in s.rows if not n.startswith(('hull_', 'upper_'))]
items = []
for n in names:
    row = s.rows[n]
    system = 'RouteStock' if 'Rod' in n else 'RouteSeat' if 'Seat' in n else 'RouteMount' if any(t in n for t in ['Support', 'Mount', 'Bracket']) else 'RouteControl'
    items.append(dict(id=n, definition=row['definition'], shape=s.world(n),
                      target=SimpleNamespace(Shape=s.definition(row['definition'])),
                      representation='assembly', system=system))
for name, direction in [('isometric', (1, -1.8, 1.3)), ('plan', (0, 0, 1))]:
    shaded(items, out / (name + '.svg'), direction,
           'Coupled controls | complete existing rods and joints; remaining foot/reverse connections unbuilt',
           canvas=(2200, 1100))
write(out / 'render_receipt.json', dict(native_sha256=sha(s.native),
      renderer_sha256=sha(Path(__file__)), occurrences=names, geometry_integrated=False,
      display_note='Hull and floors omitted from display; all saved control route stock retained. No historical camera fitting.',
      images={p.name:sha(p) for p in out.glob('*.png')}))
print('Complete coupled route views saved.', flush=True)
