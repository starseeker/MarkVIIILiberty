"""Render actual saved high-control trial with inherited context and fixed source registration."""
import argparse
from pathlib import Path
from types import SimpleNamespace
from control_rebuild_io_v2 import *
from lib.camera_review import validate_native_bindings
from lib.cad_build import COLORS
from lib.visual_review import shaded
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args()
s=Saved(a.candidate);parent=Saved((ROOT/s.report['parent_native']).parent)
validate_native_bindings(dict(native_file=str(s.native),render_occurrences=list(s.rows),landmarks=[]),s.manifest)
COLORS.update(New=(.28,.48,.66),Casting=(.43,.57,.44),Context=(.68,.69,.66),Spring=(.75,.61,.37),Rod=(.34,.49,.67),Floor=(.75,.75,.7))
items=[]
clip=Part.makeBox(1250,720,610,App.Vector(1820,-360,510))
selected=set(s.rows)|{n for n in parent.rows if n.startswith('ClutchSupport_') or n.startswith('ClutchThrowout_') or n.startswith('PortHighSpeedBrake') or n.startswith('StarboardHighSpeedBrake')}
for n in sorted(selected):
    provider=s if n in s.rows else parent
    if n=='hull_floor_7':continue
    shape=provider.world(n)
    if shape.BoundBox.XMin>3070:continue
    shape=shape.common(clip)
    if not shape.Faces:continue
    system='Casting' if 'Bracket' in n or 'Channel' in n else 'Spring' if 'Spring' in n else 'Rod' if 'Rod' in n else 'New' if n in s.rows else 'Context'
    items.append(dict(id=n,shape=shape,target=SimpleNamespace(Shape=shape),definition=n,system=system,representation='assembly'))
shaded(items,s.folder/'isometric.svg',(-1,-1,.8),'High-speed control route trial | revised receivers and source-constrained rear eyes')
shaded(items,s.folder/'plan.svg',(0,0,1),'Rear controls | continuous M575 routes and inherited clutch interfaces')
shaded(items,s.folder/'side.svg',(0,-1,.04),'Rear controls | source-derived rear eye height; provisional floor-supported castings')
# Source side-registration overlay: silhouette samples from actual saved revised
# levers, compared to the same registration. Pin pick is a construction input.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
reg=read(H/'transmission_controls_study/channel_local_registration01.json')
im=Image.open(ROOT/reg['source_image']);fig,ax=plt.subplots(figsize=(11,7));ax.imshow(im)
scale=reg['pixels_per_mm'];cx,cy=reg['center_px'];ox,_,oz=reg['axis_world_mm']
for n in ['PortHighSpeedBrakeLeverLeft','PortHighSpeedBrakeControlFork','PortHighSpringBracket']:
    shape=s.world(n)
    for e in shape.Edges:
        ps=e.discretize(Deflection=.3)
        ax.plot([cx-(v.x-ox)*scale for v in ps],[cy-(v.z-oz)*scale for v in ps],color='#0072b2',lw=.7,alpha=.8)
ax.set_xlim(1300,1680);ax.set_ylim(975,680);ax.set_title('Fixed local SNL6 registration; blue = revised CAD. Rear eye is a construction pick.');ax.axis('off');fig.tight_layout();fig.savefig(s.folder/'source_overlay.png',dpi=160);plt.close(fig)
write(s.folder/'render_receipt.json',dict(native_sha256=sha(s.native),renderer_sha256=sha(Path(__file__)),manifest_sha256=sha(s.folder/'isolated/manifest.json'),images={n:sha(s.folder/n) for n in ['isometric.png','plan.png','side.png','source_overlay.png']},source_camera_refitted=False,source_registration_sha256=sha(H/'transmission_controls_study/channel_local_registration01.json'),scope='Actual saved parts; clipping for local view. Rear pin now construction input. Exact casting/routing still provisional.'))
