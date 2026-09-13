"""Original-pixel illustration crops; background normalization without geometric changes."""
from pathlib import Path
import json,hashlib,io
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1]
# Figure, scan, source-pixel crop, cleanup type, white point, source text-centre.
FIGURES=[
(33,41,[165,385,1688,1320],'tone',246,925),
(34,41,[390,1750,1478,2800],'tone',246,925),
('34a',42,[180,1350,1835,2115],'line',232,1010),
(35,43,[225,345,1510,2690],'tone',246,852),
(36,44,[455,1255,1675,2680],'tone',246,1060),
(37,45,[410,2010,1320,2805],'line',228,868),
(38,46,[95,225,1862,2245],'tone',246,986),
(39,48,[190,855,1795,2160],'line',234,994),
(40,49,[245,225,1478,1318],'line',232,840),
(41,49,[352,1600,1340,2750],'line',232,840),
(42,51,[405,725,1285,1527],'line',228,867),
(43,52,[460,282,1675,1953],'tone',246,1056),
(44,54,[218,292,1840,1220],'line',234,1018),
(45,54,[305,2108,1760,2817],'tone',246,1018),
(46,55,[570,1082,1270,2260],'line',232,900),
(47,56,[308,935,1690,2175],'line',236,1002),
(48,60,[720,1222,1490,2105],'line',234,1100)]
def background(a):
 h,w=a.shape;pts=[]
 for y in range(0,h,100):
  for x in range(0,w,100):
   t=a[y:y+100,x:x+100];pts.append([(x+t.shape[1]/2)/w,(y+t.shape[0]/2)/h,float(np.percentile(t,90))])
 x,y,z=np.array(pts).T;A=np.array([x*0+1,x,y,x*x,x*y,y*y]).T;keep=z>np.percentile(z,35)
 for _ in range(4):
  c=np.linalg.lstsq(A[keep],z[keep],rcond=None)[0];r=z-A@c;keep=(r>-12)&(r<16)&(z>160)
 yy,xx=np.mgrid[:h,:w];xx=xx/w;yy=yy/h
 return np.clip(c[0]+c[1]*xx+c[2]*yy+c[3]*xx*xx+c[4]*xx*yy+c[5]*yy*yy,165,255)
def save(im,p):
 b=io.BytesIO();im.save(b,format='PNG',dpi=(344,344));Image.open(io.BytesIO(b.getvalue())).load();p.write_bytes(b.getvalue());Image.open(p).load()
records=[]
for number,leaf,box,kind,white,cx in FIGURES:
 im=Image.open(R/'sources'/f'liberty12cylinde00grea_{leaf:04}.jp2').convert('RGB')
 if kind=='color':
  a=np.asarray(im,dtype=float);bg=np.stack([background(a[:,:,c]) for c in range(3)],axis=2)
 else:
  a=np.asarray(im.convert('L'),dtype=float);bg=background(a)
 clean=np.clip(a/bg*255*255/white,0,255).astype('uint8')
 original=im.crop(box);out=Image.fromarray(clean).crop(box);key=str(number).zfill(3);asset=f'figure_{key}.png'
 if number==47:
  # Remove printed Fig. 47 caption only; the lower B label remains original pixels.
  from PIL import ImageDraw
  ImageDraw.Draw(out).rectangle((885-box[0],2113-box[1],1140-box[0],2175-box[1]),fill=255)
 save(out,R/'assets'/asset);save(original,R/'assets'/f'figure_{key}_original.png')
 records.append(dict(figure=number,leaf=leaf,asset=asset,crop=box,kind=kind,white_point=white,source_center=cx,method='per-channel robust quadratic paper normalization' if kind=='color' else 'robust quadratic paper normalization',geometry='unchanged; no rotation, shear or nonlinear warp',pixels=list(out.size),sha256=hashlib.sha256((R/'assets'/asset).read_bytes()).hexdigest()))
 
 if number==47:records[-1]['caption_exclusion_source_pixels']=[885,2113,1140,2175]
 print(number,kind,flush=True)
(R/'data/batch03_artwork.json').write_text(json.dumps(records,indent=2))
old=json.loads((R/'data/batch02_artwork.json').read_text())
(R/'data/artwork.json').write_text(json.dumps(old+records,indent=2))
