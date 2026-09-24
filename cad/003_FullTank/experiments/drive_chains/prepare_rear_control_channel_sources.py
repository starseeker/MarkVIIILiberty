"""Retain channel-specific evidence without changing the qualified joint packet."""
import argparse
import json
from pathlib import Path
import sqlite3
import sys

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path.insert(0, str(H.parents[1]))
from lib.evidence import sha, write

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
out = a.output.resolve()
assert not out.exists(), 'Evidence versions must be written to a new directory'
out.mkdir(parents=True)
db = ROOT / 'cad/001_Survey/mark_viii_parts.sqlite'
c = sqlite3.connect(db.as_uri() + '?mode=ro&immutable=1', uri=True)
c.row_factory = sqlite3.Row
marks = [f'M{i}' for i in range(4128, 4139)]
records = {}
for row in c.execute('SELECT * FROM source_records'):
    raw = json.loads(row['raw_json'])
    text = row['description'] + ' ' + raw.get('brit', '')
    selected = row['source_id'] == 'SNL' and (
        any(mark in text for mark in marks)
        or row['printed_page'] == '63' and 3 <= row['row_no'] <= 14
        or row['printed_page'] == '36' and 15 <= row['row_no'] <= 18)
    selected |= row['source_id'] == 'HB' and row['printed_page'] == '190' and row['row_no'] >= 59
    if selected:
        records[row['record_id']] = dict(row)
        records[row['record_id']]['part_ids'] = [v[0] for v in c.execute(
            'SELECT DISTINCT part_id FROM part_evidence WHERE record_id=?', (row['record_id'],))]
identities = {mark: [dict(v) for v in c.execute(
    'SELECT * FROM part_identifiers WHERE identifier=?', (mark,))] for mark in marks}
files = {ROOT / v['source_path'] for v in records.values()}
hb = ROOT / 'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets'
snl = ROOT / 'references/1928-03-30_SNL_G13/SNL_G13_Project'
images = [hb / f'plate{i}.png' for i in (92, 104, 113)] + [snl / 'assets/p280-geometry.png']
images += [snl / f'sources/p{i:03d}.jpg' for i in (33, 36, 39, 63, 65, 169, 170)]
files.update(images)
pages = [dict(v) for v in c.execute(
    "SELECT * FROM source_pages WHERE source_id='HB' AND printed_page IN ('148','149','150','158','159','190')")]
files.update(ROOT / v['path'] for v in pages)
conflicts = [
    dict(id='left_cleat_quantity', mark='M4130', alternatives=[
        dict(quantity=2, records=['HB:nomenclature:190:061']),
        dict(quantity=4, records=['SNL:63:006', 'SNL:65:023', 'SNL:170:006'])],
        note='Later SNL aggregate and separate physical row agree; twelve rivets at three per cleat support four. Handbook transcription must be checked against the scan. Do not multiply both variants.'),
    dict(id='fulcrum_quantity', mark='M4131', alternatives=[
        dict(quantity=5, records=['HB:nomenclature:190:062']),
        dict(quantity=4, records=['SNL:36:015', 'SNL:36:017', 'SNL:63:005', 'SNL:141:016', 'SNL:170:007'])],
        note='SNL gives four bracket assemblies, four split pins and eight mounting rivets. Handbook five may be an error or variant; do not silently correct the literal row.')]
write(out / 'sources.json', dict(
    scope='Rear channel M4128, cleats, spring supports and brake fulcrums; additive evidence for the existing control study.',
    survey_sha256=sha(db), producer_sha256=sha(Path(__file__)),
    source_records=[records[k] for k in sorted(records)], part_identifier_rows=identities,
    source_pages=pages, source_hashes={str(f.relative_to(ROOT)): sha(f) for f in sorted(files)},
    image_paths=[str(f.relative_to(ROOT)) for f in images], quantity_conflicts=conflicts,
    interfaces=[
        dict(records=['SNL:33:005'], feature='M4129 floor attachment', diameter_mm=19.05, stock_length_mm=41.275, quantity=2, note='One bolt with plain nut and lock washer per cleat. Attachment surface and length datum need image/geometry review.'),
        dict(records=['SNL:33:007'], feature='M4130 floor attachment', diameter_mm=19.05, stock_length_mm=50.8, quantity=4, note='One bolt with plain nut and lock washer per cleat.'),
        dict(records=['SNL:169:011', 'SNL:63:011'], feature='M4135 mounting rivets', diameter_mm=12.7, stock_length_mm=19.05, quantity=4),
        dict(records=['SNL:170:005', 'SNL:63:012'], feature='M4136 mounting rivets', diameter_mm=12.7, stock_length_mm=47.625, quantity=4),
        dict(records=['SNL:170:006', 'SNL:63:013'], feature='M4130 mounting rivets', diameter_mm=12.7, stock_length_mm=50.8, quantity=12),
        dict(records=['SNL:170:007', 'SNL:63:014'], feature='M4131 mounting rivets', diameter_mm=12.7, stock_length_mm=53.975, quantity=8),
        dict(records=['SNL:36:018', 'SNL:141:016'], feature='M4131 pivot retention', split_pin_diameter_mm=6.35, split_pin_length_mm=50.8, quantity=4)],
    projection_policy=dict(
        plan_side='HB92/HB113/SNL6 are related drawings with explicit rod-length breaks. Only intact local segments can be registered; no overall longitudinal scale.',
        photograph='HB104 is perspective. Preserve its feature identifications; no calibrated camera is claimed.',
        reuse='Retain any established local registration. Add new features as independent checks first; changed source or anchor evidence triggers targeted review before fitting.'),
    geometry_modified=False, historical_geometry_qualified=False))
print(f'Retained {len(records)} source rows, {len(conflicts)} quantity conflicts; no CAD mutation')
