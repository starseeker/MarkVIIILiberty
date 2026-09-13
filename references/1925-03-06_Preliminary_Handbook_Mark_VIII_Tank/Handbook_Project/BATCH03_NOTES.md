# Preliminary Handbook of the Mark VIII Tank — checkpoint 03

The cumulative native Scribus master now includes the unnumbered title leaf
(inferred page 1) and printed pages 2–60, with Plates 1–41. This batch adds
printed pages 41–60. The handbook is still being reconstructed in twenty-page batches.

## Open and review

- `Handbook_Master.sla` — current sixty-page native document.
- `Handbook_Master_001-060_v3.pdf` — cumulative PDF exported from the reopened master.
- `Handbook_Comparison_041-060_v3.pdf` — this batch's source/reconstruction comparison.
- `CONTINUE_HERE.md` — next batch and the rules for preserving earlier work.
- `PROJECT_STATUS.json` — machine-readable checkpoint state.
- `REVIEW_NOTES.md` — source readings and remaining editorial questions.

Install the three bundled C059 OpenType fonts before opening the SLA in Scribus
1.6.x. Disable conflicting Type 1 copies of C059; their different metrics change
the layout. Keep `assets/` beside the SLA. All image links are relative and all
42 artwork files are included. C059 is a provisional Century approximation;
the original font and physical trim have not been established conclusively.
The working canvas remains 396 × 612 pt (5.5 × 8.5 in).

## What is editable

The master has 2,250 native text frames, including 649 added in this batch.
Source text is retained in individual line frames. Specification lists, the
firing-order table and part legends use separate editable cells. Paragraph
lead-ins use native italic runs; the 4 15/16-inch value uses a native stacked
fraction. Caption text, folios, rules and leaders are native objects.

Illustration interiors retain the scan's pixels, including their original
lettering. The 42 linked assets comprise the title seal and Plates 1–41.
This batch adds Plates 32–41. Grayscale paper normalization reduces discoloration;
it does not redraw detail. Print texture, stains and some geometric distortion
remain. No rotation, nonlinear dewarping, sharpening or generated replacement
artwork is applied. The page 59 list baselines are regularized while preserving
its source order and line breaks.

## Verification

The saved master was reopened in Scribus 1.6.1. All 2,250 text frames passed
text, single-line and overflow checks. The new PDF was rendered and all twenty
new pages visually inspected. Small fractions, specifications, part numbers
and firing-order entries were checked against enlarged source crops.
An independent proofread remains pending.

All 1,950 page objects from checkpoint 02 retain their text, geometry and style
assignments. The first forty PDF pages are pixel-identical to the previous
checkpoint at 144 dpi. Scribus rounds two earlier horizontal-scale style values
(99.86 to 99.9 and 92.45 to 92.5) and removes 33 unused SHADE attributes from
line objects; neither changes those rendered pages. See `data/*validation.json`.

## Rebuild this batch

The source-checked inputs are `data/body_batch03.json` and
`data/batch03_tables.py`. `data/batch03_body_transcription.txt` is a readable body
transcript; tables and legends are in the Python data file. The build does not
need the original scans when the bundled artwork is retained.

1. Preserve any manual edits to the current master. The script rebuilds from
   `Handbook_Checkpoint_001-040_v2.sla`; it cannot discover later manual edits.
2. Run `build_project.py` inside Scribus's Script menu to append pages 41–60 and
   save `Handbook_Master.sla`. Check `build-status.txt` and `data/native_validation.json`.
3. Run `check_project.py` inside Scribus. It reopens the saved master, validates
   every text frame and exports `Handbook_Master_001-060_v3.pdf`.
4. Run `python verify_pdf.py` outside Scribus to inspect PDF text, fonts, page
   bounds, artwork links and hashes. An optional `--previous-pdf PATH` also checks
   the first forty rendered pages against checkpoint 02.
5. To rebuild the comparison, run
   `python make_comparison.py --source-dir /path/to/source/scans`.

For headless Scribus, pass `-platform offscreen` explicitly, set `HANDBOOK_BATCH=1`,
and put `-py /absolute/path/script.py` last. Use a font configuration that selects
these exact OpenType files. Scripts write status/error files because the headless
exit path may return exit status zero even when an exception has been caught.
The PDF exporter is a local function so its file is finalized before that exit.

Original scans are recoverable with `fetch_sources.py` and the SHA-256 hashes in
`data/source_inventory.json` (scans 001–031). Fetch in small resumable groups.
`prepare_batch03_assets.py` regenerates only this batch's images and preserves
previous assets. Image/comparison tools use Pillow, NumPy, SciPy, PyMuPDF and
ReportLab. The older build scripts and 20/40-page SLAs are historical baselines.

## Release naming and continuation

Never deliver a new cumulative PDF as the unversioned `Handbook_Master.pdf`.
Every published checkpoint or revised proof must use a fresh range/version name.
This release is `Handbook_Master_001-060_v3.pdf`; the planned next release is
`Handbook_Master_001-080_v4.pdf`. If this sixty-page release is revised first,
use a new suffix such as `v3r1`, then update scripts and status consistently.
The native working file can keep its stable `Handbook_Master.sla` name.

Next: printed pages 61–80, scan 031 right through scan 041 left. The cumulative
ZIP contains everything needed to open and continue this checkpoint. Retain it
and provide the latest copy if these workspace files are unavailable later.
