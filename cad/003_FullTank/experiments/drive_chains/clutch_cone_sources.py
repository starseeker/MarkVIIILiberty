"""Freeze cone and spring catalogue evidence without modifying the survey."""
import hashlib
import json
from pathlib import Path
import sqlite3

ROOT=Path(__file__).resolve().parents[4]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
survey=ROOT/'cad/001_Survey/mark_viii_parts.sqlite'
ids=['SNL:68:010']+[f'SNL:68:{n:03}' for n in range(12,18)]+[
    'SNL:157:018','SNL:164:006','SNL:165:002','SNL:219:025','SNL:167:012']
with sqlite3.connect(f'file:{survey}?mode=ro',uri=True) as db:
    db.row_factory=sqlite3.Row; rows=[]
    for rid in ids:
        r=dict(db.execute('select * from source_records where record_id=?',(rid,)).fetchone())
        r['raw']=json.loads(r.pop('raw_json'))
        r['part_ids']=[a[0] for a in db.execute('select part_id from part_evidence where record_id=?',(rid,))]
        rows.append(r)
assets=[f'references/1928-03-30_SNL_G13/SNL_G13_Project/sources/p{n:03}.jpg' for n in [68,157,164,165,167,219,293]]
assets+=['references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p293-geometry.png']
assets+=[f'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/original_scans/MarkVIII{n:03}.jpg' for n in [58,59]]
angle=93+31/60+36/3600
result=dict(survey_sha256=sha(survey),records=rows,source_assets={p:sha(ROOT/p) for p in assets},
    inventory=dict(cone=1,lining=1,plug=1,support_rivet=6,lining_rivet=43,plunger=6,cup=6,spring=6,ring=1,
                   new_physical=71,revised_support=1,cone_assembly_nonphysical=True),
    pattern_check=dict(radii_in=[36.924,34.424],angle_deg=angle,derived_diameters_in=[2*r*angle/360 for r in [36.924,34.424]],table_diameters_in=[19.186,17.887]),
    source_review=dict(full_figures_inspected=True,dimensional_calibration=False,inspection_viewport=[330,305,675,455],
      plate21_callouts={'3':'cone assembly','4':'existing SH998A stop ring','5':'SH861A plungers','6':'SH861C cups','7':'SH861F springs','8':'SH849C ring','9':'existing SH869A support','31':'six cone/support rivets'}),
    decisions=[
      'Reuse and refine SH869A; do not count the cone assembly heading or supporting collar a second time.',
      'Six support rivets, not the24 total across unrelated SNL167 allocations.',
      'HB72 pattern closes a conical surface and supports treating2.5in as slant width. HB and SNL marks differ; transfer remains conditional.',
      '58.5in expanded length differs from computed mean circumference by6.753mm; do not distort supported diameters to absorb this discrepancy.',
      'SNL small-spring free length117.475mm conflicts with HB148.59mm. Installed height is seat-derived, neither quoted free length is silently used as installed height.',
      'Lining material wording conflicts within HB115; geometric lining is named without claiming material identification.',
      'Support has six axial cup bores, inclined riveted cone seat, and preserved keyed running bore. Cups receive springs from a separate rear ring threaded onto plunger tails.',
      'Port location, section stock, cup/ring profiles, threaded envelopes, rivet layout and upset form remain explicit reconstruction assumptions.'
    ])
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
print('Frozen12source records;71new physical components plus one reused/refined support.')
