# Preliminary Handbook of the Mark VIII Tank — checkpoint 06

The cumulative native Scribus master now contains the title leaf (inferred page 1)
and printed pages 2–120, with Plates 1–72. This iteration adds pages 101–120.
Work continues in batches of about twenty printed pages.

## Open and review

- `Handbook_Master.sla` — current 120-page native document.
- `Handbook_Master_001-120_v6.pdf` — cumulative PDF exported from the reopened master.
- `Handbook_Comparison_101-120_v6.pdf` — this batch's source/reconstruction comparison.
- `CONTINUE_HERE.md` and `PROJECT_STATUS.json` — continuation instructions and state.
- `REVIEW_NOTES.md` — source readings and remaining editorial questions.

Install the three bundled C059 OpenType fonts before opening in Scribus 1.6.x.
Disable conflicting Type 1 copies: their different metrics alter layout. Keep
`assets/` beside the SLA; all 74 links are relative and all artwork is included.
C059 is a provisional Century approximation. The original font and physical trim
remain unconfirmed; the working canvas is 396 × 612 pt (5.5 × 8.5 in).

## What is editable

The master has 4,577 native text frames, including 998 added in this batch.
Body text retains individual source lines and page breaks. Tables and legends
use native cells, including the rotated Plate 67 legend, clearance summary,
clutch specifications and parts lists. Three special fractions use separate
native numerator/denominator components; familiar fractions use C059 glyphs.
Italics, small-cap lead-ins, captions, folios and rules remain editable.

The 74 linked assets comprise the title seal, Plates 1–72, and a second crop for
Plate 62. This batch adds seven plates. Original drawing interiors and lettering
remain raster. Grayscale paper normalization reduces discoloration; texture,
stains and geometric distortion can remain. There is no rotation, nonlinear
warp, sharpening, redrawing or generated replacement artwork. Older Plate 62
has a documented outside-art caption exclusion.

Text baselines are straightened using the observed local line spacing; source
baseline estimates remain in the body JSON. The clearance table uses a regular
row grid. Original wording, apparent errors and differing printed values are
retained and flagged in the review notes. Independent proofreading is pending.

## Verification

The saved master was reopened in Scribus 1.6.1. All 4,577 native text frames pass
text, single-line and overflow checks. All twenty new pages were rendered and
visually reviewed. Caption/header collisions found during review were corrected,
and fractions and small table readings checked at larger size.

All 4,007 earlier page objects retain content, geometry and style assignments.
PDF pages 1–100 are pixel-identical to v5 at 144 dpi. Scribus regenerates internal
IDs, rounds five earlier character-style scales and drops two unused SHADE line
attributes; these serialization differences are recorded. All fonts are embedded,
all expected text sequences are present, all linked asset hashes match, and no
text falls outside page bounds. See `data/*validation.json`.

## Rebuild this batch

Authoritative inputs are `data/body_batch06.json` and `data/tables_batch06.json`.
A readable body transcript is `data/batch06_body_transcription.txt`. Caption,
table and legend layout is in `layout_batch06.py`. Bundled artwork makes original
scans unnecessary for rebuilding the Scribus master.

1. Preserve manual edits. `build_project.py` starts from the exact
   `Handbook_Checkpoint_001-100_v5.sla` and cannot discover later manual changes.
2. Run `build_project.py` inside Scribus to append pages 101–120 and save
   `Handbook_Master.sla`; inspect status and native validation records.
3. Run `check_project.py` inside Scribus to reopen, validate and export
   `Handbook_Master_001-120_v6.pdf`.
4. Run `python verify_preservation.py` and `python verify_pdf.py` outside Scribus.
   The latter accepts `--previous-pdf PATH` to compare the first hundred pages.
5. Run `python make_comparison.py --source-dir /path/to/source/scans` to reproduce
   the source comparison.

Headless Scribus needs explicit `-platform offscreen`, `HANDBOOK_BATCH=1`, an
OpenType-only font configuration, and `-py /absolute/path/script.py` last.
Inspect error/status files: a caught exception can still return exit status zero.
The PDF exporter must remain a local function so it finalizes before process exit.

`fetch_sources.py` retrieves the 61 hash-pinned spreads sequentially and resumably.
`prepare_batch06_assets.py --source-dir PATH` rebuilds only this batch's artwork.
Image/comparison tools use Pillow, NumPy, SciPy, PyMuPDF and ReportLab. The
comparison PDF embeds the separately bundled DejaVu Sans fonts. Older
builders and 20/40/60/80/100-page SLAs are historical baselines; preserve manual
edits by continuing from the latest master.

## Release names and continuation

Every released PDF must have a unique page-range/version filename. Current:
`Handbook_Master_001-120_v6.pdf`. Next planned: `Handbook_Master_001-140_v7.pdf`.
A revision of this 120-page release needs a fresh suffix such as `v6r1`, with
scripts and status updated together. Do not release a generic `Handbook_Master.pdf`.
The native working file may retain `Handbook_Master.sla`.

Next batch: printed pages 121–140, scan 061 right through scan 071 left. Retain
the cumulative ZIP and provide the latest copy if the workspace is unavailable
in a later session. The user manually commits downloads to GitHub; this release
does not push repository changes.
