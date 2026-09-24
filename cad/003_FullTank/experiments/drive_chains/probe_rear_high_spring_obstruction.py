"""Measure actual support obstruction around the provisional high-speed spring guides."""
import argparse
from pathlib import Path
import sys
H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path.insert(0, str(H.parents[1]))
import FreeCAD as App
import Part
from lib.evidence import read, write, sha
from lib.camera_review import validate_native_bindings
V = App.Vector
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, required=True)
a = p.parse_args()
out = a.candidate.resolve()
r = read(out/'report.json')
native = ROOT/r['parent_native']
m = read(native.parent/'isolated/manifest.json')
assert sha(native) == r['parent_native_sha256'] == m['native_sha256']
names = ['ClutchSupport_LeftBracket', 'ClutchSupport_RearAuxRod', 'ClutchSupport_AuxFork']
validate_native_bindings(dict(native_file=str(native), render_occurrences=names, landmarks=[]), m)
shapes = {}
def bounds(shape):
    b = shape.BoundBox
    return [b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax]
for name in names:
    row = next(v for v in m['occurrences'] if v['name'] == name)
    d = m['definitions'][row['definition']]
    assert sha(d['brep_path']) == d['brep_sha256']
    shape = Part.Shape()
    shape.read(d['brep_path'])
    shape.Placement = App.Placement(App.Matrix(*row['frame']))
    shapes[name] = shape
sections = []
for y in [150., 190.5, 203.2, 222.25, 241.3, 254., 285., 315., 350.]:
    for z in [584.5, 590., 600., 606.9279411764706, 620., 630., 645.]:
        line = Part.makeLine(V(2150, y, z), V(2525, y, z))
        occupied = {}
        for name, shape in shapes.items():
            common = line.common(shape)
            if common.Edges:
                occupied[name] = [bounds(edge) for edge in common.Edges]
        sections.append(dict(y_mm=y, z_mm=z, occupied=occupied))
result = dict(parent_native_sha256=sha(native), probe_sha256=sha(Path(__file__)),
              occurrence_bounds={n: bounds(s) for n, s in shapes.items()},
              x_sections=sections, geometry_modified=False,
              scope='Saved material intersected by zero-radius probe lines; not rod-clearance qualification.')
write(out/'support_obstruction.json', result)
print(result['occurrence_bounds'], flush=True)
for row in sections:
    if row['y_mm'] == 222.25:
        print(row, flush=True)
