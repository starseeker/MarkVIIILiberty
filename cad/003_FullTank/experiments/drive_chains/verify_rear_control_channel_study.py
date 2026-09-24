"""Read-only freshness check for the unfinished rear-channel evidence study."""
import json
from pathlib import Path
import sys

H=Path(__file__).resolve().parent;ROOT=H.parents[3];sys.path.insert(0,str(H.parents[1]))
from lib.evidence import read,sha

receipt=H/'transmission_controls_study/channel_study_receipt01.json'
r=read(receipt);failed=[]
for path,digest in r['dependencies'].items():
    f=ROOT/path
    if not f.is_file() or sha(f)!=digest:failed.append(path)
if failed:
    print(json.dumps(dict(current=False,changed=failed,action='Review affected evidence before reusing it'),indent=2))
    raise SystemExit(1)
assert r['stock_checks_passed'] and not r['channel_assembly_complete'] and not r['historical_geometry_qualified']
print('Rear-channel study current:',len(r['dependencies']),'dependencies; unfinished stock only, source pin discrepancy retained; no CAD recomputation or automatic acceptance.')
