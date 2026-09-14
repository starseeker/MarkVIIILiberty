#!/usr/bin/env python3
"""Prepare Plates 111–118 by deterministic paper normalization only."""
from pathlib import Path
import argparse,json,hashlib,io
from PIL import Image
import numpy as np
from prepare_assets import page,background
ROOT=Path(__file__).resolve().parent
FIGURES=[
 ('plate111',186,[240,226,1745,1324],'tone',995,[]),
 ('plate112',186,[645,1525,1330,2152],'tone',995,[]),
 ('plate113',187,[335,173,1548,2430],'line',960,[]),
 ('plate114',193,[80,504,1490,1970],'tone',784,[]),
 ('plate115',195,[119,180,1525,1527],'tone',818,[]),
 ('plate116',195,[55,1622,1537,2380],'tone',795,[]),
 ('plate117',197,[276,442,1441,941],'tone',858,[]),
 ('plate118',197,[309,1418,1428,1882],'tone',868,[])]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source-dir',type=Path,required=True);args=ap.parse_args()
 records=[a for a in json.loads((ROOT/'data/assets.json').read_text()) if a['page']<=180]
 for name,n,box,kind,cx,mask in FIGURES:
  im=page(n,args.source_dir);a=np.array(im.convert('L'),dtype=float);bg=background(a);white=246 if kind=='tone' else 224
  clean=np.clip(np.clip(a/bg*255,0,255)*255/white,0,255).astype('uint8')
  for x0,y0,x1,y1 in mask:clean[y0:y1,x0:x1]=255
  crop=Image.fromarray(clean).crop(box);buf=io.BytesIO();crop.save(buf,format='PNG',dpi=(300,300));raw=buf.getvalue()
  out=ROOT/'assets'/f'{name}.png';out.write_bytes(raw);Image.open(out).load()
  records.append(dict(name=name,page=n,crop=box,kind=kind,content_center_px=cx,method=f'quadratic paper normalization; grayscale white point {white}',label_exclusions=mask,rotation_degrees=0,output_size=list(crop.size),sha256=hashlib.sha256(raw).hexdigest()))
  print(name,flush=True)
 (ROOT/'data/assets.json').write_text(json.dumps(records,indent=2)+'\n')
 inventory=json.loads((ROOT/'data/source_inventory.json').read_text());inventory['scope']='Title leaf (inferred page 1), printed pages 2–200. Leading blank excluded. Scan 101 right/page 201 is outside this checkpoint.';inventory['sources']=[]
 for n in range(1,102):
  f=args.source_dir/f'MarkVIII{n:03}.jpg';inventory['sources'].append(dict(filename=f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),size_bytes=f.stat().st_size))
 (ROOT/'data/source_inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
if __name__=='__main__':main()
