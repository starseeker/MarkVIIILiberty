"""Fit shared smooth cross-sections to H/V lettering and drawing references.

Coordinates are measured in the original portrait JPEG. A low-order field is
nonlinear across page width but affine in page height: a restrained approximation
to photographed open-book curvature, not a calibrated 3-D sheet reconstruction.
Nearby same-parity observations supply a weak depth-profile prior, never a fixed
warp. Reserved labels/lines do not enter the fit. Original pixels are sampled once.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import map_coordinates
from scipy.optimize import least_squares
from rectify_borders import save_png
ROOT=Path(__file__).resolve().parent

def fit_model(page,cfg,output_root=None):
 dest=Path(output_root) if output_root else ROOT
 for folder in ['calibration','assets','proofs']:(dest/folder).mkdir(parents=True,exist_ok=True)
 im=Image.open(ROOT/'sources'/cfg['source']).convert('RGB');width,height=im.size
 center=np.array([width/2,height/2]);scale=width;rows=cfg['controls']
 prior=json.loads((ROOT/'calibration/book_priors.json').read_text())[page]
 uses_prior=any(i>=3 for i in cfg.get('active_y',range(6)))
 def features(points,orientation):
  x,y=((np.asarray(points)-center)/scale).T
  return np.column_stack([x,x*x,x*x*x,x*y,x*x*y,x*x*x*y]) if orientation=='H' else np.column_stack([y,x*y,x*x*y])
 def fit(orientation):
  A=[];z=[]
  for row in rows:
   if row['orientation']!=orientation or row['holdout']:continue
   points=np.array(row['points']);f=features(points,orientation)
   v=points[:,1 if orientation=='H' else 0]/scale
   weight=.6 if row.get('kind')=='line' else 1.
   A.extend((f-f.mean(0))*weight);z.extend(-(v-v.mean())*weight)
  if not A:return np.zeros(6 if orientation=='H' else 3)
  A=np.array(A);z=np.array(z)
  reg=np.array([.0001,.001,.004,.0001,.001,.004]) if orientation=='H' else np.array([.0001,.001,.003])
  u=np.array([-.32,-.16,.16,.32]);B=np.column_stack([u,u*u,u*u*u])
  def residual(c):
   extra=prior['weight']*(B@(c[3:]-np.array(prior['coeff']))) if orientation=='H' else np.zeros(0)
   return np.r_[A@c-z,reg*c,extra]
  active=cfg.get('active_y' if orientation=='H' else 'active_x',list(range(A.shape[1])))
  def expand(c):
   full=np.zeros(A.shape[1]);full[active]=c;return full
  return expand(least_squares(lambda c:residual(expand(c)),np.zeros(len(active)),loss='soft_l1',f_scale=.001).x)
 cy=fit('H');cx=fit('V')
 def forward(points):
  points=np.asarray(points);return points+scale*np.column_stack([features(points,'V')@cx,features(points,'H')@cy])
 validation=[]
 for r in rows:
  pts=np.array(r['points']);out=forward(pts);idx=1 if r['orientation']=='H' else 0
  validation.append(dict(name=r['name'],holdout=r['holdout'],orientation=r['orientation'],points=len(pts),source_rms_pixels=float(np.std(pts[:,idx])),corrected_rms_pixels=float(np.std(out[:,idx])),source_angle_degrees=float(np.degrees(np.arctan(np.polyfit(pts[:,1-idx],pts[:,idx],1)[0]))),corrected_angle_degrees=float(np.degrees(np.arctan(np.polyfit(out[:,1-idx],out[:,idx],1)[0])))))
 x0,y0,x1,y1=crop=cfg['crop_portrait']
 perimeter=np.vstack([np.column_stack([np.linspace(x0,x1,200),np.full(200,y)]) for y in [y0,y1]]+[np.column_stack([np.full(200,x),np.linspace(y0,y1,200)]) for x in [x0,x1]])
 mapped=forward(perimeter);lo=np.floor(mapped.min(0));hi=np.ceil(mapped.max(0));ww,hh=(hi-lo).astype(int)
 y,x=np.mgrid[:hh,:ww];target=np.column_stack([x.ravel()+lo[0],y.ravel()+lo[1]]);source=target.copy()
 for _ in range(16):source-=forward(source)-target
 error=float(np.max(abs(forward(source)-target)));assert error<1e-4
 sx=source[:,0].reshape(hh,ww);sy=source[:,1].reshape(hh,ww)
 dxdy,dxdx=np.gradient(sx);dydy,dydx=np.gradient(sy);jac=dxdx*dydy-dxdy*dydx
 assert jac.min()>0
 sourceim=im.copy();box=cfg.get('identifier_exclusion')
 if box:ImageDraw.Draw(sourceim).rectangle(box,fill=im.getpixel((box[0]-20,box[1]+15)))
 a=np.array(sourceim);out=np.stack([map_coordinates(a[:,:,j],[sy,sx],order=3,mode='nearest') for j in range(3)],axis=2).astype('uint8')
 outside=(sx<x0)|(sx>=x1)|(sy<y0)|(sy>=y1);out[outside]=[248,246,239]
 result=Image.fromarray(out);before=im.crop(crop);annotated=im.copy();draw=ImageDraw.Draw(annotated)
 for r in rows:
  color=(35,110,210) if r['holdout'] else (220,40,45)
  points=r['points']
  if r.get('kind')=='line':draw.line([tuple(p) for p in points],fill=color,width=3)
  else:
   for px,py in points:draw.ellipse([px-2,py-2,px+2,py+2],fill=color)
 save_png(annotated,dest/'calibration'/f'p{page}-text-constraint-overlay.png')
 constraints=annotated.crop(crop)
 if cfg['rotate']:
  result=result.transpose(Image.Transpose.ROTATE_270);before=before.transpose(Image.Transpose.ROTATE_270);constraints=constraints.transpose(Image.Transpose.ROTATE_270)
 save_png(result,dest/'assets'/f'p{page}-geometry.png');save_png(before,dest/'proofs'/f'p{page}-before.png');save_png(constraints,dest/'proofs'/f'p{page}-constraints.png')
 held=[v for v in validation if v['holdout']]
 report=dict(uses_book_profile_prior=uses_prior,active_y=cfg.get('active_y',list(range(6))),active_x=cfg.get('active_x',list(range(3))),source_size=im.size,center=center.tolist(),scale=scale,x_coefficients=cx.tolist(),y_coefficients=cy.tolist(),output_origin_portrait=lo.tolist(),output_size_portrait=[int(ww),int(hh)],inverse_max_error_pixels=error,min_jacobian=float(jac.min()),max_jacobian=float(jac.max()),neutral_margin_fraction=float(outside.mean()),prior=prior,validation=validation,heldout_count=len(held),heldout_source_rms_pixels=float(np.sqrt(np.mean([v['source_rms_pixels']**2 for v in held]))),heldout_corrected_rms_pixels=float(np.sqrt(np.mean([v['corrected_rms_pixels']**2 for v in held]))))
 record=dict(uses_book_profile_prior=uses_prior,plates=cfg['plates'],rotate=cfg['rotate'],crop=crop,crop_coordinate_system='original portrait JPEG',source_image_size=im.size,output_size=result.size,method='smooth shared cross-section fitted to text and reference lines',reference='Lettering and selected drawing or photographic boundaries. '+('Nearby same-parity pages supply a weak profile prior. ' if uses_prior else 'Sparse references permit only a reduced alignment model. ')+'Red: fitted observations; blue: withheld validation.',status='text/line-constrained correction; remaining interior geometry and physical scale uncalibrated',min_jacobian=report['min_jacobian'],max_jacobian=report['max_jacobian'],heldout_count=len(held),heldout_source_rms_pixels=report['heldout_source_rms_pixels'],heldout_corrected_rms_pixels=report['heldout_corrected_rms_pixels'])
 return record,report

def main():
 controls=json.loads((ROOT/'calibration/text_line_controls.json').read_text());records={};reports={}
 for page,cfg in controls.items():
  records[page],reports[page]=fit_model(page,cfg)
  print(page,'held-out RMS:',round(reports[page]['heldout_source_rms_pixels'],3),'->',round(reports[page]['heldout_corrected_rms_pixels'],3),flush=True)
 (ROOT/'calibration/text_model_validation.json').write_text(json.dumps(reports,indent=2))
 (ROOT/'calibration/text_model_transforms.json').write_text(json.dumps(records,indent=2))
 return records
if __name__=='__main__':main()
