"""Rebuild archived candidate scripts in fresh sandboxes, then recheck their CAD."""
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/cad_packets'))
from common import HERE,RUNS,read,sha,write
from controller import verify_record
from isolation import execute,sandbox


def reproduce(run):
    saved=RUNS/run
    request,result=verify_record(saved)
    if not result['mechanical_pass']:raise ValueError('Only completed passing geometry trials are replayed')
    packet=read(saved/'packet.json')
    work=ROOT/'.work/cad-packets/reproduction'/run
    out=RUNS/'reproduction'/run
    if out.exists():raise ValueError('Preserve existing reproduction evidence')
    out.mkdir(parents=True);(work/'inputs').mkdir(parents=True);(work/'deliverables').mkdir()
    shutil.copyfile(saved/'packet.json',work/'inputs/packet.json')
    for row in packet['inputs']:
        dst=work/'inputs'/row['destination'];dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/row['source'],dst)
    shutil.copyfile(HERE/'freecad_python.py',work/'freecad_python.py')
    shutil.copyfile(saved/'artifacts/deliverables/build.py',work/'deliverables/build.py')
    cmd=sandbox(work,[work/'inputs',work/'freecad_python.py'],[work],
                ['python3','freecad_python.py','deliverables/build.py'])
    launch=execute(cmd,work,out/'build.stdout',out/'build.stderr',120)
    grade=dict(passed=False,error='Builder did not finish successfully')
    if launch['returncode']==0:
        artifacts=out/'artifacts/deliverables';artifacts.mkdir(parents=True)
        for src in (work/'deliverables').iterdir():
            if src.is_file() and (src.suffix in ('.FCStd','.step','.json') or src.name=='build.py'):
                shutil.copyfile(src,artifacts/src.name)
        validation=out/'validation';validation.mkdir()
        cmd=sandbox(validation,[HERE,saved/'packet.json',out/'artifacts',work/'inputs'],[validation],
                    ['python3',HERE/'freecad_python.py',ROOT/packet['validator'],'--packet',saved/'packet.json',
                     '--inputs',work/'inputs','--artifacts',out/'artifacts','--out',validation/'grade.json'])
        checked=execute(cmd,validation,out/'validation.stdout',out/'validation.stderr',120)
        if checked['returncode']==0 and (validation/'grade.json').exists():grade=read(validation/'grade.json')
    write(out/'result.json',dict(passed=bool(grade.get('passed')),launch=launch,grade=grade,
           original_result_sha256=sha(saved/'result.json'),builder_sha256=sha(work/'deliverables/build.py'),
           evidence_hashes={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file() and 'runtime' not in p.parts}))
    print(run, 'reproduced=',grade.get('passed'),flush=True)


if __name__=='__main__':
    for run in sys.argv[1:]:reproduce(run)
