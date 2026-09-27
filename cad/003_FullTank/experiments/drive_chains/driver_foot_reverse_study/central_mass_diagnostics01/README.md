# Bridle integration discrepancy

`central03` and `central_variation03` exchange01 preserve a failed application of
the specialized V6 trimmed-surface integrator. Native and STEP have zero material
differences, empty fuzzy differences, valid closed solids and acceptable kernel
tolerances. Nevertheless, V6 reports native/STEP centroid differences of 2.207 and
2.288 mm. Its two precision requests converge internally while disagreeing across
representations. The underlying face-integration cause is not yet isolated;
previous control qualification does not establish applicability to this bridle.

The independent diagnostic measures the unchanged native and exact STEP solid in
definition and installed coordinates with standard adaptive Gauss and
Gauss–Kronrod. Standard Gauss passes the existing error/convergence predicates for
all eight measurements and agrees across representations. GK fails its predicates
and is not used. No native geometry, STEP bytes or numerical limits are changed.

Exchange02 attempts to reuse passing rows, but refuses a serialized BRep-hash
mismatch before prior Boolean operations. It makes no acceptance claim. Exchange03
therefore reruns all 17 strict comparisons per case using standard Gauss and the
unchanged original STEP files. Both cases pass. Failure logs and worker versions
are retained; cache reuse is never accepted on a hash mismatch.

Prefer the standard mass method first. Use specialized alternatives only after a
diagnosed failure, with evidence for the actual new surface class. Internal
quadrature convergence alone cannot establish correctness across representations.
