# R02 — partial front idler wheels

Standard configuration, 20 September 2026. This stage replaces both annular
layout envelopes with individual native wheel constituents and bushes. The
shaft and adjustment installations remain incomplete; no operating pose or
continuous engagement is claimed.

## Composition and source identity

Each rotating wheel has 119 leaves: two rims, two disks, one boss, five X
and one Y diaphragm, plus 36 short, 24 long and 48 rim rivets. SNL274:023–028
and 275:001–004 control that composition, independently checked against the
frozen survey BOM. The two M1409 bushes per wheel belong to the shaft assembly,
SNL214:021–028, rather than the riveted wheel itself. The current two installations
therefore contain **242 physical leaves from nine native definitions**.

The shaft template explicitly accounts for its seven missing leaves: shaft,
two nuts, two locking screws and two oil plugs. Its composition report is
`complete: false`, even though its modeled-plus-omitted quantities reconcile.
A missing component cannot silently become an accepted partial assembly.
Shared whole-tank boss/disk/bush quantities are not treated as per-idler counts.
Drive and roller-pinion installations remain to be added.

The original SNL274 constituent literally prints M147. HB235:049 and SNL189:007
identify the adjusting-wheel rim as M1471. The model provisionally equates these
roles while preserving both frozen survey identities; its rim definition uses
the SNL274 constituent identity, with an explicit candidate-equivalence record.
No duplicate rim or finished coverage is created from that alias.

M1405X and Y retain separate source identities and definitions. Their distinguishing
feature is not resolved; they currently share the same approximate primary shape.
This is a limitation, not proof of interchangeability.

## Native construction and dimensions

The running diameter remains the handbook's **40.187 inches / 1020.7498 mm**.
M1409 bushes retain the SNL **129.9972 mm OD, 112.7125 mm ID and 203.2 mm length**.
Rivets retain the three printed shank diameters and under-head stock lengths.
Their installed grips are 25.4, 50.8 and 38.1 mm respectively. Each inferred
spherical upset tail conserves the printed shank stock volume; head profiles
and joint assignments remain approximations.

The rims use separate revolved running/attachment sections. Each disk has six
large lightening openings and separate joint drilling. The boss has a through
bore, end journals, two flanges and the long-rivet holes. Each diaphragm uses a
native constrained sketch with cubic NURBS relief boundaries, a padded web,
formed attachment flanges and drilling. Circular openings, fits, stocks,
curves and rivet patterns are controlled by the documented `wheel_*` parameters.
The resulting forms are source-informed reconstructions, not measured originals.
All nine definitions remain `partial`.

The rim/disk attachment-land orientation is also provisional: the current disks
are outboard, while a possible inboard reading of the source section still needs
a complete interface trial. See the research packet’s queued refinement.

The 50.8 mm rim width and ±190 mm axial centers are inferred. A possible transfer
from the two-inch drive-rim width is unconfirmed. Narrow rims lie between the
track rail bars and approach the transverse track bushings. HB138's wording and
the narrow section support investigating this arrangement, but do not establish
its historical correctness. The earlier wide-rim rail-contact alternative remains
in [the research packet](R02-idler-research.md).

## Coupled static installation

The independent SNL2 shaft pick stays at pixel (194,339), X 9167.058208 /
Z 1517.637951 mm. Holding that Z, the model solves a local X adjustment against
the reconstructed track's actual pin centers. The nominal result is
X 9163.195854 mm, **3.862354 mm rearward**, for a 0.5 mm unloaded rim/bushing gap.
The ±100 mm numerical search bound is not a historical travel allowance.
The native BRep validator independently measures both rims on both hands.

The first installation revealed an idler/foremost-roller collision. The prior
roller fit had raised Lower00 by 41.494 mm to meet the reconstructed rail.
Trials at 24.108 and 36.162 mm rearward still overlapped the new rim. Lower00
now has an explicit **45 mm rearward X offset** while retaining its original
pixel (202,444). This exceeds the original ±6-pixel horizontal allowance
(36.162 mm) by **8.838 mm**. Its rail-derived Z and every other station remain
separately reported; the calibration, printed pitch and idler diameter were not
changed to conceal the discrepancy. The hull's roller shaft openings follow the
updated station through their existing parameter dependency.

This placement improves physical consistency but is not historical-fit evidence.
The track route and inferred roller shoulders remain relevant uncertainties.
Future source or interface corrections may supersede the offset.

## Verification

The integrated prototype has 716 internal and 162 external candidate material
pairs, zero overlap, four 0.5 mm native rim/bushing gaps, and four approximately
1.686894 mm rim/foremost-roller gaps. Twelve representative rivets (both sides,
three sizes, both wheels) seat both heads against native joint faces. Printed
wheel/bush dimensions and all three rivet stock volumes pass.

The full delivery additionally runs saved-native validity and placements,
component/layout STEP round trips, relocated external links, independent rebuild,
cache reuse and an idler-diameter perturbation alongside the existing parameter
trials. Track-pitch changes update idler placement without changing wheel stock.
Read the current machine-readable `build/reports/validation.json` for qualification
status; a prototype pass alone does not qualify the delivered assembly.

Visual review identifies a shape refinement still needed: the native diaphragm
waist is smoothly rounded, while the source section has a flatter central trough
and steeper shoulders. No dimensional claim is inferred from that qualitative
difference. Preserve it for shared wheel-section refinement.

The comparison bundle includes wheel oblique/elevation, a transverse half section,
and the wheel with track units 18–26 and the foremost roller. These are compared
with HB87 / SNL28 without claiming metric calibration of the plate figure.
Most wheel detail is enclosed by the hull in the standard exterior isometric.

## Next installation work

Reconstruct M1474 shafts, M1477 nuts, M1475 locking screws, M1476 copper plugs,
M1473 tension screws, M1472 brackets, M1484 plates, M1483 washers, M1479 guards and
attachment hardware. Resolve the sliding interfaces and owned hull openings
before claiming a complete front-wheel installation. Keep the 171.45 × 120.65 mm
printed opening distinct from an assumed shaft-travel envelope. See
[the retained source research](R02-idler-research.md) for locators and scope.

## Delivered qualification

The full delivery passes all implemented checks: 203 native definitions, 4,675
placements, separate STEP round trips, relocated external links, independent
rebuild/cache reuse and all nine parameter trials. Independent/cached native
build times were 53.01 / 42.09 s. The 25 record/renderer tests pass.
Snapshots 001–005 are unchanged; the inspected standard isometric is preserved
as 006, with a separate idler close-up. All physical definitions remain partial.

## Subsequent mounting stage

The current delivery is the [idler-mount stage](R02-idler-mounts.md). It adds the
shaft/adjustment hardware and refines this wheel section to nested disks on
inboard rim lands with a flatter diaphragm trough. The original wheel-only
measurements above describe snapshot 006; current source-axis fitting, native
checks and snapshot 007 are recorded in the mounting packet.
