# P01 — Liberty water pump

This is the historical `6c42df8` checkpoint. Current work and regeneration commands
are in the [mounting and casting revision](P01-engine-water-pump-mounting.md);
use that commit's frozen inputs when reviewing the earlier implementation.

Status: **development candidate; installation unqualified; pump-body STEP precision issue open**,
23 September 2026. This extends the
[receiving-case checkpoint](P01-engine-lower-drive-receivers.md).

The builder adds a hierarchical water pump to the drivetrain development
document: one geared shaft with its key, nut and bronze cotter; a radial ball
bearing with separate estimated internals; conical retainer; two packing boxes,
two tabbed glands and their spring; pump body and two outlets; open impeller;
inlet cover; sealing/adjustment layers; drain plug; and eight cover stud sets.
The first successful save contains 2,230 physical occurrences, including 60 new
pump constituents in 24 definitions. This count includes drivetrain context
and must not be added wholesale to the standard tank BOM.

## Evidence and unresolved identities

The [source dossier](../experiments/drive_chains/engine_water_pump_sources.json)
retains literal catalogue records, handbook instructions and hashed figures.
SNL160/161 describes pump assembly 12211; SNL21 decomposes body assembly 12071
into casting LQ144A, eight LQ88A stud assemblies and eight LQ113A washers.
SNL216 decomposes geared shaft assembly 8079 into LQ138A, key LQ105A, nut
LQ147A and a bronze 3/32 × 5/8 inch cotter. No separate pump gear is enumerated;
the model represents one geared spindle without claiming its manufacturing
method. The eight cover stud sets retain the printed 1/4 × 1-3/16 inch studs
and 1/16 × 1/2 inch cotters.

SNL160:018 prints the bearing dimensions as 1.8504 inch outside diameter,
0.6693 inch bore and 0.5512 inch width. Their direct conversions are
47.00016 × 17.00022 × 14.00048 mm; these do not imply submicron historical
precision. The two races, seven balls and cage are estimated commercial
internals subordinate to one catalogue bearing, not additional SNL identities.

HB100 and LIB28 describe two packing boxes, each compressed by a gland, with
one spring between them. SNL131:012 also specifies two lengths of packing.
That arrangement is selected here. SNL160:023 nevertheless lists three
LQ141A packing pieces; this quantity conflict is unresolved. HB100 recommends
approximately 8-1/2 inch lengths, whereas SNL131:012 specifies 11-9/16 inch
lengths. The model uses two compressed annular envelopes with explicit
estimated dimensions; it does not purport to reproduce the rope winding.

The catalogue calls LQ151A a gasket in the pump composition and a thin
adjustment shim elsewhere. The candidate models one thin adjustment layer
at the case face. LQ154A/8345 is represented as a separate sealing layer at
the retainer/body joint; that placement and the full attachment stack remain
provisional. HB109's repeated 8345 marking for the retainer is retained as a
source conflict; SNL assigns the retainer LQ140A/8069/B14333.

SNL17 and HB plate52 label both cover12435 and inlet feature12081, but the
pump composition enumerates only cover LQ150A. The candidate treats the cover
and curved inlet as one casting pending corroboration of 12081's ownership.
It does not silently create another separately counted elbow. The source
cover and impeller alternatives in HB99/100 (12078/12073) remain distinct
from the SNL17 identities (12435/12517).

## Geometry and interfaces

The pump's local X axis points outward from the common bevel apex. Its frame
is attached to `TankLibertyEngine` at the inherited main-apex X station and
the provisional Z−184 mm pump axis. The horizontal 21-tooth gear uses the
same estimated module, face width, pressure angle and spline-flank method
as the lower vertical gear. The source requires one-and-one-half engine
speed; the existing 33:22 pair followed by this 21:21 pair supplies that ratio.

The printed bearing envelope constrains the journal and the narrow end of
the retainer. The long conical shell, packing sleeves, gland tabs/slots,
spring and impeller share the same shaft axis. The impeller has an estimated
tapered key seat and six open radial vanes. A full rear shroud in the initial
hypothesis was removed after comparison with the exposed source impeller;
the exact vane section and count still require better source registration.

The pump body contains an open centrifugal chamber and two outlet bores.
Its annular cast chamber is an explicit approximation of the unprinted
scroll profile; no flow performance is claimed. The cover uses a recorded
spline meridian, analytic circular inlet elbow and open straight hose end.
HB98's printed 2 inch inlet diameter applies to that straight barrel. Raised
hose-end rings are estimated from the source figures. Threads are smooth
nominal envelopes.

The current crankcase remains unchanged. The mounting flange is positioned
beyond its face by the selected shim thickness, without moving the gear
apex or bearing. Four pump flange holes exist, but the corresponding case
lug geometry, holes, studs, washers and nuts have not yet been reconciled.
The drain-plug lock wire also remains to be populated. No complete pump
installation or standard tank integration is claimed.

Regenerate with
`python3 cad/003_FullTank/experiments/drive_chains/engine_water_pump_build.py`.
The [controls](../experiments/drive_chains/engine_water_pump_controls.json)
separate printed dimensions from estimates. Definition properties retain
their inputs, source ownership and regeneration command; they are not live
feature expressions.

## Checks and development evidence

The first saved candidate passed 22 of 23 independent checks, including
the printed bearing/key/stud dimensions, open flow paths, and nine rotations
of the actual saved mating gears. A deliberate half-tooth phase shift
produced interference, confirming the mesh test rejects a wrong assembly.
The 202 material comparisons found overlap at the incorrectly placed shim
and at the cover's washer seats. The original candidate and checks remain
in `.work/engine-water-pump/initial_fit_candidate`.

The shim correction moves the retainer flange beyond the case face and opens
the shim bore around the retainer cone. The cover now has local flat washer
seats. Their relief tools are bounded to avoid cutting the remote inlet end;
an independent circumferential wall check guards that passage. An earlier
nut-crown estimate also proved too wide for the printed cotter length and
was reduced without changing the source pin dimensions.

The next revision passed all 26 native checks, including complete preservation
of the 2,170 inherited components, 202 affected material comparisons, nine
mesh samples and eight complete-rotor rotation samples. STEP reopening then
isolated an invalid bearing cage. A
[three-orientation probe](../experiments/drive_chains/engine_water_pump_study/diagnostics/cage_step/README.md)
showed that radial sphere poles preserve the cage's material and pass strict
STEP comparison; axial and tangential poles fail. The revised generator uses
the radial parametrization without changing dimensions or acceptance limits.
The final full assembly passes all 26 native checks; 82 of 84 STEP comparisons pass. The body exceeds the unchanged native kernel-tolerance limit in definition and installed frames. Both exported body solids are valid and have zero material differences; the [body diagnostic](../experiments/drive_chains/engine_water_pump_study/diagnostics/body_tolerance/README.md) records the unresolved issue and rejected trials.

The receiving hardware introduces a further source constraint. SNL239:015–020
specifies [four LQ197A stud sets](../experiments/drive_chains/engine_water_pump_study/inputs/mounting_stud_sources.json), each 3/8 × 1-31/32 inch, with 21/32 inch inner
and 5/8 inch outer threaded ends. Full embedding of the inner threaded end
leaves 17.4625 mm of plain projection before the outer thread starts. The
current estimated 10.65 mm flange/shim stack is too short to seat a thin washer
and nut on that thread. The mounting revision must reconcile flange spacing,
body profile and nut/tool access using those printed lengths.

Current saved-artifact, material-preservation, rotor, STEP and source-view
receipts must be inspected before accepting the final geometry. Full case
attachment, source conflicts, parameter variation, independent regeneration,
oil pump, remaining engine systems and standard integration remain open.


## Current saved artifacts

- [Native candidate](../experiments/drive_chains/engine_water_pump_study/DrivetrainWithWaterPump.FCStd)
- [Native checks](../experiments/drive_chains/engine_water_pump_study/independent_checks.json)
- [STEP checks, including two body failures](../experiments/drive_chains/engine_water_pump_study/exchange_checks.json)
- [Source comparison gallery](../experiments/drive_chains/engine_water_pump_study/source_review/index.html)
- [Development checkpoint and open work](../experiments/drive_chains/engine_water_pump_study/development_checkpoint.json)

Two progression images bring the total to 135. All 133 previous images and
20 standard native files are preserved. The current independent checker includes
all development-document neighbors, but a new full standard-tank context check
has not yet been performed for this pump. Parameter-trial and fresh-reproduction
scripts are prepared in `.work/engine-water-pump` and have not been run.
