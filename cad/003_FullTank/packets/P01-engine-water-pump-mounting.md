# P01 — Water-pump mounting and casting revision

This extends the [water-pump development checkpoint](P01-engine-water-pump.md).
The new development assembly has 2,246 physical occurrences: 76 pump constituents
in 28 definitions, one revised lower crankcase and 2,169 preserved parent parts.
It remains separate from the standard tank assembly.

## Source constraints and selected approximation

The original SNL239 scan confirms four LQ197A/140 mounting studs, each with an
LQ198A/103 special nut, LQ166A/113 special washer and a 3/32 × 5/8 inch cotter.
The studs are 3/8 × 1-31/32 inch, with 21/32 inch US Standard and 5/8 inch SAE
threaded ends. The model retains those stock lengths as smooth thread envelopes.
Fully embedding the case thread is an installation assumption. It leaves
33.3375 mm projecting, with the outer thread starting 17.4625 mm from the case.

The estimated clamped stack is a 0.25 mm shim, 5 mm retainer flange, 0.4 mm
sealing layer and 14 mm body flange. The washer is 1.5875 mm thick and the nut
9.525 mm long. Thus the nut spans 21.2375–30.7625 mm from the case face,
inside the printed outer thread; 2.575 mm of stud remains beyond it. These
calculated decimals do not imply corresponding historical precision. Flange,
nut, washer and casting dimensions are explicitly estimated.

The survey transcription of SNL273:017 lists a 5/8 inch nominal size for the
same LQ166A washer, whereas the explicit pump assembly row SNL239:020 specifies
3/8 inch. This model selects the pump-specific row and retains that discrepancy
in a supplemental evidence record; the frozen survey is unchanged.

The 84 mm mounting pitch radius, 74 mm flange radius and 12 mm ears place the
hardware beyond the estimated chamber bulge. Added integral case pads contain
four blind receiving holes, with circumferential support and bottom walls.
Canonical case regeneration metadata now points to this combined reconstruction
instead of the inherited crankshaft-stage inputs.

Two rejected installation hypotheses are retained. Diagonal ears collided with
the outlet barrels; cardinal ears collided with the drain plug and the lower-drive
retaining screw. Rotating the ears and outlets together by an estimated 22.5°
provides an alternative to test against those constraints. SNL plate14 explicitly
states that its water outlets are transposed; it cannot establish their installed
clocking. The selected angle is unregistered to a measured source view.

## Casting and fluid boundaries

The outlet centerlines now run tangentially from the annular chamber. A 20 mm
outer and 15 mm inner outlet radius makes a small throat transition to the
21/16 mm annular tube radii. These are unprinted reconstruction estimates;
the model is not a measured volute and carries no flow-performance claim.
The earlier crossing-barrel profile is preserved in the preceding checkpoint.

The thicker rear flange is cleared before adding the blind cover-stud bosses,
so those bosses retain their surrounding and bottom material. The drain boss
now extends to a flat local-Z −85 mm gasket seat, below the clocked outlet
casting. The source nominal 5/8 inch drain plug retains its diameter and thread
envelope; the boss projection is estimated. A full ring of seat material is
checked independently.

The exact matched-radius tangent construction lost connected material and was
rejected. A later candidate with an insufficient drain boss both overlapped the
drain fittings and exceeded the kernel-tolerance limit. The deeper boss addresses
the physical seat, with its numerical behavior traced independently. This is a
physical casting revision, not a material-equivalent tolerance reset. Acceptance
criteria have not been relaxed.

## Verification

The saved [native assembly](../experiments/drive_chains/engine_water_pump_mounting_study/DrivetrainWithWaterPump.FCStd)
passes all 38 independent native checks and 472 material comparisons, including
standard tank context, nine gear-mesh samples, eight complete-rotor rotations,
full nut engagement, receiving material, drain seating and complete parent
preservation outside the declared case revision. The case edit is bounded to
an independently fixed mounting region.

All 106 nominal STEP comparisons pass, including the revised case in both frames.
The six-control trial passes 37 of 38 native checks and all 473 local material
pairs, but fails the unchanged 5 mm-radius passage witness in the negative
outlet. The likely interaction is drain-boss material added after machining the
fluid cavity. The [trial diagnostic](../experiments/drive_chains/engine_water_pump_mounting_study/diagnostics/parameter_trial/README.md)
retains the failure; no trial STEP qualification is claimed. The next correction
must preserve the fluid void while retaining the blind stud bosses. Fresh nominal
reproduction passes: all 848 serialized shapes and 45,133 checked properties match.
This remains a development checkpoint; the coupled trial is not qualified.
Regenerate with `python3 cad/003_FullTank/experiments/drive_chains/engine_water_pump_build.py`;
its default output is now `engine_water_pump_mounting_study`.
The [controls](../experiments/drive_chains/engine_water_pump_controls.json) expose
133 construction/validation inputs, with separate evidence labels. The builder
freezes 82 records, nine source pages and five assets; the washer discrepancy
has a separately hashed supplemental source review.

## Remaining scope

Drain lock wire is still absent. Packing quantity/stock-length conflicts,
LQ151A adjustment-layer terminology, LQ154A placement and the inlet/cover identity
remain recorded in the preceding packet. Commercial bearing internals, cast
profiles and shaft-to-case registration remain estimates. Full service paths,
source-camera registration, complete engine population and standard integration
are not established by the mounting checks. Socket checks cover only an estimated
installed envelope, not tool insertion or swing. Posing work remains deferred.

All five nominal views were inspected against the source arrangement. The final
exploded display keeps the drain plug with the displaced body. Two progression
images bring the total to 137 and preserve all 135 previous snapshots. The source
camera is unregistered; cutaways and display offsets do not alter physical parts.

The [FreeCAD skill](../../../skills/freecad-reconstruction/references/assembly-and-validation.md)
now documents non-null empty Boolean compounds. A contained-box probe confirms
that distinction; its second cut succeeds, whereas the original casing check's
second cut raised an error. The nominal validator explicitly handles empty material.
