CREATE TABLE assembly_edges(edge_id INTEGER PRIMARY KEY,parent_part_id TEXT REFERENCES parts,child_part_id TEXT REFERENCES parts,record_id TEXT REFERENCES source_records,quantity_raw TEXT,quantity_per_parent REAL,relation TEXT,confidence TEXT,UNIQUE(parent_part_id,child_part_id,record_id,relation));

CREATE TABLE coverage(source_id TEXT REFERENCES sources,category TEXT,count INTEGER,method TEXT,limitation TEXT,PRIMARY KEY(source_id,category));

CREATE TABLE dimensions(dimension_id INTEGER PRIMARY KEY,part_id TEXT REFERENCES parts,record_id TEXT REFERENCES source_records,feature TEXT,raw_value TEXT,value_numeric REAL,unit TEXT,value_mm REAL,status TEXT,interpretation TEXT);

CREATE TABLE figures(figure_id INTEGER PRIMARY KEY,source_id TEXT REFERENCES sources,printed_page TEXT,figure TEXT,caption TEXT,kind TEXT,source_path TEXT);

CREATE TABLE issue_parts(issue_id TEXT REFERENCES issues,part_id TEXT REFERENCES parts,link_basis TEXT,PRIMARY KEY(issue_id,part_id));

CREATE TABLE issues(issue_id TEXT PRIMARY KEY,category TEXT,severity TEXT,title TEXT,source_id TEXT REFERENCES sources,locator TEXT,details TEXT,resolution TEXT,status TEXT);

CREATE TABLE lead_parts(lead_id TEXT REFERENCES research_leads,part_id TEXT REFERENCES parts,match_basis TEXT,PRIMARY KEY(lead_id,part_id));

CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL);

CREATE TABLE notes(note_id TEXT PRIMARY KEY,source_id TEXT REFERENCES sources,printed_page TEXT,symbol TEXT,text TEXT);

CREATE VIRTUAL TABLE pages_fts USING fts5(page_id UNINDEXED,text);

CREATE TABLE part_evidence(part_id TEXT REFERENCES parts,record_id TEXT REFERENCES source_records,relationship TEXT,confidence TEXT,PRIMARY KEY(part_id,record_id,relationship));

CREATE TABLE part_figures(part_id TEXT REFERENCES parts,source_id TEXT REFERENCES sources,printed_page TEXT,figure TEXT,callout TEXT,record_id TEXT REFERENCES source_records);

CREATE TABLE part_identifiers(part_id TEXT REFERENCES parts,namespace TEXT,identifier TEXT,raw_identifier TEXT,role TEXT,record_id TEXT REFERENCES source_records,PRIMARY KEY(part_id,namespace,identifier,role,record_id));

CREATE TABLE part_notes(part_id TEXT REFERENCES parts,note_id TEXT REFERENCES notes,record_id TEXT REFERENCES source_records,PRIMARY KEY(part_id,note_id,record_id));

CREATE TABLE part_relations(part_id TEXT REFERENCES parts,related_part_id TEXT REFERENCES parts,relation TEXT,basis TEXT,record_id TEXT REFERENCES source_records,PRIMARY KEY(part_id,related_part_id,relation,record_id));

CREATE TABLE part_variants(part_id TEXT REFERENCES parts,variant_id TEXT REFERENCES variants,status TEXT,record_id TEXT REFERENCES source_records,basis TEXT,PRIMARY KEY(part_id,variant_id,record_id,status));

CREATE TABLE parts(part_id TEXT PRIMARY KEY,canonical_name TEXT NOT NULL,kind TEXT NOT NULL,identity_basis TEXT,subsystem TEXT,readiness TEXT,readiness_basis TEXT,missing_geometry TEXT);

CREATE TABLE quantities(quantity_id INTEGER PRIMARY KEY,part_id TEXT REFERENCES parts,record_id TEXT REFERENCES source_records,quantity_raw TEXT,quantity_value REAL,scope TEXT,interpretation TEXT);

CREATE VIRTUAL TABLE records_fts USING fts5(record_id UNINDEXED,description);

CREATE TABLE research_leads(lead_id TEXT PRIMARY KEY,title TEXT,vendor TEXT,url TEXT,date_or_period TEXT,verification TEXT,priority INTEGER,benefit TEXT,limitations TEXT,checked_date TEXT);

CREATE TABLE review_queue(review_id INTEGER PRIMARY KEY,record_id TEXT REFERENCES source_records,part_id TEXT REFERENCES parts,reason TEXT,detail TEXT);

CREATE TABLE source_files(path TEXT PRIMARY KEY,sha256 TEXT NOT NULL,bytes INTEGER NOT NULL);

CREATE TABLE source_pages(page_id TEXT PRIMARY KEY,source_id TEXT REFERENCES sources, path TEXT REFERENCES source_files,pdf_page INTEGER,printed_page TEXT,text TEXT);

CREATE TABLE source_records(record_id TEXT PRIMARY KEY,source_id TEXT REFERENCES sources,printed_page TEXT,row_no INTEGER,record_type TEXT,source_path TEXT,description TEXT,raw_json TEXT NOT NULL);

CREATE TABLE sources(source_id TEXT PRIMARY KEY,title TEXT,configuration TEXT,primary_role TEXT);

CREATE TABLE variants(variant_id TEXT PRIMARY KEY,description TEXT);

CREATE INDEX identifier_lookup ON part_identifiers(namespace,identifier);

CREATE VIEW v_bom_edges AS SELECT e.edge_id,e.parent_part_id,p.canonical_name AS parent,e.child_part_id,ch.canonical_name AS child,e.quantity_per_parent,e.quantity_raw,e.relation,e.confidence,r.source_id,r.printed_page,e.record_id FROM assembly_edges e JOIN parts p ON p.part_id=e.parent_part_id JOIN parts ch ON ch.part_id=e.child_part_id JOIN source_records r ON r.record_id=e.record_id;

CREATE VIEW v_cross_source_parts AS SELECT p.part_id,p.canonical_name,count(DISTINCT r.source_id) AS source_count,group_concat(DISTINCT r.source_id) AS sources FROM parts p JOIN part_evidence e USING(part_id) JOIN source_records r USING(record_id) GROUP BY p.part_id HAVING count(DISTINCT r.source_id)>1;

CREATE VIEW v_geometry_queue AS SELECT part_id,canonical_name,subsystem,readiness,readiness_basis,missing_geometry FROM parts ORDER BY readiness,subsystem,canonical_name;

CREATE VIEW v_parts AS SELECT p.*, (SELECT group_concat(DISTINCT namespace||':'||identifier) FROM part_identifiers i WHERE i.part_id=p.part_id AND role IN ('part_mark','manufacturer_cross_reference')) AS identifiers,(SELECT count(*) FROM part_evidence e WHERE e.part_id=p.part_id) AS evidence_count FROM parts p;

CREATE VIEW v_reviewed_dimensions AS SELECT d.*,r.source_id,r.printed_page FROM dimensions d JOIN source_records r USING(record_id) WHERE d.status IN ('direct_dimension','derived_dimension','disputed_direct_dimension');

CREATE VIEW v_source_evidence AS SELECT e.part_id,p.canonical_name,r.record_id,r.source_id,r.printed_page,r.row_no,r.record_type,r.source_path,r.description,e.relationship,e.confidence FROM part_evidence e JOIN parts p USING(part_id) JOIN source_records r USING(record_id);
