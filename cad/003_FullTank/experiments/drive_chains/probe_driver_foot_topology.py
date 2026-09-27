"""Compare retained driver receivers against fixed local source projections before foot reconstruction."""
import argparse,os
from pathlib import Path
from control_rebuild_io_v2 import App,Part,H,ROOT,Saved,read,write,sha
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
s=Saved(H/'coupled_driver_integration/integrated01');old=H/'transmission_controls_study/driver_redo01/operating_integrated01/render_receipt.json';reg=read(old)
source=ROOT/reg['side_source'];planpath=H/'transmission_controls_study/driver_redo01/mount_registration01.json';plan=read(planpath)
os.environ['MPLCONFIGDIR']=str(out/'plot_runtime');import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
from PIL import Image
im=Image.open(source).crop(tuple(reg['side_registration']['crop'])).transpose(Image.Transpose.ROTATE_90)
main=App.Vector(*s.report['details']['main_world_mm']);scale=complex(*reg['side_registration']['complex_scale']);center=complex(*reg['side_registration']['main_shaft_px'])
def pixel(v):
 d=v-main;q=center-scale*complex(d.x,d.z);return q.real,q.imag
names=['PortDriverOperatingFulcrum','PortDriverLowSelector','PortDriverLowConnecting','PortDriverHighSelector','PortDriverLowBrake','PortHighDriverSwingLink']
records={};fig,axes=plt.subplots(2,3,figsize=(18,11),dpi=150)
for name,ax in zip(names,axes.flat):
 shape=s.world(name);ax.imshow(im)
 for edge in shape.Edges:
  pts=[pixel(v) for v in edge.discretize(Deflection=.6)];ax.plot(*zip(*pts),color='#d53819',linewidth=.85,alpha=.85)
 axes_seen={};surfaces=[]
 for f in shape.Faces:
  surf=f.Surface
  if isinstance(surf,Part.Cylinder):
   axis=surf.Axis
   if abs(abs(axis.y)-1)>1e-7:continue
   point=surf.Center;key=(round(point.x,6),round(point.z,6),round(surf.Radius,6))
   if key in axes_seen:continue
   axes_seen[key]=True;u,v=pixel(point);ax.scatter([u],[v],s=18,color='#167ce8');ax.text(u+2,v+2,str(len(surfaces)+1),color='#0072c1',fontsize=9)
   surfaces.append(dict(radius_mm=surf.Radius,axis=list(axis),point_world_mm=list(point),pixel=[u,v],note='All cylindrical supports parallel to Y, including outer stock; radius alone does not identify a bore.'))
 records[name]=dict(definition=s.rows[name]['definition'],frame=s.rows[name]['frame'],cylindrical_surfaces=surfaces)
 ax.set_xlim(240,530);ax.set_ylim(460,235);ax.set_aspect('equal');ax.set_title(name);ax.axis('off')
fig.suptitle('Foot-control interface diagnosis | saved receivers, unchanged HB113 registration')
fig.tight_layout();fig.savefig(out/'existing_receiver_comparison.png');plt.close(fig)
write(out/'report.json',dict(native_sha256=sha(s.native),source_sha256=sha(source),side_registration_receipt_sha256=sha(old),plan_registration_sha256=sha(planpath),worker_sha256=sha(Path(__file__)),occurrences=records,source_camera_refitted=False,geometry_modified=False,images={'existing_receiver_comparison.png':sha(out/'existing_receiver_comparison.png')}))
print('Saved6 fixed-projection receiver comparisons; no geometry modification.',flush=True)
