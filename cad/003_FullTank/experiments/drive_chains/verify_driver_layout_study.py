"""Freeze/verify the mechanically feasible, historically unresolved layout study."""
import argparse
import hashlib
import json
from pathlib import Path

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
STUDY = H / 'driver_layout_study'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze', action='store_true')
    args = parser.parse_args()
    cases = {}
    for name, height in [('trial01', 975.), ('variation01', 970.)]:
        folder = STUDY / name
        report = read(folder / 'report.json')
        checks = read(folder / 'checks03/independent_checks.json')
        context = read(folder / 'context_audit/report.json')
        exchange = read(folder / 'exchange01/exchange_checks.json')
        manifest = read(folder / 'isolated/manifest.json')
        native_sha = sha(folder / report['native_file'])
        assert all(v['native_sha256'] == native_sha for v in [report, checks, context, exchange, manifest])
        assert not report['geometry_integrated'] and not report['historical_geometry_qualified']
        assert report['details']['main_world_mm'][2] == height
        assert report['prototype_physical_occurrences'] == 189 and report['prototype_definition_count'] == 81
        assert checks['passed'] and len(checks['checks']) == 521 and all(v['passed'] for v in checks['checks'])
        assert context['passed'] and not context['findings'] and context['no_mating_pair_exemptions']
        assert len(context['pairs']) == 1022 and len(context['targets']) == 183
        assert exchange['passed'] and len(exchange['checks']) == 226 and all(v['passed'] for v in exchange['checks'])
        for file, digest in exchange['step_hashes'].items():
            assert sha(folder / 'exchange01' / file) == digest
        for file, digest in report['input_hashes'].items():
            assert sha(ROOT / file) == digest, file
        for key, worker in [(checks, 'check_driver_bow_layout.py'),
                            (context, 'check_control_rebuild_context.py'),
                            (exchange, 'exchange_control_rebuild_clutch_swing.py')]:
            assert sha(H / worker) == key['checker_sha256']
        for definition in manifest['definitions'].values():
            assert sha(Path(definition['brep_path'])) == definition['brep_sha256']
        cases[name] = dict(native_sha256=native_sha, height_mm=height,
                           construction_checks=521, context_pairs=1022, step_comparisons=226,
                           handle_bow_clearance_mm=checks['handle_bow_clearance_mm'])
    reproduction = read(STUDY / 'trial01/reproduction_checks.json')
    assert reproduction['passed'] and all(reproduction['checks'].values())
    assert reproduction['native_sha256'] == cases['trial01']['native_sha256']
    assert reproduction['reproduction_native_sha256'] == sha(STUDY / 'reproduction01/ControlRebuildTrial.FCStd')
    assert reproduction['checker_sha256'] == sha(H / 'check_control_rebuild_reproduction.py')
    visual = read(STUDY / 'trial01/visual02/visual_review.json')
    rendering = read(STUDY / 'trial01/visual02/render_receipt.json')
    assert visual['native_sha256'] == rendering['native_sha256'] == cases['trial01']['native_sha256']
    assert visual['disposition'] == 'mechanically_feasible_historical_position_unresolved'
    assert not rendering['source_camera_refitted'] and not visual['geometry_promoted']
    assert len(visual['inspected_images']) == 3
    for file, digest in rendering['images'].items():
        assert sha(STUDY / 'trial01/visual02' / file) == digest == visual['inspected_images'][file]
    receipt = STUDY / 'study_receipt.json'
    if args.freeze:
        assert not receipt.exists()
        dependencies = {}

        def add(path, expected=None):
            path = Path(path)
            path = path if path.is_absolute() else ROOT / path
            value = sha(path)
            assert expected is None or expected == value, str(path)
            dependencies[str(path.relative_to(ROOT))] = value

        for path in sorted(STUDY.rglob('*')):
            if path.is_file() and not any(v.endswith('_runtime') or v == '__pycache__' for v in path.parts):
                add(path)
        for name in ['trial01', 'variation01', 'reproduction01']:
            report = read(STUDY / name / 'report.json')
            for path, digest in report['input_hashes'].items():
                add(path, digest)
            add(report['parent_native'], report['parent_native_sha256'])
        for path, digest in read(STUDY / 'source_review.json')['input_hashes'].items():
            add(path, digest)
        workers = ['driver_layout_trial_parts.py', 'driver_folded_floor_support.py',
                   'build_driver_bow_layout.py', 'probe_driver_bow_layout.py',
                   'check_driver_bow_layout.py', 'render_driver_bow_layout.py',
                   'render_driver_bow_layout_v2.py', 'verify_driver_layout_study.py',
                   'control_rebuild_io_v2.py', 'pump_integration_worker.py',
                   'check_control_rebuild_context.py', 'check_control_rebuild_reproduction.py',
                   'exchange_control_rebuild_clutch_swing.py',
                   'control_rebuild_surface_mass_v3.py', 'control_rebuild_surface_mass_v3.cpp',
                   'control_rebuild_surface_mass_v5.py', 'control_rebuild_surface_mass_v5.cpp']
        for name in workers:
            add(H / name)
        for name in ['mass_properties.py', 'occt_mass_properties.cpp', 'kronrod_mass.py',
                     'occt_kronrod_mass.cpp', 'camera_review.py', 'step_matching.py', 'evidence.py', 'cad_build.py']:
            add(H.parents[1] / 'lib' / name)
        add(H / 'transmission_controls_study/redo01/diagnostics/trimmed_mass01/qualification.json')
        value = dict(diagnostic_complete=True, geometry_promoted=False,
                     historical_geometry_qualified=False, source_camera_refitted=False,
                     cases=cases, reproduction_passed=True,
                     scope='Coupled full-stock layout and actual floor mounting prototype; absolute shaft/seat position and source control state remain unresolved.',
                     dependencies=dependencies)
        receipt.write_text(json.dumps(value, indent=2) + '\n')
    value = read(receipt)
    assert value['diagnostic_complete'] and not value['geometry_promoted'] and value['cases'] == cases
    assert all(sha(ROOT / path) == digest for path, digest in value['dependencies'].items())
    print('PASS: two complete layout hypotheses; each 521 material/contact checks, 1022 context pairs, 226 STEP comparisons; fresh reproduction;', len(value['dependencies']), 'bound dependencies. Historical position unresolved; no integration.')


if __name__ == '__main__':
    main()
