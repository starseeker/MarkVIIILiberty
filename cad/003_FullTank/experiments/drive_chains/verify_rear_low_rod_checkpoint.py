"""Recover the installed rear low-speed straight-rod checkpoint from saved, hashed evidence."""
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
    C = H / 'transmission_controls_study'
    out = C / 'low_rods_integrated01'
    q = read(out / 'qualification.json')
    failed = [p for p, digest in q['dependencies'].items()
              if not (ROOT / p).is_file() or sha(ROOT / p) != digest]
    require(not failed, 'Changed or missing low-rod evidence:\n' + '\n'.join(failed))
    require(q['local_static_checks_passed'] and not any(q[k] for k in [
        'channel_complete', 'packet_complete', 'historical_geometry_qualified',
        'installation_qualified', 'complete_rods_or_springs_qualified',
        'source_camera_refitted', 'standard_assembly_modified']), 'Qualification scope changed')
    r = read(out / 'report.json')
    digest = sha(out / r['native_file'])
    require(digest == r['native_sha256'] == q['native_sha256'], 'Integrated native changed')
    m = read(out / 'isolated/manifest.json')
    require((len(m['occurrences']), len(m['definitions']), len(m['assemblies'])) ==
            (3282, 570, 365), 'Wrong integrated counts')
    require(set(r['changed_definitions']) == {
        'Def_RearControlFulcrum_lever_low_right', 'Def_RearControlFulcrum_lever_low_left'
    } and len(r['expected_new_occurrences']) == 2, 'Unexpected receiver changes or additions')
    for file, expected in q['checks'].items():
        check = read(out / file)
        require(sha(out / file) == expected and check['passed'] and
                check['native_sha256'] == digest, 'Invalid integrated check: ' + file)
    preservation = read(out / 'definition_preservation_checks.json')
    require(preservation['definition_count'] == 567 and
            all(v['passed'] for v in preservation['checks']), 'Inherited material not preserved')
    for candidate in ['low_rods01', 'low_rods_variation01']:
        folder = C / candidate
        report = read(folder / 'report.json')
        native_hash = sha(folder / report['native_file'])
        require(native_hash == report['native_sha256'], 'Prototype changed')
        require(report['prototype_physical_occurrences'] == 22 and
                report['prototype_definition_count'] == 8, 'Wrong prototype count')
        for file, key, count in [('independent_checks.json', 'checks', 81),
                                 ('context_checks.json', 'pairs', 127),
                                 ('exchange_checks.json', 'checks', 30)]:
            check = read(folder / file)
            require(check['passed'] and check['native_sha256'] == native_hash and
                    len(check[key]) == count and all(v['passed'] for v in check[key]),
                    'Invalid prototype check: ' + candidate + '/' + file)
    require(read(C / 'low_rods01/reproduction_checks.json')['passed'],
            'Prototype reproduction did not pass')
    for folder in [C / 'low_rods01', out]:
        render = read(folder / 'render_receipt.json')
        require(not render['source_camera_refitted'] and
                render['source_registration_sha256'] == q['source_registration_sha256'],
                'Camera identity changed')
    eyes = read(out / 'operating_interfaces.json')
    require(eyes['native_sha256'] == digest and len(eyes['interfaces']) == 6,
            'Revised operating-eye coordinates not bound to integrated native')
    progression = read(out / 'progression_receipt.json')
    require(progression['total_count'] == 254 and len(progression['new']) == 4 and
            all(sha(ROOT / p) == h for p, h in (progression['prior'] | progression['new']).items()),
            'Progression images changed')
    subprocess.run([sys.executable, str(H / 'verify_rear_low_joint_checkpoint.py')], check=True)
    print('Rear low-speed straight-rod checkpoint current:', len(q['dependencies']),
          'dependencies; 3282 occurrences / 570 definitions / 365 groups;',
          'two shared straight rods installed; M567 washers, M564 springs and long rods remain open.')


if __name__ == '__main__':
    verify()
