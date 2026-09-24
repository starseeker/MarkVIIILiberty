"""Qualify final definition material directly against merged pumps and rebuilt engine supports."""
import argparse
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
STAGE = HERE.parents[1]
ROOT = STAGE.parents[1]
sys.path[:0] = [str(STAGE)]
from lib import runtime
from lib.evidence import read, write, sha

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, required=True)
a = p.parse_args()
out = a.candidate.resolve()
r = read(out/'report.json')
m = read(out/'isolated/manifest.json')
assert sha(out/r['native_file'])==r['native_sha256']==m['native_sha256']
baseline = HERE/'engine_pump_receiver_study/assembly_trial02'
br = read(baseline/'report.json')
bm = read(baseline/'isolated/candidate/manifest.json')
qualified = read(baseline/'independent_checks.json')
assert qualified['passed'] and qualified['native_sha256']==br['native_sha256']==bm['native_sha256']
assert sha(baseline/br['native_file'])==br['native_sha256']
support = ROOT/r['source_native']
sm = read(support.parent/'isolated/manifest.json')
sc = read(support.parent/'independent_checks.json')
assert sha(support)==sm['native_sha256']==sc['native_sha256'] and sc['local_support_checks_passed']
changed = {'Def_EngineSuspension_'+name+'_bracket' for name in ['left','right','front']}
assert m['definitions'].keys()==bm['definitions'].keys()==sm['definitions'].keys()
worker = HERE/'pump_integration_worker.py'
worker_hash = sha(worker)
area = out/'preservation_runtime'
area.mkdir(exist_ok=True)
records = []
for name,target in sorted(m['definitions'].items()):
    parent = sm if name in changed else bm
    source = parent['definitions'][name]
    for definition in [source,target]:
        assert sha(Path(definition['brep_path']))==definition['brep_sha256']
    assert source['properties']==target['properties']
    pair = source['brep_sha256'],target['brep_sha256']
    exact = pair[0]==pair[1]
    result = None
    if not exact:
        work = area/(pair[0]+'_'+pair[1])
        work.mkdir(exist_ok=True)
        request = dict(definition=name,source_path=source['brep_path'],candidate_path=target['brep_path'],
                       source_sha256=pair[0],candidate_sha256=pair[1])
        write(work/'request.json',request)
        result_path = work/'result.json'
        if not result_path.exists():
            with (work/'run.log').open('w') as log:
                subprocess.run([sys.executable,str(worker),'material','--input',str(work/'request.json'),
                                '--output',str(result_path)],env=runtime.environment(work),
                               stdout=log,stderr=subprocess.STDOUT,check=True)
        result = read(result_path)
        assert (result['source_sha256'],result['candidate_sha256'])==pair
        assert result['worker_sha256']==worker_hash
        print('Strict material',name,result['passed'],flush=True)
    records.append(dict(definition=name,baseline='rebuilt_engine_supports' if name in changed else 'merged_pumps',
        source_sha256=pair[0],candidate_sha256=pair[1],exact_brep=exact,
        strict_material=result,passed=exact or result['passed']))
    write(out/'definition_preservation_progress.json',records)
result = dict(passed=all(v['passed'] for v in records),native_sha256=r['native_sha256'],
    checker_sha256=sha(Path(__file__)),worker_sha256=worker_hash,checks=records,
    baseline_native_sha256=br['native_sha256'],support_native_sha256=sha(support),
    baseline_qualification_sha256=sha(baseline/'independent_checks.json'),
    support_qualification_sha256=sha(support.parent/'independent_checks.json'),
    definition_count=len(records),exact_count=sum(v['exact_brep'] for v in records),
    strict_count=sum(not v['exact_brep'] for v in records),
    scope='All final definition material compared directly with qualified merged pumps, except three intentionally rebuilt engine brackets compared with their locally checked saved source. Does not qualify placements or historical interpretation.',
    installation_qualified=False)
write(out/'definition_preservation_checks.json',result)
assert result['passed'] and len(records)==461
