#!/usr/bin/env python3
"""Prepare only Plates 42–50; preserve all earlier artwork files."""
from pathlib import Path
import argparse,json,hashlib,io
from PIL import Image
import numpy as np
from prepare_assets import page,background
ROOT=Path(__file__).resolve().parent
# name, page, native crop pixels, treatment, page content center, erased outside-art plate label rectangles
FIGURES=[
('plate42',62,[215,155,1605,2305],'tone',910,[]),
('plate43',64,[250,350,1590,2130],'line',930,[]),
('plate44',66,[525,390,1390,2175],'line',950,[]),
('plate45',68,[310,350,1535,1947],'line',929,[]),
('plate46',71,[202,750,1580,1600],'tone',880,[]),
('plate47',73,[145,552,1490,1857],'line',821,[]),
('plate48',74,[220,580,1570,1854],'line',896,[]),
('plate49',75,[160,645,1475,1768],'line',816,[]),
('plate50',78,[190,495,1590,1998],'tone',890,[]),
]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source-dir',type=Path,default=ROOT.parent);args=ap.parse_args()
 records=[a for a in json.loads((ROOT/'data/assets.json').read_text()) if a['page']<=60]
 for name,n,box,kind,cx,mask in FIGURES:
  im=page(n,args.source_dir);a=np.array(im.convert('L'),dtype=float);bg=background(a);white=246 if kind=='tone' else 224
  clean=np.clip(np.clip(a/bg*255,0,255)*255/white,0,255).astype('uint8')
  for x0,y0,x1,y1 in mask:clean[y0:y1,x0:x1]=255
  crop=Image.fromarray(clean).crop(box);b=io.BytesIO();crop.save(b,format='PNG',dpi=(300,300));raw=b.getvalue()
  out=ROOT/'assets'/f'{name}.png';out.write_bytes(raw);Image.open(out).load()
  records.append(dict(name=name,page=n,crop=box,kind=kind,content_center_px=cx,method=f'quadratic paper normalization; grayscale white point {white}',label_exclusions=mask,rotation_degrees=0,output_size=list(crop.size),sha256=hashlib.sha256(raw).hexdigest()))
  print(name,flush=True)
 (ROOT/'data/assets.json').write_text(json.dumps(records,indent=2))
 inventory=json.loads((ROOT/'data/source_inventory.json').read_text());inventory['scope']='Title leaf (inferred page 1), printed pages 2–80. Leading blank excluded. Scan 041 right/page 81 is outside this checkpoint.'
 inventory['sources']=[]
 for n in range(1,42):
  f=args.source_dir/f'MarkVIII{n:03}.jpg';inventory['sources'].append(dict(filename=f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),size_bytes=f.stat().st_size))
 (ROOT/'data/source_inventory.json').write_text(json.dumps(inventory,indent=2))
if __name__=='__main__':main()
