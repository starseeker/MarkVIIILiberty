# P01 — Oil-pump reconstruction in development

This continues the [water-pump checkpoint](P01-engine-water-pump-connections.md).
The oil pump is a separate component study in engine-aligned coordinates, with
its crankcase mating face at local Z=0. It is **not yet installed or qualified
against the engine and standard tank**. The full engine and tank remain incomplete.

## Geometry and identity

The current reconstruction represents five gears, their common driving shaft,
two fixed idler pins, two bushes, the separating plate, two locating dowels and
both body castings. It also includes the relief seat, mushroom valve, cage,
spring and shim; three machining plugs; the bottom cover and gasket; the drain
plug and gasket; two strainer frames, four separate screens, and the upper
screen's retaining nut and tab lock. Four upper-body and ten cover bolt sets add
69 constituents, and the relief-cage lock adds one wire: **105 physical occurrences
in 38 definitions**. The remaining two catalogue wires and mounting components
are still pending. The earlier 35- and 104-piece checkpoints are retained.

The native hierarchy separates bodies, rotors, relief components, strainers and
fasteners. Repeated occurrences link to shared definitions. Each definition has
source references and a piece-mark property; source transcription is retained.
For example, the nomenclature transcription calls the separating plate 8138,
while HB86's assembly instructions identify 8188. Native custom controls require
scripted regeneration; they are not live feature expressions.

The [source dossier](../experiments/drive_chains/engine_oil_pump_sources.json)
retains HB, SNL and Liberty records, original image hashes and alternatives.
The provisional 107-piece catalogue expansion is not a final pump BOM: its
quantity/ownership differences, mounting hardware and external fittings remain
under reconciliation. Development counts must not be added directly to the
whole-tank count.

## Source decisions and approximations

- HB86 and HB113 support selected **0.004 inch diametrical gear clearance** and
  **0.003 inch end play** (0.1016 and 0.0762 mm). Their broader inspection ranges
  remain recorded. The gear tooth count, module and profiles are estimates:
  twelve teeth at module 3, with deeper upper teeth and shorter lower teeth.
  A previous threshold-based image tooth count was rejected.
- LIB27–30 show a two-gear pressure stage below a three-gear duplex scavenge
  stage. The source describes the crossing passage above the scavenge housing.
  Reconstructed routes implement that connection pattern, but their dimensions
  and exact paths are estimates. LIB25 is explicitly diagrammatic and supplies
  no geometric placement calibration.
- HB86 calls for **two locating dowels**. SNL20's lower-body composition lists
  one, while HB203 calls one an upper-screen dowel. The selected pair follows
  the explicit assembly instructions; the alternatives remain open evidence.
- HB87 cotters three upper-body bolts and connects the fourth to the relief cage
  with wire. Those fourteen joints and the relief lock are now modeled. HB203's upper bolt
  is 1-5/16 inch long with a 7/8 inch head-to-nut span; SNL24 prints 15/16 inch.
  This is a real printed disagreement, not silently corrected OCR.
- The cover flange estimate is 4.3 mm: the HB203 1/2 inch head-to-nut span less
  the estimated 6 mm body flange, 0.4 mm gasket and two 1 mm washers. The actual
  bolts now meet the printed joint span in the saved native. Both washer layers,
  castle nuts and separate cotters are represented; detailed helical threads
  remain nominal cylinder envelopes.
- LIB29/30/33 and SNL plate33 show separate open strainer frames and gauze.
  The modeled dome/dish, four end spokes, eight side posts and all basket
  dimensions are estimates. Each gauze component is a porous thin BRep with
  deliberately coarse square apertures. **Individual woven wires, solder joints
  and the original filtration rating are not reconstructed.** HB203 distinguishes
  the lower 8466 and upper 8533 side screens; SNL later lists a common side screen.
- HB203 lists two 8420 connections with two 207 gaskets. SNL plate33 says those
  parts are not required. The 1919–1920 target does not justify assuming the
  later omission universally; the installed pipe configuration must settle this.
- HB110 requires mounting gasket 8348 and unobstructed oil ports. That gasket,
  the mounting sets and the receiving crankcase revision remain pending.

The proposed engine placement is X=1243.87630083555, Y=0, Z=-282 mm. The earlier
receiver opening was about 45.8763 mm forward of the driving spindle. LIB27/28's
plan geometry places that spindle near the circular pump centre; the apparent
offset in the oblique LIB96 photograph is insufficient evidence for an eccentric
pump. The case opening and mounting level must be revised and requalified with
the actual lower drive, water pump and tank context before installation.

## Construction diagnostics

Initial passage routing crossed intake and delivery routes. Separating them in
plan and elevation restored the intended source connection graph. The 27-part
services probe passed 40 bore/closure checks and all 27 sampled gear meshes with
no component material intersections. Unconnected bore networks retained at least
4 mm separation in that configuration; this is not a hydraulic simulation.

The initial cover exposed an OCC 7.8 failure: subtracting a cavity coincident with
the existing revolved dish left duplicate conical patches. The result reported a
valid solid, yet its later drain bore disappeared and the drain plug overlapped
the cover by 2177.258699 mm³. Building filled stock, adding the boss and cutting
the complete dish once retained the same intended cone and restored the bore.
The diagnostic preserves the rejected shape, intermediate solids and point/bore
witnesses; validity alone would have missed the error.

The initial side screens intersected the sloping basket rims by 40.191434 and
44.274557 mm³. Their ends now follow the supporting conical profiles. This is
a geometry correction, not an overlap exemption.

## Hardware and relief-lock checkpoint — 23 September 2026

The 104-piece hardware study passes 241 native checks and 338 affected material
pairs. Its first fitting trial found 28 contacts with the former casting. Moving
estimated galleries, lowering the strainer ceiling and adding shallow cover-head
seats cleared the source-length joints without changing acceptance tolerances.
The changed casting retains the intended oil-path graph.

The current [105-piece native](../experiments/drive_chains/engine_oil_pump_relief_lock_study/OilPump.FCStd)
adds HB87(f)'s cage-to-bolt lock. HB203 identifies wire177; SNL160 specifies
No18 × 8 inches. The 203.2 mm continuous centerline is retained as hidden,
nonphysical construction geometry. The formed route, two-turn tail, fourth-bolt
corner and cage drilling are estimates. Under the lower casting, four access
wells expose the bolt nuts and permit the lock route. They retain at least
2.397106 mm to the checked oil passages and preserve the lower-strainer rim seat.

The three-turn wire trial produced a valid solid and cleared all neighboring
parts, yet folded into itself and lost 6.337590 mm³ of stock through fusion.
The revised two-turn wire conserves the complete stock volume, with 1.405765 mm
minimum sampled nonlocal centerline spacing. The retained
[positive and negative controls](../experiments/drive_chains/engine_oil_pump_relief_lock_study/diagnostics/wire_self_contact/README.md)
reproduce the distinction. No source stock was trimmed and no tolerance relaxed.

## Verification and next work

The [saved native report](../experiments/drive_chains/engine_oil_pump_relief_lock_study/native_checks.json)
passes **266 checks and 345 material comparisons**, including 27 gear meshes,
source bolt lengths and joint spans, passage voids, wire stock volume, both
attachment bores, material surrounding the holes, and local/nonlocal wire fit.
The held-out helical-reference fit has maximum 0.000667107 mm residual; this
measures the estimated curve fit, not historical accuracy.

Compared with the 104-piece checkpoint, only the lower body and relief cage
change: 70 prior serialized BReps and 2,553 frame/identity properties match.
A fresh rebuild matches **77 serialized shapes, all 559 object types and 6,059
object properties**; only new document object UUIDs are excluded. This includes
the wire reference, controls and datums.

A four-control local wire trial changes cage-hole offset/radius, bend radius and
strand spacing. Its eight local material comparisons, self-spacing and stock
volume pass. This is a bounded wire probe, not the required coupled full-pump
parameter qualification; that broader trial remains open.

All **143 definition/occurrence STEP comparisons are covered**: 135 direct
strict comparisons and eight exact-pair reuses for the unchanged screens. The
[combined report](../experiments/drive_chains/engine_oil_pump_relief_lock_study/exchange_checks.json)
binds the native and both STEP files, records each reused pair and proves complete,
disjoint coverage. The [reference evidence](../experiments/drive_chains/engine_oil_pump_relief_lock_study/screen_reference/completed_comparisons.json)
retains the four completed strict screen-definition comparisons and their actual
native/STEP BReps. Reuse requires exact serialized pairs, identity placement and
unit link scale; it does not infer success from a matching volume or valid export.
Changed native geometry, changed STEP geometry, an unpassed source comparison and
a nonidentity pose are rejected by the negative controls.

The original 35-part whole-assembly STEP process remains separate and may still
be running. Only its completed per-part comparisons are reused. This qualification
covers the present isolated pump geometry, not crankcase installation or historical
completeness. The nonscreen subset report intentionally retains its eight deferred
entries; the combined report resolves those entries explicitly.

Six [views](../experiments/drive_chains/engine_oil_pump_relief_lock_study/source_review/index.html)
were directly compared with LIB27/29/30/33/34 and SNL plate33. The new access wells
address the underside attachment, while LIB34 still shows more contoured bosses
than the broad modeled ceiling. The mounting holes, external pipes and relative
passage diameters also need source-led refinement. These discrepancies remain
open; the views are not registered to the source cameras.

Two snapshots bring the progression to **143**, preserving all 141 prior images,
20 standard native files, and the previous water-pump and hardware natives.
The build has **171 controls**, with the retained 160 source records and 18 hashed
source images. Local dependencies and checks are frozen in `frozen_inputs`;
shared stage libraries and runtime come from this repository.

The reusable entry points are:

```sh
python3 cad/003_FullTank/experiments/drive_chains/engine_oil_pump_build.py --output .work/oil-pump-rebuild
python3 cad/003_FullTank/experiments/drive_chains/check_engine_oil_pump.py --candidate .work/oil-pump-rebuild
python3 cad/003_FullTank/experiments/drive_chains/check_engine_oil_pump_exchange.py --candidate .work/oil-pump-rebuild
python3 cad/003_FullTank/experiments/drive_chains/render_engine_oil_pump.py --candidate .work/oil-pump-rebuild
```

Complete the two remaining source wires, mounting gasket/stud sets, mounting-hole
pattern and external connection selection. Reconcile the unequal openings shown
in LIB28 with the current estimated passage sizes. Then revise the receiving
case, verify the shaft coupling and shared water-drive constraints, run the
coupled full-pump parameter trial and qualify the combined installation. Continue
the remaining engine systems and standard integration. Poses remain deferred.

Direct inspection of HB196/199 (original scans MarkVIII099/100) now establishes
ten 132 mounting studs, **1/4-28 × 1-7/16 inch**, with **7/16 inch between nut and
case surface**, plus ten washers111, nuts101 and cotters106. The present estimated
6 mm flange + 0.4 mm gasket + 1 mm washer is 3.7125 mm short of that 11.1125 mm
span. A 9.7125 mm flange would satisfy the assumed stack; this is a proposed
revision requiring actual joint checks, not a change already made. The next-work
notes retain those source rows and original-image hashes.

A further direct check of SNL237 finds LQ196A/manufacturer132 printed as
**1/4 × 1-9/16 inches**, with 7/16-inch U.S. Standard and 9/16-inch S.A.E.
threaded ends. This is **3.175 mm longer** than HB196's 1-7/16-inch stud.
The source application includes ten studs for the lower crankcase. Retain this
conflict when choosing the mounting stack and engagement; the same assumed
case engagement does not put both versions' nut threads at the HB bearing plane.
The [calculation](../experiments/drive_chains/engine_oil_pump_relief_lock_study/next_work/mounting_stud_conflict.json)
records the alternatives without treating an assumed engagement as a printed fact.
