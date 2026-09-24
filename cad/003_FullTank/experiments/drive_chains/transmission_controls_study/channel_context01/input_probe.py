"""Measure saved rear floor/support geometry before choosing channel coordinates."""
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
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
out = a.output.resolve()
assert not out.exists()
out.mkdir(parents=True)
parent = H / 'transmission_controls_study/us_nuts01'
m = read(parent / 'isolated/manifest.json')
r = read(parent / 'report.json')
native = parent / r['native_file']
assert sha(native) == m['native_sha256'] == r['native_sha256']
standard_path = H / 'transmission_brake_front_study/trial01/standard_context_manifest.json'
standard = read(standard_path)
assert all(sha(ROOT / f) == digest for f, digest in standard['native_files'].items())
rows = {v['name']: v for v in m['occurrences']}
cache = {}

def world(row, manifest):
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
    return s, key

def bounds(s):
    b = s.BoundBox
    return [b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax]

def intersects(b, region):
    return all(b[i] <= region[i+3] and b[i+3] >= region[i] for i in range(3))

region = [2200, -1200, 520, 3050, 1200, 1000]
records = []
items = []
context = []
selected = []
COLORS.update(Floor=(.49,.53,.50), Structure=(.52,.59,.64), Control=(.76,.48,.24))
for name, row in rows.items():
    s, key = world(row, m)
    b = bounds(s)
    if not intersects(b, region):
        continue
    selected.append(name)
    planes = []
    for f in s.Faces:
        if isinstance(f.Surface, Part.Plane):
            normal = f.normalAt(0, 0)
            if abs(normal.z) > .999999:
                planes.append(dict(z_mm=f.CenterOfMass.z, area_mm2=f.Area, bounds_mm=bounds(f), normal=[normal.x, normal.y, normal.z]))
    records.append(dict(name=name, origin='development', definition_sha256=key, bounds_mm=b, horizontal_faces=planes))
    item = dict(id=name, shape=s, target=SimpleNamespace(Shape=cache[key]), definition=key,
                system='Floor' if 'hull_floor' in name else 'Control' if 'Control' in name else 'Structure', representation='assembly')
    (context if 'hull_floor' in name else items).append(item)
validate_native_bindings(dict(native_file=str(native), render_occurrences=selected, landmarks=[]), m)
excluded = set(rows) | {'PortPinion_Rotor_Casting', 'StarboardPinion_Rotor_Casting'}
for row in standard['occurrences']:
    if row['name'] in excluded or row['representation'] != 'assembly' or not intersects(row['bounds_mm'], region):
        continue
    s, key = world(row, standard)
    records.append(dict(name=row['name'], origin='retained_standard', definition_sha256=key, bounds_mm=bounds(s)))
    if row['system'] == 'HullStructure':
        context.append(dict(id=row['name'], shape=s, target=SimpleNamespace(Shape=cache[key]), definition=key, system='Floor', representation='assembly'))
write(out / 'report.json', dict(
    native_sha256=sha(native), manifest_sha256=sha(parent/'isolated/manifest.json'),
    standard_manifest_sha256=sha(standard_path), probe_sha256=sha(Path(__file__)),
    region_world_mm=region, axes='X forward, Y port, Z up', measurements=records,
    rendered_development=selected, rendered_standard_context=[v['id'] for v in context if v['id'] not in rows],
    geometry_modified=False, source_camera_fitted=False,
    limits=['Current CAD dimensions and interfaces only; not historical dimensions.',
            'Bounding boxes shortlist the region; no empty-space or mounting-fit acceptance is implied.',
            'Standard source natives and selected BReps are hashed; development archive bindings are independently verified.']))
shaded(items, out/'rear_floor_context.svg', (1,-1,.55), 'Rear controls | existing floor and powertrain mounting context', context=context)
print('Measured',len(records),'nearby occurrences; native documents unchanged',flush=True)
