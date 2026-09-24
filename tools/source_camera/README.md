# Reusable source cameras

Each source image has an explicit projection hypothesis, fitting landmarks,
independent held-out landmarks and an immutable numerical fit. New geometry is
normally viewed through the existing camera. A lower residual alone does not
justify changing it or changing the CAD model.

The fitter supports perspective (square pixels, no lens distortion), orthographic
(including rotated axonometric views) and explicitly selected oblique/affine
illustrations. Affine projection is not a physical perspective camera. Mixed
views, exploded arrangements and local drawing distortions may have no single
valid camera. Classify these instead of increasing model flexibility until they fit.

## Reuse and refit policy

| Change | Action |
|---|---|
| New unrelated parts, detail, color or visibility | Reuse camera; render current geometry |
| New held-out landmarks | Reuse camera; recompute residuals |
| Holdouts conflict | Flag review; inspect picks, projection and geometry independently |
| Fitting anchor placement changes | Recompute coordinates; review refit reason; retain old fit |
| Anchor definition changes | Stop and reverify the local locator against the revised shape |
| Source pixels/crop/rotation change | Reverify image picks; use a new image hash |
| Projection, assumptions or solver changes | Separate fit version and before/after review |

Numerical fits are usually inexpensive on small landmark sets. Source reading,
landmark identification and diagnosis are the costly reasoning steps worth
preserving. Cache identity includes original image bytes and dimensions, projection,
fit coordinates/picks/uncertainties, assumptions, fitter code and numerical library
versions. It excludes unrelated geometry and holdouts. Every reuse reassesses the
current holdouts. Camera changes never mutate CAD geometry.

### When to reverify

Reverification and refitting are separate decisions. Reuse the saved camera for
routine detail additions. When producing a source comparison, resolve the current
CAD anchors and reassess holdouts before interpreting the overlay. Review the
projection hypothesis again when a newly populated subassembly supplies useful
depth information, a previously estimated anchor gains better dimensional
evidence, or a new source contradicts the existing interpretation. These events
call for targeted checks, not an automatic new fit or a reread of every figure.
Preserve the source classification, landmark identities, uncertainty rationale
and unresolved ambiguities alongside the numerical camera.

Inspect where discrepancies occur. A disagreement confined to one uncertain
component first calls for checking that component and its image picks. A coherent
pattern across several independently supported parts is a reason to investigate
camera/projection or scan assumptions. Neither pattern proves its cause; mixed
illustrations and local scan distortion may not admit a single camera. Add useful
new features as holdouts first, retaining the existing fitting/checking roles.

Before adopting a refit, record the evidence that warrants revising the old hypothesis
and compare both cameras against the same current geometry and independent check
features. Preserve the previous assessments as well. A smaller fitting error is
insufficient if it merely compensates for estimated geometry or worsens agreement
with established parts. Revisit only the affected source views; standard
progression cameras remain fixed. Routine evidence review belongs to the modeling
workflow and does not require another user approval.

A packet needs `source_image`, `source_sha256`, `image_size_px: [width,height]`,
`projection`, and `landmarks`. Each landmark has a unique `id`, `use: fit|holdout`,
`world_mm: [x,y,z]`, `pixel: [u,v]`, and positive `sigma_px`. Use original decoded
pixels, x right/y down; no implicit EXIF rotation. Uncertainty must account for
picking and estimated CAD anchors and must be justified before inspecting residuals.
At least eight distributed, nonplanar fitting points and three separate holdouts
are required for a useful review. Planar-only automatic calibration is deliberately
rejected; it needs independent view/intrinsic constraints not implemented here.

For saved CAD, add `native_file`, `manifest` (the existing extraction format) and
an `anchor` on each landmark: `occurrence`, `local_mm`, `definition_sha256`, and
`evidence`. Anchor coordinates are recomputed from actual assembly frames. The
resolver independently checks selected archive BReps and composed placements
against the FCStd, and refuses changed definitions until the locator is reviewed.
Bounding-box points in the controlled demo are synthetic landmarks; they are not
valid substitutes for identifiable points in a historical photograph.

Optional rendering requires `render_occurrences`, optional `render_colors`, and
`tessellation_mm`. Use absolute command arguments with the headless launcher,
which changes the working directory. Paths *inside packets* are repository-relative
or absolute. Example (replace packet/output paths with a prepared review packet):

```sh
python3 tools/source_camera/review.py /absolute/packet.json --cache /absolute/cameras --output /absolute/new_assessment
python3 skills/freecad-reconstruction/scripts/freecad_headless.py --workdir .work/camera-runtime tools/source_camera/review.py /absolute/packet.json --cache /absolute/cameras --output /absolute/new_render --render
python3 tools/source_camera/test_camera.py
```

Every assessment directory is new. Keep its `assessment.json`, `next_packet.json`,
optional geometry/overlay PNGs, and referenced immutable fit. Start subsequent
reviews from `next_packet.json`; it carries `previous_fit_key`. A changed fit with
a prior key requires `refit_review: {reason, reviewer}`. The project reviewer can
make routine evidence-backed decisions; this is not an extra user approval gate.
Keep competing families and before/after residuals, including rejected versions.
`camera_assumptions` records reasoning; it does not implement additional solver
constraints. Current optimization settings are fixed in the versioned fitter.

Overlay circles mark picks, crosses mark projected positions; blue points fit,
magenta points are held out. Solid pixels are blended into the original image.
No automatic framing, image warp or fitted per-part transforms are applied.
Perspective raster depth is reciprocal camera distance; geometry crossing the
near plane fails explicitly. Affine occlusion uses a documented cross-product
view convention and needs visual review. These display meshes do not replace
native solid, interface or STEP validation.

Numerical residual thresholds and conditioning diagnostics **never automatically
accept a historical camera or qualify geometry**. A consistent result still needs
review of anchor identity, spatial distribution, family plausibility and independent
features. Estimated or wrong geometry can produce an apparently good fit.

The constrained robust solver uses SciPy's documented
[least_squares](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html).
The headless renderer consumes FreeCAD BReps directly. GUI/Coin camera export is
not yet implemented; a cropped image's off-centre principal point needs more than
setting a symmetric field of view. Coin's
[camera documentation](https://www.coin3d.org/coin/classSoPerspectiveCamera.html)
is the reference for future GUI parity work.
