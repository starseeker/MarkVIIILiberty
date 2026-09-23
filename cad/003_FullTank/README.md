# Complete-tank workflow and execution queue

This stage contains the **full-tank installation layout, closed track loops and
individual upper/main hull plates, hollow sponson plate shells, roof louvers and
lower/upper roller stacks, upper/lower support angles, partial front idler wheels/adjusters and driving wheels with partial shafts/bearings and roller pinions**. The complete
tank remains in progress.
Follow the [complete-tank workflow](../../docs/complete-tank-workflow.md).
The working target is the Rock Island first-100 production configuration, all
identifiable installed components including interiors, documented approximations,
and selected static poses. The user confirmed the interior and pose scope on
19 September 2026.

The current priority is to fully populate the standard assembled configuration,
including identifiable interiors. Pose variants follow that geometry work.
Preserve significant standard-view milestones as numbered
`../intermediate_snapshot_iso_NNN.png` images and update the
[visual progression](../VISUAL_PROGRESSION.md); keep existing snapshots intact.

`work_queue.json` is the dependency-ordered work inventory. Packet statuses record
actual progress; acceptance criteria describe the complete required result.
The validated foundation remains in
[`../002_Foundation/`](../002_Foundation/README.md).

When starting a packet, copy the
[work-packet template](../../docs/templates/cad-work-packet.md) to `packets/<ID>.md`.
Keep evidence records and geometric outputs tied to those packet IDs. The queue
is a scheduling aid; it does not replace the eventual configuration-specific
component inventory, occurrence BOM or parameter registry.

## Run and inspect

From the repository root:

```sh
python3 cad/003_FullTank/manage.py inventory
python3 cad/003_FullTank/manage.py check
python3 cad/003_FullTank/manage.py build
python3 cad/003_FullTank/manage.py validate
```

Open **build/native/MarkVIII.FCStd** in FreeCAD. Keep its library and subsystem
directories with it. The standard assembly contains 11 layout definitions,
seven track definitions, 26 upper plate/leaf definitions and 77 main hull plate
definitions, plus 39 sponson plate, 19 louver, 14 roller, ten wheel, eleven idler-mount, ten drive-mount, ten pinion and eighteen lower-support definitions. Its 5,341 leaves comprise 15 layout
occurrences (13 solids and two wires), 2,964 components in two 78-unit tracks,
103 upper/main hull plates, 39 sponson plates, 82 louver components and 1,228
components in 60 roller stacks (58 lower and two separate handbook upper, including four M2092 angles), plus 306 idler wheel, shaft and adjustment components, 110 lower support/bolt components 298 driving-wheel/shaft/bearing components and 196 pinion/shaft/mount components.
Each shoe unit has the 19 physical leaves specified by the SNL. Upper and main
hull plates cover 84 source identities, with hollow enclosures, floors, open
sponson/louver apertures and closed standard leaves. All physical definitions
retain partial coverage. Exact drive shaft/bearing and tensioner profiles and inner plate retention, continuous drive/idler engagement, exact lower support sections and removable retention, upper attachment and covers, remaining hull structures/fittings,
sponson shields/supports/fittings, louver spacing/support hardware and interiors remain open; no complete tank is claimed.

Open **build/comparisons/index.html** for source/model comparisons. The SNL
longitudinal overlay projects actual native edges through the fixed recorded
calibration; its opacity slider exposes differences. The independently retained
handbook cutaway appears beside a model view. No automatic fit is applied to make
either comparison agree. Source-traced profiles are explicitly distinguished from
independent dimensional or visual checks. Shaded views use software rendering;
native CAD and STEP remain BRep geometry. Track close-ups compare the actual
three-unit reconstruction with HB Plate 84. Shading and visible native edges
distinguish the shoe, paired link bars and connecting hardware. Whole-vehicle
previews omit small track hardware for legibility; close views, native documents
and physical STEP exports retain it. Upper close-ups compare front/rear plate
assemblies with SNL7 and HB30, with an underside view confirming hollow shells.
Main hull views compare oblique and opposite-side native projections with
SNL7/1, plus an underside inspection. See [S01](packets/S01.md) and
[H01](packets/H01.md) for source conflicts and geometric approximations.
Sponson close views show both handed shells, their hollow interiors and lower
plates; see [the sponson packet](packets/S01-sponsons.md). Louver oblique/top and
blade-section views accompany SNL4; see [the louver packet](packets/X01-louvers.md)
for conflicting counts and section assumptions. Roller oblique and transverse
section views accompany HB88/89 and SNL29. The [upper support packet](packets/R02-upper-supports.md) records the corrected pin/angle interface and unfinished attachment. See [R02](packets/R02.md) for the
separate quantity scopes, dimensional conflicts and reported source-station
offsets. The upper roller position follows the rear roof bend and HB144's
engine-room access description. The [idler-wheel packet](packets/R02-idler-wheels.md) records the separate rims, disks, boss, diaphragms, rivets and bushes, including the coupled foremost-roller clearance correction. The [mounting packet](packets/R02-idler-mounts.md) covers the two source-complete shaft BOMs and partial adjustment installations. Source comparisons include elevation, transverse section, mounting detail and adjustment-axis section views. Earlier visual milestones remain in the
[visual progression](../VISUAL_PROGRESSION.md); the latest mounting milestone is
[snapshot011](../intermediate_snapshot_iso_011.png), with preserved
[pinion and wheel](../intermediate_snapshot_detail_pinions_011.png) and
[pinion shaft/support](../intermediate_snapshot_detail_pinion_mounts_011.png) close-ups.
A [transparent-hull isometric](../intermediate_snapshot_iso_transparent_011.png)
exposes the enclosed components; its armor uses 18% display opacity. The colored
interior layout envelopes remain provisional. The
[pinion packet](packets/R02-roller-pinions.md) records the source counts, static
clearances, inferred fuel-backplate station and unresolved tooth-count conflict.
The [drive-wheel packet](packets/R02-drive-wheels.md) records the source tooth-count
conflict, shared wheel geometry and corrected rim alignment. The
[drive-mount packet](packets/R02-drive-mounts.md) records the completed source shaft
BOMs, corrected receiving-plate identities and partial bearing interfaces.
The [installed support close-up](../intermediate_snapshot_detail_supports_008.png)
remains preserved from snapshot 008.
The [lower-support packet](packets/R02-lower-supports.md) records source allocations,
front skirt refinement, native bearing/receiver checks and unfinished retention.

The latest isolated [transmission candidate](experiments/drive_chains/transmission_case_mount_trial_build/MX5CaseMountTrial.FCStd)
contains **1,407 valid solids**, including both planetary trains, bevel drive,
input installation, brake-bearing supports, case joint, reversing controls and
four MX5 case attachments. The [mounting packet](packets/I03-case-mount-trial.md)
accepts the long receiver bosses as a documented casting approximation; their
visible source-profile discrepancy remains explicit. The trial filename and
original receipts are preserved; subsequent `qualification.json` records this
acceptance. All 183 affected material pairs, 61 interfaces, 84 independent checks,
19 STEP comparisons and three local variants pass.
The preceding [vertical-controls packet](packets/I03-vertical-controls.md)
retains the 1,391-solid checkpoint with its shaft,
keyed levers, two bearings and distinct MX11/MX12 attachments. All 148 affected
material pairs, 21 native/STEP comparisons, 116 independent checks and three
parameter trials pass; 63 interfaces are rechecked and 641 retained. Seven
inspected views record the remaining source-contour differences. Three new
snapshots show the [installed rear](../intermediate_snapshot_iso_transmission_vertical_001.png),
[mechanism](../intermediate_snapshot_iso_transmission_vertical_mechanism_001.png)
and [bearing/key section](../intermediate_snapshot_detail_vertical_bearing_001.png).
No. C key dimensions and blind bearing construction remain inferred. The
[air-pressure pump](packets/I05-air-pressure-pump.md), separate input-bearing
support, brakes, oil circuits, long controls and standard tank
integration remain ahead. Standard tank 011 and its transparent companion are unchanged.
The existing M249 quantity, MX25 count/nut and MX14 length conflicts remain open
in the preceding packets.

The separate [air-pressure pump native assembly](experiments/drive_chains/air_pressure_pump_build/AirPressurePump.FCStd)
adds 51 source-linked physical pieces, including four pistons and return springs,
a cam shaft, bushes and pulley. Its [assembled STEP](experiments/drive_chains/air_pressure_pump_build/AirPressurePump.step),
[isometric](../intermediate_snapshot_iso_air_pressure_pump_001.png) and
[internal view](../intermediate_snapshot_iso_air_pressure_pump_internals_001.png)
are available for inspection. All 139 local material pairs, 104 independent checks,
17 detailed STEP comparisons, 51 placed-solid exchange checks and two dimension
trials pass. The [pump packet](packets/I05-air-pressure-pump.md) records scale and
hidden-detail approximations. This core is not yet part of the standard tank011 assembly.

The subsequent [pump mounting reconstruction](experiments/drive_chains/air_pump_mount_build/TransmissionWithAirPump.FCStd)
combines that pump with the transmission and adds 32 bracket/stud/fastener pieces,
including the twelve base-attachment pieces. Its 1,490 physical leaves retain
separate FuelPressure and Drivetrain ownership. The
[installation STEP](experiments/drive_chains/air_pump_mount_build/AirPumpInstallation.step)
exports the 83 additions and two revised receiving castings. Pump height, bracket
shape and MX99 construction remain explicit hypotheses, with
[handbook comparison](experiments/drive_chains/air_pump_mount_build/source_review/source_comparison.png)
and a conditional 54-inch belt study. Clutch-stop drive geometry, air lines and
standard-tank integration remain unfinished at that checkpoint.

The [clutch-stop drive candidate](experiments/drive_chains/clutch_drive_build/TransmissionWithClutchDrive.FCStd)
extends the combined model to **1,520 physical components**. It adds the coupling
box, two cover halves, stop drum, shaft, eight bolt/nut/washer sets and a closed
V-belt representation. The belt fit moves the pump and its supports together.
[HB/SNL comparison](experiments/drive_chains/clutch_drive_build/source_review/index.html)
led to a wider shaft head; its transverse form and the handbook-to-catalogue
shaft dimension transfer remain uncertain. The [packet](packets/I03-clutch-stop-drive.md)
records scope, approximations and checks. The full clutch, air circuit and standard
tank integration remain unfinished.

The [front-clutch checkpoint](experiments/drive_chains/front_clutch_build/TransmissionWithFrontClutch.FCStd)
extends the combined native to **1,530 physical components** with a front
coupling, split spring flange, seven-turn NURBS spring and two fastening sets.
It also blends the cardan shoulders and relieves the adjacent receiving passage.
All 88 material pairs, 70 independent checks, 8 definition STEP comparisons,
12 placed-solid exchange checks and two size trials pass. The
[source comparison](experiments/drive_chains/front_clutch_build/source_review/index.html)
and [packet](packets/I03-front-clutch.md) retain the coupling identity transfer,
spring diameter convention and catalogue bolt-callout mismatch. The
[isometric](../intermediate_snapshot_iso_front_clutch_001.png) shows the installed
spring and coupling; the main collar, cones, bearings and standard integration
remain unfinished.

The subsequent [collar-joint checkpoint](experiments/drive_chains/clutch_collar_build/TransmissionWithClutchCollar.FCStd)
contains **1,540 physical components**. Closer SNL inspection required separate
spring and collar flanges and a forward end-bearing pocket; the earlier coupling
approximation remains preserved. The new collar, ring, bush, six drilled screws
and continuous locking wire complete this joint. All 104 independent checks,
65 local interference pairs, 8 definition STEP comparisons, 20 placed-solid
exchange checks and two size trials pass. The [source comparison](experiments/drive_chains/clutch_collar_build/source_review/index.html)
shows the corrected and earlier sections, and the [packet](packets/I03-clutch-collar.md)
records estimated stations, bearing fits and wire geometry. The
[isometric](../intermediate_snapshot_iso_clutch_collar_001.png) preserves this
stage. Main internal clutch parts, cones, operating connections and standard
integration remain unfinished; tank 011 retains its transparent hull companion.

The [main-clutch core](experiments/drive_chains/clutch_stack_build/TransmissionWithClutchStack.FCStd)
now contains **1,549 physical components**: a relieved bearing, nested sleeve,
four keys, cone support, thrust collar and separate external snap ring extend
the 1,540-component parent. Full SNL callout tracing corrected the first core's
end-ring mapping; its rejected native and images remain preserved. The
[source comparison](experiments/drive_chains/clutch_stack_build/source_review/index.html)
shows the full plate and both sections. The [packet](packets/I03-clutch-stack.md)
records the correction, HB/SNL dimensional transfers and thicker key bands from
the literal handbook interpretation. Ball reaction, cones, spring plungers,
exact drive attachment and engine engagement remain unfinished; standard tank
integration follows.

The next [clutch thrust checkpoint](experiments/drive_chains/clutch_thrust_build/TransmissionWithClutchThrust.FCStd)
contains **1,581 physical components**, adding a separate SH998C retainer,
30 quarter-inch balls sharing one definition, and the SH998A spring-stop ring.
The existing thrust collar now has a receiving race; all other 1,548 parent
occurrences retain their geometry and placement. All 95 affected material pairs,
460 independent checks, four definition STEP comparisons, 33 placed-solid checks,
two coupled size trials and a fresh rebuild pass. Seven fine native/source views
were inspected. The [packet](packets/I03-clutch-thrust.md) records estimated race,
cage and ring geometry, the contact-query diagnostic and unfinished plunger/cone
interfaces. The [source comparison](experiments/drive_chains/clutch_thrust_build/source_review/index.html)
retains the full SNL figure. Standard tank011 remains unchanged.

The [cone and spring checkpoint](experiments/drive_chains/clutch_cone_build/TransmissionWithClutchCone.FCStd)
contains **1,652 physical components**. It adds 71 occurrences across nine shared
part definitions and refines the existing cone support; 1,580 parent components
retain their geometry and placement. All 326 affected material pairs, 462
independent checks, ten definition and 72 installed STEP comparisons pass, along
with two coupled dimension trials and a fresh rebuild. Seven native/source views
were inspected, and four new progression snapshots are preserved.

The [packet](packets/I03-clutch-cone.md) records conditional handbook dimensions,
conflicting spring free lengths and estimated receiving profiles. Independent
hole checks caught two bad Boolean cuts despite passing whole-part interference
and STEP tests; the corrected cutters and retained diagnostics are included.
The [source review](experiments/drive_chains/clutch_cone_build/source_review/index.html)
shows the full SNL figure beside actual native sections. SH861K plunger locking
wire/head holes were unfinished at that checkpoint.

The [plunger retention checkpoint](experiments/drive_chains/clutch_retention_build/TransmissionWithClutchRetention.FCStd)
contains **1,653 physical components**: one new SH861K wire, six revised plunger
heads sharing one definition, and 1,646 preserved parent occurrences. The wire
retains the catalogue 30in length; diameter, head passages and route are documented
estimates. All 84 independent checks, 68 material pairs, nine STEP comparisons,
two parameter trials and a fresh rebuild pass. Five views were inspected and
three new progression snapshots are saved. The [packet](packets/I03-clutch-retention.md)
records these checks and the numerical volume diagnostic.

The latest [clutch release development candidate](experiments/drive_chains/clutch_throwout_build/TransmissionWithClutchThrowout.FCStd)
contains **1,758 physical components**. It adds the two release bearings, pins and
retaining hardware, forks, main shaft, operating lever and three keys. All90
independent checks,332 affected material pairs and93 STEP comparisons pass;
a coupled parameter trial also passes. Bearing internals and unprinted lever/
shaft profiles are explicit estimates. The [packet](packets/I03-clutch-throwout.md)
records unresolved source alignment and remaining brackets, retention and brake
linkage. Three new progression images bring the total to105. This development
candidate is unqualified; standard tank011 remains unchanged.

The earlier [clutch-stop band development candidate](experiments/drive_chains/clutch_stop_band_build/TransmissionWithClutchStopBand.FCStd)
contains **1,681 physical components**, including the band, lining and seventeen
rivets. The printed stop-drum diameter now controls the coupled belt/pump update.
Geometry, STEP and two parameter trials pass, but the anchor and operating
linkage remain missing. This candidate is unqualified; its
[packet](packets/I03-clutch-stop-brake.md) records the source-envelope questions
to resolve before mounting those parts. Three new progression views bring the
total to 102. Standard tank011 remains unchanged.

The latest qualified [drum/flywheel checkpoint](experiments/drive_chains/clutch_drum_build/TransmissionWithClutchDrum.FCStd)
contains **1,662 physical components**. It adds the outer drum, flywheel, six
drilled screws and their 48in wire. The existing 30in plunger wire now routes
inward to clear the flywheel; the other 1,652 parent occurrences remain unchanged.
All 270 independent checks, 262 interference pairs, 15 STEP comparisons, two
coupled parameter trials and a fresh rebuild pass. Six views were inspected and
four new progression images preserve the visual improvement.

The [packet](packets/I03-clutch-drum.md) records the uncertain hub interpretation,
starter tooth count and flywheel dish profile, including its visible difference
from the handbook sketch. Next are the clutch-stop brake and complete crankshaft,
key/nut retention and starter interfaces. Standard tank011 remains unchanged;
full tank geometry and integration remain incomplete.

Additional commands:

```sh
python3 cad/003_FullTank/manage.py dossier P_a18a32069ef93911
python3 cad/003_FullTank/manage.py build --subsystem Powerplant
python3 cad/003_FullTank/manage.py validate --subsystem Powerplant
python3 cad/003_FullTank/manage.py review
python3 cad/003_FullTank/manage.py export
python3 cad/003_FullTank/tools/transparent_isometric.py
python3 -m unittest discover -s cad/003_FullTank/tests -v
```

Subsystem builds use their own output directory under build. All commands accept
`--output DIRECTORY`. The launcher uses the installed, tested FreeCAD 1.1.1
libraries directly, with its own settings/cache directories; the desktop Snap
launcher does not need to work in the sandbox.
Preview rendering also uses the installed C compiler to build a small software
depth-buffer renderer, cached by its source hash. Repeated definitions reuse a
single tessellation; this does not change the native geometry.

Native features include constrained sketches, pads, revolved cubic B-spline
roller profiles, analytic BRep features and a closed shoe pressing with native
quartic NURBS top/bottom surfaces. Their authoritative
inputs are the records under data and the Python builders. A GUI feature edit can
be inspected, but transfer it back into those inputs before regeneration.
The current layout does not yet provide multiple selectable detail representations,
completed component internals or motion poses. The two static track loops are
closed at every shared pin. Static roller-to-rail clearance is checked; drive/idler
engagement, complete support interfaces and continuous motion remain unqualified.

Validation checks occurrence coverage, actual nested placements against named
datums, shape validity, STEP equivalence, native relocation, an independent
rebuild, unchanged-definition cache reuse, a fuel-tank spacing change and a track
pitch change through nested component placements. Upper checks add independent
SNL plate quantities, handed opening order, nominal material intersections,
hollow interiors, sampled armor thicknesses and a main-width propagation trial.
Main hull checks add source quantities, plate/upper/track material contacts,
lower shell spacing, floor clearance, louver openings and a shell-gap trial.
Sponson checks add independent quantities, handed opening/absence probes, normal
armor thickness, hollow interiors, whole-vehicle width and physical contacts.
A roof-thickness trial verifies inward growth, adjoining wall updates and
unchanged floors. Louver checks add source quantities, exact curved-section
dimensions, open-passage probes, guard projection, physical contacts and a blade
thickness trial. The full pitch trial checks sponson and louver interfaces.
Track checks independently read
the SNL assembly composition and test actual component intersections. Selected
joint-bend trials record limits without claiming a continuous permitted range.
It reports remaining complete-tank gates separately. Reference-envelope overlaps
are not accepted as proof of physical component fit.

The milestone011 qualification retains the original 29-stage/17-parameter-trial
run and 37 record/renderer tests. A fresh main-path check reopened all 20 native
documents and verified every definition, placement and original geometry signature.
The trials were not rerun after this byte-identical geometry transfer. See
[the transfer receipt](releases/011-roller-pinions-transfer.json) and
[release record](releases/011-roller-pinions.json). The original validation
records remain intact under build/reports/qualified_origin.

The inventory includes all 5,482 survey identities, retaining quantity assertions,
variants, issues and review records. Only explicit decisions establish inclusion
or exclusion; the other rows remain production/transfer candidates or unresolved.
The installed vehicle count remains unknown. Generated inventory reports track
which identities have layout or partial component geometry without calling the
vehicle complete. STEP exports separate MarkVIII_Layout.step from
MarkVIII_Components.step.

See [PROGRESS.md](PROGRESS.md) for current findings, remaining gates and the next
implementation work.
The [visual review](VISUAL_REVIEW.md) records inspected artifacts and unresolved
packaging conflicts; [data contracts](DATA_CONTRACTS.md) describe the current
record and placement semantics.

## Implementation organization

The implementation currently uses flat authored JSON records, split into
configuration, parameters, calibrations, datums, definitions and occurrences.
Split these into subsystem directories as their contents grow. The intended
organization is:

```text
cad/003_FullTank/
  README.md
  work_queue.json
  packets/                    evidence, construction and review records
  data/
    configurations/           applicability, quantity scope and selected loadout
    parameters/               typed values, provenance, uncertainty, dependencies
    calibrations/             controls, transforms, residuals and profile traces
    interfaces/               named datums, mounts, axes and ports
    definitions/              geometry builders, identities and representations
    occurrences/              installation hierarchy and local transforms
    poses/                    named static arrangements and supported ranges
    research/                 added sources, reviewed mappings and open issues
  lib/                        reusable evidence, CAD and validation routines
  builders/                   component-family and subsystem generators
  manage.py                   subsystem build/check/export/report entry point
  build/                      generated native, STEP, views, reports and runtime
```

The current command interface and record validation are implemented in manage.py
and lib. Further F02/F03 work adds interface fit contracts and multiple detail
representations. Keep generated files outside authored inputs, and preserve
relative native links in delivery packages. Changes to the frozen survey require
a new research baseline rather than edits here to its published files.

## Queue conventions

- `depends_on` contains packet IDs whose technical outputs must be available.
- `status` records actual work, independently of readiness from dependencies.
- An evidence packet can finish with a bounded documented approximation; it need
  not wait for every archive lead. An unresolved necessary interface keeps the
  affected geometry packet blocked and remains in its issue record.
- Milestone acceptance uses the workflow's gates and all required packets for that
  stage. Later discoveries invalidate affected accepted work and its dependents.
- `accepted_approximate` requires the same geometry/integration checks as
  `accepted`, with its evidence limitations recorded. It does not silently waive
  failed geometry checks or hide unfinished scope.
- The full-tank component count is deliberately unset until F01 and subsequent
  inventory reconciliation establish it.
