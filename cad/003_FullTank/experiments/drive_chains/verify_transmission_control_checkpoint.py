"""Read-only receipt freshness check; does not execute CAD or accept new geometry."""
import argparse,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[3];sys.path.insert(0,str(H.parents[1]))
from lib.evidence import read,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args()
seen=set();checked=0
def inspect(folder):
    global checked
    folder=folder.resolve();assert folder not in seen;seen.add(folder)
    q=read(folder/'qualification.json');r=read(folder/'report.json');m=read(folder/'isolated/manifest.json')
    assert q['local_static_checks_passed'] and sha(folder/r['native_file'])==q['native_sha256']==r['native_sha256']==m['native_sha256']
    for name,digest in q['input_hashes'].items():assert sha(ROOT/name)==digest,name;checked+=1
    for name,digest in q['checks'].items():
        f=folder/name;assert sha(f)==digest,name;data=read(f);checked+=1
        assert data.get('passed',True) and data['native_sha256']==q['native_sha256'],name
        for step,digest in data.get('step_hashes',{}).items():assert sha(f.parent/step)==digest,step;checked+=1
    if q.get('parent_control_checkpoint'):inspect(ROOT/q['parent_control_checkpoint'])
inspect(a.candidate)
print('Control checkpoint evidence current:',len(seen),'checkpoint(s),',checked,'hashed dependencies/receipts; CAD checks reused, no automatic historical acceptance.')
