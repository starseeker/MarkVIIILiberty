# Engine pump source and installation reconciliation

This is a **development study with unqualified installation** following the
146-part oil-pump mounting checkpoint. The selected
[source-profile candidate](oil_profile_joint_trial/OilPump.FCStd) passes
402 saved-native checks, 482 material comparisons and seven conditional source
envelope checks. Fresh reproduction matches 81 serialized shapes, 629 object
types and 7,376 properties (excluding new UUIDs). Its full STEP qualification
subsequently completed: all 186 comparisons pass, including changed screens.
The standard tank is unchanged; source interpretation, standalone
part validity and installed fit are separate results.

## Newly applied source constraints

HB **printed page 68, Plate 45**, in original `MarkVIII035.jpg`, explicitly
labels its engine view **“AVIATION MOUNTING.”** Its conditional transfer to the
tank therefore remains visible. These are plate numbers, not references to the
prose on printed page 45.

| Dimension in Plate 45 | Exact inch conversion |
|---|---:|
| Crankshaft to water-pump axis: 6¾ in | 171.45 mm |
| Higher oil connection: 10 45/64 in | 271.859375 mm below crankshaft |
| Lower oil connection: 12 5/64 in | 306.784375 mm below crankshaft |
| Oil-axis to either connection end: 5⅛ in | 130.175 mm |

The [source record](source_constraints.json) preserves literal values,
locators, image hashes, pixel picks, separate horizontal/vertical calibration,
and independent dimensions. The camshaft-height check **fails** the local
pump-region scale; this is evidence against applying one accurate metric scale
to the whole drawing. HB58 Plate40 and SNL Plate14 are qualitative crosschecks,
not additional independent dimensioned drawings.

[Annotated Plate45](hb45_constraints.png) suggests a **168.9 mm flange diameter**
(pixel-only interval 161.4–176.7 mm) and **144.1 mm body diameter**
(137.0–151.5 mm), compared with the old study's 212/188 mm. These are measured
drawing envelopes, not printed manufacturing dimensions. Drawing/projection
errors and configuration transfer add uncertainty beyond the ±3-pixel bounds.

Provisionally associating the higher connection with return and the lower with
supply gives mount-plane estimates **−262.859375 / −262.784375 mm** from the
current local ports, agreeing within **0.075 mm**. This does not make the mount
plane a printed dimension. External fitting identity/orientation remains open.

## Coupled layout and floor registration

The [actual-solid diagnostic](coupled_layout_checks.json) uses the rebuilt
171.45 mm lower drive, raises the water pump 12.55 mm, and places the unchanged
146-part oil pump at the return-derived level. **All 20 bounding-box candidate
pairs between the oil pump and 94 water-pump/lower-drive occurrences are clear.**
Ten oil-pump/case pairs still collide with the obsolete receiver. This does not
check the revised lower drive against every case/hull component or qualify the
existing water-pump mounting pads.

At the inherited engine elevation, the full oil-pump envelope remains
**43.3759 mm below the floor top**. The separately documented
[SNL2 picks](snl2_registration.png) place the engine axis at 906.5312 mm if
the illustrated crankshaft-to-floor distance is registered to the modeled floor
top. That is 57.2977 mm above the inherited datum and leaves **13.9218 mm**
below the pump. The ±3-pixel picks alone contribute a **±35.57 mm** bound to
that height difference, so nominal clearance is not a historically qualified fit.

Both [inherited-datum](layout_inherited_drivetrain.png) and
[floor-relative hypothesis](layout_floor_referenced_SNL2_hypothesis.png)
sections were inspected. The display floor moves in a common engine frame;
no physical floor or engine in the source documents is moved. An adopted datum
change must propagate through engine supports, clutch, transmission, control
linkages and output chains. No arbitrary floor opening or rigid pump-only raise
has been accepted.

The selected `oil_profile_joint_trial/layout` diagnostic repeats the actual-solid
check with the smaller pump. **All 17 nearby pump/drive pairs are clear**;
five pairs still intersect the obsolete receiver (three strainer components and
two mounting studs). The inherited-datum floor envelope gap is **−43.8759 mm**;
the SNL2 floor-relative hypothesis gives **+13.4218 mm**, still subject to the
same ±35.57 mm pick bound. Both new section views were inspected. Source natives
are hash-preserved, and receiving material, stud seating and full installation
remain unqualified.

## Geometry trials and retained failures

`lower_drive_trial` regenerates the complete 17-part lower-drive unit with the
printed axis drop. **37 component checks pass** in the saved 2,170-occurrence
native, preserving the 2,153-component parent. Its 68 material pairs include
three expected clashes with the pre-receiver crankcase. All **27 strict STEP
comparisons pass**. It is not a qualified installation.

`oil_radial_trial` changes 29 estimated controls to follow the smaller casing
envelopes, retaining 146 occurrences and 40 definitions. It passes 397 of 402
native checks, but is **rejected**: 3 of 471 material pairs clash (idler/case,
idler/relief cage, cage/wire), three nut-access web checks fail, and one mounting
wall witness fails. Seven rendered views are retained; isometric, cutaway and
mounting plan were directly inspected. The smaller silhouette is encouraging
but does not override failed material checks.

`oil_radial_clearance_trial` moves the relief unit to estimated `(23,−12)` mm,
away from the idler and to allow a wire approach outside the cage. It builds,
but is only an intermediate diagnostic: it does not address the gallery webs.

`oil_radial_passage_trial` additionally moves the front-sump transverse route
to Y=19 mm and separates the pressure/return routes from nut-access and mounting
wall regions. Only the front-route Y coordinate needed a new optional generator
control. [Compatibility evidence](legacy_route_compatibility.json) verifies that
its default retains the prior saved route exactly; this is not a full baseline
rebuild. Independent checks of the revised candidate remain necessary.

`oil_profile_trial` reduces the lower body to 61 mm depth and increases the
bottom dish to 20 mm. It passes all seven source-envelope checks and all 482
material pairs, but only **401 of 402 native checks**: a continuous wall witness
above the cover-bolt heads loses 21.4968 mm³ into the supply passage. It is
rejected despite the improved silhouette.

`oil_profile_joint_trial` resolves that conflict without altering the printed
12.7 mm cover-joint span. The [constraint calculation](profile_joint_constraint.json)
requires at least 63.46875 mm chamber depth for 1 mm separation; selecting
63.5 mm gives 1.03125 mm. A 16 mm dish keeps the body, rim and drain within the
unchanged [source-depth intervals](oil_vertical_profile_sources.json).
The actual saved body/flange diameters are 144/169 mm. All **402 native checks
and 482 material pairs pass**. The seven envelope checks pass and reject the
previous oversized candidate in all seven comparisons. These checks use the
conditional proposed engine pose; they do not establish installation.

All seven review views and the
[before/after source overlay](oil_profile_joint_trial/source_review/hb45_overlay.png)
were directly inspected. The overlay projects actual saved native shapes onto
HB45 with the retained local scales; it is a conditional source-fit view, not
an independent registration proof. Two progression images bring the total to
147, preserving all 145 earlier images, 20 standard natives and four prior
subsystem natives. The selected candidate has 181 controls; the newly applied
HB45 evidence is bound through this study's supplements, rather than claimed
as newly embedded entries in the builder's original source catalogue.

Two original STEP-check processes terminated without a reported geometric
failure. Their terminal handles and diagnostic output are retained under
`lower_drive_trial/diagnostics`. The checker now copies all 27 required saved
shapes/poses, closes the full document, and releases its unrelated occurrences
before exchange comparison; its numerical/material criteria are unchanged.
The retry finished with all 27 comparisons passing. The retained
[equivalence record](lower_drive_trial/checker_memory_revision.json) confirms
an identical acceptance predicate and identical results for all ten comparisons
completed by the original process. Heavy full-document checks should be
serialized: one observed exchange worker used approximately 10.2 GiB RSS even
after this change. The cause of the earlier terminations is not established.

## Reproduce the selected candidate

Run from the repository root:

```sh
python3 cad/003_FullTank/experiments/drive_chains/engine_oil_pump_build.py --controls cad/003_FullTank/experiments/drive_chains/engine_pump_layout_study/oil_profile_joint_controls.json --output .work/oil-profile-rebuild
python3 cad/003_FullTank/experiments/drive_chains/check_engine_oil_pump.py --candidate .work/oil-profile-rebuild
python3 cad/003_FullTank/experiments/drive_chains/check_engine_oil_pump_exchange.py --candidate .work/oil-profile-rebuild
```

Frozen copies and hashes are in `oil_profile_joint_trial/frozen_inputs`; use
the repository's shared libraries and original entry points. The selected
controls must be supplied explicitly; the canonical default still reproduces
the earlier mounting geometry. Headless source-envelope and overlay scripts
require absolute candidate paths because the launcher changes working directory.

## Next integration work

1. Strict exchange is complete, including fresh checks for changed screens.
   Finish the saved coupled-hierarchy verification; preserve rejected trials.
2. Refine remaining vertical/cast profiles and unequal oil passages from the
   section drawings; the current lower cover/dish and broad filter ceiling remain
   estimates. Resolve the two remaining lock wires and external fittings.
3. The subsequent coupled receiver study supplies a locally qualified case,
   including pads, studs, oil sockets and coupling checks. Complete the upstream
   oil circuit and outstanding installation/service-access qualification.
4. Resolve global engine/drivetrain registration and all downstream interfaces,
   then qualify against the complete standard tank and integrate. Continue
   remaining engine/tank systems; standard geometry still precedes poses.
