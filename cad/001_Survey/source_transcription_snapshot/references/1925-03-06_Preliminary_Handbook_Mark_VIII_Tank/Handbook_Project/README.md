# Preliminary Handbook of the Mark VIII Tank — checkpoint 13

The cumulative native Scribus master contains **251 pages**, completing all
available scanned content: the title leaf (inferred page 1) and printed pages
2–251. This iteration adds eleven index pages, 241–251, with 491 entries.
The first reconstruction pass is complete; independent proofreading remains open.

## Open and review

- `Handbook_Master.sla` — current 251-page native document.
- `Handbook_Master_001-251_v13.pdf` — cumulative PDF from the reopened master.
- `Handbook_Comparison_241-251_v13.pdf` — cover and eleven source/reconstruction pairs.
- `CONTINUE_HERE.md`, `PROJECT_STATUS.json` — review and continuation state.
- `REVIEW_NOTES.md` — source readings, retained printing errors and review questions.

Install the three bundled C059 OpenType fonts before opening in Scribus 1.6.x.
Disable conflicting Type 1 copies, whose metrics alter layout. Keep `assets/`
beside the SLA; all 146 image links are relative and included. C059 remains a
provisional Century approximation; physical trim is unmeasured. Working canvas:
396 × 612 pt (5.5 × 8.5 inches).

## Content and source treatment

The master has 15,235 native text frames, including 1,033 added here. The final
index uses 9 pt C059 Roman. Entries, references, letter headings, folios,
printer signatures and leaders are editable Scribus objects. The open closing
circle on p251 is a native ellipse. No new raster artwork was needed.

Repeated index entries, inconsistent references and unusual wording remain as
printed. “Brake, track” on p242 and “Engine-oil specifications” on p244 retain
their empty reference columns. No corrective page references were invented.

Earlier illustrations retain their cleaned original raster detail and internal
labels. Paper normalization reduces discoloration; residual texture and binding
curvature can remain. Existing crop/mask records are in `data/assets.json`.
No new figure redrawing or nonlinear warp is applied in this batch.

Text baselines are straightened separately from illustration geometry. Final
index text was transcribed from full source halves. Draft OCR can clip initial
letters on right pages and is retained as a draft aid only. Separate reference
OCR agreed with 444 printed values; the other 45 values and two blank references
were confirmed directly from the scans. See `data/source_reference_validation.json`.

## Verification

The master was reopened in Scribus 1.6.1. All 15,235 native text frames pass exact
text, single-line and overflow checks. All eleven new pages were rendered with
Poppler and visually reviewed. Expected text is present in PDF extraction,
fonts are embedded, and all 146 artwork hashes and portable links are valid.

Pages 1–240 are pixel-identical to v12 at 144 dpi. All 17,216 earlier page objects
retain content, geometry and style assignments, and all earlier named styles are
unchanged. Only internal object IDs were regenerated on save. See
`data/*validation.json` and `data/visual_review.md` for the recorded checks.

## Rebuild this batch

Authoritative native index input: `data/index_batch13.json`. Readable transcript:
`data/batch13_index_transcription.tsv`. Layout: `layout_batch13.py`.
All artwork is bundled; original scans are unnecessary to rebuild the SLA.

1. Preserve manual edits. `build_project.py` opens the exact
   `Handbook_Checkpoint_001-240_v12.sla`; it cannot discover later manual changes.
2. Run `build_project.py` inside Scribus to append 241–251 and save the master.
3. Run `check_project.py` inside Scribus to reopen, validate and export v13.
4. Run `python verify_preservation.py` and `python verify_pdf.py` outside Scribus.
   Supply `--previous-pdf PATH` to compare the first 240 pages with v12.
5. Run `python render_batch13.py` and inspect all eleven new-page PNGs.
6. Run `python make_comparison.py --source-dir /path/to/scans`, then
   `python verify_comparison.py`, to reproduce and check the comparison proof.

`prepare_batch13_index.py` reproduces the explicit source-checked transcription.
Running it replaces manual edits to these inputs. `fetch_sources.py` retrieves
the 126 hash-pinned spreads sequentially and resumably. Scans are not duplicated
in the ZIP. Historical builders and preparation tools are preserved as records;
they are not the entry point for revising the current master.

Headless Scribus requires explicit -platform offscreen, HANDBOOK_BATCH=1, an
OpenType-only font configuration and -py /absolute/script.py last. Inspect
status/error files: caught exceptions can return exit status zero. Keep the PDF
exporter local so it finalizes before exit. Preparation/review tools use Pillow,
NumPy, SciPy, PyMuPDF, ReportLab and Poppler. Comparison PDFs embed DejaVu Sans.

## Versioning and further work

Current PDF: `Handbook_Master_001-251_v13.pdf`. Every revised proof needs a fresh
suffix such as v13r1 or v14. Never release a generic Handbook_Master.pdf.

The last available scan, MarkVIII126.jpg right, ends at printed p251 after the
final W index entry and closing circle. There is no further scanned batch and no
blank end leaf to add. Further sessions can proofread or refine the complete
document, identify the original typeface and measure physical trim. Preserve
the latest cumulative ZIP and any subsequent manual edits. The user manually
commits downloads to GitHub; no repository changes have been pushed.
