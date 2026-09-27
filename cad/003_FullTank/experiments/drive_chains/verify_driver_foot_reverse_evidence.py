"""Verify the selected source packet and exact retained interfaces; no CAD acceptance."""
import argparse,hashlib,json
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[3];S=H/'driver_foot_reverse_study'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--freeze',action='store_true');a=p.parse_args()
r=read(S/'evidence02/report.json');review=read(S/'source_review.json');native=ROOT/r['parent_native'];assert sha(native)==r['parent_native_sha256']==review['parent_native_sha256']
assert len(r['selected_rows'])==44 and len(r['images'])==31 and len(r['retained_interfaces'])==9
assert r['input_hashes'][str((H/'build_driver_foot_reverse_evidence_v2.py').relative_to(ROOT))]==sha(H/'build_driver_foot_reverse_evidence_v2.py')
for f,h in r['input_hashes'].items():assert sha(ROOT/f)==h,f
for v in r['images']:assert sha(S/'evidence02'/v['file'])==v['sha256']
assert sha(S/'evidence02/report.json')==review['evidence_report_sha256']
for f,h in review['inspected_images'].items():assert sha(S/'evidence02'/f)==h
assert set(review['inspected_images'])|set(review['uninspected_collected_images'])=={v['file'] for v in r['images']}
m=read(native.parent/'isolated/manifest.json');rows={v['name']:v for v in m['occurrences']}
assert all(rows[n]==v for n,v in r['retained_interfaces'].items())
assert sum(v['definition']=='Def_DriverClutchFrontRod_M576' for v in rows.values())==3
assert r['complete_selected_pages']['118'][7]['item'].strip().startswith('*one M177')
assert review['source_identity_conflicts'][0]['original_printed_mark']=='M177'
assert not r['geometry_created'] and not review['geometry_created'] and not review['geometry_qualified']
receipt=S/'evidence_receipt.json'
if a.freeze:
 assert not receipt.exists();deps=dict(r['input_hashes'])
 for f in [Path(__file__),S/'README.md',S/'source_review.json',S/'evidence02/report.json',native.parent/'qualification.json',*[S/'evidence02'/v['file'] for v in r['images']]]:deps[str(f.relative_to(ROOT))]=sha(f)
 receipt.write_text(json.dumps(dict(dependencies=deps,source_packet_verified=True,geometry_created=False,geometry_qualified=False,parent_native_sha256=sha(native),selected_rows=44,source_views=31,inspected_images=10,retained_interfaces=9),indent=2)+'\n')
q=read(receipt)
for f,h in q['dependencies'].items():assert sha(ROOT/f)==h,f
print('PASS',len(q['dependencies']),'dependencies;44 rows,31 collected/10 inspected views,9 exact retained interfaces; no new geometry.')
