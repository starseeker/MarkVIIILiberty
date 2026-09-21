# Rejected installation trials

- `reversed_elbow_rotation`: a pre-save assertion found the cup axis horizontal.
  The local 45-degree arc was reversed to turn the inclined inlet upright.
- `initial_clearances`: valid saved solids, but seven material clashes affected
  nuts, cotters and the elbow bead. STEP comparisons also failed for the swept
  cotters and elbow. This is not an accepted geometry checkpoint.
- `swept_exchange_failure`: the hardware and fitting clearance corrections
  removed all 598 affected material intersections. The sweep construction
  still failed STEP material comparison. The isolated leg experiment retained
  here shows an equivalent analytic cylinder/torus leg passing the comparison.
- `missing_cotter_leg`: STEP comparison passed after changing the bends, but
  the independent stock/leg gauges found one missing leg after the polygonal
  eye fusion. The final method trims a full torus for the eye and joins its
  leads before adding complete legs. This also repairs the two older cotter
  definitions identified by the focused audit.
- `tolerance_roundoff`: all52 raw/bounded STEP material comparisons were zero,
  but the input-pin tolerance report drifted by1.35e-11mm. The final validator
  declares1e-10mm reporting roundoff without editing either shape's tolerance.
  It retains the native tolerance ceiling and exact material-difference gates.

Each trial retains its exact builder inputs and terminal log; completed trials
also retain fit, exchange and overall reports. Failed native and STEP files are
preserved in the durable `.work/transmission-input-installation-study` folder,
with `rejected_` and `swept_` prefixes respectively. They are not promoted into
the delivered standard tank. The missing-leg candidate is retained there with
the `missing_leg_` prefix. The accepted candidate uses analytic arc solids,
and its independent checks require both cotter legs and their formed tails.
