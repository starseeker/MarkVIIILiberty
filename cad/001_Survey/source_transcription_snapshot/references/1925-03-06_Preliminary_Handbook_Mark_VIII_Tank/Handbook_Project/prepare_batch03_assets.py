#!/usr/bin/env python3
"""Prepare only Plates 32–41; preserve all earlier artwork files."""
from pathlib import Path
import argparse,json,hashlib,io
from PIL import Image
import numpy as np
from prepare_assets import page,background
ROOT=Path(__file__).resolve().parent
# name, page, native crop pixels, treatment, page content center, erased outside-art plate label rectangles
FIGURES=[
('plate32',41,[225,300,1610,1435],'tone',905,[]),
('plate33',43,[500,870,1280,1498],'line',890,[]),
('plate34',44,[250,615,1635,1558],'tone',940,[]),
('plate35',48,[230,245,1615,2055],'tone',922,[]),
('plate36',50,[220,140,1670,2375],'line',945,[]),
('plate37',52,[250,150,1605,2245],'tone',925,[]),
('plate38',54,[220,10,1595,2445],'tone',908,[]),
('plate39',56,[180,140,1565,2315],'tone',872,[]),
('plate40',58,[255,235,1640,2215],'tone',947,[]),
('plate41',60,[255,140,1630,2270],'tone',942,[]),
]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source-dir',type=Path,default=ROOT.parent);args=ap.parse_args()
 records=[a for a in json.loads((ROOT/'data/assets.json').read_text()) if a['page']<=40]
 for name,n,box,kind,cx,mask in FIGURES:
  im=page(n,args.source_dir);a=np.array(im.convert('L'),dtype=float);bg=background(a);white=246 if kind=='tone' else 224
  clean=np.clip(np.clip(a/bg*255,0,255)*255/white,0,255).astype('uint8')
  for x0,y0,x1,y1 in mask:clean[y0:y1,x0:x1]=255
  crop=Image.fromarray(clean).crop(box);b=io.BytesIO();crop.save(b,format='PNG',dpi=(300,300));raw=b.getvalue()
  out=ROOT/'assets'/f'{name}.png';out.write_bytes(raw);Image.open(out).load()
  records.append(dict(name=name,page=n,crop=box,kind=kind,content_center_px=cx,method=f'quadratic paper normalization; grayscale white point {white}',label_exclusions=mask,rotation_degrees=0,output_size=list(crop.size),sha256=hashlib.sha256(raw).hexdigest()))
  print(name,flush=True)
 (ROOT/'data/assets.json').write_text(json.dumps(records,indent=2))
 inventory=json.loads((ROOT/'data/source_inventory.json').read_text());inventory['scope']='Title leaf (inferred page 1), printed pages 2–60. Leading blank excluded. Scan 031 right/page 61 is outside this checkpoint.'
 inventory['sources']=[]
 for n in range(1,32):
  f=args.source_dir/f'MarkVIII{n:03}.jpg';inventory['sources'].append(dict(filename=f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),size_bytes=f.stat().st_size))
 (ROOT/'data/source_inventory.json').write_text(json.dumps(inventory,indent=2))
if __name__=='__main__':main()
