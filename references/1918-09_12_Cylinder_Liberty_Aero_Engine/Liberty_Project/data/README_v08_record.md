# The Liberty 12-Cylinder Aero Engine Handbook (September 1918)

Editable Scribus reconstruction, batches 01–08: **source scans 0001–0160**.
This 160-page checkpoint reaches printed p151. Batch 08 adds scans 0141–0160:
printed pp137–151, five blank leaves, the two-page fits-and-clearances table,
Figures 97–107, and four appendix foldouts.

Open `Liberty_Master_scans0001-0160_v08_20260913T175934Z.sla` in Scribus 1.6.x. Install the four OpenType fonts in `fonts/` first and keep
`assets/` beside the SLA. No scripts need to run to open or edit it. The matching
master PDF is the reading copy. The separate comparison PDF pairs each new
source scan with its reconstruction. Exact filenames are in `data/release.json`;
all released deliverables have unique version and UTC timestamp names.

The compact ZIP includes all released native SLAs, all 160 source JP2s, original
and cleaned artwork, fonts, reviewed data and scripts, the current master PDF
and exact v07 baseline master PDF. Comparison PDFs are separate downloads.
Older PDF exports remain in their earlier releases; explicit omissions and
file hashes are recorded in `data/release_manifest.json`.

## Source and scope

- [Internet Archive item](https://archive.org/details/liberty12cylinde00grea)
- [Staged source directory](https://github.com/starseeker/MarkVIIILiberty/tree/main/references/1918-09_12_Cylinder_Liberty_Aero_Engine/original_scans)
- Repository baseline: `4f71ced7acbde9ec51ac8ed5eafba96cdaa8eca4`.
- `data/source_inventory.json` records all 167 staged JP2s, SHA-256 hashes,
  pixel dimensions, original folios, and Archive page classifications.
- The first 160 original JP2s are bundled under `sources/`. Full Archive scan
  metadata and its OCR are under `source_metadata/`; the latter is evidence for
  comparison, not an approved transcription.

Archive's headline page count is 166; its scan metadata includes scanner leaves,
five foldouts, a deleted leaf, and calibration cards. Do not infer reading order
or completeness solely from that headline count. Staged filenames 0001–0167
are present. Leaf 0000 is an Archive deletion and is absent from the repository.
Archive labels the engine frontispiece "Copyright"; this project identifies it
from the visible image instead. Later scanner-only material must be accounted
for separately from reconstructed manual pages.

## Reconstruction standard

The workflow follows the completed Mark VIII Preliminary Handbook project:
reviewed text in structured data, retained source line breaks, native text frames,
rules, leaders and fractions, original-pixel artwork, explicit scan mapping,
and native save/reopen, text, image-link and visual checks.

The cumulative master contains **4,858 editable text frames**, 53 straight rules,
native dot leaders, 102 structured illustration-index entries, and 108 linked
illustrations (Figures 1–107 plus 34a). Batch 08 adds 330 text frames, eleven
figures, 32 structured clearance-table rows, one stacked fraction and a native
double heading rule. Minimum, maximum and desired columns, captions, dates,
headings and prose are editable. Blank table cells and apparent printed errors
remain unchanged. Internal drawing labels retain the original pixels.
Text is editable line by line; this layout preserves source placement rather
than paragraph reflow. Numeric fractions have separate numerator, denominator
and rule objects. Local italics and selected small baseline digits retain their
source treatment.

Ordinary pages use a provisional **396 × 691 pt** canvas. The p123 and p145
foldouts use **612 × 691 pt**; the p146, p147 and p151 foldouts use **792 × 691 pt**.
Original drawing geometry is uniformly scaled on each canvas. These are working
dimensions, not measured original trim sizes. C059 Roman, Bold and Italic and
Nimbus Sans Bold remain provisional typeface substitutes. Body type is 10.8 pt;
index type is 10 pt; batch-08 numeric table cells are 9.4 pt. Physical trim and
font identification remain open.
Library labels, stamps, handwriting and paper discoloration are omitted from
reconstructed print; their evidence remains in the original JP2s and comparisons.
Blank scans 0125, 0128, 0149, 0151, 0153, 0156 and 0159 remain blank without
invented printed folios. Visible folios on all five foldouts override missing
Archive folio metadata; the explicit map is recorded in source inventory and
batch transcription data.

Artwork uses the handbook's robust quadratic paper-background estimate, followed
by conservative white-point adjustment. Batch-01 values remain unchanged.
Batch 02 uses 246 for photographs and 224–240 for monochrome line drawings;
faint circles and dotted lines retain a gentler adjustment. Figures 24–26 use
per-channel paper estimates and RGB output, retaining the red oil paths.
Batch 03 uses 246 for halftones and 228–236 for line drawings. In Figure 47,
a documented rectangle removes only the printed caption from the cleaned crop
because the lower B label shares its vertical range; that caption is native text.
The unaltered original crop preserves the complete source region.
Batch 04 uses 246 for halftones and 234 for line drawings; all seventeen new
illustrations retain their original geometry, including sideways Figures 53–54.
Batch 05 uses 246 for halftones and 234–240 for line drawings. Figure 72 retains
its printed sideways orientation. Figure 73 has a documented caption-only
exclusion, preserving the adjoining compass instruction and the unaltered crop.
Batch 06 uses 246 for photographs and 234–240 for line drawings. Figure 75
retains its sideways orientation and is uniformly reduced to fit its wider scan
on the unchanged page. Figure 88 has a caption-only exclusion that preserves
the adjacent Dowel / Dowel hole labels and their leaders. Figure 81's separate
explanatory legend is native text with small baseline numerals.
Batch 07 uses 246 for the photograph and 236–240 for line drawings. Figure 93
is uniformly scaled on a wider page; its internal labels, fine sections, shaft
outlines and fold evidence remain source pixels. No new caption masks are used.
Batch 08 uses 236–242 for its eleven line drawings. Figure 101 has a documented
caption-only exclusion preserving the adjacent modification label and diagonal
leader. Figures 102 and 107 have documented exclusions of unprinted paper-edge
strips, preserving engineering ink and unaltered original crops. All four new
foldouts keep their complete dimensions and labels; there
is no geometric rectification or reconstruction of missing detail.
There is no binarization, sharpening, vector tracing, generated detail, rotation,
shear, or nonlinear warp. Original and cleaned crops are both included; exact
crop boxes and hashes are in `data/artwork.json`. Fine hatching and halftones
remain source pixels. Some print grain, worn borders and damage survive; they
have not been replaced with inferred engineering detail.

## Validation and review

All 160 source scans were visually inspected during the eight batches. All 20
new output pages were rendered with Poppler and reviewed, with detailed checks
of the clearance-table values and column alignment, source anomalies, captions,
blank leaves and foldout dimensions. The earlier 140 PDF pages match v07 pixel
for pixel at 144 dpi. Their 10,364 native objects and 200 earlier styles match
structurally, ignoring only regenerated ItemID values. All 342 protected baseline,
source, artwork and font files retain their released hashes.

Scribus 1.6.1 reports zero overflowing frames before saving and after reopening.
The PDF's per-page character inventories match the native frames exactly, with
no text or illustration outside a page. All 108 relative image links resolve,
fonts are embedded, and figure images use lossless compression. All 160 source
hashes match the inventory; all 108 original crops exactly match decoded source
regions. RGB Figures 24–26 preserve their red oil paths.
See `data/native_validation.json`, `data/pdf_validation.json`,
`data/baseline_v07_preservation.json`, `data/artwork_validation.json`,
`data/render_validation.json` and `data/visual_review.md`.

This is a reviewed first reconstruction pass. An independent final technical
proofread and physical trim/typeface verification remain outstanding. Apparent
source errors are preserved and documented in `REVIEW_NOTES.md`.

## Rebuild and continuation

`build_project.py` runs within Scribus and rebuilds this checkpoint from the
preserved 140-page v07 SLA, reviewed batch-08 JSON and bundled artwork. It
regenerates `_batch08_seed.sla` with `scripts/prepare_batch08_seed.py`, appending
empty page definitions and setting new foldout widths without changing earlier
pages or objects. The seed is an intermediate input, not a released reading copy.
The builder verifies actual dimensions with `getPageNSize`. It always starts
from v07, so rerunning does not append duplicate pages. It replaces the current
checkpoint's SLA/PDF; save manual edits separately before rebuilding.

`scripts/check_and_compare.py` validates the export, applies explicit folio
labels and bookmarks, and generates the comparison proof. It requires PyMuPDF,
Pillow and lxml. `scripts/verify_batch08.py` records preservation, source-pixel,
font, bounds and Poppler checks. Preparation scripts use Pillow, NumPy, fontTools
and Tesseract; they are provenance records and are not required to edit the
native document. Historical batch-01 through batch-07 scripts are records only;
do not run them against cumulative JSON. Current preparation is in
`prepare_batch08_*`; reviewed transcription and placements are in
`scripts/author_batch08.py`.

Seven staged scans remain: 0161–0167. Their closing leaves and scanner-only
material require final visual classification before completing the manual.
Read `CONTINUE_HERE.md` before that final batch.
For repository integration, place this folder at
`references/1918-09_12_Cylinder_Liberty_Aero_Engine/scribus/`.
No upstream files were changed or pushed.
