"""Verify the coupled station checkpoint without claiming historical acceptance."""
import argparse
import hashlib
import json
from pathlib import Path

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
STUDY = H / 'coupled_driver_station_study'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--freeze', action='store_true')
    a = p.parse_args()
    cases = {}
    for name, offset, pairs in [('trial02', 0., 1168), ('variation01', 5., 1166)]:
        folder = STUDY / name
        r, m = read(folder/'report.json'), read(folder/'isolated/manifest.json')
        digest = sha(folder/r['native_file'])
        assert digest == r['native_sha256'] == m['native_sha256']
        assert len(m['occurrences']) == 394 and len(m['definitions']) == 125
        assert len(r['changed_definitions']) == 19 and r['details']['main_x_offset_mm'] == offset
        assert not r['geometry_integrated'] and not r['historical_geometry_qualified']
        assert not r['details']['source_camera_refitted']
        for path, count, worker in [
                ('checks01/independent_checks.json',1075,'check_coupled_driver_station.py'),
                ('mount_material03/report.json',31,'check_coupled_mount_material_v3.py'),
                ('exchange01/exchange_checks.json',329,'exchange_coupled_driver_station.py')]:
            q = read(folder/path)
            assert q['passed'] and q['native_sha256'] == digest
            assert len(q['checks']) == count and all(v['passed'] for v in q['checks'])
            assert q['checker_sha256'] == sha(H/worker)
        for file, d in q['step_hashes'].items():
            assert sha(folder/'exchange01'/file) == d
        q = read(folder/'context_audit/report.json')
        assert q['passed'] and not q['findings'] and q['no_mating_pair_exemptions']
        assert q['native_sha256'] == digest and q['checker_sha256'] == sha(H/'check_driver_seat_context.py')
        assert len(q['pairs']) == pairs and len(q['targets']) == 290
        assert q['context_occurrences'] == 8987
        for file,d in r['input_hashes'].items():
            assert sha(ROOT/file) == d, file
        for value in m['definitions'].values():
            assert sha(value['brep_path']) == value['brep_sha256']
        cases[name] = dict(native_sha256=digest, main_x_offset_mm=offset,
                           interface_checks=1075, supplementary_checks=31,
                           context_pairs=pairs, step_comparisons=329)
    failed = read(STUDY/'trial01/context_audit/report.json')
    assert not failed['passed'] and len(failed['findings']) == 3
    assert failed['native_sha256'] == sha(STUDY/'trial01/ControlRebuildTrial.FCStd')
    rep = read(STUDY/'trial02/reproduction_checks.json')
    assert rep['passed'] and all(rep['checks'].values())
    assert rep['native_sha256'] == cases['trial02']['native_sha256']
    assert rep['reproduction_native_sha256'] == sha(STUDY/'reproduction01/ControlRebuildTrial.FCStd')
    assert rep['archive_brep_count'] == 391 and rep['persistent_property_count'] == 20529
    assert rep['checker_sha256'] == sha(H/'check_control_rebuild_reproduction.py')
    for folder,worker in [('visual01','render_coupled_driver_station.py'),
                          ('routes_visual01','render_coupled_control_routes.py')]:
        base = STUDY/'trial02'/folder
        render, review = read(base/'render_receipt.json'), read(base/'visual_review.json')
        assert render['native_sha256'] == cases['trial02']['native_sha256'] == review['native_sha256']
        assert render['renderer_sha256'] == sha(H/worker)
        assert review['inspected_images'] == render['images'] and not review['geometry_promoted']
        for file,d in render['images'].items():
            assert sha(base/file) == d
    snap = read(STUDY/'snapshot_provenance.json')
    assert snap['accepted_progression_count'] == 308 and snap['diagnostic']
    assert sha(ROOT/snap['path']) == snap['sha256'] == sha(ROOT/snap['source_image'])
    receipt = STUDY/'study_receipt.json'
    if a.freeze:
        assert not receipt.exists()
        dependencies = {}

        def add(path, expected=None):
            path = Path(path)
            path = path if path.is_absolute() else ROOT/path
            d = sha(path)
            assert expected is None or d == expected, str(path)
            dependencies[str(path.relative_to(ROOT))] = d

        for path in sorted(STUDY.rglob('*')):
            if path.is_file() and not any(v.endswith('_runtime') or v in ['runtime','__pycache__'] for v in path.parts):
                add(path)
        for name in ['trial01','trial02','variation01','reproduction01']:
            r = read(STUDY/name/'report.json')
            for file,d in r['input_hashes'].items():
                add(file,d)
            add(r['parent_native'],r['parent_native_sha256'])
        for file in ['build_coupled_driver_station.py','build_coupled_driver_station_v2.py',
                     'driver_clutch_delayed_set_parts.py','check_coupled_driver_station.py',
                     'check_coupled_mount_material.py','check_coupled_mount_material_v2.py',
                     'check_coupled_mount_material_v3.py','exchange_coupled_driver_station.py',
                     'probe_coupled_clutch_set.py','render_coupled_driver_station.py',
                     'render_coupled_control_routes.py','verify_coupled_driver_station_study.py',
                     'pump_integration_worker.py','control_rebuild_io.py','control_rebuild_io_v2.py',
                     'check_driver_seat_context.py','check_control_rebuild_reproduction.py',
                     'control_rebuild_surface_mass_v3.py','control_rebuild_surface_mass_v3.cpp',
                     'control_rebuild_surface_mass_v6.py','control_rebuild_surface_mass_v6.cpp']:
            add(H/file)
        for file in ['evidence.py','cad_build.py','camera_review.py','visual_review.py','raster.py','raster.c',
                     'mass_properties.py','occt_mass_properties.cpp','kronrod_mass.py','occt_kronrod_mass.cpp','step_matching.py']:
            add(H.parents[1]/'lib'/file)
        for file in ['driver_seat_support_study/study_receipt.json','driver_seat_study/study_receipt.json',
                     'driver_seat_study/diagnostics/mass_controls02/qualification.json',
                     'transmission_controls_study/driver_redo01/mount_registration01.json',
                     'transmission_controls_study/driver_redo01/operating_integrated01/render_receipt.json']:
            add(H/file)
        standard_path = H/'transmission_brake_front_study/trial01/standard_context_manifest.json'
        add(standard_path)
        for file,d in read(standard_path)['native_files'].items():
            add(file,d)
        add(r['details']['retained_development_native'], r['details']['retained_development_native_sha256'])
        cal = read(H.parents[1]/'data/calibrations.json')['snl_2']
        reg = read(H/'transmission_controls_study/driver_redo01/mount_registration01.json')
        older = read(H/'transmission_controls_study/driver_redo01/operating_integrated01/render_receipt.json')
        for file in [cal['image'], reg['source_image'], older['side_source'], snap['path']]:
            add(file)
        receipt.write_text(json.dumps(dict(cases=cases, mechanical_checks_passed=True,
            geometry_promoted=False, historical_installation_qualified=False,
            source_camera_refitted=False, dependencies=dependencies),indent=2)+'\n')
    frozen = read(receipt)
    assert frozen['cases'] == cases and frozen['mechanical_checks_passed']
    assert not frozen['geometry_promoted'] and not frozen['historical_installation_qualified']
    for file,d in frozen['dependencies'].items():
        assert sha(ROOT/file) == d, file
    print('PASS: coupled nominal/+5mm;1075+31 checks each;1168/1166 context pairs;329 STEP each;391-BRep fresh reproduction;',len(frozen['dependencies']),'dependencies. Source limits retained; no integration.')


if __name__ == '__main__':
    main()
