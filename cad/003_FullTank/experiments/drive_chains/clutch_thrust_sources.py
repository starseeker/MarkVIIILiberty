"""Freeze catalogue identities and source assets for the clutch thrust mechanism."""
import hashlib
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[4]
SURVEY = ROOT/'cad/001_Survey/mark_viii_parts.sqlite'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


selected = ['SNL:8:016', 'SNL:67:020', 'SNL:164:002', 'SNL:164:004',
            'SNL:164:005', 'SNL:165:003', 'SNL:157:018']
with sqlite3.connect(f'file:{SURVEY}?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    rows = []
    for rid in selected:
        row = dict(db.execute('select * from source_records where record_id=?', (rid,)).fetchone())
        row['raw'] = json.loads(row.pop('raw_json'))
        row['part_ids'] = [r[0] for r in db.execute('select part_id from part_evidence where record_id=?', (rid,))]
        rows.append(row)
    ids = sorted({pid for row in rows for pid in row['part_ids']})
    identities = [dict(db.execute('select * from parts where part_id=?', (pid,)).fetchone()) for pid in ids]
    variants = [dict(r) for pid in ids for r in db.execute('select * from part_variants where part_id=?', (pid,))]
assets = [f'references/1928-03-30_SNL_G13/SNL_G13_Project/sources/p{n:03}.jpg' for n in [8,67,157,164,165,293]]
assets += ['references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p293-geometry.png',
           'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/original_scans/MarkVIII058.jpg',
           'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/original_scans/MarkVIII059.jpg']
result = dict(survey_sha256=sha(SURVEY), records=rows, identities=identities, variants=variants,
    source_assets={p:sha(ROOT/p) for p in assets},
    inventory=dict(retainer=1, balls=30, spring_stop_ring=1, new_physical=32,
                   revised_existing_thrust_collar=1, assembly_heading_is_extra_physical_part=False),
    source_review=dict(full_figures_inspected=True,
        plate21_callouts={'28':'SH998B thrust collar', '29':'SH998C retainer plus 30 balls', '4':'SH998A spring-stop ring'},
        inspection_viewport=[320,635,590,800], viewport_asset=assets[6],
        dimensional_calibration=False,
        note='Full plate establishes separate members; enlarged lower section informs the opposing race arrangement. Catalogue quantity/size is printed, while all race and cage dimensions are estimates. HB marks differ. No load or manufacturing qualification.'),
    decisions=[
        'SNL8:016 and164:005 describe the same thirty quarter-inch balls; do not count sixty.',
        'The parent thrust collar remains one existing physical part. Retainer assembly164:002 is a container only.',
        'Use forward-facing pocket and opposing stop-ring boss, with rounded axial reaction grooves. Exact historic contour and cage construction are unresolved.',
        'Six stop-ring holes are provisional interfaces for later SH861A plungers, using HB115 diameter plus stated clearance. Hole pitch and phase remain adjustable.',
        'Thirty shared-definition balls, cage and ring are geometry for the standard static view. Springs, cones, crankshaft and operating linkages remain unfinished.'
    ])
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print('Frozen seven source records: 32 new physical occurrences, one revised parent.')
