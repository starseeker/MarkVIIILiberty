"""Verify source-only seat-fitting evidence without inventing installed parts."""
import hashlib
import json
from pathlib import Path

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
S = H/'seat_adjustment_study'
receipt = json.loads((S/'evidence_receipt.json').read_text())
assert receipt['evidence_only'] and not receipt['geometry_created']
for file, expected in receipt['dependencies'].items():
    assert hashlib.sha256((ROOT/file).read_bytes()).hexdigest() == expected, file
r = json.loads((S/'evidence01/report.json').read_text())
assert len(r['selected_rows']) == 13 and not r['geometry_created'] and not r['source_camera_refitted']
items = {v['mark']:v for v in r['inventory_candidates']}
assert items['SH291C']['quantity'] == 1 and items['SH291C']['printed_length_mm'] == 88.9
assert items['SH291D']['quantity'] is None and items['SH291D']['rivets_per_named_application'] == 2
assert items['SH291F']['quantity'] is None and items['SH291F']['rivets_per_named_application'] == 10
assert items['SH291D']['printed_rivet_diameter_mm'] == 6.35
assert items['SH291F']['printed_rivet_diameter_mm'] == 4.7625
print('PASS:',len(receipt['dependencies']),'bound seat-fitting dependencies; C/D/F mounting remains unresolved; no geometry added.')
