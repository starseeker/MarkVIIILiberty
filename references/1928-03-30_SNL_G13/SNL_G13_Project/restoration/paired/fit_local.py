from pathlib import Path
import json
import numpy as np
from scipy import ndimage as nd,optimize
from scipy.interpolate import griddata
from PIL import Image
P=Path(__file__).resolve().parents[2];O=Path(__file__).parent/'fitting-output';O.mkdir(exist_ok=True)
a=np.load(O/'inputs.npz');fg=a['fg'];fc=a['fc'];mask=a['mask'];b=np.load(O/'aligned_density.npy');h,w=fg.shape
f=1-fg/nd.gaussian_filter(fc,50)
bb=nd.gaussian_filter(b,3)-nd.gaussian_filter(b,50)
ff=nd.gaussian_filter(a['f'],2)
records=[]
for cy in range(180,1740,150):
 for cx in range(140,1040,150):
  yy,xx=np.mgrid[max(30,cy-130):min(h-60,cy+130):3,max(30,cx-130):min(w-30,cx+130):3];m=mask[yy,xx];y=yy[m];x=xx[m]
  zf=ff[y,x];zf-=zf.mean()
  def fun(d):
   z=nd.map_coordinates(bb,[y+d[1],x+d[0]],order=1);z-=z.mean()
   return -np.dot(z,zf)/max(1e-10,np.linalg.norm(z)*np.linalg.norm(zf))+.0001*np.dot(d,d)
  res=optimize.minimize(fun,[0,0],method='Powell',bounds=[(-18,18)]*2,options={'xtol':.03,'maxiter':15})
  dx,dy=res.x;corr=-fun(res.x)+.0001*np.dot(res.x,res.x)
  if corr>.25:records.append(dict(x=cx,y=cy,dx=dx,dy=dy,corr=corr))
print('matches',len(records),flush=True)
yy,xx=np.indices(f.shape);pts=[[r['y'],r['x']] for r in records]
def field(values,sigma=100):
 z=griddata(pts,values,(yy,xx),method='linear');nn=griddata(pts,values,(yy,xx),method='nearest')
 return nd.gaussian_filter(np.where(np.isfinite(z),z,nn),sigma)
dx=field([r['dx'] for r in records]);dy=field([r['dy'] for r in records]);bl=nd.map_coordinates(b,[yy+dy,xx+dx],order=1)
bb=nd.gaussian_filter(bl,2)-nd.gaussian_filter(bl,50)
# Estimate reverse-ink transfer separately in overlapping local windows, from
# front pixels without sharp dark linework; low frequency paper light excluded.
for r in records:
 cy,cx=r['y'],r['x'];sy=slice(cy-100,cy+100);sx=slice(max(15,cx-100),min(w-15,cx+100));sel=mask[sy,sx]
 zb=bb[sy,sx][sel];zf=f[sy,sx][sel];zb-=zb.mean();zf-=zf.mean()
 alpha=np.dot(zb,zf)/max(1e-9,np.dot(zb,zb));r['alpha']=float(np.clip(alpha,0,.35))
 r['local_corr_after']=float(np.dot(zb,zf)/max(1e-9,np.linalg.norm(zb)*np.linalg.norm(zf)))
alpha=field([r['alpha'] for r in records],80)
# only subtract blurred registered reverse ink; don't synthesize high-frequency
# details. Keep a conservative transfer fraction for uncertain intersections.
ghost=nd.gaussian_filter(bl,1.5)*alpha
paper=nd.gaussian_filter(nd.grey_closing(fg,size=(81,81)),20)
correction=ghost*paper
geom=json.loads((P/'calibration/figure_transforms.json').read_text())['284']
def rectify(field):
 im=Image.fromarray(field.astype(np.float32),'F').transpose(Image.Transpose.ROTATE_270).crop(geom['crop'])
 return np.array(im.transform(tuple(geom['output_size']),Image.Transform.AFFINE,geom['inverse_affine_coefficients'],resample=Image.Resampling.BICUBIC,fillcolor=0))
corrgeom=rectify(ghost)
raw=np.asarray(Image.open(P/'assets/p284-geometry.png').convert('L')).astype(float)/255
np.savez_compressed(O/'local_model.npz',correction=corrgeom,dx=dx,dy=dy,alpha=alpha,aligned=bl)
(O/'local_fit.json').write_text(json.dumps(records,indent=2))
for factor in [0, .65,1.]:
 g=nd.gaussian_filter(np.clip(raw/np.maximum(1-corrgeom*factor,.65),0,1),.35)
 local=nd.gaussian_filter(nd.grey_closing(g,size=(31,31)),3);ink=1-g/np.maximum(local,.1)
 for floor in [.035,.055]:
  line=1-np.clip((ink-floor)/(.5-floor),0,1)**.85
  Image.fromarray(np.uint8(line*255)).save(O/f'plate12-ratio-{factor}-floor-{floor}.png')
# Registration panels and transfer prediction in front raw coordinates
for name,z in [('registered-back',1-bl),('predicted-ghost',1-np.clip(ghost*9,0,.95)),('corrected-raw',np.clip(fg+correction,0,1))]:
 im=Image.fromarray(np.uint8(z*255));im.thumbnail((660,1200));im.save(O/f'{name}.png')
print('alpha range',np.quantile(alpha,[0,.1,.5,.9,1]),flush=True)
