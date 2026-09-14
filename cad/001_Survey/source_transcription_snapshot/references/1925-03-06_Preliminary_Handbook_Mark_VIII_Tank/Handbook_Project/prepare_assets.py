#!/usr/bin/env python3
"""Deterministic cleanup of the first eleven source spreads; no generated detail.
Run from any directory. Original MarkVIII001.jpg ... MarkVIII011.jpg belong in
this project's parent directory (or supply --source-dir).
"""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
ROOT=Path(__file__).resolve().parent
# Native per-page pixels: even left half, odd right half; source spread x split=1750.
FIGURES=[
 ('seal',1,[520,1390,920,1860],'line'),
 ('plate01',8,[350,125,1320,2350],'tone'),
 ('plate02',10,[540,105,1260,2360],'tone'),
 ('plate03',12,[190,75,1580,1150],'tone'),
 ('plate04',13,[135,935,1510,1940],'tone'),
 ('plate05',14,[210,65,1590,765],'tone'),
 ('plate06',16,[210,115,1550,1260],'tone'),
 ('plate07',17,[120,1490,1490,2320],'line'),
 ('plate08',18,[250,345,1480,1290],'line'),
 ('plate09',19,[120,65,1500,1260],'line'),
 ('plate10',20,[450,140,1420,848],'line'),
 ('plate11',20,[420,1198,1410,2220],'line')]
def page(n,src):
 scan=1 if n==1 else n//2+1
 a=Image.open(src/f'MarkVIII{scan:03}.jpg').convert('RGB')
 return a.crop((0,0,1750,2550) if n%2==0 else (1750,0,3509,2550))
def background(a):
 # Robust quadratic fit to high-quantile tile samples. Dark illustration tiles
 # are rejected; this estimates paper illumination, not missing ink.
 h,w=a.shape;pts=[]
 for y in range(0,h,100):
  for x in range(0,w,100):
   tile=a[y:y+100,x:x+100]
   if tile.size:pts.append([(x+tile.shape[1]/2)/w,(y+tile.shape[0]/2)/h,float(np.percentile(tile,90))])
 pts=np.array(pts);x,y,z=pts.T;A=np.array([x*0+1,x,y,x*x,x*y,y*y]).T
 keep=z>np.percentile(z,35)
 for _ in range(4):
  coef=np.linalg.lstsq(A[keep],z[keep],rcond=None)[0];res=z-A@coef;keep=(res>-12)&(res<16)&(z>160)
 yy,xx=np.mgrid[:h,:w];xx=xx/w;yy=yy/h
 return np.clip(coef[0]+coef[1]*xx+coef[2]*yy+coef[3]*xx*xx+coef[4]*xx*yy+coef[5]*yy*yy,165,255)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source-dir',type=Path,default=ROOT.parent);args=ap.parse_args();src=args.source_dir
 (ROOT/'assets').mkdir(exist_ok=True);records=[]
 for name,n,box,kind in FIGURES:
  im=page(n,src);a=np.array(im.convert('L'),dtype=float);bg=background(a)
  norm=np.clip(a/bg*255,0,255)
  # Tone masters retain a broad grayscale range; drawings use a white-point
  # lift. No sharpening, inpainting, tracing or interior geometric constraints.
  white=246 if kind=='tone' else 224
  clean=np.clip(norm*255/white,0,255).astype('uint8')
  # Remove only separately reconstructed plate labels outside artwork.
  exclusions={12:[[1320,92,1565,138]],14:[[1320,67,1575,113]],19:[[1225,112,1465,157]]}.get(n,[])
  for x0,y0,x1,y1 in exclusions:clean[y0:y1,x0:x1]=255
  crop=Image.fromarray(clean).crop(box)
  crop.save(ROOT/'assets'/f'{name}.png',dpi=(300,300))
  records.append(dict(name=name,page=n,crop=box,method='quadratic paper normalization; grayscale white point '+str(white),kind=kind,label_exclusions=exclusions,rotation_degrees=0,output_size=list(crop.size),sha256=hashlib.sha256((ROOT/'assets'/f'{name}.png').read_bytes()).hexdigest()))
 (ROOT/'data/assets.json').write_text(json.dumps(records,indent=2))
 inventory=[]
 for n in range(1,12):
  f=src/f'MarkVIII{n:03}.jpg';inventory.append(dict(filename=f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),size_bytes=f.stat().st_size))
 (ROOT/'data/source_inventory.json').write_text(json.dumps(dict(repository='https://github.com/starseeker/MarkVIIILiberty',source_directory='references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank',scope='Title leaf (inferred page 1), printed pages 2–20; leading blank excluded. Spread 011 right/page 21 is outside pilot.',sources=inventory),indent=2))
 print('Prepared',len(records),'artwork assets')
if __name__=='__main__':main()
