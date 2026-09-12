from pathlib import Path
import numpy as np,json
from scipy import ndimage as nd,optimize
from PIL import Image
P=Path(__file__).resolve().parents[2];O=Path(__file__).parent/'fitting-output';O.mkdir(exist_ok=True)
fg=np.asarray(Image.open(P/'sources/p284.jpg').convert('L')).astype(float)/255
bg=np.asarray(Image.open(P/'sources/p283.jpg').convert('L'))[:,::-1].astype(float)/255
# Remove narrow front drawing strokes before registering the faint reverse image.
fc=nd.grey_closing(fg,size=(9,9));fb=nd.gaussian_filter(fc,50)
f=1-fc/np.maximum(fb,.1)
bc=nd.gaussian_filter(nd.grey_closing(bg,size=(121,121)),20)
b=1-bg/np.maximum(bc,.1)
mask=(fc-fg)<.022
mask &= (np.indices(fg.shape)[0]>100)&(np.indices(fg.shape)[0]<1800)
mask &= (np.indices(fg.shape)[1]>45)&(np.indices(fg.shape)[1]<1045)
# Keep narrow drawing lines and dark surface blemishes out of the fit.
mask &= fg>.54
np.savez_compressed(O/'inputs.npz',fg=fg,bg=bg,fc=fc,f=f,b=b,mask=mask)
yy,xx=np.indices(f.shape);sel=mask & (yy%5==0)&(xx%5==0)
y=yy[sel]/1000;x=xx[sel]/1000
p=np.array([1.,0.,.012, -.03,1.,.19,0.,0.])
for sig in [9,5,2]:
 bb=nd.gaussian_filter(b,sig)-nd.gaussian_filter(b,50)
 ff=nd.gaussian_filter(f,sig)[sel];ff-=ff.mean()
 def mapped(p):
  den=1+p[6]*x+p[7]*y
  return nd.map_coordinates(bb,[(p[3]*x+p[4]*y+p[5])*1000/den,(p[0]*x+p[1]*y+p[2])*1000/den],order=1,mode='constant',cval=0)
 def fun(p):
  z=mapped(p);z-=z.mean()
  return -np.dot(z,ff)/max(1e-12,np.linalg.norm(z)*np.linalg.norm(ff))
 res=optimize.minimize(fun,p,method='Powell',bounds=[(.85,1.2),(-.07,.07),(-.10,.10),(-.10,.07),(.88,1.18),(.12,.30),(-.04,.04),(-.04,.04)],options={'maxiter':60,'xtol':.00002,'ftol':.000002})
 p=res.x;print(sig,res.fun,p,flush=True)
 (O/'fit.json').write_text(json.dumps({'parameters':p.tolist(),'correlation':-res.fun,'blur':sig},indent=2))
# Render grayscale ghost view, registered reverse and blend.
x=xx/1000;y=yy/1000;den=1+p[6]*x+p[7]*y
coords=[(p[3]*x+p[4]*y+p[5])*1000/den,(p[0]*x+p[1]*y+p[2])*1000/den]
aligned=nd.map_coordinates(b,coords,order=1,mode='constant',cval=0)
np.save(O/'aligned_density.npy',aligned)
for name,a in [('ghost',1-np.clip(f*9,0,.9)),('aligned',1-np.clip(aligned,0,.9)),('front',fg),('blend',1-np.clip(f*4+aligned*.4,0,.9))]:
 im=Image.fromarray(np.uint8(np.clip(a,0,1)*255));im.thumbnail((660,1200));im.save(O/f'{name}.png')
