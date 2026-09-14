"""Fetch pinned staged originals and verify SHA-256, in a selected scan range."""
from pathlib import Path
import argparse,json,hashlib,urllib.request
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--first',type=int,default=21);p.add_argument('--last',type=int,default=40);p.add_argument('--output',type=Path,default=ROOT/'sources');a=p.parse_args()
inv=json.loads((ROOT/'data/source_inventory.json').read_text());a.output.mkdir(parents=True,exist_ok=True)
for f in inv['sources']:
 if not a.first<=f['leaf']<=a.last:continue
 dest=a.output/f['filename']
 if dest.exists() and hashlib.sha256(dest.read_bytes()).hexdigest()==f['sha256']:continue
 url='https://raw.githubusercontent.com/starseeker/MarkVIIILiberty/'+inv['commit']+'/'+inv['source_directory']+'/'+f['filename']
 data=urllib.request.urlopen(url,timeout=60).read()
 if hashlib.sha256(data).hexdigest()!=f['sha256']:raise RuntimeError('Source hash mismatch: '+f['filename'])
 tmp=dest.with_suffix('.download');tmp.write_bytes(data);tmp.replace(dest);print(f['filename'])
