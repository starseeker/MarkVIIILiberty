"""Preserve clutch-stop drive identities, source sizes and unresolved transfers."""
from pathlib import Path
import hashlib,json,sqlite3
REPO=Path(__file__).resolve().parents[4];OUT=Path(__file__).with_suffix('.json')
SURVEY=REPO/'cad/001_Survey/mark_viii_parts.sqlite'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
records=['SNL:18:011','SNL:31:013','SNL:34:012','SNL:74:027','SNL:83:035','SNL:211:031','SNL:112:018',
 'HB:legend:116:011','HB:legend:116:017','HB:legend:116:018','HB:legend:116:019','HB:nomenclature:188:003']
with sqlite3.connect(f'file:{SURVEY}?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row;rows=[]
 for rid in records:
  r=dict(db.execute('select * from source_records where record_id=?',(rid,)).fetchone());r['raw']=json.loads(r.pop('raw_json'))
  r['part_ids']=[x[0] for x in db.execute('select part_id from part_evidence where record_id=?',(rid,))];rows.append(r)
 ids=sorted({p for r in rows for p in r['part_ids']})
 identities=[dict(db.execute('select * from parts where part_id=?',(pid,)).fetchone()) for pid in ids]
 variants=[dict(r) for pid in ids for r in db.execute('select * from part_variants where part_id=?',(pid,))]
assets=[f'references/1928-03-30_SNL_G13/SNL_G13_Project/sources/p{n:03}.jpg' for n in [18,31,34,74,83,211]]
assets += ['references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p293-geometry.png',
 'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate71.png',
 'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/data/batch06_body_transcription.txt']
result=dict(status='Source-linked approximate clutch-stop drive; main clutch remains separate work',survey_sha256=sha(SURVEY),records=rows,identities=identities,variants=variants,source_assets={p:sha(REPO/p) for p in assets},
 physical_inventory=dict(coupling_box=1,half_covers=2,stop_drum=1,cardan_shaft=1,eight_bolt_nut_washer_sets=24,belt=1,total=30),
 decisions=[
 'SNL31:013 explicitly allocates eight half-inchx2-7/8in bolt/plainnut/lockwasher sets to M855. HB118 independently says eight coupling-box bolts to the bevel-pinion shaft. Replace the prior six inferred M246 holes; keep its shaft fit and axial datum.',
 'SNL211:031 shaftSH1000A and HB71 shaftSH864A have distinct survey identities. No explicit supersession relationship is established. Select SNL identity for this reconstruction; transfer HB116 length11-1/4in,body2in and10-spline enlarged4.359in section provisionally, with at least15percent dimensional uncertainty.',
 'M855,M856,M858 share explicit identifiers across HB and SNL. M856 quantity is two physical halves, not two complete covers.',
 'Sections support a shaft head captured inside the coupling box, a separate closure and an enclosing clutch-stop cup/V pulley. The transverse head outline is not visible; a rounded-square positive-drive head and matching clearance pocket are explicit assumptions. Axial endplay and socket shape remain historically unverified.',
 'M855 axial nut-access pockets, stepped outer shell and M858 inner clearance are inferred to make the printed fasteners usable. They are not claimed as exact hidden casting details.',
 'BeltSH900G is specified as linked V,54in,5/8in,28degrees. Model a complete trapezoidal loop with inferred transverse link-junction marks; individual commercial link construction/material/count remains an unquantified inventory gap. Do not count marks as physical links.',
 'For the selected static belt, treat54in as pitch-line length and place the pitch line5mm below the outside. This convention is an explicit estimate. Actual link elasticity, adjustment and manufacturing geometry remain unverified.',
 'Main compound clutch,front coupling/spring and brake band remain pending; this drive module is not a complete clutch or tank.'],
 handbook_controls={'source':'HB116-118','cardan_length_mm':285.75,'cardan_body_diameter_mm':50.8,'spline_count':10,'spline_outside_diameter_mm':110.7186,'coupling_box_bolt_count':8},
 source_review='HB71 and SNL21 visibly compared; opposite source section orientations retained. Direct shaft/fastener controls are transfers to the chosen identity, not independent manufacturing metrology.')
OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(len(rows),'source records;',len(ids),'identities;30 new physical occurrences.')
