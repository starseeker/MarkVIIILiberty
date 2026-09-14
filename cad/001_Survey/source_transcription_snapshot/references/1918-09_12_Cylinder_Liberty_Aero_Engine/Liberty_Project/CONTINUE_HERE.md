# Liberty engine manual: all source batches complete

The complete first reconstruction pass has **162 manual pages**, from staged
scans 0001–0162. All **167** staged JP2s have been inspected and are bundled.
There is no next source batch. The final printed page is **151**, Fig. 107,
**General Arrangement (Longitudinal Section).** Last prose remains the Zenith
control adjustment on p142. Do not invent further folios or add scanner cards
to the manual.

| Scan | Final treatment |
| --- | --- |
| 0160 | Printed p151, longitudinal-section foldout; unchanged from v08 |
| 0161 | Unprinted inside back cover surface, retained as blank page 161 |
| 0162 | Unprinted back cover, retained as blank page 162 |
| 0163 | Scanner support and narrow book fragment; excluded from manual |
| 0164–0165 | Color calibration targets; excluded from manual |
| 0166–0167 | White calibration references; excluded from manual |

The barcode on 0161 and later library marks, handwriting and repairs on 0162
are not original manual printing. They remain in the source JP2s and final
comparison proof. Original physical board color and discoloration are omitted,
consistent with the reconstruction's treatment of the front inside cover.
No artwork cleanup or inferred engineering detail was introduced in batch 09.

Exact current filenames are in `data/release.json`. Open the released v09 SLA,
with `assets/` beside it and the four bundled OpenType fonts installed. The
first 160 pages, all 4,858 editable text frames, 53 native rules and 108 linked
illustrations are unchanged from v08. All five foldouts retain their provisional
working dimensions; the two new blank surfaces use 396 × 691 pt.

For future revisions, preserve the current released SLA/PDF and user edits,
assign a new version and UTC timestamp, and work from this release. Do not
rebuild previously reviewed pages from OCR. The current builder is a reproducible
record of adding the final two pages to the exact v08 baseline, not a general
editor for later manual changes. `_batch09_seed.sla` contains unpopulated new
pages and is an intermediate, not the released master.

The remaining work is independent technical proofreading and verification of
physical trim and typefaces. Source anomalies and uncertain editorial readings
are documented in `REVIEW_NOTES.md`; preserve them until an explicit correction
is authorized. Geometry and internal drawing labels remain original pixels.
Retain RGB Figures 24–26, sideways source orientations, caption-only masks in
Figures 47, 73, 88 and 101, and background-edge exclusions in 102 and 107.
See the preserved `data/CONTINUE_HERE_v08_record.md` for detailed batch-08
transcription and foldout notes. Earlier maps, scripts and review records are
historical evidence, not indications of unfinished source batches.

The final source decision record is `data/batch09_classification.json`; the
complete 167-source map is `data/source_disposition.json`. Current validation
records include native save/reopen, exact PDF/native character inventories,
all 160 earlier page render comparisons, native object/style preservation,
167 source hashes, 108 original-crop comparisons, fonts and bounds, and two
blank closing pages with no native objects or ink. Final visual review is in
`data/visual_review.md`. An unchanged earlier page inherits its completed review;
this batch is not a fresh independent technical proofread of the whole book.

The compact ZIP contains every released native SLA, all source files, original
and cleaned assets, fonts, data and scripts, plus the current and exact v08
master PDFs. Comparison PDFs are delivered separately. The internal release
manifest hashes included files and names omitted historical PDF exports.
Update `scripts/package_release.py` if creating a later release with a new
immediate baseline. No repository files were changed or pushed.
