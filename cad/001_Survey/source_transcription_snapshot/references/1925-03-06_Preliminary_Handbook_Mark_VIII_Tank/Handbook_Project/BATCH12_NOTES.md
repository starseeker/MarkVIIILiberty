# Preliminary Handbook of the Mark VIII Tank — checkpoint 12

The cumulative native Scribus master contains 240 pages: the title leaf (inferred
page 1) and printed pages 2–240. This iteration adds pages 221–240, covering hull,
louver, oil-tank, road-track and other parts lists, thirteen technical plates,
and the first page of the nomenclature index.

## Open and review

- `Handbook_Master.sla` — current 240-page native document.
- `Handbook_Master_001-240_v12.pdf` — cumulative PDF from the reopened master.
- `Handbook_Comparison_221-240_v12.pdf` — twenty source/reconstruction pairs.
- `CONTINUE_HERE.md`, `PROJECT_STATUS.json` — continuation instructions and state.
- `REVIEW_NOTES.md` — source readings, retained printing errors and review questions.

Install the three bundled C059 OpenType fonts before opening in Scribus 1.6.x.
Disable conflicting Type 1 copies, whose metrics alter layout. Keep `assets/`
beside the SLA; all 146 image links are relative and included. C059 remains a
provisional Century approximation; physical trim is unmeasured. Working canvas:
396 × 612 pt (5.5 × 8.5 inches).

## Content and source treatment

The master has 14,202 native text frames, including 2,231 added here. This batch
contains 660 nomenclature rows and 39 index entries. Column headings, part numbers,
quantities, description lines, rules, braces, stacked fractions, captions, folios
and index leaders are editable Scribus objects. Empty cells remain empty. Two
pairs of codes on p235 share one quantity and description, with native braces.

Plates 131–143 retain the original raster engineering detail and internal labels.
Paper normalization reduces discoloration; residual texture and binding
curvature can remain. The Plate 133 and 136 labels are replaced by native text; one small
blank-paper stain above Plate 133 is repaired by paper-tone interpolation. Masks
are documented in `data/assets.json`. No redrawing or nonlinear warp is applied.
Earlier unnumbered figures and the missing Plate 126 label remain as before.

Text baselines are straightened separately from illustration geometry. Draft
OCR coordinates and source-line indices are included; the index is transcribed
directly from the scan. Printed anomalies remain as printed. Independent
proofreading, original font identification and physical trim measurement remain
open. See the side-by-side comparison PDF for review.

## Verification

The master was reopened in Scribus 1.6.1. All 14,202 native text frames pass exact
text, single-line and overflow checks. All twenty new pages were rendered with
Poppler and visually reviewed. Expected text is present in PDF extraction,
fonts are embedded, and all 146 artwork hashes and portable links are valid.

Pages 1–220 pixel-identical to v11 at 144 dpi; all 14,210 earlier page objects retain content, geometry and style assignments. Scribus rounds 12 character-style scales and removes 461 unused line SHADE attributes; see preservation_validation.json.

See `data/*validation.json` and `data/visual_review.md` for the recorded checks.

## Rebuild this batch

Authoritative native table input: `data/tables_batch12.json`. Readable transcript:
`data/batch12_table_transcription.tsv`. Index input and layout: `layout_batch12.py`;
readable index transcript: `data/batch12_index_transcription.tsv`.
All artwork is bundled; original scans are unnecessary to rebuild the SLA.

1. Preserve manual edits. `build_project.py` opens the exact
   `Handbook_Checkpoint_001-220_v11.sla`; it cannot discover later manual changes.
2. Run `build_project.py` inside Scribus to append 221–240 and save the master.
3. Run `check_project.py` inside Scribus to reopen, validate and export v12.
4. Run `python verify_preservation.py` and `python verify_pdf.py` outside Scribus.
   Supply `--previous-pdf PATH` to compare the first 220 pages with v11.
5. Run `python render_batch12.py` and inspect all twenty new-page PNGs.
6. Run `python make_comparison.py --source-dir /path/to/scans`, then
   `python verify_comparison.py`, to reproduce and check the comparison proof.

`prepare_batch12_transcription.py` reproduces table inputs from bundled draft
OCR, TSV coordinates and explicit source corrections. Running it replaces
manual edits to these inputs. `prepare_batch12_assets.py --source-dir PATH`
reproduces the 13 new crops. `fetch_sources.py` retrieves the 121 hash-pinned
spreads sequentially and resumably. Scans are not duplicated in the ZIP.

Headless Scribus requires explicit -platform offscreen, HANDBOOK_BATCH=1, an
OpenType-only font configuration and -py /absolute/script.py last. Inspect
status/error files: caught exceptions can return exit status zero. Keep the PDF
exporter local so it finalizes before exit. Preparation/review tools use Pillow,
NumPy, SciPy, PyMuPDF, ReportLab and Poppler. Comparison PDFs embed DejaVu Sans.
Historical builders and SLAs are baselines; continue from the current master.

## Versioning and continuation

Current PDF: `Handbook_Master_001-240_v12.pdf`. Revised 240-page proofs need a new
suffix such as v12r1. Never release a generic Handbook_Master.pdf.

Next: remaining pages starting 241, scan 121 right, through the unassessed final
scan 126. Determine the final printed page before naming the cumulative v13 PDF.
Keep the cumulative ZIP for later sessions. The user manually commits downloads
to GitHub; no repository changes have been pushed.
