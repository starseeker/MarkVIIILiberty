"""Read-only recovery of the unintegrated M4136 supports and corridor witnesses."""
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


def verify():
    C = H/'transmission_controls_study'
    q = read(C/'low_spring_study_receipt01.json')
    failed = [p for p, h in q['dependencies'].items()
              if not (ROOT/p).is_file() or sha(ROOT/p) != h]
    require(not failed, 'Changed or missing evidence:\n'+'\n'.join(failed))
    require(q['local_static_checks_passed'] and not any(q[k] for k in [
        'geometry_integrated', 'packet_complete', 'historical_geometry_qualified',
        'complete_rods_or_springs_qualified', 'source_camera_refitted',
        'standard_assembly_modified']), 'Study scope changed')
    for suffix in ['04', '_variation04']:
        out = C/('low_spring'+suffix)
        r = read(out/'report.json')
        digest = sha(out/r['native_file'])
        require(digest == r['native_sha256'] == q['native_hashes'][out.name],
                'Native identity changed')
        require(r['parent_native_sha256'] == q['parent_native_sha256'] and
                r['receiver_native_sha256'] == q['receiver_native_sha256'],
                'Receiving geometry changed')
        require(r['prototype_physical_occurrences'] == 7 and
                r['prototype_definition_count'] == 3 and not r['geometry_integrated'],
                'Wrong prototype scope')
        for file, key, count in [('independent_checks.json', 'checks', 36),
                                 ('context_checks.json', 'pairs', 8),
                                 ('exchange_checks.json', 'checks', 10)]:
            check = read(out/file)
            require(check['passed'] and check['native_sha256'] == digest and
                    len(check[key]) == count and all(v['passed'] for v in check[key]),
                    'Wrong check result: '+str(out/file))
        route = read(C/('low_spring_routes'+suffix)/'route_checks.json')
        require(route['passed'] and route['trial_native_sha256'] == digest and
                len(route['pairs']) == 27 and all(v['passed'] for v in route['pairs']),
                'Wrong corridor result')
    require(read(C/'low_spring04/reproduction_checks.json')['passed'],
            'Fresh reproduction did not pass')
    for file in ['low_spring01/context_checks.json', 'low_spring02/context_checks.json',
                 'low_spring_routes03/route_checks.json']:
        require(not read(C/file)['passed'], 'A retained failure was lost: '+file)
    for file in ['low_spring04/render_receipt.json',
                 'low_spring_routes04/render_receipt.json']:
        r = read(C/file)
        require(not r['source_camera_refitted'] and
                r['source_registration_sha256'] == q['source_registration_sha256'],
                'Camera identity changed')
    subprocess.run([sys.executable, str(H/'verify_rear_high_spring_study.py')], check=True)
    print('Rear low-speed spring study current:', len(q['dependencies']),
          'dependencies; saved nominal/stock/corridor checks reused;',
          'full rods, springs, integration and complete tank remain open.')


if __name__ == '__main__':
    verify()
