"""Saved M769 profile hypotheses with fixed local source projections and receivers."""
import argparse, os
from pathlib import Path
from types import SimpleNamespace
from control_rebuild_io_v2 import *
from lib.camera_review import validate_native_bindings
from lib.cad_build import COLORS
from lib.visual_review import shaded

p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args()
s=Saved(a.candidate);parent=Saved((ROOT/s.report['parent_native']).parent)
out=s.folder/'visual01';out.mkdir(exist_ok=False)
os.environ['MPLCONFIGDIR']=str(out/'plot_runtime')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
validate_native_bindings(dict(native_file=str(s.native),render_occurrences=list(s.rows),landmarks=[]),s.manifest)
COLORS.update(FootProfile=(.76,.39,.17),Receiver=(.42,.52,.63))
def item(source,name,system):
    row=source.rows[name];q=source.world(name);canonical=source.definition(row['definition'])
    return dict(id=name,definition=row['definition'],target=SimpleNamespace(Shape=canonical),shape=q,system=system,representation='assembly')
names=s.report['new_occurrences'];items=[item(s,n,'FootProfile') for n in names]
receivers=['DriverMainShaft','DriverSwingShaft','PortDriverOperatingFulcrum','StarboardDriverOperatingFulcrum',
           'PortDriverLowSelector','StarboardDriverLowSelector','PortDriverHighSelector','StarboardDriverHighSelector',
           'PortDriverLowConnecting','StarboardDriverLowConnecting','PortHighDriverSwingLink','StarboardHighDriverSwingLink']
shaded(items,out/'isometric.svg',(-1,-1,.85),'M769 bowed-link profile hypotheses | two complete solids | interfaces still open')
shaded(items+[item(parent,n,'Receiver') for n in receivers],out/'receiver_context.svg',(-1,-1,.85),
       'M769 in retained driver controls | brown: provisional links | blue: unchanged receivers')
c=s.report['details']['controls'];main=App.Vector(*parent.report['details']['main_world_mm'])
side_receipt=H/'transmission_controls_study/driver_redo01/operating_integrated01/render_receipt.json'
sr=read(side_receipt);source=ROOT/sr['side_source']
side=Image.open(source).convert('RGB').crop(tuple(sr['side_registration']['crop'])).transpose(Image.Transpose.ROTATE_90)
prfile=H/'transmission_controls_study/driver_redo01/mount_registration01.json';pr=read(prfile)
plansource=ROOT/pr['source_image'];plan=Image.open(plansource).convert('RGB')
coef=complex(*c['side_complex_scale']);ctr=complex(*c['side_main_px'])
def project(v,view):
    d=v-main
    if view=='side':
        z=ctr-coef*complex(d.x,d.z);return z.real,z.imag
    return tuple(pr['image_center_px'][i]+pr['pixels_per_mm']*(d.x*pr['world_plus_x_image_unit'][i]+v.y*pr['world_plus_y_image_unit'][i]) for i in range(2))
for view,im,limits in [('side',side,(300,515,447,299)),('plan',plan,(275,465,397,270))]:
    fig,axes=plt.subplots(1,2,figsize=(14,6),dpi=150)
    for i,ax in enumerate(axes):
        ax.imshow(im)
        if i:
            for n in ['DriverMainShaft','DriverSwingShaft']:
                for e in parent.world(n).Edges:
                    pts=[project(v,view) for v in e.discretize(Deflection=.7)]
                    ax.plot(*zip(*pts),color='#3978a9',linewidth=.7,alpha=.5)
            for n in names if view=='plan' else names[:1]:
                for e in s.world(n).Edges:
                    pts=[project(v,view) for v in e.discretize(Deflection=.4)]
                    ax.plot(*zip(*pts),color='#d04b15',linewidth=1.0,alpha=.9)
        ax.set_xlim(limits[:2]);ax.set_ylim(limits[2:]);ax.set_aspect('equal')
        ax.set_title('Source drawing' if not i else 'Saved M769 hypothesis; unchanged shaft registration')
    fig.suptitle('HB113 local side construction comparison' if view=='side' else 'SNL6 local plan comparison; transverse arrangement remains estimated')
    fig.text(.06,.035,'Profile, two-eye interpretation, web stock and rod socket are estimates. No camera refit.\nSource tracing is a construction constraint, not independent historical validation. Complete mechanism is not connected.',fontsize=10)
    fig.subplots_adjust(bottom=.17,top=.88);fig.savefig(out/('source_'+view+'.png'));plt.close(fig)
write(out/'render_receipt.json',dict(native_sha256=sha(s.native),parent_native_sha256=sha(parent.native),
    renderer_sha256=sha(Path(__file__)),manifest_sha256=sha(s.folder/'isolated/manifest.json'),
    sources={str(f.relative_to(ROOT)):sha(f) for f in [source,plansource,side_receipt,prfile]},
    source_camera_refitted=False,construction_not_independent_validation=True,geometry_integrated=False,
    shown_new_occurrences=names,retained_context=receivers,images={f.name:sha(f) for f in out.glob('*.png')}))
print('Rendered isolated links, retained context, and fixed side/plan comparisons.',flush=True)
