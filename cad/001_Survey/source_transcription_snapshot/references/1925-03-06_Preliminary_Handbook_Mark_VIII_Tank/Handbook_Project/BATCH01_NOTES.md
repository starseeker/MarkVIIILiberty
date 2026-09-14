# Preliminary Handbook of the Mark VIII Tank: batch 01

This is a clean, editable Scribus feasibility pilot of the title leaf and printed
pages 2–20, including Plates 1–11. The title leaf is treated as inferred page 1;
its unprinted number has not been added to the reconstructed page. The blank
left side of scan 001 is excluded. This is a modern research reconstruction,
not an official corrected edition or a completed transcription of the book.

The source is **No. 1977, Preliminary Handbook of the Mark VIII Tank**, dated
November 15, 1918, **reprinted March 6, 1925**, as printed on the title page.

## Open and review

1. Extract the complete `Handbook_Project` directory.
2. Install the three bundled C059 OpenType fonts and restart Scribus. If the
   same family is already installed as Type 1, ensure Scribus uses the bundled
   `.otf` versions: the older files can have different metrics.
3. Open `Handbook_Pilot_001-020_v1.sla` with Scribus 1.6.x or later. Keep `assets/`
   beside it. Opening the document needs neither the source scans nor a rebuild.
4. Review `Handbook_Pilot_001-020_v1.pdf`. Its fonts are embedded. The separate
   `Handbook_Comparison_001-020_v1.pdf` gives the assessment, font specimens,
   and a source/reconstruction comparison for every pilot page.
5. Read `REVIEW_NOTES.md` before treating transcribed quantities as technical data.

## What the pilot demonstrates

A clean Scribus edition is feasible. The main text blocks are generally flat,
readable, and well separated from the worst gutter damage. Typesetting removes
paper discoloration and text curvature directly. The contents and plate lists
need explicit transcription: automatic OCR frequently reads their dashed leaders
as false words, despite the text being quite readable to a person.

The native document contains **1,059 editable text frames**, editable list and
table entries, vector rules/leaders, and 12 linked grayscale artwork assets
(11 plates plus the title seal). Individual prose lines retain source line and
page breaks. Large textual revisions can require moving neighboring frames;
this is a faithful layout reconstruction, not a continuously reflowing e-book.

The illustrations are cropped from original pixels and normalized against a
smooth estimate of the paper illumination. Line drawings use a stronger white
point; shaded illustrations keep a broader grayscale range. Original halftone
patterns, interior lettering, leaders and shading remain raster. No generated
imagery, inpainting, sharpening, tracing or invented mechanical geometry is used.
External captions are typeset; lettering inside illustrations remains pixels.

**This checkpoint applies no illustration rotation or nonlinear dewarping.**
The geometry survey measures text tilt; it does not prove the correct transform
for the neighboring artwork. Some residual tilt, paper texture and print/scan
blemishes remain, particularly around shaded plates. Angled lines in mechanical
perspective drawings have not been forced horizontal or vertical.

## Typography and page size

The working canvas is **5.5 × 8.5 inches**, chosen as a convenient approximation
to the single-page scan proportions. The original trim has not been measured.
The 300-dpi JPEG metadata describes the scan canvas, which includes gutter and
opposite-page material; it does not establish the original leaf dimensions.
This project does not inherit the SNL project's provisional 6 × 9 inch size.

C059 is a **provisional Century-style approximation**, not an identification of
the historical metal type. It was compared independently with Nimbus Roman on
handbook prose. Both are plausible approximations; C059 tracked relative word
widths somewhat better in the small sample, while requiring modest horizontal
compression to balance the observed glyph height and width. The body pilot uses
9.7-point C059 with approximately 92.5% horizontal scale. Small capitals, some
spacing, leader patterns and display proportions remain approximations.

A robust word-baseline survey on pages 11–20 found median prose tilt ranging
from roughly -0.24° to +0.98° in image coordinates. Pages 18–19 are among the
more visibly tilted samples. These are OCR-derived observations on readable
words, not a camera calibration or a bound on the remaining binding distortion.
The full observations are in `data/text_geometry_survey.json`.

## Scope and provenance

Sources live in the existing repository directory:

https://github.com/starseeker/MarkVIIILiberty/tree/main/references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank

The pilot uses `MarkVIII001.jpg` through `MarkVIII011.jpg`. These are **spreads**,
not single pages: p2 is scan 002 left, p3 is scan 002 right, and so on. Only the
left/page 20 half of scan 011 is used in this checkpoint. The repository listing
contains 126 JPEGs; the later pages have not been comprehensively inventoried.
Twenty scan files were fetched in the bounded initial download; only the first
eleven were needed for this twenty-book-page reconstruction.

The SNL project was consulted for its editable-frame workflow, provenance and
review practices, and separation of illustration geometry from cleanup:

https://github.com/starseeker/MarkVIIILiberty/tree/main/references/1928-03-30_SNL_G13/SNL_G13_Project

`data/source_inventory.json` records the exact SHA-256 and byte length of each
used original. `data/assets.json` records crop rectangles, cleanup settings,
label exclusions and output hashes. Coordinates refer to a page split at source
spread x=1750. Original JPEGs are unchanged and are not duplicated in this ZIP.
The source-versus-pilot comparison is for visual review, not physical scale
measurement or pixel registration.

## Repository placement and rebuild

Place this directory at:

`references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/`

The original JPEGs already belong in its parent directory. There is no change
to the repository's top-level README or existing SNL project.

1. Optional: run `python3 fetch_sources.py` if the eleven source JPEGs are absent.
   It fetches one file at a time, checks its recorded size and SHA-256, and saves
   a checkpoint after each complete transfer. It refuses to overwrite a differing
   existing source.
2. Run `python3 prepare_assets.py`. It needs Pillow, NumPy and SciPy. Use
   `--source-dir /path/to/scans` when the scans are elsewhere.
3. Inside Scribus, execute `build_project.py`. This overwrites the named pilot
   SLA/PDF. Save any manual Scribus work under a separate name before rebuilding.
   Use the bundled OpenType font files; `check_project.py` records actual font paths.
4. Inside Scribus, execute `check_project.py` to reopen and check the saved file.
5. Run `python3 make_comparison.py --source-dir /path/to/scans` with Pillow,
   PyMuPDF and ReportLab to reproduce the comparison proof. Font-comparison
   specimens use the included bitmap from the inspected candidates.

The final SLA was reopened in Scribus 1.6.1: all 20 pages and all 1,059 text frames
survived with identical text, one line per frame and no overflow. The PDF uses
embedded OpenType-derived Type 0 fonts. Every final page was rendered and visually
reviewed. This is an initial transcription/layout pass; independent proofreading,
font selection and dimensional confirmation remain pending.

## Next batch

Continue with printed pages **21–40**: scan 011 right through scan 021 left.
Retain the current checkpoint and append pages by printed folio, not upload order.
Keep each iteration to roughly twenty book pages, fetch only missing scans, and
save the native document and PDF before moving to the next batch. Later foldouts,
dense diagrams or differently distorted pages should be assessed when reached.
