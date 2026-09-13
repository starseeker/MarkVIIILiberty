# The Liberty 12-Cylinder Aero Engine Handbook (September 1918)

Complete first reconstruction pass, batches 01–09: **162 manual pages from
source scans 0001–0162**. All 167 staged scans are accounted for. The last
printed page is p151; scans 0161–0162 are unprinted closing cover surfaces.
Scans 0163–0167 are scanner-only exposures retained as source evidence and
excluded from the reconstructed manual.

Open `Liberty_Master_scans0001-0162_v09_20260913T182703Z.sla` in Scribus 1.6.x. Install the four OpenType fonts in `fonts/` first and keep
`assets/` beside the SLA. No scripts need to run to open or edit it. The matching
master PDF is the reading copy. The separate final comparison PDF documents all seven closing exposures: two
source/reconstruction pairs and five explicit scanner-source exclusions. Exact filenames are in `data/release.json`;
all released deliverables have unique version and UTC timestamp names.

The compact ZIP includes all released native SLAs, all 167 source JP2s, original
and cleaned artwork, fonts, reviewed data and scripts, the current master PDF
and exact v08 baseline master PDF. Comparison PDFs are separate downloads.
Older PDF exports remain in their earlier releases; explicit omissions and
file hashes are recorded in `data/release_manifest.json`.

## Source and scope

- [Internet Archive item](https://archive.org/details/liberty12cylinde00grea)
- [Staged source directory](https://github.com/starseeker/MarkVIIILiberty/tree/main/references/1918-09_12_Cylinder_Liberty_Aero_Engine/original_scans)
- Repository baseline: `4f71ced7acbde9ec51ac8ed5eafba96cdaa8eca4`.
- `data/source_inventory.json` records all 167 staged JP2s, SHA-256 hashes,
  pixel dimensions, original folios, and Archive page classifications.
- All 167 original JP2s are bundled under `sources/`. Full Archive scan
  metadata and its OCR are under `source_metadata/`; the latter is evidence for
  comparison, not an approved transcription.

Archive's headline page count is 166; its scan metadata includes scanner leaves,
five foldouts, a deleted leaf, and calibration cards. Do not infer reading order
or completeness solely from that headline count. Staged filenames 0001–0167
are present. Leaf 0000 is an Archive deletion and is absent from the repository.
Archive labels the engine frontispiece "Copyright"; this project identifies it
from the visible image instead. The final seven exposures have been visually classified: scans 0161–0162
are blank inside/back cover surfaces; 0163 shows scanner support and a narrow
book fragment; 0164–0165 are color calibration targets; 0166–0167 are white
calibration references. `data/source_disposition.json` maps every staged scan
to a manual page or an explicit exclusion. No manual printing follows p151.

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
Batch 09 adds two unprinted pages and no text or artwork objects.
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
Blank scans 0125, 0128, 0149, 0151, 0153, 0156 and 0159 and the closing
cover surfaces 0161–0162 remain blank without invented printed folios. Visible folios on all five foldouts override missing
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

All 167 staged source scans were visually inspected during the nine batches.
The two closing manual pages were rendered with Poppler and reviewed; all seven
final comparison sheets were inspected for correct source pairing, blank-page
treatment and exclusions. The earlier 160 PDF pages match v08 pixel for pixel
at 144 dpi. All 11,125 earlier native objects and 234 styles match structurally,
ignoring only regenerated ItemID values. All 384 protected baseline, source,
artwork and font files retain their released hashes.

Scribus 1.6.1 reports zero overflowing frames before saving and after reopening.
The PDF's per-page character inventories match the native frames exactly, with
no text or illustration outside a page. All 108 relative image links resolve,
fonts are embedded, and figure images use lossless compression. All 167 source
hashes match the inventory; all 108 original crops exactly match decoded source
regions. RGB Figures 24–26 preserve their red oil paths.
See `data/native_validation.json`, `data/pdf_validation.json`,
`data/baseline_v08_preservation.json`, `data/artwork_validation.json`,
`data/render_validation.json` and `data/visual_review.md`.

This is a reviewed first reconstruction pass. An independent final technical
proofread and physical trim/typeface verification remain outstanding. Apparent
source errors are preserved and documented in `REVIEW_NOTES.md`.

## Rebuild and future review

`build_project.py` runs inside Scribus and finishes this release from the exact
160-page v08 SLA. `scripts/prepare_batch09_seed.py` appends two empty page
definitions at 396 × 691 pt, preserving earlier pages, styles and objects. The
seed `_batch09_seed.sla` is an unpopulated intermediate input; open the uniquely
named released master to read or edit it. Rebuilding always starts from v08,
so it does not append duplicate closing pages. It replaces this release's
SLA/PDF; save subsequent manual edits under a new version before rebuilding.

Run `scripts/check_and_compare.py` after native export for explicit PDF labels,
bookmarks, export checks and the seven-sheet final source proof. Then run
`scripts/verify_batch09.py` for baseline preservation, all-source hashes,
original-crop comparisons, fonts, bounds, closing-page blank checks and Poppler
renders. These scripts require PyMuPDF, Pillow, NumPy, lxml and Poppler. Earlier
preparation scripts and build/layout records preserve the original process;
never rerun them against the cumulative data without isolating their inputs.
The existing native document can be edited without running scripts.

No source batch remains. An independent final technical proofread and measured
trim/typeface review are separate outstanding review tasks, not missing pages.
Read `CONTINUE_HERE.md` before further revisions. For repository integration,
place this folder at
`references/1918-09_12_Cylinder_Liberty_Aero_Engine/scribus/`.
No upstream files were changed or pushed.
