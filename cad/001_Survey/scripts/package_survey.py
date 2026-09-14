#!/usr/bin/env python3
"""Package this folder under its repository-relative path, with file hashes."""
from pathlib import Path
import argparse,hashlib,json,zipfile
HERE=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);args=ap.parse_args()
out=args.output.resolve();out.parent.mkdir(parents=True,exist_ok=True)
def selected():
 return sorted(p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.zip') and not p.name.endswith(('-journal','-wal','-shm')) and p.name!='package_manifest.json')
files=selected()
manifest={'source_commit':json.loads((HERE/'inputs/source_manifest.json').read_text())['commit'],'layout':'cad/001_Survey/','note':'Hashes cover all other files in this package. Original source PDFs/images remain in the pinned repository.','files':[{'path':p.relative_to(HERE).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
(HERE/'package_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in files+[HERE/'package_manifest.json']:z.write(p,'cad/001_Survey/'+p.relative_to(HERE).as_posix())
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 for r in manifest['files']:
  data=z.read('cad/001_Survey/'+r['path'])
  assert len(data)==r['bytes'] and hashlib.sha256(data).hexdigest()==r['sha256']
print(json.dumps({'output':str(out),'files':len(files)+1,'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'all_packaged_hashes_verified':True},indent=2))
