# Low-speed selectors and complete upper connections

[Native assembly](PowertrainControlRebuild.FCStd): **3,534 physical occurrences /
625 definitions / 428 assembly groups**. Six additions comprise the two handed
M756/M757 selectors and two complete M790 pin/cotter sets. Only the shared M762
definition is revised; all inherited world frames stay fixed.

The [source review](../selector_source_review01.json) corrects the preceding
provisional curved M762: the bowed lower outline is M765 foot-brake bridle.
M762 instead runs diagonally from the upper M790 joint to the retained M761 knee.
See the [source close-up](../selector_source_views01/hb113_joint_detail.png) and
[construction pick](../selector_landmarks01.json). The local drawing registration
is unchanged. SNL names M756 left and M757 right; HB190 reverses those labels.
The model explicitly follows the SNL convention.

Both M574 rods retain their complete printed 49½-inch stock. Shaft stations,
low-speed rear knee assemblies, SH220A washers and clutch geometry are preserved.
The new M790 cotters retain 3/16 × 1¼-inch source stock. Selector profiles, gate
opening, pin dimensions and axial stack remain estimates. The upper joint is
chosen 90 mm aft and 92 mm above M782 from the fixed drawing registration; this
construction consistency does not independently validate the historical shape.

Nominal and 13 mm upper-web variants each pass **307 saved-solid checks, 21
context pairs without mating exemptions, and 12 strict native/STEP comparisons**.
Full integration passes 146 checks. All **621 undeclared inherited definitions**
are preserved (593 exact BReps and 28 strict material comparisons).
Fresh full rebuilding reproduces **1907 BReps and 172,949 persistent properties**.
The [qualification](qualification.json) binds 1155 dependencies.
[Trial dispositions](../selector_trials.md) retain the implementation diagnostics.

Five inspected [views](visual_review.json) bring progression to **297 images**:
[isometric](isometric.png), [driver detail](driver_detail.png),
[low-speed section](low_section.png), [source plan](source_plan.png), and
[source side](source_side.png). Section/display cuts do not change the native.
HB93 supports the short side-opening jaws qualitatively; no metric perspective
fit is claimed for that incomplete pictorial assembly.

Next build the high-speed selectors and their source-length M789A connections.
SNL194 lists three M789A assemblies, so the reverse short connection also remains.
Reconcile the five M576 long-rod applications as their real receivers are built.
Operating handles/fulcrums, separate control gates/stops, brake interconnection,
spring anchors, axial spacing, reverse controls and full seat support remain open.
Standard tank011 is unchanged. This static reconstruction does not qualify motion,
service access, hand clearance or exact historical geometry.

Recovery:

```sh
python3 cad/003_FullTank/experiments/drive_chains/verify_control_rebuild_checkpoint.py --candidate cad/003_FullTank/experiments/drive_chains/transmission_controls_study/driver_redo01/selector_integrated01
```

Regenerate with `trial_driver_low_selectors.py`, `selector_controls01.json` and a
new output directory. Use absolute worker/argument paths with the headless
launcher. `driver_low_selector_parts.py` contains the parameterized definitions;
parameter changes require regeneration. Local/context/exchange/variation,
reproduction and visual checks precede `build_driver_low_selectors.py` integration.
