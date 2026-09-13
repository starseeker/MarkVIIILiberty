# Manufacture of Mark VIII Tanks at Rock Island Arsenal

Harry B. Jordan. *Army Ordnance*, July–August 1920, pp. 27–33.

Release: **v01_20260913T172808Z**. Complete seven-page editable reconstruction.

## Open and read

- **Jordan_MarkVIII_Master_v01_20260913T172808Z.sla**: editable Scribus 1.6.x document.
- **Jordan_MarkVIII_Master_v01_20260913T172808Z.pdf**: clean seven-page PDF with original folios and bookmarks.
- **Jordan_MarkVIII_Comparison_v01_20260913T172808Z.pdf**: seven source/reconstruction comparison sheets.
- **TRANSCRIPTION.md**: text in reading order, with printed line breaks and page/column boundaries retained.

Install the three C059 OpenType fonts in `fonts/` before opening the SLA. Keep
`assets/` next to it: all six image links are relative. All headings, body text,
captions, page numbers, the inset letter, and the final workforce list are native
editable text. Printed line endings are retained using separate line frames;
this is a layout-preserving reconstruction, not a continuous reflowing story.
The arsenal identification cards within photographs remain original image pixels.

## Source selection and scope

Primary source: the supplied color scans in
[starseeker/MarkVIIILiberty](https://github.com/starseeker/MarkVIIILiberty/tree/main/references/1920-07_Manufacture_of_Mark_VIII_Tanks/original_scans),
checked out at `0b825f3608161f0fb1c82dc755013523c3951787`.
Secondary reading reference: [Internet Archive issue scan](https://archive.org/details/sim_ordnance_july-august-1920_1_1).
An extracted seven-page article PDF and the nine supplied JPEGs are in `sources/`.

`MarkVIII_manufacture002_composite.jpg` supplies printed page 28, including the
right-hand material lost from `MarkVIII_manufacture002.jpg`. It is a reconstruction
of that one page and is not counted twice. Both files are preserved.
`MarkVIII_manufacture000.jpg` is a bound-volume title leaf, retained as provenance
but not inserted into the article. The unrelated journal departments below the
article ending on page 33 are not transcribed. The comparison sheet shows the full
source page so that this boundary remains evident.

The transport panorama and its continuing caption remain on their original pages
28 and 29. The portrait, loading-accident photograph, and both interior photographs
retain their original places in the article.

## Reconstruction choices

The document uses a provisional 8.5 × 12 inch page (612 × 864 pt). This is a clean,
consistent digital canvas; it is not a claim about the magazine's exact trim.
Column arrangement, illustration scale, printed line sequence, headings and
folios follow the scans closely. C059 is a practical open-font approximation;
small capitals in the letter are approximated with capitals.

Text was independently transcribed from the supplied scans and compared with
region OCR and the Internet Archive reference. `data/ocr_corrections.json` records
85 differences from the local OCR, including false characters from page texture.
The text retains source wording and apparent errors; see `REVIEW_NOTES.md`.

Photographs were rectified from their printed borders, converted to neutral
grayscale and given a restrained global tonal adjustment (0.1% tail limits).
They remain at approximately their source sampling resolution and are compressed
losslessly. There is no generated detail, inpainting, sharpening, redrawing of
photographic content, or replacement of embedded identification cards. Original
scan files are unchanged. Photographic perspective within the scenes is preserved.
The original halftone texture remains visible at high magnification.

## Rebuild

Ordinary editing needs only Scribus and the fonts. To recreate this release,
execute `build_project.py` from Scribus's Script menu. It creates a new document
from the reviewed JSON and overwrites the names in `data/release.json`; save manual
edits separately first.

On Linux, the preferred unattended command is `python3 scripts/rebuild.py` with
Scribus 1.6.x, PyMuPDF and lxml installed. It uses the bundled OpenType font set in
an isolated font configuration, avoiding ambiguous duplicate Type 1 installations,
and produces the clean PDF and comparison PDF. The exported PDF embeds subsets
of all three OpenType fonts.

The source-preparation scripts are reproducibility records and are not required
for ordinary editing. They require Pillow, NumPy and Tesseract. Run in order:
`prepare_sources.py`, `author_transcription.py`, `prepare_artwork.py`,
`prepare_layout.py`, then `rebuild.py`. All script paths are under `scripts/`
except `build_project.py`. Regeneration uses the reviewed transcription rather
than accepting raw OCR as final text.

## Validation

Scribus 1.6.1 reports 586 editable text frames, six linked images and zero text
frames overflowing before save or after reopening. PDF text inventories match
the native frames on every page after whitespace/ligature normalization. All
image links resolve as relative paths; all output pages were rendered with
Poppler and visually reviewed. `data/native_validation.json` and
`data/pdf_validation.json` contain the machine checks. Source SHA-256 hashes are
in `source_metadata/source_inventory.json`; figure transforms and tonal endpoints
are in `data/artwork.json`.

This is a reviewed reconstruction, not an independent historical or engineering
verification of Jordan's claims. The numerical statements are reproduced, not
reconciled from modern sources.

## Repository placement

This folder can be copied to
`references/1920-07_Manufacture_of_Mark_VIII_Tanks/scribus/` in the repository.
No upstream files were changed or pushed. The included originals can be retained
for a self-contained package or managed separately by the repository maintainer.
