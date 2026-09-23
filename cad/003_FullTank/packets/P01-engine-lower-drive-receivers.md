# P01 — lower distribution drive receiving casting

Status: **receiver development candidate; full installation unqualified**,
23 September 2026. This extends the [lower-drive component study](P01-engine-lower-distribution.md).
Standard geometry and identifiable interiors remain the priority before poses.

The candidate revises one integral lower crankcase in the 2,170-occurrence
development document. It adds no separately counted parts: all 17 lower-drive
constituents and the other 2,152 inherited occurrences remain present. The native
document includes drivetrain context; its count is not additive to the tank BOM.

## Source interpretation and geometry

LIB23/28 describes a cylindrical lug cast into the lower crankcase to receive the
split lower-drive housing. The SNL19 section shows the long housing screw and
supporting casting. LIB96 shows an offset bottom opening with the oil pump
removed. LIB79/107 and SNL14/17 show the horizontal water-pump installation and
its conical bearing retainer. These sources support the arrangement; they do not
print the new casting dimensions.

The [receiver controls](../experiments/drive_chains/engine_lower_drive_receiver_controls.json)
and [source dossier](../experiments/drive_chains/engine_lower_drive_receiver_sources.json)
retain those distinctions. The cylindrical lug receives the 43 mm radius housing
with an estimated 0.05 mm radial gap and 6 mm wall. It stops short of the housing
ends: 18 mm at the bottom and 8 mm at the top. An estimated annular recess above the lug leaves a route from the radial
oil-entry ports to the space above. The long screw retains its printed 3/8 ×
3-1/4 inch dimensions; the new cast support reaches its head seat and has a
clearance bore. Screw threads remain nominal smooth envelopes.

The bottom opening has estimated radius 94 mm, centered at engine-local X1198,
retaining approximately 45.9 mm offset from the driver axis. Its outer mounting
rim has radius 106 mm and lies at Z−254. The deeper well leaves a continuous
bottom rim beneath the rear pump opening. The local rear bay ends at X1294;
the water-pump mounting face extends to X1368 with estimated opening radius
56 mm and outer radius 64 mm. Pump attachment holes, hardware, oil connections
and complete pump assemblies remain to be populated.

The water-pump axis follows the lower driver's provisional 184 mm drop. The
former 154 mm aperture was also estimated. This revision makes the candidate's
interfaces consistent; it does **not** prove the historical axis spacing. The
actual water-pump retainer, bearing, shaft, gear and casing must constrain the
final choice. SNL160:018 supplies a useful future constraint: the pump bearing
has printed outside diameter 1.8504 inches, bore 0.6693 inches and width
0.5512 inches.

The earlier handoff's requirement for separate upper-edge oil-entry notches is
not established by the labels in LIB88: its oil-entry arrows point to drilled
ports and the bearing groove. The drawing also shows rim/counterbore steps,
whose precise shape remains uncertain. Its housing retains a cylindrical
outside; curved windows and bolt-access pockets account for much of the
waisted appearance. Refine those contours against matched views without adding
an unsupported concave outside or declaring the current profiles exact.

HB109 repeats mark 8345 for both gasket and bearing retainer. SNL99:003 identifies
8345 as gasket LQ154A, while SNL164:025 identifies retainer LQ140A/8069/B14333.
SNL161:001 calls LQ151A a gasket; SNL217:016 identifies it as thin shim 8510.
These literal differences are retained for the water-pump packet.

Regenerate this stage with
`python3 cad/003_FullTank/experiments/drive_chains/engine_lower_drive_receiver_build.py`.
The native case carries `LowerDriveReceiverInputs` and
`LowerDriveReceiverRegeneration` properties for this revision, alongside the
inherited case inputs. Dimension changes require regeneration; those metadata
properties are not live feature expressions.

## Validation scope

The receiver checker reads the saved native shapes independently of the builder.
It checks supporting material, the screw seat and clearance bore, connected oil
access, both pump openings and the complete bottom mounting rim. All casing
material outside a fixed receiving region must be preserved in both directions;
all other occurrence material and every frame must be preserved.

The withdrawal test includes **16 constituents together**: the integral driver,
two bushes, two housing halves, dowel and both five-piece clamp sets. Only the
housing retaining screw is excluded. It first verifies that these saved shapes
fit within a cylinder, then checks the entire continuously swept cylinder against
the actual casing. This proves a conservative continuous casing clearance, not
just a series of empty sampled positions. Actual separation from the retained
main bevel is checked at sampled stations. HB99 dismounts the water pump before
HB100 discusses the driver; both pump assemblies must be removed for this study.
No complete tank service route or pose variant is claimed.

The initial candidate had no overlaps in 261 affected material pairs, including
standard tank context, but two access checks failed. A straight radial oil-route
witness struck the rear wall; the revised model provides an annular recess and
tests a connected radial-then-upward path. The screw-support cone also intruded
into the pump opening; that passage is now machined after all casting additions.
The [initial diagnostic](../experiments/drive_chains/engine_lower_drive_installation/diagnostics/initial_receiver/README.md)
preserves the rejected checks and views. Numerical acceptance tolerances remain
unchanged.

A second candidate cleared both access routes and all 261 material pairs, but
machining the pump passage interrupted the bottom of the lug. Increasing the
estimated lower inset from 8 to 18 mm leaves a complete supporting ring above
that opening. Its [diagnostic](../experiments/drive_chains/engine_lower_drive_installation/diagnostics/oil_pump_access/README.md)
preserves the failed support check; the upper inset remains 8 mm.

The next candidate passed the native interfaces, neighbor checks and actual
gear mesh, but failed the strict native/STEP tolerance criterion. A focused
[cleanup diagnostic](../experiments/drive_chains/engine_lower_drive_installation/diagnostics/cleanup_tolerance/README.md)
localized the increase to optional `removeSplitter()` face unification. The
valid shape before cleanup has zero added or missing material relative to the
cleaned shape and passes the original STEP limits. The generator now retains
that shape if cleanup increases its maximum kernel tolerance. No casting
dimension, fit allowance or acceptance tolerance was changed for this repair.

Final native, STEP, mesh/free-play, parameter-trial and reproduction receipts are
recorded in the saved checkpoint below. The full engine, pump fit,
historical dimensional registration, inventory reconciliation and standard tank
integration remain open.

## Saved checkpoint evidence

The [native candidate](../experiments/drive_chains/engine_lower_drive_installation/DrivetrainWithLowerDriveReceivers.FCStd)
passes **25 independent checks and 261 affected material pairs**, including
standard tank context. All three earlier casing interferences are resolved. The
other 2,169 occurrences retain full material and every frame is preserved. The
entire 16-constituent removable unit clears the actual case continuously; the
retained main gear clears the actual moving parts at ten sampled stations.

Both casing STEP comparisons pass in definition and installed coordinates under
the original strict material, centroid and kernel-tolerance limits. A coupled
seven-control trial passes 25 checks / 263 pairs and both STEP comparisons.
A fresh empty-output build reproduces all serialized geometry, object types and
checked placement/link/hierarchy/identity metadata. It does not depend on a stale
candidate document. The builder starts from the committed component-study native,
revises one case and adds no duplicate unit.

Nine rotations over a main-gear tooth pitch show zero overlap for the actual
saved 128-station integral lower driver. The deliberate half-tooth misphase
produces substantial overlap. Native contact bracketing puts circumferential
backlash within the source 0.127–0.254 mm cold range at outer, middle and inner
pitch stations. This is geometric evidence, not load or manufacturing qualification.

See the [native checks](../experiments/drive_chains/engine_lower_drive_installation/independent_checks.json),
[STEP checks](../experiments/drive_chains/engine_lower_drive_installation/exchange_checks.json),
[mesh checks](../experiments/drive_chains/engine_lower_drive_installation/mesh_checks.json),
[trial](../experiments/drive_chains/engine_lower_drive_installation/variants/trial_receipt.json),
[reproduction](../experiments/drive_chains/engine_lower_drive_installation/reproduction_checks.json),
and [source comparison gallery](../experiments/drive_chains/engine_lower_drive_installation/source_review/index.html).

Six native views were inspected. Their case support and openings follow the
source arrangement; exact cast profiles, the pump position and the incomplete
housing-window contours remain approximations. Two new images bring the visual
progression to 133. All 131 previous images and 20 standard native documents remain
unchanged. Full pumps, attachment holes/hardware, engine internals/services and
standard tank integration remain incomplete.
