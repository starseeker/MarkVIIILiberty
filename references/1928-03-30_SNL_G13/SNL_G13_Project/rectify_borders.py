"""Rectify photographed rectangular plate borders with a Coons surface.

Only explicitly identified printed borders are used. Polynomial edge curves
remove curvature as well as skew/keystone. Interior geometry is interpolated,
not independently calibrated. Sources are sampled once with cubic interpolation.
"""
from pathlib import Path
import json, io
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, map_coordinates
from scipy.optimize import root

ROOT=Path(__file__).resolve().parent
# Corners and padding measured in a source preview 800 pixels wide.
# Corner order: top left, top right, bottom left, bottom right.
CONFIG={
297:dict(plate=25,corners=[[63,345],[747,377],[53,1250],[758,1223]],padding=[12,60,12,38]),
305:dict(plate=33,corners=[[78,254],[715,296],[61,1389],[722,1354]],padding=[12,42,12,37]),
306:dict(plate=34,corners=[[81,164],[715,154],[81,1141],[746,1134]],padding=[12,42,12,37]),
285:dict(plate=13,corners=[[79,223],[749,257],[60,1331],[751,1305]],padding=[45,15,40,18]),
286:dict(plate=14,corners=[[85,431],[736,421],[82,887],[748,883]],padding=[18,45,18,42]),
287:dict(plate=15,corners=[[74,229],[727,267],[54,1307],[733,1277]],padding=[18,42,18,35]),
288:dict(plate=16,corners=[[74,127],[711,112],[67,1188],[736,1188]],padding=[18,42,18,35]),
289:dict(plate=17,corners=[[96,232],[742,275],[73,1326],[744,1300]],padding=[42,15,38,18]),
290:dict(plate=18,corners=[[146,284],[712,265],[155,1017],[744,1005]],padding=[52,18,38,18]),
291:dict(plate=19,corners=[[92,417],[732,443],[85,1137],[739,1113]],padding=[45,18,35,18]),
}

def save_png(im,path):
 b=io.BytesIO();im.save(b,format='PNG');path.write_bytes(b.getvalue())

def trace(ink,a,b,horizontal,radii=(28,7)):
 axis=0 if horizontal else 1;other=1-axis
 lo,hi=a[axis],b[axis]
 xs=np.linspace(lo,hi,int(abs(hi-lo)/2)+1)
 expected=np.interp(xs,[lo,hi],[a[other],b[other]])
 selected=None;coeff=None
 for radius in radii:
  offsets=np.arange(-radius,radius+1)
  ys=expected[:,None]+offsets
  xx=np.broadcast_to(xs[:,None],ys.shape)
  coords=[ys,xx] if horizontal else [xx,ys]
  response=map_coordinates(ink,coords,order=1,mode='nearest')-.006*offsets**2
  choice=np.argmax(response,axis=1)
  selected=ys[np.arange(len(xs)),choice]
  strength=response[np.arange(len(xs)),choice]
  t=(xs-lo)/(hi-lo)
  mask=(t>.015)&(t<.985)&(strength>1)
  weights=np.ones(mask.sum())
  for _ in range(7):
   coeff=np.polynomial.polynomial.polyfit(t[mask],selected[mask],4,w=weights)
   residual=selected[mask]-np.polynomial.polynomial.polyval(t[mask],coeff)
   scale=max(.8,1.4826*np.median(abs(residual-np.median(residual))))
   weights=np.minimum(1,1.5*scale/np.maximum(abs(residual),.01))
  expected=np.polynomial.polynomial.polyval(t,coeff)
 chord=expected[0]+t*(expected[-1]-expected[0])
 stats=dict(samples=int(mask.sum()),curve_bow_pixels=float(np.max(abs(expected-chord))),
   robust_fit_residual_pixels=float(np.median(abs(selected[mask]-expected[mask]))))
 return dict(domain=[float(lo),float(hi)],coefficients=coeff.tolist(),stats=stats)

def evaluate(curve,t):
 lo,hi=curve['domain']
 return np.polynomial.polynomial.polyval((t-lo)/(hi-lo),curve['coefficients'])

def corners_of(edges,guess):
 pairs=[('top','left'),('top','right'),('bottom','left'),('bottom','right')]
 points=[]
 for (h,v),g in zip(pairs,guess):
  r=root(lambda q:[q[1]-evaluate(edges[h],q[0]),q[0]-evaluate(edges[v],q[1])],g)
  if not r.success:raise RuntimeError('Border corner intersection failed')
  points.append(r.x)
 return np.array(points)

def surface(edges,corners,u,v):
 tl,tr,bl,br=corners
 tx=tl[0]+u*(tr[0]-tl[0]);ty=evaluate(edges['top'],tx)
 bx=bl[0]+u*(br[0]-bl[0]);by=evaluate(edges['bottom'],bx)
 ly=tl[1]+v*(bl[1]-tl[1]);lx=evaluate(edges['left'],ly)
 ry=tr[1]+v*(br[1]-tr[1]);rx=evaluate(edges['right'],ry)
 bilx=(1-u)*(1-v)*tl[0]+u*(1-v)*tr[0]+(1-u)*v*bl[0]+u*v*br[0]
 bily=(1-u)*(1-v)*tl[1]+u*(1-v)*tr[1]+(1-u)*v*bl[1]+u*v*br[1]
 return (1-v)*tx+v*bx+(1-u)*lx+u*rx-bilx,(1-v)*ty+v*by+(1-u)*ly+u*ry-bily

def rectify(page,cfg):
 im=Image.open(ROOT/'sources'/f'p{page}.jpg').convert('RGB')
 scale=im.width/800
 guess=np.array(cfg['corners'],float)*scale
 gray=np.array(im.convert('L'),dtype=float)
 ink=gaussian_filter(gray,6)-gaussian_filter(gray,.65)
 tl,tr,bl,br=guess
 edges={key:trace(ink,a,b,h) for key,a,b,h in [
  ('top',tl,tr,True),('bottom',bl,br,True),('left',tl,bl,False),('right',tr,br,False)]}
 corners=corners_of(edges,guess);tl,tr,bl,br=corners
 width=(np.linalg.norm(tr-tl)+np.linalg.norm(br-bl))/2
 height=(np.linalg.norm(bl-tl)+np.linalg.norm(br-tr))/2
 pl,pt,pr,pb=np.array(cfg['padding'])*scale
 ww,hh=int(np.ceil(width+pl+pr)),int(np.ceil(height+pt+pb))
 uu,vv=np.meshgrid((np.arange(ww)-pl)/width,(np.arange(hh)-pt)/height)
 sx,sy=surface(edges,corners,uu,vv)
 dxdy,dxdx=np.gradient(sx);dydy,dydx=np.gradient(sy)
 determinant=dxdx*dydy-dxdy*dydx
 if determinant.min()<=0:raise RuntimeError(f'p{page}: folded mapping')
 rgb=np.array(im)
 out=np.stack([map_coordinates(rgb[:,:,i],[sy,sx],order=3,mode='nearest',prefilter=True) for i in range(3)],axis=2).astype('uint8')
 result=Image.fromarray(out)
 save_png(result,ROOT/'assets'/f'p{page}-geometry.png')
 bounds=[int(np.floor(sx.min())),int(np.floor(sy.min())),int(np.ceil(sx.max())),int(np.ceil(sy.max()))]
 save_png(im.crop(bounds),ROOT/'proofs'/f'p{page}-before.png')
 # Show which source lines constrained the reconstruction.
 annotated=im.copy();draw=ImageDraw.Draw(annotated)
 for name,curve in edges.items():
  xs=np.linspace(*curve['domain'],250);ys=evaluate(curve,xs)
  pts=list(zip(xs,ys)) if name in ['top','bottom'] else list(zip(ys,xs))
  draw.line(pts,fill=(220,40,45),width=3)
 save_png(annotated.crop(bounds),ROOT/'proofs'/f'p{page}-constraints.png')
 annotated.thumbnail((700,1300));save_png(annotated,ROOT/'calibration'/f'p{page}-constraint-overlay.png')
 record=dict(plates=[cfg['plate']],rotate=0,method='nonlinear Coons surface from four traced printed border curves',
  reference='Four printed frame edges constrained to a rectangle; angled illustrated components retain their intended angles.',
  status='border-constrained dewarp; interior interpolation and absolute aspect ratio remain estimates',
  source_image_size=im.size,output_size=result.size,crop=bounds,corners=corners.tolist(),edges=edges,
  output_border_size=[width,height],output_padding=[pl,pt,pr,pb],
  min_jacobian=float(determinant.min()),max_jacobian=float(determinant.max()),
  outside_source_fraction=float(np.mean((sx<0)|(sx>=im.width)|(sy<0)|(sy>=im.height))))
 return record

def main():
 records={}
 for page,cfg in CONFIG.items():
  records[str(page)]=rectify(page,cfg)
  print(page,'bow max',round(max(e['stats']['curve_bow_pixels'] for e in records[str(page)]['edges'].values()),2))
 (ROOT/'calibration'/'border_transforms.json').write_text(json.dumps(records,indent=2))
 return records

if __name__=='__main__':main()
