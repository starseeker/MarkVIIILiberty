"""Nonlinear alignment of explicit perpendicular section reference lines.

The p293 centerline and outer dashed vertical reference are used, not component
silhouettes. A separable pair of smooth displacement fields aligns both axes.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import gaussian_filter,map_coordinates
from rectify_borders import trace,evaluate,save_png
ROOT=Path(__file__).resolve().parent

def main():
 im=Image.open(ROOT/'sources/p293.jpg').convert('RGB').transpose(Image.Transpose.ROTATE_270)
 gray=np.asarray(im.convert('L'),dtype=float)
 ink=gaussian_filter(gray,6)-gaussian_filter(gray,.65)
 h=trace(ink,np.array([300,627]),np.array([1570,646]),True,(6,3))
 v=trace(ink,np.array([295,112]),np.array([325,1046]),False,(6,3))
 # Use low-order fits for extrapolation beyond the measured reference extents.
 for edge in [h,v]:
  t=np.linspace(0,1,200)
  edge['coefficients']=np.polynomial.polynomial.polyfit(t,np.polynomial.polynomial.polyval(t,edge['coefficients']),2).tolist()
 xref=float(evaluate(v,630));yref=float(evaluate(h,900))
 crop=[255,75,1660,1108]
 x0,y0,x1,y1=crop
 perimeter=np.vstack([np.column_stack([np.linspace(x0,x1,200),np.full(200,y)]) for y in [y0,y1]]+
   [np.column_stack([np.full(200,x),np.linspace(y0,y1,200)]) for x in [x0,x1]])
 fw=np.column_stack([perimeter[:,0]-evaluate(v,perimeter[:,1])+xref,
   perimeter[:,1]-evaluate(h,perimeter[:,0])+yref])
 lo=np.floor(fw.min(axis=0));hi=np.ceil(fw.max(axis=0))
 ww,hh=(hi-lo).astype(int)
 u,w=np.meshgrid(np.arange(ww)+lo[0],np.arange(hh)+lo[1])
 sx=u.copy();sy=w.copy()
 for _ in range(12):
  sx=u+evaluate(v,sy)-xref
  sy=w+evaluate(h,sx)-yref
 dxdy,dxdx=np.gradient(sx);dydy,dydx=np.gradient(sy)
 jac=dxdx*dydy-dxdy*dydx
 assert jac.min()>0
 rgb=np.array(im)
 out=np.stack([map_coordinates(rgb[:,:,i],[sy,sx],order=3,mode='nearest') for i in range(3)],axis=2).astype('uint8')
 save_png(Image.fromarray(out),ROOT/'assets/p293-geometry.png')
 save_png(im.crop(crop),ROOT/'proofs/p293-before.png')
 draw=ImageDraw.Draw(im)
 for edge,horizontal in [(h,True),(v,False)]:
  xs=np.linspace(*edge['domain'],300);ys=evaluate(edge,xs)
  draw.line(list(zip(xs,ys)) if horizontal else list(zip(ys,xs)),fill=(220,40,45),width=3)
 save_png(im.crop(crop),ROOT/'proofs/p293-constraints.png')
 im.thumbnail((1300,800));save_png(im,ROOT/'calibration/p293-constraint-overlay.png')
 result=dict(plates=[21],rotate=90,source_image_size=[2048,1164],output_size=[int(ww),int(hh)],crop=crop,
  method='nonlinear paired axis displacement fields',reference='Main shaft centerline and long outer dashed vertical reference constrained to page axes.',
  horizontal=h,vertical=v,reference_origin=[xref,yref],output_origin=lo.tolist(),
  min_jacobian=float(jac.min()),max_jacobian=float(jac.max()),
  status='line-constrained pilot; remaining interior geometry and absolute scale uncalibrated')
 (ROOT/'calibration/axis_transforms.json').write_text(json.dumps({'293':result},indent=2))
 return {'293':result}

if __name__=='__main__':main()
