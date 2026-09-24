# Retained operating-mechanism diagnostics

`probe01` and `installed01` preserve the initial ten BReps and installed collision
checks. Pin heads were sized for the cheek width alone and intersected the wider
curved fitting feet. The estimated grip now spans the whole fitting. Assigning an
occurrence placement also overwrote the cotter definition's rotation; its rotated
analytic solid is now retained under an identity compound. `installed02` confirms
clearance for that revised circular-saddle probe, before its tolerance review.

`circular_saddle` retains the first saved candidate's frozen inputs, new BReps,
report and failed checker. Both lever members had about 0.00394 mm maximum kernel
tolerance after fusing the circular screw-bearing barrel to the curved profile.
The instrumented traces isolate that step: the base extrusion is near 1e-7 mm;
rotating the cylinder seam does not resolve the intersection. Continuing the flat
members through a rectangular saddle gives about 5e-6 mm. The section is inferred,
not independently established by the repeated handbook/SNL illustration. This is
a documented geometric interpretation change; no tolerance limits were relaxed.

STEP material differences were empty, but whole-face Gauss integration of the
trimmed B-spline lever did not converge: two precisions differed by about 2.50 mm³.
Default Z partitioning also failed at a measurement slice. Span-aware
Gauss–Kronrod integration passed the original convergence criteria, with about
5.8e-6mm³ volume change and below 2e-9 mm centroid change between precisions.
Seven independent controls cover known box/annular geometry, an exact quadratic
B-spline prism, their rigid transforms and rejection of an open face. Both native
and STEP lever material remain unchanged. The spring retains its separately
qualified partitioned integration method.

The first independent pin-axis check also selected the lever's separate lower
control-rod eye because it shares the pivot bore diameter. The corrected checker
selects the eye above the drum datum and then verifies its actual axis. It retains
the required bore count and all neighboring-material checks.

Trace scripts refer to the retained working-run frozen inputs, and their captured
logs preserve the observed results. `circular_saddle/frozen_inputs` contains those
inputs for recovery. The initial pipeline's nonzero check and subsequent successful
run remain distinct. One preservation invocation terminated without a terminal
receipt; the worker lock was released before resumption, and completed strict
comparisons were reused. No cause was established for that process termination.
