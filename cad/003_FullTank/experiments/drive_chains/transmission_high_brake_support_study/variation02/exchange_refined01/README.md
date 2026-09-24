# Receiver stock variation — completed STEP check

The retained M362 bracket-stock variation adds 1 mm. Its existing native and
interface checks already passed. The initial STEP round trip preserved all
material and tolerances, but the large case failed default mass convergence.
The failed receipt and STEP files remain in the parent directory.

All 13 comparisons now pass using the previously qualified refined quadrature
for that case. The nine independent analytic/transform controls in
`../../receivers04/diagnostics/refined_mass_controls/qualification.json` are
hash-bound in the new receipt. Geometry and acceptance limits are unchanged.
This closes the earlier variation STEP gap; complete packet qualification is
separate.
