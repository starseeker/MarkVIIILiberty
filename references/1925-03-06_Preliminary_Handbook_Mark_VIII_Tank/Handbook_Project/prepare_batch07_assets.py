#!/usr/bin/env python3
"""Prepare Plates 73–88 from exact source crops; preserve earlier artwork."""
from pathlib import Path
import argparse,json,hashlib,io
from PIL import Image
import numpy as np
from prepare_assets import page,background
ROOT=Path(__file__).resolve().parent
FIGURES=[('plate73', 121, [142, 123, 1515, 2448], 'tone', 827, []), ('plate74', 123, [162, 262, 1530, 1085], 'line', 845, []), ('plate75', 123, [158, 1355, 1530, 2185], 'line', 845, []), ('plate76', 124, [290, 323, 1658, 1118], 'line', 978, []), ('plate77', 124, [320, 1410, 1695, 2225], 'line', 978, []), ('plate78', 125, [110, 476, 1520, 1568], 'tone', 815, []), ('plate79', 126, [374, 859, 1695, 1520], 'tone', 1033, []), ('plate80', 128, [335, 598, 1565, 1878], 'tone', 950, []), ('plate81', 129, [190, 187, 1144, 2418], 'tone', 790, []), ('plate82', 131, [135, 212, 1515, 1940], 'tone', 825, []), ('plate83', 133, [260, 573, 1460, 1730], 'tone', 860, []), ('plate84', 137, [475, 727, 1180, 1525], 'tone', 837, []), ('plate85', 138, [330, 697, 1710, 1835], 'tone', 1020, []), ('plate86', 139, [275, 387, 1540, 1850], 'tone', 902, []), ('plate87', 140, [300, 160, 1700, 853], 'tone', 1000, []), ('plate88', 140, [310, 1615, 1740, 2235], 'tone', 1000, [])]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source-dir',type=Path,required=True);args=ap.parse_args()
 records=[a for a in json.loads((ROOT/'data/assets.json').read_text()) if a['page']<=120]
 for name,n,box,kind,cx,mask in FIGURES:
  im=page(n,args.source_dir);a=np.array(im.convert('L'),dtype=float);bg=background(a);white=246 if kind=='tone' else 224
  clean=np.clip(np.clip(a/bg*255,0,255)*255/white,0,255).astype('uint8')
  for x0,y0,x1,y1 in mask:clean[y0:y1,x0:x1]=255
  crop=Image.fromarray(clean).crop(box);b=io.BytesIO();crop.save(b,format='PNG',dpi=(300,300));raw=b.getvalue()
  out=ROOT/'assets'/f'{name}.png';out.write_bytes(raw);Image.open(out).load()
  records.append(dict(name=name,page=n,crop=box,kind=kind,content_center_px=cx,method=f'quadratic paper normalization; grayscale white point {white}',label_exclusions=mask,rotation_degrees=0,output_size=list(crop.size),sha256=hashlib.sha256(raw).hexdigest()))
  print(name,flush=True)
 (ROOT/'data/assets.json').write_text(json.dumps(records,indent=2)+'\n')
 inventory=json.loads((ROOT/'data/source_inventory.json').read_text());inventory['scope']='Title leaf (inferred page 1), printed pages 2–140. Leading blank excluded. Scan 071 right/page 141 is outside this checkpoint.';inventory['sources']=[]
 for n in range(1,72):
  f=args.source_dir/f'MarkVIII{n:03}.jpg';inventory['sources'].append(dict(filename=f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),size_bytes=f.stat().st_size))
 (ROOT/'data/source_inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
if __name__=='__main__':main()
