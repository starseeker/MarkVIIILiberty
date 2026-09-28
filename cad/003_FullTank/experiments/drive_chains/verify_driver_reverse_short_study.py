"""Verify the frozen reverse-body/short-rod study without promoting the mechanism."""
import argparse,hashlib,json
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[3];N=H/'driver_foot_reverse_study'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--freeze',action='store_true');a=p.parse_args();receipt=N/'reverse_short_study_receipt.json'
if a.freeze:
    assert not receipt.exists()
    deps=dict(read(N/'central_study_receipt.json')['dependencies'])
    def bind(p):
        p=Path(p).resolve();deps[str(p.relative_to(ROOT))]=sha(p)
    bind(N/'central_study_receipt.json');bind(Path(__file__))
    for name in ['build_driver_reverse_short.py','build_driver_reverse_short_v2.py','driver_reverse_lever_parts.py','driver_reverse_lever_parts_v2.py','check_driver_reverse_short.py','check_driver_reverse_short_v2.py','diagnose_driver_reverse_short.py','probe_driver_reverse_blade_set.py','probe_driver_reverse_blade_set_v2.py','measure_driver_reverse_source.py','render_driver_reverse_short.py','exchange_driver_reverse_short.py','check_driver_seat_context.py','pump_integration_worker.py','check_control_rebuild_reproduction.py']:
        bind(H/name)
    for case,offset in [('reverse_short03',0),('reverse_short_variation03',-1)]:
        f=N/case;r=read(f/'report.json');m=read(f/'isolated/manifest.json');native=f/r['native_file']
        assert sha(native)==r['native_sha256']==m['native_sha256']
        assert len(r['new_occurrences'])==10 and len(r['new_definitions'])==1 and len(m['occurrences'])==13
        assert not r['changed_definitions'] and not r['geometry_integrated'] and not r['details']['mechanism_complete']
        assert r['details']['stock_offset_mm']==offset and r['details']['controls']['delayed_set_mm']==30
        assert r['details']['metadata_revisions']=={'Def_DriverFrontShortRod_M789A':['ReconstructionStatus']}
        for rel,count,worker in [('checks04/independent_checks.json',75,'check_driver_reverse_short_v2.py'),('exchange01/exchange_checks.json',11,'exchange_driver_reverse_short.py')]:
            q=read(f/rel);assert q['passed'] and q['native_sha256']==sha(native) and q['checker_sha256']==sha(H/worker)
            assert len(q['checks'])==count and all(x['passed'] for x in q['checks'])
        q=read(f/'context_audit/report.json');assert q['passed'] and not q['findings'] and len(q['pairs'])==53 and q['context_occurrences']==8997
        assert q['native_sha256']==sha(native) and q['checker_sha256']==sha(H/'check_driver_seat_context.py') and q['no_mating_pair_exemptions']
        e=read(f/'exchange01/exchange_checks.json')
        for file,digest in e['step_hashes'].items():assert sha(f/'exchange01'/file)==digest
        for row in e['checks']:
            assert row['native_mass']['converged'] and row['step_mass']['converged'] and row['centroid_error_mm']<1e-5
            assert abs(row['missing_mm3'])<1e-5 and abs(row['added_mm3'])<1e-5 and not row['fuzzy_missing_faces'] and not row['fuzzy_added_faces']
            assert row['native_tolerance_mm']<=1e-4 and row['step_tolerance_mm']<=max(row['native_tolerance_mm'],1e-7)+1e-10
        assert e['mass_provenance']['default']['adapter_sha256']==sha(H.parents[1]/'lib/mass_properties.py')
        assert e['mass_provenance']['default']['source_sha256']==sha(H.parents[1]/'lib/occt_mass_properties.cpp')
    repro=read(N/'reverse_short03/reproduction_checks.json')
    assert repro['passed'] and repro['archive_brep_count']==27 and repro['persistent_property_count']==1291 and not repro['allowed_property_differences']
    visual=read(N/'reverse_short03/visual01/visual_review.json');render=read(N/'reverse_short03/visual01/render_receipt.json')
    assert not visual['integration_ready'] and visual['native_sha256']==repro['native_sha256']==render['native_sha256']
    assert visual['render_receipt_sha256']==sha(N/'reverse_short03/visual01/render_receipt.json') and render['renderer_sha256']==sha(H/'render_driver_reverse_short.py')
    assert len(visual['reviewed_images'])==4 and not render['source_camera_refitted']
    for file,digest in visual['reviewed_images'].items():assert sha(N/'reverse_short03/visual01'/file)==digest
    for rel,digest in render['source_hashes'].items():assert sha(ROOT/rel)==digest;deps[rel]=digest
    measurement=read(N/'reverse_short03/source_measurement01/report.json')
    assert measurement['native_sha256']==repro['native_sha256'] and 25.2<measurement['residual_px']<25.3 and not measurement['source_camera_refitted']
    assert measurement['worker_sha256']==sha(H/'measure_driver_reverse_source.py')
    for case,count in [('reverse_short01',1),('reverse_short02',4),('reverse_short_variation02',5)]:
        q=read(N/case/'context_audit/report.json');assert not q['passed'] and len(q['findings'])==count
    for rel,digest in read(N/'reverse_progression_receipt.json')['images'].items():assert sha(ROOT/rel)==digest;deps[rel]=digest
    for file,digest in read(N/'external_controls01/source_screening.json')['inspected_images'].items():assert sha(N/'external_controls01'/file)==digest
    standard=H/'transmission_brake_front_study/trial01/standard_context_manifest.json';bind(standard)
    for rel,digest in read(standard)['native_files'].items():assert sha(ROOT/rel)==digest;deps[rel]=digest
    for f in N.rglob('*'):
        if not f.is_file() or not (f.relative_to(N).parts[0].startswith('reverse') or f.relative_to(N).parts[0]=='external_controls01'):continue
        if any('runtime' in part or part=='__pycache__' for part in f.relative_to(N).parts):continue
        if f.suffix in ['.FCBak','.FCStd1','.pyc']:continue
        bind(f)
        if f.name=='report.json':
            for rel,digest in read(f).get('input_hashes',{}).items():assert sha(ROOT/rel)==digest;deps[rel]=digest
        if f.name.startswith('reverse_source_review'):
            for rel,digest in read(f)['source_hashes'].items():assert sha(ROOT/rel)==digest;deps[rel]=digest
    bind(N/'REVERSE_SHORT_STUDY.md')
    for rel,digest in deps.items():assert sha(ROOT/rel)==digest,rel
    receipt.write_text(json.dumps(dict(short_connection_geometry_checks_passed=True,mechanism_complete=False,historical_geometry_qualified=False,geometry_integrated=False,integration_ready=False,authoritative_parent='cad/003_FullTank/experiments/drive_chains/coupled_driver_integration/integrated01',nominal_native_sha256=repro['native_sha256'],dependencies=deps,scope='Ten reverse-body/short-connection additions;75 checks,53 context pairs and11 strict STEP comparisons per case. Exact27-BRep/1291-property fresh build. Unfinished trigger/quadrant and source-profile discrepancy; no complete mechanism integration.'),indent=2)+'\n')
r=read(receipt)
assert r['short_connection_geometry_checks_passed'] and not any(r[k] for k in ['integration_ready','geometry_integrated','mechanism_complete'])
for rel,digest in r['dependencies'].items():assert sha(ROOT/rel)==digest,rel
print('PASS',len(r['dependencies']),'bound dependencies; reverse body and complete short connection. Full reverse mechanism remains unfinished.')
