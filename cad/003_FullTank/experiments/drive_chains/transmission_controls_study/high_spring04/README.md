# Rear high-speed spring guides — local prototype

[RearHighSpringBrackets.FCStd](RearHighSpringBrackets.FCStd) contains a revised
receiving channel, two M4135 guide brackets and four rivets: seven occurrences
using three shared definitions. The six proposed new parts are **not yet
integrated** into the development assembly. Its authoritative native remains
[the fulcrum checkpoint](../fulcrum_integrated01/README.md), with 3,226 occurrences,
558 used definitions and 347 groups. Standard tank011 is unchanged.

## Source identity correction

The additive [source packet](../spring_sources01/sources.json) retains 53 rows
and corrects the four short-connection labels in the earlier
[interface measurements](../fulcrum_integrated01/operating_interfaces.json).
Their coordinates and pin axes remain valid; the old receipt is preserved.

| Short connection, two per tank | SNL identity | Corresponding handbook tube | Fork at both ends |
|---|---|---|---|
| Foot/track brake | SH946D | M577 | M569C |
| Low-speed brake | SH946E | M572 | M569A |

M578 and M573 name the longer rear rods between the center controls and the
other horizontal-lever arms. The handbook/SNL tube correspondence is a functional
interpretation, not proven dimensional interchangeability. Original SNL pages
86, 87, 194 and 195 distinguish these applications. M569A's one-inch length lacks
an explicit datum; M568A's conflicting catalogue lengths remain unresolved.

## Geometry and retained alternatives

M4135 uses an estimated 6.35 mm plate against the rear vertical channel flange,
with a 20 mm guide bore at Z = 606.927941 mm. Four source-listed half-inch by
three-quarter-inch rivets pass through actual receiving holes. Stock length is
interpreted as unformed shank; the upset tail conserves the remaining stock
volume. Plate contour, stock, attachment orientation, guide diameter and stations
are reconstruction estimates.

The starboard guide follows Y = -222.25 mm. The port guide is at Y = 273.05 mm,
50.8 mm outward from its brake-eye lane, to clear the current asymmetric clutch
support and auxiliary pin. This offset is a coupled rod-route hypothesis, not a
dimension recovered from a drawing. Existing clutch geometry is itself approximate.
The thicker-stock trial uses 6.85 mm plate and moves its outer face back 0.5 mm,
keeping the receiving plane fixed and adjusting rivet grip/upset volume.

| Candidate | Finding |
|---|---|
| high_spring01 | Top-mounted foot intersects five retained material pairs. |
| high_spring02 | Rear-flange bracket at the straight port lane intersects the left casting. |
| high_spring03 | A 38.1 mm port offset clears the bracket, but the rod envelope clips the auxiliary pin by 29.163969 mm³. |
| high_spring04 | A 50.8 mm port offset clears both bracket and local route checks. |

All candidates, failed checks and frozen inputs are retained. The variation03
native was generated but not qualified; variation04 is the tested stock variant.

## Validation and visual limits

Nominal and thicker stock each pass 32 saved-native/interface checks, 21 local
material comparisons, two surrounding-material comparisons and ten strict STEP
comparisons (three definitions plus seven installed shapes). Context screening
includes all 3,226 parent occurrences and 5,316 retained standard solids. Native
links reopen after relocation. Checks cover actual cylindrical passages, receiving
holes, seating, head/tail bearing and source stock volume. STEP checks compare
missing/added material, face tolerances and converged adaptive mass properties.

Fresh nominal generation passes seven reproduction checks: nine archive BReps,
659 persistent properties, occurrence frames and hierarchy agree. Whole FCStd
archive byte identity is not claimed. The source packet reproduces byte for byte.

The [local route study](../high_spring_routes04/route_checks.json) and stock variant
each pass 29 material comparisons. They contain 19.05 mm rod envelopes joining
the saved M569B socket directions to the guides, plus 32 mm spring envelopes.
Line/Bezier/line paths test local feasibility only. Sampled curvature is not a
forming limit, and these witnesses do not constitute completed M575 rods,
source-supported springs, remote connections, movement or service qualification.

The [reviewed source overlay](../high_spring_routes04/route_source_detail.png)
uses the existing local SNL6 registration without refitting. The provisional
route remains below the drawn rod level and its bend differs from the source.
The earlier 21.867 px high-speed control-bore discrepancy remains open. Passing
clearance checks does not resolve that historical disagreement. HB104 remains
an uncalibrated photograph; plan picks and estimated route points are not
independent camera holdouts.

Reuse this camera for routine additions. Reverify affected landmarks when a
supported interface changes or new geometry supplies independent depth evidence.
Investigate coherent disagreement across reliable parts before adopting a new
fit; compare old and proposed cameras against the same geometry and holdouts.
Do not adjust the camera to conceal this provisional rod mismatch.

## Continuation

Establish M4136 and M4129 mounting topology and the corrected SH946D/SH946E short
connections, then complete M575 and the long rear rods with their real spring
interfaces. Integrate the connected support family after these relationships
are checked, reusing the bounded prototype evidence where geometry is identical.
This avoids repeatedly rechecking the whole hierarchy for isolated additions.

The hash-bound [study receipt](../high_spring_study_receipt01.json) records the
scope and preserved failures. Read-only recovery requires no CAD regeneration:

```sh
python3 cad/003_FullTank/experiments/drive_chains/verify_rear_high_spring_study.py
```
