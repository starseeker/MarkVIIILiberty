"""Mounted reverse quadrant and full stock, with unchanged source projections."""
import argparse,os
from pathlib import Path
from types import SimpleNamespace
from control_rebuild_io_v2 import *
from lib.visual_review import shaded
from lib.cad_build import COLORS
from lib.camera_review import validate_native_bindings
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args()
s=Saved(a.candidate);parent=Saved((ROOT/s.report['parent_native']).parent);d=s.report['details']
out=s.folder/'visual01';out.mkdir(exist_ok=False)
os.environ['MPLCONFIGDIR']=str(out/'plot_runtime')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
validate_native_bindings(dict(native_file=str(s.native),render_occurrences=list(s.rows),landmarks=[]),s.manifest)
COLORS.update(Lever=(.40,.56,.43),Rod=(.69,.39,.19),Quadrant=(.33,.52,.67),Hardware=(.68,.62,.45),Shafts=(.43,.48,.53))
def role(name):
    r=s.report['specs'][name]['role']
    return dict(lever='Lever',rod='Rod',quadrant='Quadrant',receiver='Shafts').get(r,'Hardware')
def item(source,name,system):
    r=source.rows[name];return dict(id=name,definition=r['definition'],shape=source.world(name),target=SimpleNamespace(Shape=source.definition(r['definition'])),system=system,representation='assembly')
items=[item(s,n,role(n)) for n in s.rows]
shaded(items,out/'isometric.svg',(-1,-1,.7),'Reverse quadrant | complete mounting stock | trigger and pawl pending')
context_names=[n for n in parent.rows if (n.startswith('DriverSeat') or n.startswith('StarboardDriver') or n.startswith('PortDriver') or n.startswith('DriverClutch')) and n not in s.rows]
context=[item(parent,n,'Shafts') for n in context_names]
shaded(items,out/'retained_context.svg',(-1,-1,.7),'Reverse quadrant within retained driver station | existing controls and seat outlined',context=context)
main=App.Vector(*d['main_world_mm'])
box=Part.makeBox(450,110,370,main+App.Vector(-150,-335,70));detail=[]
for v in items:
    q=v['shape'].common(box)
    if q.Faces:detail.append(dict(id=v['id']+'Detail',definition=v['id']+'Detail',shape=q,target=SimpleNamespace(Shape=q),system=v['system'],representation='assembly'))
shaded(detail,out/'mount_detail.svg',(-1,-1,.7),'Quadrant mounting detail | full bolts, nuts and spacers | support clipped for display only')
sidefile=H/'transmission_controls_study/driver_redo01/operating_integrated01/render_receipt.json';sr=read(sidefile);sidepath=ROOT/sr['side_source'];side=Image.open(sidepath).convert('RGB').crop(tuple(sr['side_registration']['crop'])).transpose(Image.Transpose.ROTATE_90)
planfile=H/'transmission_controls_study/driver_redo01/mount_registration01.json';pr=read(planfile);planpath=ROOT/pr['source_image'];plan=Image.open(planpath).convert('RGB')
coef=complex(*sr['side_registration']['complex_scale']);center=complex(*sr['side_registration']['main_shaft_px'])
def pixel(v,view):
    delta=v-main
    if view=='side':
        p=center-coef*complex(delta.x,delta.z);return p.real,p.imag
    return [pr['image_center_px'][i]+pr['pixels_per_mm']*(delta.x*pr['world_plus_x_image_unit'][i]+v.y*pr['world_plus_y_image_unit'][i]) for i in range(2)]
for view,im,lim in [('side',side,(0,545,475,80)),('plan',plan,(30,475,360,130))]:
    fig,axes=plt.subplots(1,2,figsize=(15,7),dpi=150)
    for i,ax in enumerate(axes):
        ax.imshow(im)
        if i:
            for name in s.rows:
                color='#417a5a' if name=='DriverReverseOperatingLever' else '#bc591f' if name=='DriverReverseShortRod' else '#467798'
                for edge in s.world(name).Edges:
                    points=[pixel(v,view) for v in edge.discretize(Deflection=.7)];ax.plot(*zip(*points),color=color,linewidth=.8,alpha=.85)
        ax.set_xlim(lim[:2]);ax.set_ylim(lim[2:]);ax.set_aspect('equal');ax.set_title('Original local figure' if not i else 'Saved quadrant-mount hypothesis')
    fig.suptitle('Fixed '+('HB113 side' if view=='side' else 'SNL6 plan')+' comparison | no camera refit')
    fig.text(.045,.025,'Full source bolt/rod stock retained. Quadrant profile, ears, detents, spacers and support attachment are estimates.\nMounting picks are construction inputs, not holdouts. Trigger/pawl and long reverse route remain pending; no camera refit.',fontsize=10)
    fig.subplots_adjust(bottom=.14,top=.91);fig.savefig(out/('source_'+view+'.png'));plt.close(fig)
write(out/'render_receipt.json',dict(native_sha256=sha(s.native),parent_native_sha256=sha(parent.native),renderer_sha256=sha(Path(__file__)),
    manifest_sha256=sha(s.folder/'isolated/manifest.json'),source_hashes={str(f.relative_to(ROOT)):sha(f) for f in [sidefile,sidepath,planfile,planpath]},
    images={f.name:sha(f) for f in out.glob('*.png')},source_camera_refitted=False,geometry_integrated=False,shown_context=context_names,
    scope='Actual saved mounted quadrant and complete reverse short connection. Source-derived mounting picks are construction inputs, not independent validation. No complete latch, historical profile or motion qualification.'))
print('Rendered mounted quadrant, local detail, retained context and fixed source views.',flush=True)
