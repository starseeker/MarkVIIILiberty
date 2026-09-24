# Rear transmission brake anchors

The saved development assembly adds eight rear brackets, four anchor pins,
four retaining springs, two spacers, four retainer rivets and 60 steel rivets.
Sixteen existing copper lining rivets use longer stock through the bracket feet.
It contains **2,857 physical occurrences, 484 definitions and 276 assemblies**.

Open [PowertrainWithBrakeAnchors.FCStd](PowertrainWithBrakeAnchors.FCStd) for the
native hierarchy. The [isometric](isometric.png), [inner detail](anchor_detail.png)
and [outer detail](anchor_back.png) show the saved solids. The detail images use
display crops; their cut edges and cropped rivet heads do not change the model.
[Low-speed](lowspeed_source_overlay.png) and [track](track_source_overlay.png)
overlays retain the previous handbook channel registration and its residual.

## Source decisions and approximation

SNL9–11,39,41 identify one front ear and one rear bracket per half-band. This
stage supplies the rear MX49/MX47 brackets only. The source-handed spring
locations are low-speed port lower/starboard upper and track port upper/starboard
lower. M348/M353 pins pass through both estimated bracket lugs and the inboard
M337 suspension link.

MX82 spacers preserve the printed 0.189 inch bore, half-inch outside diameter
and three-eighth-inch thickness. Rear steel-rivet counts are eight per MX49 and
seven per MX47. The later SNL quarter-inch by 1⅜ inch copper-rivet stock is used
at the 16 covered lining holes; the earlier handbook segmented lining lengths
and pitches remain unchanged. Later long-strip quantities are not added.

The rear half-gap grows from 1 to 5 degrees. Each lining group advances four
degrees toward the front; the steel band definition follows its pattern.
Only the new steel-rivet holes and the filled, covered upset pockets alter
backing material relative to this rotation. Opposite halves reuse the same
bracket by rigid rotation, retaining source quantities and separate links.

The hidden transverse arrangement, lug profiles and stock, pin sections,
grooves, forked retaining springs, fitted clearances and rivet heads are
estimates. Track lugs sit 6.35 mm inside the band edges to clear the chain cases;
low-speed lugs lie at the edges with the source spacers outside. Retainer studs
are estimated 5 mm forward and 19.05 mm above the anchor. Parameter properties
are documented inputs; changes require regeneration with the builder.

Rivet forming uses the generator's documented below-head stock-volume
convention. The catalogue listing does not establish the historical finished
head dimensions or forming operation. This is a geometric reconstruction,
without load, spring-deflection or manufacturing-process qualification.

HB service prose refers to coupling screws after anchor-pin removal. That
detail, the additional SNL MX49 button-rivet application and the original
production joint arrangement remain unresolved. The channel-registered model
anchor is forward and below the pictured station. Neither historical agreement
nor a service/removal sequence is claimed merely because the solids fit.

## Verification status

Native checks pass: 106 checks and 1,362 development material pairs, including
all 330 affected occurrences. Spatial filtering covers all 5,316 retained
standard-context occurrences and finds no possible pair. The checks include
complete bracket-foot support, bore voids, rivet seats, source handedness,
pin-retention witnesses and displaced/plugged negative controls.

All 472 unchanged inherited definitions pass preservation checks. Fresh
reproduction matches 1,478 BReps, 10,191 object types and 133,313 persistent
properties. A variation adds 0.25 mm foot stock and 0.5 mm track-lug inset;
it passes the same native/context checks and retains all 472 unchanged nominal
definition BReps. Variant STEP exchange is not separately qualified.

All **342 STEP comparisons pass**: 12 new/changed definitions and all 330
affected installed occurrences. Strict material/tolerance checks and converged
adaptive mass integration retain the previous acceptance limits.
`validation_receipt.json` binds the completed checks to the saved native file.
Preservation uses 453 exact BReps and 19 strict material comparisons. Five
reviewed progression images bring the total to 183, preserving 178 prior images
and 30 native baselines.

The initial foot-seat check excluded small support patches at restored rivet
pockets. [The retained diagnostic](diagnostics/seat_coverage/README.md) explains
the correction; full union coverage passes without changing geometry or
relaxing tolerances. Earlier layout probes also remain recorded.

## Remaining work

Front ears, M336 pins, adjusting screws/springs, levers, stops, support fastening
and high-speed brake fittings remain incomplete. The broader workflow still
requires frame/hull joints, full engine and compartment equipment, inventory
reconciliation, standard-tank integration and final qualification. Standard
tank011 is unchanged. Pose variants remain deferred.
