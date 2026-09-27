"""Verify the source-sized static support chain and retained historical limits."""
import argparse
import hashlib
import json
from pathlib import Path

H=Path(__file__).resolve().parent
ROOT=H.parents[3]
STUDY=H/'driver_seat_support_study'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--freeze',action='store_true')
    a=p.parse_args()
    cases={}
    for name,offset,pairs in [('trial01',0.,269),('variation01',5.,267)]:
        folder=STUDY/name
        r=read(folder/'report.json')
        m=read(folder/'isolated/manifest.json')
        checks=read(folder/'checks03/independent_checks.json')
        context=read(folder/'context_audit/report.json')
        exchange=read(folder/'exchange01/exchange_checks.json')
        digest=sha(folder/r['native_file'])
        assert all(v['native_sha256']==digest for v in [r,m,checks,context,exchange])
        assert r['details']['lower_z_offset_mm']==offset
        assert len(m['occurrences'])==281 and len(m['definitions'])==97
        assert len(r['new_occurrences'])==54 and len(r['new_definitions'])==9
        assert len(r['changed_definitions'])==3 and len(r['details']['relocated_existing_hardware'])==24
        assert len(r['details']['stays'])==4 and len(r['details']['joints'])==24
        assert not r['geometry_integrated'] and not r['historical_geometry_qualified']
        assert not r['details']['source_camera_refitted']
        assert checks['passed'] and len(checks['checks'])==607 and all(v['passed'] for v in checks['checks'])
        assert context['passed'] and not context['findings'] and context['no_mating_pair_exemptions']
        assert len(context['targets'])==84 and len(context['pairs'])==pairs
        assert exchange['passed'] and len(exchange['checks'])==96 and all(v['passed'] for v in exchange['checks'])
        for file,d in exchange['step_hashes'].items():
            assert sha(folder/'exchange01'/file)==d
        for file,d in r['input_hashes'].items():
            assert sha(ROOT/file)==d,file
        for v in m['definitions'].values():
            assert sha(Path(v['brep_path']))==v['brep_sha256']
        for receipt,worker in [(checks,'check_driver_seat_supports.py'),
                              (context,'check_driver_seat_context.py'),
                              (exchange,'exchange_driver_seat_v2.py')]:
            assert receipt['checker_sha256']==sha(H/worker)
        cases[name]=dict(native_sha256=digest,lower_z_offset_mm=offset,construction_checks=607,
            context_pairs=pairs,step_comparisons=96)
    rep=read(STUDY/'trial01/reproduction_checks.json')
    assert rep['passed'] and all(rep['checks'].values())
    assert rep['native_sha256']==cases['trial01']['native_sha256']
    assert rep['reproduction_native_sha256']==sha(STUDY/'reproduction01/ControlRebuildTrial.FCStd')
    assert rep['checker_sha256']==sha(H/'check_control_rebuild_reproduction.py')
    assert rep['archive_brep_count']==291 and rep['persistent_property_count']==15059
    visual=read(STUDY/'trial01/visual01/visual_review.json')
    rendering=read(STUDY/'trial01/visual01/render_receipt.json')
    assert visual['native_sha256']==rendering['native_sha256']==cases['trial01']['native_sha256']
    assert visual['disposition']=='connected_static_support_hypothesis_historical_position_unresolved'
    assert not visual['geometry_promoted'] and not rendering['source_camera_refitted'] and rendering['depth_buffer']
    assert len(visual['inspected_images'])==3
    for file,d in rendering['images'].items():
        assert sha(STUDY/'trial01/visual01'/file)==d==visual['inspected_images'][file]
    snap=read(STUDY/'snapshot_provenance.json')
    assert sha(ROOT/snap['path'])==snap['sha256']==rendering['images']['isometric.png']
    assert snap['accepted_progression_count']==308
    standard_path=H/'transmission_brake_front_study/trial01/standard_context_manifest.json'
    standard=read(standard_path)
    assert context['standard_manifest_sha256']==sha(standard_path)
    for file,d in standard['native_files'].items():
        assert sha(ROOT/file)==d
    receipt_path=STUDY/'study_receipt.json'
    if a.freeze:
        assert not receipt_path.exists()
        dependencies={}

        def add(path,expected=None):
            path=Path(path)
            path=path if path.is_absolute() else ROOT/path
            digest=sha(path)
            assert expected is None or digest==expected,str(path)
            dependencies[str(path.relative_to(ROOT))]=digest

        for path in sorted(STUDY.rglob('*')):
            if path.is_file() and not any(v.endswith('_runtime') or v in ['runtime','__pycache__'] for v in path.parts):
                add(path)
        for file,d in read(STUDY/'evidence_receipt.json')['dependencies'].items():
            add(file,d)
        for name in ['trial01','variation01','reproduction01']:
            r=read(STUDY/name/'report.json')
            for file,d in r['input_hashes'].items():
                add(file,d)
            add(r['parent_native'],r['parent_native_sha256'])
        for file in ['build_driver_seat_supports.py','driver_seat_support_parts.py','check_driver_seat_supports.py',
                     'render_driver_seat_supports.py','verify_driver_seat_support_study.py','pump_integration_worker.py',
                     'control_rebuild_io.py','control_rebuild_io_v2.py','check_driver_seat_context.py',
                     'exchange_driver_seat_v2.py','check_control_rebuild_reproduction.py',
                     'control_rebuild_surface_mass_v3.py','control_rebuild_surface_mass_v3.cpp',
                     'control_rebuild_surface_mass_v6.py','control_rebuild_surface_mass_v6.cpp']:
            add(H/file)
        for file in ['evidence.py','cad_build.py','camera_review.py','visual_review.py','raster.py','raster.c',
                     'mass_properties.py','occt_mass_properties.cpp','kronrod_mass.py','occt_kronrod_mass.cpp','step_matching.py']:
            add(H.parents[1]/'lib'/file)
        add(H/'driver_seat_study/diagnostics/mass_controls02/qualification.json')
        add(standard_path)
        for file,d in standard['native_files'].items():
            add(file,d)
        add(read(STUDY/'trial01/report.json')['details']['retained_development_native'])
        add(ROOT/'references/1928-03-30_SNL_G13/SNL_G13_Project/sources/p035.jpg')
        add(ROOT/'references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p277_foldout-geometry.png')
        add(snap['path'],snap['sha256'])
        receipt_path.write_text(json.dumps(dict(diagnostic_complete=True,mechanical_connection_verified=True,
            geometry_promoted=False,historical_installation_qualified=False,source_camera_refitted=False,
            cases=cases,reproduction_passed=True,
            scope='Four source-sized upper and lower stay joints, eight plate-angle joints and eight angle-floor joints. Complete local static support chain; source identities, part boundaries, adjusting details and absolute driver layout remain conditional.',
            dependencies=dependencies),indent=2)+'\n')
    value=read(receipt_path)
    assert value['diagnostic_complete'] and value['mechanical_connection_verified'] and not value['geometry_promoted']
    assert value['cases']==cases
    assert all(sha(ROOT/file)==d for file,d in value['dependencies'].items())
    print('PASS: connected seat nominal/+5mm variation;607 interface/material checks each;269/267 context pairs;96 STEP comparisons each; fresh291-BRep reproduction;',len(value['dependencies']),'bound dependencies. Historical installation unresolved; no integration.')


if __name__=='__main__':
    main()
