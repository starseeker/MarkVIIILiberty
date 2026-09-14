"""Original-pixel illustration crops; background normalization without geometric changes."""
from pathlib import Path
import json,hashlib,io
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1]
# Figure, scan, source-pixel crop, cleanup type, white point, source text-centre.
FIGURES=[
(13,21,[193,330,1878,2825],'tone',246,955.5),
(14,22,[177,280,1828,1173],'tone',246,1000),
(15,22,[181,2063,1829,2850],'tone',246,1000),
(16,23,[128,1114,1648,1940],'tone',246,885),
(17,24,[122,421,1668,2893],'tone',246,987),
(18,26,[260,310,1665,1645],'tone',246,970),
(19,26,[211,2266,1741,2822],'tone',246,970),
(20,27,[122,440,1755,1008],'tone',246,935),
(21,28,[378,1538,1616,2260],'line',224,990),
(22,29,[112,590,1605,2535],'line',232,862),
(23,31,[202,1700,1614,2840],'tone',246,907),
(24,32,[52,1115,1775,2138],'color',242,946.5),
(25,34,[246,776,1715,1474],'color',242,980),
(26,35,[162,579,1528,2840],'color',246,925),
(27,36,[330,500,1740,1562],'line',240,1034),
(28,36,[343,1865,1747,2930],'line',240,1034),
(29,37,[187,432,1580,1254],'line',224,881),
(30,37,[182,1926,1570,2758],'line',224,881),
(31,39,[136,1048,1740,1945],'line',236,876),
(32,40,[547,1305,1345,2042],'line',228,1025)]
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
 original=im.crop(box);out=Image.fromarray(clean).crop(box);asset=f'figure_{number:03}.png'
 save(out,R/'assets'/asset);save(original,R/'assets'/f'figure_{number:03}_original.png')
 records.append(dict(figure=number,leaf=leaf,asset=asset,crop=box,kind=kind,white_point=white,source_center=cx,method='per-channel robust quadratic paper normalization' if kind=='color' else 'robust quadratic paper normalization',geometry='unchanged; no rotation, shear or nonlinear warp',pixels=list(out.size),sha256=hashlib.sha256((R/'assets'/asset).read_bytes()).hexdigest()))
 print(number,kind,flush=True)
(R/'data/batch02_artwork.json').write_text(json.dumps(records,indent=2))
old=json.loads((R/'data/batch01_artwork.json').read_text())
(R/'data/artwork.json').write_text(json.dumps(old+records,indent=2))
