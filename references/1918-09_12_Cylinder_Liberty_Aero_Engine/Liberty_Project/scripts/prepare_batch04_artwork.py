"""Original-pixel illustration crops; background normalization without geometric changes."""
from pathlib import Path
import json,hashlib,io
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1]
# Figure, scan, source-pixel crop, cleanup type, white point, source text-centre.
FIGURES=[
(49,61,[145,1190,1625,2650],'line',234,883),
(50,62,[375,398,1705,1265],'tone',246,1035),
(51,64,[400,390,1655,2870],'tone',246,1020),
(52,66,[560,1400,1540,2265],'line',234,1045),
(53,68,[187,2025,1505,3025],'tone',246,946.5),
(54,68,[255,530,1445,1705],'tone',246,946.5),
(55,69,[135,935,1600,1745],'line',234,880),
(56,71,[500,1050,1250,2175],'line',234,867),
(57,72,[550,935,1500,2770],'line',234,1025),
(58,74,[512,515,1500,2610],'line',234,1035),
(59,75,[230,750,1430,1838],'line',234,830),
(60,76,[300,600,1715,2610],'tone',246,1025),
(61,77,[88,790,1650,2155],'line',234,880),
(62,78,[380,925,1680,2260],'line',234,1025),
(63,79,[465,548,1310,1355],'line',234,883),
(64,79,[460,2070,1320,2590],'line',234,880),
(65,80,[590,780,1445,1945],'line',234,1025)]
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
 save(out,R/'assets'/asset);save(original,R/'assets'/f'figure_{key}_original.png')
 records.append(dict(figure=number,leaf=leaf,asset=asset,crop=box,kind=kind,white_point=white,source_center=cx,method='per-channel robust quadratic paper normalization' if kind=='color' else 'robust quadratic paper normalization',geometry='unchanged; no rotation, shear or nonlinear warp',pixels=list(out.size),sha256=hashlib.sha256((R/'assets'/asset).read_bytes()).hexdigest()))
 
 print(number,kind,flush=True)
(R/'data/batch04_artwork.json').write_text(json.dumps(records,indent=2))
old=json.loads((R/'data/baseline_v03_artwork.json').read_text())
(R/'data/artwork.json').write_text(json.dumps(old+records,indent=2))
