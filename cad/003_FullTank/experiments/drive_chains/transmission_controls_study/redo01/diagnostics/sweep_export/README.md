# Sweep and STEP diagnostics

FreeCAD 1.1.1 / OCC 7.8.0, 26 September 2026. Scripts retain original
`.work` paths as execution records; outputs and source hashes bind the checked
geometry. Production construction is the versioned stage worker.

Whole-path Frenet and parallel sweeps gave full-volume Boolean differences after
STEP exchange. Separate edge sweeps fused into one wire solid fixed the isolated
nominal case. Per-edge Frenet fusion returned an empty result at 2.4 mm wire;
per-edge parallel transport produced complete stock for both controlled sizes.
All four native solids and both sizes passed independent wire-volume, capture,
clearance and context tests. The prototype's spring definitions also passed STEP.

Located STEP export made the starboard low-speed spring unorientable at its
installed position (both sizes), despite valid definition exchange. App::Link and
nested App::Part exports reproduced the issue. A single placed root Part lost its
translation. Baking the rigid transform into a temporary export copy retained the
installed material with no difference in either direction. This preserves the
saved native definitions and placements; full installed exchange remains required.

`exchange02` runs were terminated with exit 143 before completion; their partial
results are diagnostics, not acceptance receipts. The following run uses the same
geometry/export construction in a fresh directory. No acceptance limits changed.

The rigidly baked STEP representation turns planar caps into affine 2×2
B-spline surfaces. Measurement v3 admits only certified degree-one nonrational
parallelograms as planes and integrates their physical boundary coordinates.
The intermediate v2 controls caught a missing knot split where a periodic
B-spline boundary was wrapped in `Geom2d_TrimmedCurve`. Unwrapping only for knot
selection, while evaluating the actual trimmed curve, fixes the control failures.
All 28 analytic, rigid-frame, stock-loss and rejection controls in
`../surface_mass04/qualification.json` pass. Original measurement/native geometry
and STEP acceptance limits are unchanged. Final exchange05 compares against the
original native placements and material, including independently converged mass.
