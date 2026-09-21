"""Preserve distinct HB/SNL identities for the connected main-clutch stack."""
from pathlib import Path
import hashlib
import json
import sqlite3

REPO = Path(__file__).resolve().parents[4]
SURVEY = REPO / 'cad/001_Survey/mark_viii_parts.sqlite'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


selected = ['SNL:17:016','SNL:67:018','SNL:114:024','SNL:217:024','SNL:165:001',
    'SNL:67:019','SNL:67:020','SNL:164:002','SNL:164:004','SNL:164:005','SNL:165:003',
    'HB:legend:116:008','HB:legend:116:009','HB:legend:116:012','HB:legend:116:020']
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
    variants = [dict(row) for pid in ids for row in db.execute('select * from part_variants where part_id=?', (pid,))]
assets = [f'references/1928-03-30_SNL_G13/SNL_G13_Project/sources/p{n:03}.jpg'
    for n in [17,67,114,164,165,217,293]]
assets += ['references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p293-geometry.png',
    'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate71.png',
    'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/original_scans/MarkVIII059.jpg']
result = dict(status='Connected main-clutch stack; cones, thrust mechanism and engine interfaces pending',
    survey_sha256=sha(SURVEY), records=rows, identities=identities, variants=variants,
    source_assets={name:sha(REPO/name) for name in assets},
    inventory=dict(bearing=1,sleeve=1,cone_support=1,keys=4,thrust_collar=1,snap_ring=1,total_new=9),
    decisions=[
        'SNL Plate21 shows a long bearing with middle bore relief and a sleeve nested in its rear band. They are not placed end-to-end. Original source pages17,67,114,165 and217 confirm selected marks and quantities.',
        'SH869A cone support agrees between HB and SNL. Catalogue SH998D bearing,SH861B sleeve andSH861E snap ring differ from HB SH863A,SH864C andSH863C. Variant membership remains unresolved; no universal equivalence is inferred.',
        'HB117 sleeve2.687in length,3.531in ID and24splines are provisional transfers. ID is interpreted at internal tooth tips. Groove depth/width and straight tooth form are estimates.',
        'HB1174.002in bearing bore is transferred provisionally to the forward journal band. The different SNL profile uses a larger rear sleeve bore and relieved middle. HB4.684in bearing OD is not applied;152mm OD is estimated for this profile.',
        'HB117 preliminary-drive key4.25in long,.75in thick,.375in wide is transferred provisionally to the four catalogue SH861D keys. Thickness is selected radially and width tangentially; exact section-axis interpretation remains uncertain.',
        'SH999A body/bore, four key beds and end groove are revised together to receive the stack. Cone support follows a documented inferred profile; actual cone/rivet attachment is pending.',
        'Full SNL21 callout tracing corrects the rejected first candidate:28identifies the large SH998B thrust collar at the bearing end;30identifies the separate external SH861E ring aft of that collar. The unsupported internal snap-ring groove is removed.',
        'SH998B has an inferred bearing-end plug, front disk and outer guiding lip. SH861E is a separate split ring seated in an external SH999A groove. Profiles, attachment, fits and elastic installation remain unqualified.',
        'Sleeve rear flange and bearing OD use nominal fitted surfaces in SH999A. Exact sleeve-to-collar drive attachment is unresolved. This does not qualify torque transmission or the eventual crankshaft positive engagement.',
        'SH998C retainer and30quarter-inchballs,SH998A stop ring,cones/linings/rivets and six spring-plunger sets remain unbuilt. Source assembly rows are not extra physical pieces.'
    ])
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print('Retained15source records;9new physical pieces with explicit dimensional transfers.')
