# Resume the complete Mark VIII handbook

Current master: `Handbook_Master.sla`, **251 pages**, checkpoint 13.
Current PDF: **`Handbook_Master_001-251_v13.pdf`**.

All available scanned content is reconstructed: title leaf (inferred p1), printed
pages 2–251, numbered Plates 1–143 and the source's unnumbered illustrations.
There is no visible Plate 126 label on p212; no label was invented.

**No next unprocessed batch remains in the supplied repository.** All 126 scans
were accounted for. The final source, `MarkVIII126.jpg` RIGHT, is printed p251:
the final entry is **Wiring, high-tension, disassembling and inspection — 67**,
followed by an open closing circle. No additional scanned blank end leaves exist.
The leading blank in scan001 is excluded. The first full reconstruction pass is
complete; independent proofreading, font identification and trim measurement remain.

## Continue with review or refinement

1. Locate the latest user-provided or committed project and check for manual edits.
   Preserve an exact copy before editing. The user manually commits downloads to
   GitHub; no permission to push is assumed. Historical SLAs are baselines.
2. Proofread against source scans in manageable batches. Retain printed errors,
   duplicates, blank cells and references; record findings in REVIEW_NOTES.md.
   Do not silently replace printed index references with inferred corrections.
3. Continue the provisional 396 × 612 pt canvas and bundled C059 OpenType fonts
   until a deliberate typography/trim revision is agreed. Body: 9.7 pt at 92.5%
   horizontal scale; nomenclature: 6.3 pt; index: 9 pt. Preserve raster engineering
   geometry and internal labels.
4. Use unique new styles for revised material; never unintentionally redefine
   older styles. Reopen and validate all native frames before exporting. Compare
   unaffected earlier pages with the preceding release at 144 dpi.
5. Every released PDF needs a fresh page-range/version name, e.g.
   `Handbook_Master_001-251_v13r1.pdf` or v14. Update scripts, README and state
   together. Never deliver an unversioned Handbook_Master.pdf.
6. Update transcription, page/source maps, review and validation records, then
   package a uniquely named cumulative ZIP for continuation across sessions.

## Checkpoint 13 contents

15,235 native text frames and 146 linked assets. This batch adds 1,033 frames,
491 index entries and one native closing ellipse; no raster artwork is added.
The nomenclature index concludes on p241. General index spans p242–251.
P242 uses bottom folio `(242)` and no top folio. Printer signatures are native
on p241 and p249. Blank references: p242 “Brake, track”; p244 “Engine-oil
specifications.” Source anomalies and repetitions are recorded in REVIEW_NOTES.

Authoritative final-batch data: `data/index_batch13.json`; readable transcript:
`data/batch13_index_transcription.tsv`. `prepare_batch13_index.py` regenerates
these inputs and overwrites manual input edits. `build_project.py` appends from
the exact 240-page v12 baseline, so it discards subsequent manual master edits.
Use it only for a deliberate rebuild. Historical batch builders are records.

Pages 1–240 are pixel-identical to v12 at 144 dpi. All 17,216 earlier native
objects retain content, geometry and style assignments; all prior named styles
are unchanged. Only internal object IDs were regenerated. Baseline SHA-256:
`20ac6f340b8318fed954590472861375d455277f1875029f8034bde733b1ad53`.

## Source mapping and runtime

For n >= 2: scan=floor(n/2)+1; even=left (0,0,1750,2550);
odd=right (1750,0,3509,2550). Title=scan001 right. Earlier p132 needs the wider
crop (0,0,1850,2550); retain that override. Final index comparison uses nominal
halves. Draft OCR x=100 loses leading letters on some right pages; full source
images, not clipped OCR, were used for transcription. Reference-column OCR and
manual resolutions are recorded separately.

Parse TSV with csv.QUOTE_NONE. Capture Tesseract/Poppler stdout before writing
and fully load each PNG. Exclude conflicting Type 1 C059 copies. Headless Scribus
needs -platform offscreen, HANDBOOK_BATCH=1 and -py /absolute/script.py last.
Check status/error files because caught exceptions can return exit code zero.
Keep the PDF exporter local so it finalizes before exit. Both runtime library
paths end in /usr/lib/x86_64-linux-gnu and /usr/lib.

The cumulative ZIP includes the master, historical baselines, fonts, artwork,
transcripts, scripts, hashes, comparison proof and continuity records. Original
scans are recoverable from GitHub using `fetch_sources.py` and the 126-file
SHA-256 inventory. Resume from the latest ZIP or committed project if workspace
files are unavailable.
