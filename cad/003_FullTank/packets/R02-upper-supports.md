# R02 — upper roller support interface

Standard geometry work, 20 September 2026. This subset adds four partial M2092
upper support angles and corrects the shared pin-end/clamp reconstruction.
It does not complete R02 or establish a structurally qualified support system.

## Source decision

HB141 describes the shafts as suspended by angles and U bolts, with the shaped
shaft ends fitting the angle toe to prevent rotation. HB88/89 and SNL Plate 29
show the flange above the pin and a descending leg beside the shell. The lower
L section near the skirt bottom is a different interface in those drawings;
it must not be substituted for the pin support. The earlier bottom pin flats
and 31 mm clamp seat did not reproduce the suspended-toe topology.

HB:nomenclature:221:019 identifies **M2092**, four per vehicle. Direct inspection
of original `MarkVIII111.jpg`, right-hand page, confirmed both mark and count.
That scan joins the authored source lock. The four occurrences share
`roller_upper_support` / `P_19d6f046e2cd29dd`, two per upper station; a yaw of
180 degrees installs the symmetric part at the opposite pin end. This is the
handbook upper scope, separate from the SNL lower totals. No SNL equivalence is
invented. M2092 is not SH294A, the still-unpopulated upper cover.

## Explicit approximations

| Item | Working geometry | Status |
|---|---|---|
| Pin end seats | Upper-facing flats at Z +12 mm, 40 mm axial reach | Section topology supported; depth/length inferred. Shared M1337 identity retained. |
| Upper angle | 160 mm long, 34 mm flange, 6.35 mm stock, 4 mm inside root radius | Dimensions and exact form unlocated. |
| Flange / washer seat | Z +50 mm above shaft | Section-proportioned estimate, replacing +31 mm. |
| Staple leg top | Z +74 mm | Inferred extension for flange, washer and nut. |
| Staple bores | 13.1 mm; centered on existing staple legs | Assembly clearance; threads omitted. |
| Shell attachment holes | Two 13.1 mm holes at 130 mm longitudinal pitch | Inferred, hardware identity and attachment construction unresolved. |
| Roof access relief | Local support/clamp envelope plus 1 mm clearance | Inferred rectangular relief in the rear roof only; exact cover/opening shape unresolved. |

The pin flats and clamp heights change at all 60 stations because the handbook
states upper/lower pins are interchangeable. Lower support runs remain absent;
their inclination and retaining plates must be resolved before claiming fit.
Pin bore/length/diameter, roller sizes, station picks, track pitch and spring/ring
interpretations are retained. No hole sizes or shape estimates above are presented
as original manufacturing dimensions.

The first integrated probe found a 1,274.239 mm³ nut/roof overlap after the clamp
height correction. The local roof relief follows the same station and support
parameters; it removes that overlap without moving the source station picks.
This geometric clearance does not prove the historical roof construction.

## Construction and checks

The angle is a constrained native section sketch and PartDesign pad, including
a true circular inside root. Separate analytic cuts form staple and attachment
holes. The installed upper assembly has 21 physical leaves; lower plain/spring
stacks retain 19/22. This gives 1,228 roller-family components from 14 definitions.

Validation checks the independent HB221 whole-vehicle count, repeated native
placements and all candidate material intersections. Four native toe/pin bearing
faces and eight washer/flange faces must have zero gap and nonzero contact area;
zero interference alone would not reject a floating clamp. Nearest-hull distances
are reported separately with attachment qualification false. A +0.5 mm stock
trial must increase support material inside the fixed outside envelope, retain
all seats, and leave unrelated shapes/placements unchanged.

The full saved-native qualification and visual review pass for this partial
subset. The nominal build checks 230 internal and 620 external candidate pairs
with zero overlap. All 12 bearing faces have zero gap: four pin seats about
328.818 mm² each, and eight washer seats about 365.772 mm² each. Moving a test
pin away by 0.1 mm makes the face-contact check reject it. Both outer angles
meet the shell side plates; both inner angles remain 1 mm from the inferred
roof-relief edge. Their attachment remains unfinished.

The delivery has 195 definitions and 4,435 leaves (4,416 physical solids,
17 layout solids and two wires). Twenty-two record/renderer tests and all eight
parameter trials pass, including support stock +0.5 mm. Both STEP files reopen
with their full solid counts; relocated native links, independent rebuild and
cache reuse pass. Native build / independent / cached times are 43.15 /
51.24 / 40.50 s. All 20 native and 117 delivery-file hashes match;
724 source files verify, including the unchanged frozen survey. The six reviewed
raster hashes match the recorded inspection. Full-tank verification remains false.
The upper oblique and transverse section compare against HB88. The isometric
snapshot sequence advances only after a significant whole-vehicle visual change;
001–005 remain preserved.

## Next work

Reconcile the 34 lower runs, their inclination and removable retention pieces.
M2176 / M2175 retain their printed 168.275 / 822.325 mm lengths and shared skirt
identities. Do not assign one long angle per shaft. The inner split and the final
rear stations still require geometric reconciliation. Exact upper attachment,
SH294A covers, drive/idler assemblies and the rest of the tank remain open.
