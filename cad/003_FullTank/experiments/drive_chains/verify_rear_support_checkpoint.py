"""Read-only recovery of the installed rear support family and its source evidence."""
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
    out = C/'support_integrated01'
    q = read(out/'qualification.json')
    failed = [p for p, digest in q['dependencies'].items()
              if not (ROOT/p).is_file() or sha(ROOT/p) != digest]
    require(not failed, 'Changed or missing support evidence:\n'+'\n'.join(failed))
    require(q['local_static_checks_passed'] and not any(q[k] for k in [
        'channel_complete', 'packet_complete', 'historical_geometry_qualified',
        'installation_qualified', 'complete_rods_or_springs_qualified',
        'source_camera_refitted', 'standard_assembly_modified']), 'Qualification scope changed')
    r = read(out/'report.json')
    digest = sha(out/r['native_file'])
    require(digest == r['native_sha256'] == q['native_sha256'], 'Integrated native changed')
    m = read(out/'isolated/manifest.json')
    require((len(m['occurrences']), len(m['definitions']), len(m['assemblies'])) ==
            (3246, 564, 353), 'Wrong integrated counts')
    for file, expected in q['checks'].items():
        check = read(out/file)
        require(sha(out/file) == expected and check['passed'] and
                check['native_sha256'] == digest, 'Invalid integrated check: '+file)
    for candidate, route in [('support_family01', 'support_family_routes01'),
                              ('support_family_variation01', 'support_family_routes_variation01')]:
        folder = C/candidate
        report = read(folder/'report.json')
        native_hash = sha(folder/report['native_file'])
        require(native_hash == report['native_sha256'], 'Prototype changed')
        require(report['prototype_physical_occurrences'] == 22 and
                report['prototype_definition_count'] == 10, 'Wrong prototype count')
        for file, key, count in [('independent_checks.json', 'checks', 67),
                                 ('context_checks.json', 'pairs', 20),
                                 ('exchange_checks.json', 'checks', 32)]:
            check = read(folder/file)
            require(check['passed'] and check['native_sha256'] == native_hash and
                    len(check[key]) == count and all(v['passed'] for v in check[key]),
                    'Invalid prototype check: '+candidate+'/'+file)
        check = read(C/route/'route_checks.json')
        require(check['passed'] and check['trial_native_sha256'] == native_hash and
                len(check['pairs']) == 27 and all(v['passed'] for v in check['pairs']),
                'Invalid provisional corridor check')
    require(read(C/'support_family01/reproduction_checks.json')['passed'],
            'Prototype reproduction did not pass')
    require(not read(C/'support_family01/diagnostics/washer_contact/original_checks.json')['passed'],
            'Original checker diagnostic was lost')
    for folder in [C/'support_family01', out]:
        render = read(folder/'render_receipt.json')
        require(not render['source_camera_refitted'] and
                render['source_registration_sha256'] == q['source_registration_sha256'],
                'Camera identity changed')
    progression = read(out/'progression_receipt.json')
    require(progression['total_count'] == 238 and all(sha(ROOT/p) == h
            for p, h in (progression['prior'] | progression['new']).items()),
            'Progression images changed')
    subprocess.run([sys.executable, str(H/'verify_rear_low_spring_study.py')], check=True)
    print('Rear support checkpoint current:', len(q['dependencies']),
          'dependencies;3246 occurrences/564 definitions/353 groups;',
          'saved checks and fixed source camera reused; complete tank remains open.')


if __name__ == '__main__':
    verify()
