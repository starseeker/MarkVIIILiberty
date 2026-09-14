# SNL G-13 — complete supplied-page Scribus draft

This working project reconstructs **314 unique supplied photographs/leaves** of
the 1928 **Standard Nomenclature List No. G-13, Tank, Mk. VIII**. Main pages use
the agreed **6 × 9 inch** estimate. Plate 2 uses a provisional **18 × 9 inch**
foldout canvas. All Arabic folios 1–311 are now included, plus Roman I/II and the separate
foldout: 314 electronic pages. A targeted cross-book ambiguity audit is complete;
a fresh independent proofread of all pages remains pending.

## Open and review

1. Extract the entire project ZIP, retaining its folder structure.
2. Install the three C059 OpenType fonts in `fonts/`, then restart Scribus.
3. Open `SNL_G13_Pilot.sla` in Scribus 1.6.x or later. Keep `restoration/` and `assets/` beside it.
4. Review `SNL_G13_Pilot.pdf`; the fonts are embedded and its bookmarks use
   original folios. `Figure_Geometry_Proof.pdf` compares all 31 artwork assets.
5. Open `Figure_Refinement_Study.pdf` for the comparisons and all-plate geometry audit.
6. Open `Transcription_Ambiguity_Audit.pdf` for the cross-book resolutions and source comparisons.

The native document contains editable text frames, cell frames, rules and
leaders. All 275 parts tables use named cell frames rather than Scribus table
objects. Five notes pages preserve photographed line breaks in separate editable
frames. Multiline manufacturer and identification cells retain their stacking;
component-list indentations, continuation lines and price baselines are preserved.
Long cell text uses limited horizontal scaling to retain source line breaks.
Substantial rewriting may require moving frames. Figures use native SVG groups
or linked raster images; internal lettering remains traced outlines or pixels.

C059 is a Century-style approximation, not an identification of the original
metal type. Sizes and margins are estimates. Typeset pages use clean black text;
the linked figures now use clean grayscale masters. Residual blemishes and source
sampling limits remain; unmodified source-color references are preserved.
The font license is included. Neither main-page nor foldout dimensions have been
confirmed by physical measurement.

## Current figure-restoration checkpoint

All 34 plates have cleaned masters. The book now uses five pure vector SVG groups,
two hybrid SVG groups and 24 linked clean PNGs. Plate 12 is the user-approved
aggressive candidate; its earlier conservative master, keep mask and comparison
are retained in `restoration/aggressive/`. Its remaining variable slant is unchanged.

Scribus imports SVG directly through File → Import → Get Vector File. The native
book already contains the seven recommended groups. Hybrid shaded regions link
lossless tone PNGs in `restoration/native/`; keep them beside the document.
The matching PDF preserves vector artwork and uses lossless raster compression,
with downsampling disabled. No new geometric correction was applied.

Start with `Figure_Restoration_Comparisons.pdf`, `Restored_Figures.pdf` and
`FIGURE_RESTORATION.md`. `Plate12_Mirror_Study.pdf` records the earlier paired
experiment; it is historical, not a comparison of the latest aggressive master.
`DOCUMENTATION.md` provides the comprehensive README and archival provenance.

`restoration/validation.json` records this release's checks: 314 pages in order,
25,682 editable text frames, 32,625 unchanged objects outside seven replaced
artwork frames, original artwork bounds, preserved source files and lossless raster
pixels. The complete native document contains 125,890 objects, including vector
contours. All 283 non-figure pages render identically to the previous checkpoint.
Earlier audit and geometry reports below describe their respective checkpoints.

## Cross-book transcription audit

The 2026-09-12 audit closes 13 prior review entries across 10 distinct findings.
Three cells were corrected: SH40AD on 43, SH976C on 66, and the first
transmission-frame rivet length, 1⅛″, on 97. Six existing readings were
corroborated and the repeated SH599A manifold component was explained by note
(go). One new discrepancy was recorded: D22920 on 44 versus D29920 on 110.
The current log contains 113 open and 99 resolved entries; these are log entries,
including general proofreading flags, rather than a count of uncertain characters.

`Transcription_Ambiguity_Audit.pdf` contains the findings and selected source
comparisons. `TRANSCRIPTION_AUDIT.md` and `audit/ambiguity_audit.json` retain the
full evidence trail; `audit/review_before_context_audit.json` preserves the old log.
All 7,571 structured table records were indexed for cross-references. The audit
uses the full notes and selected photographs/Plate 16, and is not a new independent
proofread of every page. Original source inconsistencies remain explicitly flagged.

For scripted re-export, use the bundled C059 OpenType files. A system Type 1 font
with the same family name can have different metrics; the correction script checks
font file identity before opening the document. Current audit validation is in
`audit/context_delivery_validation.json`. Earlier geometry validation files record
the preceding figure-refinement stage.

## Page order and source reconciliation

| Scribus/PDF position | Printed label | Contents |
| --- | --- | --- |
| 1–2 | I, II | Editable front matter |
| 3 | 1 | Editable title leaf |
| 4–278 | 2–276 | Editable sideways parts tables |
| 279 | 277 | Plate 1 |
| 280 | Face p. 277 | Plate 2 foldout, provisional wide page |
| 281–298 | 278–295 | Plates 3–23 in original numbered-page order |
| 299–309 | 296–306 | Plates 24–34 |
| 310–314 | 307–311 | Editable notes and manufacturer table |

Pages 278, 282 and 283 each contain two plates. **All Plates 1–34 are now present.**
Plate 2 visibly says “Face p. 277.” It is placed after 277 in plate reading order;
physical binding placement and final print imposition remain unconfirmed.
`Foldout_Plate_2.sla` is the standalone native wide page used by the build.

The final batch added 11 unique sources, recorded in
`data/batch17_reconciliation.json`: p296–306, containing Plates 24–34.
Together with previously supplied pages, **Arabic 1–311 is now continuous**.
Batch 16 completed the parts-list section on 276.
Earlier batches are recorded in `data/batch3_reconciliation.json` through
`data/batch16_reconciliation.json`; batch 5 retains the p055(1).jpg upload
mapping to printed page 55. Page 1 visibly
contains the title “STANDARD / NOMENCLATURE LIST / No. G–13” and a printed 1.
The previous illustration batch contained six byte-identical repeat uploads,
recorded in `data/batch2_reconciliation.json`; those do not add pages.

`page_inventory.json` records source names, SHA-256 hashes, original labels and
pilot positions; `page_inventory.tsv` provides a tabular view. Upload order does
not determine book order. Arabic folios 1–311, Roman I/II and the unnumbered
foldout are tracked separately. The user-reported full-book count is 311; this
checkpoint includes all numbered folios, without equating them with the total
physical leaves. Any unnumbered blanks or further inserts need distinct identifiers.
There are no missing numbered pages in the supplied sequence.

The foldout's modern archive metadata panel is excluded from the reconstructed
print area, retained in the source JPEG and transcribed in
`data/foldout_provenance.json`. Its original caption, Plate 2 label and “Face p.
277” footer remain in the artwork. The wide canvas is an estimate, not a scale
calibration.

## Reviewed geometric correction

The lettering/open-book refinement is documented in `FIGURE_REFINEMENT.md` and
`Figure_Refinement_Study.pdf`. All 30 numbered figure pages were visually checked;
the flat-scanned Plate 2 foldout is unchanged. Six pages were refined, containing
Plates 3–4, 10–11, 24, 27, 29 and 31. The study compares the previous delivered
corrections with the new images and records a decision for every plate.

| Pages | Current correction |
| --- | --- |
| 285–291, 297, 305–306 | Individual nonlinear correction using four printed frame curves; retained |
| 293 | Paired nonlinear reference-axis fields; retained |
| 278, 283, 296, 299, 301, 303 | New text/reference-line models, with restrained complexity and reserved checks |
| 294 | Existing affine reference-axis correction; stronger trial rejected |
| 277, 279–281, 284, 292, 295, 298, 300, 302, 304 | Existing caption deskew retained |
| 282 | Existing crop retained; stronger trial worsened a reserved caption |
| Plate 2 foldout | Existing flat-scan crop and native placement retained |

An automatic rule survey of all 275 table pages yields 261 accepted models.
The changing parity trend guides local fits; it does not define a single global
odd/even warp. Selected same-parity neighbors contribute a weak prior where
supported by the figure model. The foldout is excluded from this process.

The source-versus-current `Figure_Geometry_Proof.pdf` covers all 31 assets.
Red overlays identify fitted observations; blue observations on the six refined
pages were withheld for validation. Full source-pixel controls, coefficients,
per-group checks and rejected trials are in `calibration/`. Prior corrected
assets for the six changed pages are also retained there.

No linework or lettering is generated. Original JPEGs remain unchanged in
`sources/`; corrected assets are PNG. Interior geometry and original physical
aspect ratios remain uncertain. Angled components, isometric armor and splayed
control rods retain their intended perspective. See the plate-by-plate audit
for residual distortion and limited-reference cases.

## Transcription and review

Structured text is in `data/parts_tables.py`, `data/opening_tables.py`,
`data/tables_025_044.py`, `data/tables_045_064.py`, `data/tables_065_084.py`,
`data/tables_085_104.py`, `data/tables_105_124.py`, `data/tables_125_144.py`,
`data/tables_145_164.py`, `data/tables_165_184.py`, `data/tables_185_204.py`,
`data/tables_205_224.py`, `data/tables_225_244.py`, `data/tables_245_264.py`,
`data/tables_265_276.py` and `data/notes.py`. `review.json`
lists doubtful readings and resolved cross-page evidence. Independent proofreading
is still needed, particularly for part numbers, fractions, quantities and prices.

- Front-matter `(gam)` is supported by the matching note on 310 about a future
  spare-parts and accessories set.
- The major-item symbol's function is confirmed on 307; `ø` remains a glyph
  approximation.
- Damaged cover wording and page II's clipped initial S were restored from
  surviving text and repeated forms. Damaged Plate 34 “Assembled” was restored;
  Plate 24 remains “Assembled” without an added “view.”
- Period wording is preserved, including “Distributer,” “Thrackray,” and the
  apparent “ANFLE” on 3. The p287 printer imprint visibly reads “53476—23——19”
  and is retained as printed, despite the catalog's 1928 date.
- In the new tables, apparent “OLT” on 32 and the printed price “.672 P” on
  40 are retained and flagged. The camp-kettle bracket price on 37 needs a
  clearer reading. Stacked identification and plate numbers on 41 and 43
  are centered beside their shared item rows.
- Cable assemblies on 45–50 retain their individual numbers, prices and original
  continuation breaks. The apparent L12339 and L3308 codes on 48 and LQ328A
  spark-plug terminal on 46 are preserved as printed and recorded for review.
  The LQ196A stud length differs between 58 and 59 in the photographs.
- Pages 65–84 retain assemblies across their original page breaks. Blank quantities
  on 66 and a blank price on 73 remain blank. The collar descriptions on 67 and
  79 disagree; both readings are preserved. Small uncertain codes are recorded
  in `review.json`. The page 79 printer imprint is editable.
- Pages 85–104 retain the original engine, fan and exhaust-guard continuation
  breaks. Blank fuze and gage-glass cells remain blank. The elbow listing on 85
  corroborates the earlier Q51QC reading. NBIB on 93 remains flagged. The first rivet length
  on 97 is now resolved as 1⅛″ in the cross-book audit. The page 95 printer imprint is editable.
- Pages 105–124 retain the camshaft, generator, lever and lubricator assemblies
  across their original page breaks. Page 105 corroborates GB5G on 104 and the
  LQ196A length on 58; the conflicting length on 59 is preserved. The individual
  hook on 107 reads NB1B. Apparent quantity, length and code inconsistencies are
  recorded in `review.json`. The page 111 printer imprint is editable.
- Pages 125–144 retain the nut, packing-piece and pin assemblies across their
  original page breaks. The long nut references on 128 finish on 129; the split-pin
  entry on 140 finishes on 141. Blank cells and apparent quantity discrepancies
  are preserved. Small uncertain fractions and source wording are recorded in
  `review.json`. Pages 127 and 143 have editable printer imprints.
- Pages 145–164 retain the plate lists and pump assemblies. The oil pump crosses
  159–160, water pump 160–161, and radiator 161–162. Duplicate source entries,
  blank cells and apparent source wording are preserved and recorded in
  `review.json`. Page 159 has an editable printer imprint.
- Pages 165–184 retain the ring and rivet listings, including reference lists that
  span several pages. Quantities and prices remain on the terminating printed
  lines. Apparent code and quantity inconsistencies are retained in the text and
  recorded in `review.json`. Page 175 has an editable printer imprint. The last
  rivet entry is completed in the next batch on page 185.
- Pages 185–204 complete the earlier rivet lists and continue through rods,
  rollers, screens and screws. Blank quantity and price cells remain blank.
  Apparent code and quantity inconsistencies, the faint sponson-roller price
  on 197, and a faint letter in SH81H on 203 are recorded in `review.json`.
  Page 191 has an editable printer imprint.
- Pages 205–224 retain screws, seat and shaft assemblies, shims, springs and
  ammunition-storage lists. Grouped alternatives and multirow references remain
  editable. Source inconsistencies and blank prices are recorded in `review.json`.
  Pages 207 and 223 have editable printer imprints. The platform ammunition-storage
  assembly begins on 223 and finishes on 225.
- Pages 225–244 retain storage, strainer, strap, strip, strut, stud and switch
  listings. Grouped quantities and stacked references remain editable. Blank
  cells and conflicting source dimensions are retained and recorded for review.
  Page 239 has an editable printer imprint. The engine-oil-tank assembly starts
  on 244 and finishes on 245.
- Pages 245–264 retain tank, transmission, tube, tubing and turret lists. The
  transmission assembly spans 251–254 and the high-tension cable list spans
  260–261. Page 255 has an editable printer imprint. Blank price cells and
  apparent source inconsistencies remain in place and are recorded for review.
  Page 264 closes its final unilet entry; no assembly is left open by this batch.
- Pages 265–276 complete the unilet, union, unit, valve, washer, wheel, wire,
  worm and yoke entries. Long washer references keep their original line and
  page breaks. Grouped references on 273–275 use editable numbers and vector
  brace approximations. The page 271 printer imprint and page 276 closing
  notice are editable. The parts list ends on 276, followed by Plate 1 on 277.
- Dashes, fractions, quotes, small capitals and leader spacing are approximations.
  Handwriting, tears and external archival cards are excluded from typeset pages.

## Continue and rebuild

All numbered source pages are supplied and assembled. The next work is independent
proofreading and review of remaining drawing distortion. No repeat upload is
needed. Keep this ZIP and inventory as the checkpoint when continuing work.

Opening the SLA requires no rebuild. This checkpoint inserted the final figures
into the saved master with `insert_figure_batch.py`; the prior pages were checked
for preserved text, geometry and page-relative positions. That guarded script
requires `SNL_FIRST` and `SNL_LAST` and refuses duplicate insertion. The complete
rebuild route below remains available independently. To regenerate:

1. Run `python3 prepare_assets.py` with Pillow, NumPy and SciPy available.
   Use `--inventory-only` when only text sources or the reading sequence changed.
2. Run `python3 validate_geometry.py` to record the output-border checks.
3. In Scribus, choose Script → Execute Script and select `build_project.py`.
   This writes the master SLA/PDF and the standalone foldout SLA.
4. Run `python3 make_proofs.py` with Pillow, PyMuPDF and ReportLab to add PDF
   navigation and regenerate comparison proofs and page renders. Use
   `--pilot-only` to retain the existing geometry comparison PDF.
5. Optionally execute `check_reopened.py` inside Scribus to verify the saved file.

Rebuilding overwrites generated files. Save manual Scribus changes under a
separate name before rebuilding. `validation.json`, `reopen-validation.json` and
`pdf-validation.json` record the checks. The current build includes 314 native pages. Frame counts and overflow checks are
recorded in `build-status.txt` and `delivery-validation.json`. The complete PDF was
rendered for visual review, including the 11 new figure pages. The geometry
comparison PDF now contains all 31 artwork assets. Reproducible page-render intermediates are
omitted from the ZIP to keep it compact.

## Distribution note

The large `Figure_Restoration_Comparisons.pdf` is a separate companion download;
it is omitted from the project ZIP to keep the package manageable. The complete
book PDF, editable Scribus document, all source images and restored masters remain
in the project ZIP. Place the comparison PDF beside the main document if desired.
