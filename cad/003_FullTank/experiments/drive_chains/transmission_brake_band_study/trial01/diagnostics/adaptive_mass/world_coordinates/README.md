# Extra net-volume diagnostic

The first adaptive exchange pass added an absolute **net integrated volume**
difference requirement of 1e-5 mm³ to the original exchange criteria. Four
installed drums failed this added predicate, by 0.00002651–0.00010724 mm³ on
volumes of 5.5–8.8 million mm³ (relative differences 3e-12–2e-11). All original
material, topology and kernel-tolerance predicates pass, and adaptive centroid
errors are below 0.00000000032 mm. Both adaptive integrations converge.

Moving both shapes into a common translated or fully inverse installation frame
does not remove these tiny net-volume differences. The retained replay disproves
simple global-origin cancellation as the cause. The STEP file writes finite
coordinate precision; exact attribution between exchange rounding and integration
is not independently established. Do not claim byte-identical geometry.

The final acceptance retains the **original** thresholds of 1e-5 mm³ on missing
and added material, empty fuzzy difference topology, 1e-5 mm centroid error and
unchanged maximum kernel tolerance. It additionally requires adaptive-integration
convergence. Net-volume differences are reported separately; the new diagnostic
predicate is not used as a substitute for the stronger spatial material tests.
No geometric tolerance was raised, geometry changed, or failed report discarded.
