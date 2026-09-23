# Pump-body precision issue remains open

All 26 native checks and 202 material comparisons pass. Of 84 native/STEP
comparisons, 82 pass; the body fails in both definition and installed frames.
Both exported body solids are valid and have zero added/missing material.
The native body's maximum kernel tolerance is 2.19066e-4 mm, above the
unchanged 1e-4 mm limit; reopened STEP tolerance is about 3e-7 mm.

Stage tracing locates the increase at fusing the outlet cylinders into the
annular body, before optional cleanup. Subsequent flange construction leaves
high-tolerance curves near the outlet/flange intersections. Optional cleanup
is not the cause in this case. Native high-tolerance edge bounds are recorded.

Rejected probes: moving the flange earlier also removes 171.78158 mm3 of
material and does not solve the tolerance issue. Rotating torus seams by
45 degrees preserves material but does not solve it. Rotating cylinder seams,
alone or together with the torus, also preserves material but increases the
maximum tolerance to 2.50438e-4 mm. None is adopted. No acceptance criterion,
physical dimension or tolerance value has been relaxed or reset.

The casting and mounting region already require source-driven refinement:
the printed mounting-stud thread lengths do not fit the estimated flange
stack, and the source outlet/scroll contours need a closer reconstruction.
Reconcile that geometry and requalify the final body. The current native is
a development checkpoint, not an accepted installed pump. Full probe scripts,
all four trial shapes and individual STEP exports remain under
`.work/engine-water-pump/body_tolerance_probe` and `body_order_probe`.
