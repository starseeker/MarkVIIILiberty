# Preliminary Handbook of the Mark VIII Tank — cumulative checkpoint 02

Open **Handbook_Master.sla**. It contains the title leaf and printed pages 2–40
in one continuous Scribus document, including Plates 1–31. This iteration added
printed pages 21–40. The goal is to extend this same master by approximately
20 printed pages per session until the handbook is complete.

The source is *No. 1977, Preliminary Handbook of the Mark VIII Tank*, dated
November 15, 1918, reprinted March 6, 1925. This is a modern research
reconstruction and remains a review draft.

## Opening and reviewing

1. Extract the complete `Handbook_Project` folder.
2. Install the three bundled C059 OpenType fonts and restart Scribus. Disable
   competing Type 1 copies of C059: they have different metrics.
3. Open `Handbook_Master.sla` in Scribus 1.6.x or later. Keep `assets/` beside it.
   The original scans and build scripts are not needed merely to open the file.
4. `Handbook_Master.pdf` previews all forty pages with embedded fonts.
5. `Handbook_Comparison_021-040_v2.pdf` pairs each new page with its source scan.
6. Read `REVIEW_NOTES.md` for source ambiguities and retained apparent errors.

The project contains **1,601 editable text frames** (542 added in this batch),
editable specification and reference-table cells, vector rules, and **32 linked
artwork assets**. Prose retains individual source lines and page breaks rather
than flowing continuously. Large textual revisions may require moving adjacent
frames. External captions are editable; lettering inside illustrations remains
raster.

## Continuation across sessions

**The next batch is printed pages 41–60**, from `MarkVIII021.jpg` right through
`MarkVIII031.jpg` left. Start with `CONTINUE_HERE.md` and `PROJECT_STATUS.json`.
Keep the latest complete project ZIP as the portable checkpoint. If a later
session cannot access this workspace, provide that ZIP to resume without
recreating completed pages. The files record the current master, source mapping,
completed folios, next range, typography, validation and unresolved readings.

Append to the latest master, including any user edits made since this release.
Create a new checkpoint ZIP and an updated cumulative PDF after each batch.
Do not substitute a separate twenty-page document for the cumulative master.
The full book's later foldouts and final folio count have not yet been surveyed.

## Working reconstruction choices

The canvas remains **5.5 × 8.5 inches** (396 × 612 points); the physical trim is
unmeasured. C059 is a provisional Century-style approximation, chosen separately
from the SNL work. Body text is generally 9.7 pt at 92.5% horizontal scale.
Original spelling, dimensions and apparent printing errors are retained, with
uncertain readings documented. Independent proofreading remains pending.

Artwork comes from original scan pixels. A robust quadratic paper-background
estimate removes illumination variation; line drawings use a stronger white
point than shaded plates. Halftone texture and some blemishes remain.
**No illustration rotation, nonlinear dewarping, tracing or generated detail is
applied.** This treatment does not infer the true geometry of mechanical parts
from the tilt of nearby text. `BATCH01_NOTES.md` preserves the earlier assessment
and typography rationale; its old next-batch directions are historical.

## Provenance and bounded downloads

Source scans:
https://github.com/starseeker/MarkVIIILiberty/tree/main/references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank

Sources are facing-page spreads. For book page n >= 2, the scan number is
`floor(n/2)+1`; even pages are left, odd pages right. The title leaf is scan 001
right, inferred page 1; scan 001 left is blank and excluded. The page split is
source x=1750, with 2550-pixel page height. `data/page_map.json` records every
included folio, source side and artwork link.

This checkpoint uses scans 001–021. Only scan 021 needed a new transfer in this
session; scans 011–020 were already cached. Only scan 021 left/page 40 is included.
`data/source_inventory.json` contains exact source SHA-256 hashes and byte counts;
`data/assets.json` contains crop rectangles, normalization settings, label masks
and output hashes. Original JPEGs are unchanged and are not duplicated in the ZIP.

## Rebuilding this checkpoint

Place this folder inside the repository's handbook scan directory; the JPEGs
then belong in its parent folder. Opening the supplied master needs no rebuild.
Rebuilding overwrites the named master outputs, so retain any manual edits first.

1. If sources are missing, run `python3 fetch_sources.py`. It downloads the
   21 manifest-pinned spreads sequentially and skips verified files. It refuses
   to replace a differing existing scan. Use `--destination /path/to/scans` as needed.
2. Existing artwork is included. To reproduce it from scans, run
   `python3 prepare_assets.py --source-dir /path/to/scans` for batch 01, then
   `python3 prepare_batch02_assets.py --source-dir /path/to/scans` for batch 02.
   These require Pillow, NumPy and SciPy and must run in that order.
3. Execute `build_project.py` inside Scribus. It opens the preserved
   `Handbook_Pilot_001-020_v1.sla` baseline and appends pages 21–40 to make
   `Handbook_Master.sla` and its PDF. New paragraph/character styles use a distinct
   prefix so they cannot redefine earlier styles.
4. Execute `check_project.py` inside Scribus. It reopens the saved master,
   validates all 1,601 text frames and exports the PDF from that reopened document.
5. Run `python3 make_comparison.py --source-dir /path/to/scans` to produce the
   comparison proof. It requires Pillow, PyMuPDF and ReportLab.

The supplied master is the file to extend for batch 03. The current build script
reproduces checkpoint 02 from its preserved baseline; it does not discover or
preserve later manual edits automatically. `build_batch01.py` is retained only
as the original pilot's rebuild recipe. `data/body_batch02.json` and
`data/batch02_tables.py` are the reviewed transcription inputs for this batch.

## Validation and earlier-page preservation

The final master was reopened in Scribus 1.6.1. All 40 pages and all 1,601 text
frames were checked for identical text, one line per frame and no overflow.
Every newly added page was rendered and visually reviewed; OCR baseline errors
and caption/table spacing defects found in the initial render were corrected.
The PDF's extracted text was checked against every native text frame, with
Unicode normalization for ligatures.

All **1,343 original page objects** preserve their text and geometry. Existing
style assignments are retained; Scribus rounds numeric font properties in seven
character styles to its saved precision (0.1 pt or 0.1% scale).
Scribus changes internal object IDs on save and drops unused invalid fill-shade
attributes on some original line objects. In PDF comparisons, 18 prior pages
render identically at 144 dpi. Reopening the baseline rounds the page 9
specification text from the earlier export's 8.25 pt to 8.3 pt, and slightly
normalizes horizontal scaling on one justified line of page 2. These serialization
effects do not change transcription, baselines or page breaks. The cumulative
PDF is exported after reopening, so it represents the saved native master.

Detailed results are recorded in `data/native_validation.json`,
`data/reopen_validation.json`, `data/pdf_validation.json` and
`data/preservation_validation.json`. These checks verify layout integrity and
retention of supplied text; they do not replace independent source proofreading.
