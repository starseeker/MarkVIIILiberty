# Figure restoration — clean raster and selective vector masters

This pass restores all **34 plates in 31 artwork assets**, using the previously
accepted geometry corrections as its input. It removes the paper color, reduces
uneven illumination and show-through, and increases usable contrast. Original
source JPEGs and the earlier geometry PNGs are retained unchanged.

Start with `Figure_Restoration_Comparisons.pdf`: pages 2–7 compare the three pilots
and enlarged details; pages 8–38 compare every artwork asset in reading order.
`Plate12_Mirror_Study.pdf` adds a five-page before/after investigation of
mirrored reverse-page separation. `Restored_Figures.pdf` is a gallery of the preferred masters with the historical
image content alone. It uses vector content where recommended.

## Results and format choices

- **Five vector SVG masters:** Plates 6, 7, 21, 24 and 29 (folios 280, 281, 293,
  296 and 301). They contain paths only, with eight levels of gray.
- **Two hybrid SVG masters:** folio 283 (Plates 10–11) and folio 288 (Plate 16).
  Shaded components and the photograph remain embedded lossless grayscale pixels;
  the surrounding drawing, leaders and lettering use vector outlines.
- **Twenty-four preferred raster masters:** all other artwork assets. They retain
  continuous shading, photographic detail or particularly uncertain fine linework.
- **All 31 assets also have lossless grayscale PNG and PDF versions**, at the
  rectified input pixel dimensions. The book uses native SVG groups for the seven recommended vector/hybrid assets,
  with lossless linked PNGs for the other 24 assets.

The foldout remains flat, with no new geometric correction. Its small, dense
lettering favors the grayscale raster over the vector trial. Plate 12 (folio 284)
also retains raster preference. A registered mirror of page 283 now reduces its
identifiable show-through. The user subsequently approved an aggressive keep mask
that removes unassociated mottling while protecting reviewed text, details and
line corridors. Plate 12 remains raster. The older conservative Plate 12 vector
trial is historical and is not the current artwork. The foldout trial remains
**not recommended** in the full project manifest; they are omitted from
the small recommended-figures bundle.

The SVGs are **source-derived outline traces**, not semantic CAD drawings. Text
is retained as traced lettering, not retyped editable characters. Curves and
hatching are scalable, but they still inherit the source's focus and sampling
limits. A vector does not establish original dimensions or recover missing detail.

## Method

`restore_figures.py` reads `assets/p*-geometry.png` and
`restoration/config.json`. It does not rewarp or crop the accepted geometry.

1. Convert to grayscale with a very mild 0.35-pixel Gaussian grain filter.
2. For line regions, estimate local paper using a 31-pixel morphological closing
   and a 3-pixel Gaussian smoothing of that background field. Map the ratio of
   foreground luminance to the estimated paper using a per-page threshold and
   contrast range. This suppresses broad pale show-through without treating it as
   drawing geometry.
3. For tonal artwork, use manually specified protection regions. Estimate the
   paper field from unprotected samples (90th percentile in 60-pixel tiles),
   interpolate and smooth it, and apply a gentler continuous gray mapping.
   Protected regions blend over a small boundary. Photographic and shaded plates
   use different settings; faint engine-section callouts received gentler settings.
4. Remove only the pale artificial padding seam left by earlier rectification.
   Dark ink near that seam is protected. Plate 29's leftmost **8** was explicitly
   checked after a trial exposed the risk of eroding a close edge label.
5. On Plate 16, keep individually selected components, labels, leaders, frame,
   pins and caption; make clearly blank outside-paper regions white. The masks are
   retained in the configuration and generated mask previews.
6. Trace selected clean regions in **eight gray layers** with Potrace 1.16, using
   a 3× contour sampling grid, zero speck-size deletion, corner parameter 1 and
   curve tolerance 0.12. Sampling is interpolation for contours, not recovered
   resolution. Layering avoids the excessive black weight seen in a single binary
   tracing trial. The SVGs retain the original viewBox and placement coordinates.
7. Export SVGs using Inkscape. Hybrid assets use opaque white outside the retained
   raster regions; this avoids thin soft-mask seams in PDF viewers. PDF comparisons
   embed actual vector PDF content, rather than screenshots of the SVGs.

No generative fill, semantic redrawing, inferred wire connections, invented teeth,
retyped internal part numbers, or newly constructed gradients were used. Background
fields estimate paper illumination only; they do not invent object pixels.
Plate 12 additionally uses its actual reverse, page 283, as a reference. The earlier
local-only cleanup had not tried this pairing. The reference is mirrored in the
original portrait orientation, aligned projectively, then adjusted by a smooth
field from 66 locally matched windows. Its blurred ink density and a locally fitted
transfer strength estimate the visible reverse-ink attenuation. Plate 12's existing
luminance is divided by one minus that field before the same local cleanup.
Only the reference and correction field are resampled; front-side geometry stays
unchanged. Bicubic field overshoot is clamped to nonnegative ink.

The paired comparison reduces remaining ink in two selected blank patches by about
24–32%; a darker mottled patch improves only about 4%. In three checked foreground
regions no dark pixel becomes near-white, and the mean dark-pixel change is about
1–2 levels out of 255. These are selected checks, not a full proof of every faint
line. The 0.59 whole-page registration correlation is fitting evidence, not a
held-out accuracy score. At that conservative stage, residual mottling was retained. Several clusters coincide with inked battery and
wiring regions on the registered reverse, so localized ink penetration is
plausible. A smooth transfer field can underestimate such intense local marks;
failure of that model to remove a spot is not evidence that it is an unrelated
stain. The photographs alone do not establish the physical cause.

`Plate12_Mirror_Study.pdf`, `paired_bleedthrough.py` and `restoration/paired/`
retain the previous master, source hashes, registration model, correction field,
fitting experiment and measurements. The paired model has been applied only to
Plate 12; other figures use their recorded local/tonal cleanup.

The accepted aggressive follow-up is recorded in `restoration/aggressive/`.
`Plate12_KeepMask.png` is authoritative: white keeps the exact conservative pixel;
black replaces it with white paper. The approved candidate removes 29,725 nonwhite
pixels, approximately 2.396% of the earlier image's total darkness. This is an
editorial assumption about unassociated marks, not proof of their physical cause.
Its reviewed lettering, details and retained line corridors remain unchanged.
`restore_figures.py` now reapplies this mask after reproducing the conservative
master and checks that the pre-mask pixels match. The comparison and earlier
conservative image remain available for review.

Plate 12 retains a small, varying residual slant: approximately 1.8 degrees
clockwise at the upper rule, 1.2 degrees in the middle and nearly zero at the
bottom. A uniform rotation would tilt already-level portions. This release
preserves the approved geometry; it makes no new warp or global rotation.

## Fidelity and remaining limits

Every plate was reviewed in a full-plate preview. The three pilots received
additional enlarged comparisons; difficult engine shading, weak-line drawings and
edge lettering received specific checks. Some residual blemishes remain on Plates
6, 7, 12, 21 and 24, especially where pale marks overlap fine drawing. The faintest
lines, highlights and original print defects cannot always be separated from
paper noise. The original geometry PNG is the reference for disputed details.

The clean figures are improved reproduction masters, not claims of complete
restoration or engineering accuracy. No source resolution is synthesized. Some
photos retain a gray photographic background because it belongs to the printed
image, rather than the surrounding book paper.

`restoration/validation.json` records the preservation checks. These compare the
full native document and PDF against the pre-restoration checkpoint, and verify
source hashes, clean image sizes, vector/raster content, text and page order.
Rasterized vectors are compared with their cleaned PNG inputs at the same pixel
size. That check detects tracing/export changes; it does **not** independently
prove historical fidelity or resolve ambiguous source marks.

## Using the results

The main `SNL_G13_Pilot.sla` now contains **seven native SVG groups** in the
original artwork positions: five pure vector plates and two hybrid assets. The
remaining **24 artwork frames** link `restoration/clean/p*-clean.png`, including
the accepted aggressive Plate 12. All 25,682 editable text frames are retained.
The complete document has 125,890 native objects including imported contour paths.

Scribus supports SVG directly through **File → Import → Get Vector File**, or the
Scripter `placeSVG` operation. Rasterizing a vector plate first is unnecessary.
These imports were tested in Scribus 1.6.1. Its SVG importer dropped embedded PNG
data URIs in the hybrid test; the prepared import copies therefore link decoded,
lossless PNGs in `restoration/native/`. The imported groups retain those images
alongside the vector paths. Keep that folder with the document. The supplied
standalone hybrid SVG masters still have embedded images and remain portable.

The matching book PDF preserves the vector paths and exports raster regions using
ZIP/Flate compression with downsampling disabled. Internal figure lettering is
still source-derived outlines or pixels, not editable characters. Many thousands
of imported paths increase the native file's size and editing cost.

`Restored_Figures.pdf` uses the preferred vector/hybrid/raster format for each
asset. Its page sizes are convenient native-pixel canvases (0.75 pt per input
pixel), **not measured original plate dimensions**. The book remains 6 × 9 inches
with the provisional 18 × 9 inch foldout.

The complete project keeps the source images, previous geometry assets, historical trials,
configuration, scripts and preservation records. The smaller
`SNL_G13_Restored_Figures.zip` contains all clean PNG/PDF files, the seven recommended
SVG/PDF masters, this guide and the per-asset manifest. Files use original folio
numbers so that paired plates and the foldout cannot be silently reordered.

## Reproduction

Requires Python with NumPy, SciPy, Pillow, PyMuPDF and ReportLab; Potrace; Inkscape;
and Scribus 1.6.x with the bundled C059 OpenType fonts for the main book export.
Run from the project root:

```bash
python3 paired_bleedthrough.py
python3 restore_figures.py --trace --potrace /path/to/potrace
python3 export_restored_figures.py
```

The first command recreates the accepted Plate 12 correction field from its saved
registration coefficients. The restoration command recalculates assets and hashes;
unchanged outputs retain their review decisions, while changed outputs are flagged
for renewed review. The checked-in manifest records the reviewed decisions. The
optional `restoration/paired/fit_global.py` and `fit_local.py` reproduce the fitting
experiment into `fitting-output/`; they do not replace the accepted model silently.
Review changes before generating publication proofs. `integrate_restored_figures.py` handles the initial raster links. For native SVGs,
run `prepare_native_vectors.py`, run `import_native_vectors.py` inside Scribus,
then run `integrate_native_vectors.py`. The latter preserves every other native
object. Derived import copies and isolated test documents can be regenerated;
only tone PNGs, placement records and validation need accompany the native book.
Run `export_restored_book.py` inside Scribus to export; then run
`make_proofs.py --pilot-only` for original-folio navigation.
`validate_final_book.py --baseline-zip /path/to/previous-project.zip` performs
current preservation checks; `validate_figure_restoration.py` documents the earlier
all-raster stage. Do not substitute an earlier transcription checkpoint
for the immediate pre-restoration baseline.

Source publication and provenance are documented in the main README, including
[Internet Archive SNL_G13_TANK_MKVIII](https://archive.org/details/SNL_G13_TANK_MKVIII)
and National Archives Record Group 394, series NAI 26417262.

## Plate-by-plate decisions

| Folio | Plates | Preferred master | Review note |
| --- | --- | --- | --- |
| 277 | 1 | raster | Grayscale photograph: retain ground shadows and continuous tones. |
| 277_foldout | 2 | raster | Flat scan. No geometric change. Dense, small original lettering favors the continuous grayscale master over the tracing trial. |
| 278 | 3, 4 | raster | Both photographic views retained together; highlights and plate captions preserved. |
| 279 | 5 | raster | Shaded pump views retained as raster. Faint residual marks remain near some leaders. |
| 280 | 6 | vector | Layered outline paths retain heavy rods, thin leaders and dashed context outlines. Some paper blemishes remain where they overlap fine drawing. |
| 281 | 7 | vector | Layered outlines preserve the isometric drawing and original hand lettering. A little residual paper texture remains near fine details. |
| 282 | 8, 9 | raster | Line diagram and shaded tank view retain their arrangement. The photograph is protected with a contour mask. |
| 283 | 10, 11 | hybrid | Hybrid SVG: photograph and shaded components remain raster; surrounding labels, leaders and wiring use traced outlines. Original intersections retained. |
| 284 | 12 | raster | Approved aggressive cleanup removes unassociated mottling while preserving reviewed lettering, details and line corridors. Remaining variable slant is unchanged; raster preferred. |
| 285 | 13 | raster | Continuous shading retained in the shafts, gears and cam surfaces; labels and frame cleaned separately. |
| 286 | 14 | raster | Dense section shading and fine callouts retained as grayscale; no automatic binary conversion. |
| 287 | 15 | raster | Gentler tone and threshold settings protect faint labels and subtle cast-surface detail. |
| 288 | 16 | hybrid | Hybrid SVG: individually protected components retain gray shading; labels, leaders and frame use vector outlines. Clearly blank surroundings were masked. |
| 289 | 17 | raster | Smooth highlights on the pump housing remain grayscale; no invented gradient surfaces. |
| 290 | 18 | raster | Three connecting-rod views kept together. Shading, holes and part callouts remain raster. |
| 291 | 19 | raster | Four shaded gear views retain their arrangement and original highlight structure. |
| 292 | 20 | raster | Both assembled views retained; dark cutaway detail and pulley shading remain grayscale. |
| 293 | 21 | vector | Layered outlines retain section hatching and dashed context lines. Some dark paper blemishes remain; no inferred geometry. |
| 294 | 22 | raster | Grayscale retains the dense transmission cutaway and its small callouts. |
| 295 | 23 | raster | Section shading and linework remain grayscale to preserve fine surface differences. |
| 296 | 24 | vector | Layered paths retain the radiator schematic and source lettering. Weak dashed context lines remain weak; residual blemishes are visible in places. |
| 297 | 25 | raster | Printed photographic backdrop retained as part of the image; the surrounding page is white. |
| 298 | 26 | raster | Photographic track surface kept in continuous grayscale. |
| 299 | 27 | raster | Wheel highlights, holes and complex tooth silhouettes remain raster; no modeled teeth. |
| 300 | 28 | raster | Both assembled views retain gray shading and callouts. |
| 301 | 29 | vector | Layered vector paths preserve thin section hatching, hidden lines, the scale and labels. The leftmost 8 was explicitly checked at the canvas edge. |
| 302 | 30 | raster | Grayscale retains the brake band, fasteners and faint cast-surface tones. |
| 303 | 31 | raster | Grayscale preserves the band and hub tones after the accepted geometry correction. |
| 304 | 32 | raster | Grayscale preserves shaded members, band and tiny callouts. |
| 305 | 33 | raster | Exploded shaded components retained as raster; clear outside-paper regions normalized. |
| 306 | 34 | raster | Gentler grayscale treatment preserves the engine section and small callouts. |

## Distribution note

The large `Figure_Restoration_Comparisons.pdf` is a separate companion download;
it is omitted from the project ZIP to keep the package manageable. The complete
book PDF, editable Scribus document, all source images and restored masters remain
in the project ZIP. Place the comparison PDF beside the main document if desired.
