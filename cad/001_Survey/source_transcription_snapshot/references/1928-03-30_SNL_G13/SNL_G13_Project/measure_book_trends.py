from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import gaussian_filter,map_coordinates,maximum_filter1d
from scipy.signal import find_peaks
from concurrent.futures import ProcessPoolExecutor
P=Path(__file__).resolve().parent;T=P/'calibration';sys.path.insert(0,str(P));from rectify_borders import trace,evaluate,save_png

def measure(n):
 im=Image.open(P/f'sources/p{n:03}.jpg').convert('L');im.thumbnail((400,850));a=np.asarray(im,dtype=float);h,w=a.shape
 ink=gaussian_filter(a,5)-gaussian_filter(a,.5)
 # Hough candidates tolerate a little bow; subsequent full line tracing rejects
 # text, dashed leaders, and unstable fits by continuous support and residual.
 smooth=maximum_filter1d(np.clip(ink,0,18),size=5,axis=0)
 xs=np.linspace(.18*w,.86*w,70);ys=np.arange(int(.13*h),int(.90*h));slopes=np.linspace(-.14,.14,57)
 xx=np.broadcast_to(xs,(len(ys),len(xs)));score=[]
 for m in slopes:
  yy=ys[:,None]+m*(xs-w*.52)[None,:]
  score.append(np.quantile(map_coordinates(smooth,[yy,xx],order=1),.35,axis=1))
 scores=np.array(score);best=scores.max(0);peaks,_=find_peaks(best,distance=20,prominence=1.3)
 candidates=sorted(peaks,key=lambda k:best[k],reverse=True)[:10];curves=[]
 for k in candidates:
  y=ys[k];m=slopes[scores[:,k].argmax()]
  p1=np.array([.15*w,y+m*(.15*w-.52*w)]);p2=np.array([.88*w,y+m*(.88*w-.52*w)])
  try:c=trace(ink,p1,p2,True,(12,3))
  except Exception:continue
  xx=np.linspace(*c['domain'],200);yy=evaluate(c,xx);response=map_coordinates(ink,[yy,xx],order=1)
  support=float(np.mean(response>3));res=c['stats']['robust_fit_residual_pixels'];bow=c['stats']['curve_bow_pixels']
  if support<.76 or res>1.0 or bow>15:continue
  curves.append(dict(y=float(np.mean(yy)/h),support=support,curve=c))
 curves.sort(key=lambda c:c['y'])
 if len(curves)>=4:
  feats=[];targets=[]
  for r in curves:
   x=np.linspace(.18*w,.86*w,80);y=evaluate(r['curve'],x);u=x/w-.5;v=y/h-.5
   A=np.column_stack([u,u*u,u*u*u,u*v,u*u*v,u*u*u*v]);feats.extend(A-A.mean(0));targets.extend(-(v-v.mean()))
  A=np.array(feats);b=np.array(targets)
  c=np.linalg.lstsq(np.vstack([A,np.diag([.001,.002,.006,.001,.002,.006])]),np.r_[b,np.zeros(6)],rcond=None)[0]
  resid=(A@c-b)*h
  # Height scaling derivative of forward map at left/right normalized columns.
  def scale(u):return 1+c[3]*u+c[4]*u*u+c[5]*u*u*u
  ratio=scale(-.32)/scale(.32)
  model=dict(coeff=c.tolist(),fit_rms_px=float(np.sqrt(np.mean(resid**2))),left_right_vertical_correction_ratio=float(ratio),cross_section_swing=float(c[3]),accepted=True)
  model['accepted']=model['fit_rms_px']<=.7
 else:model=dict(accepted=False)
 return dict(page=n,width=w,height=h,curves=curves,model=model)

if __name__=='__main__':
 ns=list(map(int,sys.argv[1:])) or list(range(2,277))
 with ProcessPoolExecutor(max_workers=4) as ex:
  results=list(ex.map(measure,ns))
 (T/('book_page_trends.json' if len(ns)>20 else 'trends-pilot.json')).write_text(json.dumps(results,indent=2))
 for r in results:
  if len(ns)<=20:
   im=Image.open(P/f'sources/p{r["page"]:03}.jpg').convert('RGB');im.thumbnail((400,850));d=ImageDraw.Draw(im)
   for c in r['curves']:
    x=np.linspace(*c['curve']['domain'],200);y=evaluate(c['curve'],x);d.line(list(zip(x,y)),fill='red',width=1)
   save_png(im,T/f'trends-{r["page"]}.png')
   print(r['page'],len(r['curves']),r['model'],flush=True)
 print('accepted',sum(r['model']['accepted'] for r in results),'of',len(results),flush=True)
