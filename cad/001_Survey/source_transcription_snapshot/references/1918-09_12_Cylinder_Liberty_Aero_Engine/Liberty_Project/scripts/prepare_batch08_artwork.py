"""Original-pixel illustration crops; background normalization without geometric changes."""
from pathlib import Path
import json,hashlib,io
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1]
# Figure, scan, source-pixel crop, cleanup type, white point, source text-centre.
FIGURES=[
(97,142,[280,1108,1668,1968],'line',236,980),
(98,147,[307,445,1415,1130],'line',236,875),
(99,147,[138,1568,1655,2893],'line',236,875),
(100,148,[275,375,1825,2608],'line',238,1050),
(101,150,[405,169,1512,1428],'line',240,965),
(102,152,[187,156,1895,1309],'line',240,1041),
(103,154,[205,399,1883,1040],'line',240,1044),
(104,155,[208,402,1757,2780],'line',238,980),
(105,157,[171,430,1635,2703],'line',238,899),
(106,158,[198,378,1732,2740],'line',238,965),
(107,160,[201,149,1921,1232],'line',242,1061)]
# These points place original artwork at a uniform scale on each wider page.
LAYOUT={101:[69,57,.43,612],102:[36,93,.42,792],103:[42,171,.42,792],107:[35,88,.42,792]}
# Only the printed caption shares the art's lower extent. Retain the Mod. label,
# its diagonal leader and every dimension; retype the caption in native frames.
MASKS={101:[[489,1332,761,1430]]}
# Empty photographed paper edges only. Leave the edge beside the propeller
# untouched where original engineering ink approaches it. Original crops stay exact.
BACKGROUND_MASKS={102:[[187,156,206,820],[187,1090,206,1309]],107:[[1875,149,1921,995]]}

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
 original=im.crop(box)
 for mx0,my0,mx1,my1 in MASKS.get(number,[])+BACKGROUND_MASKS.get(number,[]):clean[my0:my1,mx0:mx1]=255
 out=Image.fromarray(clean).crop(box);key=str(number).zfill(3);asset=f'figure_{key}.png'
 save(out,R/'assets'/asset);save(original,R/'assets'/f'figure_{key}_original.png')
 records.append(dict(figure=number,leaf=leaf,asset=asset,crop=box,kind=kind,white_point=white,source_center=cx,method='per-channel robust quadratic paper normalization' if kind=='color' else 'robust quadratic paper normalization',geometry='unchanged; no rotation, shear or nonlinear warp',pixels=list(out.size),sha256=hashlib.sha256((R/'assets'/asset).read_bytes()).hexdigest()))
 
 if number in MASKS:
  records[-1]['excluded_caption_rectangles']=MASKS[number]
  records[-1]['exclusion_note']='Printed caption only; diagonal Mod. No. D859 / DRG. No. A.B. 4313 leader and label remain original pixels.'
 if number in BACKGROUND_MASKS:
  records[-1]['excluded_background_rectangles']=BACKGROUND_MASKS[number]
  records[-1]['background_exclusion_note']='Unprinted photographed paper-edge strips only; all engineering ink and the unaltered original crop retained.'
 if number in LAYOUT:
  x,y,scale,pw=LAYOUT[number]
  records[-1]['layout_box_points']=[x,y,(box[2]-box[0])*scale,(box[3]-box[1])*scale]
  records[-1]['foldout_page_points']=[pw,691]
  records[-1]['layout_note']='Provisional wider foldout canvas; uniform original-pixel scale; no geometric rectification; external weights and backdrop outside crop.'
 print(number,kind,flush=True)
(R/'data/batch08_artwork.json').write_text(json.dumps(records,indent=2))
old=json.loads((R/'data/baseline_v07_artwork.json').read_text())
(R/'data/artwork.json').write_text(json.dumps(old+records,indent=2))
