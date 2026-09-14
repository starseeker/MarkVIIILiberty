# Preliminary Handbook of the Mark VIII Tank — checkpoint 11

The cumulative native Scribus master contains the title leaf (inferred page 1)
and printed pages 2–220. This iteration adds pages 201–220: engine, epicyclic gear,
exhaust, fan, petrol-system and hull parts lists, with technical illustrations.

## Open and review

- `Handbook_Master.sla` — current 220-page native document.
- `Handbook_Master_001-220_v11.pdf` — cumulative PDF from the reopened master.
- `Handbook_Comparison_201-220_v11.pdf` — twenty source/reconstruction pairs.
- `CONTINUE_HERE.md` and `PROJECT_STATUS.json` — continuation instructions/state.
- `REVIEW_NOTES.md` — retained source readings and editorial questions.

Install the three bundled C059 OpenType fonts before opening in Scribus 1.6.x.
Disable conflicting Type 1 copies, whose metrics alter layout. Keep `assets/`
beside the SLA; all 133 image links are relative and included. C059 remains a
provisional Century approximation. Original typeface and physical trim remain
unconfirmed; the working canvas is 396 × 612 pt (5.5 × 8.5 in).

## Editable content and source treatment

The master has 11,971 native text frames, including 2,191 added in this batch.
The new content comprises 657 nomenclature rows, native column headings, part
number leaders, shared description blocks, braces, captions and folios. Table
cells use native text and rules. Common fractions use font glyphs; other table
fractions use separate editable numerators, denominators and rule objects.
Blank part-number and quantity cells remain blank; x quantities are retained.

This batch adds eleven numbered plates (119–125 and 127–130), plus the two
unnumbered charts on page 212. No Plate 126 label is invented. Earlier artwork
includes the title seal, Plates 1–118 and a second crop for Plate 62. Internal
lettering, leaders, engineering detail and chart curves remain raster. Paper
normalization reduces discoloration; texture and binding distortion can remain.
Three isolated marks in confirmed blank paper were masked and recorded. No
nonlinear warp, sharpening, redrawing or generated artwork is applied.

Source baseline estimates and OCR indices remain in the transcription JSON.
Text baselines are straightened independently of illustration geometry. Draft
OCR used wider left-page crops; new comparisons use nominal source halves. The
earlier page 132 crop override is retained. Apparent errors, repeated numbers,
blank cells and inconsistent dimensions remain as printed; see REVIEW_NOTES.md.
Independent proofreading remains pending.

## Verification

The master was reopened in Scribus 1.6.1. All 11,971 native text frames pass text,
single-line and overflow checks. All twenty new pages were rendered with Poppler
and visually reviewed, with enlarged checks of fractions, shared descriptions,
rotated captions and plate edges. Expected native text is present in PDF
extraction, fonts are embedded, and all 133 asset hashes match.

All 11,259 earlier page objects retain content, geometry and style assignments.
PDF pages 1–200 are pixel-identical to v10 at 144 dpi. Scribus regenerates ItemIDs,
rounds 34 earlier character-style scales and drops 491 unused line SHADE
attributes. These serialization changes do not affect the earlier renders.
See `data/*validation.json` and `data/visual_review.md`.

## Rebuild this batch

Authoritative table input: `data/tables_batch11.json` (including shared blocks).
Readable transcript: `data/batch11_table_transcription.tsv`, supplemented by
`data/batch11_shared_descriptions.txt`. Layout: `layout_batch11.py`.
All artwork is bundled, so source scans are unnecessary for rebuilding the SLA.

1. Preserve manual edits. `build_project.py` starts from the exact
   `Handbook_Checkpoint_001-200_v10.sla` and cannot discover later manual changes.
2. Run `build_project.py` inside Scribus to append pages 201–220 and save the master.
3. Run `check_project.py` inside Scribus to reopen, validate and export the v11 PDF.
4. Run `python verify_preservation.py` and `python verify_pdf.py` outside Scribus.
   Supply `--previous-pdf PATH` to the latter to compare the first 200 pages.
5. Run `python render_batch11.py` and inspect every new-page PNG.
6. Run `python make_comparison.py --source-dir /path/to/scans`, then
   `python verify_comparison.py`, to reproduce/check the comparison proof.

`prepare_batch11_transcription.py` reproduces JSON and readable transcripts from
bundled draft OCR, TSV coordinates and explicit source corrections. It invokes
`batch11_special_tables.py` for the shared-description layouts. Running it replaces
manual edits to these inputs. `prepare_batch11_assets.py --source-dir PATH`
reproduces the 13 new crops. `fetch_sources.py` retrieves 111 hash-pinned spreads
sequentially and resumably. Original scans are recoverable from recorded GitHub
paths and hashes and are not duplicated in this ZIP.

Headless Scribus needs explicit `-platform offscreen`, `HANDBOOK_BATCH=1`, an
OpenType-only font configuration and `-py /absolute/path/script.py` last. Inspect
error/status files: caught exceptions can return exit status zero. Keep the PDF
exporter a local function so it finalizes before exit. After workspace cleanup,
check local Scribus data/plugin links before running a private runtime.

Preparation/review tools use Pillow, NumPy, SciPy, PyMuPDF, ReportLab and Poppler.
Comparison PDFs embed bundled DejaVu Sans fonts. Historical builders and earlier
SLAs are baselines; continue from the current master to preserve edits.

## Release names and continuation

Current PDF: `Handbook_Master_001-220_v11.pdf`.
Next planned PDF: `Handbook_Master_001-240_v12.pdf`.
Every released PDF needs a unique page-range/version filename. A revised proof
of this release requires a fresh suffix such as `v11r1`, with scripts and state
updated together. Never release a generic `Handbook_Master.pdf`. The native
working file may retain `Handbook_Master.sla`.

Next batch: printed pages 221–240, scan 111 right through scan 121 left. Retain
the cumulative ZIP and provide the latest copy if the workspace is unavailable
later. The user manually commits downloads to GitHub; no repository changes
have been pushed.
