# Preliminary Handbook of the Mark VIII Tank — checkpoint 04

The cumulative native Scribus master includes the unnumbered title leaf
(inferred page 1) and printed pages 2–80, with Plates 1–50. This batch adds
printed pages 61–80. Work continues in twenty-page batches.

## Open and review

- `Handbook_Master.sla` — current eighty-page native document.
- `Handbook_Master_001-080_v4.pdf` — cumulative PDF from the reopened master.
- `Handbook_Comparison_061-080_v4.pdf` — this batch's source/reconstruction comparison.
- `CONTINUE_HERE.md` — next batch and rules for preserving earlier work.
- `PROJECT_STATUS.json` — machine-readable checkpoint state.
- `REVIEW_NOTES.md` — source readings and remaining editorial questions.

Install the three bundled C059 OpenType fonts before opening the SLA in Scribus
1.6.x. Disable conflicting Type 1 copies of C059; their different metrics change
the layout. Keep `assets/` beside the SLA. All 51 image links are relative and
their artwork files are included. C059 is a provisional Century approximation;
the original font and physical trim have not been established conclusively.
The working canvas remains 396 × 612 pt (5.5 × 8.5 in).

## What is editable

The master has 2,881 native text frames, including 631 added in this batch.
Source text is retained in individual line frames. Earlier specification lists,
tables and part legends use separate editable cells. Italic runs and small-cap
lead-ins use native character formatting. Four inline fractions in this batch
use separate native numerator/denominator frames and rules. Caption text, folios,
rules and leaders are native objects.

Illustration interiors retain the scan's pixels, including original lettering.
The 51 linked assets comprise the title seal and Plates 1–50. This batch adds
Plates 42–50. Grayscale paper normalization reduces discoloration; it does not
redraw detail. Print texture, stains and some geometric distortion remain.
No rotation, nonlinear dewarping, sharpening or generated replacement artwork
is applied. The opening list on page 61 has regularized baselines. Source order
and line/page breaks are retained; the page 63 ENGINE OVERHAUL heading is moved
down 2.25 pt to clear the preceding line.

## Verification

The saved master was reopened in Scribus 1.6.1. All 2,881 text frames passed
text, single-line and overflow checks. All twenty new PDF pages were rendered
and visually inspected. Fractions, part numbers, clearances and unusual readings
were checked against enlarged source crops. Independent proofreading is pending.

All 2,647 page objects from checkpoint 03 retain their text, geometry and style
assignments. The first sixty PDF pages are pixel-identical to checkpoint 03 at
144 dpi. Scribus rounds three earlier horizontal-scale style values (92.28 to
92.3, 92.18 to 92.2, and 91.22 to 91.2) and removes 26 unused SHADE attributes
from line objects; neither changes those rendered pages. All PDF fonts are
embedded, all expected text sequences are present and all relative artwork
links and hashes pass. See `data/*validation.json`.

## Rebuild this batch

The authoritative source-checked input is `data/body_batch04.json`.
`data/batch04_body_transcription.txt` is a readable transcript. Native captions
and illustration placement are in `build_project.py`. Rebuilding the master
does not need original scans when the bundled artwork is retained.

1. Preserve any manual edits to the current master. The script rebuilds from
   `Handbook_Checkpoint_001-060_v3.sla`; it cannot discover later manual edits.
2. Run `build_project.py` inside Scribus's Script menu to append pages 61–80 and
   save `Handbook_Master.sla`. Check `build-status.txt` and `data/native_validation.json`.
3. Run `check_project.py` inside Scribus. It reopens the saved master, validates
   every text frame and exports `Handbook_Master_001-080_v4.pdf`.
4. Run `python verify_pdf.py` outside Scribus to inspect PDF text, fonts, page
   bounds, artwork links and hashes. Optional `--previous-pdf PATH` checks the
   first sixty rendered pages against checkpoint 03.
5. Rebuild the comparison with
   `python make_comparison.py --source-dir /path/to/source/scans`.

For headless Scribus, pass `-platform offscreen` explicitly, set `HANDBOOK_BATCH=1`,
and put `-py /absolute/path/script.py` last. Use a font configuration selecting
these exact OpenType files. Scripts write status/error files because the headless
exit path may return zero even when an exception has been caught. The PDF
exporter is a local function so its file is finalized before that exit.

Original scans are recoverable using `fetch_sources.py` and the SHA-256 hashes in
`data/source_inventory.json` (scans 001–041). Fetch sequentially in resumable groups.
`prepare_batch04_assets.py` regenerates this batch's images while preserving earlier
assets. Image/comparison tools use Pillow, NumPy, SciPy, PyMuPDF and ReportLab.
Older build scripts and 20/40/60-page SLAs are historical baselines.

## Release naming and continuation

Never deliver a new cumulative PDF as the unversioned `Handbook_Master.pdf`.
Every published checkpoint or revised proof must use a fresh range/version name.
This release is `Handbook_Master_001-080_v4.pdf`; the planned next release is
`Handbook_Master_001-100_v5.pdf`. A revision to this eighty-page release should
use a new suffix such as `v4r1`, updating scripts and status consistently.
The native working file can keep its stable `Handbook_Master.sla` name.

Next: printed pages 81–100, scan 041 right through scan 051 left. The cumulative
ZIP contains everything needed to open and continue this checkpoint. Retain it
and provide the latest copy if these workspace files are unavailable later.
