# SNL G-13 — Tank, Mk. VIII (1928)

An editable Scribus reconstruction of the U.S. Ordnance Department’s **Standard
Nomenclature List No. G-13, Tank, Mk. VIII**, dated **March 30, 1928**. The work
preserves the book’s printed sequence, table structure and typography as closely
as practicable, while making its text editable and improving the geometry of
photographed illustrations.

**Status:** all supplied pages have been transcribed and assembled. Figure review
and a targeted cross-book ambiguity audit are complete. Independent proofreading
of the entire transcription remains pending. This is a modern research edition,
prepared iteratively with ChatGPT/Codex and user review, rather than an official
corrected edition of the historical publication.

This README summarizes the accompanying `SNL_G13_Project` package. File paths
below are relative to that package’s root. The documented transcription checkpoint
is the audit of **September 12, 2026**.

## Source and archival provenance

The source images come from the Internet Archive item
[Standard Nomenclature List No. G-13 TANK, MK. VIII](https://archive.org/details/SNL_G13_TANK_MKVIII).
Its description identifies the original publication in the **U.S. National
Archives, Record Group 394**, in the series **Ordnance Notes and Handbooks on Guns
and Gun Carriages, 1900–August 1941**, with **National Archives Identifier
26417262**. This is the series identifier, not a separately established identifier
for this individual volume. [Internet Archive item metadata](https://archive.org/metadata/SNL_G13_TANK_MKVIII)
provides the publication and imaging history; the corresponding
[National Archives catalog reference](https://catalog.archives.gov/id/26417262)
is retained for archival lookup.

Additional details were transcribed from the modern archival panel in the supplied
foldout image and are preserved in `data/foldout_provenance.json`:

| Field | Recorded information |
| --- | --- |
| Archival creator | War Department, Office of the Chief of Ordnance, Rock Island Arsenal, Illinois |
| Container | 5 |
| Item | Mark VIII Tank |
| Declassification project | NND 740018 |
| Access and use restrictions shown on the panel | Unrestricted |

The Internet Archive notes explain that the bound pages were photographed with a
camera in **2017**, producing page curvature, perspective distortion and some
local focus problems. The loose foldout facing page 277 was scanned flat on a
large-format scanner. The Internet Archive item was made public in July 2022.
These acquisition differences are preserved in the reconstruction’s treatment of
the images. See the [source item and its imaging notes](https://archive.org/details/SNL_G13_TANK_MKVIII).

The provenance chain is therefore the original National Archives volume, its
photographs and foldout scan, their Internet Archive distribution, and this modern
transcription and layout reconstruction. Original supplied JPEGs remain in
`sources/`; archival cards and modern annotations excluded from the reconstructed
print area are still present in those source images.

## Scope and reading order

The reconstructed book contains **314 electronic pages**: Roman-numbered pages
I–II, Arabic-numbered pages 1–311, and the separate Plate 2 foldout. All **34
plates** are included. There are no missing numbered pages in the supplied set.
The electronic page count should not be interpreted as a count of physical leaves.

| Scribus/PDF position | Original printed label | Contents |
| --- | --- | --- |
| 1–2 | I–II | Front matter and list of plates |
| 3 | 1 | Title leaf |
| 4–278 | 2–276 | 275 parts-table pages |
| 279 | 277 | Plate 1 |
| 280 | Face p. 277 | Plate 2 foldout |
| 281–309 | 278–306 | Plates 3–34 |
| 310–314 | 307–311 | Notes, manufacturer table and use of prices |

The foldout follows page 277 in plate reading order, retaining its “Face p. 277”
reference. Physical binding placement and final printing imposition remain
unconfirmed. Pages 278, 282 and 283 each contain two plates.

`page_inventory.json` and `page_inventory.tsv` map source filenames, original
folios, output positions and source hashes. Repeated uploads were reconciled
without adding duplicate pages. PDF bookmarks and page labels use the original
folios, so references remain usable despite the front matter and inserted foldout.

## Text and Scribus layout

The native document contains **25,682 editable text frames** and **32,632 native
objects**, including text, rules, leaders and artwork frames. The structured
transcription includes **7,571 table records**.

Parts tables were rebuilt with named cell frames and vector rules, preserving the
sideways orientation, column alignment, component indentations, grouped entries,
continuations and source line breaks. They use individual Scribus frames rather
than Scribus table objects. Front matter, headings, notes, page numbers and
printer imprints are also editable. Figures and their internal lettering remain
linked raster artwork.

Main pages use the agreed **6 × 9 inch estimate**. The foldout uses a provisional
**18 × 9 inch** canvas. These dimensions, margins and type sizes have not been
verified by physical measurement.

The bundled **C059 Roman, Bold and Italic** fonts provide a Century-style
approximation. They are not an identification of the original metal type.
Typeset pages use clean text rather than reproducing paper discoloration, tears
or photographic shadows. Fractions, small capitals, dashes, braces and leader
spacing are approximated where necessary. Limited horizontal scaling helps keep
long table cells on their original lines.

Period wording, blank cells and apparent printed inconsistencies are generally
preserved. Supported restorations and uncertain readings are documented in
`review.json`; clearer-looking modern terminology is not substituted silently.

## Figure distortion correction

All **30 numbered figure pages, 277–306**, were reviewed against their sources.
Together with the foldout they produce **31 artwork assets**. Corrections were
chosen according to the evidence available on each page:

- Long printed borders and reference lines constrain perspective and nonlinear
  straightening where they can reasonably be treated as page-aligned lines.
- Captions and selected horizontal or vertical lettering provide additional
  orientation evidence, particularly on unframed plates.
- A survey of the long rules on all 275 table pages supplied 261 accepted page
  models. Nearby observations of the same page parity provide a weak local guide
  to curvature; there is no single universal odd/even transform or assumed flip
  point for the whole book.
- More complex fits were accepted only where supported. Reserved observations
  were used to assess the later refinements, and unsuccessful trials were retained
  in the records rather than applied to the delivered artwork.

The later refinement improved pages **278, 283, 296, 299, 301 and 303**, containing
Plates **3–4, 10–11, 24, 27, 29 and 31**. The largest gains were on pages 283 and
301. Stronger trials on 282, 284 and 294 were rejected; other pages retain their
previous correction or crop. The flat-scanned **Plate 2 foldout was excluded from
book-curvature modeling** and retained its existing crop and placement.

These are restrained geometric corrections of the source pixels. No drawing
linework or lettering was generated. Corrected assets are lossless PNGs; the
original JPEGs remain available. Some interior distortion persists, especially
where reference evidence is sparse. Part silhouettes, intentional perspective and
splayed components were not forced into rectangular or circular templates.

`Figure_Geometry_Proof.pdf` compares source regions with the current artwork.
`Figure_Refinement_Study.pdf` compares the earlier and refined corrections and
records the review of every plate. Methods, controls, rejected trials and numerical
checks are described in `FIGURE_REFINEMENT.md` and `calibration/`.

## Cross-book transcription audit

Once the complete transcription was available, repeated codes, assembly lists,
quantities, end notes and selected original photographs were compared with the
remaining review flags. The audit closed **13 earlier log entries across 10
findings**: three corrected cells, six corroborated readings and one explained
component relationship.

| Printed page | Earlier transcription | Applied correction |
| --- | --- | --- |
| 43 | SH40A1D | SH40AD |
| 66 | SH975C, water-pipe connection clip | SH976C |
| 97 | First transmission-frame rivet: 1½″ long | 1⅛″ long; diameter remains ½″ |

Other resolutions include confirming **606 radiator tubes** from two cores of
303 tubes each, identifying washer **8209** through Plate 16, and using note (go)
to explain the shared **SH599A** component code in left and right manifold
assemblies.

One new source discrepancy was logged: the plain tachometer-shaft bushing is
printed **D22920 on page 44** and **D29920 on page 110**. Both readings remain.
The current review log contains **113 open and 99 resolved entries**. Some entries
cover general proofreading or layout, so these totals are not counts of uncertain
characters.

See `Transcription_Ambiguity_Audit.pdf`, `TRANSCRIPTION_AUDIT.md` and
`audit/ambiguity_audit.json` for the evidence and remaining conflicts.
`audit/review_before_context_audit.json` preserves the preceding review log.
A confirmed reading establishes what the source says; it does not by itself
establish that a printed dimension or specification is correct.

## Validation and remaining work

The saved Scribus document was reopened and all 25,682 text frames checked, with
**no overflow or unexpected line counts**. All 314 PDF pages were rendered;
page dimensions, embedded fonts and original-folio navigation were verified.
The revised cells and audit report were visually inspected.

For the latest transcription audit, comparison with the preceding delivered
project established that only the three intended cells changed. All native object
geometry, all 314 source JPEGs and all 31 figure assets were preserved. The other
**311 PDF pages rendered identically**. These checks are recorded in
`audit/context_delivery_validation.json`, with supporting native, reopen and PDF
validation records. Earlier geometry validation files document the preceding
figure-refinement stage.

Remaining work includes independent proofreading of small codes, fractions,
quantities and prices; investigation of contradictory original entries; and
further review of figures with limited geometric references. Physical page size,
foldout size, lens effects and interior drawing scale remain uncalibrated.

For subsequent CAD research, the transcription and illustrations provide part
identities, assembly relationships and visual references. Dimensions inferred
from image measurements should remain provisional until supported by explicit
source dimensions or independent evidence.

## Files and use

| File or directory | Purpose |
| --- | --- |
| `SNL_G13_Pilot.sla` | Complete editable Scribus document; “Pilot” is the retained working filename |
| `SNL_G13_Pilot.pdf` | Complete reading and review export |
| `Foldout_Plate_2.sla` | Standalone wide-page foldout document |
| `sources/` | Unmodified source JPEGs |
| `assets/` | Linked corrected figure images |
| `data/` | Structured transcription and source reconciliation records |
| `fonts/` | C059 fonts, proof fonts and their license files |
| `calibration/` | Geometry controls, models, comparisons and plate decisions |
| `review.json` | Current transcription review log |
| `audit/` | Cross-book audit evidence and preservation checks |
| `PROJECT_STATUS.md` | Checkpoint status and earlier figure-refinement history |

Extract the full project package, install the three C059 OpenType fonts and open
`SNL_G13_Pilot.sla` in **Scribus 1.6.x or later**. Validation used Scribus 1.6.1.
Keep `assets/` beside the document. A rebuild is unnecessary for normal editing.
Use the bundled OpenType fonts: a system Type 1 font with the same name can have
different metrics. Substantial text changes may require adjusting frames because
the reconstruction deliberately preserves the original line and page breaks.

The package includes Python scripts for asset preparation, Scribus construction,
proof generation and validation. Principal entry points are `prepare_assets.py`,
`build_project.py`, `make_proofs.py` and `check_reopened.py`.
`audit_context.py` regenerates the recorded audit decisions, while
`apply_context_corrections.py` applies the three named corrections and checks the
native text. Preserve manual edits separately before rebuilding generated files.
Bundled fonts retain their accompanying license notices.
