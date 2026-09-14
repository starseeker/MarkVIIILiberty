#!/usr/bin/env python3
"""Prepare Plates 119–130 and the unnumbered page 212 curves by deterministic paper normalization only."""
from pathlib import Path
import argparse,json,hashlib,io
from PIL import Image
import numpy as np
from prepare_assets import page,background
ROOT=Path(__file__).resolve().parent
FIGURES=[
 ('plate119',202,[190,490,1580,1960],'tone',885,[]),
 ('plate120',204,[180,175,1670,898],'tone',905,[]),
 ('plate121',204,[195,1090,1650,2275],'tone',905,[[1608,1360,1642,1440]]),
 ('plate122',206,[262,600,1550,1840],'tone',898,[]),
 ('plate123',208,[160,125,1602,2445],'tone',880,[]),
 ('plate124',210,[150,376,1622,1125],'tone',884,[]),
 ('plate125',210,[182,1410,1520,2034],'tone',856,[]),
 ('p212_speed_curves',212,[214,118,1600,903],'line',900,[[1580,520,1610,600]]),
 ('p212_governor_curves',212,[215,990,1590,2300],'line',900,[]),
 ('plate127',214,[180,602,1710,1880],'tone',950,[]),
 ('plate128',216,[249,765,1640,1795],'tone',948,[]),
 ('plate129',218,[340,140,1540,2390],'line',942,[]),
 ('plate130',220,[260,208,1665,2205],'tone',945,[[1510,430,1630,580]])]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source-dir',type=Path,required=True);args=ap.parse_args()
 records=[a for a in json.loads((ROOT/'data/assets.json').read_text()) if a['page']<=200]
 for name,n,box,kind,cx,mask in FIGURES:
  im=page(n,args.source_dir);a=np.array(im.convert('L'),dtype=float);bg=background(a);white=246 if kind=='tone' else 224
  clean=np.clip(np.clip(a/bg*255,0,255)*255/white,0,255).astype('uint8')
  # Only confirmed blank-paper marks: interpolate the surrounding paper tone.
  # Preserve the local gutter gradient so no white rectangular patch is visible.
  for x0,y0,x1,y1 in mask:
   l=np.median(clean[y0:y1,max(0,x0-5):x0].astype(float),axis=1)
   r=np.median(clean[y0:y1,x1:x1+5].astype(float),axis=1)
   blend=np.linspace(0,1,x1-x0)[None,:]
   clean[y0:y1,x0:x1]=np.rint(l[:,None]*(1-blend)+r[:,None]*blend).astype('uint8')
  crop=Image.fromarray(clean).crop(box);buf=io.BytesIO();crop.save(buf,format='PNG',dpi=(300,300));raw=buf.getvalue()
  out=ROOT/'assets'/f'{name}.png';out.write_bytes(raw);Image.open(out).load()
  records.append(dict(name=name,page=n,crop=box,kind=kind,content_center_px=cx,method=f'quadratic paper normalization; grayscale white point {white}',label_exclusions=mask,blank_paper_repair='horizontal interpolation from five-pixel side bands' if mask else None,rotation_degrees=0,output_size=list(crop.size),sha256=hashlib.sha256(raw).hexdigest()))
  print(name,flush=True)
 (ROOT/'data/assets.json').write_text(json.dumps(records,indent=2)+'\n')
 inventory=json.loads((ROOT/'data/source_inventory.json').read_text());inventory['scope']='Title leaf (inferred page 1), printed pages 2–220. Leading blank excluded. Scan 111 right/page 221 is outside this checkpoint.';inventory['sources']=[]
 for n in range(1,112):
  f=args.source_dir/f'MarkVIII{n:03}.jpg';inventory['sources'].append(dict(filename=f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),size_bytes=f.stat().st_size))
 (ROOT/'data/source_inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
if __name__=='__main__':main()
