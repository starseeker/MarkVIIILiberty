"""Render saved bow candidate and baseline in the unchanged SNL2 registration."""
import argparse
import math
import os
from pathlib import Path
from control_rebuild_io_v2 import *

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,required=True)
a=p.parse_args();folder=a.candidate.resolve();r=read(folder/'report.json')
out=folder/'visual01';out.mkdir(exist_ok=False)
os.environ['MPLCONFIGDIR']=str(ROOT/'.work/bow-correction-20260927/matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image

native=folder/r['native_file'];assert sha(native)==r['native_sha256']
doc=App.openDocument(str(native));world={}
for name,row in r['occurrences'].items():
    link=doc.getObject(name);s=link.LinkedObject.Shape.copy();s.Placement=link.LinkPlacement;world[name]=s
App.closeDocument(doc.Name)
standard_path=H/'transmission_brake_front_study/trial01/standard_context_manifest.json'
standard=read(standard_path);oldrows={q['name']:q for q in standard['occurrences']}
params=read(H.parents[1]/'data/parameters.json')
cal=read(H.parents[1]/'data/calibrations.json')['snl_2']
scale=[cal['axes'][a]['sign']*params[cal['axes'][a]['span_parameter']]['value']/abs(cal['axes'][a]['pixels'][1]-cal['axes'][a]['pixels'][0]) for a in ['x','z']]
datum=cal['datum_pixel']
pixel=lambda p:[datum[0]+p.x/scale[0],datum[1]+p.z/scale[1]]
source=ROOT/cal['image'];im=Image.open(source).convert('RGB')


def edges(ax,s,color,width=0.8):
    for e in s.Edges:
        pts=[pixel(v) for v in e.discretize(Deflection=1.)]
        if len(pts)>1:ax.plot(*zip(*pts),color=color,linewidth=width,alpha=.85)


display=[n for n,row in r['occurrences'].items() if row['candidate'] and
         (n.startswith('upper_') or n in ['hull_front_slope','hull_floor_1','hull_floor_2','hull_port_roof_driver'])]
fig,axes=plt.subplots(2,1,figsize=(15,15),dpi=150)
for ax,new in zip(axes,[False,True]):
    ax.imshow(im)
    for name in display:
        if new:s=world[name]
        else:
            row=oldrows[name];entry=standard['definitions'][row['definition']]
            assert sha(entry['brep_path'])==entry['brep_sha256']
            s=Part.Shape();s.read(entry['brep_path']);s.Placement=pose(row['frame'])
        edges(ax,s,'#007656' if new else '#b33128')
    for name in ['PortDriverOperatingHandle','PortDriverOperatingFulcrum','DriverMainShaft','DriverSwingShaft']:
        edges(ax,world[name],'#2451a4',1.)
    ax.set_xlim(290,1045);ax.set_ylim(535,45);ax.set_aspect('equal')
    ax.set_title('Inclusive-length bow hypothesis | saved candidate' if new else 'Baseline | saved standard shell',fontsize=15)
    ax.set_xlabel('SNL2 image pixels');ax.set_ylabel('SNL2 image pixels')
fig.suptitle('Same conditional whole-tank calibration; no camera refit or driver relocation',fontsize=16)
fig.text(.07,.02,'Red: baseline plates. Green: proposed plates. Blue: unchanged driver controls.\nInclusive length is an interpretation under review. Bow/floor route and joins remain approximate; control interference is unresolved.',fontsize=11)
fig.subplots_adjust(bottom=.07,top=.95,hspace=.15)
fig.savefig(out/'section_comparison.png');plt.close(fig)

fig=plt.figure(figsize=(15,11),dpi=150);ax=fig.add_subplot(111,projection='3d');ax.set_proj_type('ortho')
bb=[]
for name,s in world.items():
    # Two long rear roof panels are included in source/context checks but make
    # the localized construction view hard to read. State the view's omission.
    if name.endswith('roof_track_rear') or name=='hull_roof_aft_upper':continue
    row=r['occurrences'][name]
    if row['group']=='RetainedDriverControls':color='#ca6a1c';alpha=1.
    elif row['group']=='RetainedStandardContext':color='#898b93';alpha=.45
    elif name.startswith('upper_'):color='#64a4a0';alpha=.38
    else:color='#719666';alpha=.32
    vs,ts=s.tessellate(2.)
    xyz=[list(v) for v in vs]
    coll=Poly3DCollection([[xyz[i] for i in t] for t in ts],facecolor=color,edgecolor='none',alpha=alpha)
    ax.add_collection3d(coll)
    for edge in s.Edges:
        if len(edge.Vertexes)==2 and edge.Length>50:
            pts=[list(v) for v in edge.discretize(Deflection=3.)]
            ax.plot(*zip(*pts),color='#2d453e',alpha=.18,linewidth=.35)
    b=s.BoundBox;bb.extend([[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]])
lo=[min(p[i] for p in bb) for i in range(3)];hi=[max(p[i] for p in bb) for i in range(3)]
ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[1],hi[1]);ax.set_zlim(lo[2],hi[2]);ax.set_box_aspect([hi[i]-lo[i] for i in range(3)])
ax.view_init(elev=25,azim=130);ax.set_xlabel('X forward (mm)');ax.set_ylabel('Y (mm)');ax.set_zlabel('Z (mm)')
ax.set_title('Bow/enclosure hypothesis | transparent plates, unchanged controls',fontsize=15)
fig.text(.07,.035,'Diagnostic assembly, not integrated or accepted. Two rear track roofs and aft roof strip omitted from this local view only.\nAll 40 proposed plates remain present in the native/STEP files and physical-context audit.',fontsize=11)
fig.subplots_adjust(bottom=.08,top=.92,left=.01,right=.99);fig.savefig(out/'isometric.png');plt.close(fig)
lower=App.Vector(*[r['joint_datums']['outer']['bow_lower'][0],0,r['joint_datums']['outer']['bow_lower'][1]])
upper=App.Vector(*[r['joint_datums']['outer']['bow_upper'][0],0,r['joint_datums']['outer']['bow_upper'][1]])
write(out/'render_receipt.json',dict(native_sha256=sha(native),renderer_sha256=sha(Path(__file__)),report_sha256=sha(folder/'report.json'),
    calibration_file_sha256=sha(H.parents[1]/'data/calibrations.json'),source_sha256=sha(source),
    source_camera_refitted=False,source_wall_upper_comparison_px=[404,240],candidate_wall_upper_px=pixel(upper),
    wall_upper_discrepancy_px=math.dist(pixel(upper),[404,240]),
    source_comparison_note='Source wall point was considered in choosing the dimension-scope hypothesis; this is a selection diagnostic, not independent validation.',
    upward_rake_degrees=math.degrees(math.atan2(upper.z-lower.z,upper.x-lower.x)),
    rendered_section_occurrences=display,images={p.name:sha(p) for p in out.glob('*.png')},historical_geometry_qualified=False))
print('Rendered unchanged registration and transparent local isometric',flush=True)
