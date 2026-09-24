"""Read-only dependency verification for the mounted rear-channel development increment."""
import argparse
from pathlib import Path
import subprocess
import sys
H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path.insert(0, str(H.parents[1]))
from lib.evidence import read, sha

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, default=H / 'transmission_controls_study/channel_integrated01')
a = p.parse_args()
out = a.candidate.resolve()
q = read(out / 'qualification.json')
failed = [path for path, digest in q['dependencies'].items()
          if not (ROOT / path).is_file() or sha(ROOT / path) != digest]
if failed:
    print('Changed or missing dependencies:', *failed, sep='\n')
    raise SystemExit(1)
assert q['local_static_checks_passed'] and not q['channel_complete'] and not q['historical_geometry_qualified']
assert q['counts']['occurrences'] == 3202
r = read(out / 'report.json')
assert sha(out / r['native_file']) == q['native_sha256'] == r['native_sha256']
for file in q['checks']:
    receipt = read(out / file)
    assert receipt['passed'] and receipt['native_sha256'] == q['native_sha256']
subprocess.run([sys.executable, str(H / 'verify_transmission_control_checkpoint.py'),
                '--candidate', str((ROOT / r['source_native']).parent)], check=True)
subprocess.run([sys.executable, str(H / 'verify_rear_control_channel_study.py')], check=True)
print('Rear-channel mounting checkpoint current:', len(q['dependencies']),
      'dependencies; saved local checks reused, camera unchanged; complete channel and tank remain open.')
