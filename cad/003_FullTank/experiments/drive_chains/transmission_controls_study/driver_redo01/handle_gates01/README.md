# Conditional operating-handle gate study

The [native pilot](ControlRebuildTrial.FCStd) revises only the four upper selector
jaws, preserving every journal, lower connection, rod and occurrence frame.
It contains 140 contextual occurrences and **no new tank parts**. This is a
conditional interface study, awaiting the complete operating handles and pivots;
it is not integrated into the full development assembly.

The preceding empty-pocket checks did not test a through-going radial handle.
Saved material in the old jaws intersects each 12.7 mm square diagnostic stem
by **4,096.766000 mm³**. The proposed jaws provide radial passages between tangential
drive walls. Each diagnostic stem clears the revised material and seats against
either drive face over **406.4 mm²**. Lifted and over-displaced controls distinguish
contact, separation and interference. These witness tools are not actual handles.
See the [old/proposed diagnostic](gate_interface.png).

The radial/tangential envelope is changed from 70/32 to 32/70 mm, around the
retained estimated high/low radial centers of 175/250 mm. Lip thickness is
12.7 mm nominal and 13 mm in the independent variant. Axial reaches are retained.
All these upper-jaw dimensions remain estimates. A complete handle must establish
which selector it engages and how it clears the other selector, the shaft and hull.
Do not distort a handle merely to preserve these provisional jaw dimensions.

Both nominal and wall variant pass **252 saved-material checks, 20 interference
pairs without exemptions and eight strict native/STEP comparisons**. A fresh
nominal rebuild reproduces 105 archive BReps and 8,195 persistent properties.
Six views were inspected. The initial diagnostic viewed the backs of the jaws;
its renderer/image/receipt are preserved under `../handle_gate_diagnostics01`.
Neither source registration changed; the high-eye discrepancy remains 13.53 px.

The [source review](../handle_source_review01.json) also establishes the next
interfaces. HB113 places M746/M747 fulcrums inboard of the selector collars.
M738B is the port operating handle; M738A is starboard. HB148 prints 37 inches
for their length, without specifying pivot-to-tip or developed-centerline datums.
M776 is their separate pivot bolt. The original SNL23 lists an M768 7/8-inch
special nut and a 3/16 x 1-inch cotter in each M776 assembly. SNL129 gives the
crown nut a 1/2-inch thickness. The generic SNL141 1-1/2-inch cotter row also
names M776. Preserve this conflict and verify actual full pin reach, slot/eye
clearance and nut seating; do not silently lengthen the pin to fit an estimated nut.

Next reconstruct complete fulcrums, handles and pivot joints using this pilot as
an interface hypothesis. Their real geometry and the source views must confirm
or revise the jaws before integration. The current full assembly remains
[high_integrated01](../high_integrated01/README.md): 3,572 occurrences, 628
definitions and 439 groups, with 302 progression images. Standard tank011 remains
unchanged. Historical form, complete engagement and motion are unqualified.

Recovery:

```sh
python3 cad/003_FullTank/experiments/drive_chains/verify_driver_handle_gate_study.py
```

Regenerate with `trial_driver_handle_gates.py`, `handle_gate_controls01.json` and
a new output directory. Extract through `pump_integration_worker.py`; run
`check_driver_handle_gates.py`, `check_control_rebuild_context.py` and
`exchange_control_rebuild_clutch_swing.py`. Use absolute worker/argument paths
with the headless launcher. `study_receipt.json` binds the parent and pilot evidence.
