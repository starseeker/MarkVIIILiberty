# Operating-handle length and registration review

The current native assembly remains
[operating_integrated01](../operating_integrated01/README.md). This review changes
neither geometry nor source cameras. It follows the complete-handle checkpoint
and tests whether its grip discrepancies could be explained by the stated
registration uncertainty.

## Finding

**The plan discrepancy survives the existing pick allowances.** With independent
5 px disks around the two main-shaft endpoints and each source grip, the smallest
possible residual is **31.47 px port / 32.90 px starboard**. Interpreting the
allowance more generously as +/-5 px in each coordinate still leaves conservative
lower bounds of **24.97 / 26.40 px**. These are conditional geometric bounds, not
statistical confidence intervals or historical accuracy estimates.

The [inspected diagnostic](plan_uncertainty.png) shows source picks in red,
saved-native grip projections in blue, and shaft anchors in green. Dashed blue
disks bound hypothetical projection changes; no alternate camera is adopted.
The [report](report.json) binds the original sources, accepted native hash,
measurement receipts, worker and calculation controls.

For shaft endpoints `a,b`, printed span `S`, and saved coordinates `X,Y` relative
to the main shaft, complex image coordinates give
`p=(a+b)/2 + ((Y+iX)/S)*(b-a)`. Endpoint disk radius `e` therefore gives an exact
projected disk radius `e*(|1/2-w|+|1/2+w|)`, where `w=(Y+iX)/S`.
The report reproduces the saved projection and verifies an explicit pair of
endpoint shifts attaining the boundary. Shaft endpoint, midpoint and image
translation controls also pass. The two-sided disk bound intentionally allows
more freedom than preserving all other drawing landmarks; a positive residual
therefore cannot be removed by adding those constraints.

## Original source review

The original HB148 scan says that the speed-control levers are 37 inches long,
without identifying the measurement endpoints. Nearby wording is more explicit:
HB149 calls the pedal length "over all" and measures the clutch hand end from the
fulcrum centre; HB150 refers to the hand side of the reverse-lever fulcrum.
This comparison confirms ambiguity, not a particular replacement dimension.

The nominal HB113 side projection puts the speed grip **940.88 mm from the main
shaft axis**, close to 939.8 mm. That supports testing a functional-radius
interpretation, but does not establish it. Its scale is derived through the
estimated main/swing shaft separation. The larger cap-to-handle-pivot radius is
still inconsistent with a simple rotation of the unchanged current handle under
the nominal registrations; see the preceding
[saved-native diagnosis](../operating_integrated01/source_comparison_diagnosis.json).

The full figures were reviewed, including their callouts. HB113 and SNL6 repeat
substantially the same control layout, so agreement between them is not two
independent sets of engineering measurements. HB93 illustrates lateral high/low
selection pictorially. HB6 is a perspective interior photograph useful for seat,
control and ammunition-storage context; no metric camera has been established
for it. Neither justifies adjusting the whole driver station to absorb the grip
error. Broken long rods remain excluded from source scaling.

## Next bounded geometry experiment

Compare the existing overall-extent interpretation with a **separately labelled
functional-radius hypothesis** using complete handles and fulcrums. Preserve the
printed number and record which datum each hypothesis assigns to it. Keep source
registrations fixed and report grip, pivot and selector residuals for each.

Check full stock, selector engagement, pivot joints and the actual front hull
before considering integration. A profile that improves an overlay but enters
the hull is a failed candidate. If no local interpretation satisfies these
constraints, review the coupled driver/hull station using independent evidence
before changing the inherited rods or mounting datums. Keep upper fittings
dependent on explicit handle datums so any later justified revision is traceable.

This review does not settle the 37-inch datum, establish a matching source pose,
or qualify the controls' operation. The previously checked approximation remains
usable as a development checkpoint; the historical placement question stays open.

Reproduce in a fresh directory:

```sh
MPLCONFIGDIR=.work/driver-handles-20260927/matplotlib python3 cad/003_FullTank/experiments/drive_chains/review_driver_handle_datums.py --output .work/driver-handles-20260927/datum-review-reproduction
```
