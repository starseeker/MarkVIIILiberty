#!/usr/bin/env python3
"""Prepare only Plates 51–65; preserve all earlier artwork files."""
from pathlib import Path
import argparse,json,hashlib,io
from PIL import Image
import numpy as np
from prepare_assets import page,background
ROOT=Path(__file__).resolve().parent
# name, page, native crop pixels, treatment, page content center, erased outside-art plate label rectangles
FIGURES=[('plate51', 82, [290, 222, 1555, 2325], 'tone', 920, []), ('plate52', 85, [188, 166, 1530, 2310], 'tone', 850, []), ('plate53', 87, [342, 1034, 1265, 1630], 'line', 806, []), ('plate54', 89, [830, 341, 1449, 678], 'tone', 809, []), ('plate55', 89, [135, 1572, 858, 2205], 'tone', 805, []), ('plate56', 90, [289, 1511, 671, 2214], 'tone', 910, []), ('plate57', 91, [110, 664, 1495, 1756], 'tone', 803, []), ('plate58', 93, [80, 228, 834, 787], 'tone', 775, []), ('plate59', 93, [868, 181, 1459, 789], 'tone', 775, []), ('plate60', 93, [123, 899, 739, 1499], 'tone', 775, []), ('plate61', 95, [58, 153, 725, 2273], 'tone', 797, []), ('plate62a', 95, [928, 963, 1525, 1250], 'line', 797, []), ('plate62b', 95, [775, 1626, 1495, 2311], 'line', 797, [[775, 1626, 830, 1740]]), ('plate63', 96, [284, 816, 1635, 1722], 'tone', 959, []), ('plate64', 97, [268, 633, 1334, 1828], 'tone', 810, []), ('plate65', 99, [166, 614, 1531, 1914], 'tone', 849, [])]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source-dir',type=Path,default=ROOT.parent);args=ap.parse_args()
 records=[a for a in json.loads((ROOT/'data/assets.json').read_text()) if a['page']<=80]
 for name,n,box,kind,cx,mask in FIGURES:
  im=page(n,args.source_dir);a=np.array(im.convert('L'),dtype=float);bg=background(a);white=246 if kind=='tone' else 224
  clean=np.clip(np.clip(a/bg*255,0,255)*255/white,0,255).astype('uint8')
  for x0,y0,x1,y1 in mask:clean[y0:y1,x0:x1]=255
  crop=Image.fromarray(clean).crop(box);b=io.BytesIO();crop.save(b,format='PNG',dpi=(300,300));raw=b.getvalue()
  out=ROOT/'assets'/f'{name}.png';out.write_bytes(raw);Image.open(out).load()
  records.append(dict(name=name,page=n,crop=box,kind=kind,content_center_px=cx,method=f'quadratic paper normalization; grayscale white point {white}',label_exclusions=mask,rotation_degrees=0,output_size=list(crop.size),sha256=hashlib.sha256(raw).hexdigest()))
  print(name,flush=True)
 (ROOT/'data/assets.json').write_text(json.dumps(records,indent=2))
 inventory=json.loads((ROOT/'data/source_inventory.json').read_text());inventory['scope']='Title leaf (inferred page 1), printed pages 2–100. Leading blank excluded. Scan 051 right/page 101 is outside this checkpoint.'
 inventory['sources']=[]
 for n in range(1,52):
  f=args.source_dir/f'MarkVIII{n:03}.jpg';inventory['sources'].append(dict(filename=f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),size_bytes=f.stat().st_size))
 (ROOT/'data/source_inventory.json').write_text(json.dumps(inventory,indent=2))
if __name__=='__main__':main()
