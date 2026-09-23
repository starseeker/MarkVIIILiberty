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
screen's retaining nut and tab lock. This is 35 physical occurrences in 32
definitions, before fastening sets, lock wires and mounting components.

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
  with wire. Those fastening components are still pending. HB203's upper bolt
  is 1-5/16 inch long with a 7/8 inch head-to-nut span; SNL24 prints 15/16 inch.
  This is a real printed disagreement, not silently corrected OCR.
- The cover flange estimate is 4.3 mm: the HB203 1/2 inch head-to-nut span less
  the estimated 6 mm body flange, 0.4 mm gasket and two 1 mm washers. The actual
  bolts and their fitted joint still need construction and checking.
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

## Verification and next work

The saved [hierarchical native](../experiments/drive_chains/engine_oil_pump_development/OilPump.FCStd)
passes **138 checks and 123 component material comparisons**, including all 27
sampled gear meshes. Checks reopen the actual file and examine validity,
occurrence identity, parent-relative placements, passage connections/separation,
open bores and screen apertures. This qualifies the stated local checks only;
crankcase fit and the complete pump are unproven.

The strict STEP comparisons are still running. The two exported files exist,
but export completion is not exchange acceptance. Parameter variation and fresh
reproduction remain pending. The [native report](../experiments/drive_chains/engine_oil_pump_development/native_checks.json)
and the eventual `exchange_checks.json` provide the actual check results.

Five [views](../experiments/drive_chains/engine_oil_pump_development/source_review/index.html)
were inspected against LIB27/29/30/33 and SNL plate33. The separate component
arrangement is recognizable; unprinted profiles, source-camera registration and
fine weave remain uncertain. The isometric and cutaway snapshots bring the
progression to 141 images, preserving all 139 previous images, 20 standard
natives and the preceding water-pump checkpoint.

The build exposes 143 controls, with 160 source records and 18 hashed source
images. A copy of its local input dependencies is retained in the study's
`inputs` directory; shared stage libraries and runtime are supplied by this
repository. No complete-pump acceptance is claimed.
The reusable entry points are:

```sh
python3 cad/003_FullTank/experiments/drive_chains/engine_oil_pump_build.py --output .work/oil-pump-rebuild
python3 cad/003_FullTank/experiments/drive_chains/check_engine_oil_pump.py --candidate .work/oil-pump-rebuild
python3 cad/003_FullTank/experiments/drive_chains/check_engine_oil_pump_exchange.py --candidate .work/oil-pump-rebuild
python3 cad/003_FullTank/experiments/drive_chains/render_engine_oil_pump.py --candidate .work/oil-pump-rebuild
```

Complete the source-length upper and cover bolt sets, source-length lock wires,
mounting gasket/fasteners and external fittings. Then revise the receiving case,
verify the shaft coupling and shared water-drive constraints, perform a coupled
parameter trial and fresh reproduction, and qualify the combined installation.
Continue all remaining engine systems and standard-tank integration afterward.
Pose variants remain deferred until standard geometry is populated.

Direct inspection of HB196/199 (original scans MarkVIII099/100) now establishes
ten 132 mounting studs, **1/4-28 × 1-7/16 inch**, with **7/16 inch between nut and
case surface**, plus ten washers111, nuts101 and cotters106. The present estimated
6 mm flange + 0.4 mm gasket + 1 mm washer is 3.7125 mm short of that 11.1125 mm
span. A 9.7125 mm flange would satisfy the assumed stack; this is a proposed
revision requiring actual joint checks, not a change already made. The next-work
notes retain those source rows and original-image hashes.
