# Complete operating handles and pivot joints

[Native assembly](PowertrainControlRebuild.FCStd): **3,582 physical occurrences /
635 definitions / 442 assembly groups**. Ten additions represent two M738 handles,
M746/M747 fulcrums and complete M776/M768/cotter joints. Four upper selector
arms/jaws are revised for actual handle engagement; every inherited world frame
and all protected lower linkage material remain fixed.

Nominal and 13 mm handle stock each pass **419 local checks, 53 context pairs
without exemptions and 25 strict native/STEP comparisons**. Full integration
passes 206 checks. All 624 undeclared inherited definitions are preserved
(607 exact BReps and 17 strict material comparisons). Fresh full rebuilding
reproduces 1937 archive BReps and 175,953 persistent properties.
[Qualification](qualification.json) binds 1263 dependencies.

Six inspected views bring progression to **308 images**: [isometric](isometric.png),
[driver detail](driver_detail.png), [pivot section](operating_joint.png),
[high-control section](high_section.png), [source plan](source_plan.png), and
[source side](source_side.png). Display sections cut only review copies.

The specific source M776 assembly uses a **3/16 x 1-inch cotter**, selected over
its conflicting generic 1-1/2-inch entry. Actual saved leg centerlines retain
25.4 mm, and displaced checks confirm retention and crown-nut locking. M768
retains the printed 7/8-inch nominal thread and 1/2-inch thickness. Nominal threads,
bolt stock, cast/forged profiles, pin eye form and all unprinted dimensions remain
estimates. See [trial record](../operating_trials.md).

**Source placement remains unqualified.** Grip-tip residuals are 47.16/48.59 px
in plan and 49.41 px in side, beyond the 5 px pick allowance. The pivot is 4.92 px
from its side pick. The inherited high-eye discrepancy remains 13.53 px. Neither
source registration is refitted.

The [diagnosis](source_comparison_diagnosis.json) rules out a simple rotation of
the current handle around its current pivot as a complete explanation. Source
views disagree in X by 35–39 mm; literal source-tip transfer lies outside the
current front hull plane. The adopted 37-inch overall radial length datum is
explicitly provisional. A main-shaft-to-tip interpretation, source scale/feature
identities, depicted configuration and absolute driver/hull placement remain
candidates for review. Mechanical fit does not decide this evidence question.

Next reconcile that length/position evidence before attaching trigger and grip
fittings to the current upper blade. Continue the remaining pawls/guides, separate
gates/stops, brake interconnection and foot rods, springs/axial spacing, reverse
controls and complete seat support. No historical-pose, motion or hand-space
qualification is claimed. Standard tank011 remains unchanged.

Recovery:

```sh
python3 cad/003_FullTank/experiments/drive_chains/verify_control_rebuild_checkpoint.py --candidate cad/003_FullTank/experiments/drive_chains/transmission_controls_study/driver_redo01/operating_integrated01
```

Regenerate the prototype using `trial_driver_operating_handles_v2.py`,
`operating_controls02.json` and a new output directory. Use absolute worker and
argument paths with the headless launcher. Local/context/exchange/variation,
fresh rebuilding and visual/source review precede full integration through
`build_driver_operating_handles.py`. The first failed `operating01` is retained.
