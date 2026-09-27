"""Verify the frozen central pedal CAD study without accepting its unresolved graph."""
import argparse,hashlib,json,math
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[3];N=H/'driver_foot_reverse_study'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--freeze',action='store_true');a=p.parse_args()
receipt=N/'central_study_receipt.json'
if a.freeze:
    assert not receipt.exists()
    deps=dict(read(N/'profile_study_receipt.json')['dependencies'])
    def bind(p):
        p=Path(p).resolve();deps[str(p.relative_to(ROOT))]=sha(p)
    bind(N/'profile_study_receipt.json');bind(Path(__file__))
    for name in ['build_driver_central_pedal.py','build_driver_central_pedal_v2.py','build_driver_central_pedal_v3.py',
                 'driver_central_pedal_parts.py','driver_central_pedal_parts_v2.py','driver_central_pedal_parts_v3.py',
                 'check_driver_central_pedal.py','check_driver_central_pedal_v2.py','render_driver_central_pedal.py',
                 'exchange_driver_central_pedal.py','exchange_driver_central_pedal_v2.py','exchange_driver_central_pedal_v3.py',
                 'diagnose_driver_central_pedal.py','diagnose_driver_central_mass.py','probe_driver_foot_central_compatibility.py']:
        bind(H/name)
    for case in ['central03','central_variation03']:
        folder=N/case;r=read(folder/'report.json');m=read(folder/'isolated/manifest.json');native=folder/r['native_file']
        assert sha(native)==r['native_sha256']==m['native_sha256']
        assert len(r['new_occurrences'])==10 and len(r['new_definitions'])==7 and len(m['occurrences'])==12
        assert not r['changed_definitions'] and not r['geometry_integrated'] and not r['details']['mechanism_complete']
        for rel,count,worker in [('checks03/independent_checks.json',63,'check_driver_central_pedal_v2.py'),('exchange03/exchange_checks.json',17,'exchange_driver_central_pedal_v3.py')]:
            q=read(folder/rel)
            assert q['passed'] and q['native_sha256']==sha(native) and q['checker_sha256']==sha(H/worker)
            assert len(q['checks'])==count and all(x['passed'] for x in q['checks'])
        q=read(folder/'context_audit/report.json')
        assert q['passed'] and not q['findings'] and len(q['pairs'])==34 and q['context_occurrences']==8997
        assert q['native_sha256']==sha(native)
        e=read(folder/'exchange03/exchange_checks.json');assert e['same_step_bytes']
        assert e['prior_receipt_sha256']==sha(folder/'exchange01/exchange_checks.json')
        for file,digest in e['step_hashes'].items():assert sha(folder/'exchange03'/file)==digest==sha(folder/'exchange01'/file)
        for row in e['checks']:
            assert row['native_mass']['converged'] and row['step_mass']['converged'] and row['centroid_error_mm']<1e-5
        assert e['mass_provenance']['default']['adapter_sha256']==sha(H.parents[1]/'lib/mass_properties.py')
        assert e['mass_provenance']['default']['source_sha256']==sha(H.parents[1]/'lib/occt_mass_properties.cpp')
    repro=read(N/'central03/reproduction_checks.json')
    assert repro['passed'] and repro['archive_brep_count']==40 and repro['persistent_property_count']==1501 and not repro['allowed_property_differences']
    visual=read(N/'central03/visual01/visual_review.json');render=read(N/'central03/visual01/render_receipt.json')
    assert not visual['integration_ready'] and visual['native_sha256']==repro['native_sha256']==render['native_sha256']
    assert visual['render_receipt_sha256']==sha(N/'central03/visual01/render_receipt.json')
    assert render['renderer_sha256']==sha(H/'render_driver_central_pedal.py') and len(visual['reviewed_images'])==5
    for file,digest in visual['reviewed_images'].items():assert sha(N/'central03/visual01'/file)==digest
    for rel,digest in render['source_hashes'].items():assert sha(ROOT/rel)==digest;deps[rel]=digest
    compatibility=read(N/'central_compatibility01/report.json')
    assert compatibility['central_native_sha256']==repro['native_sha256'] and len(compatibility['pairs'])==20 and len(compatibility['findings'])==2
    assert all(4678<v['intersection_mm3']<4679 for v in compatibility['findings'])
    repair=compatibility['rigid_representation_repair'];assert repair['missing_mm3']<1e-5 and repair['added_mm3']<1e-5
    assert compatibility['worker_sha256']==sha(H/'probe_driver_foot_central_compatibility.py')
    for item in read(N/'central_sources01/report.json')['images']:
        for key in ['image','source']:assert sha(ROOT/item[key])==item[key+'_sha256'];bind(ROOT/item[key])
    for rel,digest in read(N/'central_progression_receipt.json')['images'].items():assert sha(ROOT/rel)==digest;deps[rel]=digest
    for file in N.rglob('*'):
        if not file.is_file() or not file.relative_to(N).parts[0].startswith('central'):continue
        if any('runtime' in part or part=='__pycache__' for part in file.relative_to(N).parts):continue
        if file.suffix in ['.FCBak','.FCStd1','.pyc']:continue
        bind(file)
        if file.name=='report.json':
            for rel,digest in read(file).get('input_hashes',{}).items():assert sha(ROOT/rel)==digest;deps[rel]=digest
    bind(N/'CENTRAL_PEDAL_STUDY.md')
    for rel,digest in deps.items():assert sha(ROOT/rel)==digest,rel
    receipt.write_text(json.dumps(dict(central_group_geometry_checks_passed=True,mechanism_connectivity_qualified=False,
        historical_geometry_qualified=False,geometry_integrated=False,integration_ready=False,
        authoritative_parent='cad/003_FullTank/experiments/drive_chains/coupled_driver_integration/integrated01',
        nominal_native_sha256=repro['native_sha256'],dependencies=deps,
        scope='Ten central-group additions;63 saved checks,34 context pairs and17 strict STEP comparisons per case. Exact40-BRep/1501-property fresh rebuild. Prior M769 profile intersects this bridle; reconcile source graph before integration.'),indent=2)+'\n')
r=read(receipt)
assert r['central_group_geometry_checks_passed'] and not any(r[k] for k in ['integration_ready','geometry_integrated','mechanism_connectivity_qualified'])
for rel,digest in r['dependencies'].items():assert sha(ROOT/rel)==digest,rel
print('PASS',len(r['dependencies']),'bound dependencies; central pedal CAD study. Combined M769/bridle graph remains unresolved.')
