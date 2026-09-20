# R02 — chain sprockets and roller pinions

Preparatory source review, 20 September 2026. This packet does not add geometry
to the tank. The [evidence folder](../experiments/roller_pinions/source_review.json)
preserves inspected source hashes, source rows and printed controls separately
from the authored model.

## Assembly scope

SNL144:002–006 gives two complete pinion assemblies. Each contains one M1541
casting, eighteen roller-pin assemblies and eighteen M1542 rollers. Each pin
assembly in SNL143:007–011 contains an M1543 pin, a 5/16 × 1 3/4 inch split pin
and a 1/8 inch square-head brass pipe plug. The rotating assembly therefore has
**73 physical leaves per side**. Model the nested pin assemblies explicitly;
do not count their assembly parents as additional physical parts.

SNL215:009–013 gives a separate four-leaf shaft assembly: M1544 shaft,
20297/D89 key and two Q52E 3/4 inch pipe plugs. Its two M1409 bushes are supported
by SNL43:011 and HB printed p134 but absent from that four-leaf BOM. Keep them
outside the source-defined shaft assembly. Unlike the driving-wheel shaft,
this BOM does not include M1477 nuts or M1411 locking plates.

The support scope includes one M1546 inner bearing, one common M1407 outer
bearing and one common M1552 backing plate per side. SNL189:008 assigns six
3/4 × 2 1/2 inch rivets to each M1978/M1546 inner joint. SNL201:008 assigns six
3/4 × 2 1/4 inch cap screws per M1407. SNL170:004 explicitly assigns four
1/2 × 1 3/4 inch rivets to each M1976/M1552 outer joint. Its additional
plate-only M1552 allocation remains unresolved. These named supports add
nineteen physical leaves per side, giving a preliminary scope of 98 per side
including the rotating assembly, shaft assembly and two bushes. This is a
planning subtotal, not a completed vehicle quantity reconciliation.

## Printed dimensions and observed topology

HB printed p132 (original scan `MarkVIII067.jpg`) describes a single unit
casting with the chain sprocket centered between two roller pinions. HB
Plate 81 (p129) shows the sectional arrangement; HB Plate 82 (p131) and SNL
Plate 25 show the installed assembly. The eighteen rollers divide into two
nine-roller banks. Do not confuse the **23 central chain teeth** with the nine
roller stations or the unresolved 35/37 teeth on the separate driving wheel.

| Control | Printed inches | Millimetres |
|---|---:|---:|
| Casting overall length | 19.5 | 495.3 |
| Diameter at roller-pin bosses | 13.687 | 347.6498 |
| Chain sprocket diameter | 23.031 | 584.9874 |
| Chain tooth width | 1.39 | 35.306 |
| Roller diameter | 2 | 50.8 |
| Roller length | 2.37 | 60.198 |
| Roller-pin length | 5.593 | 142.0622 |
| Roller-pin diameter | 1.75 | 44.45 |
| Shaft overall length | 25.25 | 641.35 |
| Shaft diameter | 4.434 | 112.6236 |

The 13.687 inch dimension is stated as the diameter **at the roller-pin
bosses**, without identifying a pitch circle. Do not silently use it as the
roller-center diameter. The photographed scalloped bosses, paired supports
for each pin, central web and axial reliefs should guide topology; exact
profiles and wall dimensions remain inferred until further evidence appears.
HB237 nomenclature distinguishes M1541A and M1541B. Retain those references
without adding unlisted physical castings to the SNL144 assembly.

HB132 describes an axial oil passage through the fixed shaft with radial leads
to the bushes. It specifies cutting the inner plug flush after installation
while retaining the outer head for filling. Both supplied plugs retain their
Q52E identity, with separately documented installed geometry. Nominal pipe
size is a thread designation, not an established outside shank diameter.

## Interface conflicts and next study

The driving-wheel pitch/count/diameter conflict remains open in the
[drive research packet](R02-drive-research.md). A static pinion installation
must not imply validated gear engagement. First construct an isolated,
source-counted pinion with explicit inferred boss-circle, wall, bore and tooth
controls. Verify distinct rollers, pins, split pins, lubrication plugs and
full native solids before choosing its installed phase or axis.

Then review the calibrated side elevation and sectional plan for the fixed
pinion center. Test the two roller banks against both driving-wheel rings,
including relative phase and axial alignment, and separately test the central
chain sprocket against its future chain path. Keep rejected station/profile
hypotheses and measured clearances. A native nonintersection result alone
does not establish continuous engagement.

Reuse common M1409 bushes, M1407 outer bearings, M1552 plates and the shared
key only where the source and geometry support identical definitions. The
shorter shaft, distinct inner bearing, absence of nuts and flush inner plug
require their own interface checks. Receiver identities are M1978 inside and
M1976 outside; the earlier drive-mount study corrected the initial reversed
inner-panel assignment. Every attachment needs an owned bore in its actual
receiving plate, source counts and bearing-face checks.

The subsequent chain study must also preserve a separate arithmetic conflict:
HB132 gives 1 7/32 inch pins, 1.231 inch reamed holes and 0.005 inch clearance.
The first two imply 0.01225 inch diametral clearance. Do not silently discard
one value. Its 3 inch pitch and fifty pitches are unrelated to road-track pitch.
The M1502 label in HB Plate 132 has not yet been reconciled with the surveyed
parts and must not become an invented chain alias.

The chain dimensions do provide a useful independent consistency check. A
3 inch chord pitch on twelve equally spaced teeth gives a pitch diameter of
`3 / sin(pi/12) = 11.591110` inches, close to HB132's “pitch” of 11.592 inches.
That supports, but does not prove, interpreting that wording as pitch diameter.
For the twenty-three-tooth central sprocket the same calculation gives
22.031827 inches (559.608395 mm), approximately one inch smaller than its
printed 23.031 inch diameter. Keep this derived pitch circle distinct from the
printed outside envelope. Exact chain-bush diameters and tooth profiles still
need reconstruction; these calculations do not resolve the separate wheel and
roller-pinion engagement conflict.

This work continues the standard assembly. Poses and motion qualification wait
until the geometry and its documented approximations are populated and reviewed.
