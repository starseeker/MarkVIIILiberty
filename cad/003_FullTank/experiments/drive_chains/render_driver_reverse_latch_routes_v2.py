"""Inspect nonphysical latch-route witnesses with saved receiving geometry."""
import argparse
from pathlib import Path
from types import SimpleNamespace
from control_rebuild_io_v2 import App, Part, ROOT, Saved, pose, read, write, sha
from lib.visual_review import shaded
from lib.cad_build import COLORS

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--probe', type=Path, required=True)
args = parser.parse_args()
folder = args.probe.resolve()
report = read(folder / 'report.json')
seed = Saved(ROOT / report['controls']['seed'])
assert sha(seed.native) == report['native_sha256']
parent = Saved((ROOT / seed.report['parent_native']).parent)
assert sha(parent.native) == report['parent_native_sha256']
out = folder / 'visual02'
out.mkdir(exist_ok=False)
COLORS.update(Blade=(.40, .56, .43), Quadrant=(.33, .52, .67),
              Context=(.50, .53, .56), Route=(.75, .35, .75), Rejected=(.8, .25, .2))


def native_item(source, name, system):
    row = source.rows[name]
    return dict(id=name, definition=row['definition'], shape=source.world(name),
                target=SimpleNamespace(Shape=source.definition(row['definition'])),
                system=system, representation='assembly')


def witness(name, path, digest, system):
    assert sha(path) == digest
    shape = Part.Shape()
    shape.read(str(path))
    return dict(id=name, definition=name, shape=shape, target=SimpleNamespace(Shape=shape),
                system=system, representation='assembly')


items = [native_item(seed, 'DriverReverseOperatingLever', 'Blade'),
         native_item(seed, 'DriverReverseQuadrant', 'Quadrant')]
context_names = ['DriverSeatStarboardFrontStay', 'DriverSeatStarboardFrontStayLowerBolt']
context = [native_item(parent, name, 'Context') for name in context_names]
tooth = report['detent_tooth']
tooth_item = witness('NonphysicalDetentTooth', folder / tooth['brep'], tooth['sha256'], 'Route')
selected = next(row for row in report['cases'] if row['x_offset_mm'] == 20)
paths = [witness('NonphysicalRod', folder / selected['rod_brep'], selected['rod_brep_sha256'], 'Route'),
         witness('NonphysicalPawlRoute', folder / selected['offset_brep'], selected['offset_brep_sha256'], 'Route'),
         tooth_item]
shaded(items + paths, out / 'isometric.svg', (1, -1, .7),
       'Latch route probe | purple witnesses are not finished parts | trigger, guide and attachments pending',
       context=context)

# Clip only the display at the detent; preserve every physical source artifact.
frame = pose(report['lever_frame'])
box = Part.makeBox(85, 70, 110, App.Vector(-40, -60, 245))
box.Placement = frame
detail = []
for item in items + paths + context:
    shape = item['shape'].common(box)
    if shape.Faces:
        detail.append(dict(id=item['id'] + 'Detail', definition=item['id'] + 'Detail',
                           shape=shape, target=SimpleNamespace(Shape=shape),
                           system=item['system'], representation='assembly'))
shaded(detail, out / 'detent_detail.svg', (1, -1, .7),
       'Actual saved detent and hypothetical offset path | display cuts only | guide and receiving holes pending')

failed_paths = []
for index, row in enumerate(report['cases']):
    if row['corridor_clear']:
        continue
    failed_paths.append(witness('RejectedRod%d' % index, folder / row['rod_brep'],
                                row['rod_brep_sha256'], 'Rejected'))
shaded(items + context + failed_paths, out / 'failed_routes.svg', (1, -1, .7),
       'Rejected nonphysical rod routes | actual intersections retained | receiving parts unchanged')
write(out / 'render_receipt.json', dict(
    native_sha256=sha(seed.native), parent_native_sha256=sha(parent.native),
    probe_sha256=sha(folder / 'report.json'), renderer_sha256=sha(__file__),
    shown_context=context_names, images={p.name: sha(p) for p in out.glob('*.png')},
    geometry_integrated=False, physical_parts_created=False, source_camera_refitted=False,
    scope='Saved BRep witnesses and actual retained receivers. Display only; no latch part or movement acceptance.',
))
print('Rendered three route-probe views.', flush=True)
