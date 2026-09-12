#!/usr/bin/env python3
"""Reproduce the accepted p283 -> p284 reverse-ink correction field.

Only the reverse image and an illumination field are resampled. Plate 12's
accepted geometry pixels are never moved. Model coefficients and their source
hashes are stored in restoration/paired/p284-model.json. The registration fitting
experiment is retained alongside that model, separately from this reproduction.
"""
from pathlib import Path
import hashlib,io,json
import numpy as np
from PIL import Image
from scipy import ndimage as nd
from scipy.interpolate import griddata
ROOT=Path(__file__).resolve().parent;D=ROOT/'restoration/paired'

def build():
    model=json.loads((D/'p284-model.json').read_text())
    for name,digest in model['source_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    front=Image.open(ROOT/'sources/p284.jpg');h,w=front.height,front.width
    back=np.asarray(Image.open(ROOT/'sources/p283.jpg').convert('L'))[:,::-1].astype(float)/255
    paper=nd.gaussian_filter(nd.grey_closing(back,size=(121,121)),20)
    ink=1-back/np.maximum(paper,.1)
    yy,xx=np.indices((h,w));x=xx/1000;y=yy/1000;p=model['inverse_homography_normalized']
    den=1+p[6]*x+p[7]*y
    aligned=nd.map_coordinates(ink,[(p[3]*x+p[4]*y+p[5])*1000/den,(p[0]*x+p[1]*y+p[2])*1000/den],order=1,mode='constant',cval=0)
    recs=model['local_matches'];pts=[[r['y'],r['x']] for r in recs]
    def field(key,sigma):
        vals=[r[key] for r in recs]
        z=griddata(pts,vals,(yy,xx),method='linear');nn=griddata(pts,vals,(yy,xx),method='nearest')
        return nd.gaussian_filter(np.where(np.isfinite(z),z,nn),sigma)
    dx=field('dx',100);dy=field('dy',100);alpha=field('alpha',80)
    aligned=nd.map_coordinates(aligned,[yy+dy,xx+dx],order=1)
    ghost=np.clip(nd.gaussian_filter(aligned,1.5)*alpha,0,.25)
    # Same saved map as the accepted Plate 12 geometry, applied ONLY to the field.
    geom=json.loads((ROOT/'calibration/figure_transforms.json').read_text())['284']
    im=Image.fromarray(ghost.astype(np.float32),'F').transpose(Image.Transpose.ROTATE_270).crop(geom['crop'])
    corr=np.array(im.transform(tuple(geom['output_size']),Image.Transform.AFFINE,geom['inverse_affine_coefficients'],resample=Image.Resampling.BICUBIC,fillcolor=0))
    corr=np.clip(corr,0,.25)  # Bicubic interpolation must not invent negative ink.
    buf=io.BytesIO();np.savez_compressed(buf,reverse_ink_fraction=corr.astype(np.float32));(D/'p284-reverse-field.npz').write_bytes(buf.getvalue())
    # Retain diagnostic registration, not a proposed replacement for the source.
    for name,a in [('p283-mirrored-registered',1-np.clip(aligned,0,1)),('p284-predicted-ghost',1-np.clip(ghost*9,0,.95))]:
        im=Image.fromarray(np.uint8(a*255));buf=io.BytesIO();im.save(buf,format='PNG');(D/(name+'.png')).write_bytes(buf.getvalue())
    reference=Image.open(D/'p283-mirrored-registered.png').transpose(Image.Transpose.ROTATE_270).crop(geom['crop'])
    reference=reference.transform(tuple(geom['output_size']),Image.Transform.AFFINE,geom['inverse_affine_coefficients'],resample=Image.Resampling.BICUBIC,fillcolor=255)
    buf=io.BytesIO();reference.save(buf,format='PNG');(D/'p283-reference-in-plate12-canvas.png').write_bytes(buf.getvalue())
    return corr
if __name__=='__main__':
    a=build();print('Recreated reverse-ink field:',a.shape,'range',float(a.min()),float(a.max()))
