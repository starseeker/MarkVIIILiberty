# Driver support foundation — 27 September 2026

[Native assembly](PowertrainControlRebuild.FCStd): **3,475 occurrences / 611 definitions / 414 groups**.
The completed withheld-control redo is the unchanged parent. This increment adds
36 driver components and imports two existing standard floor panels with their
new receiving holes. Standard tank011 is not modified.

The driver foundation contains M782 and M783, their separate M313/M314 nuts and
source-length split pins, partial M786/M787 seat-support plates, and eight complete
½ × 1¼-inch bolt/plain-nut/lock-washer sets. Shafts bear in actual side-plate bores;
shoulders and nut seats capture plate stock; feet and hardware bear on floor1/2.
Only the eight declared receiving bores change those two floors.

Nominal and 6.35 → 6.85 mm plate-stock variants each pass **144 local checks,
123 context pairs without exemptions, and 47 strict native/STEP comparisons**.
All 602 inherited definitions, placements, groups and persistent properties are
preserved except declared new members and checkpoint descriptions. Fresh full
reproduction matches 1,865 archive BReps and 169,337 persistent properties.
[Qualification](qualification.json) binds the saved evidence and limitations.

[Isometric](isometric.png), [plan](plan.png), [mount section](mount_section.png)
and [source overlay](source_plan.png) were visually inspected. The section only
clips the displayed view. The saved parts remain complete.

## Interpretation and remaining work

- M746/M747 belong to the operating-lever mechanism. They are **not** the floor
  blocks suggested in the earlier uninstalled shaft study. M786/M787 are the
  source-counted seat-support plates; their exact full profile is still unknown.
- The local SNL6 plan registration estimates 406.53 mm shaft separation. Its
  shaft endpoints are construction picks, not independent validation points.
  Endpoint ambiguity and schematic distortion leave approximately 20–35 mm
  uncertainty. No fit spans the broken long rods.
- Source-sized M782 is 628.65 mm long and 38.0238 mm in central diameter. M783
  length/diameter, reduced ends, plate shape/stock, shaft elevations and floor
  mounting pattern are estimates. Seat attachments/extensions remain absent.
- The old [7280,0,1020] shaft-study origin is superseded. Actual shaft coordinates
  are in [the report](report.json). The new station still depends on an unmodeled
  driver low receiver and must be confirmed or reopened when actual links and
  source-length front rods close. No virtual receiver or rod is counted.
- The main shaft's short keeper lies beyond the M313 front face; castle-slot
  engagement is not claimed. The rear keeper engages the reused M314 slot.
  Historical shaft-end details and real threads remain unresolved.
- Rejected mount01 had reversed M314 nut seats. Mount02 corrected the seats but
  its axially spread keeper eyes/tails touched the nut base. Mount03 orients the
  full source-sized keeper in the shaft-normal plane. Rejected evidence remains.

Next: map the actual M784 swing links and M760 suspension receivers, then the
M789A/B short rods and control-lever interfaces. Preserve source stock lengths
and reopen provisional support placement if those interfaces require it.
Complete seat supports, spring anchors, selectors, brake interconnection and all
front rods remain required. This is a local static approximation, not a complete
driver assembly, motion validation or finished tank.

## Recovery

```sh
python3 cad/003_FullTank/experiments/drive_chains/verify_control_rebuild_checkpoint.py --candidate cad/003_FullTank/experiments/drive_chains/transmission_controls_study/driver_redo01/mount_integrated01
```

Build new output directories with `trial_driver_control_mounts_v3.py`,
`mount_controls03.json` / `mount_variation03.json`, then extract with
`pump_integration_worker.py`. Run `check_driver_control_mounts.py`,
`check_control_rebuild_context.py`, `exchange_control_rebuild_clutch_swing.py`,
and fresh reproduction; inspect `render_driver_control_mounts_v2.py` outputs.
The full installer is `build_driver_control_mounts.py`; its strict transfer and
preservation checks precede `qualify_driver_control_mounts.py`. Use the established
FreeCAD launcher with absolute worker and argument paths.
