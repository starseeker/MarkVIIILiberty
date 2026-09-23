"""Balanced paired tool-enabled trials. Sequential execution preserves isolation."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/cad_packets'))
from common import read,sha,write

HERE=Path(__file__).resolve().parent
SCHEDULE=[('stack','medium'),('stack','xhigh'),('mount','xhigh'),('mount','medium'),('spring','medium'),('spring','xhigh')]


def main():
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int,default=6);a=p.parse_args()
    protocol=dict(model='gpt-6-astra',timeout_seconds=480,repeats=1,schedule=SCHEDULE,
                  runner_sha256=sha(Path(__file__)),protocol_sha256=sha(HERE/'PROTOCOL.md'),
                  mode='shadow',automatic_production_promotion=False)
    frozen=HERE/'results/protocol.json'
    if frozen.exists():
        assert read(frozen)==read_protocol(protocol),'Protocol changed; assign a new experiment'
    else:write(frozen,protocol)
    for index,(case,effort) in enumerate(SCHEDULE[:a.limit],1):
        run=f'shadow01_{case}_{effort}'
        write(HERE/'results/progress.json',dict(index=index,total=len(SCHEDULE),run=run,state='running'))
        code=subprocess.call([sys.executable,str(ROOT/'tools/cad_packets/controller.py'),'run',
            str(HERE/'packets'/(case+'.json')),'--id',run,'--effort',effort,'--timeout','480'])
        if code not in (0,2):raise RuntimeError('Infrastructure or provenance failure: '+run)
    write(HERE/'results/progress.json',dict(state='complete' if a.limit>=6 else 'partial',completed=min(a.limit,6),total=6))


def read_protocol(p):
    import json
    return json.loads(json.dumps(p))


if __name__=='__main__':main()
