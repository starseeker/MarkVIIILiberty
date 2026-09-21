# I05 — air-pressure pump and transmission attachment

Status: **pump core plus a 32-piece mounting reconstruction; drive installation remains conditional**
(21 September 2026). The [combined native model](../experiments/drive_chains/air_pump_mount_build/TransmissionWithAirPump.FCStd)
contains 1,490 physical leaves: the 1,407-piece transmission checkpoint plus
51 pump pieces and 32 brackets/attachment pieces. Two transmission castings gain
integral blind receivers; the installed pump base has wider mounting feet.
The clutch-stop drive, belt, air connections and standard-tank integration remain
unfinished. The earlier [standalone pump](../experiments/drive_chains/air_pressure_pump_build/AirPressurePump.FCStd)
and [assembled STEP](../experiments/drive_chains/air_pressure_pump_build/AirPressurePump.step)
contain separate casting, cylinders, pistons, springs, shaft, pulley, bushes,
covers and catalogue closure/retention hardware and remain preserved as the core checkpoint.

The proposed installation uses the accepted approximate MX5 transmission
checkpoint. This packet spans FuelPressure and its Drivetrain interfaces. It is not
the transmission mechanical lubricator, the engine oil pump, or the B6205
input-pinion bearing-housing support.

## Identity and quantity

One engine-driven pump, survey assembly `P_dd55a02fabc8964b`, is enumerated by
SNL159:003–020. Its composition and shaft subassembly were checked visually
against original SNL pages159 and209. SNL Plate5 (printed279) and HB Plate115
(printed195) show the same four-cylinder form. HB Plate22 (printed29) repeats the
views; repetition is not independent dimensional confirmation.

| Item | Physical quantity | Source record |
|---|---:|---|
| SH901F air-hole cover | 1 | SNL159:005 |
| SH903A base | 1 | SNL159:006 |
| SH900A bearing/end cover | 2 | SNL159:007 |
| SH901C bushing | 2 | SNL159:008 |
| SH901B check nut | 4 | SNL159:009 |
| SH900C cylinder | 4 | SNL159:010 |
| SH901E displacement plug | 4 | SNL159:011 |
| SH901D piston | 4 | SNL159:012 |
| SH900B pulley | 1 | SNL159:013 |
| SH900D cam shaft | 1 | SNL209:022 |
| Plain US half-inch hex nut, shaft retention | 1 | SNL209:023 |
| SH901A spring | 4 | SNL159:015 |
| US 3/8 × 1-1/4in base bolt, plain nut and lock washer | 4 sets / 12 pieces | SNL159:016;30:004 |
| Woodruff No.5 key | 1 | SNL159:017;115:010 |
| Q52A square-head 1/8in pipe plug | 7 | SNL159:018 |
| US 5/16 × 3/4in hex cap screw | 8 | SNL159:019 |
| US 3/8 × 3/4in hex cap screw | 6 | SNL159:020 |

The catalogue expands to **63 physical pieces**, including the four base-attachment
sets, before the drive belt, transmission brackets and studs. The native core
contains 51 pieces; the twelve base-fastener pieces are now included in the
combined mounting reconstruction, completing these 63 catalogue pieces geometrically.
Port/plug allocation must be checked again when the air
lines are installed; a closed catalogue pump may differ from the connected
installation. Pump and shaft assembly records are containers. The
base-bolt survey identity describes a set; splitting it into three physical
pieces must retain that identity as the set's provenance and must not duplicate
it as a fourth solid. No invented survey identifiers are required.

The survey lists no configuration membership for the pump assembly. The decision
is to carry this documented equipment provisionally into the selected production
reconstruction, with 1925 handbook/1928 catalogue applicability retained. SNL's
%, X and & notes concern requisition/issue classification, not tank variants.
The handbook's 80-gallon tank description is not a reason to replace the
separately selected production fuel tanks.

## Form and useful dimensional controls

The inspected views show two cylinders on each sloping side of a hollow base,
a shaft along the two cylinder stations, and a grooved pulley at one shaft end.
Triangular three-screw bearing covers enclose separate bushes. Each cylinder has
a two-screw mounting flange. The section exposes the pistons, displacement plugs,
return springs and cam shaft. All are separate native solids in the current core.
Two spring definitions represent the different installed compressions at the
selected static cam positions; both retain the single SH901A survey identity.

The end view suggests bank axes roughly 45degrees from vertical. This is a visual
estimate. Overall length, width, pulley diameter, shaft journals, piston stroke,
spring dimensions, cam profiles and internal port routes are not dimensioned in
the inspected figures. The [controls](../experiments/drive_chains/air_pressure_pump_controls.json)
identify the reconstruction values explicitly. Do not scale from a nominal pipe-thread size as if it were an
outside diameter.

SNL18:011 explicitly gives SH900G as a **link V belt, 54in long, 5/8in wide,
28degree angle** (1371.6mm,15.875mm,28degrees); the original page was inspected.
The length's pitch/inside/outside convention is unstated. Treat it as a closure
constraint with that uncertainty, not an exact pulley-center dimension. The
adjacent 60in belt belongs to the transmission mechanical lubricator. No.5 key
dimensions require a historical standard or a declared estimate; its number
alone is not a millimeter dimension.

## Installation and ownership

HB printed31 explicitly places the pump above the clutch, driven by the V pulley
on the engine-shaft brake; its own cam shaft operates the pistons directly.
HB Plate15 (printed23) shows the pump over the input-bearing housing with the
belt descending to the drive pulley. HB32 describes a frame above the cardan
shaft. These support the broad placement, not an exact mounting transform.

The catalogue separates the following installation items:

| Owning installation | Item | Evidence |
|---|---|---|
| Transmission assembly | One left MX101 and one right MX100 pump bracket | SNL251:018/019;36:012/013 |
| M264 input cover | Two MX98 stud assemblies | SNL77:003;240:019–023 |
| M250 input-bearing housing assembly | Two MX99 stud assemblies | SNL112:013;231:020–026 |
| Pump base to supports | Four 3/8 × 1-1/4in bolt/nut/washer sets already counted above | SNL159:016;30:004 |
| FuelPressure pump drive | One SH900G link V belt | SNL18:011 |

MX98 has a printed half-inch diameter and 2-7/8in length, with 1in US and 7/8in
SAE thread spans. Each owns a half-inch castle nut and a 3/32 × 1in split pin;
the latter explicitly names the air-pressure pump. MX99 has a special MX102
half-inch SAE jam nut (3/8in thick), a 3/8in SAE plain nut, a half-inch SAE plain
nut and **two** 3/8in lock washers per stud. This mixed hardware suggests a stepped
or adjustable arrangement; its exact construction remains unproved. Resolve the
bracket shape and stud axes from installed views before making receiver holes.

Own the pump body and its internals once under FuelPressure. Own transmission
brackets and their transmission attachment hardware once under Drivetrain, and
reference their mounting faces from the pump installation. The four base-bolt
sets must occur once across that interface. A combined experimental document may
contain both subsystem containers until standard-tank integration.

B6205, capA7679, two A7681 stud/nut/pin sets, stiffenerA7680, shimA7682 and eight
3/8 × 2-1/4in attachment sets form a separate input-bearing support family.
Their split-clamp relationship is supported by the catalogue; a particular tall
pedestal shape or mounting location has not yet been established.
Relevant records are SNL41:030–034,56:011,217:013,222:021,241:006–010 and25:017.

## Geometry, checks and source comparison

The core uses a 140mm base, 190.5mm pulley diameter, two opposed 45degree banks
and cylinder stations at X±28mm. These are approximate dimensions. Source-sized
cap screws retain their printed under-head lengths. The hollow casting has
separate piston guide bores and a crank cavity; covers use rounded triangular
outlines, with separate bushes. Opposed inferred shaft shoulders leave 0.3mm total
axial endplay. A semicircular key and shaft nut locate the pulley. Circular
eccentric cams, reduced piston feet and ground-end helical springs form a
consistent static internal arrangement. Cam law, spring properties, actual
thread forms and the historical No.5 key dimensions remain unverified.

The first cylinder screw heads intersected the barrel walls. Widening the
estimated flange screw spacing resolved this. Source review then reduced the
overlarge bearing covers and replaced their lobed outline with an analytic
rounded triangle. The smaller crank cavity also required the vent passage's
lower endpoint to follow the new cavity radius. Native geometry checks include
continuous vent access, cam/piston contact, spring seating, shaft axial stops,
guide clearances and deliberate displaced-part collision checks.

The [fixed-scale source comparison](../experiments/drive_chains/air_pressure_pump_build/source_review/source_overlay.png)
normalizes the **assumed** 190.5mm pulley diameter to approximately400 source
pixels. It is a proportional comparison, not independent dimensional calibration.
The four-cylinder arrangement, base length and revised bearing-cover form agree
broadly with SNL5/HB115. The foot ledges extend beyond the visibly illustrated
end ledge; their shape and bolt locations remain installation assumptions.
Cylinder reach, pulley axial spacing and unshown casting blends retain visible
differences. No image warping or forced source fit is applied. The manual's side
section is not treated as a simple upright projection of both inclined banks.

The initial proposed location, core [300,0,205]mm, put the pulley slightly inside
the M250 housing flange. The revised study uses [300,0,210]mm and has no material
overlap in six candidate pairs against 6,733 current physical context leaves.
This is a placement study, not a supported installation: neither transmission brackets nor belt
alignment has been qualified. The clutch and its drive pulley are still layout
dependencies; the earlier source-preparation wording referring to an existing
finished drive pulley was premature.

Internal pressure routing and valve action remain unresolved. The model provides
the named physical components, oil/vent openings and closure receivers, but does
not claim a functional fluid circuit or verified historical hidden drillings.

The [qualification receipt](../experiments/drive_chains/air_pressure_pump_build/qualification.json)
binds the native model, checks, source review and scope. All 139 local material
pairs and 104 independent physical checks pass. Detailed STEP comparisons
cover all 17 reusable definitions; the assembled STEP separately checks 51 placed
solids. Default mass integration initially reported discrepancies on rotated
springs and the casting; explicit-accuracy OCC integration resolved these without
enlarging shape tolerances or changing export geometry. Two coherent dimension
trials vary base length126/154mm, bank seat54/60mm and cam eccentricity2.5/4.5mm,
moving end hardware, oil plugs, feet, pulley and key with the case ends. Their
scope is sampled local topology, contact and clearance, not the whole uncertainty
domain or moving-tank operation.

## Remaining construction cycle

1. Establish the clutch-stop drive pulley and its shaft datum, then check pump
   pulley alignment and the54in belt closure with its unstated length convention.
   Revise the current support height, pump scale/position and bracket profiles
   coherently if that evidence requires it. The geometry described below is a
   supported mounting hypothesis, not a resolved historical installation.
2. Resolve connected air ports and hidden passage/valve approximations, then route
   the air lines and reconcile the seven catalogue plugs with the installed state.
3. Integrate the linked pump under FuelPressure and mounts under Drivetrain,
   qualify affected standard-tank interfaces, and regenerate opaque/transparent
   standard views. Current component snapshots do not constitute tank012.

```sh
python3 cad/003_FullTank/experiments/drive_chains/air_pressure_pump_build.py
python3 cad/003_FullTank/experiments/drive_chains/check_air_pressure_pump.py
python3 cad/003_FullTank/experiments/drive_chains/check_air_pressure_pump_variants.py
python3 cad/003_FullTank/experiments/drive_chains/render_air_pressure_pump_review.py
```

The [source dossier](../experiments/drive_chains/air_pressure_pump_sources.json)
preserves exact survey records, linked identities, selected assembly edges and
source hashes. The core is an isolated deliverable; it is not yet counted as
populated standard-tank geometry.

## Mounting reconstruction checkpoint

The [mounting controls](../experiments/drive_chains/air_pump_mount_controls.json)
and [source records](../experiments/drive_chains/air_pump_mount_sources.json) retain
all unprinted dimensions as assumptions. Two distinct handed MX101/MX100 brackets
join the M264 cover to M250 housing through two MX98 stud/nut/pin sets and two
MX99 stud/three-nut/two-washer sets. These 20 pieces belong to Drivetrain. The
four base bolt/nut/washer sets contribute 12 pieces under FuelPressure. Set records
are provenance containers, not extra solids. US base nuts and SAE adjustment nuts
have separate definitions even though their smooth inspection envelopes coincide.

The prior core[300,0,210]mm position was only a clearance study. Its pulley plane
X396 falls within the input-housing length, so it does not establish a workable
drive to the clutch-stop drum. The new pump origin is core
**[420,0,375.005218]mm**, with pulley planeX516. The height solves the open-belt
equation for the printed1371.6mm length using **assumed** pitch radii89.25 and
108.3mm. The driving radius corresponds to an estimated9-inch pulley OD with a
6mm radial deduction; neither is a printed dimension. Changing both reference
radii by±6mm gives heights356.130 and393.878mm. These scenarios do not establish
the belt's historical length convention or the actual clutch datum.

MX98 retains its printed73.025mm overall length and25.4/22.225mm thread spans.
Its forward axis meets an inferred blind boss in the M264 front face. MX99 is
interpreted as a vertical stepped half-inch/three-eighth-inch stud, with an MX102
jam nut below and the other nuts/washers clamping the rail. Its roughly290mm
length, the rail shape and the tall triangular webs remain hypotheses. The M250
bosses preserve the existing cup passage. Smooth threads and compressed split
washers are explicit inspection approximations; no structural capacity is claimed.

The mounting trial exposed insufficient bolt-head clearance at the original pump
feet. The installed base extends each ledge4mm and moves the holes fromY±87 to
Y±90.5mm. The other50 pump pieces retain their original geometry. A first trial
also intersected the cover boss and flange shims at the rear bracket corners;
a cylindrical relief of radius110.5mm cleared the existing110mm flange envelope.
The rejected report and geometry inputs are retained with the new build.

A separate exchange failure traced to global face refinement: after the valid
boss/receiver Booleans, `removeSplitter()` merged existing grease-port edges at
X279 and increased their stored tolerance to0.000603mm. The Boolean result before
that refinement has maximum tolerance about0.000000306mm. The final build retains
its valid face divisions. It does not alter the original port or manually relax
tolerances, and the same exchange criteria are retained.

The [source comparison](../experiments/drive_chains/air_pump_mount_build/source_review/source_comparison.png)
places the actual native rendering beside HB15 without image warping or claiming
matched scale. The four-cylinder form, grooved pulley and longitudinal mounting
ledges agree broadly. The source hides much of the support; it does **not** verify
the tall open frame or stepped-stud arrangement. The conditional height, source
profile differences and absent air lines remain explicit. A separate
[belt diagram](../experiments/drive_chains/air_pump_mount_build/source_review/belt_datum_study.png)
shows the unresolved construction without adding a fictional completed driver
or belt to the physical BOM.

```sh
python3 cad/003_FullTank/experiments/drive_chains/air_pump_mount_build.py
python3 cad/003_FullTank/experiments/drive_chains/check_air_pump_mount.py
python3 cad/003_FullTank/experiments/drive_chains/check_air_pump_mount_variants.py
python3 cad/003_FullTank/experiments/drive_chains/render_air_pump_mount_review.py
```

The combined native and affected85-solid STEP are component-installation
deliverables. They do not supersede standard tank011 or constitute tank012.

The [qualification](../experiments/drive_chains/air_pump_mount_build/qualification.json)
binds 529 affected material pairs, 93 independent interface/count checks,
16 definition-level STEP comparisons and 85 placed-solid exchange checks.
Two rebuilt height scenarios each pass529 pairs and20 seating contacts. Seven
final images were visually reviewed. This accepts the local mounting geometry
for clutch development while retaining the source-profile and belt-datum limits.
