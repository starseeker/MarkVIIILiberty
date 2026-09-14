# U.S. Patent 1,366,550 - Tank

Herbert W. Alden. Patented January 25, 1921; application filed December 14,
1918, serial 266,817. Four-page Scribus reconstruction of the supplied USPTO
scan, prepared September 13, 2026.

## Open this edition

Open `US1366550A_Master_v01_20260913T174356Z.sla` with Scribus 1.6.x.
Install the four bundled OpenType fonts from `fonts/` before opening it.
The corresponding master PDF has embedded fonts and needs no installation.
The five-page comparison PDF pairs all four source/reconstructed pages and
includes an additional drawing-detail sheet.

The Scribus file contains the complete edition: 266 editable printed-text
frames, plus native vector outlines imported from the cleaned drawings.
The drawings and handwritten labels/signatures are embedded paths. They
have no external image-link dependency and can be ungrouped in Scribus.
They are traced historical artwork, not dimensioned engineering/CAD geometry.

## What was preserved and changed

- Original four-page order, two drawing sheets, three figures, two-column
  specification, nine claims, printed folio, and five-line reference numbers.
- The original body line and column breaks, including hyphenated words and
  the continuation of claim 3 between columns. Paragraph indents were reset.
- Source wording, spelling and technical references. The seemingly unusual
  phrase "ultimate perfection of the gun" is present in the source and retained.
  Scan/OCR confusions such as chamber 13 versus 18 and wall 3 versus 8 were
  resolved by visual reading of the supplied scan.
- All printed matter was typeset with C059 and Nimbus Sans. Specification
  columns and running matter use consistent alignment. This is an editable
  reconstruction, not an exact facsimile of the original metal type.
- Drawing crops exclude the page background and heavy scanner-edge mark.
  A restricted mask removes the old printed sheet-header fragments where
  their vertical band overlaps the top of the drawings.
- Conservative connected-component filtering removes only isolated marks of
  at most six black pixels, more than fourteen native pixels from a component
  of at least twenty-four pixels. Dotted outlines, hatching, label fragments,
  and signature punctuation next to meaningful detail are protected.
- Potrace 1.16 outline tracing uses `-t 0 -a 0.55 -O 0.1`. Tracing smooths
  pixel boundaries; it does not reconstruct missing technical information.
  Native-resolution cleaned bitmaps are retained beside the SVGs, and the
  original PDF is included unchanged.
- The source PDF's 612 x 792-point page geometry and displayed drawing
  proportions are retained. The embedded 2320 x 3408 images have different
  effective x/y sampling rates in that PDF; no unsubstantiated aspect-ratio
  correction, nonlinear dewarp, sharpening, or geometric redrawing was applied.

## Files and reproducibility

- `sources/`: untouched supplied PDF and source provenance/checksum.
- `assets/`: cleaned native-resolution PNGs and source-derived SVGs.
- `data/`: reviewed text, original line inventory, placement, release data,
  and machine-readable validation results.
- `fonts/`: C059 Roman/Bold/Italic and Nimbus Sans Bold, with license and metrics.
- `build_project.py`: Scribus-native authoring and save/reopen validation.
- `scripts/author_transcription.py`: generates the reviewed text inputs.
- `scripts/prepare_artwork.py`: repeats extraction, cleanup and vector tracing.
- `scripts/rebuild.py`: unattended rebuild using the bundled fonts in an
  isolated fontconfig configuration.
- `scripts/check_and_compare.py`: validates the export and generates comparisons.
- `SHA256SUMS.txt`: checksums for the release contents.

To rebuild using the reviewed inputs, run `python3 scripts/rebuild.py` on Linux
with Scribus 1.6.x installed. Its comparison/verification step also needs
PyMuPDF, Pillow, NumPy, SciPy and lxml. Alternatively, install the bundled fonts
and execute `build_project.py` through Scribus's Script menu. To regenerate
the artwork first, install Potrace and run `scripts/prepare_artwork.py` with
the same Python dependencies. `POTRACE` may point to an explicit executable.

Rebuilding overwrites this release's master and comparison files. Save manual
Scribus edits under another filename first. Change `data/release.json` when
issuing a new revision so downloaded files remain distinguishable.

## Validation

All four pages were reopened in Scribus 1.6.1 and visually inspected after
independent PDF rendering with Poppler. There are zero text-overflow errors,
no font substitution, and no external artwork links. The exported PDF contains
searchable printed text, embedded fonts, and vector artwork with no raster pages.
The normalized PDF character inventory matches the authored text on each page;
each reopened Scribus text frame also matches its reviewed string exactly.

At the source's native sample grid, all retained black drawing pixels have
visible reconstructed ink within two pixels, and all reconstructed drawing ink
is within two pixels of retained source ink. Visibility is measured at gray
value below 240/255 to include antialiased fine lines. This checks preservation
and alignment; it does not imply that tracing adds detail beyond the scan.

The included original remains the authority for interpretation and measurement.

## Source

[Supplied repository scan](https://github.com/starseeker/MarkVIIILiberty/blob/main/references/1921-01-25_US1366550A/original_scan/US-1366550-A.pdf)

Git blob: `3759d70be28b37cd0d62dc20c1baee9891884d1b`.
