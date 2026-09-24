"""Compare ground and local-floor registrations without changing source pixels."""
import os
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(STAGE)]
from lib.model import load,point
from lib.evidence import read,write,sha
OUT=HERE/'engine_pump_receiver_study/registration'
os.environ['MPLCONFIGDIR']=str(OUT/'matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
data=load();cal=data['calibrations']['snl_2'];image_path=ROOT/cal['image'];im=Image.open(image_path)
r=read(OUT/'station_candidates.json');old=read(HERE/'installed_pitch_route_report.json')
s=read(HERE/'engine_pump_layout_study/source_constraints.json');selected=r['candidates']['common_horizontal_axis_mean']
origin=point(data,'snl_2',[0,0]);unit=point(data,'snl_2',[1,1]);scale=s['snl2_vertical_scale_mm_per_px']
floor=r['floor_top_world_z_mm'];checks={}
fig,axes=plt.subplots(2,1,figsize=(14,7),sharex=True,sharey=True)
for mode,ax in zip(['ground','local_floor'],axes):
    def pixel(q):
        x,z=q
        return [(x-origin[0])/(unit[0]-origin[0]),
                (z-origin[1])/(unit[1]-origin[1]) if mode=='ground' else 512-(z-floor)/scale]
    ax.imshow(im);ax.set_xlim(995,1690);ax.set_ylim(535,390)
    for title,vertices,color in [('Existing chain',old['vertices_world_xz_mm'],'#bf4b24'),
                                 ('Mean-axis trial',selected['vertices_world_xz_mm'],'#126caf')]:
        points=[pixel(p) for p in vertices+[vertices[0]]]
        ax.plot([p[0] for p in points],[p[1] for p in points],color=color,lw=1,label=title)
    floor_y=pixel([0,floor])[1];ax.plot([995,1480],[floor_y,floor_y],color='#ad2029',lw=1.3,label='Modeled floor top')
    axis=pixel(selected['transmission_axis_xz_mm']);fixed=pixel(selected['fixed_roller_pinion_axis_xz_mm'])
    ax.plot(*axis,'+',color='#126caf',markersize=9);ax.plot(*fixed,'+',color='#126caf',markersize=9)
    x,y=s['snl2_picks']['transmission_axis'];bound=s['snl2_picks']['bound_px']
    ax.errorbar(x,y,xerr=bound,yerr=bound,fmt='o',ms=3,color='#171717',label='SNL transmission pick ±3 px')
    ax.set_title('Global ground registration' if mode=='ground' else 'Local registration to the floor line',loc='left')
    ax.legend(loc='upper left',fontsize=8,ncol=2);ax.set_ylabel('Source pixel Y')
    checks[mode]=dict(transmission_axis_pixel=axis,fixed_pinion_axis_pixel=fixed,
        modeled_floor_top_pixel_y=floor_y,source_floor_line_pixel_y=512,
        transmission_pick_residual_px=[axis[0]-x,axis[1]-y],
        transmission_within_pick_box=abs(axis[0]-x)<=bound and abs(axis[1]-y)<=bound)
axes[-1].set_xlabel('Source pixel X')
fig.suptitle('SNL Plate 2 | station hypotheses: one global drawing scale does not reconcile floor and axes',fontsize=12)
fig.tight_layout();fig.savefig(OUT/'registration_comparison.png',dpi=150);plt.close(fig)
write(OUT/'source_comparison.json',dict(source_sha256=sha(image_path),
    input_hashes={str(p.relative_to(ROOT)):sha(p) for p in [OUT/'station_candidates.json',STAGE/'data/calibrations.json',STAGE/'data/parameters.json']},
    script_sha256=sha(Path(__file__)),image_sha256=sha(OUT/'registration_comparison.png'),comparisons=checks,
    interpretation=['The mean-axis trial is within the source transmission pick box only when registered locally to the floor.',
        'A uniform local-floor registration shifts the fixed roller-pinion projection too; it cannot be accepted as a new whole-vehicle transform.',
        'Keep dimensioned floor clearance, local engine-source measurements and fixed final-drive geometry as separate constraints; drawing accuracy and floor-line interpretation remain uncertain.'],
    historical_installation_qualified=False,standard_assembly_modified=False))
print(checks)
