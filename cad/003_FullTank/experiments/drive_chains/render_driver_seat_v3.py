"""Depth-buffered seat views; reuse the already rendered fixed source section."""
import argparse
import shutil
from pathlib import Path
from types import SimpleNamespace
from control_rebuild_io_v2 import *
from lib.visual_review import shaded, COLORS
from lib.camera_review import validate_native_bindings

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);a=p.parse_args()
s=Saved(a.candidate);out=s.folder/'visual03';out.mkdir(exist_ok=False)
prior=read(s.folder/'visual02/render_receipt.json')
assert prior['native_sha256']==sha(s.native)
assert sha(s.folder/'visual02/source_section.png')==prior['images']['source_section.png']
validate_native_bindings(dict(native_file=str(s.native),render_occurrences=s.report['new_occurrences'],landmarks=[]),s.manifest)
COLORS.update(SeatSteel=(.5,.63,.57),SeatUpholstery=(.38,.25,.16),SeatBearing=(.67,.5,.27),SeatFastener=(.56,.57,.6))
items=[]
for n in s.report['new_occurrences']:
    row=s.rows[n];q=s.definition(row['definition'])
    system='SeatSteel' if n=='DriverSeatFrame' else 'SeatUpholstery' if n in ['DriverSeatCushion','DriverSeatBackPadding'] else 'SeatBearing' if 'Bearing' in n and 'Rivet' not in n else 'SeatFastener'
    items.append(dict(id=n,definition=row['definition'],shape=s.world(n),target=SimpleNamespace(Shape=q),representation='assembly',system=system))
for name,direction in [('isometric',(1,1,.7)),('underside',(1,1,-.65))]:
    shaded(items,out/(name+'.svg'),direction,'M791 seat-side prototype | support connections unfinished',canvas=(1400,1000))
shutil.copy2(s.folder/'visual02/source_section.png',out/'source_section.png')
write(out/'render_receipt.json',dict(native_sha256=sha(s.native),renderer_sha256=sha(Path(__file__)),
    depth_buffer=True,source_camera_refitted=False,geometry_integrated=False,
    reused_source_section_receipt_sha256=sha(s.folder/'visual02/render_receipt.json'),
    visual_renderer_sha256=sha(H.parents[1]/'lib/visual_review.py'),raster_sha256=sha(H.parents[1]/'lib/raster.c'),
    seat_occurrences=s.report['new_occurrences'],images={p.name:sha(p) for p in out.glob('*.png')}))
print('Depth-buffered seat views complete',flush=True)
