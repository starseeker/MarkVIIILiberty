#!/usr/bin/env python3
"""Fetch the checkpoint's hash-pinned source spreads, sequentially and resumably."""
from pathlib import Path
import hashlib,json,urllib.request,argparse
ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--destination',type=Path,default=ROOT.parent);a=ap.parse_args();a.destination.mkdir(parents=True,exist_ok=True)
manifest=json.loads((ROOT/'data/source_inventory.json').read_text())
base='https://raw.githubusercontent.com/starseeker/MarkVIIILiberty/main/'+manifest['source_directory']+'/'
for row in manifest['sources']:
 p=a.destination/row['filename']
 def valid(b):return len(b)==row['size_bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
 if p.exists():
  if not valid(p.read_bytes()):raise RuntimeError('Existing source differs; retained without overwrite: '+str(p))
  print(p.name,'already verified');continue
 for attempt in range(3):
  try:
   with urllib.request.urlopen(base+row['filename'],timeout=60) as r:b=r.read()
   if not valid(b):raise RuntimeError('Downloaded source does not match checkpoint')
   temp=p.with_suffix(p.suffix+'.part');temp.write_bytes(b);temp.replace(p);print(p.name,'verified');break
  except Exception:
   if attempt==2:raise
