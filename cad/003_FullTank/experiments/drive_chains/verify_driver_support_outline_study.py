"""Verify the corrected support outline and exact inherited coupled geometry."""
import argparse
import hashlib
import json
from pathlib import Path

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
S = H/'driver_support_outline_study'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--freeze',action='store_true')
    a = p.parse_args()
    baseline_path = H/'coupled_driver_station_study/study_receipt.json'
    baseline = read(baseline_path)
    assert baseline['mechanical_checks_passed']
    for file,d in baseline['dependencies'].items():
        assert sha(ROOT/file)==d,file
    cases = {}
    for name,offset in [('trial02',0.),('variation01',5.)]:
        folder=S/name
        r,m=read(folder/'report.json'),read(folder/'isolated/manifest.json')
        native=folder/r['native_file'];digest=sha(native)
        assert digest==r['native_sha256']==m['native_sha256']
        assert len(m['occurrences'])==394 and len(m['definitions'])==125
        assert r['details']['support_front_offset_mm']==offset
        assert not r['geometry_integrated'] and not r['details']['source_camera_refitted']
        for file,d in r['input_hashes'].items():
            assert sha(ROOT/file)==d,file
        for v in m['definitions'].values():
            assert sha(v['brep_path'])==v['brep_sha256']
        for path,count,worker in [
            ('checks01/independent_checks.json',1075,'check_coupled_driver_station.py'),
            ('mount_material03/report.json',31,'check_coupled_mount_material_v3.py'),
            ('delta_checks.json',8,'check_driver_support_outline_delta.py'),
            ('exchange01/exchange_checks.json',34,'exchange_driver_support_outline.py')]:
            q=read(folder/path)
            assert q['native_sha256']==digest and q['passed']
            assert len(q['checks'])==count and all(v['passed'] for v in q['checks'])
            assert q['checker_sha256']==sha(H/worker)
        assert q['baseline_provenance']['receipt_sha256']==sha(baseline_path)
        assert len(q['baseline_provenance']['changed_definitions'])==5
        for file,d in q['step_hashes'].items():
            assert sha(folder/'exchange01'/file)==d
        q=read(folder/'context_audit/report.json')
        assert q['passed'] and not q['findings'] and q['no_mating_pair_exemptions']
        assert q['native_sha256']==digest and q['checker_sha256']==sha(H/'check_driver_seat_context.py')
        assert len(q['pairs'])==1174 and len(q['targets'])==290
        cases[name]=dict(native_sha256=digest,support_front_offset_mm=offset,
                         checks=1075,supplementary_checks=31,delta_checks=8,context_pairs=1174,step_comparisons=34)
    failure=read(S/'trial01/context_audit/report.json')
    assert not failure['passed'] and len(failure['findings'])==2
    rep=read(S/'trial02/reproduction_checks.json')
    assert rep['passed'] and all(rep['checks'].values())
    assert rep['native_sha256']==cases['trial02']['native_sha256']
    assert rep['reproduction_native_sha256']==sha(S/'reproduction01/ControlRebuildTrial.FCStd')
    assert rep['archive_brep_count']==391 and rep['persistent_property_count']==20529
    visual=read(S/'trial02/visual01/visual_review.json')
    render=read(S/'trial02/visual01/render_receipt.json')
    assert visual['native_sha256']==render['native_sha256']==cases['trial02']['native_sha256']
    assert visual['disposition']=='reviewed_local_approximation' and not visual['geometry_promoted']
    assert render['renderer_sha256']==sha(H/'render_coupled_driver_station.py')
    assert visual['inspected_images']==render['images'] and not render['source_camera_refitted']
    for file,d in render['images'].items():
        assert sha(S/'trial02/visual01'/file)==d
    snap=read(S/'snapshot_provenance.json')
    assert sha(ROOT/snap['path'])==snap['sha256']==render['images']['isometric.png']
    assert snap['accepted_progression_count']==308
    receipt=S/'study_receipt.json'
    if a.freeze:
        assert not receipt.exists()
        deps={}

        def add(path,expected=None):
            path=Path(path);path=path if path.is_absolute() else ROOT/path
            d=sha(path)
            assert expected is None or d==expected,str(path)
            deps[str(path.relative_to(ROOT))]=d

        add(baseline_path)
        for file,d in baseline['dependencies'].items():
            add(file,d)
        for path in S.rglob('*'):
            if path.is_file() and not any(v.endswith('_runtime') or v in ['runtime','__pycache__'] for v in path.parts):
                add(path)
        for name in ['trial01','trial02','variation01','reproduction01']:
            r=read(S/name/'report.json')
            for file,d in r['input_hashes'].items():
                add(file,d)
        for file in ['build_driver_support_outline.py','build_driver_support_outline_v2.py',
                     'driver_seat_floor_footprint.py','driver_seat_floor_footprint_v2.py',
                     'check_driver_support_outline_delta.py','exchange_driver_support_outline.py',
                     'verify_driver_support_outline_study.py']:
            add(H/file)
        add(snap['path'],snap['sha256'])
        receipt.write_text(json.dumps(dict(cases=cases,mechanical_checks_passed=True,
            source_disposition='reviewed_local_approximation',geometry_promoted=False,
            historical_installation_qualified=False,dependencies=deps),indent=2)+'\n')
    value=read(receipt)
    assert value['cases']==cases and value['mechanical_checks_passed'] and not value['geometry_promoted']
    for file,d in value['dependencies'].items():
        assert sha(ROOT/file)==d,file
    print('PASS: support outline nominal/+5mm;1075+31+8 checks,1174 context pairs and34 delta STEP each;391-BRep reproduction;',len(value['dependencies']),'dependencies; ready for local-approximation integration.')


if __name__=='__main__':
    main()
