"""Recheck the frozen conditional gate study; this does not qualify full handles."""
import argparse
from pathlib import Path
import sys

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path.insert(0, str(H.parents[1]))
from lib.evidence import read, sha

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, default=H / 'transmission_controls_study/driver_redo01/handle_gates01')
a = p.parse_args()
out = a.candidate.resolve()
proof = read(out / 'study_receipt.json')
assert proof['local_interface_checks_passed']
assert not any(proof[k] for k in ['geometry_integrated', 'historical_geometry_qualified', 'handle_engagement_qualified'])
for file, digest in proof['dependencies'].items():
    assert sha(ROOT / file) == digest, file
for folder in [out, ROOT / proof['variation']]:
    report = read(folder / 'report.json')
    native = folder / report['native_file']
    assert sha(native) == report['native_sha256']
    for name in ['checks03/independent_checks.json', 'context_audit/report.json', 'exchange01/exchange_checks.json']:
        q = read(folder / name)
        assert q['passed'] and q['native_sha256'] == sha(native), name
assert read(out / 'reproduction_checks.json')['passed']
visual = read(out / 'visual_review.json')
assert visual['disposition'] == 'conditional_interface_study'
assert visual['native_sha256'] == proof['native_sha256']
assert sha(out / 'ControlRebuildTrial.FCStd') == proof['native_sha256']
assert read(ROOT / proof['parent_qualification'])['local_static_checks_passed']
print('PASS conditional gate study;', len(proof['dependencies']),
      'bound dependencies. Full handles, hardware and integration remain open.')
