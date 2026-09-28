"""Verify the frozen mounted-quadrant study without promoting the mechanism."""
import argparse
import hashlib
import json
from pathlib import Path

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
N = H / 'driver_foot_reverse_study'
RECEIPT = N / 'reverse_quadrant_study_receipt.json'


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def freeze():
    assert not RECEIPT.exists(), 'Do not overwrite a frozen receipt'
    deps = dict(read(N / 'reverse_short_study_receipt.json')['dependencies'])

    def bind(path, expected=None):
        path = Path(path).resolve()
        rel = str(path.relative_to(ROOT))
        digest = sha(path)
        assert expected is None or digest == expected, rel
        assert rel not in deps or deps[rel] == digest, rel
        deps[rel] = digest

    bind(Path(__file__))
    bind(N / 'reverse_short_study_receipt.json')
    for name in [
        'prepare_driver_reverse_fittings.py', 'driver_reverse_quadrant_parts.py',
        'build_driver_reverse_quadrant.py', 'check_driver_reverse_quadrant.py',
        'probe_driver_reverse_quadrant_lane.py', 'render_driver_reverse_quadrant.py',
        'render_driver_reverse_quadrant_v2.py', 'render_driver_reverse_bolt_section.py',
        'exchange_driver_reverse_quadrant.py', 'check_driver_seat_context.py',
        'pump_integration_worker.py', 'check_control_rebuild_reproduction.py',
    ]:
        bind(H / name)

    for case, offset in [('reverse_quadrant03', 0), ('reverse_quadrant_variation03', 1)]:
        folder = N / case
        report = read(folder / 'report.json')
        manifest = read(folder / 'isolated/manifest.json')
        native = folder / report['native_file']
        digest = sha(native)
        assert digest == report['native_sha256'] == manifest['native_sha256']
        assert manifest['extractor_sha256'] == sha(H / 'pump_integration_worker.py')
        assert len(report['new_occurrences']) == 19
        assert len(report['new_definitions']) == 6
        assert len(manifest['occurrences']) == report['prototype_physical_occurrences'] == 23
        assert len(manifest['definitions']) == report['prototype_definition_count'] == 15
        assert report['changed_definitions'] == ['Def_DriverStarboardSupportPlate_MountStudy']
        assert not report['geometry_integrated'] and not report['historical_geometry_qualified']
        assert not report['details']['mechanism_complete']
        assert report['details']['stock_offset_mm'] == offset
        assert not report['details']['source_camera_refitted']
        for rel, count, worker in [
            ('checks01/independent_checks.json', 92, 'check_driver_reverse_quadrant.py'),
            ('exchange01/exchange_checks.json', 27, 'exchange_driver_reverse_quadrant.py'),
        ]:
            result = read(folder / rel)
            assert result['passed'] and result['native_sha256'] == digest
            assert result['checker_sha256'] == sha(H / worker)
            assert len(result['checks']) == count and all(row['passed'] for row in result['checks'])
        result = read(folder / 'context_audit/report.json')
        assert result['passed'] and not result['findings']
        assert len(result['pairs']) == 116 and result['context_occurrences'] == 9006
        assert result['native_sha256'] == digest and result['no_mating_pair_exemptions']
        assert result['checker_sha256'] == sha(H / 'check_driver_seat_context.py')
        exchange = read(folder / 'exchange01/exchange_checks.json')
        assert exchange['base_worker_sha256'] == sha(H / 'exchange_driver_central_pedal_v3.py')
        for filename, expected in exchange['step_hashes'].items():
            bind(folder / 'exchange01' / filename, expected)
        for row in exchange['checks']:
            assert row['native_mass']['converged'] and row['step_mass']['converged']
            assert row['centroid_error_mm'] < 1e-5
            assert abs(row['missing_mm3']) < 1e-5 and abs(row['added_mm3']) < 1e-5
            assert not row['fuzzy_missing_faces'] and not row['fuzzy_added_faces']
            assert row['native_tolerance_mm'] <= 1e-4
            assert row['step_tolerance_mm'] <= max(row['native_tolerance_mm'], 1e-7) + 1e-10
        provenance = exchange['mass_provenance']['default']
        bind(H.parents[1] / 'lib/mass_properties.py', provenance['adapter_sha256'])
        bind(H.parents[1] / 'lib/occt_mass_properties.cpp', provenance['source_sha256'])

    nominal = N / 'reverse_quadrant03'
    repro = read(nominal / 'reproduction_checks.json')
    assert repro['passed'] and all(repro['checks'].values())
    assert repro['archive_brep_count'] == 45 and repro['persistent_property_count'] == 2074
    assert not repro['allowed_property_differences']
    assert repro['checker_sha256'] == sha(H / 'check_control_rebuild_reproduction.py')
    assert repro['native_sha256'] == sha(nominal / 'ControlRebuildTrial.FCStd')
    bind(N / 'reverse_quadrant_reproduction03/ControlRebuildTrial.FCStd', repro['reproduction_native_sha256'])

    visual = read(nominal / 'visual01/visual_review.json')
    assert visual['native_sha256'] == repro['native_sha256']
    assert not visual['integration_ready'] and not visual['geometry_integrated']
    assert not visual['source_camera_refitted'] and len(visual['reviewed_images']) == 7
    for rel, digest in visual['reviewed_images'].items():
        bind(nominal / rel, digest)
    for directory, key, worker in [
        ('visual01', 'render_receipt_sha256', 'render_driver_reverse_quadrant_v2.py'),
        ('section02', 'section_receipt_sha256', 'render_driver_reverse_bolt_section.py'),
    ]:
        path = nominal / directory / 'render_receipt.json'
        bind(path, visual[key])
        render = read(path)
        assert render['native_sha256'] == repro['native_sha256']
        assert render['renderer_sha256'] == sha(H / worker)
        assert render['manifest_sha256'] == sha(nominal / 'isolated/manifest.json')
        for filename, digest in render['images'].items():
            bind(nominal / directory / filename, digest)
    assert not read(nominal / 'visual01/render_receipt.json')['source_camera_refitted']

    failed = read(N / 'reverse_quadrant01/checks01/independent_checks.json')
    assert not failed['passed'] and sum(not row['passed'] for row in failed['checks']) == 2
    for case, pair, minimum in [
        ('reverse_quadrant01', {'DriverReverseQuadrant', 'DriverSeatStarboardRearStayLowerBolt'}, 586),
        ('reverse_quadrant02', {'DriverReverseOperatingLever', 'DriverReverseQuadrant'}, 51),
        ('reverse_quadrant_variation02', {'DriverReverseOperatingLever', 'DriverReverseQuadrant'}, 51),
    ]:
        result = read(N / case / 'context_audit/report.json')
        assert not result['passed'] and len(result['findings']) == 1
        finding = result['findings'][0]
        assert {finding['first'], finding['second']} == pair
        assert finding['common_mm3'] > minimum
        assert result['no_mating_pair_exemptions']
    probe = read(N / 'reverse_quadrant_lane_probe01/report.json')
    assert probe['worker_sha256'] == sha(H / 'probe_driver_reverse_quadrant_lane.py')
    assert probe['geometry_worker_sha256'] == sha(H / 'driver_reverse_quadrant_parts.py')

    sources = read(N / 'reverse_fittings_sources01/report.json')
    assert len(sources['selected_rows']) == 28 and len(sources['images']) == 20
    for row in sources['images']:
        bind(N / 'reverse_fittings_sources01' / row['file'], row['sha256'])
    latch = read(N / 'reverse_latch_source_review01.json')
    assert not latch['geometry_created'] and not latch['source_camera_refitted']
    bind(ROOT / latch['crop']['source'], latch['crop']['source_sha256'])
    bind(ROOT / latch['crop']['image'], latch['crop']['image_sha256'])
    progression = read(N / 'reverse_quadrant_progression_receipt.json')
    assert progression['accepted_progression_count'] == 314 and not progression['geometry_integrated']
    assert progression['native_sha256'] == repro['native_sha256']
    assert progression['visual_review_sha256'] == sha(nominal / 'visual01/visual_review.json')
    assert len(progression['images']) == 3
    for rel, digest in progression['images'].items():
        bind(ROOT / rel, digest)

    for path in sorted(N.rglob('*')):
        if not path.is_file():
            continue
        parts = path.relative_to(N).parts
        if not (parts[0].startswith('reverse_quadrant') or parts[0] in [
            'reverse_fittings_sources01', 'reverse_latch_source_review01.json',
        ]):
            continue
        if any('runtime' in part or part == '__pycache__' for part in parts):
            continue
        if path.suffix in ['.FCBak', '.FCStd1', '.pyc']:
            continue
        bind(path)
        if path.suffix == '.json':
            data = read(path)
            if isinstance(data, dict):
                for key in ['input_hashes', 'source_hashes']:
                    for rel, digest in data.get(key, {}).items():
                        bind(ROOT / rel, digest)
    bind(N / 'REVERSE_QUADRANT_STUDY.md')
    for rel, digest in deps.items():
        assert sha(ROOT / rel) == digest, rel
    RECEIPT.write_text(json.dumps(dict(
        mounted_quadrant_geometry_checks_passed=True,
        mechanism_complete=False, historical_geometry_qualified=False,
        geometry_integrated=False, integration_ready=False,
        authoritative_parent='cad/003_FullTank/experiments/drive_chains/coupled_driver_integration/integrated01',
        nominal_native_sha256=repro['native_sha256'], dependencies=deps,
        scope='Nine quadrant/mount additions and two real support bores; full prior reverse connection retained. '
              '92 checks,116 context pairs and27 strict STEP comparisons per nominal/+1mm case. '
              'Exact45-BRep/2074-property fresh build. Latch, long route and historical mounting remain open.',
    ), indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze', action='store_true')
    args = parser.parse_args()
    if args.freeze:
        freeze()
    receipt = read(RECEIPT)
    assert receipt['mounted_quadrant_geometry_checks_passed']
    assert not any(receipt[key] for key in ['integration_ready', 'geometry_integrated', 'mechanism_complete'])
    for rel, digest in receipt['dependencies'].items():
        assert sha(ROOT / rel) == digest, rel
    print('PASS', len(receipt['dependencies']),
          'bound dependencies; mounted quadrant study. Full reverse mechanism remains unfinished.')
