# Continue the Liberty engine manual

Batch 08 is complete: **160 cumulative pages**, source scans 0001–0160, through
printed p151. The next and final source batch is **scans 0161–0167**. No scan
after 0160 has been reconstructed. Exact filenames are in `data/release.json`.

The last reconstructed page is the longitudinal-section foldout, Fig. 107,
captioned **General Arrangement (Longitudinal Section).** The last prose is the
Zenith-control adjustment on p142, ending **back.** Appendix drawings follow it.
Do not assume more prose follows scan 0160.

**Explicit scan-to-folio mapping is mandatory.** The current final batch maps:

| Scan | Visible folio / treatment |
| --- | --- |
| 0141–0148 | 137–144 |
| 0149 | Blank leaf |
| 0150 | 145; 612 × 691 pt foldout |
| 0151 | Blank leaf |
| 0152 | 146; 792 × 691 pt foldout |
| 0153 | Blank leaf |
| 0154 | 147; 792 × 691 pt foldout |
| 0155 | 148 |
| 0156 | Blank leaf |
| 0157 | 149 |
| 0158 | 150 |
| 0159 | Blank leaf |
| 0160 | 151; 792 × 691 pt foldout |

The earlier foldout, scan 0126 / p123, is 612 × 691 pt; earlier blank leaves
0125 and 0128 remain in sequence. All page dimensions are provisional working
sizes. Original diagrams are uniformly scaled and not geometrically corrected.

For the final seven files, Archive metadata records:

| Scan | Archive type | Included by Archive | Pixels |
| --- | --- | --- | --- |
| 0161 | Normal; unrecorded folio | Yes | 1893 × 3303 |
| 0162 | Cover | Yes | 2028 × 3339 |
| 0163 | Delete | No | 2912 × 4368 |
| 0164–0165 | Color Card | No | 2912 × 4368 |
| 0166–0167 | White Card | No | 2912 × 4368 |

These are metadata observations, not completed visual classifications. Inspect
all seven scans. Account for closing manual leaves and scanner-only material
separately; calibration cards should not become reconstructed manual pages.
Keep the original source evidence and explicit exclusion/classification records.
Do not infer a folio or simply append every remaining file as a book page.

1. Locate the latest project ZIP or committed Scribus project, and check for user
   edits. Preserve the exact released SLA and PDF before editing. Do not push
   upstream or replace manual work implicitly.
2. Use the source hashes and repository commit in `data/source_inventory.json`.
   Fetch only the next 20 scans. Do not apply an ordinary-page folio formula to
   later foldouts: use Archive metadata and the visible scan itself.
3. Preserve existing typography and layout unless explicitly revising them.
   Append new pages using new style names. Keep original engineering geometry
   and internal labels; apply distortion corrections only when supported by
   intended printed reference lines, never by parity assumptions.
4. Review technical numbers, fractions and references against full source images.
   Retain printed errors and blank values, and add findings to REVIEW_NOTES.md.
5. Use a new release version and timestamp for every delivered master PDF, SLA,
   comparison proof and project ZIP. Never release an unversioned master PDF.
   Keep a cumulative master and a comparison proof for the newly processed pages.
6. Reopen in Scribus, check all frames, fonts and image links; export and inspect
   all new pages. Compare unchanged earlier pages against this release's exact
   PDF rendering and preserve earlier styles, objects and artwork hashes.
7. Update state, source maps, reviewed text, artwork manifests and validation
   records, then package the cumulative project for the next session.

For the final batch, preserve the exact v08 release and snapshot current data
under `baseline_v08_*.json`. Append any actual closing manual leaves to its
160-page native master with new style names. Never rebuild earlier pages from
OCR or rerun historical preparation scripts against cumulative JSON. The current
builder starts from v07's 140-page baseline and reads `batch08_transcription.json`
and `batch08_artwork.json` for the newest twenty scans. Preserve all released
batch-specific data and historical build/layout records.

Scribus 1.6.1's scripter cannot resize an individual page. The seed script uses
standard-library ElementTree to append empty PAGE definitions and assign each
new foldout's PAGEWIDTH. It preserves earlier page definitions, objects and
styles. Use `getPageNSize(page)` to check actual dimensions; `getPageSize()`
returns document defaults. `_batch08_seed.sla` is an unpopulated intermediate;
open the uniquely named released master when editing. The current seed uses a
constant 691 pt page height and 731 pt vertical page pitch.

The native helpers support explicit per-line alignment, bold prefixes, local
italics, small baseline digits, positioned/rotated captions, explanatory legends,
stacked fractions and formulas. Batch 08 adds `clearance_tables`: independent
label/minimum/maximum/desired cells with native dotted leaders. Table cells are
9.4 pt, with a 45-source-pixel row pitch. Two split bold headings use a 54-pixel
pitch to avoid crowding. Their following rows shift by nine pixels. Do not
silently supply the missing decimal in p140's `00125`, reconcile table values
with prose, or correct period anomalies. Consult `REVIEW_NOTES.md`.

Figure 34a has a string identifier; derive original-asset filenames from `asset`.
Figures 47, 73, 88 and 101 have distinct caption-only masks. Figure 101's mask
is **[489, 1332, 761, 1430]**, retaining the diagonal leader and Mod. No. D859 /
DRG. No. A.B. 4313 label. Other new appendix drawings need no caption mask. Figures 102 and 107 also
have `excluded_background_rectangles` for unprinted photographed paper-edge
strips; the source edge beside the propeller remains where engineering ink
approaches it. Preserve these independent background exclusions.
Figure 101 is uniformly scaled at 0.43 pt per source pixel; Figures 102, 103 and
107 at 0.42. The complete originals and cleaned crops are bundled.

All engineering geometry and internal labels remain original pixels. Figures
53, 54, 72 and 75 retain printed sideways orientations; Figure 75's maximum
image width is 386 pt. Figure 93 retains its explicit 0.38 scale on the p123
foldout. Figures 24–26 require RGB and their color preparation path. Do not
replace earlier cleaned assets when finishing the book.

The apparent misplaced p96 line supplies a possible missing transition after
p105's `The hub may now`. It remains only on p96, where printed; do not relocate
or duplicate it. This is documented as an editorial inference, not a correction.

PDF folio labels and bookmarks are deterministic post-export additions from
`scripts/check_and_compare.py`; the visible content is Scribus-exported. Rebuild
and export, then run comparison and final verification in that order. The native
exporter validates every recorded line frame before saving and after reopening.
For rotated captions, call `moveObjectAbs` after `setRotation`. For PNG/Poppler
results, serialize to a byte buffer/stdout, fully decode, then write complete
bytes; this avoids intermittent truncated image files seen in this environment.

For headless Scribus 1.6.x, use fontconfig selecting bundled OpenType fonts
without conflicting Type 1 versions, `-platform offscreen`, `LIBERTY_BATCH=1`,
and `-py /absolute/path/build_project.py` last. Inspect build success/error files;
a caught script error can still return exit code zero. Let PDF export finish.

The compact ZIP retains all native documents, source scans, artwork, fonts,
reviewed data and provenance records, plus the current and immediate-baseline
master PDFs. Comparison proofs are delivered separately. The checksum manifest
names every omitted PDF export. Update the retained baseline in
`package_release.py` for the final release. Verify a prior comparison only if
it was included in that release's manifest. Keep uniquely versioned filenames
for every user-facing PDF, native master and ZIP.
