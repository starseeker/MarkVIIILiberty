"""Recover the common M568A reconstruction from immutable saved evidence."""
from pathlib import Path
import subprocess
import sys

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path.insert(0, str(H.parents[1]))
from lib.evidence import read, sha


def verify():
    C = H/'transmission_controls_study'
    out = C/'pin_family_integrated01'
    q = read(out/'qualification.json')
    failed = [f for f, h in q['dependencies'].items() if not (ROOT/f).is_file() or sha(ROOT/f) != h]
    assert not failed, '\n'.join(failed)
    assert q['local_static_checks_passed'] and not any(q[k] for k in [
        'historical_geometry_qualified', 'installation_qualified', 'standard_assembly_modified',
        'source_camera_refitted', 'low_speed_connections_complete', 'packet_complete'])
    r, m = read(out/'report.json'), read(out/'isolated/manifest.json')
    digest = sha(out/r['native_file'])
    assert digest == r['native_sha256'] == q['native_sha256'] == m['native_sha256']
    assert (len(m['occurrences']), len(m['definitions']), len(m['assemblies'])) == (3264, 568, 359)
    assert set(r['changed_definitions']) == {'Def_ControlJoint_pin', 'Def_ControlJoint_fork',
        'Def_HighBrakeMechanism_lever_left', 'Def_HighBrakeMechanism_lever_right'}
    assert not r['new_definitions'] and not r['placement_changed_objects']
    for file, expected in q['checks'].items():
        check = read(out/file)
        assert sha(out/file) == expected and check['passed'] and check['native_sha256'] == digest
    assert read(out/'definition_preservation_checks.json')['definition_count'] == 564
    for name in ['pin_family01', 'pin_family_variation01']:
        folder = C/name
        report = read(folder/'report.json')
        assert sha(folder/report['native_file']) == report['native_sha256']
        assert (report['prototype_physical_occurrences'], report['prototype_definition_count']) == (16, 9)
        for file, key, count in [('independent_checks.json', 'checks', 73),
                                 ('context_checks.json', 'pairs', 143), ('exchange_checks.json', 'checks', 25)]:
            check = read(folder/file)
            assert check['passed'] and check['native_sha256'] == report['native_sha256']
            assert len(check[key]) == count and all(v['passed'] for v in check[key])
        diag = read(folder/'diagnostics/low_fork_one_inch/report.json')
        assert not diag['passes_engagement'] and not diag['geometry_integrated']
    assert read(C/'pin_family01/reproduction_checks.json')['passed']
    for folder in [C/'pin_family01', out]:
        view = read(folder/'render_receipt.json')
        assert not view['source_camera_refitted'] and view['source_registration_sha256'] == q['source_registration_sha256']
    eyes = read(out/'operating_interfaces.json')
    assert eyes['native_sha256'] == digest and len(eyes['interfaces']) == 6
    progress = read(out/'progression_receipt.json')
    assert progress['total_count'] == 247 and len(progress['new']) == 2
    assert all(sha(ROOT/f) == h for f, h in (progress['prior'] | progress['new']).items())
    subprocess.run([sys.executable, str(H/'verify_rear_track_rod_checkpoint.py')], check=True)
    print('Shared control-pin checkpoint current:', len(q['dependencies']),
          'dependencies;3264 occurrences/568 definitions/359 groups;',
          'four shared definitions revised; low-speed fork datum and full tank remain open.')


if __name__ == '__main__':
    verify()
