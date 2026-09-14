#!/usr/bin/env python3
"""Check coverage, identity, source scope and structural risks of this survey."""
from pathlib import Path
import collections, hashlib, json, sqlite3
HERE=Path(__file__).resolve().parents[1]
db=HERE/'mark_viii_parts.sqlite'
c=sqlite3.connect('file:'+str(db)+'?mode=ro&immutable=1',uri=True)
checks=[]
def check(name,ok,detail):
 checks.append({'check':name,'passed':bool(ok),'detail':detail})
def scalar(sql,args=()):return c.execute(sql,args).fetchone()[0]
check('sqlite_integrity',scalar('PRAGMA integrity_check')=='ok','Closed file reopened read-only')
fk=c.execute('PRAGMA foreign_key_check').fetchall();check('foreign_keys',not fk,fk)
snl=json.loads((HERE/'inputs/snl_rows.json').read_text());hb=json.loads((HERE/'inputs/hb_rows.json').read_text())
check('all_SNL_rows_preserved',scalar("SELECT count(*) FROM source_records WHERE source_id='SNL'")==len(snl)==7571,'7,571 catalogue, component, composition and continuation rows')
check('all_HB_rows_preserved',scalar("SELECT count(*) FROM source_records WHERE source_id='HB' AND record_type IN ('legend','nomenclature')")==len(hb)==2435,'2,082 nomenclature rows and 353 legend rows, including blank-reference rows')
check('all_pdf_pages_indexed',scalar('SELECT count(*) FROM source_pages')==771,'10 PDFs; source identifiers and 1-based PDF page numbers')
check('source_json_lossless',all(json.loads(c.execute('SELECT raw_json FROM source_records WHERE record_id=?',(f"SNL:{r['page']}:{r['row']:03d}",)).fetchone()[0])==r for r in snl),'Every SNL raw row compares equal to the frozen input')
check('every_SNL_physical_row_linked',scalar("SELECT count(*) FROM source_records r WHERE source_id='SNL' AND record_type IN ('component','catalogue_entry') AND NOT EXISTS (SELECT 1 FROM part_evidence e WHERE e.record_id=r.record_id)")==0,'Every parsed catalogue/component row has canonical-part evidence')
check('every_part_has_evidence',scalar('SELECT count(*) FROM parts p WHERE NOT EXISTS (SELECT 1 FROM part_evidence e WHERE e.part_id=p.part_id)')==0,'No unsupported canonical records')
check('composed_of_rows_have_parents',scalar("SELECT count(*) FROM assembly_edges WHERE relation='composed_of'")==3540,'Every leading-quantity component is attached to an explicit composition context')
check('no_self_containment',scalar('SELECT count(*) FROM assembly_edges WHERE parent_part_id=child_part_id')==0,'No assembly is its own child')
g=collections.defaultdict(set)
for a,b in c.execute('SELECT parent_part_id,child_part_id FROM assembly_edges'):g[a].add(b)
seen=set();stack=set();cycles=[]
def visit(a):
 if a in stack:cycles.append(a);return
 if a in seen:return
 stack.add(a)
 for b in g[a]:visit(b)
 stack.remove(a);seen.add(a)
for a in list(g):visit(a)
check('no_containment_cycles',not cycles,cycles)
check('radiator_tube_quantity',scalar("SELECT quantity_per_parent FROM assembly_edges WHERE record_id='SNL:73:013'")==303,'Three hundred and three tubes per named core; not three')
check('quantities_not_flattened',scalar('SELECT count(DISTINCT scope) FROM quantities')>=7,'Catalogue, parent, parenthetical, handbook and spare counts remain distinct')
check('drawing_reference_not_identity',scalar("SELECT count(DISTINCT part_id) FROM part_identifiers WHERE namespace='Ordnance_drawing' AND identifier='679A'")==4,'679A occurs on distinct pinion and ring parts and has not merged them')
check('numeric_blank_legends_not_parts',scalar("SELECT count(*) FROM part_identifiers WHERE namespace='handbook_mark' AND identifier='21153'")==0,'Blank numeric legend lines remain source records in the review queue')
check('HB_140b_locator',scalar("SELECT count(*) FROM source_records WHERE record_id LIKE 'HB:legend:140b:%' AND printed_page<>'140'")==0,'Second legend on page 140 has unique row IDs and a correct printed-page locator')
check('inch_conversion',abs(scalar("SELECT value_mm FROM dimensions WHERE feature='overall_length'")-10426.7)<1e-8,'410.5 inches × 25.4 = 10,426.7 mm')
check('scope_of_roller_counts',scalar("SELECT value_numeric FROM dimensions WHERE feature='lower_rollers_total'")==scalar("SELECT value_numeric FROM dimensions WHERE feature='lower_rollers_with_springs'")+scalar("SELECT value_numeric FROM dimensions WHERE feature='lower_rollers_without_springs'"),'58 lower rollers = 28 spring-equipped + 30 plain')
check('track_shoe_count',scalar("SELECT value_numeric FROM dimensions WHERE feature='total_track_shoes'")==156,'Production account gives two tracks × 78 shoes; derived, excludes spares')
check('disputed_wheel_not_numeric',scalar("SELECT count(*) FROM dimensions WHERE feature='mislabelled_driving_wheel_diameter' AND value_numeric IS NULL AND status='disputed_direct_dimension'")==1,'HB p. 136 erroneous label is not promoted to an approved wheel diameter')
check('Belleville_conflict_blocked',scalar("SELECT count(*) FROM parts p JOIN part_identifiers i USING(part_id) WHERE identifier='SH642B' AND readiness='D_INSUFFICIENT'")>0,'Impossible inside/outside-diameter claim remains blocked')
check('spheres_only_fully_specified',scalar("SELECT count(*) FROM parts WHERE readiness='A_SIMPLE_GEOMETRY'")==2,'Only nominal 1/4-inch and 1-inch steel spheres qualify; no complex assembly certified')
check('figure_index_coverage',dict(c.execute('SELECT source_id,count(*) FROM figures GROUP BY source_id'))=={'SNL':34,'HB':143,'LIB':102,'GUN':13,'PATENT':3},'295 index entries, not 295 unique independent geometric constraints')
check('FTS_population',scalar('SELECT count(*) FROM records_fts')==scalar('SELECT count(*) FROM source_records') and scalar('SELECT count(*) FROM pages_fts')==771,'Both normalized records and PDF pages searchable')
check('record_locations_nonempty',scalar("SELECT count(*) FROM source_records WHERE source_path='' OR printed_page=''")==0,'Every source record has a source path and printed-page locator')
check('research_verification_states',scalar('SELECT count(*) FROM research_leads WHERE verification IS NULL OR limitations IS NULL')==0,'Accessible texts, catalog records, archival leads and unsuccessful matches differentiated')
check('configuration_not_flattened',scalar('SELECT count(*) FROM variants')==8,'Preliminary, production, replacement, future, aircraft, patent, shipping and spare contexts')
warnings=[{'reason':k,'count':n} for k,n in c.execute('SELECT reason,count(*) FROM review_queue GROUP BY reason')]
out={'database_sha256':hashlib.sha256(db.read_bytes()).hexdigest(),'checks':checks,'all_passed':all(x['passed'] for x in checks),'review_queue':warnings,'interpretation':'Data and parser checks, not a manufacturing validation or certification of complete geometric coverage.'}
(HERE/'reports/validation.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'all_passed':out['all_passed'],'checks':len(checks),'failures':[x for x in checks if not x['passed']],'review_queue':warnings},indent=2))
raise SystemExit(0 if out['all_passed'] else 1)
