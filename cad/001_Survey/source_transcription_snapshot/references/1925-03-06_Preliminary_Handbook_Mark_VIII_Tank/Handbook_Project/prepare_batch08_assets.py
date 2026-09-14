#!/usr/bin/env python3
"""Prepare Plates 89–104 from exact source crops; preserve earlier artwork."""
from pathlib import Path
import argparse,json,hashlib,io
from PIL import Image
import numpy as np
from prepare_assets import page,background
ROOT=Path(__file__).resolve().parent
FIGURES=[('plate89', 143, [185, 824, 1585, 1555], 'tone', 880, []), ('plate90', 144, [265, 827, 1590, 1437], 'tone', 930, [[285, 831, 556, 873]]), ('plate91', 145, [150, 378, 1555, 1192], 'tone', 855, []), ('plate92', 147, [285, 136, 1520, 2435], 'tone', 900, []), ('plate93', 149, [185, 724, 1565, 1678], 'line', 855, [[630, 1656, 1140, 1700]]), ('plate94', 150, [275, 724, 1695, 1710], 'line', 980, []), ('plate95', 151, [275, 615, 1525, 1742], 'line', 880, []), ('plate96', 152, [619, 167, 1240, 1126], 'line', 942, []), ('plate97', 152, [238, 1268, 1660, 2280], 'tone', 951, []), ('plate98', 153, [120, 193, 1570, 1018], 'tone', 843, []), ('plate99', 153, [152, 1265, 1525, 2192], 'tone', 843, []), ('plate100', 155, [180, 239, 1544, 1840], 'tone', 870, []), ('plate101', 156, [230, 438, 1640, 1550], 'tone', 940, []), ('plate102', 157, [160, 542, 1565, 1680], 'tone', 865, []), ('plate103', 158, [625, 875, 1265, 1945], 'tone', 945, []), ('plate104', 159, [154, 610, 1510, 1780], 'tone', 832, [])]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source-dir',type=Path,required=True);args=ap.parse_args()
 records=[a for a in json.loads((ROOT/'data/assets.json').read_text()) if a['page']<=140]
 for name,n,box,kind,cx,mask in FIGURES:
  im=page(n,args.source_dir);a=np.array(im.convert('L'),dtype=float);bg=background(a);white=246 if kind=='tone' else 224
  clean=np.clip(np.clip(a/bg*255,0,255)*255/white,0,255).astype('uint8')
  for x0,y0,x1,y1 in mask:clean[y0:y1,x0:x1]=255
  crop=Image.fromarray(clean).crop(box);b=io.BytesIO();crop.save(b,format='PNG',dpi=(300,300));raw=b.getvalue()
  out=ROOT/'assets'/f'{name}.png';out.write_bytes(raw);Image.open(out).load()
  records.append(dict(name=name,page=n,crop=box,kind=kind,content_center_px=cx,method=f'quadratic paper normalization; grayscale white point {white}',label_exclusions=mask,rotation_degrees=0,output_size=list(crop.size),sha256=hashlib.sha256(raw).hexdigest()))
  print(name,flush=True)
 (ROOT/'data/assets.json').write_text(json.dumps(records,indent=2)+'\n')
 inventory=json.loads((ROOT/'data/source_inventory.json').read_text());inventory['scope']='Title leaf (inferred page 1), printed pages 2–160. Leading blank excluded. Scan 081 right/page 161 is outside this checkpoint.';inventory['sources']=[]
 for n in range(1,82):
  f=args.source_dir/f'MarkVIII{n:03}.jpg';inventory['sources'].append(dict(filename=f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),size_bytes=f.stat().st_size))
 (ROOT/'data/source_inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
if __name__=='__main__':main()
