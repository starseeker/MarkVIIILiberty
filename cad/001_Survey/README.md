# Mark VIII source survey

Read `survey_report.md` first. Open `mark_viii_parts.sqlite` with SQLite or a SQLite browser. All deliverables belong under `cad/001_Survey/` in the repository; the ZIP preserves that layout.

This is a source-linked inventory and geometry-readiness survey, not a released engineering BOM. It preserves configuration alternatives, source contradictions and unresolved identities. Do not sum the `quantities` table or all assembly paths to derive a whole-tank part count.

## Contents

- `mark_viii_parts.sqlite`: canonical survey records, source evidence, assembly assertions, dimensional statements, issues, notes, variants, figures, research leads and full-text search.
- `survey_report.md`: findings from both survey passes, readiness, high-value conflicts, primary-source candidates and proposed next work.
- `schema.sql`, `examples.sql`: schema and useful inspection queries.
- `inputs/`: frozen current-source records, full available transcription data, page text, source manifest and reviewed supplement.
- `scripts/`: extract, rebuild, supplement authoring, validation and report generation.
- `reports/`: statistics, validation, and the bounded prior-session recovery assessment.
- `source_transcription_snapshot/`: 597 project text/data/script files from the surveyed git revision, with a manifest. This includes reconstruction/transcription and review sources beyond the subset consumed directly by the database.
- `package_manifest.json`: SHA-256 and size for every other packaged file.

## Rebuild

Use Python 3.11+ with SQLite FTS5. These commands need only the frozen package:

```sh
python scripts/build_database.py
python scripts/validate_database.py
python scripts/write_report.py
```

Scripts locate their inputs relative to themselves, so full paths also work. To change the reviewed supplement, edit `scripts/author_supplement.py` and run it before the rebuild. To refresh from source documents, run `scripts/extract_sources.py` in a checkout containing the source PDFs and project data; it requires PyMuPDF. A source refresh should be treated as a new survey revision.

Rebuilding replaces only generated survey outputs. The report generator is a reviewed narrative plus live counts; substantial data changes also require editorial review of that narrative. `schema.sql` describes the current database; normally use the Python builder to create and populate it together.

Original PDF/image assets are available at the pinned repository revision in `inputs/source_manifest.json`; the package preserves their paths and hashes but does not duplicate their bytes. The text snapshot retains the original `references/...` layout inside its own folder. It is an archival copy, not a second live checkout.

## Important fields

`source_pages.pdf_page` is 1-based. `printed_page` is a string because plates, front matter and patent specification sheets do not have one uniform numeric sequence. `part_figures.printed_page` is the location of the reference; use `figures` to find the figure's own indexed location. Figure references may contain a group/range rather than one normalized number. Original figure-index errors are not silently corrected.

`parts.part_id` is a stable survey key derived from an identity rule; it is not an original engineering part number. `part_identifiers.namespace` and `role` tell piece marks, manufacturer cross-references, drawings and callouts apart. `identity_basis` records where consolidation is provisional. Names can preserve an erroneous source dimension: always inspect `issues` and `dimensions.status` before taking a value into CAD.

`dimensions.raw_value` often contains several measurements in one source sentence. `value_numeric`, `unit`, and `value_mm` are populated only for reviewed scalars. A blank numeric field does not mean the source lacks sizing information. `status` distinguishes direct, derived, uninterpreted and conflicting values.

Readiness categories are initial triage. Only A represents a fully specified nominal primitive; B and C still require dimensional and placement work. D includes unresolved identity-only records and blocked dimensions. Neither figure presence nor a bare catalogue dimension proves a complete solid can be constructed.

Configuration membership is partial evidence, not a finished applicability filter for every part. Absence of a `part_variants` row means unclassified, not universal applicability. Source-level conflicts must be read even if no `issue_parts` link exists. Consult the report before choosing a production baseline.

## Checks

`reports/validation.json` records 27 passing coverage, identity, quantity, dimensional and structural checks, plus 37 unresolved review records. No self-containing assemblies or containment cycles were found. These checks verify the survey data structure and selected high-risk interpretations; they do not certify historical or manufacturing completeness.
