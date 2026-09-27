"""Depth-buffered connected seat views and unchanged source-section projection."""
import argparse
import os
from pathlib import Path
from types import SimpleNamespace
from control_rebuild_io_v2 import *
from lib.camera_review import validate_native_bindings
from lib.visual_review import shaded, COLORS

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,required=True)
a=p.parse_args()
s=Saved(a.candidate)
out=s.folder/'visual01'
out.mkdir(exist_ok=False)
validate_native_bindings(dict(native_file=str(s.native),render_occurrences=list(s.rows),landmarks=[]),s.manifest)
os.environ['MPLCONFIGDIR']=str(ROOT/'.work/seat-support-20260927/matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

COLORS.update(SeatSteel=(.5,.63,.57),SeatUpholstery=(.38,.25,.16),
              SeatBearing=(.67,.5,.27),SeatFastener=(.56,.57,.6),
              SeatSupport=(.60,.45,.26),SeatAngle=(.42,.58,.44),
              DriverControls=(.37,.47,.64),LocalFloor=(.69,.73,.66))
names=[n for n in s.rows if n.startswith('DriverSeat') or n.startswith('Driver') and 'Support' in n]
controls=[n for n in s.rows if n.startswith(('Driver','PortDriver','StarboardDriver','PortHighDriver','StarboardHighDriver')) and n not in names]
# Long rods are still native and audited; this close view limits its contents to
# the connected local unit rather than allowing them to dominate the camera box.
controls=[n for n in controls if not any(v in n for v in ['FrontRod','RodSpring','RodWasher'])]
world={n:s.world(n) for n in set(names+controls+['hull_floor_1','hull_floor_2'])}


def system(name):
    if name in ['DriverSeatCushion','DriverSeatBackPadding']:
        return 'SeatUpholstery'
    if name=='DriverSeatFrame':
        return 'SeatSteel'
    if 'Bearing' in name and 'Rivet' not in name:
        return 'SeatBearing'
    if name.endswith('Stay') or name.endswith('SupportPlate'):
        return 'SeatSupport'
    if name.endswith('SupportAngle'):
        return 'SeatAngle'
    return 'SeatFastener' if name in names else 'DriverControls'


def items(selected,floors=False):
    result=[]
    for name in selected:
        row=s.rows[name]
        result.append(dict(id=name,definition=row['definition'],shape=world[name],
            target=SimpleNamespace(Shape=s.definition(row['definition'])),representation='assembly',system=system(name)))
    if floors:
        window=Part.makeBox(760,760,600,App.Vector(7080,-380,540))
        for name in ['hull_floor_1','hull_floor_2']:
            q=world[name].common(window)
            # Unique identity-frame rendering copy; never share a world-posed
            # mesh under a canonical definition key.
            assert q.Placement.isIdentity()
            result.append(dict(id='Display_'+name,definition='Display_'+name,shape=q,
                target=SimpleNamespace(Shape=q),representation='assembly',system='LocalFloor'))
    return result


shaded(items(names+controls,True),out/'isometric.svg',(1,1,.7),
       'Connected driver seat study | actual stays, joints and separate floor angles',canvas=(1600,1200))
support_names=[n for n in names if n not in ['DriverSeatCushion','DriverSeatBackPadding'] and 'UpholsteryNail' not in n]
shaded(items(support_names+['DriverMainShaft','DriverSwingShaft'],True),out/'connections.svg',(-1,-1,.25),
       'Seat support connections | upholstery hidden for inspection only',canvas=(1600,1200))

cal=read(H.parents[1]/'data/calibrations.json')['snl_2']
params=read(H.parents[1]/'data/parameters.json')
scale=[cal['axes'][v]['sign']*params[cal['axes'][v]['span_parameter']]['value']/abs(cal['axes'][v]['pixels'][1]-cal['axes'][v]['pixels'][0]) for v in ['x','z']]
source=ROOT/cal['image'];image=Image.open(source).convert('RGB')
pixel=lambda p:[cal['datum_pixel'][0]+p.x/scale[0],cal['datum_pixel'][1]+p.z/scale[1]]
section=Part.Face(Part.makePolygon([V for V in [App.Vector(*v) for v in [(7080,0,500),(8000,0,500),(8000,0,2100),(7080,0,2100),(7080,0,500)]]]))
shown=['DriverPortSupportPlate','DriverSeatPortSupportAngle','DriverSeatPortFrontStay','DriverSeatPortRearStay',
       'DriverSeatPortFrontBearing','DriverSeatPortRearBearing','DriverMainShaft','DriverSwingShaft']
fig,axes=plt.subplots(1,2,figsize=(15,9),dpi=150)
for index,ax in enumerate(axes):
    ax.imshow(image)
    if index:
        for name in ['DriverSeatFrame','DriverSeatCushion','DriverSeatBackPadding']+shown:
            q=world[name].section(section) if name in ['DriverSeatFrame','DriverSeatCushion','DriverSeatBackPadding'] else world[name]
            color='#42669b' if name in ['DriverMainShaft','DriverSwingShaft'] else '#467851' if name.endswith('Angle') else '#93602c' if name in shown else '#784e34'
            for edge in q.Edges:
                pts=[pixel(v) for v in edge.discretize(Deflection=.8)]
                if len(pts)>1:
                    ax.plot(*zip(*pts),color=color,linewidth=.7 if name in shown else 1.4,alpha=.8)
    ax.set_xlim(420,550);ax.set_ylim(498,275);ax.set_aspect('equal')
    ax.set_xlabel('Fixed SNL2 pixels');ax.set_ylabel('Fixed SNL2 pixels')
    ax.set_title('Original source' if not index else 'Saved seat section and projected port support geometry')
fig.suptitle('Connected seat reconstruction | existing conditional section calibration, no camera refit')
fig.text(.04,.022,'Seat and lower-stay picks constrain the construction; coincidence is not independent validation. Blue shaft positions, cushion/back profiles,\nplate outlines and M788 allocation remain hypotheses. Source adjustment state and absolute control/seat relationship are unresolved.',fontsize=10)
fig.subplots_adjust(bottom=.13,top=.92);fig.savefig(out/'source_section.png');plt.close(fig)
write(out/'render_receipt.json',dict(native_sha256=sha(s.native),renderer_sha256=sha(Path(__file__)),
    depth_buffer=True,source_camera_refitted=False,geometry_integrated=False,
    isometric_occurrences=names+controls,connections_occurrences=support_names+['DriverMainShaft','DriverSwingShaft'],section_occurrences=shown,
    display_only_floor_crop_mm=[7080,-380,540,7840,380,1140],
    source_sha256=sha(source),calibration_sha256=sha(H.parents[1]/'data/calibrations.json'),parameters_sha256=sha(H.parents[1]/'data/parameters.json'),
    visual_renderer_sha256=sha(H.parents[1]/'lib/visual_review.py'),raster_sha256=sha(H.parents[1]/'lib/raster.c'),
    images={p.name:sha(p) for p in out.glob('*.png')}))
print('Three connected-seat views complete',flush=True)
