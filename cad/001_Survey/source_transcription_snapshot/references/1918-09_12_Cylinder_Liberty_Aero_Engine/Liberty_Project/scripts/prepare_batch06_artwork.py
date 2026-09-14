"""Original-pixel illustration crops; background normalization without geometric changes."""
from pathlib import Path
import json,hashlib,io
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1]
# Figure, scan, source-pixel crop, cleanup type, white point, source text-centre.
FIGURES=[
(75,101,[0,328,1925,2910],'tone',246,962.5),
(76,106,[140,390,1748,1995],'tone',246,947),
(77,107,[132,1500,1790,2177],'line',236,965),
(78,108,[354,992,1585,2520],'line',236,995),
(79,110,[263,1050,1757,2134],'line',236,1020),
(80,111,[365,1060,1415,2275],'line',236,895),
(81,112,[278,1080,1700,1985],'line',236,990),
(82,113,[520,350,1275,945],'line',234,905),
(83,113,[563,1950,1230,2240],'line',236,905),
(84,115,[596,1030,1165,2275],'line',240,885),
(85,116,[278,752,1720,1770],'line',236,1000),
(86,117,[295,1110,1585,1985],'line',234,945),
(87,118,[163,1290,1815,2420],'line',236,990),
(88,120,[267,1138,1725,2045],'line',236,1000)]

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
 if number==88:
  # Only the separate figure number shares the lower Dowel hole label's y range.
  # Both Dowel labels and their original leaders are retained.
  from PIL import ImageDraw
  ImageDraw.Draw(out).rectangle((910-box[0],1980-box[1],1135-box[0],2045-box[1]),fill=255)
 save(out,R/'assets'/asset);save(original,R/'assets'/f'figure_{key}_original.png')
 records.append(dict(figure=number,leaf=leaf,asset=asset,crop=box,kind=kind,white_point=white,source_center=cx,method='per-channel robust quadratic paper normalization' if kind=='color' else 'robust quadratic paper normalization',geometry='unchanged; no rotation, shear or nonlinear warp',pixels=list(out.size),sha256=hashlib.sha256((R/'assets'/asset).read_bytes()).hexdigest()))
 
 if number==88:records[-1]['caption_exclusion_source_pixels']=[910,1980,1135,2045]
 if number==75:records[-1]['layout_max_width_points']=386
 print(number,kind,flush=True)
(R/'data/batch06_artwork.json').write_text(json.dumps(records,indent=2))
old=json.loads((R/'data/baseline_v05_artwork.json').read_text())
(R/'data/artwork.json').write_text(json.dumps(old+records,indent=2))
