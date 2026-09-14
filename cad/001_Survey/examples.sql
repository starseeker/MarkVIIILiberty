-- Open with: sqlite3 mark_viii_parts.sqlite < examples.sql
-- These are inspection queries, not an approved whole-vehicle BOM calculation.

-- 1. Look up a piece mark, then inspect all its source evidence.
SELECT DISTINCT p.part_id, p.canonical_name, i.namespace, i.role, p.readiness
FROM parts p JOIN part_identifiers i USING(part_id)
WHERE i.identifier = 'M1264';

SELECT e.* FROM v_source_evidence e
WHERE e.part_id IN (SELECT part_id FROM part_identifiers WHERE identifier='M1264')
ORDER BY e.source_id,e.printed_page,e.row_no;

-- 2. Explicit composition and quantity-per-parent evidence.
SELECT parent,child,quantity_per_parent,quantity_raw,source_id,printed_page,record_id
FROM v_bom_edges WHERE parent LIKE '%CORE%radiator%';

-- 3. All distinct quantity meanings for the same part.
SELECT p.canonical_name,q.quantity_raw,q.quantity_value,q.scope,q.record_id
FROM quantities q JOIN parts p USING(part_id)
WHERE q.part_id IN (SELECT part_id FROM part_identifiers WHERE identifier='SH607C');

-- 4. Reviewed dimensions and their precise source scope.
SELECT feature,raw_value,value_numeric,unit,value_mm,status,source_id,printed_page
FROM v_reviewed_dimensions ORDER BY source_id,printed_page,feature;

-- 5. Textual sizing statements that have not been decomposed into scalars.
SELECT p.canonical_name,d.raw_value,d.status,r.source_id,r.printed_page
FROM dimensions d LEFT JOIN parts p USING(part_id)
JOIN source_records r USING(record_id)
WHERE d.raw_value LIKE '%Timken%' OR p.canonical_name LIKE '%BEARING%';

-- 6. Linked conflicts, plus the separate global issue list.
SELECT i.* FROM issues i JOIN issue_parts ip USING(issue_id)
WHERE ip.part_id IN (SELECT part_id FROM part_identifiers WHERE identifier='SH642B');
SELECT issue_id,title,locator,status,resolution FROM issues WHERE category<>'inherited_source_erratum';

-- 7. Configuration qualifications are evidence, not a complete fit filter.
SELECT v.variant_id,v.description,p.canonical_name,pv.status,pv.basis,pv.record_id
FROM part_variants pv JOIN parts p USING(part_id) JOIN variants v USING(variant_id)
WHERE v.variant_id IN ('ROCK_ISLAND_FIRST_100','SERVICE_REPLACEMENT');

-- 8. Parts needing geometric evidence.
SELECT * FROM v_geometry_queue
WHERE readiness='D_INSUFFICIENT' AND subsystem='Fuel and pressure';

-- 9. Supplier research and its actual verification level.
SELECT lead_id,title,url,verification,benefit,limitations
FROM research_leads ORDER BY priority,lead_id;

-- 10. Full-text search returns references to original text, not inferred facts.
SELECT r.record_id,r.source_id,r.printed_page,r.description
FROM records_fts f JOIN source_records r ON r.record_id=f.record_id
WHERE records_fts MATCH '"Bijur"' LIMIT 30;

SELECT p.page_id,p.printed_page,p.path
FROM pages_fts f JOIN source_pages p ON p.page_id=f.page_id
WHERE pages_fts MATCH '"transport"' LIMIT 20;

-- 11. Ambiguous matches and unlabelled source records are explicit work items.
SELECT q.*,p.canonical_name FROM review_queue q LEFT JOIN parts p USING(part_id);

-- 12. Different physical objects sharing an Ordnance drawing reference.
SELECT DISTINCT p.part_id,p.canonical_name,i.namespace,i.role
FROM part_identifiers i JOIN parts p USING(part_id)
WHERE i.identifier='679A';
