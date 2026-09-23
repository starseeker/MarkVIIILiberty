# P01 — Water-pump fluid-passage correction

Historical checkpoint `e819833`; current regeneration and source decisions are in the [connection and wire revision](P01-engine-water-pump-connections.md).

This follows the [mounting checkpoint](P01-engine-water-pump-mounting.md).
The development assembly still has 2,246 physical occurrences, including 76
pump constituents in 28 definitions. No new physical parts are introduced.

## Problem and correction

The six-control trial at the preceding checkpoint failed the unchanged 5 mm
outlet passage gauge after the outlet and mounting angles changed from 22.5°
to 24°. The drain boss was joined after the fluid cavity had been removed,
putting material back inside the intended outlet and adjoining annular chamber.
The nominal casting also had an intrusion there, outside its smaller passage
gauge. This was a modeling dependency error within the estimated casting.

The builder now removes the existing fluid cavity from the additional drain
stock before joining that stock to the body. It preserves the flat drain seat
and leaves the blind cover-stud supports intact. Recutting the whole assembled
body would remove required support material and is not used.

A focused comparison reproduces the old trial's approximately 1.806 mm³
intersection with the 5 mm-radius gauge. The corrected nominal and trial
castings have zero intersection with both centerline gauges and with the
intended fluid volume inside the drain-stock region. No material is added;
all removed material lies within that region's intended fluid volume.
The old nominal and trial shapes provide failing controls for the stronger
fluid-volume check. Neither the gauge nor numerical tolerances were relaxed.

## Verification

The saved [native assembly](../experiments/drive_chains/engine_water_pump_passage_study/DrivetrainWithWaterPump.FCStd)
passes all 39 native checks and 472 affected material comparisons,
including standard tank context, nine gear-mesh samples and eight rotor angles.
All 106 STEP comparisons pass, covering definitions, installed pump parts and
the case in both coordinate frames. The same six-control trial passes all 39
native checks, 473 context pairs and all 106 STEP comparisons.

Compared with the mounting checkpoint, only the pump-body definition and its
feature BRep change; 846 other serialized shapes and 45,133 checked placement,
hierarchy and identity properties match. A fresh nominal rebuild reproduces all
848 serialized shapes and those 45,133 properties. The focused frozen-input
diagnostic also replays successfully.

Five native views and the local before/after drain sections were inspected.
All 137 progression images and 20 standard native documents retain their hashes.
This small internal correction does not add a full-tank visual milestone.
See [diagnostics](../experiments/drive_chains/engine_water_pump_passage_study/diagnostics/passage/README.md)
and the [parameter trial](../experiments/drive_chains/engine_water_pump_passage_study/diagnostics/parameter_trial/README.md).

Regenerate with `python3 cad/003_FullTank/experiments/drive_chains/engine_water_pump_build.py`;
at this historical checkpoint the builder default was `engine_water_pump_passage_study`,
preserving the previous mounting checkpoint. The same 133 controls, 82 source
records, nine source pages and five builder assets remain in use.

## Evidence and remaining scope

The cavity, clocking, drain projection and casting profiles remain estimates.
LIB figure79 supports the arrangement of the shaft, packing, impeller, outlets
and drain but does not supply measured profiles for this correction. The source
cameras remain unregistered. A clear passage proves a geometric property, not
historical dimensional accuracy or hydraulic performance.

The drain lock wire is still absent. Packing quantity/stock length, adjustment
layer terminology, sealing-layer placement and inlet/cover identity conflicts
remain documented in the earlier pump packet. Oil-pump and other engine parts,
combined qualification and standard integration remain outstanding. The user
priority remains populated standard geometry and interiors before poses.
