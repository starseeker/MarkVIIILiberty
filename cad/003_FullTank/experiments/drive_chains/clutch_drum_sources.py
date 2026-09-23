"""Freeze outer drum/flywheel inventory, dimensional evidence and conflicts."""
import hashlib
import json
from pathlib import Path
import sqlite3

ROOT=Path(__file__).resolve().parents[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
survey=ROOT/'cad/001_Survey/mark_viii_parts.sqlite'
ids=['SNL:83:034','SNL:83:035','SNL:95:015','SNL:201:002','SNL:276:004','SNL:275:023',
     'SNL:115:002','SNL:203:019','SNL:212:011','HB:nomenclature:201:025','HB:nomenclature:201:026','HB:nomenclature:201:027',
     'HB:spec:112','HB:legend:116:016']
with sqlite3.connect(f'file:{survey}?mode=ro',uri=True) as db:
    db.row_factory=sqlite3.Row;rows=[]
    for rid in ids:
        r=dict(db.execute('select * from source_records where record_id=?',(rid,)).fetchone());r['raw']=json.loads(r.pop('raw_json'))
        r['part_ids']=[x[0] for x in db.execute('select part_id from part_evidence where record_id=?',(rid,))];rows.append(r)
assets=[f'references/1928-03-30_SNL_G13/SNL_G13_Project/sources/p{n:03}.jpg' for n in [83,95,115,201,203,211,212,275,276,293]]
assets+=['references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p293-geometry.png']
assets+=[f'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/original_scans/MarkVIII{n:03}.jpg' for n in [58,59,82,83,94,101]]
assets+=['references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate111.png']
result=dict(survey_sha256=sha(survey),records=rows,source_assets={p:sha(ROOT/p) for p in assets},
    inventory=dict(drum=1,flywheel=1,screws=6,drum_wire=1,new_physical=9,revised_plunger_wire=1),
    source_decisions=[
        'SNL95 flywheel callout16Plate21 conflicts with actual Plate21callout16 stopdrum870; HB71callout16 names flywheel. Preserve this cross-reference conflict.',
        'SH866A drum is bolted to SH868A flywheel by six SH866B screws. Each5/8x1-1/4in screw is threaded1in and has a drilled hex head.',
        'SH866C is one48in wire. Spool allocation275:023 is corroboration, not another installed wire.',
        'HB115 largest flywheel diameter19.811in controls the selected reconstruction; source figure outlines are not calibrated.',
        'HB162-165 confirms starter pinion meshes with flywheel teeth and calls for3/8in disengaged edge gap. Tooth count and form remain estimates until better evidence is found.',
        'HB71/111 section shows the long hub continuous with the dished flywheel. A removable tapered/keyed mounting cannot pass over a larger integral shaft-end spline; positive teeth are therefore inferred on the flywheel hub extension. HB wording instead calls them crankshaft teeth. Explicit interpretation, not historical certainty.',
        'SNL203:019 and212 specify ONE No10(3/16)-24x3/4 flathead screw for SH136B; HB201 specifies TWO SH64JH. Preserve quantity/identity conflict and select SNL for future key installation.',
        'Key, screw, crankshaft nut/retention, complete crankshaft/thrust bearing and starter are still separate required work. No shaft coupon is counted as a completed engine component.'
    ],original_figures_reviewed=['Full SNL21','Full HB71 and111','HB40/SNL14 engine sections (flywheel absent)','Full HB162-165 and Plate106'],
    calibrated_drawing=False)
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
print('Frozen outer drum/flywheel evidence, nine new occurrences, key-screw and hub interpretation conflicts.')
