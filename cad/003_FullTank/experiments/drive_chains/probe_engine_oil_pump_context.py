"""Measure the proposed oil-pump placement against the saved engine assembly.

Read-only diagnostic: records collisions and shaft engagement before revising
the receiving case. It neither installs the pump nor qualifies the assembly.
Run through freecad_headless.py with an explicit --output directory.
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STAGE = HERE.parents[1]
ROOT = STAGE.parents[1]
sys.path[:0] = [str(HERE), str(STAGE)]
import FreeCAD as App
import Part
from lib.cad_build import leaves
from lib.evidence import read, write, sha

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
out = a.output.resolve()
out.mkdir(parents=True, exist_ok=True)
pump_dir = HERE/'engine_oil_pump_mounting_study'
parent_dir = HERE/'engine_water_pump_connections_study'
r, pr = read(pump_dir/'report.json'), read(parent_dir/'report.json')
native, parent = pump_dir/r['native_file'], parent_dir/pr['native_file']
assert sha(native) == r['native_sha256']
assert sha(parent) == pr['native_sha256']
doc = App.openDocument(str(parent))
pdoc = App.openDocument(str(native))
try:
    engine_frame = doc.TankLibertyEngine.getGlobalPlacement()
    pump_frame = App.Placement(App.Vector(r['controls']['pump_axis_x'], 0,
                                         r['controls']['pump_mount_z']), App.Rotation())
    world = engine_frame.multiply(pump_frame)
    inverse = engine_frame.inverse()
    neighbors = leaves(doc.Root)
    pairs = []
    matched = set()
    oil_shapes = {}
    for row in r['occurrences']:
        link = pdoc.getObject(row['name'])
        local = pdoc.getObject(row['assembly']).getGlobalPlacement().multiply(link.LinkPlacement)
        s = link.LinkedObject.Shape.copy()
        s.Placement = world.multiply(local).multiply(s.Placement)
        oil_shapes[row['name']] = s
        for n in neighbors:
            t = n['shape']
            if not s.BoundBox.intersect(t.BoundBox):
                continue
            volume = abs(s.common(t).Volume)
            entry = dict(pump=row['name'], neighbor=n['id'], overlap_mm3=volume,
                         clear=volume < 1e-5)
            pairs.append(entry)
            matched.add(n['id'])
            write(out/'progress.json', pairs)
            print(row['name'], n['id'], volume, flush=True)
    # Read actual shapes in a common engine frame, retaining the proposed
    # installation separately from both source documents.
    selected = {}
    for n in neighbors:
        if n['id'] in matched:
            s = n['shape'].copy()
            s.Placement = inverse.multiply(s.Placement)
            selected[n['id']] = s
    for name, shape in oil_shapes.items():
        s = shape.copy()
        s.Placement = inverse.multiply(s.Placement)
        selected[name] = s
    bounds = {name: dict(zip(['xmin', 'ymin', 'zmin', 'xmax', 'ymax', 'zmax'],
              [s.BoundBox.XMin, s.BoundBox.YMin, s.BoundBox.ZMin,
               s.BoundBox.XMax, s.BoundBox.YMax, s.BoundBox.ZMax]))
              for name, s in selected.items()}
    result = dict(status='Proposed placement diagnostic; no installation qualification',
                  pump_native_sha256=sha(native), parent_native_sha256=sha(parent),
                  checker_sha256=sha(Path(__file__)), proposed_engine_placement=list(pump_frame.toMatrix().A),
                  engine_world_frame=list(engine_frame.toMatrix().A),
                  pump_components=len(oil_shapes), parent_components=len(neighbors),
                  checked_pairs=len(pairs), pairs=pairs,
                  collisions=[row for row in pairs if not row['clear']],
                  engine_frame_bounds=bounds, neighbors=sorted(matched),
                  source_documents_unchanged=(sha(native)==r['native_sha256'] and sha(parent)==pr['native_sha256']))
    write(out/'context_probe.json', result)
    print(json.dumps(dict(checked_pairs=len(pairs), collisions=len(result['collisions']),
                          neighbors=sorted(matched))), flush=True)
finally:
    App.closeDocument(pdoc.Name)
    App.closeDocument(doc.Name)
