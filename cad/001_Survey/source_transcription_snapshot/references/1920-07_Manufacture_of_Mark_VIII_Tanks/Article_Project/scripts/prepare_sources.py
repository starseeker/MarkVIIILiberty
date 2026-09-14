"""Deterministic scan normalization and region OCR. Original files are untouched."""
from pathlib import Path
import json, math, subprocess, concurrent.futures
import numpy as np
from PIL import Image, ImageOps
ROOT=Path(__file__).resolve().parents[1]
SPECS={
27:dict(file='001',refw=1300,quad=[[167,210],[1210,208],[1210,1655],[167,1655]],regions={'Ltop':[169,500,667,611],'L':[168,611,395,1656],'Rtop':[685,497,1210,581],'R':[969,578,1213,1655]}),
28:dict(file='002_composite',refw=1229,quad=[[29,20],[1200,20],[1204,1756],[34,1756]],regions={'L':[28,346,614,1759],'R':[630,344,1210,1759]}),
29:dict(file='003',refw=1300,quad=[[167,120],[1198,115],[1208,1680],[163,1680]],regions={'L':[161,406,670,1682],'R':[678,404,1206,1682]}),
30:dict(file='004',refw=1300,quad=[[99,134],[1149,130],[1164,1671],[103,1671]],regions={'L':[102,1041,625,1672],'R':[638,1040,1168,1672]}),
31:dict(file='005',refw=1300,quad=[[151,144],[1178,163],[1145,1698],[103,1677]],regions={'Ltop':[139,181,640,581],'Lbottom':[104,1019,626,1680],'Rtop':[651,188,1180,595],'Rbottom':[625,1034,1156,1702]}),
32:dict(file='006',refw=1300,quad=[[185,155],[1238,151],[1250,1670],[196,1674]],regions={'L':[184,199,716,1678],'R':[726,196,1254,1678]}),
33:dict(file='007',refw=1300,quad=[[146,132],[1177,132],[1177,571],[146,579]],regions={'L':[145,177,641,582],'R':[658,175,1180,577]})}

def homography(src,dst):
    a=[];b=[]
    for (x,y),(u,v) in zip(src,dst):
        a.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]]);b.extend([u,v])
    return np.r_[np.linalg.solve(a,b),1].reshape(3,3)
def point(m,x,y):
    p=m@np.array([x,y,1]);return p[:2]/p[2]
def rectify(im,quad,size):
    w,h=size;m=homography([[0,0],[w,0],[w,h],[0,h]],quad)
    return im.transform(size,Image.Transform.PERSPECTIVE,tuple(m.flatten()[:8]),Image.Resampling.BICUBIC,fillcolor='white')
def ocr(job):
    page,key,path=job
    out=ROOT/'data/ocr'/f'p{page}_{key}'
    subprocess.run(['tesseract',str(path),str(out),'--psm','6','-l','eng','txt','tsv'],check=True,capture_output=True)
    return str(out.name)
def main():
    for d in ['data/ocr','qa/normalized','qa/regions']: (ROOT/d).mkdir(parents=True,exist_ok=True)
    result={};jobs=[]
    for page,spec in SPECS.items():
        im=Image.open(ROOT/'sources'/('MarkVIII_manufacture'+spec['file']+'.jpg'))
        qa_scale=im.width/spec['refw'];q=np.array(spec['quad'],float)
        w=2080;h=round(w*((np.linalg.norm(q[3]-q[0])+np.linalg.norm(q[2]-q[1]))/(np.linalg.norm(q[1]-q[0])+np.linalg.norm(q[2]-q[3]))))
        norm=rectify(im,q*qa_scale,(w,h));norm.save(ROOT/'qa/normalized'/f'p{page}.png')
        thumb=norm.copy();thumb.thumbnail((1040,1600));thumb.save(ROOT/'qa/normalized'/f'p{page}.jpg')
        m=homography(q,[[0,0],[w,0],[w,h],[0,h]])
        rr={}
        for key,(x0,y0,x1,y1) in spec['regions'].items():
            pts=np.array([point(m,x,y) for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]])
            bb=[max(0,math.floor(pts[:,0].min())),max(0,math.floor(pts[:,1].min())),min(w,math.ceil(pts[:,0].max())),min(h,math.ceil(pts[:,1].max()))]
            crop=ImageOps.autocontrast(norm.crop(bb).convert('L'),cutoff=.2)
            path=ROOT/'qa/regions'/f'p{page}_{key}.png';crop.save(path)
            rr[key]=dict(box=bb);jobs.append((page,key,path))
        result[page]=dict(size=[w,h],source=spec,regions=rr)
    (ROOT/'data/normalization.json').write_text(json.dumps(result,indent=2))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        for r in ex.map(ocr,jobs): print(r,flush=True)
if __name__=='__main__':main()
