# Preliminary Handbook of the Mark VIII Tank — checkpoint 07

The cumulative native Scribus master contains the title leaf (inferred page 1)
and printed pages 2–140, with Plates 1–88. This iteration adds pages 121–140.
Work continues in batches of about twenty printed pages.

## Open and review

- `Handbook_Master.sla` — current 140-page native document.
- `Handbook_Master_001-140_v7.pdf` — cumulative PDF from the reopened master.
- `Handbook_Comparison_121-140_v7.pdf` — this batch's source/reconstruction proof.
- `CONTINUE_HERE.md` and `PROJECT_STATUS.json` — continuation instructions and state.
- `REVIEW_NOTES.md` — source readings and editorial questions.

Install the three bundled C059 OpenType fonts before opening in Scribus 1.6.x.
Disable conflicting Type 1 copies, whose metrics alter layout. Keep `assets/`
beside the SLA; all 90 image links are relative and their files are included.
C059 is a provisional Century approximation. The original font and physical trim
remain unconfirmed; the working canvas is 396 × 612 pt (5.5 × 8.5 in).

## Editable content and source treatment

The master has 5,544 native text frames, including 967 added in this batch.
Body text retains source lines and page breaks. Parts legends, specifications,
captions, folios and rules use native objects. The long Plate 81 caption remains
editable and rotated. Two special fractions on page 132 have separate editable
numerator, denominator and rule components; common fractions use C059 glyphs.

The 90 linked assets comprise the title seal, Plates 1–88 and a second crop for
Plate 62. This batch adds sixteen plates. Original drawing interiors and labels
remain raster. Grayscale paper normalization reduces discoloration; texture,
stains and geometric distortion may remain. No rotation, nonlinear warp,
sharpening, redrawing or generated replacement artwork is applied. Older Plate
62 has a documented outside-art caption exclusion.

Text baselines are straightened using observed local line spacing; source
estimates remain in the body JSON. Page 132 requires a wider source crop because
its binding-side line endings cross the nominal scan midpoint. Original wording,
apparent errors, blank cells and duplicate references are retained in native
text and flagged in REVIEW_NOTES.md. Independent proofreading remains pending.

## Verification

The master was reopened in Scribus 1.6.1. All 5,544 native text frames pass text,
single-line and overflow checks. All twenty new pages were rendered with Poppler
at 144 dpi and visually reviewed, with enlarged checks of fractions and legends.

All 5,075 earlier page objects retain content, geometry and style assignments;
earlier named styles are unchanged. PDF pages 1–120 are pixel-identical to v6 at
144 dpi. Scribus regenerates internal ItemIDs. All fonts are embedded, expected
native text sequences are present in the PDF, linked asset hashes match, and
text stays within page bounds. See `data/*validation.json` and `data/visual_review.md`.

## Rebuild this batch

Authoritative inputs are `data/body_batch07.json` and `data/tables_batch07.json`.
A readable body transcript is `data/batch07_body_transcription.txt`. Captions,
tables and legend layout are in `layout_batch07.py`. Original scans are not
required for rebuilding the master because all cleaned artwork is bundled.

1. Preserve manual edits. `build_project.py` starts from the exact
   `Handbook_Checkpoint_001-120_v6.sla` and cannot discover later manual changes.
2. Run `build_project.py` inside Scribus to append pages 121–140 and save
   `Handbook_Master.sla`; inspect status and native validation records.
3. Run `check_project.py` inside Scribus to reopen, validate and export
   `Handbook_Master_001-140_v7.pdf`.
4. Run `python verify_preservation.py` and `python verify_pdf.py` outside Scribus.
   The latter accepts `--previous-pdf PATH` to compare the first 120 pages.
5. Run `python make_comparison.py --source-dir /path/to/scans` to reproduce the
   source comparison, including page 132's crop override.

Headless Scribus needs explicit `-platform offscreen`, `HANDBOOK_BATCH=1`, an
OpenType-only font configuration, and `-py /absolute/path/script.py` last.
Inspect error/status files: caught exceptions can return exit status zero. The
PDF exporter must remain a local function to finalize before process exit.

`fetch_sources.py` retrieves 71 hash-pinned spreads sequentially and resumably.
`prepare_batch07_assets.py --source-dir PATH` rebuilds this batch's artwork.
Image/comparison tools use Pillow, NumPy, SciPy, PyMuPDF and ReportLab. Comparison
PDFs embed the separately bundled DejaVu Sans fonts. Historical builders and
20/40/60/80/100/120-page SLAs are baselines; continue from the latest master to
preserve subsequent manual edits.

## Release names and continuation

Every released PDF must use a unique page-range/version filename. Current:
`Handbook_Master_001-140_v7.pdf`. Next planned: `Handbook_Master_001-160_v8.pdf`.
A revision of this 140-page release needs a fresh suffix such as `v7r1`, with
scripts and status updated together. Do not release a generic `Handbook_Master.pdf`.
The native working file may retain `Handbook_Master.sla`.

Next batch: printed pages 141–160, scan 071 right through scan 081 left. Retain
the cumulative ZIP and provide the latest copy if the workspace is unavailable
in a later session. The user manually commits downloads to GitHub; no repository
changes are pushed by this release.
