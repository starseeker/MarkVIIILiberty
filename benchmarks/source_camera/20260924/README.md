# Source-camera controls — 24 September 2026

This is a **synthetic known-camera experiment using real saved transmission
geometry**, not a fit to a historical photograph. It tests the complete path from
FCStd archive/placements through image fitting, calibrated raster rendering and
camera reuse. Bounding-box datums are synthetic controls, including points in
empty space; historical picks must identify actual image features instead.

The control uses 12 fitting points and four held-out points from four saved
transmission-frame/bearing occurrences. The perspective camera is generated
independently from a known position, rotation and focal length. The recovered
camera's maximum held-out reprojection error is below 1e-9 pixels. This exact,
noise-free control tests implementation; it says nothing about attainable accuracy
on historical scans or uncertain geometry.

The first durable numerical fit took about 0.0023 s; reuse/reassessment took about
0.00043 s, excluding native verification, image I/O and rendering. Both use the
same camera hash and produce byte-identical geometry and overlay images. Small
numerical fits are inexpensive here; retaining source research and reviewed
landmark identities is the more important efficiency improvement.

- [Known camera](native_control/known_camera.json)
- [Landmark packet](native_control/packet.json)
- [First assessment](fit01/assessment.json), [overlay](fit01/overlay.png)
- [Reused assessment](reuse02/assessment.json)

Eight numerical/cache/raster tests cover known perspective, orthographic and
oblique projections; fixed-camera holdout conflicts; reviewed refits with old
fits preserved; wrong/altered images; tampered fit records; planar/insufficient
anchors; wrong projection; missing holdouts; robust-fit outliers; and reciprocal
depth occlusion. Three actual-native negative tests reject altered frames, changed
archive shape bindings and stale anchor definitions. These do not automatically
accept any historical camera.

The initial CLI render attempt used a relative packet argument with the headless
launcher, which changes working directory; it failed before fitting. Absolute
arguments resolved it. The tested commands and current limitations are in the
[source-camera README](../../../tools/source_camera/README.md).

Handbook plate79 has been visually classified as a promising perspective
photograph, but no historical fit is claimed. Its trusted spatial landmarks and
independent holdouts are a separate open evidence decision in the tank ledger.
The existing fixed-register HB134/135 comparisons remain unchanged.
