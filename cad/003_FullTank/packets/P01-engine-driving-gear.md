# P01 — engine driving bevel and thrust-nut lock

Status: **verified development checkpoint; historical geometry remains provisional**, 23
September 2026. The complete powerplant, standard-tank integration and full-tank goal
remain open.

## Scope and ownership

The
[candidate](../experiments/drive_chains/engine_gear_build/DrivetrainWithEngineGear.FCStd)
extends shaft-fittings checkpoint `5872630`. It contains **2,153 physical occurrences:
22 new, two locally revised and 2,129 preserved**. The development count includes
drivetrain context and must not be added to the standard tank BOM. Seven new shared
definitions supply the new occurrences.

`EngineDrivingGear` and `EngineThrustNutLock` belong to `EngineRotatingAssembly`. Six
nested bolt-set containers each own a bolt, nut and split pin. The gear's starting claws
and internal splines are integral features, not extra BOM pieces.

| Physical constituent | Count | Selected evidence |
|---|---:|---|
| LQ258A driving bevel, C8067 | 1 | SNL99:013; HB199 gear 8067 |
| LQ259A thin shim | 1 provisional | SNL217:004; conditional LIB117 thickness |
| LQ262A bolt, B6270 | 6 | SNL23:016; conditional HB199 bolt 198 size |
| LQ51A nut | 6 | SNL23:017; SNL129:015 |
| Unmarked 1/16 × 5/8 inch split pin | 6 | SNL23:018; SNL140:009 |
| LQ276A thrust-nut lock screw | 1 | SNL202:017 |
| LQ277A lock wire | 1 | SNL212:010 |

## Evidence and unresolved dimensions

The [source dossier](../experiments/drive_chains/engine_gear_sources.json) retains 26
literal catalogue records, eleven page records, 24 hashed source assets and explicit
decisions. The [55 controls](../experiments/drive_chains/engine_gear_controls.json)
record each value's basis. Tank gear 8067/C8067 supports conditional transfer from the
Liberty engine book; aviation details do not automatically become tank facts.

LIB27/28 specifies a 33-tooth main bevel with 22-tooth vertical-shaft mates. Module 3.5
mm, 20-degree pressure angle, 10 mm face width and 0.1 mm tooth thinning are estimates.
Cubic spline flanks approximate a spherical involute; ruled surfaces join radial
stations. Root fillets, manufacturing corrections and load capacity remain unqualified.
Analytic conical/cylindrical material is retained where appropriate, rather than
converted unnecessarily to splines.

LIB17 identifies an integral starting claw and internally splined centre. The more
specific exploded mounting view, figure 86, shows a broad annular claw rim and a
substantially larger centre opening than the initial hypothesis. The revision selects
two 150-degree rim sectors separated by 30-degree slots, an outer hub radius of 26.5 mm,
central bore radius of 21 mm and shim bore radius of 22.5 mm. These sizes, the inferred
opposed slot count and twelve internal spline slots remain estimates; no calibrated
source dimensions are claimed. The original three-finger/small-bore candidate and its
passing numerical receipts are preserved as superseded diagnostics. No aircraft
gun-interrupter device is installed.

The original handbook scan, MarkVIII100 right, prints **5/16–24 × 7/8 inch** for bolt
198 and **3/32 inch between head and nut**. The later SNL gives bolt B6270 without its
dimensions. Both manufacturer and grip conflicts remain visible. The model conditionally
uses 22.225 mm under-head length and a 7.9375 mm nominal diameter. Its estimated 15.0508
mm installed grip combines the inherited 10 mm shaft flange, one 0.0508 mm shim and 5 mm
gear web. It **does not satisfy** the printed 2.38125 mm grip. The literal 3/32 is not
silently changed to 23/32. Nuts, head sizes, castellations and thread envelopes remain
estimates.

SNL thin/medium/thick shims are alternatives supplied as required. Only one thin shim is
provisionally installed. LIB117 specifies 0.002 inch packing shims and 0.007 inch cold
backlash, with 0.005–0.010 inch limits. Mapping that shim thickness to LQ259A is
conditional; the final stack and backlash cannot be qualified before the mating pinions
are modeled. The pitch apex is about 6.2 mm beyond the inherited estimated
vertical-shaft receiver centre; that installation needs reconciliation. LIB93 places the
indexed tooth on the lower vertical centreline at 10 degrees past left-bank TDC. The
inherited -12.5 degree crank phase includes the 22.5 degree bank offset and matches that
reference. The revision indexes one tooth downward, with a dependency on crank phase.
Physical marks and full mating-gear timing remain pending.

HB94 requires a screw through the thrust nut and wire seating in a slot. The selected
screw has a blind radial receiver and transverse head hole; the open 330-degree wire
passes through it and turns into an existing wrench slot. All screw dimensions, wire
diameter and route are estimates. The source establishes the named locking elements, not
this exact geometry or its mechanical performance.

## Geometry and validation

The inherited engine frame remains X nose-to-gear, Y port and Z up. Only the crankshaft
and thrust nut acquire local receivers. Gear bolts clear the preceding journal, main
bearing, closure hardware and conical tooth-root rim. Six source split pins cross
drilled bolt shanks and open nut castellations. The hub's central bore clears the
existing gear-end closure stud. The screw receiver remains blind to the shaft's internal
oil cavity. Casing and other inherited definitions remain unchanged.

The superseded initial hypothesis passed 91 independent checks and 428 affected
material-pair checks, including standard tank context, plus 33 STEP comparisons. The
figure 86 revision separately passes **93 independent checks and 428 affected material
pairs including standard context**. Its own STEP and parameter-trial receipts are
recorded below; earlier receipts do not qualify the revision. Native radial material
crossings confirm 33 teeth; held-out spherical-involute points are measured against the
actual saved surfaces. Independent checks also cover central voids, estimated
claw/spline counts, bolt length, shim seating, installed frames, cotter clearance, wire
material/slot engagement and blind screw termination. Unchanged parent material is
compared by exact BRep serialization or Boolean differences in both directions; changed
material must lie inside independently bounded receiver zones.

The [source
gallery](../experiments/drive_chains/engine_gear_build/source_review/index.html)
provides six native views: installation isometric, gear joint, gear end, gear section,
thrust lock and thrust-lock section. Figures 86/22/93/107 supply arrangement context,
with tank catalogue and handbook scans linked alongside them. Both the initial and
revised views were inspected directly. The new bore and broad claw rim more closely
follow figure 86; the exact dimensions, opposed-slot count, spline count and lock-wire
route remain estimates. A widened triangular sector initially produced four lobes
instead of two; the saved-section diagnostic exposed it and an exact circular sector
corrected the construction. Cameras are not registered and no calibrated silhouette fit
is claimed. Review cuts and hidden casing do not change the physical model.

All 33 nominal native/STEP comparisons pass: nine definitions and 24 affected installed
shapes. The coupled trial changes module 3.5→3.6 mm, face width 10→10.5 mm and web stock
5→5.2 mm while retaining the source-selected bolt length. It passes 93 independent
checks, 428 affected material pairs including standard context, and 33 native/STEP
comparisons. This is a parameter robustness trial, not a tank pose.

The [checkpoint
receipt](../experiments/drive_chains/engine_gear_build/development_checkpoint.json)
freezes native/source/checker/visual/trial hashes. Three new progression snapshots bring
the total to 129, preserving all 126 earlier images and all 20 standard native files.
Fresh nominal reproduction and full combined qualification remain pending.

## Reproduction and next work

```bash
python3 cad/003_FullTank/experiments/drive_chains/engine_gear_build.py
python3 cad/003_FullTank/experiments/drive_chains/check_engine_gear.py
python3 cad/003_FullTank/experiments/drive_chains/check_engine_gear_exchange.py
python3 cad/003_FullTank/experiments/drive_chains/render_engine_gear.py
```

The builder accepts `--output` and `--controls`; checkers and renderer accept
`--candidate`. Parameter changes require regeneration; metadata alone is not a live
parametric feature dependency graph.

Next comes the mating distribution gear installation and related source/geometry
constraints, followed by rods, pistons, cylinders, valve gear and engine services.
Inventory/source registration, mounting reconciliation, fresh nominal reproduction,
combined drivetrain qualification and standard-tank integration remain open. Standard
geometry remains the priority before poses.
