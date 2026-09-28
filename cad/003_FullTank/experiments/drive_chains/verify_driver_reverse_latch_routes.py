"""Verify nonphysical latch-route evidence; do not promote witnesses as parts."""
import argparse
import hashlib
import json
from pathlib import Path

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
N = H / 'driver_foot_reverse_study'
F = N / 'reverse_latch_routes01'
RECEIPT = N / 'reverse_latch_routes_receipt.json'


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--freeze', action='store_true')
args = parser.parse_args()
if args.freeze:
    assert not RECEIPT.exists()
    deps = dict(read(N / 'reverse_quadrant_study_receipt.json')['dependencies'])

    def bind(path, digest=None):
        path = Path(path).resolve()
        rel = str(path.relative_to(ROOT))
        actual = sha(path)
        assert digest is None or actual == digest, rel
        assert rel not in deps or deps[rel] == actual, rel
        deps[rel] = actual

    bind(Path(__file__))
    bind(N / 'reverse_quadrant_study_receipt.json')
    bind(N / 'REVERSE_LATCH_ROUTES.md')
    bind(N / 'reverse_latch_routes_controls01.json')
    report = read(F / 'report.json')
    bind(H / 'probe_driver_reverse_latch_routes.py', report['worker_sha256'])
    for rel, digest in report['input_hashes'].items():
        bind(ROOT / rel, digest)
    seed = ROOT / report['controls']['seed']
    bind(seed / 'ControlRebuildTrial.FCStd', report['native_sha256'])
    assert report['context_occurrences'] == 9006 and report['no_mating_pair_exemptions']
    assert not any(report[k] for k in [
        'geometry_integrated', 'physical_parts_created', 'latch_qualified', 'source_camera_refitted',
    ])
    cases = {row['x_offset_mm']: row for row in report['cases']}
    assert set(cases) == {0, 20, -20}
    assert cases[20]['corridor_clear'] and not cases[0]['corridor_clear'] and not cases[-20]['corridor_clear']
    assert {r['other'] for r in cases[0]['rod_audit']['findings']} == {
        'DriverReverseOperatingLever', 'DriverSeatStarboardFrontStayLowerBolt',
    }
    assert {r['other'] for r in cases[-20]['rod_audit']['findings']} == {'DriverSeatStarboardFrontStay'}
    for case in cases.values():
        for key in ['rod', 'offset']:
            bind(F / case[key + '_brep'], case[key + '_brep_sha256'])
            audit = case[key + '_audit']
            assert audit['passed'] == all(row['passed'] for row in audit['pairs'])
            assert audit['findings'] == [row for row in audit['pairs'] if not row['passed']]
            for row in audit['pairs']:
                assert row['passed'] == (row['common_valid'] and row['common_mm3'] <= 1e-5)
    tooth = report['detent_tooth']
    bind(F / tooth['brep'], tooth['sha256'])
    assert tooth['audit']['passed'] and len(tooth['audit']['pairs']) == 4
    assert not tooth['audit']['findings']
    assert len(tooth['negative_controls']) == 2
    assert all(row['rejected'] and row['common_mm3'] > 1e-5 for row in tooth['negative_controls'])
    visual = read(F / 'visual_review.json')
    assert visual['native_sha256'] == report['native_sha256']
    assert visual['probe_sha256'] == sha(F / 'report.json')
    assert len(visual['reviewed_images']) == 6
    assert not visual['physical_parts_created'] and not visual['latch_qualified']
    for rel, digest in visual['reviewed_images'].items():
        bind(F / rel, digest)
    for rel, digest in visual['render_receipts'].items():
        bind(F / rel, digest)
        render = read(F / rel)
        assert render['probe_sha256'] == sha(F / 'report.json')
        assert render['native_sha256'] == report['native_sha256']
        suffix = '_v2' if rel.startswith('visual02/') else ''
        bind(H / ('render_driver_reverse_latch_routes' + suffix + '.py'), render['renderer_sha256'])
        for name, image_digest in render['images'].items():
            bind((F / rel).parent / name, image_digest)
    for path in sorted(F.rglob('*')):
        if path.is_file() and not any('runtime' in part or part == '__pycache__' for part in path.relative_to(F).parts):
            bind(path)
    for rel, digest in deps.items():
        assert sha(ROOT / rel) == digest, rel
    RECEIPT.write_text(json.dumps(dict(
        route_probe_reviewed=True, physical_parts_created=False, geometry_integrated=False,
        latch_qualified=False, selected_corridor_only_x_mm=20,
        dependencies=deps,
        scope='Three nonphysical straight-rod and offset witnesses against9006 saved occurrences; '
              'actual detent tooth and two penetrating negatives. No finished latch or part acceptance.',
    ), indent=2) + '\n')

receipt = read(RECEIPT)
assert receipt['route_probe_reviewed']
assert not any(receipt[k] for k in ['physical_parts_created', 'geometry_integrated', 'latch_qualified'])
for rel, digest in receipt['dependencies'].items():
    assert sha(ROOT / rel) == digest, rel
print('PASS', len(receipt['dependencies']), 'bound dependencies; nonphysical latch routes only.')
