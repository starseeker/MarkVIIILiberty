"""Saved coupled mechanism views and unchanged source projections."""
import argparse
import os
from pathlib import Path
from types import SimpleNamespace
from control_rebuild_io_v2 import *
from lib.camera_review import validate_native_bindings
from lib.visual_review import shaded, COLORS

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True)
s=Saved(p.parse_args().candidate);out=s.folder/'visual01';out.mkdir(exist_ok=False)
a=Saved((ROOT/s.report['details']['retained_development_native']).parent)
validate_native_bindings(dict(native_file=str(s.native),render_occurrences=list(s.rows),landmarks=[]),s.manifest)
os.environ['MPLCONFIGDIR']=str(ROOT/'.work/coupled-station-20260927/matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

COLORS.update(StationSteel=(.49,.60,.54),StationSeat=(.38,.25,.16),StationSupport=(.61,.46,.28),
    StationControls=(.36,.48,.67),StationHardware=(.53,.55,.58),StationFloor=(.69,.73,.66),StationClutch=(.76,.50,.24))
cache={}
def world(n):
    if n not in cache:cache[n]=s.world(n)
    return cache[n]


def item(n):
    row=s.rows[n]
    system='StationControls'
    if n in ['DriverSeatCushion','DriverSeatBackPadding']:system='StationSeat'
    elif n=='DriverSeatFrame':system='StationSteel'
    elif n.endswith(('Stay','SupportPlate','SupportAngle')):system='StationSupport'
    elif n.startswith('DriverSeat') or 'SupportMount' in n:system='StationHardware'
    elif n=='DriverClutchOperatingLever':system='StationClutch'
    return dict(id=n,definition=row['definition'],shape=world(n),target=SimpleNamespace(Shape=s.definition(row['definition'])),representation='assembly',system=system)


local=sorted(set(s.report['details']['rigid_groups']['DriverMechanism']['names'])|
    {n for n in s.rows if n.startswith('DriverSeat') or n.startswith('Driver') and 'Support' in n})
floors=[]
window=Part.makeBox(1400,950,1600,App.Vector(6800,-475,500))
for n in ['hull_floor_1','hull_floor_2']:
    q=world(n).common(window)
    floors.append(dict(id='Display_'+n,definition='Display_'+n,shape=q,target=SimpleNamespace(Shape=q),representation='assembly',system='StationFloor'))
shell=['hull_front_slope','upper_driver_front','upper_driver_roof','upper_port_driver_side','upper_starboard_driver_side']
shell=[n for n in shell if n in s.rows]
shaded([item(n) for n in local]+floors,out/'isometric.svg',(1,1,.65),
    'Coupled driver/seat candidate | wireframe bow; conditional clutch bend',context=[item(n) for n in shell],canvas=(1700,1200))
detail=[n for n in local if n not in ['DriverSeatCushion','DriverSeatBackPadding'] and 'UpholsteryNail' not in n]
shaded([item(n) for n in detail]+floors,out/'connections.svg',(-1,1,.3),
    'Complete connections | upholstery hidden; amber clutch blade profile is provisional',canvas=(1700,1200))

reg=read(C/'driver_redo01/mount_registration01.json')
oldrender=read(a.folder/'render_receipt.json');coef=complex(*oldrender['side_registration']['complex_scale'])
anchors=reg['construction_picks'];pa,pb=[complex(*anchors[k]) for k in ['main_shaft_starboard_tip_px','main_shaft_port_tip_px']]
span=reg['printed_main_shaft_length_mm'];main=App.Vector(*s.report['details']['main_world_mm'])
plan_source=ROOT/reg['source_image'];side_source=ROOT/oldrender['side_source']
plan=Image.open(plan_source).convert('RGB')
side=Image.open(side_source).crop((0,0,590,650)).transpose(Image.Transpose.ROTATE_90).convert('RGB')
old=a.definition(a.rows['DriverClutchOperatingLever']['definition']);old.Placement=pose(s.rows['DriverClutchOperatingLever']['frame'])
fig,axes=plt.subplots(1,2,figsize=(14,7),dpi=150)
for ax,view,im in zip(axes,['plan','side'],[plan,side]):
    ax.imshow(im)
    for q,color in [(old,'#267348'),(world('DriverClutchOperatingLever'),'#b46620')]:
        for edge in q.Edges:
            pts=[]
            for v in edge.discretize(Deflection=.7):
                delta=v-main
                px=(pa+pb)/2+complex(delta.y,delta.x)*(pb-pa)/span if view=='plan' else complex(315,322)-coef*complex(delta.x,delta.z)
                pts.append([px.real,px.imag])
            if len(pts)>1:ax.plot(*zip(*pts),color=color,linewidth=.9,alpha=.8)
    ax.set_xlim(85,330) if view=='plan' else ax.set_xlim(45,350)
    ax.set_ylim(490,375) if view=='plan' else ax.set_ylim(410,100)
    ax.set_aspect('equal');ax.set_title('Fixed SNL6 local plan' if view=='plan' else 'Fixed HB113 local side')
fig.suptitle('M772 profile hypothesis | complete reach, hub, bell and grip retained')
fig.text(.04,.02,'Green: inherited straight splay. Amber: later outward set. Side silhouette and grip endpoint remain unchanged; the middle plan profile differs.\nMaximum60mm section setback projects to19.87px in plan. This is a documented interface hypothesis, not a source-validated bend.',fontsize=10)
fig.tight_layout(rect=(0,.11,1,.95));fig.savefig(out/'clutch_source_comparison.png');plt.close(fig)

cal=read(H.parents[1]/'data/calibrations.json')['snl_2'];params=read(H.parents[1]/'data/parameters.json')
scale=[cal['axes'][v]['sign']*params[cal['axes'][v]['span_parameter']]['value']/abs(cal['axes'][v]['pixels'][1]-cal['axes'][v]['pixels'][0]) for v in ['x','z']]
source=ROOT/cal['image'];im=Image.open(source).convert('RGB')
fig,ax=plt.subplots(figsize=(12,9),dpi=150);ax.imshow(im)
shown=['DriverPortSupportPlate','DriverSeatPortSupportAngle','DriverSeatPortFrontStay','DriverSeatPortRearStay',
       'DriverMainShaft','DriverSwingShaft','PortDriverOperatingHandle','DriverClutchOperatingLever',
       'DriverSeatFrame','hull_front_slope','hull_floor_1','hull_floor_2']
for n in shown:
    color='#93602c' if 'Seat' in n or 'Support' in n else '#3f8051' if n.startswith('hull') else '#2d5f9e'
    for edge in world(n).Edges:
        pts=[[cal['datum_pixel'][0]+v.x/scale[0],cal['datum_pixel'][1]+v.z/scale[1]] for v in edge.discretize(Deflection=1.)]
        if len(pts)>1:ax.plot(*zip(*pts),color=color,linewidth=.7,alpha=.8)
ax.set_xlim(315,585);ax.set_ylim(500,255);ax.set_aspect('equal');ax.set_xlabel('Fixed SNL2 pixels');ax.set_ylabel('Fixed SNL2 pixels')
ax.set_title('Connected candidate at tentative shaft pair | unchanged section calibration')
fig.text(.06,.025,'Projected mechanism edges remain visible through the source side plate for diagnosis.\nShaft identities, side-plate outline, handle configuration and seat curves remain reconstruction hypotheses.',fontsize=10)
fig.tight_layout(rect=(0,.09,1,.97));fig.savefig(out/'source_section.png');plt.close(fig)
write(out/'render_receipt.json',dict(native_sha256=sha(s.native),renderer_sha256=sha(Path(__file__)),
    source_camera_refitted=False,geometry_integrated=False,isometric_occurrences=local,wireframe_context=shell,
    connection_occurrences=detail,section_occurrences=shown,display_only_floor_crop_mm=[6800,-475,500,8200,475,2100],
    source_sha256=sha(source),plan_source_sha256=sha(plan_source),side_source_sha256=sha(side_source),
    registration_sha256=sha(C/'driver_redo01/mount_registration01.json'),
    inherited_side_registration_sha256=sha(a.folder/'render_receipt.json'),
    images={p.name:sha(p) for p in out.glob('*.png')}))
print('Four coupled station views saved.',flush=True)
