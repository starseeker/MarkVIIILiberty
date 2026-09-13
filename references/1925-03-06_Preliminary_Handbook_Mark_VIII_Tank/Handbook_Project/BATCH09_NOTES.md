# Preliminary Handbook of the Mark VIII Tank — checkpoint 09

The cumulative native Scribus master contains the title leaf (inferred page 1)
and printed pages 2–180, with Plates 1–110. This iteration adds pages 161–180.
Work continues in batches of about twenty printed pages.

## Open and review

- `Handbook_Master.sla` — current 180-page native document.
- `Handbook_Master_001-180_v9.pdf` — cumulative PDF exported from the reopened master.
- `Handbook_Comparison_161-180_v9.pdf` — this batch's source/reconstruction proof.
- `CONTINUE_HERE.md` and `PROJECT_STATUS.json` — continuation instructions and state.
- `REVIEW_NOTES.md` — source readings and editorial questions.

Install the three bundled C059 OpenType fonts before opening in Scribus 1.6.x.
Disable conflicting Type 1 copies, whose metrics alter layout. Keep `assets/`
beside the SLA; all 112 image links are relative and their files are included.
C059 is a provisional Century approximation. Original typeface and physical trim
remain unconfirmed; the working canvas is 396 × 612 pt (5.5 × 8.5 in).

## Editable content and source treatment

The master has 7,012 native text frames, including 769 added in this batch.
Body text retains source lines and page breaks. Parts legends, specifications,
captions, folios, printer signatures and rules use native objects. This batch
includes electrical equipment, armament, ventilation and the tentative equipment
list. Lists preserve their indentation and continued lines. Italic terms remain
editable. The 5/16 fractions on pages 176 and 177 use native stacked components;
common fractions use C059 glyphs.

The 112 linked assets comprise the title seal, Plates 1–110 and a second crop for
Plate 62. This batch adds six plates, including wiring and ventilation drawings,
a pinion-shift section, a brush-regulation diagram and two photographs. Original
internal labels and engineering detail remain raster. Paper normalization reduces
discoloration; texture, stains and geometric distortion may remain. No rotation,
nonlinear warp, sharpening, redrawing or generated replacement artwork is applied.
Historical caption exclusions on Plates 62, 90 and 93 are unchanged.

Text baselines are straightened using local line spacing; source estimates remain
in the body JSON. Draft OCR used wider left-page crops and fuller bottom margins.
This batch's text and artwork fit within the nominal source halves used for
comparison. Page 132's earlier source-crop override remains in cumulative records.
Original errors, duplicate reference numbers, incomplete statements and differing
quantities are retained and flagged in REVIEW_NOTES.md. Independent proofreading
remains pending.

## Verification

The master was reopened in Scribus 1.6.1. All 7,012 native text frames pass text,
single-line and overflow checks. All twenty new pages were rendered with Poppler
at 144 dpi and visually reviewed, with enlarged checks of legends, fractions
and list continuations. No new frames were compressed below 85% horizontal scale.

All 6,843 earlier page objects retain content, geometry and style assignments.
PDF pages 1–160 are pixel-identical to v8 at 144 dpi. Scribus regenerates internal
ItemIDs, rounds six earlier character-style scales and drops 25 unused line SHADE
attributes. These serialization changes are recorded. All fonts are embedded,
expected native text sequences appear in the PDF, asset hashes match, and text
stays within page bounds. See `data/*validation.json` and `data/visual_review.md`.

## Rebuild this batch

Authoritative inputs are `data/body_batch09.json` and `data/tables_batch09.json`.
Readable transcript: `data/batch09_body_transcription.txt`. Caption/table layout:
`layout_batch09.py`. All artwork is bundled, so original scans are unnecessary
for rebuilding the Scribus master.

1. Preserve manual edits. `build_project.py` starts from the exact
   `Handbook_Checkpoint_001-160_v8.sla` and cannot discover later manual changes.
2. Run `build_project.py` inside Scribus to append pages 161–180 and save the master.
3. Run `check_project.py` inside Scribus to reopen, validate and export
   `Handbook_Master_001-180_v9.pdf`.
4. Run `python verify_preservation.py` and `python verify_pdf.py` outside Scribus.
   The latter accepts `--previous-pdf PATH` to compare the first 160 pages.
5. Run `python make_comparison.py --source-dir /path/to/scans`, then
   `python verify_comparison.py`, to reproduce and check the comparison proof.

Headless Scribus needs explicit `-platform offscreen`, `HANDBOOK_BATCH=1`, an
OpenType-only font configuration and `-py /absolute/path/script.py` last. Inspect
error/status files: caught exceptions can return exit status zero. Keep the PDF
exporter a local function so it finalizes before process exit. If using a local
runtime after workspace cleanup, check that Scribus data/plugin paths still exist.

`fetch_sources.py` retrieves 91 hash-pinned spreads sequentially and resumably.
`prepare_batch09_assets.py --source-dir PATH` rebuilds this batch's artwork.
Image/comparison tools use Pillow, NumPy, SciPy, PyMuPDF and ReportLab. Comparison
PDFs embed bundled DejaVu Sans fonts. Historical builders and 20/40/60/80/100/120/
140/160-page SLAs are baselines; continue from the latest master to preserve edits.

## Release names and continuation

Current PDF: `Handbook_Master_001-180_v9.pdf`.
Next planned PDF: `Handbook_Master_001-200_v10.pdf`.
Every released PDF requires a unique page-range/version filename. A revision of
this release needs a fresh suffix such as `v9r1`, with scripts and state updated
together. Never release a generic `Handbook_Master.pdf`. The native working file
may retain `Handbook_Master.sla`.

Next batch: printed pages 181–200, scan 091 right through scan 101 left. Retain
the cumulative ZIP and provide the latest copy if the workspace is unavailable
in a later session. The user manually commits downloads to GitHub; this release
does not push repository changes.
