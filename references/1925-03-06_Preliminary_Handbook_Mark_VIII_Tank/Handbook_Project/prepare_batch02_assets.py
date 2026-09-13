#!/usr/bin/env python3
"""Prepare only Plates 12–31; preserve all first-batch artwork files."""
from pathlib import Path
import argparse,json,hashlib,io
from PIL import Image
import numpy as np
from prepare_assets import page,background
ROOT=Path(__file__).resolve().parent
# name, page, native crop pixels, treatment, page content center, erased outside-art plate label rectangles
FIGURES=[
('plate12',21,[160,140,1535,1300],'line',845,[]),
('plate13',21,[155,1570,1535,2230],'line',845,[]),
('plate14',22,[285,365,1510,1710],'line',895,[[1190,480,1445,518]]),
('plate15',23,[205,130,1430,1410],'line',815,[]),
('plate16',24,[270,145,1540,1250],'line',900,[]),
('plate17',25,[480,350,1120,1360],'line',810,[]),
('plate18',26,[425,245,1400,1810],'line',900,[[1105,247,1370,285]]),
('plate19',27,[195,250,1455,1090],'line',825,[]),
('plate20',27,[180,1320,1480,2170],'line',825,[]),
('plate21',28,[385,140,1375,2395],'line',890,[]),
('plate22',29,[125,660,1520,2020],'tone',825,[]),
('plate23',30,[220,190,1590,1655],'tone',900,[]),
('plate24',31,[130,1570,1480,2055],'tone',800,[]),
('plate25',33,[165,545,1510,1655],'tone',840,[]),
('plate26',34,[255,108,1635,2380],'tone',935,[]),
('plate27',36,[255,185,1620,1685],'line',950,[]),
('plate28',37,[345,345,1520,2050],'line',920,[]),
('plate29',38,[290,890,1540,1405],'line',915,[]),
('plate30',39,[210,460,1595,1485],'tone',905,[[1330,480,1592,520]]),
('plate31',40,[270,750,1620,1605],'line',950,[]),
]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source-dir',type=Path,default=ROOT.parent);args=ap.parse_args()
 records=[a for a in json.loads((ROOT/'data/assets.json').read_text()) if a['page']<=20]
 for name,n,box,kind,cx,mask in FIGURES:
  im=page(n,args.source_dir);a=np.array(im.convert('L'),dtype=float);bg=background(a);white=246 if kind=='tone' else 224
  clean=np.clip(np.clip(a/bg*255,0,255)*255/white,0,255).astype('uint8')
  for x0,y0,x1,y1 in mask:clean[y0:y1,x0:x1]=255
  crop=Image.fromarray(clean).crop(box);b=io.BytesIO();crop.save(b,format='PNG',dpi=(300,300));raw=b.getvalue()
  out=ROOT/'assets'/f'{name}.png';out.write_bytes(raw);Image.open(out).load()
  records.append(dict(name=name,page=n,crop=box,kind=kind,content_center_px=cx,method=f'quadratic paper normalization; grayscale white point {white}',label_exclusions=mask,rotation_degrees=0,output_size=list(crop.size),sha256=hashlib.sha256(raw).hexdigest()))
  print(name,flush=True)
 (ROOT/'data/assets.json').write_text(json.dumps(records,indent=2))
 inventory=json.loads((ROOT/'data/source_inventory.json').read_text());inventory['scope']='Title leaf (inferred page 1), printed pages 2–40. Leading blank excluded. Scan 021 right/page 41 is outside this checkpoint.'
 inventory['sources']=[]
 for n in range(1,22):
  f=args.source_dir/f'MarkVIII{n:03}.jpg';inventory['sources'].append(dict(filename=f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),size_bytes=f.stat().st_size))
 (ROOT/'data/source_inventory.json').write_text(json.dumps(inventory,indent=2))
if __name__=='__main__':main()
