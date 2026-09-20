# Driving-wheel shaft and mounting study

This isolated study is preparation for the next standard-assembly increment.
It is not part of the delivered tank. See [the packet](../../packets/R02-drive-mounts.md)
for source scopes and unresolved installation interfaces.

`probe.py` constructs a seven-leaf shaft assembly, inner/outer bearings,
backing plate, two nut locking plates and positively allocated fasteners around
the existing wheel. Printed shaft, key and fastener dimensions are retained;
`hypotheses.json` identifies the inferred journal, casting and attachment geometry.
The native fixture contains 149 physical occurrences and two explicitly marked
receiver coupons. These coupons do not establish fit to the actual hull plates.

The revised fixture passes 441 material candidate pairs with zero overlaps and
39 bearing-face checks. A fresh reopen confirms 23 valid single-solid definitions,
151 occurrences, the 39 seats and printed shaft/key bounds. Moving an end nut
outward by 0.2 mm correctly loses its bearing face. Printed shaft and bush sizes
give 0.04445 mm radial clearance; historical tolerances remain unqualified.

The first locking-plate proposal collided with one neighboring head at each end.
`rejected_initial/` preserves that result. Inferred scallops in the revised plate
clear the heads while retaining the nut-flat and bearing-face contacts. This
resolves the geometric interference, not the historical casting or load capacity.

Open [the assembled view](build/assembled.png), [mounts](build/mounts.png), or
`build/DriveMountStudy.FCStd`. In the GUI hide `Library` and show `Fixture`.
The saved reports bind the native file and reviewed images by SHA-256. Copies
of the executed construction and reopen scripts are preserved beside them;
the reopen copy records its original execution paths rather than serving as a
portable launcher. Regeneration is guarded by the authored-input fingerprint.

The source review found a more specific plate-mapping problem than a seam
offset: M1977 receives the rear driving-wheel bearing M1406, while M1978 receives
the forward roller-pinion bearing M1546. Cross-member rivet allocations pair
M1977 with outer M1975 and M1978 with outer M1976. The original inferred inner
fore/aft assignments appear reversed. `receiver_source_rows.json` preserves
these rows; correction and actual installation checks remain pending. Exact
inner seams and the lower skirt boundary still require bounded hypotheses.

Further M1552 plate-only rivets, thread forms, exact profiles, lubrication
passages, historical fit and continuous track engagement remain open.

## Actual receiver trial

`receiver_probe.py` records the unmodified tank's receiver problem. The inner
bearing touches M1978, while M1977 is 387.295 mm away. Both bearing footprints
cross the old inferred skirt seam. Twenty material overlaps include the missing
attachment bores and bearing barrels intruding into the skirt. Its corrected
diagnostic render uses a unique mesh-cache key for each directly installed target;
the render provenance and executed redraw script are preserved alongside it.

`installed_probe.py` tests 56 new shaft/mount occurrences and 12 reconstructed
rear hull plates at both fixed drive axes. Source identities stay with their
definitions; the inner fore/aft geometric slots are corrected from the bearing
and cross-member allocations. A level provisional skirt border continues from
source pixel [1630,500] to [1800,500], meeting the rising hull outline naturally.
The previous attempt to return to [1800,430] left a disconnected or invalid
skirt; its script and rejection are preserved in `rejected_receiver_border/`.

The [installed receiver view](installed_build/receivers.png) exposes the complete
outer bearing footprint and attachment hardware. All 430 changed/new material
candidates clear the existing physical tank. Twenty-six hull bearing/rivet
contacts and 32 receiving-hole ring checks pass. `reopen_installed.py` freshly
opens the saved file, verifies all 68 single-solid occurrences, confirms the
26 contacts and measures a complete 12 mm native cylindrical wall at each of
the 32 holes. A displaced rivet correctly loses its receiving seat.

Replacing the trial plates in the full native context also retains all 424
lower-support bearing faces, 34 angle/hull contacts and 76 lower attachment
bores. Source identities, shaft axes, source scale and the frozen main model
inputs remain unchanged. These results support integration of this bounded
approximation; they do not prove exact historical seams or casting geometry.
The trial is still separate from the main build and snapshot sequence.

## Reusable adapter draft

`integration_draft/` contains the next native builders and derived mounting
datums, outside the active main-model imports. `check_draft.py` verifies all ten
new nominal definitions by native subtraction against the inspected fixture and
all 28 added placements against its saved links. Three trials (nominal, shaft
length +2 mm, frame spacing +10 mm) each pass 39 bearing contacts and 441 material
candidate pairs. Head across-flats dimensions and stocks are exposed as inferred
controls. These checks support transferring the construction; they do not replace
main-registry source reconciliation or full integrated delivery qualification.

## Qualified integration

The source-correct receiver and mounting hypothesis is now in the qualified
partial tank stage, preserved as snapshot010. All fifteen parameter trials pass.
The private preflight, corrected pipe-plug check and rejected shoulder-seat
assumption are preserved in `integration_preflight`. Earlier studies retain
their original inputs and claims. Historical fit, threads, sealing, retention
and extra plate-only rivets remain unresolved.
