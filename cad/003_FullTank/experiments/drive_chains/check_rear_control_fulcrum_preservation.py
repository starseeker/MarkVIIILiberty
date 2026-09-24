"""Compare every inherited definition against the saved pre-channel powertrain parent."""
import argparse
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
STAGE = HERE.parents[1]
ROOT = STAGE.parents[1]
sys.path.insert(0, str(STAGE))
from lib import runtime
from lib.evidence import read, write, sha

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, required=True)
a = p.parse_args()
out = a.candidate.resolve()
report = read(out / 'report.json')
source = ROOT / report['source_native']
target_manifest = read(out / 'isolated/manifest.json')
source_manifest = read(source.parent / 'isolated/manifest.json')
qualification = read(out / 'independent_checks.json')
assert qualification['passed']
assert sha(out / report['native_file']) == report['native_sha256'] == target_manifest['native_sha256'] == qualification['native_sha256']
assert sha(source) == report['source_native_sha256'] == source_manifest['native_sha256']
assert target_manifest['definitions'].keys() == source_manifest['definitions'].keys() | set(report['new_definitions'])
changed = set(report['changed_definitions'])
assert changed == {'Def_RearControlMount_channel'}
assert len(source_manifest['definitions']) == 551
assert len(report['new_definitions']) == 7
worker = HERE / 'pump_integration_worker.py'
worker_hash = sha(worker)
area = out / 'preservation_runtime'
area.mkdir(exist_ok=True)
records = []
for name, target in sorted(target_manifest['definitions'].items()):
    if name in changed or name in report['new_definitions']:
        continue
    old = source_manifest['definitions'][name]
    assert old['properties'] == target['properties'], name
    for definition in [old, target]:
        assert sha(Path(definition['brep_path'])) == definition['brep_sha256']
    pair = old['brep_sha256'], target['brep_sha256']
    exact = pair[0] == pair[1]
    result = None
    if not exact:
        work = area / (pair[0] + '_' + pair[1])
        work.mkdir(exist_ok=True)
        request = dict(definition=name, source_path=old['brep_path'],
                       candidate_path=target['brep_path'], source_sha256=pair[0],
                       candidate_sha256=pair[1])
        write(work / 'request.json', request)
        result_path = work / 'result.json'
        if not result_path.exists():
            with (work / 'run.log').open('w') as log:
                subprocess.run([sys.executable, str(worker), 'material', '--input',
                                str(work / 'request.json'), '--output', str(result_path)],
                               env=runtime.environment(work), stdout=log,
                               stderr=subprocess.STDOUT, check=True)
        result = read(result_path)
        assert (result['source_sha256'], result['candidate_sha256']) == pair
        assert result['worker_sha256'] == worker_hash
        print('Strict material', name, result['passed'], flush=True)
    records.append(dict(definition=name, source_sha256=pair[0], candidate_sha256=pair[1],
                        exact_brep=exact, strict_material=result,
                        passed=exact or result['passed']))
    write(out / 'definition_preservation_progress.json', records)
result = dict(passed=all(v['passed'] for v in records), native_sha256=report['native_sha256'],
              source_native_sha256=sha(source), checker_sha256=sha(Path(__file__)),
              worker_sha256=worker_hash, checks=records, definition_count=len(records),
              exact_count=sum(v['exact_brep'] for v in records),
              strict_count=sum(not v['exact_brep'] for v in records),
              intentionally_rebuilt_definitions=sorted(changed),
              local_rebuild_qualification_sha256=sha(out / 'independent_checks.json'),
              scope='All550 unchanged inherited definitions preserved. The revised channel and seven new definitions match the independently tested fulcrum prototype; eight-definition and25-installed-shape transfer is checked separately. Does not qualify placements or historical interpretation.',
              installation_qualified=False)
write(out / 'definition_preservation_checks.json', result)
assert result['passed'] and len(records) == 550
