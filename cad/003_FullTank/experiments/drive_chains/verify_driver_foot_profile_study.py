"""Verify a frozen CAD profile study; never promote its unresolved mechanism."""
import argparse,hashlib,json
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[3];N=H/'driver_foot_reverse_study'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--freeze',action='store_true');a=p.parse_args()
receipt=N/'profile_study_receipt.json'
if a.freeze:
    assert not receipt.exists()
    deps=dict(read(N/'evidence_receipt.json')['dependencies'])
    def bind(p):deps[str(p.resolve().relative_to(ROOT))]=sha(p)
    workers=['build_driver_foot_link_profile.py','build_driver_foot_link_profile_v2.py','build_driver_foot_link_profile_v3.py',
        'driver_foot_link_parts.py','build_driver_foot_topology_views.py','check_driver_foot_link_profile.py',
        'probe_driver_foot_topology.py','probe_driver_foot_rod_closure.py','probe_driver_foot_rod_closure_v2.py',
        'render_driver_foot_link_profile.py','exchange_driver_foot_link_profile.py','exchange_driver_foot_link_profile_v2.py',
        'exchange_driver_foot_link_profile_v3.py','exchange_control_rebuild_clutch_swing.py','pump_integration_worker.py',
        'check_control_rebuild_reproduction.py','check_driver_seat_context.py','control_rebuild_io_v2.py','control_rebuild_io.py',
        'control_rebuild_surface_mass_v6.py','control_rebuild_surface_mass_v6.cpp',Path(__file__).name]
    for worker in workers:bind(H/worker)
    for name in ['mass_properties.py','occt_mass_properties.cpp','kronrod_mass.py','occt_kronrod_mass.cpp',
                 'camera_review.py','cad_build.py','evidence.py','step_matching.py','visual_review.py','raster.py']:
        bind(H.parents[1]/'lib'/name)
    proof=H/'driver_seat_study/diagnostics/mass_controls02/qualification.json';bind(proof)
    assert read(proof)['passed']
    for case in ['profile03','profile_variation03']:
        folder=N/case;r=read(folder/'report.json');m=read(folder/'isolated/manifest.json')
        native=folder/r['native_file'];assert sha(native)==r['native_sha256']==m['native_sha256']
        assert len(r['new_occurrences'])==2 and len(r['new_definitions'])==1 and not r['geometry_integrated']
        for rel,count in [('checks03/independent_checks.json',49),('exchange04/exchange_checks.json',3)]:
            q=read(folder/rel);assert q['passed'] and q['native_sha256']==sha(native) and len(q['checks'])==count
            assert all(x['passed'] for x in q['checks'])
        context=read(folder/'context_audit/report.json')
        assert context['passed'] and context['native_sha256']==sha(native) and context['context_occurrences']==8989 and len(context['pairs'])==6 and not context['findings']
        exchange=read(folder/'exchange04/exchange_checks.json')
        assert exchange['checker_sha256']==sha(H/'exchange_driver_foot_link_profile_v3.py')
        for rel,digest in exchange['step_hashes'].items():assert sha(folder/'exchange04'/rel)==digest
        assert read(folder/'exchange04/diagnosis.json')['same_step_bytes']
        assert exchange['mass_provenance']['spring']['adapter_sha256']==sha(H/'control_rebuild_surface_mass_v6.py')
        assert exchange['mass_provenance']['spring']['source_sha256']==sha(H/'control_rebuild_surface_mass_v6.cpp')
        for rel,digest in r['input_hashes'].items():assert sha(ROOT/rel)==digest;deps[rel]=digest
        bind(ROOT/r['parent_native'])
    repro=read(N/'profile03/reproduction_checks.json');assert repro['passed'] and repro['archive_brep_count']==26 and repro['persistent_property_count']==966
    visual=read(N/'profile03/visual01/visual_review.json');assert visual['disposition']=='reviewed_profile_study_only' and not visual['integration_ready']
    assert visual['native_sha256']==read(N/'profile03/report.json')['native_sha256']==repro['native_sha256']
    for image,digest in visual['reviewed_images'].items():assert sha(N/'profile03/visual01'/image)==digest==sha(N/'profile02/visual01'/image)
    closure=read(N/'rod_closure03/report.json');assert closure['worker_sha256']==sha(H/'probe_driver_foot_rod_closure_v2.py') and not closure['connections_closed']
    assert closure['candidate_native_sha256']==visual['native_sha256']
    assert all(abs(x['required_single_fork_pin_to_face_mm']-90.26399608461838)<1e-7 for x in closure['cases'])
    for file in N.rglob('*'):
        if not file.is_file() or any('runtime' in x or x=='__pycache__' for x in file.relative_to(N).parts):continue
        if file.suffix in ['.FCBak','.FCStd1','.pyc']:continue
        bind(file)
        if file.name=='report.json':
            for rel,digest in read(file).get('input_hashes',{}).items():assert sha(ROOT/rel)==digest;deps[rel]=digest
    for rel,digest in read(N/'profile_progression_receipt.json')['images'].items():assert sha(ROOT/rel)==digest;deps[rel]=digest
    receipt.write_text(json.dumps(dict(profile_construction_passed=True,mechanism_connectivity_qualified=False,
        historical_geometry_qualified=False,geometry_integrated=False,integration_ready=False,
        authoritative_parent='cad/003_FullTank/experiments/drive_chains/coupled_driver_integration/integrated01',
        nominal_native_sha256=visual['native_sha256'],dependencies=deps,
        scope='Two profile-study solids,49 checks and6 context pairs per stock case,3 strict STEP comparisons per case; exact fresh rebuild. Topology and complete physical connections remain unresolved.'),indent=2)+'\n')
r=read(receipt)
assert r['profile_construction_passed'] and not r['integration_ready'] and not r['geometry_integrated'] and not r['mechanism_connectivity_qualified']
for rel,digest in r['dependencies'].items():assert sha(ROOT/rel)==digest,rel
print('PASS',len(r['dependencies']),'bound dependencies; CAD profile study only. Mechanism not connected or integrated.')
