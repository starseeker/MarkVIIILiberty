"""Central pedal hypothesis, actual joints and unchanged source projections."""
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
COLORS.update(Pedal=(.40,.56,.43),Bridle=(.69,.39,.19),Suspension=(.35,.53,.66),Sleeve=(.68,.60,.36),Spacers=(.70,.60,.36),Hardware=(.68,.62,.45),Shafts=(.43,.48,.53))
def role(name):
    r=s.report['specs'][name]['role']
    return dict(pedal='Pedal',bridle='Bridle',suspension='Suspension',sleeve='Sleeve',spacer='Spacers',receiver='Shafts').get(r,'Hardware')
def item(source,name,system):
    r=source.rows[name];return dict(id=name,definition=r['definition'],shape=source.world(name),target=SimpleNamespace(Shape=source.definition(r['definition'])),system=system,representation='assembly')
items=[item(s,n,role(n)) for n in s.rows]
shaded(items,out/'isometric.svg',(-1,-1,.7),'Central brake pedal | complete inferred bridle and journal joints | output links not yet connected')
context_names=['PortDriverOperatingFulcrum','StarboardDriverOperatingFulcrum','PortDriverLowSelector','StarboardDriverLowSelector','PortDriverHighSelector','StarboardDriverHighSelector','PortDriverLowConnecting','StarboardDriverLowConnecting','PortHighDriverSwingLink','StarboardHighDriverSwingLink']
context=[item(parent,n,'Shafts') for n in context_names]
shaded(items,out/'retained_context.svg',(-1,-1,.7),'Central pedal within retained controls | existing controls outlined',context=context)
main=App.Vector(*d['main_world_mm']);rear=App.Vector(*d['rear_joint_world_mm']);box=Part.makeBox(150,220,210,rear-App.Vector(75,110,60));detail=[]
for v in items:
    q=v['shape'].common(box)
    if q.Faces:detail.append(dict(id=v['id']+'Clipped',definition=v['id']+'Clipped',shape=q,target=SimpleNamespace(Shape=q),system=v['system'],representation='assembly'))
shaded(detail,out/'rear_joint.svg',(-1,-1,.6),'Rear joint detail | full bolt, nut, cotter, distance tube and suspension | display crop only')
sidefile=H/'transmission_controls_study/driver_redo01/operating_integrated01/render_receipt.json';sr=read(sidefile);sidepath=ROOT/sr['side_source'];side=Image.open(sidepath).convert('RGB').crop(tuple(sr['side_registration']['crop'])).transpose(Image.Transpose.ROTATE_90)
planfile=H/'transmission_controls_study/driver_redo01/mount_registration01.json';pr=read(planfile);planpath=ROOT/pr['source_image'];plan=Image.open(planpath).convert('RGB')
coef=complex(*sr['side_registration']['complex_scale']);center=complex(*sr['side_registration']['main_shaft_px'])
def pixel(v,view):
    delta=v-main
    if view=='side':
        p=center-coef*complex(delta.x,delta.z);return p.real,p.imag
    return [pr['image_center_px'][i]+pr['pixels_per_mm']*(delta.x*pr['world_plus_x_image_unit'][i]+v.y*pr['world_plus_y_image_unit'][i]) for i in range(2)]
for view,im,lim in [('side',side,(0,545,475,80)),('plan',plan,(30,475,410,265))]:
    fig,axes=plt.subplots(1,2,figsize=(15,7),dpi=150)
    for i,ax in enumerate(axes):
        ax.imshow(im)
        if i:
            for name in s.rows:
                color='#417a5a' if name=='DriverBrakePedal' else '#bc591f' if name=='DriverBrakeBridle' else '#467798'
                for edge in s.world(name).Edges:
                    points=[pixel(v,view) for v in edge.discretize(Deflection=.7)];ax.plot(*zip(*points),color=color,linewidth=.8,alpha=.85)
        ax.set_xlim(lim[:2]);ax.set_ylim(lim[2:]);ax.set_aspect('equal');ax.set_title('Original local figure' if not i else 'Saved central-group hypothesis')
    fig.suptitle('Fixed '+('HB113 side' if view=='side' else 'SNL6 plan')+' comparison | no camera refit')
    fig.text(.045,.025,'Pedal dimensions are provisionally transferred from HB149. Overall datum, static angle, bridle form and journal stack are estimates.\nDifferent apparent pedal pose remains visible; source tracing is not independent validation. M769/M771 brake-output topology remains unresolved.',fontsize=10)
    fig.subplots_adjust(bottom=.14,top=.91);fig.savefig(out/('source_'+view+'.png'));plt.close(fig)
write(out/'render_receipt.json',dict(native_sha256=sha(s.native),parent_native_sha256=sha(parent.native),renderer_sha256=sha(Path(__file__)),
    manifest_sha256=sha(s.folder/'isolated/manifest.json'),source_hashes={str(f.relative_to(ROOT)):sha(f) for f in [sidefile,sidepath,planfile,planpath]},
    images={f.name:sha(f) for f in out.glob('*.png')},source_camera_refitted=False,geometry_integrated=False,shown_context=context_names,
    scope='Actual saved central parts and complete joint stock. Source overlays retain the estimated pedal-angle discrepancy; no complete brake mechanism or historical topology qualification.'))
print('Rendered central group, retained context, rear joint and fixed source views.',flush=True)
