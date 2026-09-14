"""Rectify printed image borders and neutralize paper tint, without synthesis.
Perspective transforms are determined from the printed frame, not scene edges.
No invented detail, inpainting, AI reconstruction, sharpening or redrawn labels.
"""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
from prepare_sources import rectify,homography,point,SPECS
ROOT=Path(__file__).resolve().parents[1]
ART=[
dict(id='jordan_portrait',page=27,quad=[[427,609],[937,607],[939,1316],[428,1318]]),
dict(id='transport_left',page=28,quad=[[33,34],[1196,25],[1197,291],[33,297]]),
dict(id='transport_right',page=29,quad=[[172,126],[1191,121],[1194,356],[173,360]]),
dict(id='loading_accident',page=30,quad=[[103,189],[1143,183],[1154,994],[108,1000]]),
dict(id='sponson_interior',page=31,quad=[[136,602],[620,612],[612,1000],[124,990]]),
dict(id='driver_interior',page=31,quad=[[667,614],[1173,622],[1166,1017],[659,1007]])]
def main():
    nm=json.loads((ROOT/'data/normalization.json').read_text());out=[]
    for a in ART:
        spec=SPECS[a['page']];im=Image.open(ROOT/'sources'/('MarkVIII_manufacture'+spec['file']+'.jpg'))
        q=np.array(a['quad'],float);sc=im.width/spec['refw'];oq=q*sc
        w=round((np.linalg.norm(oq[1]-oq[0])+np.linalg.norm(oq[2]-oq[3]))/2)
        h=round((np.linalg.norm(oq[3]-oq[0])+np.linalg.norm(oq[2]-oq[1]))/2)
        clean=rectify(im,oq,(w,h)).convert('L');arr=np.array(clean)
        # At most 0.1% in each tail; a global tonal correction only.
        black,white=np.percentile(arr,[.1,99.9]);lut=np.clip((np.arange(256)-black)*255/(white-black),0,255).round().astype(np.uint8)
        clean=clean.point(lut.tolist());asset=a['id']+'.png';clean.save(ROOT/'assets'/asset)
        ns=nm[str(a['page'])]['size'];m=homography(spec['quad'],[[0,0],[ns[0],0],ns,[0,ns[1]]]);p=np.array([point(m,*xy) for xy in q])
        # Outer frame placement follows original, rectified to a true rectangle.
        box=[float(p[:,0].mean()-w/sc*ns[0]/(spec['quad'][1][0]-spec['quad'][0][0])/2),float(p[:,1].min()),float(p[:,0].max()-p[:,0].min()),float(p[:,1].max()-p[:,1].min())]
        box=[float((p[0,0]+p[3,0])/2),float((p[0,1]+p[1,1])/2),float((p[1,0]+p[2,0]-p[0,0]-p[3,0])/2),float((p[2,1]+p[3,1]-p[0,1]-p[1,1])/2)]
        out.append(dict(**a,source_file='MarkVIII_manufacture'+spec['file']+'.jpg',source_quad_pixels=oq.tolist(),size=[w,h],asset=asset,normalized_box=box,black_point=float(black),white_point=float(white),sha256=hashlib.sha256((ROOT/'assets'/asset).read_bytes()).hexdigest()))
        print(asset,w,h,flush=True)
    (ROOT/'data/artwork.json').write_text(json.dumps(out,indent=2))
if __name__=='__main__':main()
