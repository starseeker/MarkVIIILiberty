# Preliminary Handbook of the Mark VIII Tank — checkpoint 05

The cumulative native Scribus master includes the unnumbered title leaf
(inferred page 1) and printed pages 2–100, with Plates 1–65. This batch adds
printed pages 81–100. Work continues in twenty-page batches.

## Open and review

- `Handbook_Master.sla` — current hundred-page native document.
- `Handbook_Master_001-100_v5.pdf` — cumulative PDF from the reopened master.
- `Handbook_Comparison_081-100_v5.pdf` — this batch's source/reconstruction comparison.
- `CONTINUE_HERE.md` — next batch and rules for preserving earlier work.
- `PROJECT_STATUS.json` — machine-readable checkpoint state.
- `REVIEW_NOTES.md` — source readings and remaining editorial questions.

Install the three bundled C059 OpenType fonts before opening the SLA in Scribus
1.6.x. Disable conflicting Type 1 copies of C059; their different metrics change
the layout. Keep `assets/` beside the SLA. All 67 image links are relative and
their artwork files are included. C059 is a provisional Century approximation;
the original font and physical trim remain unconfirmed. The working canvas is
396 × 612 pt (5.5 × 8.5 in).

## What is editable

The master has 3,579 native text frames, including 698 added in this batch.
Source text is retained in individual line frames. Wrapped text on pages 89,
90 and 93 uses explicit columns. The ten-row rotated parts legend on page 95
uses separate native cells. Italic runs and small-cap lead-ins retain native
character formatting. Two 3/16 fractions use separate numerator/denominator
frames and rules; familiar quarter/half fractions use font glyphs. Captions,
folios and rules are native objects.

Illustration interiors retain original scan pixels and lettering. The 67 linked
assets comprise the title seal, Plates 1–65, and the second crop for Plate 62.
This batch adds fifteen plates in sixteen assets. Grayscale paper normalization
reduces discoloration without redrawing detail. Texture, stains and geometric
distortion remain. No rotation, nonlinear dewarping, sharpening or generated
replacement artwork is applied. A small outside-art caption fragment is masked
in the lower Plate 62 crop because that caption is reconstructed as native text.

Source order and line/page breaks are retained. Text baselines are straightened
and regularly spaced within continuous runs, using the observed line spacing.
The source baseline estimates remain in the input JSON for review. Headings
retain source positions except where modest clearance adjustments are needed.

## Verification

The saved master was reopened in Scribus 1.6.1. All 3,579 text frames passed
native text, single-line and overflow checks. All twenty new pages were rendered
and visually inspected, including wrapped text, rotated legend and fractions.
Part numbers, dimensions and unusual readings were checked against enlarged
source crops. Independent proofreading remains pending.

All 3,291 earlier page objects retain text, geometry and style assignments.
The first eighty PDF pages are pixel-identical to checkpoint 04 at 144 dpi.
Scribus rounds two earlier horizontal-scale values (92.14 to 92.1 and 92.44 to
92.4), regenerates internal object IDs, and removes three unused SHADE line
attributes. No change appears in the compared pages. All fonts are embedded;
all expected text sequences, artwork links and hashes pass. See `data/*validation.json`.

## Rebuild this batch

Authoritative source-checked inputs: `data/body_batch05.json` and
`data/batch05_legend.json`. A readable body transcript is included as
`data/batch05_body_transcription.txt`. Native captions and artwork placement
are in `build_project.py`. Original scans are unnecessary for rebuilding when
the included artwork is retained.

1. Preserve manual edits. This builder starts from
   `Handbook_Checkpoint_001-080_v4.sla`; it cannot discover later manual changes.
2. Run `build_project.py` inside Scribus to append pages 81–100 and save
   `Handbook_Master.sla`. Inspect `build-status.txt` and `data/native_validation.json`.
3. Run `check_project.py` inside Scribus to reopen, validate and export
   `Handbook_Master_001-100_v5.pdf`.
4. Run `python verify_pdf.py` outside Scribus. Optional `--previous-pdf PATH`
   compares the first eighty rendered pages with checkpoint 04.
5. Rebuild the comparison with
   `python make_comparison.py --source-dir /path/to/source/scans`.

Headless Scribus needs explicit `-platform offscreen`, `HANDBOOK_BATCH=1`, an
OpenType-only font configuration and `-py /absolute/path/script.py` last.
Inspect status/error files: a caught exception can still return process status
zero. Keep PDF export in a local function so its file finalizes before exit.

`fetch_sources.py` recovers the 51 hash-pinned source spreads sequentially and
resumably. `prepare_batch05_assets.py` rebuilds only this batch's artwork and
preserves earlier images. Image/comparison tools use Pillow, NumPy, SciPy,
PyMuPDF and ReportLab. The older builders and 20/40/60/80-page SLAs are historical
baselines; continue from the latest master when preserving manual edits.

## Release naming and continuation

Every released PDF must have a unique page-range/version filename. Never deliver
an updated PDF as `Handbook_Master.pdf`. Current: `Handbook_Master_001-100_v5.pdf`.
Next planned: `Handbook_Master_001-120_v6.pdf`. A revised hundred-page proof must
use a fresh suffix such as `v5r1`, with scripts and status updated consistently.
The native working file may retain `Handbook_Master.sla`.

Next batch: printed pages 101–120, scan 051 right through scan 061 left.
Retain the cumulative ZIP and provide the latest copy if these workspace files
are unavailable in a later session.
