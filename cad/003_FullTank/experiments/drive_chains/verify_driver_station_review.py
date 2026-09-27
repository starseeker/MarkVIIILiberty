"""Verify bounded station diagnostics without declaring installation acceptance."""
import argparse
import hashlib
import json
import math
from pathlib import Path

H=Path(__file__).resolve().parent
ROOT=H.parents[3]
STUDY=H/'driver_station_review'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--freeze',action='store_true');a=p.parse_args()
    review=read(STUDY/'visibility01/report.json')
    dependencies=dict(review['input_hashes'])
    assert not review['source_camera_refitted'] and not review['geometry_modified']
    assert review['shaft_pair']['swing_residual_px'] < 1
    assert not review['shaft_pair']['independent_validation']
    for r in review['full_stock_closure'].values():
        assert r['printed_core_mm']==1257.3
        assert abs(math.dist(r['required_receiver_world_mm'],r['hypothetical_driver_pin_mm'])-1308.1)<1e-7
        assert 165 < r['core_shortfall_if_fixed_mm'] < 166
        assert -166 < r['required_receiver_x_shift_mm'] < -165
    receipt=read(STUDY/'profile_probe01/probe_receipt.json')
    assert receipt['review_sha256']==sha(STUDY/'visibility01/report.json')
    assert receipt['worker_sha256']==sha(H/'probe_driver_station_profiles.py')
    assert not receipt['installation_qualified'] and not receipt['source_camera_refitted']
    pair_total=0
    for name,pairs in [('overall_control',200),('pivot_reach',200),('functional_current',202),('functional_source',202)]:
        folder=STUDY/'profile_probe01'/name;r=read(folder/'report.json');q=read(folder/'clearance_report.json')
        digest=sha(folder/r['native_file']);bound=receipt['cases'][name]
        assert digest==r['native_sha256']==q['native_sha256']==bound['native_sha256']
        assert sha(folder/'report.json')==bound['report_sha256']
        assert sha(folder/'clearance_report.json')==bound['clearance_report_sha256']
        assert q['worker_sha256']==sha(H/'probe_driver_station_profiles.py')
        assert r['prototype_physical_occurrences']==150 and len(q['valid_saved_solids'])==150
        assert all(v['passed'] for v in q['valid_saved_solids'])
        assert len(q['pairs'])==pairs and all(v['passed'] for v in q['pairs'])
        assert q['local_clearance_passed'] and q['no_mating_exemptions'] and not q['findings']
        assert not q['installation_qualified'] and not q['geometry_integrated']
        assert not r['historical_geometry_qualified'] and not r['installation_qualified']
        assert set(r['specs'])==set(r['details']['unit_occurrences']+r['details']['seat_occurrences']+r['details']['bow_occurrences'])
        assert len(r['details']['unit_occurrences'])==72
        assert all(v['bow_distance_mm']>37 for v in q['handles'].values())
        dependencies.update(r['input_hashes']);dependencies[r['parent_native']]=r['parent_native_sha256']
        pair_total+=pairs
    assert receipt['image_sha256']==sha(STUDY/'profile_probe01/source_comparison.png')
    for file,digest in review['images'].items():assert sha(STUDY/'visibility01'/file)==digest
    dependencies[str((H/'probe_driver_station_profiles.py').relative_to(ROOT))]=receipt['worker_sha256']
    for file,digest in dependencies.items():assert sha(ROOT/file)==digest,file
    for path in STUDY.rglob('*'):
        if path.is_file() and path.name!='study_receipt.json':dependencies[str(path.relative_to(ROOT))]=sha(path)
    dependencies[str(Path(__file__).relative_to(ROOT))]=sha(Path(__file__))
    frozen=dict(dependencies=dependencies,total_pairs=pair_total,geometry_integrated=False,
        installation_qualified=False,scope='Source identity review and four bounded150-part clearance experiments only.')
    path=STUDY/'study_receipt.json'
    if a.freeze:
        assert not path.exists();path.write_text(json.dumps(frozen,indent=2)+'\n')
    else:
        assert read(path)==frozen
    print(f'Station review verified: {len(dependencies)} dependencies; {pair_total} local pairs clear; installation remains unqualified.')


if __name__=='__main__':main()
