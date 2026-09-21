"""Source identities, quantity scopes and dimensional transfers for front clutch."""
from pathlib import Path
import hashlib,json,sqlite3
REPO=Path(__file__).resolve().parents[4];OUT=Path(__file__).with_suffix('.json')
SURVEY=REPO/'cad/001_Survey/mark_viii_parts.sqlite'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
selected=['SNL:73:016','SNL:94:013','SNL:219:024','SNL:33:004','SNL:165:002',
 'HB:legend:116:013','HB:legend:116:025','HB:legend:116:026','HB:nomenclature:188:018']
with sqlite3.connect(f'file:{SURVEY}?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row;rows=[]
 for rid in selected:
  r=dict(db.execute('select * from source_records where record_id=?',(rid,)).fetchone())
  r['raw']=json.loads(r.pop('raw_json'));r['part_ids']=[x[0] for x in db.execute('select part_id from part_evidence where record_id=?',(rid,))];rows.append(r)
 ids=sorted({p for r in rows for p in r['part_ids']})
 identities=[dict(db.execute('select * from parts where part_id=?',(pid,)).fetchone()) for pid in ids]
 variants=[dict(r) for pid in ids for r in db.execute('select * from part_variants where part_id=?',(pid,))]
assets=[f'references/1928-03-30_SNL_G13/SNL_G13_Project/sources/p{n:03}.jpg' for n in [33,73,94,165,219]]
assets+=['references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p293-geometry.png',
 'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate71.png',
 'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/data/batch06_body_transcription.txt']
r=dict(status='Front coupling and external spring reconstruction; main clutch remains pending',survey_sha256=sha(SURVEY),
 records=rows,identities=identities,variants=variants,source_assets={p:sha(REPO/p) for p in assets},
 physical_inventory=dict(front_coupling=1,spring_flange_halves=2,external_spring=1,bolt_nut_washer_sets=6,total=10),
 decisions=[
 'SH945A selected from SNL73:016 differs from handbook SH864B. HB116 flange9in and body5in dimensions are provisional applicability transfers, not proven manufacturing controls for SH945A.',
 'SH849A/B identifiers agree across HB/SNL. HB116 spring5-3/8in spiral diameter and4-1/4in coil length with5free+2seating coils are retained. Inside/mean/outside diameter and free/installed length conventions are not stated.',
 'Select5-3/8in as the inside coil diameter, with inferred1/2in wire and107.95mm installed envelope. The alternative mean-diameter reading with this wire would intersect the5in coupling. The selected reading also follows the broad source proportions; it is not established metrology.',
 'SNL33:004 prints quantity(2) and allocation one for flangeSH849A. SNL94:013 has2physical half flanges. Interpret this as2bolt/plainnut/lockwasher sets, one allocated per half, securing a two-piece collar. Earlier one-set preparation was incomplete.',
 'Bolt axes are inferred off-axis on opposite sides of the shaft; the section shows one projected head/nut column, not a dimensioned transverse pattern. Do not drill the shaft through its centre to satisfy that projection.',
 'SH849C retainer is SNL Plate21 callout8 at the main-clutch spring-plunger end, not the external spring23. Keep it for main-clutch reconstruction rather than inventing a separate external spring seat.',
 'SH945A has6future collar-interface holes from HB118 count, with estimated circle and size. Fasteners and mating SH999A collar remain unbuilt here; no floating bolts are counted.',
 'Split-collar nominal shaft contact represents a friction clamp. No axial-lock, clamp-load, thread-strength or spring-rate qualification is claimed.',
 'Add inferred8mm fillets to cardan shaft shoulders, following visible source blends; relieve the M855 front passage locally to preserve clearance. Prior native checkpoint remains unchanged.'
 ])
OUT.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n');print('Preserved',len(rows),'rows;',len(ids),'identities;10new physical pieces.')
