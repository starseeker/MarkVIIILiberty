"""Retain catalogue identities and the coupling topology correction evidence."""
from pathlib import Path
import hashlib,json,sqlite3
REPO=Path(__file__).resolve().parents[4];OUT=Path(__file__).with_suffix('.json');SURVEY=REPO/'cad/001_Survey/mark_viii_parts.sqlite'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
selected=['SNL:67:019','SNL:43:014','SNL:164:030','SNL:200:002','SNL:276:003','SNL:73:016',
 'HB:legend:116:013','HB:legend:116:021','HB:legend:116:022','HB:legend:116:008','HB:legend:116:010']
with sqlite3.connect(f'file:{SURVEY}?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row;rows=[]
 for rid in selected:
  r=dict(db.execute('select * from source_records where record_id=?',(rid,)).fetchone())
  r['raw']=json.loads(r.pop('raw_json'));r['part_ids']=[x[0] for x in db.execute('select part_id from part_evidence where record_id=?',(rid,))];rows.append(r)
 ids=sorted({p for r in rows for p in r['part_ids']})
 identities=[dict(db.execute('select * from parts where part_id=?',(pid,)).fetchone()) for pid in ids]
 variants=[dict(r) for pid in ids for r in db.execute('select * from part_variants where part_id=?',(pid,))]
assets=[f'references/1928-03-30_SNL_G13/SNL_G13_Project/sources/p{n:03}.jpg' for n in [43,67,73,164,200,276,293]]
assets+=['references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p293-geometry.png',
 'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate71.png',
 'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/original_scans/MarkVIII059.jpg']
r=dict(status='Catalogue sliding collar joint and end-bearing pocket; main internal stack pending',survey_sha256=sha(SURVEY),
 records=rows,identities=identities,variants=variants,source_assets={p:sha(REPO/p) for p in assets},
 inventory=dict(sliding_collar=1,end_bearing_ring=1,end_bearing_bush=1,cap_screws=6,locking_wire=1,total_new=10),
 decisions=[
  'The previous SH945A reconstruction followed the single prominent HB flange. The closer SNL Plate21 section shows distinct spring and collar-joint flanges plus a bearing pocket forward of the cardan head. Correct this topology instead of extending the mistaken single-flange interface.',
  'Retain catalogue SH945A, SH999A, SH997A and SH997B identities. HB SH864B, SH862A/B and SH863A/B are distinct records; no silent equivalence or universally applicable dimensions is established.',
  'The external spring and split clamp move67mm aft together. The spring flange then lies aft of the enlarged cardan head as in SNL21. Axial calibration and dimensions remain inferred; old native and progression images remain preserved.',
  'SNL200:002 original p200 confirms six3/8 x5/8in drilled hex-head cap screws for SH999A. The bolt heads bear on the collar lip and their shanks enter blind holes in the new forward coupling flange. These are not the six drum-to-flywheel screws.',
  'SNL276:003 original p276 confirms SH999C, soft steel W.&M.gauge16,26in, for SH999A screws. Represent one continuous wire through six drilled heads with an inferred paired end twist;1.5mm wire diameter is not a verified gauge conversion.',
  'SH997B bush and SH997A ring are separate catalogue components. Their inferred annular stock, pocket fit and axial capture do not prove the eventual crankshaft/nut interface.',
  'The collar remains partial until the main sleeve, bearing, keys, cone-support collar and thrust/ball stack are reconstructed. Do not count vacant interface regions as physical components.',
  'All nonprinted dimensions are reconstruction estimates. Threads are smooth envelopes and wire routing has no locking-strength qualification. The prior SNL33 spring-clamp bolt-callout mismatch remains open.'
 ])
OUT.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n');print('Retained',len(rows),'source rows;10new physical pieces.')
