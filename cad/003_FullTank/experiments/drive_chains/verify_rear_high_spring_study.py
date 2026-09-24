"""Read-only recovery of the unintegrated M4135 guide and local route study."""
import argparse
from pathlib import Path
import subprocess
import sys

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path.insert(0, str(H.parents[1]))
from lib.evidence import read, sha


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def verify(study):
    q = read(study / 'high_spring_study_receipt01.json')
    failed = [path for path, digest in q['dependencies'].items()
              if not (ROOT / path).is_file() or sha(ROOT / path) != digest]
    require(not failed, 'Changed or missing dependencies:\n' + '\n'.join(failed))
    require(q['local_static_checks_passed'], 'Local checks are not recorded as passed')
    require(not any(q[name] for name in [
        'geometry_integrated', 'packet_complete', 'complete_rod_qualified',
        'historical_geometry_qualified', 'standard_assembly_modified',
        'source_camera_refitted']), 'Study scope changed')
    parent = read(study / 'fulcrum_integrated01/report.json')
    require(q['parent_native_sha256'] == parent['native_sha256'], 'Wrong parent')
    for candidate, route in [('high_spring04', 'high_spring_routes04'),
                             ('high_spring_variation04', 'high_spring_routes_variation04')]:
        out = study / candidate
        report = read(out / 'report.json')
        digest = sha(out / report['native_file'])
        require(digest == report['native_sha256'] == q['native_hashes'][candidate],
                'Native identity changed: ' + candidate)
        require(report['parent_native_sha256'] == q['parent_native_sha256'],
                'Prototype parent changed: ' + candidate)
        require(not report['geometry_integrated'], 'Prototype claimed as integrated')
        require(report['prototype_physical_occurrences'] == 7 and
                report['prototype_definition_count'] == 3 and
                report['new_physical_occurrences'] == 6, 'Wrong prototype counts')
        for file, expected in [('independent_checks.json', 32),
                               ('context_checks.json', 2), ('exchange_checks.json', 10)]:
            check = read(out / file)
            rows = check['pairs'] if file == 'context_checks.json' else check['checks']
            require(check['passed'] and check['native_sha256'] == digest and
                    len(rows) == expected and all(r['passed'] for r in rows),
                    'Wrong check result: ' + candidate + '/' + file)
        routes = read(study / route / 'route_checks.json')
        require(routes['passed'] and routes['trial_native_sha256'] == digest and
                len(routes['pairs']) == 29 and all(r['passed'] for r in routes['pairs']),
                'Wrong local route result: ' + route)
        require(routes['parent_native_sha256'] == q['parent_native_sha256'],
                'Route parent changed')
    for file in ['high_spring04/reproduction_checks.json',
                 'spring_sources01/reproduction_checks.json']:
        require(read(study / file)['passed'], 'Reproduction did not pass: ' + file)
    # An earlier successful bracket check must not hide its later route failure.
    rejected = read(study / 'high_spring_routes03/route_checks.json')
    require(not rejected['passed'] and any(not p['passed'] for p in rejected['pairs']),
            'Earlier route failure was lost')
    for file in ['high_spring04/render_receipt.json',
                 'high_spring_routes04/render_receipt.json']:
        render = read(study / file)
        require(not render['source_camera_refitted'] and
                render['source_registration_sha256'] == q['source_registration_sha256'],
                'Saved camera changed')
    subprocess.run([sys.executable, str(H / 'verify_rear_control_fulcrum_checkpoint.py')],
                   check=True)
    print('Rear high-speed spring study current:', len(q['dependencies']),
          'dependencies; nominal/stock/local-route receipts reused; unintegrated,',
          'historical route discrepancy and complete tank remain open.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--study', type=Path,
                        default=H / 'transmission_controls_study')
    verify(parser.parse_args().study.resolve())
