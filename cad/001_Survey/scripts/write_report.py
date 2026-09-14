#!/usr/bin/env python3
"""Render the reviewed narrative and live database counts as a portable report."""
from pathlib import Path
import json,sqlite3
HERE=Path(__file__).resolve().parents[1]
s=json.loads((HERE/'reports/build_statistics.json').read_text())
v=json.loads((HERE/'reports/validation.json').read_text())
c=sqlite3.connect('file:'+str(HERE/'mark_viii_parts.sqlite')+'?mode=ro&immutable=1',uri=True)
commit=c.execute("SELECT value FROM metadata WHERE key='source_commit'").fetchone()[0]
base='https://github.com/starseeker/MarkVIIILiberty/blob/'+commit+'/'
def table(headers,rows):
 def cell(x):return str(x).replace('|',' / ').replace('\n',' ')
 return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(cell(x) for x in row)+' |' for row in rows])
source_rows=[]
for sid,title,configuration,role in c.execute('SELECT * FROM sources'):
 paths=[r[0] for r in c.execute("SELECT DISTINCT path FROM source_pages WHERE source_id=? ORDER BY path",(sid,))]
 links=', '.join(f'[PDF {i+1}]({base+p})' for i,p in enumerate(paths))
 pages=c.execute('SELECT count(*) FROM source_pages WHERE source_id=?',(sid,)).fetchone()[0]
 source_rows.append((sid,title,pages,links))
report=f'''# Mark VIII tank: source survey and CAD preparation

**Survey date:** 13 September 2026  
**Repository revision:** `{commit}`  
**Requested scope:** [cad/001_Survey/intent.txt]({base}cad/001_Survey/intent.txt), both survey passes and the geometry-readiness assessment.

The source collection supports a useful, traceable component inventory and the beginning of a parameterized vehicle layout. It does **not yet support a fully dimensioned, configuration-consistent detailed model of the complete tank**. The principal obstacles are proprietary commercial assemblies, undocumented interfaces and hole locations, conflicting dimensions, and differences between preliminary design, production, and later service configurations.

The deliverable is `mark_viii_parts.sqlite`, accompanied by its schema, frozen inputs, rebuild scripts, example queries, validation results, this report, and a snapshot of the repository's transcription/reconstruction text sources. It has **{s['parts']:,} conservative canonical records**, **{s['assembly_edges']:,} assembly/arrangement assertions**, and **{s['v_cross_source_parts']:,} records linked across sources**. These are inventory identities and source assertions, not the number of manufactured pieces in one tank. Assemblies, features, equipment sets, alternatives, and unresolved identities are explicitly distinguishable.

## 1. Source inventory and scope

{table(['ID','Source','PDF pages','Pinned repository source'],source_rows)}

The database indexes all **771 PDF pages** from the ten repository PDFs. It imports all **7,571 SNL table rows**, all **2,082 handbook nomenclature rows**, and **353 handbook legend rows**, plus 196 specification statements. A reviewed supplement contributes 345 component/feature/arrangement mentions from all six sources and 59 scalar geometry/count anchors; seven gun spare mentions reuse the corresponding installed-component identity. Two additional nominal sphere diameters are normalized from SNL descriptions.

The SNL rows resolve into 3,285 catalogue entries, 3,540 composed-of component rows, 681 composition markers, 40 continuation headings, and 25 continuation-text rows. Headings do not become manufactured parts. Two empty numeric handbook legend references, `21153`, are preserved for review without inventing a physical object. The blank description at handbook M-2188 is retained as a source deficiency.

**Coverage limit:** the table import is exhaustive against the preserved structured table inputs. The prose supplement is a reviewed component survey, not a proof that every incidental noun, hidden image label, commercial internal piece, or unnamed fastener in every photograph has been enumerated. The SNL itself says that some commercial subassembly parts are omitted, supplier information must be obtained separately, and a spare/accessory addendum is intended for Changes No. 1. Those are known holes in the source collection, not zero-piece assemblies. See SNL notes (b), (gy), and (gam), pp. 308–310.

### Transcription preservation and earlier sessions

Current repository data was preferable to re-extracting dense reconstructed tables from PDF. The survey freezes the table data, Liberty master transcription, gun line data, Jordan and patent reviewed transcription, all six errata files, and searchable PDF page text. It also bundles **597 tracked text/data/script files** from the six reconstruction projects under `source_transcription_snapshot/`, preserving the native transcription and review material at the surveyed commit. Large original PDFs and image assets remain in the repository; their consumed-source hashes and pinned paths are recorded.

A search of earlier session context identified the prior handbook feasibility study and handbook/Liberty master PDFs, but returned no additional recoverable complete transcript ZIP or missing transcript path. Therefore this package does not claim to contain a newly recovered full conversation archive. The earlier evidence also recorded a handbook insert that had not been separately located. That gap remains open. The existing SNL Plate 2 foldout is a separate, valuable longitudinal section. Details and the bounded recovery result are in `reports/source_recovery.md`.

## 2. First pass: requirements and schema

The schema treats **a source assertion, a canonical part identity, an occurrence in an assembly, and a geometric parameter as different things**. This separation is necessary to preserve conflicting values and repeated mentions without silently creating a false bill of materials.

{table(['Tables','Purpose and interpretation'],[
('sources, source_files, source_pages','Document identity and applicability, SHA-256 of consumed files, one-based PDF page and printed-page mapping; full searchable page text.'),
('source_records','Immutable raw JSON and description for each imported row or reviewed statement, including source path and locator.'),
('parts','Stable survey ID, descriptive name, kind, identity basis, subsystem, initial readiness and missing geometry.'),
('part_identifiers','Namespaced piece marks, manufacturer cross-references, drawing references and plate callouts; raw spelling retained.'),
('part_evidence, part_relations','Evidence behind an identity and related components whose interchangeability is not established.'),
('assembly_edges, quantities','Explicit composed-of contents, reviewed arrangements, raw counts and their scopes. No automatic whole-vehicle roll-up.'),
('dimensions','Raw dimensional statement, optional reviewed scalar/unit/mm conversion, status and interpretation. Most rows remain verbatim dimensional descriptions.'),
('figures, part_figures','Source plate/figure inventory and figure/legend references associated with parts.'),
('notes, part_notes','SNL note text and linked qualifications, including substitution and quantity meanings.'),
('variants, part_variants','Preliminary, production, replacement, future, aircraft, patent, shipping and spare applicability.'),
('issues, issue_parts, review_queue','Inherited errata, new deductions/conflicts, affected part links, and unresolved identity/label cases.'),
('research_leads, lead_parts','Primary-source candidates and failed searches, verification level, priority, benefit and related parts.'),
('coverage, records_fts, pages_fts','Audit counts and full-text search. FTS5 is required for a complete rebuild.')])}

`schema.sql` defines the schema. The `v_parts`, `v_source_evidence`, `v_bom_edges`, `v_cross_source_parts`, `v_reviewed_dimensions`, and `v_geometry_queue` views support ordinary inspection. `examples.sql` contains ready-to-run queries.

### Identity and quantity rules

1. Prefer explicit piece marks within a namespace; keep manufacturer numbers, drawing references and figure callouts distinct. For example, SNL's Ordnance column explicitly allows a piece mark **or** a drawing number. Numeric-leading reference `679A` belongs to four distinct ring/pinion objects; it is not a single part identity.
2. Normalize spaces, case, and the hyphen between a letter prefix and its digits for lookup, retaining the original text. Do not strip arbitrary drawing prefixes to manufacture an aircraft-to-tank match.
3. Reconcile exact handbook-to-SNL marks when there is one credible role match. Preserve multiple matches in the review queue. A bare stud and an assembly incorporating that stud may share a mark and still need different records.
4. Unnumbered SNL description fingerprints and assembly descriptions provide provisional consolidation. Unnumbered handbook entries and reviewed aircraft/patent objects remain separate unless evidence establishes identity. Thus some real-world duplicates remain deliberately unresolved.
5. Keep the catalogue quantity column, written quantity per named parent, parenthetical total, handbook number per machine, and carried spare quantity separate. Never add these columns together. Parenthetical totals and the asterisk note often refer to a wider unit than the immediate list.
6. Assembly edges express source composition or arrangement, not transformation matrices, verified fits or an approved vehicle BOM. Alternative versions must be selected before any eventual quantity roll-up.

Canonical names are representative source labels, not corrected engineering specifications. Consult dimensions and issues before using a dimension embedded in a name. Source row IDs remain stable within the frozen input. The `140b` handbook table key is retained in its record ID to distinguish a second legend on printed page 140; the printed-page field is normalized to 140.

## 3. Second pass: population and reconciliation

The resulting database contains {s['source_records']:,} source records, {s['part_identifiers']:,} identifier assertions, {s['part_evidence']:,} part-evidence links, {s['quantities']:,} quantity assertions, {s['dimensions']:,} dimension/specification statements, 44 SNL notes, 108 issues/source notes, and 15 research leads. There are 295 figure-index entries: 34 SNL plates, 143 handbook plates, 102 Liberty index entries, 13 gun plates including A–C, and three patent figures. An index entry is not necessarily an independent view or a calibrated geometric constraint.

The inventory includes 4,692 components, 755 assemblies, 29 integral features, four consumables, one equipment set, and one configuration group. Aircraft-only attachments, patent features, and spare equipment do not become extra installed tank pieces. The 37 review entries comprise 23 identifier-collision records, 11 ambiguous cross-source matches, two unlabelled numeric references, and one missing description. These are review records, not necessarily 37 independent physical ambiguities.

### Configuration must be selected explicitly

For an initial model of the **Rock Island production tank**, use the 1919–1920 production account for configuration and the SNL for identified service components, retaining dated replacement exceptions. The preliminary handbook is valuable for arrangement but cannot be treated as an exact American production specification. This is a recommended modeling baseline, not a claim that the documents fully establish one serial-numbered tank's fit.

{table(['Question','Evidence','Disposition'],[
('Fuel tanks','HB pp. 9,29,33: three 80-gallon tanks; Jordan pp. 27,29: three 50-gallon tanks.','Separate preliminary and production assemblies. Capacity is not sufficient to determine external dimensions; gallon convention remains unconverted.'),
('Machine guns/stowage','HB pp. 9,171,175,180,182: Hotchkiss installation, nominally seven guns; Jordan p. 27: five Brownings.','Retain different armament and ammunition-stowage configurations. Require production installation evidence before locating all mounts.'),
('Carburetors','Jordan pp. 29,32 replaces Zenith with Ball & Ball in production. SNL p. 57 and note (gx), p. 309, orders Zenith substitution under O.C.M. 2344 of 1 Sept. 1922.','Chronology reconciles the apparent contradiction. Aircraft Claudel-Hobson H.C.7 remains a reference alternative, not demonstrated tank equipment.'),
('Electrical equipment','Jordan p. 29 counts/voltages conflict with SNL pp. 14,100,123 and handbook wiring.','Use the technical wiring/catalogue for a dated fit; do not infer equipment count or wiring from Jordan alone.'),
('Pistons and aircraft attachments','LIB describes aircraft piston variants; SNL distinguishes LQ466A and SH1020A. HB p. 95 excludes the propeller hub from the Ordnance engine.','Keep original tank, service replacement and aircraft geometry distinct. C.C. synchronizer and propeller hardware remain aircraft reference objects.'),
('Future production','SNL notes (gt) and (gv), p. 309, distinguish gauge and electrical-box fits.','Future-proposed equipment does not prove that tanks were built with it.'),
('Patent sponson','Alden specification and three figures explain hinged/retracted relationships.','Useful kinematic evidence; no assumed exact dimensional or serial-production equivalence.')])}

### High-value conflicts and deductions

{table(['Issue','Finding','Action'],[
('SURVEY_05: lower main bearings','SNL p. 17 gives one long LQ238A and six short LQ240A; p. 58 reverses them in the composed-of list. Upper halves on p. 59 and LIB p. 17 support one long/six short.','High-confidence proposed correction, recorded separately. Original assembly counts remain intact for audit.'),
('SURVEY_06: wheel diameter','HB p. 136 assigns 23.031 to a driving wheel; pp. 130,132 identify that size with the chain sprocket, while the road-track wheel is 39.237 outside and 32.75 inside.','Treat p. 136 as a likely label error. Its disputed value is not populated as an approved road-wheel parameter.'),
('SURVEY_09: lower rollers','HB p. 136 gives 58 total = 28 spring-equipped + 30 plain. SNL note (gp) explains the overlapping 58/28 quantities.','Resolved scope: 58 is inclusive; two upper rollers are separate. Avoid double counting nested assemblies.'),
('SURVEY_13: Belleville spring','SNL SH642B has mutually inconsistent descriptions, including an outside diameter smaller than its inside diameter.','Blocked geometry. Conflicting dimensions remain visible; obtain original drawing/scan before modeling.'),
('Inherited: LQ229A','SNL pp. 237–238 disagree on the thread size; the p. 59 assembly gives corroborating context.','Keep the competing readings; verify the mating feature and source image before parameter adoption.'),
('Inherited: D22920/D29920','Tachometer bushing identifiers disagree.','Preserve both readings and unresolved identity rather than silently merge by a guessed digit.'),
('SURVEY_10: transport position','Gun handbook p. 21 describes drawing the gun back into its transport support; the patent concerns sponson movement.','Model separate gun and sponson states, with clearance study. A single rigid-body rotation of the entire deployed assembly is not established.'),
('SURVEY_16: engine text','HB p. 45 imports aircraft material and has cylinder-material/cam-count anomalies; p. 95 gives an explicit applicability exclusion.','No automatic transfer of all aircraft internals, materials or accessories into the tank model.'),
('Inherited: handbook p. 9','Ground-pressure statement is anomalous; other performance figures and tappet settings disagree across passages.','Retain these claims as source issues. They do not justify inventing a geometric parameter.')])}

The database retains the full companion errata as well as these reviewed cross-source issues. Inherited “open” status means this survey did not silently apply an emendation; consult the retained source text for any original explanation. Linked issue coverage uses explicit identifiers where available; source-level issues must also be checked because not every issue names a mark.

## 4. Geometry readiness

Readiness is an initial triage based on dimensions, documented views and reviewed source descriptions. It is not a manual certification of every part's geometric completeness. Parts labeled B or C can still require substantial work, and some D records may be promoted when the figure index is traced in detail. The subsystem assignment is likewise a useful first categorization; 731 records remain other/unassigned.

{table(['Class','Records','Meaning'],[(k,s['readiness'][k],meaning) for k,meaning in [
('A_SIMPLE_GEOMETRY','Complete nominal external primitive: the 1/4-inch and 1-inch steel balls. Tolerance/finish and placement are separate.'),
('B_DOCUMENTED_FORM','Explicit illustrated or described form, or named integral feature. Full dimensional/placement sufficiency has not been demonstrated.'),
('C_ENGINEERING_APPROXIMATION','Dimensioned hardware or partial dimensional description suitable for a controlled period-engineering approximation after checking standards and interfaces.'),
('D_INSUFFICIENT','Identity/arrangement evidence alone in the normalized inventory, or a blocking dimensional conflict. Requires more evidence.'),
('N_NON_GEOMETRIC','Bulk consumable; may be represented as a volume or annotation if useful.')]])}

### What can be stated confidently now

There are **61 reviewed scalar/count entries**, including one explicitly disputed nonnumeric entry and one derived shoe total. They constrain the model; they do not collectively define complete parts. Original units and source scope are retained. Selected high-value anchors follow.

{table(['Feature','Source value','Source and scope'],[
('Vehicle envelope','34 ft 2½ in long; 12 ft wide; 9 ft with sponsons withdrawn; 10 ft 3 in high','HB p. 9, preliminary envelope; 410.5 in length = 10,426.7 mm.'),
('Track-related layout','26½ in shoe width; 69½ in track-center spacing; 111½ in ground-contact length','HB p. 9. Use the labeled dimensions, not an arbitrary image-scale fit.'),
('Hull/turret/sponson material','Examples: side plate 12 mm, main turret side 16 mm, main turret roof 6 mm, sponson side 12 mm, roof 6 mm, shield 8 mm','HB p. 35; thicknesses are component-specific, not one global armor thickness.'),
('Turret envelope','Main turret 123½ × 40½ × 22½ in, excluding outlook; driver turret 27 × 19 × 13 in','HB p. 35; outline, intersections and mounting holes still need calibrated views.'),
('Engine kinematic anchors','5 in bore, 7 in stroke, 12 in rod centers; piston pin 1.25 in diameter × 4 15/16 in long','HB p. 45 with aircraft-data caveats. Tank-specific piston/cylinder geometry remains unresolved.'),
('Engine bank angle and bearings','45° bank angle; front main bearing 115 mm long, remaining described bearings 49 mm','LIB pp. 5,17. Aircraft reference and corroborating evidence, not blanket tank interchangeability.'),
('Final-drive chain','3 in pitch; 1 9/16 in inside width; 4 9/16 in maximum width; 2 in rollers; 50 pitches; 12/23-tooth chain sprockets','HB p. 130. Roller and plate form, tooth profile, interface fits and centers still need study.'),
('Running gear','39.237 in track-drive wheel outside diameter; 32.75 in inside; 35 teeth; adjusting wheel 40.187 in','HB pp. 130,136. Separate chain sprocket and road-track drive wheel.'),
('Production shoe count','78 per track, two tracks = 156 installed shoes','Jordan p. 30; arithmetic is marked derived, not a new source statement.'),
('Mount reference','Gun handbook gives external reference dimensions and mounting/transport descriptions','GUN pp. 7,17,21. Use for historical arrangement; precise tank-interface coordinates are still missing.')])}

The SNL also preserves many useful standard-part sizes: bearing envelope/bore/width descriptions, screw and stud diameters and lengths, tubing sizes, hose lengths, wire gauges and selected threads. These are searchable in `dimensions.raw_value`. Most have deliberately not been converted into separate numerical CAD parameters because a value may describe a thread, a stock size, or an uncertain reading rather than the needed feature. Exact conversion is limited to reviewed unit-bearing scalars; gallons, gauges, fractional pipe designations and unspecified conventions are not blindly converted.

### What can be approximated with reasonable period-engineering confidence

- **Plate, angle and strap construction:** use stated thicknesses, assembly membership, rivet-use notes and calibrated orthographic outlines. Model the rolled section or bent sheet and the visible fastener pattern once the joint is identified. Bend radius, hidden laps, hole centers and edge distances remain explicit assumptions unless documented.
- **Bolts, nuts, studs, rivets, cotters and washers:** use source diameter, length, thread notation, head style and material; then use a relevant period standard for otherwise missing nominal proportions. Do not replace a British or special Ordnance thread with a modern metric default. Exact threads are usually less urgent than interfaces and visible heads for a historical display model.
- **Bearings:** catalogue envelope dimensions support a credible external ring model. Internal rolling-element geometry, raceway form, fit and maker-specific shields/seals remain unresolved unless a matching vendor drawing is found. A modern bearing number match alone is insufficient.
- **Pipes, conduits, flexible hoses and wiring:** documented end sizes and lengths constrain routes. Use fittings and support points from plates, then mark intermediate bends and sag as assumed. Preserve the distinction between nominal pipe size, actual tube diameter and thread size.
- **Repeated track elements and radiators:** a verified representative element can be instanced using documented counts. SNL p. 73 has **303 tubes per named rear radiator core**. Counts alone do not establish pitch, shape or total assembly dimensions. Radiator fin and tube detail can initially be represented by a bounded core volume or patterned surface.
- **Gaskets, felt and wood packing:** derive provisional contact outlines from the mating parts where the text establishes their presence. Record assumed thickness, compression and contour separately; do not infer undocumented internals from a material name.

These are recommendations for a reconstruction model, not claims that missing drawings have been recovered. Every assumed value should eventually carry its own source/derivation, uncertainty, and affected parts.

### Subsystem assessment and the next evidence needed

{table(['Subsystem','What the collection supports','Remaining evidence needed'],[
('Hull, turret, sponsons','Envelope, thickness families, many marks/joints, orthographic/section views, patent movement relationships.','Scaled plate coordinates, folded-section calibration, hole/hinge datums, hidden laps, production-specific panel changes and gun clearance.'),
('Track and running gear','Shoes, rollers, spring/plain counts, adjusting and drive wheels, shaft and bracket identities.','Track pitch/tooth contact geometry tied to the shoe, wheel sections and center coordinates, pins/bush fits and tensioner travel.'),
('Transmission and clutch','Rich composed-of lists, sectional assembly figures, chain ratios and many bearings.','Gear tooth forms and complete gear data, bearing/shaft axial stacks, housing sections, fits, clutch friction pack and controls datums.'),
('Engine and lubrication','Extensive aircraft descriptions/sections plus tank marks and service substitutions.','Tank-specific castings, piston/cylinder/carburetor variants, governed drive, sump/ancillary interfaces; treat poured-babbitt alignment note (gq) as assembly-dependent.'),
('Cooling and ventilation','Fan drive, radiator core and hose identities, counts and installation figures.','Core envelope/pitches, tanks and headers, proprietary fan/blower casing sections, brackets and duct clearances.'),
('Fuel and pressure','System diagram, fittings, pump identities, different tank capacities.','Production 50-gallon tank shells/mounts, Ball & Ball body and flange, pressure controls and proprietary fitting shapes.'),
('Electrical and instruments','Wiring, catalogue unit names, some detail components and aircraft Delco reference.','Tank-specific Bijur generator/starter/T461 switch, battery cases and mounts, instruments, terminals, housings and cable routes.'),
('Armament and stowage','Gun/mount descriptive component survey, plate set, transport arrangement, ammunition storage identities.','Production Browning and ball-mount fit, exact tank interface and shield coordinates, optics and commercial internals, configuration-specific stowage.'),
('Shared hardware and other equipment','Large catalogue of named sizes and where-used prose.','Period standards and proprietary catalogues, spatial joint definition, unresolved names/marks, cleanup of provisional subsystem assignment.')])}

No complex assembly has been promoted to “fully dimensioned.” The most productive next geometry task is a constrained overall layout and representative running-gear/structural parts, while the source search targets the missing proprietary units and production interfaces.

## 5. Additional primary-source research

The following candidate records were checked during this survey. “Opened” means the stated text, catalogue record, preview or finding aid was accessible; it does not mean an exact tank part drawing was found. No external dimensional value has been imported into CAD parameters solely from a search-result snippet or a modern replacement part.

'''
leadrows=[]
for lid,title,vendor,url,date,verification,priority,benefit,limitations,checked in c.execute('SELECT * FROM research_leads ORDER BY lead_id'):
 title=f'[{title}]({url})' if url else title
 leadrows.append((lid+' / P'+str(priority),title+' — '+date,verification,benefit+' '+limitations))
report+=table(['Lead / priority','Source candidate','What was verified','Use and limitation'],leadrows)
report+='''

**Cleanup/archiving priorities:** the 1921 screw-thread commission report is the strongest immediately accessible period standards candidate. The 1925 revision is useful alongside it because changed fit conventions must be understood before applying later dimensions to an earlier part. Neither is automatically the controlling specification for every imported British or special tank component.

The 1908 Lunkenheimer catalogue and 1942 Timken manual merit targeted page inspection before undertaking a full reconstruction. The first is period-adjacent; the second is later than the tank and needs an exact historical bearing-series match. The Willard/Zenith collection is a physical archival lead with identified folders, not a downloadable set of product drawings. The period Hayward book can supply construction context; it is not a substitute for a Bijur tank-unit catalogue.

For vehicle-specific work, prioritize the SNL's missing supplement/common-hardware lists, the 1922 carburetor decision and original Rock Island/Ordnance sheets. The repository foldout provenance gives the more specific starting point **National Archives identifier 26417262, container 5, item “Mark VIII Tank,” in the Ordnance Notes and Handbooks on Guns and Gun Carriages series**. This is a preserved archive-panel transcription; online access to individual associated drawings was not established here.

Exact digitized historical matches were not located for the Ball & Ball tank carburetor, Bijur tank starting/charging units and T461 switch, specified instruments, hoses/fittings, Stanley No. 808 hinge or Appleton Unilet bodies. Those negative results describe this search, not proof that the documents do not exist. The database records these gaps and their associated component families for the next search.

## 6. Suggested next work

1. **Adopt a dated configuration.** A Rock Island first-100 representation is a useful default. Keep the preliminary layout, 1922/1928 replacement fit and patent embodiment as separate reference branches. Do not begin with a union of all three equipment lists.
2. **Calibrate the controlling views.** Use SNL Plates 1–4 and 10, especially the recovered Plate 2 foldout, with the handbook envelope and sections. Record image dimensions, crop bounds, source, control points, independent X/Y scaling and residual disagreement. Restored PDF page size or a printed scale alone is not a reliable calibration after resizing, photography or perspective distortion.
3. **Establish coordinate and interface datums.** Propose X along the hull, Y transverse, Z vertical; record the chosen origin and ground condition before placing anything. Solve drive/idler/roller axes and the sponson hinge/interface from multiple views. This coordinate convention is a future modeling decision, not a measured result of this survey.
4. **Build a small evidence-backed pilot.** Start with the overall reference envelope, one plate/angle joint, one track shoe/link and one roller assembly. Use them to test how evidence, assumptions, configurations and reusable part geometry attach to stable database IDs.
5. **Promote parameters deliberately.** Convert each used raw dimensional statement into a reviewed feature, unit and status. Record any scan-derived coordinate with uncertainty and source control points. Add transforms and occurrence/configuration selection only when that geometric work exists; they are intentionally not fabricated by this survey.
6. **Resolve high-impact gaps first.** Address contradictory SH642B dimensions, tank-vs-aircraft engine interfaces, production fuel tanks and Ball & Ball, and proprietary electrical units before investing in unseen internal detail. Close the identity review queue as better evidence becomes available.

## 7. Validation, reproduction and limitations

`reports/validation.json` records **27 passing checks**, including SQLite integrity and foreign keys, complete SNL/HB row coverage, lossless raw SNL data, part evidence, parent assignment, absence of self-containment/cycles, the 303-tube parse, separate quantity scopes, drawing-number identity, the second p. 140 legend, unit conversion, roller/shoe counts, blocked dimensional contradictions, figure counts, full-text population and nonempty source locators. Selected reconstructed source pages were visually checked for column meanings, envelope dimensions, chain/wheel specifications, roller counts, and gun transport wording. This is representative source verification, not a new line-by-line proof of all 771 pages.

The database is built in memory and written as a complete closed SQLite image; the published file is then reopened and checked. This avoids dependence on journal behavior in a network-backed workspace. Rebuild from the frozen package with Python 3.11+ and SQLite FTS5:

```sh
python scripts/build_database.py
python scripts/validate_database.py
python scripts/write_report.py
```

Run those commands from `cad/001_Survey/` (or give the scripts' full paths). `author_supplement.py` contains the reviewed supplement as editable source and can regenerate `inputs/curated_survey.json` before rebuilding. `extract_sources.py` refreshes inputs from the original repository and requires PyMuPDF and the repository PDFs/project files. It is unnecessary for a rebuild from the ZIP's frozen inputs. A different repository revision is a new survey input, not a silent refresh of this result.

The package includes `schema.sql`, `examples.sql`, `README.md`, the build statistics and validation JSON, raw/frozen inputs, source-consumption hashes, the text-source snapshot and this report. It does not duplicate the repository's large PDF/image collection or claim to supply the missing handbook insert. No CAD geometry, measured scan control points, manufacturing tolerances or verified whole-vehicle quantity roll-up has been generated in this survey stage.

The database is a reproducible starting inventory with explicit evidence and an actionable gap list. Its unresolved identities, partial dimensional parsing and unreviewed figure calibration are visible work items for the next stage rather than hidden assumptions.
'''
(HERE/'survey_report.md').write_text(report)
print({'report_words':len(report.split()),'database_sha256':v['database_sha256']})
