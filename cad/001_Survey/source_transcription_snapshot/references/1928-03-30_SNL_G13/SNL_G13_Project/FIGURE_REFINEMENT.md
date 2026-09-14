# Figure refinement and complete plate review

All 30 numbered figure pages (277–306) were visually reviewed against their
sources. They contain 33 plates. Plate 2 is the separate foldout; the user
confirmed that it was scanned flat. Its source, corrected asset and native
placement remain unchanged.

Six pages were refined: 278, 283, 296, 299, 301 and 303, containing Plates 3–4,
10–11, 24, 27, 29 and 31. The other 25 assets remain byte-identical to the previous
checkpoint. The 314-page order and all 25,682 editable text frames are preserved.
`Figure_Refinement_Study.pdf` compares previous delivered images with the new
ones, plots the book trend, and records a decision for every plate.
`Figure_Geometry_Proof.pdf` compares source regions with current corrections.

## Accepted models

| Page | Evidence and model scope | Reserved groups | Previous RMS → refined RMS |
| --- | --- | ---: | ---: |
| 278 | Captions and photographic crop boundaries; gentle shared field | 2 | 0.87 → 0.75 px |
| 283 | Distributed horizontal/vertical lettering, diagram references and photographic crop boundaries | 10 | 2.34 → 0.49 px |
| 296 | Selected outline references and lettering; reduced model, no depth-profile fit | 4 | 0.92 → 0.83 px |
| 299 | Header and caption; two-parameter variation of tilt with height, horizontal coordinates unchanged | 1 | 0.88 → 0.48 px |
| 301 | Two end-plate references, shaft, dimension and scale lines | 2 | 3.77 → 0.73 px |
| 303 | Base, upright and headings; varying vertical field with simple horizontal alignment | 2 | 2.39 → 0.62 px |

RMS is the pooled, equally weighted per-group departure from the intended H/V
orientation, expressed in source-pixel coordinates. It includes tilt as well as
curvature. Reserved groups were excluded from fitting. The comparison uses the
**previous delivered correction**, not the raw JPEG; raw-source measurements are
also in the JSON records. This is limited validation of selected observations,
not a measurement of all interior geometry or engineering dimensions.

On 278 the largest visible gain is in the fitted Plate 3 caption while reserved
Plate 4 captions remain level. On 296 the gain over prior caption deskew is
modest. On 299 only one short heading could be reserved, so confidence is lower
than on 283. On 303 the hub reference is not as level as in the raw source, but
is substantially better than in the prior global affine correction.

## Model and book evidence

The forward field uses normalized source coordinates x=(X-W/2)/W and
y=(Y-H/2)/W:

- X′ = X + W(a y + b x y + c x² y)
- Y′ = Y + W(d x + e x² + f x³ + g x y + h x² y + i x³ y)

The model is nonlinear across page width and affine through page height. This is
a restrained approximation to open-book curvature; it is not a calibrated 3-D
sheet or camera reconstruction. Sparse cases freeze unsupported coefficients.
Fit residuals ask each accepted baseline/reference to become constant in its
appropriate output coordinate. A robust loss and penalties on higher terms
restrain unnecessary bending.

All 275 table pages (2–276) were surveyed automatically for continuous long
rules. Initial tracing requires sufficient line support, small residual and
bounded bow. A final residual threshold of 0.7 pixels at the 400-pixel analysis
width accepts 261 page models; 14 higher-residual models are excluded. Selected
source overlays were inspected, but the survey is not a manual verification of
every detected rule. Existing printed-frame traces provide additional nearby
observations in the plate section.

Accepted same-parity observations within 24 folios supply a weak median prior
on the depth-profile terms g/h/i. There is no universal even/odd transform and
no inferred single flip point. The changing trend supports local fitting rather
than copying one neighboring page's warp. Page 296 freezes those terms, so its
fit does not use the book-profile prior. A diagnostic plot of the fitted
left/right vertical correction ratio appears in the study; it is not physical
paper stretch. The user’s flat foldout is excluded from the book model.

## Rejected and retained cases

Stronger trial fields on 282, 284 and 294 were rejected. On 282 the reserved
Plate 9 caption worsened. On 284 sparse/ambiguous outline references produced
unstable extrapolation; some outline segments are unsuitable page axes. On 294
the new fit worsened reserved checks relative to the existing affine result.
Trial measurements are retained for review, not applied to the artwork.

The ten framed pages and the existing paired-axis correction on 293 were
retained after review. Thirteen other unframed pages retain their prior
correction or crop because reference evidence is insufficient or a trial failed.
Some residual distortion remains, particularly in the sparse or ambiguous cases.
Part silhouettes, circles, isometric armor and intentionally splayed rods were
not forced into an orthogonal or circular template.

## Reproduction and provenance

- `measure_book_trends.py` surveys the table rules.
- `build_book_priors.py` rebuilds local priors from accepted table/frame traces.
- `calibration/text_line_controls.json` contains accepted source-pixel observations,
  crops, withheld groups and active parameter sets.
- `rectify_text_model.py` rebuilds the six refined assets from original JPEGs.
  `prepare_assets.py` includes this step in a complete rebuild.
- `calibration/text_model_validation.json` records coefficients, inverse errors,
  positive mapping Jacobians, priors and per-group results.
- `calibration/previous_geometry_validation.json` and
  `previous_figure_transforms.json` record the prior comparison.
- `calibration/refinement_trial_controls.json` and
  `refinement_trial_validation.json` retain accepted/rejected additional trials.
- `calibration/plate_review.json` records every page decision;
  `caption_review.json` records measurements on 17 simpler unframed pages.
- The six `calibration/p*-before-text-refinement.png` files preserve previous
  delivered assets. Red overlays show fitted observations; blue show reserved ones.
- `update_figure_geometry.py` replaces only the six artwork frames in Scribus.
  A full rebuild remains available through `build_project.py`.

Original pixels are sampled once with bicubic interpolation. No lettering or
linework is generated, and no missing details are invented. Pixels outside the
accepted source crop are neutral padding; the unmodified sources remain present.
Mapping Jacobians are positive over each output. Original physical proportions,
lens distortion, exact page dimensions and internal drawing scale remain
uncalibrated. The agreed main-page estimate is 6 × 9 inches; the foldout canvas
remains provisionally 18 × 9 inches.
