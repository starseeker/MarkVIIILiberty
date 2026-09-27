"""Freeze/verify the seat-side prototype; full support installation remains open."""
import argparse
import hashlib
import json
from pathlib import Path

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
STUDY = H / 'driver_seat_study'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze', action='store_true')
    args = parser.parse_args()
    cases = {}
    for name, width, exchange_dir in [('trial06', 480., 'exchange04'),
                                       ('variation01', 490., 'exchange02')]:
        folder = STUDY / name
        report = read(folder / 'report.json')
        checks = read(folder / 'checks03/independent_checks.json')
        context = read(folder / 'context_audit/report.json')
        exchange = read(folder / exchange_dir / 'exchange_checks.json')
        manifest = read(folder / 'isolated/manifest.json')
        native_sha = sha(folder / report['native_file'])
        assert all(v['native_sha256'] == native_sha for v in [report, checks, context, exchange, manifest])
        assert not report['geometry_integrated'] and not report['historical_geometry_qualified']
        assert not report['installation_qualified'] and not report['details']['support_installation_complete']
        assert report['details']['width_mm'] == width
        assert report['prototype_physical_occurrences'] == 227 and report['prototype_definition_count'] == 88
        assert len(report['new_occurrences']) == 38 and len(report['new_definitions']) == 7
        assert checks['passed'] and len(checks['checks']) == 447 and all(v['passed'] for v in checks['checks'])
        assert context['passed'] and not context['findings'] and context['no_mating_pair_exemptions']
        assert len(context['pairs']) == 96 and len(context['targets']) == 38
        assert exchange['passed'] and len(exchange['checks']) == 45 and all(v['passed'] for v in exchange['checks'])
        for file, digest in exchange['step_hashes'].items():
            assert sha(folder / exchange_dir / file) == digest
        for file, digest in report['input_hashes'].items():
            assert sha(ROOT / file) == digest, file
        for receipt, worker in [(checks, 'check_driver_seat_v2.py'),
                                (context, 'check_driver_seat_context.py'),
                                (exchange, 'exchange_driver_seat_v2.py')]:
            assert sha(H / worker) == receipt['checker_sha256']
        for definition in manifest['definitions'].values():
            assert sha(Path(definition['brep_path'])) == definition['brep_sha256']
        retained = report['details']['retained_development_native']
        assert sha(ROOT / retained) == context['retained_development_native_sha256']
        cases[name] = dict(native_sha256=native_sha, width_mm=width,
                           construction_checks=447, context_pairs=96, step_comparisons=45,
                           exchange_directory=exchange_dir)
    controls = read(STUDY / 'diagnostics/mass_controls02/qualification.json')
    assert controls['passed'] and len(controls['checks']) == 39
    assert all(v['passed'] for v in controls['checks'])
    for key, path in [('adapter_sha256', H / 'control_rebuild_surface_mass_v6.py'),
                      ('source_sha256', H / 'control_rebuild_surface_mass_v6.cpp'),
                      ('convergence_adapter_sha256', H.parents[1] / 'lib/mass_properties.py')]:
        assert sha(path) == controls['provenance'][key]
    assert controls['checker_sha256'] == sha(H / 'qualify_control_trimmed_mass_v6.py')
    reproduction = read(STUDY / 'trial06/reproduction_checks.json')
    assert reproduction['passed'] and all(reproduction['checks'].values())
    assert reproduction['native_sha256'] == cases['trial06']['native_sha256']
    assert reproduction['reproduction_native_sha256'] == sha(STUDY / 'reproduction01/ControlRebuildTrial.FCStd')
    assert reproduction['checker_sha256'] == sha(H / 'check_control_rebuild_reproduction.py')
    visual = read(STUDY / 'trial06/visual03/visual_review.json')
    rendering = read(STUDY / 'trial06/visual03/render_receipt.json')
    assert visual['native_sha256'] == rendering['native_sha256'] == cases['trial06']['native_sha256']
    assert visual['disposition'] == 'seat_side_prototype_support_and_historical_position_unresolved'
    assert not visual['geometry_promoted'] and not rendering['source_camera_refitted']
    assert rendering['depth_buffer'] and len(visual['inspected_images']) == 3
    for file, digest in rendering['images'].items():
        assert sha(STUDY / 'trial06/visual03' / file) == digest == visual['inspected_images'][file]
    surfaces = read(STUDY / 'trial06/surface_records/report.json')
    assert surfaces['native_sha256'] == cases['trial06']['native_sha256']
    assert surfaces['nonphysical'] and not surfaces['geometry_modified'] and len(surfaces['guides']) == 10
    assert sha(STUDY / 'trial06/surface_records/SeatBackSectionGuides.FCStd') == surfaces['nonphysical_guides_native_sha256']
    snapshot = read(STUDY / 'snapshot_provenance.json')
    assert sha(ROOT / snapshot['path']) == snapshot['sha256'] == rendering['images']['isometric.png']
    assert snapshot['accepted_progression_count'] == 308
    # Failures remain distinguishable from the accepted technical comparisons.
    for name in ['trial05/checks03/independent_checks.json', 'trial05/context_audit/report.json',
                 'trial06/exchange01/exchange_checks.json', 'trial06/exchange03/exchange_checks.json',
                 'variation01/exchange01/exchange_checks.json', 'diagnostics/mass01/report.json']:
        assert not read(STUDY / name)['passed']
    receipt = STUDY / 'study_receipt.json'
    if args.freeze:
        assert not receipt.exists()
        dependencies = {}

        def add(path, expected=None):
            path = Path(path)
            path = path if path.is_absolute() else ROOT / path
            digest = sha(path)
            assert expected is None or expected == digest, str(path)
            dependencies[str(path.relative_to(ROOT))] = digest

        for path in sorted(STUDY.rglob('*')):
            if path.is_file() and not any(v.endswith('_runtime') or v in ['runtime', '__pycache__'] for v in path.parts):
                add(path)
        for name in ['trial05', 'trial06', 'variation01', 'reproduction01']:
            report = read(STUDY / name / 'report.json')
            for path, digest in report['input_hashes'].items():
                add(path, digest)
            add(report['parent_native'], report['parent_native_sha256'])
        for path, digest in read(STUDY / 'evidence_receipt.json')['dependencies'].items():
            add(path, digest)
        workers = ['driver_seat_parts.py', 'driver_seat_parts_v2.py',
                   'build_driver_seat.py', 'build_driver_seat_v2.py',
                   'check_driver_seat.py', 'check_driver_seat_v2.py', 'check_driver_seat_context.py',
                   'render_driver_seat.py', 'render_driver_seat_v2.py', 'render_driver_seat_v3.py',
                   'record_driver_seat_surfaces.py', 'verify_driver_seat_study.py',
                   'probe_driver_seat_mass.py', 'probe_driver_seat_mass_v2.py',
                   'control_rebuild_io_v2.py', 'pump_integration_worker.py',
                   'check_control_rebuild_reproduction.py', 'exchange_control_rebuild_clutch_swing.py',
                   'exchange_driver_seat.py', 'exchange_driver_seat_v2.py',
                   'control_rebuild_surface_mass_v3.py', 'control_rebuild_surface_mass_v3.cpp',
                   'control_rebuild_surface_mass_v5.py', 'control_rebuild_surface_mass_v5.cpp',
                   'control_rebuild_surface_mass_v6.py', 'control_rebuild_surface_mass_v6.cpp',
                   'qualify_control_trimmed_mass_v6.py']
        for name in workers:
            add(H / name)
        for name in ['mass_properties.py', 'occt_mass_properties.cpp', 'kronrod_mass.py',
                     'occt_kronrod_mass.cpp', 'camera_review.py', 'step_matching.py', 'evidence.py',
                     'cad_build.py', 'visual_review.py', 'raster.py', 'raster.c']:
            add(H.parents[1] / 'lib' / name)
        add(H / 'transmission_controls_study/redo01/diagnostics/trimmed_mass01/qualification.json')
        add(retained)
        add(snapshot['path'], snapshot['sha256'])
        receipt.write_text(json.dumps(dict(
            diagnostic_complete=True, geometry_promoted=False, support_installation_complete=False,
            historical_geometry_qualified=False, source_camera_refitted=False,
            cases=cases, reproduction_passed=True, mass_controls=39,
            scope='M791 seat-side reconstruction and complete catalogue bearings/clips/rivets/nails. Source profile, support attachment and historical position remain unresolved.',
            dependencies=dependencies), indent=2) + '\n')
    value = read(receipt)
    assert value['diagnostic_complete'] and not value['geometry_promoted'] and value['cases'] == cases
    assert all(sha(ROOT / path) == digest for path, digest in value['dependencies'].items())
    print('PASS: seat widths 480/490; each 447 material/contact checks, 96 context pairs, 45 STEP comparisons; fresh reproduction; 39 mass controls;', len(value['dependencies']), 'bound dependencies. Full support installation and historical position remain open.')


if __name__ == '__main__':
    main()
