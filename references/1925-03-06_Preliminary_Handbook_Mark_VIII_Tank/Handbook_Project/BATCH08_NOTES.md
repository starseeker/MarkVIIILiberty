# Preliminary Handbook of the Mark VIII Tank — checkpoint 08

The cumulative native Scribus master contains the title leaf (inferred page 1)
and printed pages 2–160, with Plates 1–104. This iteration adds pages 141–160.
Work continues in batches of about twenty printed pages.

## Open and review

- `Handbook_Master.sla` — current 160-page native document.
- `Handbook_Master_001-160_v8.pdf` — cumulative PDF exported from the reopened master.
- `Handbook_Comparison_141-160_v8.pdf` — this batch's source/reconstruction proof.
- `CONTINUE_HERE.md` and `PROJECT_STATUS.json` — continuation instructions and state.
- `REVIEW_NOTES.md` — source readings and editorial questions.

Install the three bundled C059 OpenType fonts before opening in Scribus 1.6.x.
Disable conflicting Type 1 copies, whose metrics alter layout. Keep `assets/`
beside the SLA; all 106 image links are relative and their files are included.
C059 is a provisional Century approximation. Original typeface and physical trim
remain unconfirmed; the working canvas is 396 × 612 pt (5.5 × 8.5 in).

## Editable content and source treatment

The master has 6,243 native text frames, including 699 added in this batch.
Body text retains source lines and page breaks. Parts legends, specifications,
captions, folios and rules use native objects. Plate 92's long caption remains
editable and rotated. This batch's body fractions use native C059 glyphs; earlier
special fractions retain separate editable components. The page 160 equipment
list has native hanging indents.

The 106 linked assets comprise the title seal, Plates 1–104 and a second crop for
Plate 62. This batch adds sixteen plates. Original drawing interiors, dimensional
annotations and internal lettering remain raster. Paper normalization reduces
discoloration; texture, stains and geometric distortion may remain. No rotation,
nonlinear warp, sharpening, redrawing or generated replacement artwork is applied.
Plate 92 and dimensional Plates 97–99 use conservative cleanup to retain faint
lines. Outside-art caption exclusions on Plates 90 and 93 prevent duplicate text;
HIGH/LOW labels in Plate 93 are preserved. Older Plate 62 has a similar exclusion.

Text baselines are straightened using local line spacing; source estimates remain
in the body JSON. Draft OCR used wider left-page crops and fuller bottom margins.
All new-page text fits within the nominal source halves used for comparison.
Page 132's earlier source-crop override is retained in the cumulative records.
Original errors and reference gaps are retained and flagged in REVIEW_NOTES.md.
Independent proofreading remains pending.

## Verification

The master was reopened in Scribus 1.6.1. All 6,243 native text frames pass text,
single-line and overflow checks. All twenty new pages were rendered with Poppler
at 144 dpi and visually reviewed, with enlarged checks of legends and details.

All 6,097 earlier page objects retain content, geometry and style assignments.
PDF pages 1–140 are pixel-identical to v7 at 144 dpi. Scribus regenerates internal
ItemIDs, rounds 14 earlier character-style scales and drops 26 unused line SHADE
attributes. These serialization changes are recorded. All fonts are embedded,
expected native text sequences appear in the PDF, asset hashes match, and text
stays within page bounds. See `data/*validation.json` and `data/visual_review.md`.

## Rebuild this batch

Authoritative inputs are `data/body_batch08.json` and `data/tables_batch08.json`.
Readable transcript: `data/batch08_body_transcription.txt`. Caption/table layout:
`layout_batch08.py`. All artwork is bundled, so original scans are unnecessary
for rebuilding the Scribus master.

1. Preserve manual edits. `build_project.py` starts from the exact
   `Handbook_Checkpoint_001-140_v7.sla` and cannot discover later manual changes.
2. Run `build_project.py` inside Scribus to append pages 141–160 and save the master.
3. Run `check_project.py` inside Scribus to reopen, validate and export
   `Handbook_Master_001-160_v8.pdf`.
4. Run `python verify_preservation.py` and `python verify_pdf.py` outside Scribus.
   The latter accepts `--previous-pdf PATH` to compare the first 140 pages.
5. Run `python make_comparison.py --source-dir /path/to/scans`, then
   `python verify_comparison.py`, to reproduce and check the comparison proof.

Headless Scribus needs explicit `-platform offscreen`, `HANDBOOK_BATCH=1`, an
OpenType-only font configuration and `-py /absolute/path/script.py` last. Inspect
error/status files: caught exceptions can return exit status zero. Keep the PDF
exporter a local function so it finalizes before process exit. If using a local
runtime after workspace cleanup, check that Scribus data/plugin paths still exist.

`fetch_sources.py` retrieves 81 hash-pinned spreads sequentially and resumably.
`prepare_batch08_assets.py --source-dir PATH` rebuilds this batch's artwork.
Image/comparison tools use Pillow, NumPy, SciPy, PyMuPDF and ReportLab. Comparison
PDFs embed bundled DejaVu Sans fonts. Historical builders and 20/40/60/80/100/120/
140-page SLAs are baselines; continue from the latest master to preserve edits.

## Release names and continuation

Current PDF: `Handbook_Master_001-160_v8.pdf`.
Next planned PDF: `Handbook_Master_001-180_v9.pdf`.
Every released PDF requires a unique page-range/version filename. A revision of
this release needs a fresh suffix such as `v8r1`, with scripts and state updated
together. Never release a generic `Handbook_Master.pdf`. The native working file
may retain `Handbook_Master.sla`.

Next batch: printed pages 161–180, scan 081 right through scan 091 left. Retain
the cumulative ZIP and provide the latest copy if the workspace is unavailable
in a later session. The user manually commits downloads to GitHub; this release
does not push repository changes.
