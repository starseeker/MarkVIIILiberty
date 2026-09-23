# P01 — crankshaft closures and retaining hardware

Status: **verified development checkpoint; historical geometry remains provisional**, 23 September 2026.
This is a partial powerplant checkpoint, not a complete engine or tank.

## Scope and ownership

The [candidate](../experiments/drive_chains/engine_shaft_fittings_build/DrivetrainWithEngineShaftFittings.FCStd)
extends crankshaft checkpoint `e8b557c`: **139 new physical constituents, one
revised forging and 1,991 unchanged inherited occurrences**, for 2,131 physical
occurrences in the development assembly. This includes existing drivetrain
context; it is not a count to add to the standard tank BOM.

The new `EngineShaftClosures` container belongs to `EngineRotatingAssembly`.
Twelve nested retaining groups each own two caps, two large gaskets and the seven
constituents of a stud set. One nose plug and six oil-access plugs are separate
leaves. Sixteen shared definitions supply the 139 occurrences. Containers,
definitions and installed occurrences are counted separately.

| Constituent | Installed count | Selected evidence |
|---|---:|---|
| LQ266A crankpin plug | 12 | SNL156:001; SNL240:008 |
| LQ265A main-journal plug | 11 | SNL156:003; SNL212:022 |
| LQ263A gear-end plug | 1 | SNL156:002; SNL212:019 |
| LQ256A nose plug | 1 | SNL156:004; SNL212:024 |
| LQ257A small oil-hole plug | 6 | SNL212:023 |
| Unmarked large pin/main gaskets | 12 / 11 | SNL212:025–026 |
| LQ264A gear-end gasket | 1 | SNL97:031 |
| LQ271A / LQ270A / LQ269A studs | 5 / 6 / 1 | SNL239:023; SNL240:003; SNL231:037 |
| Small stud sealing gaskets | 24 | Detailed stud compositions |
| LQ198A / LQ272A nuts | 12 / 12 | Detailed stud compositions; conflict below |
| LQ166A washers / split pins | 12 / 12 | Detailed stud compositions |

## Evidence and interpretation

The [source dossier](../experiments/drive_chains/engine_shaft_fittings_sources.json)
retains 58 literal records, 21 hashed assets, six source-page records and explicit
decisions. The [37 controls](../experiments/drive_chains/engine_shaft_fittings_controls.json)
separate printed dimensions from reconstruction estimates. Source constraints
include 9.525 mm stud diameter, 102.39375/115.09375 mm main/pin stud lengths,
17.4625/12.7 mm threaded end lengths and a 2.38125 × 15.875 mm split pin.

Catalogue conflicts remain visible:

- SNL212 prints LQ366A for the pin plug; the individual entry and stud association
  identify LQ266A. The latter is selected, without deleting the contrary text.
- The individual LQ272A entry gives seven nuts, while the twelve detailed stud
  compositions each include one. The model provisionally selects twelve.
- LQ166A is called 3/8 inch on SNL232/239 and 5/8 inch on SNL240/273. A bore fitting
  the printed 3/8 inch stud is selected; washer OD and stock remain estimates.
- SNL97 calls LQ265A a gasket with the same manufacturer number as the plug.
  The separate unmarked main-journal sealing gasket is retained; the conflicting
  description does not create an additional physical part.
- The mixed US Standard/SAE stud ends and the SAE nut descriptions do not establish
  compatible detailed threads. Smooth nominal envelopes are modeled. The plain
  and castellated nut forms are reconstruction assumptions.

Liberty text distinguishes early soldered discs from later bolt-retained caps.
The tank SNL supports the latter arrangement. Aviation geometry is conditional
evidence; neither the photographs nor the catalogue supplies a complete machining
drawing of these closures.

## Geometry decisions

The inherited engine frame is unchanged: X runs nose to gear; the engine is
installed at the existing development placement. Printed stud lengths constrain
the complete estimated cap/gasket/nut stack. Main caps recess 0.272875 mm at each
end. Pin caps recess 24.11675 mm at the nose side and 2 mm at the gear side. This
asymmetric choice leaves the inherited rear-web oil drill inboard of the cap;
it is a fitted inference, not a recovered source dimension. The gear-end stud
length is derived from its stack because no printed length was established.

Eleven ordinary main caps are assigned to five paired interior journals and the
inboard end of the gear journal. A blind inner termination of the nose journal
accounts for the remaining source inventory without inventing a twelfth cap.
This blind termination is an inference from counts. The reduced 14 mm nose bore
leaves material behind the inherited key-screw receiver. Its axial transition,
blind stock and fitted nose-plug profile are estimated. The nose plug sits inboard
of the existing output cotter.

Each rear-web oil drill receives an external machining access, closed by one
separate small plug. The cap lips, gaskets, counterbores, plug recesses and oil
access dimensions are provisional. Threads, seal compression, pressure-tightness,
materials performance and mechanical strength are not qualified by these solids.

## Validation and visual review

Build, independent native checks, material checks, STEP round trip and parameter
variation are separate gates. Current receipts live beside the candidate. The
initial native checker passed all six continuous oil routes and all 738 affected
material pairs, including standard context. Six distance checks initially confused
oil-plug bottom contact with radial clearance; the diagnostic retains that failure.
The corrected checker separately tests bottom contact and a middle plug slice.
No native geometry or numerical acceptance tolerance changed for that correction.

Parent preservation compares placements and serialized BRep definitions; where
save normalization changes bytes, it compares material in both directions.
The revised shaft is checked against independently bounded edit regions, retaining
the old material outside the plug/nose/oil-access work. Finite-radius connected
witnesses run from each rear main inlet around its stud, through the web, around
the pin stud and out the big-end radial port. These test geometric connectivity,
not oil-flow capacity.

The [review gallery](../experiments/drive_chains/engine_shaft_fittings_build/source_review/index.html)
provides an installation isometric, exposed shaft and sections through a pin set,
main set, gear set, nose and oil web. Figures 17 and 107 provide arrangement
context; SNL156/212/239/240 provide identities, quantities and stud sizes. The
source images do not resolve every hidden closure profile. Cameras are not fitted.
The initial nose camera concealed the key-screw receiver; its corrected section
uses a different half-plane. The gear caption explicitly calls its stud length
derived. Review cuts and hidden casing do not change the physical assembly.

The final nominal candidate passes **268 independent checks, 738 affected
material pairs including standard context, and 157 native/STEP comparisons**
(17 definitions and 140 affected installed shapes). No positive-volume overlap
was found. The seven final views were directly inspected; source camera/profile
fit remains unqualified. The corrected nose section exposes the blind screw
receiver and the inboard plug/cotter relationship.

A coupled trial changes cap stock 3.175→3.5 mm, large gasket stock 0.8→1 mm and
nose-bore radius 14→13.5 mm. It retains the printed stud sizes and passes
268 independent checks and 738 material pairs, including standard context.
This is a reconstruction robustness trial, not a tank pose. Trial STEP and fresh
nominal reproduction remain unverified. The
[checkpoint receipt](../experiments/drive_chains/engine_shaft_fittings_build/development_checkpoint.json)
records the native, source, checks, trial and visual hashes. Three progression
images bring the total to 126, preserving all 123 earlier snapshots and all
20 standard native files.

## Reproduction and remaining work

From the repository root:

```bash
python3 cad/003_FullTank/experiments/drive_chains/engine_shaft_fittings_build.py
python3 cad/003_FullTank/experiments/drive_chains/check_engine_shaft_fittings.py
python3 cad/003_FullTank/experiments/drive_chains/check_engine_shaft_fittings_exchange.py
python3 cad/003_FullTank/experiments/drive_chains/render_engine_shaft_fittings.py
```

Use `--output` and `--candidate` for a separate work directory; `--controls`
selects a different control file for the builder. Changing controls requires
regeneration; metadata is not a live parametric dependency graph.

Next shaft work comprises LQ258A driving gear, six LQ262A bolt sets, source shim
selection and LQ276A/LQ277A thrust-nut lock screw/wire. Cylinders, rods, pistons,
valve gear, accessories and services remain substantially incomplete. Fresh
nominal reproduction, combined drivetrain qualification, source registration,
mounting reconciliation and integration into the standard tank remain open.
P01, I01 and the full-tank goal remain incomplete.


Subsequent [driving-gear development](P01-engine-driving-gear.md) installs the bevel, selected shim, six bolt sets and thrust-nut lock. It preserves this checkpoint and adds only local shaft/nut receiver holes; mating gears and final shim/backlash/timing remain open.
