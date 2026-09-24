# P01 — low-speed and track brake stops

Status: **active; experimental geometry, not accepted**. Configuration remains
the standard Rock Island reconstruction, before pose variants. The locally
qualified parent is the front-brake checkpoint `169c3da`; this study does not
replace it yet.

The latest local candidate is
[trial04](../experiments/drive_chains/transmission_brake_stop_study/trial04/README.md).
It revises the previously estimated lower cap-stud station and stud allocation,
retaining source stock lengths and the shaft socket. Rounded lower bosses and
connecting webs replace trial03's overly bulky casting. Its 55 mounting and 71
joint/ownership checks pass; historical casting profiles and the transverse
arrangement remain conditional. The earlier trial02 account below is retained
as the preceding experiment, not the current mounting geometry.

The deliverable is four lower-band stop joints and two support assemblies, with
individually owned lugs, adjusters, nuts and rivets. The current
[trial02 record](../experiments/drive_chains/transmission_brake_stop_study/trial02/README.md)
contains the native candidate and diagnostics. A mechanically fitting candidate
does not settle the hidden transverse arrangement or the conflicting part marks.

## Evidence and decisions

The [source packet](../experiments/drive_chains/transmission_brake_stop_study/sources.json)
retains 24 catalogue/legend records, service prose, manual image picks and 18
source-image hashes. Original SNL41 was directly checked. HB134/135 and original
SNL31/32 supply the illustrated arrangement. HB73/123 shaft sections and HB79's
photograph do not resolve the installed crossbar's transverse shape.

| Item | Source | Installed quantity / current interpretation |
|---|---|---|
| MX86 / MX87 lugs | SNL122:022/024; lower-band assemblies | Two each; curved feet riveted to the lower bands |
| Countersunk steel rivets | SNL191:007 | Three per lug, twelve total; quarter inch × 1 3/16 inch stock |
| M343 stop screw | SNL205:010–013; HB101/102 callout 9 | Four, each with one half-inch SAE hex nut; approximately tangential axis in HB134/135 |
| MX88 bar set screw | SNL205:014–017; HB134/135 | Four, each with one half-inch SAE hex nut; approximately radial axis |
| M341 / M342 support assembly | SNL41:022–026; HB207 | Two assemblies, each one bracket, one bar and four quarter inch × 1¼ inch button rivets |
| MX95-RH / MX96-LH | Labels in HB134/135 | Illustrated diagonal supports; relation to M341/M342 unresolved, not asserted as aliases |
| Removable mounting | HB154 low-gear relining prose | One nut releases the illustrated brake stop from the epicyclic frame; exact catalogue fastener allocation not found |

The current hypothesis places one M342 crossbar across the low-speed and track
bands on each side, carried by an M341 strut under an existing inner bearing-cap
nut. This is consistent with the two-versus-four quantities, but no inspected
transverse view proves it. It is not a historical configuration selection.
The same lower inboard stud is used on each hand; no extra unlisted mount bolts
are counted. Its stud, nut and cotter advance by the estimated 6.35 mm tab stock.
Source stud lengths stay fixed. Reduced embedded length remains to be qualified.

SNL252:026 also exposes an inventory gap: four **SH687A brake-adjusting spring
spacers** are absent from the front checkpoint. Their form and position need a
separate source check. MX60/MX38/MX76 anchor/coupling screws remain unresolved.

## Parameters and interfaces

[Controls](../experiments/drive_chains/transmission_brake_stop_study/controls.json)
distinguish printed rivet stock, screw diameter inferred from matching nuts, and
all other estimated dimensions. Millimetres are used. Source uncertainty is
separate from the 0.15 mm radial bore allowance and numerical comparison limits.

Definitions use U tangent forward/up, V opposite world Y and W radially outward,
at a provisional -52° band station. The low and track backing radii remain
312.7375 and 319.0875 mm. Each lug has a curved foot, a flat radial screw seat and
a tangential screw boss. Its three rivets lie at -49°; adjacent original copper
lining rivets are retained without extending or moving them.

The shared bar occupies W348–360.7 mm. Different radial screw settings bridge
the different band radii, while the tangential screws meet the same bar edge.
The four band-mounted M343 screws belong to the lower-band stop joints. The
four MX88 screws and their nuts belong to the support assemblies. M341/M342 and
their eight button rivets have one owner per vehicle side.

Only the four lower-band links switch to new drilled backing definitions; all
upper bands retain the existing definition. Two source designs now each have an
upper and a lower reconstruction definition, not additional inventory pieces.
All dimensions require regeneration; custom properties are not live constraints.

## Verification and disposition

Trial01 found ten material interferences: eight rivet-head/web clashes and two
rectangular mounting-tab/cap clashes. Trial02 moves the four bar rivets farther
from the strut web and uses a circular mounting eye inside the existing nut seat.
The failed candidate and its diagnostic remain available.

Trial02 has **3,001 physical occurrences, 503 definitions and 295 assemblies**:
44 added parts, four replacement lower-band occurrences and six moved pieces of
existing mounting hardware. The saved-native diagnostic finds eleven valid,
closed, single-solid definitions with identity frames; all 57 count/frame checks
pass. There are no material overlaps above 1e-5 mm³ in 492 development candidate
pairs, and no invalid common results. Eighteen screw/nut/bar planar contacts have
positive area. These are preliminary diagnostics, not a complete native release
gate or a historical fit certification.

Fixed-channel overlays retain the source discrepancy. At the estimated mounting
nut midpoint the model is about **38.5 mm rearward / 38.6 mm high** in HB134 and
**51.9 mm rearward / 28.7 mm high** in HB135. Approximate screw-axis differences
are 4.2° / 6.2° for M343 and 0.6° / 1.0° for MX88. Picks have ±5 px uncertainty;
their short spans and scan distortion limit the angle comparison. These values
are conditional measurements, not printed dimensions or a reason to hide the
mounting mismatch by changing registration.

Before accepting a stop checkpoint: review source ownership and the bearing-cap
mount discrepancy; verify curved foot coverage, drilled material changes, rivet
stock/retention and planar mount bearing; qualify remaining stud engagement and
the necessary removal sequence; preserve every unaffected definition/frame;
run retained standard-context checks, strict STEP exchange, fresh reproduction
and a meaningful parameter variation. Historical and installation qualification
remain false. The standard tank assembly is unchanged.

Next complete this support decision and qualification, then continue high-speed
brakes, control rods, remaining frame/hull joints, engine systems and other
interiors, inventory reconciliation and standard integration. The full tank and
selected later poses remain the objective.
