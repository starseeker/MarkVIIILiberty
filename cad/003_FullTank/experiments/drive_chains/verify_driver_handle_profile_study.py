"""Freeze or verify a completed diagnostic; never promote a handle or hull."""
import argparse
import hashlib
import json
from pathlib import Path

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
F = H/'transmission_controls_study/driver_redo01'
STUDY = F/'handle_profiles01'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze', action='store_true')
    args = parser.parse_args()
    receipt = STUDY/'study_receipt.json'
    labels = ['overall_control','pivot_reach','functional_current','functional_source']
    expected_context = [True,True,False,False]
    cases = {}
    for label, expected in zip(labels,expected_context):
        folder = STUDY/label
        report = read(folder/'report.json')
        native = folder/report['native_file']
        checks = read(folder/'profile_checks02/report.json')
        context = read(folder/'context_audit/report.json')
        assert checks['passed'] and all(c['passed'] for c in checks['checks'])
        assert context['passed'] == expected and context['no_mating_pair_exemptions']
        assert sha(native)==report['native_sha256']==checks['native_sha256']==context['native_sha256']
        assert len(context['findings']) == (0 if expected else 2)
        for finding in context['findings']:
            assert finding['second']=='standard:hull_front_slope'
            assert finding['common_mm3'] > 2000
        cases[label] = dict(native_sha256=sha(native),construction_checks=len(checks['checks']),
                            context_pairs=len(context['pairs']),context_passed=expected,
                            integrated=False,step_qualified=False,
                            measurements=checks['records'])
    audit = F/'front_hull_audit01'
    ar = read(audit/'report.json')
    assert ar['rake_sign_contradiction'] and not ar['source_camera_refitted'] and not ar['geometry_modified']
    assert read(audit/'visual_review.json')['disposition']=='confirmed_source_contradiction'
    assert read(STUDY/'comparison02/visual_review.json')['disposition']=='reviewed_diagnostic_not_accepted_geometry'
    if args.freeze:
        assert not receipt.exists()
        dependencies = {}

        def add(path, expected=None):
            path = Path(path); path = path if path.is_absolute() else ROOT/path
            digest = sha(path)
            assert expected is None or digest==expected, str(path)
            dependencies[str(path.relative_to(ROOT))]=digest

        for folder in [STUDY,audit]:
            for path in sorted(folder.rglob('*')):
                if path.is_file() and not any(v.endswith('_runtime') or v=='__pycache__' for v in path.parts):
                    add(path)
        for label in labels:
            report = read(STUDY/label/'report.json')
            for path,digest in report['input_hashes'].items():add(path,digest)
            add(report['parent_native'],report['parent_native_sha256'])
        for path,digest in ar['source_hashes'].items():add(path,digest)
        for name in ['driver_handle_profile_parts.py','trial_driver_handle_profiles.py',
                     'check_driver_handle_profiles.py','render_driver_handle_profiles.py',
                     'audit_driver_front_hull.py','verify_driver_handle_profile_study.py',
                     'pump_integration_worker.py','check_control_rebuild_context.py']:
            add(H/name)
        add(F/'handle_profile_controls01.json')
        value = dict(diagnostic_complete=True,geometry_promoted=False,source_camera_refitted=False,
                     accepted_checkpoint=str((F/'operating_integrated01').relative_to(ROOT)),
                     accepted_native_sha256=ar['native_sha256'],cases=cases,
                     scope='Complete saved-solid hypothesis comparison and confirmed front-hull source contradiction. No alternative geometry or historical control pose accepted. Reopen bow/enclosure/floor geometry before revising driver station against that boundary.',
                     next_evidence=str((audit/'report.json').relative_to(ROOT)),dependencies=dependencies)
        receipt.write_text(json.dumps(value,indent=2)+'\n')
    value = read(receipt)
    assert value['diagnostic_complete'] and not value['geometry_promoted'] and value['cases']==cases
    assert all(sha(ROOT/path)==digest for path,digest in value['dependencies'].items())
    print('PASS: four complete handle hypotheses, explicit context failures, inspected hull-rake contradiction;',len(value['dependencies']),'bound dependencies. No geometry promoted.')


if __name__=='__main__':
    main()
