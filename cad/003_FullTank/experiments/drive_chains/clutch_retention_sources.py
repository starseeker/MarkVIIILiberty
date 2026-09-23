"""Freeze the plunger-wire inventory and original figures, retaining uncertainty."""
import hashlib
import json
from pathlib import Path
import sqlite3

ROOT=Path(__file__).resolve().parents[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
survey=ROOT/'cad/001_Survey/mark_viii_parts.sqlite'
with sqlite3.connect(f'file:{survey}?mode=ro',uri=True) as db:
    db.row_factory=sqlite3.Row;rows=[]
    for rid in ['SNL:275:023','SNL:275:024','SNL:157:018']:
        row=dict(db.execute('select * from source_records where record_id=?',(rid,)).fetchone())
        row['raw']=json.loads(row.pop('raw_json'))
        row['part_ids']=[r[0] for r in db.execute('select part_id from part_evidence where record_id=?',(rid,))]
        rows.append(row)
assets=[f'references/1928-03-30_SNL_G13/SNL_G13_Project/sources/p{n:03}.jpg' for n in [157,275,293]]
assets+=['references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p293-geometry.png']
result=dict(survey_sha256=sha(survey),records=rows,source_assets={p:sha(ROOT/p) for p in assets},
    inventory=dict(new_wire=1,revised_plungers=6,revised_shared_definitions=1,spool_allocation_is_not_an_extra_piece=True),
    review=dict(original_pages_inspected=[157,275],full_plate21_inspected=True,dimensional_calibration=False,
        conclusions=['SNL275 explicitly specifies SH861K, soft iron W.&M.No16,30in, for SH861A.',
        'SNL157 specifies six SH861A plungers and Plate21callout5. The existing parent resolves their head/tail arrangement.',
        'Plate21 does not resolve a measurable wire route or head drilling. The route and bore geometry are reconstruction assumptions.',
        'The wire is counted once; six existing plunger occurrences retain their shared definition and receive individually clocked holes.']))
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
print('Frozen3source records and4original assets for one wire and six revised heads.')
