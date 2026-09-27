"""Render the saved seat prototype and compare with the unchanged SNL section."""
import argparse
import os
from pathlib import Path
from control_rebuild_io_v2 import *

p=argparse.ArgumentParser(description=__doc__); p.add_argument('--candidate', type=Path, required=True); a=p.parse_args()
s=Saved(a.candidate); out=s.folder/'visual02'; out.mkdir(exist_ok=False)
os.environ['MPLCONFIGDIR']=str(ROOT/'.work/seat-build-20260927/matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image

names=s.report['new_occurrences']; worlds={n:s.world(n) for n in names}
colors=lambda n: '#705038' if n in ['DriverSeatCushion','DriverSeatBackPadding'] else '#88a29a' if n=='DriverSeatFrame' else '#b99154' if 'Bearing' in n and 'Rivet' not in n else '#777c84'


def mesh(ax, q, color, alpha=1):
    vertices, faces=q.tessellate(.6)
    xyz=[list(v) for v in vertices]
    ax.add_collection3d(Poly3DCollection([[xyz[i] for i in face] for face in faces], facecolor=color, edgecolor='none', alpha=alpha))
    for edge in q.Edges:
        if edge.Length > 12:
            pts=[list(v) for v in edge.discretize(Deflection=1)]
            ax.plot(*zip(*pts), color='#303c37', linewidth=.45, alpha=.35)


for label, elevation, azimuth in [('isometric', 27, 35), ('underside', -22, 35)]:
    fig=plt.figure(figsize=(11,9),dpi=150); ax=fig.add_subplot(111,projection='3d'); ax.set_proj_type('ortho')
    triangles=[]; facecolors=[]
    for n in names:
        vertices,faces=worlds[n].tessellate(.6); xyz=[list(v) for v in vertices]
        triangles.extend([[xyz[i] for i in face] for face in faces]);facecolors.extend([colors(n)]*len(faces))
    ax.add_collection3d(Poly3DCollection(triangles,facecolor=facecolors,edgecolor='none'))
    boxes=[q.BoundBox for q in worlds.values()]
    lo=[min(getattr(b,v+'Min') for b in boxes)-20 for v in ['X','Y','Z']]
    hi=[max(getattr(b,v+'Max') for b in boxes)+20 for v in ['X','Y','Z']]
    ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[1],hi[1]);ax.set_zlim(lo[2],hi[2]);ax.set_box_aspect([hi[i]-lo[i] for i in range(3)])
    ax.view_init(elev=elevation,azim=azimuth);ax.set_xlabel('X forward (mm)');ax.set_ylabel('Y (mm)');ax.set_zlabel('Z (mm)')
    ax.set_title('M791 seat-side reconstruction | '+('bearing and rivet underside' if label=='underside' else 'formed frame and upholstery'))
    fig.text(.07,.025,'Four SH289E bearings; two estimated SH291X clips; eight full-stock formed rivets;21 upholstery nails.\nWidth and hidden construction remain estimates. Bearing-to-support installation is unfinished.',fontsize=10)
    fig.subplots_adjust(bottom=.13,top=.94);fig.savefig(out/(label+'.png'));plt.close(fig)

cal=read(H.parents[1]/'data/calibrations.json')['snl_2'];params=read(H.parents[1]/'data/parameters.json')
scale=[cal['axes'][v]['sign']*params[cal['axes'][v]['span_parameter']]['value']/abs(cal['axes'][v]['pixels'][1]-cal['axes'][v]['pixels'][0]) for v in ['x','z']]
source=ROOT/cal['image'];im=Image.open(source).convert('RGB')
pixel=lambda p:[cal['datum_pixel'][0]+p.x/scale[0],cal['datum_pixel'][1]+p.z/scale[1]]
fig,axes=plt.subplots(1,2,figsize=(14,8),dpi=150)
section=Part.Face(Part.makePolygon([App.Vector(*p) for p in [(7100,0,700),(8100,0,700),(8100,0,2100),(7100,0,2100),(7100,0,700)]]))
for index,ax in enumerate(axes):
    ax.imshow(im)
    if index:
        for name in ['DriverSeatFrame','DriverSeatCushion','DriverSeatBackPadding']:
            q=worlds[name].section(section)
            for edge in q.Edges:
                pts=[pixel(v) for v in edge.discretize(Deflection=.5)]
                ax.plot(*zip(*pts), color=colors(name),linewidth=1.6)
        for name in ['DriverMainShaft','DriverSwingShaft']:
            for edge in s.world(name).Edges:
                pts=[pixel(v) for v in edge.discretize(Deflection=1.)]
                ax.plot(*zip(*pts),color='#446ca0',linewidth=.6)
    ax.set_xlim(420,550);ax.set_ylim(445,275);ax.set_xlabel('Fixed SNL2 pixels');ax.set_ylabel('Fixed SNL2 pixels');ax.set_aspect('equal')
    ax.set_title('Original source section' if not index else 'Saved Y=0 seat sections; conditional shafts in blue')
fig.suptitle('Seat reconstruction against the existing conditional section registration | no camera refit')
fig.text(.055,.035,'Pan station/depth are construction fits, not independent validation. The smaller cushion and inferred back curvature\nremain approximations; complete support connections and historical shaft position are unresolved.',fontsize=11)
fig.subplots_adjust(bottom=.14,top=.91);fig.savefig(out/'source_section.png');plt.close(fig)
write(out/'render_receipt.json',dict(native_sha256=sha(s.native),renderer_sha256=sha(Path(__file__)),
    source_image=str(source.relative_to(ROOT)),source_sha256=sha(source),source_camera_refitted=False,
    calibration_sha256=sha(H.parents[1]/'data/calibrations.json'),parameters_sha256=sha(H.parents[1]/'data/parameters.json'),
    seat_occurrences=names,geometry_integrated=False,support_installation_complete=False,
    images={p.name:sha(p) for p in out.glob('*.png')}))
print('Three saved-geometry seat views rendered',flush=True)
