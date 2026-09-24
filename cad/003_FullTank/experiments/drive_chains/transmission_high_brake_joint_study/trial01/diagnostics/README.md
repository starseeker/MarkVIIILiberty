# Retained rear-joint diagnostics

The first short backing passed single-solid validity but contained material
outside its intended annulus and overlapped rivet 2 by 388.417413 mm³ per brake.
`initial_interference` retains the failed checker, part generator, receipt and
material witnesses. Making the extended annulus as one profile alone then failed
validity (`build02.log`). Neither candidate was accepted.

`short_cut_probe` compares equivalent ways to make the six countersinks. The
unchanged circular cutter rotated 90 degrees about its own axis gives a valid
in-stock band with zero rivet overlap. A separately constructed direct-axis
cutter produces exactly the same material in both Boolean directions, without
fuzzy tolerance (`comparison.json`). The corrected saved native also passes the
independent stock, seating and development-interference checks. These results
implicate the cutter parameterization; they do not establish a general kernel
root cause. The diagnostic scripts retain their original working paths.

`initial_exchange` preserves the first complete 41-comparison STEP report and
STEP files. Only the M361 definition and its two occurrences failed: mass
integration reported about 1.17e-12 against requested 1e-12, despite stable mass,
empty material differences and lower STEP tolerance. The first axial-section
measurement probe failed section topology and was rejected. Definition-Z
sections passed the existing PartitionedMass criteria, including complete
material coverage, no overlap and independent refinement. The final exchange
receipt retains both whole-solid and successful section measurements. Neither
the exported geometry nor the acceptance limits changed.
