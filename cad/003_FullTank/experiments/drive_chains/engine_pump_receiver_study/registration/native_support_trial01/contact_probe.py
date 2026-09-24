"""Distinguish volumetric intersection from planar bearing contact on this runtime."""
from pathlib import Path
import hashlib
import json
import FreeCAD as App
import Part

OUT = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.file_digest(p.open('rb'), 'sha256').hexdigest()
r = read(OUT / 'report.json')
m = read(OUT / 'isolated/manifest.json')
assert sha(OUT / r['native_file']) == m['native_sha256'] == r['native_sha256']
rows = {v['name']: v for v in m['occurrences']}

def shape(name):
    row = rows[name]
    d = m['definitions'][row['definition']]
    f = Path(d['brep_path'])
    assert sha(f) == d['brep_sha256']
    s = Part.Shape()
    s.read(str(f))
    s.Placement = App.Placement(App.Matrix(*row['frame']))
    return s

def planar(s, z):
    return [f for f in s.Faces if type(f.Surface).__name__ == 'Plane' and
            abs(f.BoundBox.ZMin - z) < 1e-7 and abs(f.BoundBox.ZMax - z) < 1e-7]

def contact(one, two, z):
    left, right = planar(one, z), planar(two, z)
    return dict(first_faces=len(left), second_faces=len(right),
                face_intersection_area_mm2=sum(a.common(b).Area for a in left for b in right),
                solid_intersection_area_mm2=one.common(two).Area,
                solid_intersection_volume_mm3=one.common(two).Volume,
                minimum_distance_mm=one.distToShape(two)[0])

one, two = Part.makeBox(10, 10, 10), Part.makeBox(10, 10, 10, App.Vector(0, 0, 10))
results = {'touching_boxes': contact(one, two, 10), 'mounts': {}}
upper = shape('EngineCase_upper')
lifted = upper.copy()
lifted.translate(App.Vector(0, 0, .01))
for side in ['Left', 'Right']:
    rail = shape('EngineSuspension_' + side + 'Rail')
    results['mounts'][side] = contact(rail, upper, r['crankshaft_axis_z'])
    results['mounts'][side + '_negative_0.01mm_gap'] = contact(rail, lifted, r['crankshaft_axis_z'])
results.update(native_sha256=r['native_sha256'], script_sha256=sha(Path(__file__)),
               freecad=App.Version(), occ=Part.OCC_VERSION)
(OUT / 'contact_probe.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps(results), flush=True)
