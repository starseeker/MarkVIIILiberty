#!/usr/bin/env python3
"""Prepare Plates 131–143 by deterministic paper normalization only."""
from pathlib import Path
import argparse,json,hashlib,io
from PIL import Image
import numpy as np
from prepare_assets import page,background
ROOT=Path(__file__).resolve().parent
FIGURES=[('plate131', 222, [262, 675, 1640, 1818], 'tone', 987, []), ('plate132', 224, [335, 288, 1730, 2038], 'tone', 1041, []), ('plate133', 226, [285, 445, 1650, 2070], 'tone', 980, [[1560, 434, 1606, 465], [309, 422, 582, 471]]), ('plate134', 228, [112, 663, 1560, 1810], 'tone', 875, []), ('plate135', 230, [166, 609, 1680, 1700], 'tone', 915, []), ('plate136', 232, [170, 75, 1670, 812], 'tone', 930, [[214, 115, 486, 157]]), ('plate137', 232, [215, 900, 1620, 1720], 'tone', 930, []), ('plate138', 232, [165, 1785, 1670, 2495], 'tone', 930, []), ('plate139', 234, [503, 242, 1425, 1075], 'tone', 932, []), ('plate140', 234, [583, 1274, 1310, 2198], 'tone', 947, []), ('plate141', 236, [448, 163, 1385, 2405], 'line', 945, []), ('plate142', 238, [687, 162, 1230, 1230], 'line', 936, []), ('plate143', 238, [509, 1336, 1315, 2424], 'line', 901, [])]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source-dir',type=Path,required=True);args=ap.parse_args()
 records=[a for a in json.loads((ROOT/'data/assets.json').read_text()) if a['page']<=220]
 for name,n,box,kind,cx,mask in FIGURES:
  im=page(n,args.source_dir);a=np.array(im.convert('L'),dtype=float);bg=background(a);white=246 if kind=='tone' else 224
  clean=np.clip(np.clip(a/bg*255,0,255)*255/white,0,255).astype('uint8')
  # Source Plate 133/136 labels and one confirmed blank-paper stain above Plate 133:
  # interpolate the surrounding paper tone.
  # Preserve the local gutter gradient so no white rectangular patch is visible.
  for x0,y0,x1,y1 in mask:
   l=np.median(clean[y0:y1,max(0,x0-5):x0].astype(float),axis=1)
   r=np.median(clean[y0:y1,x1:x1+5].astype(float),axis=1)
   blend=np.linspace(0,1,x1-x0)[None,:]
   clean[y0:y1,x0:x1]=np.rint(l[:,None]*(1-blend)+r[:,None]*blend).astype('uint8')
  crop=Image.fromarray(clean).crop(box);buf=io.BytesIO();crop.save(buf,format='PNG',dpi=(300,300));raw=buf.getvalue()
  out=ROOT/'assets'/f'{name}.png';out.write_bytes(raw);Image.open(out).load()
  records.append(dict(name=name,page=n,crop=box,kind=kind,content_center_px=cx,method=f'quadratic paper normalization; grayscale white point {white}',label_exclusions=mask if name=="plate136" else mask[1:] if name=="plate133" else [],blank_paper_masks=mask[:1] if name=="plate133" else [],blank_paper_repair='horizontal interpolation from five-pixel side bands' if mask else None,rotation_degrees=0,output_size=list(crop.size),sha256=hashlib.sha256(raw).hexdigest()))
  print(name,flush=True)
 (ROOT/'data/assets.json').write_text(json.dumps(records,indent=2)+'\n')
 inventory=json.loads((ROOT/'data/source_inventory.json').read_text());inventory['scope']='Title leaf (inferred page 1), printed pages 2–240. Leading blank excluded. Scan 121 right/page 241 is outside this checkpoint.';inventory['sources']=[]
 for n in range(1,122):
  f=args.source_dir/f'MarkVIII{n:03}.jpg';inventory['sources'].append(dict(filename=f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),size_bytes=f.stat().st_size))
 (ROOT/'data/source_inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
if __name__=='__main__':main()
