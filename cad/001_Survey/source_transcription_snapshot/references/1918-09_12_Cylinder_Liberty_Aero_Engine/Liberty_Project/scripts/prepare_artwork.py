"""Source-pixel crops and conservative tonal cleanup. No drawing geometry is warped."""
from pathlib import Path
import json,hashlib,shutil,io
import numpy as np
from PIL import Image
from fontTools.ttLib import TTFont
ROOT=Path(__file__).resolve().parents[1]
FIGURES=[
 (1,4,[138,230,1755,2815],'tone'),(2,12,[70,715,1850,2380],'tone'),
 (3,13,[510,1040,1320,2760],'line'),(4,14,[455,1380,1580,2080],'tone'),
 (5,15,[640,1110,1140,2210],'tone'),(6,16,[605,415,1380,2435],'line'),
 (7,17,[365,943,1440,2225],'line'),(8,18,[185,610,1830,1620],'tone'),
 (9,18,[550,1850,1430,2830],'tone'),(10,19,[165,398,1670,1385],'tone'),
 (11,20,[704,350,1295,725],'line'),(12,20,[315,1690,1710,2180],'line')]
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
records=[]
for number,leaf,box,kind in FIGURES:
 f=ROOT/'sources'/f'liberty12cylinde00grea_{leaf:04}.jp2';im=Image.open(f).convert('RGB')
 a=np.array(im.convert('L'),dtype=float);bg=background(a);white=246 if kind=='tone' else 224
 clean=np.clip((a/bg*255)*255/white,0,255).astype('uint8')
 original=im.crop(box);out=Image.fromarray(clean).crop(box)
 asset=f'figure_{number:03}.png'
 for img,dest in [(out,ROOT/'assets'/asset),(original,ROOT/'assets'/f'figure_{number:03}_original.png')]:
  buf=io.BytesIO();img.save(buf,format='PNG',dpi=(344,344));dest.write_bytes(buf.getvalue());Image.open(dest).load()
 records.append(dict(figure=number,leaf=leaf,asset=asset,crop=box,kind=kind,method='robust quadratic paper normalization',white_point=white,geometry='unchanged; no rotation, shear or nonlinear warp',pixels=list(out.size),sha256=hashlib.sha256((ROOT/'assets'/asset).read_bytes()).hexdigest()))
(ROOT/'data/artwork.json').write_text(json.dumps(records,indent=2))
metrics={}
for name in ['C059-Roman','C059-Bold','C059-Italic','NimbusSans-Bold']:
 p=Path('/usr/share/fonts/opentype/urw-base35')/(name+'.otf');shutil.copy2(p,ROOT/'fonts'/p.name)
 f=TTFont(p);em=f['head'].unitsPerEm;cm=f.getBestCmap();metrics[name]={chr(k):f['hmtx'][v][0]/em for k,v in cm.items()}
(ROOT/'fonts/metrics.json').write_text(json.dumps(metrics))
for p in Path('/usr/share/doc/fonts-urw-base35').glob('copyright'):shutil.copy2(p,ROOT/'fonts/LICENSE.txt')
print('Prepared',len(records),'illustrations and four bundled fonts.')
