"""Display-only section of the rejected initial oil-pump installation fit."""
import argparse
import sys
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
STAGE = HERE.parents[1]
sys.path[:0] = [str(HERE), str(STAGE)]
import FreeCAD as App
import Part
from lib.cad_build import leaves, COLORS
from lib.evidence import read, write, sha
from detail_render import shaded_detail

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
out = a.output.resolve()
out.mkdir(parents=True, exist_ok=True)
pump_dir = HERE/'engine_oil_pump_mounting_study'
parent_dir = HERE/'engine_water_pump_connections_study'
r, pr = read(pump_dir/'report.json'), read(parent_dir/'report.json')
native, parent = pump_dir/r['native_file'], parent_dir/pr['native_file']
assert sha(native) == r['native_sha256'] and sha(parent) == pr['native_sha256']
doc, pdoc = App.openDocument(str(parent)), App.openDocument(str(native))
try:
    inverse = doc.TankLibertyEngine.getGlobalPlacement().inverse()
    placement = App.Placement(App.Vector(r['controls']['pump_axis_x'], 0,
                                        r['controls']['pump_mount_z']), App.Rotation())
    cut = Part.makeBox(480, 145, 530, App.Vector(1010, 0, -420))
    COLORS.update(ContextCase=(.60, .65, .63), ContextWater=(.42, .66, .76),
                  ContextOil=(.80, .66, .42), ContextFloor=(.77, .36, .35),
                  ContextDrive=(.59, .61, .67))
    items = []

    def add(name, shape, color):
        if not shape.BoundBox.intersect(cut.BoundBox):
            return
        displayed = shape.common(cut)
        if displayed.Solids:
            items.append(dict(shape=displayed, target=SimpleNamespace(Shape=displayed),
                              definition=name, system=color, representation='assembly'))

    for row in leaves(doc.Root):
        name = row['id']
        if name == 'EngineCase_lower':
            color = 'ContextCase'
        elif name.startswith('EngineWaterPump_'):
            color = 'ContextWater'
        elif name.startswith('EngineLowerDrive_'):
            color = 'ContextDrive'
        elif name.startswith('hull_floor_'):
            color = 'ContextFloor'
        else:
            continue
        shape = row['shape'].copy()
        shape.Placement = inverse.multiply(shape.Placement)
        add(name, shape, color)
    for row in r['occurrences']:
        link = pdoc.getObject(row['name'])
        frame = pdoc.getObject(row['assembly']).getGlobalPlacement().multiply(link.LinkPlacement)
        shape = link.LinkedObject.Shape.copy()
        shape.Placement = placement.multiply(frame).multiply(shape.Placement)
        add(row['name'], shape, 'ContextOil')
    for name, direction in [('installation_section', (0, -1, 0)),
                            ('installation_cutaway', (.7, -1, .45))]:
        shaded_detail(items, out/(name+'.svg'), direction,
                      'Rejected fit | oil pump (gold), water pump (blue), floor (red)', .08)
        print('rendered', name, flush=True)
    write(out/'render_receipt.json', dict(pump_native_sha256=sha(native),
          parent_native_sha256=sha(parent), renderer_sha256=sha(Path(__file__)),
          images={f.name:sha(f) for f in out.glob('installation_*.png')},
          display_cut_engine_coordinates=dict(x=[1010,1490], y=[0,145], z=[-420,110]),
          source_documents_modified=False, installation_qualified=False))
finally:
    App.closeDocument(pdoc.Name)
    App.closeDocument(doc.Name)
