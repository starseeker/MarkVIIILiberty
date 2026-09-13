# Hotchkiss tank-gun handbook - Scribus reconstruction v01

A complete reconstruction of the surviving content in the two supplied Internet
Archive scans: 32 content pages, including the preliminary material, printed
pages 7-21, photographic Plates A-C, and drawing Plates I-X.

## Open the edition

1. Install the C059 OpenType fonts in `fonts/` and restart Scribus if necessary.
2. Open `Hotchkiss_Master_v01.sla` in Scribus 1.6.x or later.
3. Keep `assets/` alongside the SLA; all artwork links are relative.

`Hotchkiss_Master_v01.pdf` is the checked reading copy, with navigation bookmarks.
`Hotchkiss_Source_Review_v01.pdf` explains the source choices and shows comparisons.
The PDF and project filenames carry a version to avoid ambiguous cached downloads.

## What is editable

The title, preliminary notices, contents, body text, photograph captions, tables,
leaders, and rules are native Scribus objects: 836 text frames and 97 rules.
Tables use individual editable cell/row frames and native rules, consistent with
the earlier handbook workflow. The authoritative line transcription is retained
in `data/lines.json`; the title and table transcriptions are in the builder.

Drawings, their embedded lettering, photographs, the title seal, and the small
printer ornament remain source-pixel images. They have not been vector-traced or
redrawn. Editing a line frame is straightforward, but text does not automatically
reflow across all paragraphs/pages. Save manual changes under another name before
running the rebuilding script.

## Sources and completeness

Item: https://archive.org/details/HandbookForTheQ.F.Hotchkiss2.244Inch6Pdr.6Cwt.MarkIIGunWithTankMounting

The item describes an August 1919 US War Department publication, Document 949,
and identifies it as public domain. Its description says the first scan was
already processed with GIMP, ImageMagick, and ScanTailor.

The full download listing contains two original PDFs, each with separate OCR and
JP2 derivatives. Their source bytes were checked against Internet Archive's MD5
values. `data/source_inventory.json` retains the exact filenames, URLs, sizes,
MD5 checks, and SHA-256 hashes; `sources/ia_metadata.json` retains the item inventory.

- Primary: the 70,038,324-byte original PDF from 2018, with 28 pages. Its usual
  embedded image size is 2176 x 3357 pixels, nominally 400 dpi; Plate I is larger
  at approximately 600 dpi. The primary PDF's embedded images were extracted
  directly, avoiding another lossy derivative.
- Secondary: the 1,908,148-byte original PDF with an extra period before `.pdf`,
  added to the item on 13 September 2026. It has 34 PDF pages. Its metadata records
  an OmniPage production history from 2015-2016. Text images are mostly bilevel
  at about 300 dpi; photographic and drawing images are generally about 150 dpi.
- The item also links the Ike Skelton Combined Arms Research Library. No higher
  resolution master was obtained through that link during this investigation;
  the secondary PDF hosted in the item is the actual supplementary source used.

The primary lacks the document notice, the War Department authorization on
printed page 3, and drawing Plates II and V. The secondary supplies those four
content leaves. Its final library-barcode leaf and blank back cover are omitted
from the reading edition. Their omission is documented, not silently counted as
missing historical text. Unscanned blank leaves have not been invented.

The final order follows the secondary scan's first 32 pages. The primary supplies
all overlapping content because its diagrams are generally clearer. Every output
page has a source mapping in `data/page_inventory.json` and `data/page_inventory.csv`.
This establishes completeness relative to the two scans, not a physical collation
of an original bound copy.

## Layout and typography

Text pages use a modern 6 x 9 inch canvas, photographs and Plate I use 9 x 6 inch
landscape pages, and the larger folded drawings use 12 x 9 inch pages. Illustration
aspect ratios are preserved. These sizes are reading/layout choices, not verified
physical measurements or a claim that a diagram can be measured from the PDF.

C059 is a practical Century-style approximation; it is not an identification of
the original metal type. Printed line endings and page divisions are retained in
the prose. The source's hierarchy, paragraph labels, italic lead-ins, and table
structure are reconstructed. Three lines have minor recorded horizontal fitting;
the lowest scale is 96.89%. Tables, contents leaders, and title spacing are reset.

OCR is only a starting point. All 15 text pages were visually reviewed against
source images; 129 line corrections are recorded in `data/corrections.json`.
The contents, tabular material, and supplementary preliminary pages were also
transcribed from the scans. This is a first complete edition, not an independently
proofread critical edition.

## Artwork treatment and limits

The primary scan has already-clean white backgrounds on most drawings, so those
images retain their original sampled geometry and tones after grayscale
conversion. Plate I and the photographs receive exact quarter-turn rotations.
Photographs retain grayscale detail without binarization or tonal clipping; their
captions are separately editable. The title seal and end ornament are preserved
as raster crops.

Secondary-only Plates II and V receive local paper-background normalization and
monotonic contrast adjustment, without binary thresholding or removal of uncertain
linework. Bleed-through and some paper texture remain visible. Their relatively
low-resolution JPEG source is the principal quality limit. The project includes
both untouched source images and the treated versions for review or replacement.

No generated imagery, guessed replacement labels, deghosted geometry, nonlinear
warping, or dimensional reconstruction has been introduced. The primary source
may already contain earlier ScanTailor corrections that cannot be undone here.

`data/artwork.json` records source crops, rotations, processing operations, image
sizes, and output hashes. The image builder uses Pillow, NumPy, and SciPy.

## Readings deliberately retained

- Printed page 19: `clamp screw brushes` is retained as printed rather than
  silently changed to `bushes`.
- Printed page 12: the spare-parts reference letter for `2 brushes, sponge`
  appears as `E`; that reading and the separate `sights (D)` parenthesis are
  retained. These are candidates for later editorial comparison, not OCR repairs.
- Period wording such as `can not`, `nutted up`, and `sal soda` is not modernized.
- The fractional readings on printed page 17 are restored from the printed
  glyphs; the OCR's substitutions are not accepted as numerical evidence.

## Verification

The native file was saved and reopened in Scribus 1.6.1. All 836 text frames passed
text-overflow checks both before saving and after reopening. The final PDF was
rendered at every page, with detailed review of dense text, tables, photographs,
and the problematic plates. The editable frame strings were checked against
extracted text on their corresponding PDF pages: zero missing frame strings.
All 13 plates and both small ornaments render; all 32 page bookmarks resolve.

The PDF is exported by Scribus, then recompressed losslessly with PyMuPDF. This
retains native text, fonts, image pixels, and page geometry. No image downsampling
is used. JSON validation records are in `data/`.

## Rebuild

The delivered native file opens without running scripts. To reproduce it:

1. With Python 3 plus Pillow, NumPy, SciPy, and PyMuPDF installed, run
   `python scripts/prepare_text.py` and `python scripts/prepare_artwork.py`.
2. Install the bundled fonts. In Scribus, use Script > Execute Script and select
   `build_scribus.py`. It rebuilds the master SLA and a PDF using a temporary
   intermediate file to ensure a complete export.
3. Run `python scripts/verify_export.py` to recompress the PDF, add bookmarks,
   and render the inspection pages.

The Scribus builder compensates for its 1.6 scripter's lack of a page-size setter
by changing native page dimensions and object positions, then reopening the SLA
in Scribus for the authoritative export. This remains a real Scribus document.

The source-image files needed by these scripts are bundled. The original source
PDFs and JP2 ZIP need not be downloaded again to rebuild. Scripts rely on the
relative project structure and do not require the temporary dependency setup used
during this session. The font license is included in `fonts/LICENSE.txt`.
