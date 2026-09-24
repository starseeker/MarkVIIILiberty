"""Read-only recovery check for the four retained rear-control fulcrum units."""
import argparse
from pathlib import Path
import subprocess
import sys

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path.insert(0, str(H.parents[1]))
from lib.evidence import read, sha

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path,
               default=H / 'transmission_controls_study/fulcrum_integrated01')
a = p.parse_args()
out = a.candidate.resolve()
q = read(out / 'qualification.json')
failed = [path for path, digest in q['dependencies'].items()
          if not (ROOT / path).is_file() or sha(ROOT / path) != digest]
if failed:
    print('Changed or missing dependencies:', *failed, sep='\n')
    raise SystemExit(1)
assert q['local_static_checks_passed']
assert not any(q[name] for name in ['channel_complete', 'historical_geometry_qualified',
                                  'standard_assembly_modified', 'source_camera_refitted'])
assert q['counts']['occurrences'] == 3226
r = read(out / 'report.json')
assert sha(out / r['native_file']) == q['native_sha256'] == r['native_sha256']
for file, digest in q['checks'].items():
    receipt = read(out / file)
    assert sha(out / file) == digest
    assert receipt['passed'] and receipt['native_sha256'] == q['native_sha256']
subprocess.run([sys.executable, str(H / 'verify_rear_control_mount_checkpoint.py'),
                '--candidate', str((ROOT / r['source_native']).parent)], check=True)
print('Rear-control fulcrum checkpoint current:', len(q['dependencies']),
      'dependencies; saved checks and fixed source camera reused; complete tank remains open.')
