"""Reuse completed strict comparisons only for identical ordered BRep hashes and worker code."""
import argparse
import json
from pathlib import Path
import sys
H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path.insert(0, str(H.parents[1]))
from lib.evidence import read, write, sha

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, required=True)
a = p.parse_args()
out = a.candidate.resolve()
r = read(out / 'report.json')
target = read(out / 'isolated/manifest.json')
source = ROOT / r['source_native']
old = read(source.parent / 'isolated/manifest.json')
assert sha(source) == r['source_native_sha256'] == old['native_sha256']
assert sha(out / r['native_file']) == r['native_sha256'] == target['native_sha256']
worker_hash = sha(H / 'pump_integration_worker.py')
known = {}
for directory in [H / 'transmission_controls_study/us_nuts01', H / 'transmission_controls_study/integrated01', H / 'transmission_controls_study/channel_integrated01', H / 'transmission_controls_study/fulcrum_integrated01']:
    path = directory / 'definition_preservation_checks.json'
    qualification = read(directory / 'qualification.json')
    assert qualification['checks'][path.name] == sha(path)
    receipt = read(path)
    assert receipt['passed'] and receipt['worker_sha256'] == worker_hash
    for row in receipt['checks']:
        result = row.get('strict_material')
        if result and result['passed'] and result['worker_sha256'] == worker_hash:
            pair = result['source_sha256'], result['candidate_sha256']
            assert pair == (row['source_sha256'], row['candidate_sha256'])
            known[pair] = (result, path)
records = []
for name, before in old['definitions'].items():
    if name in r['changed_definitions']:
        continue
    after = target['definitions'][name]
    pair = before['brep_sha256'], after['brep_sha256']
    if pair[0] == pair[1] or pair not in known:
        continue
    assert all(sha(v['brep_path']) == v['brep_sha256'] for v in [before, after])
    work = out / 'preservation_runtime' / (pair[0] + '_' + pair[1])
    # Do not interfere with an already started worker, or replace any result.
    if (work / 'request.json').exists() or (work / 'result.json').exists():
        continue
    result, path = known[pair]
    work.mkdir(parents=True, exist_ok=True)
    with (work / 'result.json').open('x') as f:
        f.write(json.dumps(result, indent=2) + '\n')
    records.append(dict(definition=name, source_sha256=pair[0], candidate_sha256=pair[1],
                        reused_from=str(path.relative_to(ROOT)), receipt_sha256=sha(path),
                        result_sha256=sha(work / 'result.json')))
write(out / 'preservation_reuse.json', dict(records=records, worker_sha256=worker_hash,
      seeder_sha256=sha(Path(__file__)), native_sha256=r['native_sha256'],
      rule='Exact ordered BRep byte hashes, verified receipt and unchanged worker; no looser geometric matching or stale input reuse.'))
print('Reused', len(records), 'completed strict shape comparisons.', flush=True)
