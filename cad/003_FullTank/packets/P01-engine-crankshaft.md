# P01 / I01 — Liberty crankshaft and bearing installation

Status: **verified development checkpoint; historical geometry remains provisional**, 23 September 2026.
This extends the committed [engine case checkpoint](P01-engine-case.md).
The full-tank goal remains all identifiable installed components and interiors;
standard geometry precedes service poses. This packet is a partial engine stage.

## Source decisions

The [dossier](../experiments/drive_chains/engine_crankshaft_sources.json) preserves
108 literal catalogue records, 27 hashed assets and relevant manual prose.
The original SNL17 individual entries identify one long and six short bearing
halves of **each** hand: LQ238A/LQ240A lower, LQ239A/LQ241A upper. They agree with
LIB17, which prints 115 mm for the nose bearing and 49 mm for the other six.
This is the selected interpretation; the reversed lower quantities in SNL58
remain preserved as contrary evidence. The survey database is unchanged.

HB45 supplies the 66.675 mm main-journal diameter and 177.8 mm stroke. Aviation
applicability is conditional. HB96/LIB115 give 0.0025–0.00325 in diametral bearing
clearance; the selected 0.002875 in gives 0.0365125 mm radial clearance. Journal
endplay is separately selected at 0.0675 in within LIB115's 0.0575–0.0775 in range.
That value is not the thrust-bearing endplay limit.

LIB120 numbers cylinders from the distribution end. LIB124 and figure93 establish
paired crank planes 1/6, 2/5, 3/4, separated by 120 degrees. The standard static
setting places 1/6 at 12.5 degrees left of vertical viewed from the gear end,
10 degrees past left-bank TDC. In local nose-to-gear order the six phases are
−12.5, −132.5, +107.5, +107.5, −132.5, −12.5 degrees. The key-to-crank angular
registration remains an assumption; this is not a qualified moving mechanism.

LIB11/31/36/37 guide the bearing oil features: joint notches, a front pair of
oil entries with localized crossed channels, an ordinary-shell oil pocket,
shell-registering dowels and outer seat grooves feeding the camshaft
oil lead. Groove dimensions and detailed profiles are estimates. Pressure pipes,
the complete camshaft lead and the rest of the lubrication system remain pending.

The SNL catalogue supplies one LQ273A double thrust bearing, two LQ274A sleeves,
LQ275A retaining nut, SH136B key, one No10–24 ×3/4 in screw, SH136A output nut and
a 1/4 ×3 in split pin. LIB85 shows the double thrust arrangement. Its decomposition
here into three races, two cages and two rows of twenty balls is explicitly
approximate; the source does not print the ball count or these internal sizes. All 68 current controls have explicit
[parameter provenance](../experiments/drive_chains/engine_crankshaft_parameter_evidence.json).
HB thick/thin sleeve wording remains alongside the SNL selection of two LQ274A.

## Geometry and ownership

The first saved installation has 1,992 physical occurrences: 81 new constituents,
two revised case castings and 1,909 unaffected parent components. These totals
include development contexts and must not be added to the standard tank count.

| Ownership | New physical pieces |
| --- | ---: |
| One LQ255A crankshaft forging | 1 |
| Seven pairs of main-bearing halves | 14 |
| LQ194A bearing dowels | 14 |
| One LQ273A thrust bearing, decomposed into internals | 45 |
| Two sleeves and thrust retaining nut | 3 |
| Flywheel key and screw, output nut and cotter | 4 |

The source crankshaft is one connected hollow forging, with separate main
journals, twelve cheeks and six offset pins. There is no central bar passing
through the crank bays. Analytic passages join journal and crankpin cavities
through the rear webs. Crankpin diameter, hollow sizes, cheek outlines and
fillet omissions remain documented reconstruction approximations. Open journal
ends are intentional pending installation of their separately catalogued plugs.

The existing flywheel's conical bore supplies the mating taper. Its keyway
receives the rounded key, retaining screw and two extraction holes illustrated
in LIB12/18. The key top retains the conditional 0.010 in clearance from LIB116.
Threaded portions are smooth nominal envelopes. The source-sized screw reaches
the estimated hollow nose cavity; cavity dimensions need further checking when
the nose plug is installed.

The inherited engine datum remains X2906.805551, Y0, Z849.233510 mm. The cases
receive the printed bearing lengths, dowel/oil passages and an estimated split
thrust housing. The gear-compartment floor rises from 46 to 70 mm to clear the
shaft flange. The flange begins 32 mm beyond the final bearing-row center;
the neck extends to it. The thrust housing has a 74 mm outside radius and
65.05 mm sleeve seat, preserving 8.95 mm radial stock. These unprinted
installation dimensions remain estimates.
Source registration, six-versus-seven engine mounts and complete case hardware
are still unresolved.

## Verification and visual review

The initial builder saved valid single-solid parts but independent checking found
the gear flange at row+22 mm interfering with the final 49 mm bearing. Moving it
to row+32 mm required extending the neck as well; a disconnected-flange trial
was rejected before saving. The first dowel checker also assumed an undrilled
journal when measuring distance; it now tests actual tip position and minimum
recess clearance. An argument-variable collision stopped the first checker before
material-pair testing. These are retained diagnostic failures, not accepted checks. A subsequent
candidate passed all 420 independent checks but its 521 material pairs found
18.895 mm³ of original lower-nose material inside the front thrust sleeve.
The receiving bore is now machined through the finished casting after adding
the housing, and its outside radius retains at least 8 mm selected wall stock.

The next candidate passed 421 independent checks and 521 material pairs, but
visual comparison with LIB11/31 rejected its continuous inner oil grooves.
Localized crossed channels and rounded pockets replace them. Added running-land
witnesses explicitly reject the previous circumferential grooves. The output
section camera also changes to a plane through the key and retaining screw.

A focused FreeCAD1.1.1/OCC7.8.0 probe found that all new bearing Boolean cuts
produce valid single solids, but `removeSplitter()` makes the long upper shell
invalid without raising an exception, and also mutates its input. A second
probe shows that `shape.copy().removeSplitter()` preserves the original and
returns valid topology. The generator isolates optional refinement on a copy,
checks the result, and retains the original if cleanup fails. It records each
bearing's actual refinement disposition. No healing or tolerance inflation
is used. The reusable FreeCAD guidance now records this demonstrated failure.

STEP reopening then isolated a separate defect in the thrust-cage spherical
pockets. With the default sphere axis, native solids were valid but exported
pockets extended past their axial trimming planes. Aligning the sphere axis
with the plane normal preserves the spherical clearance and gives valid
nominal/trial STEP solids in definition and installed frames. The retained
probe distinguishes geometric material from the default volume integrator's
small parametrization-dependent error. The repaired cage also has tighter axial
bounding boxes. Four formerly tested cage/race-or-sleeve pairs are now outside
the broad-phase candidate set. A focused audit checks their actual separation
and zero overlap; the final material-pair count is recorded below.

The revised saved candidate passes **437 independent checks and 517 affected
material pairs including standard tank context**, with no positive-volume overlaps.
Checks cover source-sized journal/bearing material, the six paired crank planes,
hollow passages, fitted dowels and seats, thrust internals and the existing output
interface. They also compare both material directions outside declared case-edit
regions and preserve the 1,909 unaffected parent components.

**101 native/STEP comparisons** pass: 18 definitions (including revised cases) and
83 installed shapes. Material, adaptive mass integration and centroids agree within
the retained numerical tolerances. A coupled trial changes web stock 12.7→13.5 mm,
static phase −12.5→−7.5 degrees, ball radius 6→5.8 mm, gear floor 70→74 mm and key
length 150→144 mm, groove width 3→3.4 mm and depth 0.6→0.8 mm. It passes 437 independent checks and 517 material
pairs including standard context. This is a generator robustness test, not a
service pose. Source journal, stroke, bearing lengths and fastener sizes stay fixed. Variant STEP and fresh nominal
reproduction remain unverified; combined qualification remains open.

Eight saved-native views were inspected in the
[review bundle](../experiments/drive_chains/engine_crankshaft_build/source_review/index.html)
against Liberty figures 11/12/31/85/93. The source and model cameras are not fitted.
The [checkpoint receipt](../experiments/drive_chains/engine_crankshaft_build/development_checkpoint.json)
records native, verification, source, visual and trial hashes. New
[installed isometric](../../intermediate_snapshot_iso_engine_crankshaft_001.png),
[bare shaft](../../intermediate_snapshot_detail_engine_crankshaft_001.png) and
[thrust section](../../intermediate_snapshot_detail_engine_thrust_001.png) images
bring progression to 123, preserving all 120 prior snapshots and 20 standard native
files. The upper casting is hidden only in the review isometric, to expose the
new internals; both cases remain installed in the native assembly.

## Reproduction and remaining work

From the repository root, run these sequentially with the installed runtime:

```bash
python3 cad/003_FullTank/experiments/drive_chains/engine_crankshaft_build.py
python3 cad/003_FullTank/experiments/drive_chains/check_engine_crankshaft.py
python3 cad/003_FullTank/experiments/drive_chains/check_engine_crankshaft_exchange.py
python3 cad/003_FullTank/experiments/drive_chains/render_engine_crankshaft.py
```

For a fresh trial, supply an absolute `--output` directory to the builder and the
same `--candidate` directory to the other commands. Controls are script parameters;
editing displayed properties alone does not regenerate these BReps.

Next source-owned shaft pieces include twelve crankpin plugs, eleven main-journal
plugs, end plugs/gaskets, retaining studs and hardware, six small oil plugs, the
driving gear/bolts/shims and thrust-nut locking screw/wire. SNL212's LQ366A pin-plug
designation conflicts with individual SNL156 and stud association SNL240, both
LQ266A; the latter is selected for later work with the contrary literal retained.
Cylinders, rods, pistons, valve gear, accessories and services follow. Combined
drivetrain qualification, a fresh nominal reproduction and standard integration
remain required. No complete-engine or complete-tank claim is made here.


Subsequent [shaft-closure development](P01-engine-shaft-fittings.md) adds the source-selected plugs, gaskets and retaining sets. It revises internal closure seats, the inferred blind nose termination, the key-screw receiver floor and capped oil-drill entries while preserving the other 1,991 parent constituents. The earlier checkpoint and its original receipts remain intact.
