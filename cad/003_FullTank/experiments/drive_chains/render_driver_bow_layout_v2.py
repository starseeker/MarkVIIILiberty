"""Saved coupled geometry: fixed section comparison and transparent local views."""
import argparse
import os
from pathlib import Path
from control_rebuild_io_v2 import *

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);a=p.parse_args()
s=Saved(a.candidate);parent=Saved((ROOT/s.report['parent_native']).parent)
out=s.folder/'visual02';out.mkdir(exist_ok=False)
os.environ['MPLCONFIGDIR']=str(ROOT/'.work/driver-layout-20260927/matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image

world={n:s.world(n) for n in s.rows}
cal=read(H.parents[1]/'data/calibrations.json')['snl_2'];params=read(H.parents[1]/'data/parameters.json')
scale=[cal['axes'][v]['sign']*params[cal['axes'][v]['span_parameter']]['value']/abs(cal['axes'][v]['pixels'][1]-cal['axes'][v]['pixels'][0]) for v in ['x','z']]
source=ROOT/cal['image'];im=Image.open(source).convert('RGB')
pixel=lambda p:[cal['datum_pixel'][0]+p.x/scale[0],cal['datum_pixel'][1]+p.z/scale[1]]


def edges(ax,q,color,width=.6):
    for e in q.Edges:
        pts=[pixel(v) for v in e.discretize(Deflection=1.)]
        if len(pts)>1:ax.plot(*zip(*pts),color=color,linewidth=width,alpha=.85)


shown=['DriverMainShaft','DriverSwingShaft','DriverPortSupportPlate','PortDriverOperatingHandle',
       'PortDriverOperatingFulcrum','PortDriverHighSelector','PortDriverLowSelector',
       'PortDriverLowSuspension','PortDriverLowConnecting','PortDriverLowBrake','PortHighDriverSwingLink',
       'PortDriverHighShortRod','PortDriverLowRod','PortDriverHighFrontRod','DriverClutchOperatingLever']
shell=['hull_front_slope','hull_floor_1','hull_floor_2','upper_driver_front','upper_driver_roof','upper_port_driver_side']
fig,axes=plt.subplots(2,1,figsize=(14,14),dpi=150)
for index,ax in enumerate(axes):
    ax.imshow(im)
    for name in shell:edges(ax,world[name],'#388251',.75)
    for name in shown:edges(ax,world[name] if index else parent.world(name),'#2355a1',.8)
    ax.set_xlim(300,670);ax.set_ylim(535,230);ax.set_aspect('equal');ax.set_xlabel('SNL2 image pixels');ax.set_ylabel('SNL2 image pixels')
    ax.set_title('Coupled driver-height hypothesis, complete stock retained' if index else 'Corrected shell with previous driver placement (known conflicts)')
fig.suptitle('Fixed whole-tank section registration | no camera refit',fontsize=16)
fig.text(.06,.018,'Green: corrected shell. Blue: actual saved driver geometry. Source depicts a potentially different control state.\nThe lower candidate fits mechanically; shaft height, grip length datum and source proportions remain historically unresolved.',fontsize=11)
fig.subplots_adjust(bottom=.11,top=.95,hspace=.20);fig.savefig(out/'section_comparison.png');plt.close(fig)


def render(path,names,detail=False):
    fig=plt.figure(figsize=(15,11),dpi=150);ax=fig.add_subplot(111,projection='3d');ax.set_proj_type('ortho')
    boxes=[]
    for name in names:
        q=world[name];role=s.report['specs'][name]['role']
        if detail and name in ['hull_floor_1','hull_floor_2']:
            rear=s.report['details']['swing_world_mm'][0];main=s.report['details']['main_world_mm'][0]
            # Clip only the display copy to the labeled local-detail window.
            q=q.common(Part.makeBox(main-rear+300,750,670,App.Vector(rear-150,-375,530)))
        if role=='bow_plate':color='#82ab89';alpha=.20
        elif role=='support':color='#a17843';alpha=1.
        elif role.startswith('mount_'):color='#6e7178';alpha=1.
        elif role=='receiver':color='#858d87';alpha=.45
        else:color='#526e9a';alpha=1.
        vertices,triangles=q.tessellate(1.2 if detail else 2.0);xyz=[list(v) for v in vertices]
        collection=Poly3DCollection([[xyz[i] for i in tri] for tri in triangles],facecolor=color,edgecolor='none',alpha=alpha)
        ax.add_collection3d(collection)
        for e in q.Edges:
            if len(e.Vertexes)==2 and e.Length>30:
                pts=[list(v) for v in e.discretize(Deflection=2.)]
                ax.plot(*zip(*pts),color='#243429',linewidth=.4,alpha=.24)
        b=q.BoundBox;boxes.extend([[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]])
    if detail:
        rear=s.report['details']['swing_world_mm'][0];main=s.report['details']['main_world_mm'][0]
        lo=[rear-150,-375,530];hi=[main+150,375,1200]
    else:lo=[min(v[i] for v in boxes) for i in range(3)];hi=[max(v[i] for v in boxes) for i in range(3)]
    ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[1],hi[1]);ax.set_zlim(lo[2],hi[2]);ax.set_box_aspect([hi[i]-lo[i] for i in range(3)])
    ax.view_init(elev=26,azim=130);ax.set_xlabel('X forward (mm)');ax.set_ylabel('Y (mm)');ax.set_zlabel('Z (mm)')
    ax.set_title('Folded supports and mounting stacks | floor cropped to detail window' if detail else 'Coupled bow/driver hypothesis | transparent local shell',fontsize=15)
    fig.text(.06,.025,'Static development hypothesis; no historical placement or operating-motion acceptance.\nBrown: revised supports. Blue/grey: complete retained control and mounting stock. Green: conditional bow/floor reconstruction.',fontsize=11)
    fig.subplots_adjust(left=.01,right=.99,bottom=.08,top=.94);fig.savefig(path);plt.close(fig)

iso=[n for n in world if not n.endswith('roof_track_rear') and n!='hull_roof_aft_upper']
render(out/'isometric.png',iso)
detail=[n for n in world if s.report['specs'][n]['role'] in ['support','mount_bolt','mount_lock','mount_nut'] or n in ['DriverMainShaft','DriverSwingShaft','hull_floor_1','hull_floor_2']]
render(out/'mounting_detail.png',detail,True)
write(out/'render_receipt.json',dict(native_sha256=sha(s.native),parent_native_sha256=sha(parent.native),renderer_sha256=sha(Path(__file__)),
    source_sha256=sha(source),calibration_file_sha256=sha(H.parents[1]/'data/calibrations.json'),source_camera_refitted=False,
    render_only_floor_crop='Mounting detail: X swing-150 to main+150, Y +/-375, Z530..1200mm. Native and exchange geometry unchanged.',section_occurrences=shown+shell,isometric_occurrences=iso,mounting_occurrences=detail,
    source_comparison_limit='Whole-figure conditional registration and provisional configuration transfer. SNL6 local relative geometry/camera remains unchanged because the 72-part driver unit is translated rigidly; earlier 47–49px grip discrepancies remain.',
    images={p.name:sha(p) for p in out.glob('*.png')},geometry_integrated=False,historical_geometry_qualified=False))
print('Rendered three saved-geometry views',flush=True)
