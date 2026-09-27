# High selectors and complete short/long connections

[Native assembly](PowertrainControlRebuild.FCStd): **3,572 physical occurrences /
628 definitions / 439 assembly groups**. The 38 additions include M759 port and
M758 starboard selectors, two M789A short rods, two M576 long rods and all eight
complete clevis/pin/cotter/nut sets. Three new definitions are added; every
inherited definition and world frame is preserved.

M789A retains its printed **269.875 mm (10⅝ inch) stock**. The two long M576 rods
reuse the exact existing clutch definition and its complete **1296.850963 mm**
inferred stock. Three of five M576 applications are populated; both foot
applications remain required. The third M789A belongs to the remaining reverse
connection. See [source review](../high_source_review01.json) and
[trial record](../high_trials.md).

The fixed HB113 comparison retains a **13.525126 px discrepancy**, exceeding the
4 px pick allowance. Printed stock and the existing fork interfaces put the
selector eye 43.073828 mm aft and 160.345287 mm below M782. The drawing-based point
would require a longer pin span. [Layout evidence](../high_layout01.json) records
the alternatives and calculation. This is a static reconstruction estimate, not
historical position validation; neither local registration is refitted.

Selector profiles, jaw dimensions, axial stack, shaft separation calibration,
neutral pose and fork insertion remain estimates. The two operating handles and
their actual engagement are unfinished. Keep this source disagreement open while
building those interfaces.

Nominal and 13 mm upper-web variants each pass **432 local checks, 75 context pairs
without exemptions and 41 strict native/STEP comparisons**. Full integration
passes **189 checks**. All **625 inherited definitions** are preserved
(604 exact BReps, 21 strict material comparisons). Fresh full rebuilding
reproduces **1916 BReps and 174,953 persistent properties**.
The [qualification](qualification.json) binds 1169 dependencies.

Five inspected [views](visual_review.json) bring progression to **302 images**:
[isometric](isometric.png), [driver detail](driver_detail.png),
[high-speed section](high_section.png), [source plan](source_plan.png), and
[source side](source_side.png). The first section omitted a receiver from display;
its diagnostic is retained and the final section includes the actual M784 link.
Display cuts do not alter the native solids.

Next reconstruct M746/M747 fulcrums and M738A/M738B operating handles with their
pivot hardware and real selector engagement. Continue triggers, separate control
gates/stops, brake interconnection, spring anchors, axial spacing, reverse
controls and full seat support. Standard tank011 remains unchanged. No motion,
service, hand-clearance or historical-exactness qualification is claimed.

Recovery:

```sh
python3 cad/003_FullTank/experiments/drive_chains/verify_control_rebuild_checkpoint.py --candidate cad/003_FullTank/experiments/drive_chains/transmission_controls_study/driver_redo01/high_integrated01
```

Regenerate with `trial_driver_high_controls.py`, `high_controls01.json` and a new
output directory. Use absolute worker/argument paths with the headless launcher.
`driver_high_control_parts.py` contains the selector generator; parameter changes
require regeneration. Local/context/exchange/variation, reproduction and visual
checks precede `build_driver_high_controls.py` integration.
