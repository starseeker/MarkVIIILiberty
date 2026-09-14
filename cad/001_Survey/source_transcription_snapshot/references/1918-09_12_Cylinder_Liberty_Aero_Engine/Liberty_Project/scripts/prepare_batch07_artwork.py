"""Original-pixel illustration crops; background normalization without geometric changes."""
from pathlib import Path
import json,hashlib,io
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1]
# Figure, scan, source-pixel crop, cleanup type, white point, source text-centre.
FIGURES=[
(89,121,[650,1420,1175,1875],'line',236,920),
(90,122,[635,2105,1345,2415],'line',236,960),
(91,123,[350,1080,1495,1635],'line',236,930),
(92,124,[370,310,1585,1517],'line',236,985),
(93,126,[297,85,1570,1530],'line',240,940),
(94,129,[122,895,1670,1777],'line',236,900),
(95,132,[347,408,1670,1497],'line',240,1020),
(96,133,[260,335,1495,1548],'tone',246,880)]

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
 
 if number==93:
  records[-1]['layout_box_points']=[62,37,(box[2]-box[0])*.38,(box[3]-box[1])*.38]
  records[-1]['foldout_page_points']=[612,691]
  records[-1]['layout_note']='Provisional wider foldout canvas; uniform scale; complete internal labels retained; external weights and backdrop outside crop.'
 print(number,kind,flush=True)
(R/'data/batch07_artwork.json').write_text(json.dumps(records,indent=2))
old=json.loads((R/'data/baseline_v06_artwork.json').read_text())
(R/'data/artwork.json').write_text(json.dumps(old+records,indent=2))
