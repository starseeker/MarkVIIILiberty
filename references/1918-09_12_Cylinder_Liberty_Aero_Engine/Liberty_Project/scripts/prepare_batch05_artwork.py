"""Original-pixel illustration crops; background normalization without geometric changes."""
from pathlib import Path
import json,hashlib,io
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1]
# Figure, scan, source-pixel crop, cleanup type, white point, source text-centre.
FIGURES=[
(66,81,[175,1110,1565,2290],'line',234,865),
(67,82,[605,1110,1470,1918],'line',236,1030),
(68,84,[212,722,1770,2300],'tone',246,990),
(69,85,[170,732,1675,2420],'tone',246,925),
(70,86,[705,1200,1240,1878],'line',234,965),
(71,87,[180,355,1580,2834],'line',236,865),
(72,88,[175,650,1640,2770],'line',240,946.5),
(73,92,[205,280,1860,2165],'line',236,1030),
(74,96,[140,355,1775,2425],'tone',246,960)]
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
 if number==73:
  # Only the separate printed figure number shares the lower compass note's y range.
  # The drawing, all cable specifications and compass instruction are retained.
  from PIL import ImageDraw
  ImageDraw.Draw(out).rectangle((895-box[0],2110-box[1],1140-box[0],2165-box[1]),fill=255)
 save(out,R/'assets'/asset);save(original,R/'assets'/f'figure_{key}_original.png')
 records.append(dict(figure=number,leaf=leaf,asset=asset,crop=box,kind=kind,white_point=white,source_center=cx,method='per-channel robust quadratic paper normalization' if kind=='color' else 'robust quadratic paper normalization',geometry='unchanged; no rotation, shear or nonlinear warp',pixels=list(out.size),sha256=hashlib.sha256((R/'assets'/asset).read_bytes()).hexdigest()))
 
 if number==73:records[-1]['caption_exclusion_source_pixels']=[895,2110,1140,2165]
 print(number,kind,flush=True)
(R/'data/batch05_artwork.json').write_text(json.dumps(records,indent=2))
old=json.loads((R/'data/baseline_v04_artwork.json').read_text())
(R/'data/artwork.json').write_text(json.dumps(old+records,indent=2))
