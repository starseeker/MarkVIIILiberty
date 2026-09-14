# Preliminary Handbook of the Mark VIII Tank — checkpoint 10

The cumulative native Scribus master contains the title leaf (inferred page 1)
and printed pages 2–200, with Plates 1–118. This iteration adds pages 181–200:
the equipment-list conclusion, towing gear and the first nomenclature tables.

## Open and review

- `Handbook_Master.sla` — current 200-page native document.
- `Handbook_Master_001-200_v10.pdf` — cumulative PDF from the reopened master.
- `Handbook_Comparison_181-200_v10.pdf` — twenty source/reconstruction pairs.
- `CONTINUE_HERE.md` and `PROJECT_STATUS.json` — continuation instructions/state.
- `REVIEW_NOTES.md` — retained source readings and editorial questions.

Install the three bundled C059 OpenType fonts before opening in Scribus 1.6.x.
Disable conflicting Type 1 copies, whose metrics alter layout. Keep `assets/`
beside the SLA; all 120 image links are relative and included. C059 remains a
provisional Century approximation. Original typeface and physical trim remain
unconfirmed; the working canvas is 396 × 612 pt (5.5 × 8.5 in).

## Editable content and source treatment

The master has 9,780 native text frames, including 2,768 added in this batch.
The new content comprises 110 body/list lines, 765 nomenclature rows, native
column headings, part-number leaders, grouped quantities, captions and folios.
Body text retains source lines and page breaks. Table cells use native text and
rules. Common fractions use font glyphs; other table fractions use separate
editable numerator, denominator and rule objects. The three slash fractions
in the page 181 tool list remain inline, as printed. Blank part-number and
quantity cells remain blank; x quantities are retained separately.

The 120 artwork assets comprise the title seal, Plates 1–118 and a second crop
for Plate 62. This batch adds eight original illustrations. Internal lettering,
leaders and engineering detail remain raster. Paper normalization reduces
discoloration; texture, stains and binding distortion can remain. No nonlinear
warp, sharpening, redrawing or generated replacement artwork is applied.

Source baseline estimates and OCR line indices remain in the transcription JSON.
Text baselines are straightened independently of illustration geometry. Draft OCR
used wider left-page crops and fuller bottom margins; the new content fits in the
nominal source halves used for comparison. The earlier page 132 crop override is
preserved. Apparent printing errors and inconsistent dimensions remain as printed;
see REVIEW_NOTES.md, especially the 2 7/10 dimension on page 200. Independent
proofreading remains pending.

## Verification

The master was reopened in Scribus 1.6.1. All 9,780 native text frames pass text,
single-line and overflow checks. All twenty new pages were rendered with Poppler
and visually reviewed, with enlarged checks of table columns, grouped quantities,
fractions, list hierarchy and plate edges. New text stays within the page bounds.

All 7,634 earlier page objects retain content, geometry and style assignments.
PDF pages 1–180 are pixel-identical to v9 at 144 dpi. Scribus regenerates internal
ItemIDs, rounds four earlier character-style scales and drops 12 unused line SHADE
attributes. These serialization changes are recorded. All fonts are embedded,
expected native text sequences appear in PDF extraction, and asset hashes match.
See `data/*validation.json` and `data/visual_review.md`.

## Rebuild this batch

Authoritative inputs are `data/body_batch10.json` and `data/tables_batch10.json`.
Readable transcripts are `data/batch10_body_transcription.txt` and
`data/batch10_table_transcription.tsv`. Layout is in `layout_batch10.py`.
All artwork is bundled, so source scans are unnecessary for rebuilding the SLA.

1. Preserve manual edits. `build_project.py` starts from the exact
   `Handbook_Checkpoint_001-180_v9.sla` and cannot discover later manual changes.
2. Run `build_project.py` inside Scribus to append pages 181–200 and save the master.
3. Run `check_project.py` inside Scribus to reopen, validate and export the v10 PDF.
4. Run `python verify_preservation.py` and `python verify_pdf.py` outside Scribus.
   Supply `--previous-pdf PATH` to the latter to compare the first 180 pages.
5. Run `python make_comparison.py --source-dir /path/to/scans`, then
   `python verify_comparison.py`, to reproduce/check the comparison proof.

`prepare_batch10_transcription.py` reproduces the new JSON and readable transcripts
from bundled draft OCR, TSV coordinates and explicit source corrections. Running
it replaces manual edits to these inputs. `prepare_batch10_assets.py --source-dir
PATH` reproduces the eight new artwork crops. `fetch_sources.py` retrieves the
101 hash-pinned spreads sequentially and resumably. Original scans are recoverable
from the recorded GitHub paths and hashes and are not duplicated in this ZIP.

Headless Scribus needs explicit `-platform offscreen`, `HANDBOOK_BATCH=1`, an
OpenType-only font configuration and `-py /absolute/path/script.py` last. Inspect
error/status files: caught exceptions can return exit status zero. Keep the PDF
exporter a local function so it finalizes before exit. After workspace cleanup,
check local Scribus data/plugin links before running a private runtime.

Image/transcription/comparison tools use Pillow, NumPy, SciPy, PyMuPDF and ReportLab.
Comparison PDFs embed bundled DejaVu Sans fonts. Historical builders and earlier
SLAs remain baselines; continue from the current master to preserve edits.

## Release names and continuation

Current PDF: `Handbook_Master_001-200_v10.pdf`.
Next planned PDF: `Handbook_Master_001-220_v11.pdf`.
Every released PDF needs a unique page-range/version filename. A revised proof of
this release requires a fresh suffix such as `v10r1`, with scripts and state
updated together. Never release a generic `Handbook_Master.pdf`. The native
working file may retain `Handbook_Master.sla`.

Next batch: printed pages 201–220, scan 101 right through scan 111 left. Retain
the cumulative ZIP and provide the latest copy if the workspace is unavailable
later. The user manually commits downloads to GitHub; this release does not push
repository changes.
