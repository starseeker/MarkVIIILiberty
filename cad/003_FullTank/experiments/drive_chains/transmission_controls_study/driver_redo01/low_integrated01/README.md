# Low-speed front receivers and complete rods

[Native assembly](PowertrainControlRebuild.FCStd): **3,528 physical occurrences /
622 definitions / 426 assembly groups**. Thirty new parts include two each
M760/M762/M763, complete M761 pins and source-sized keepers, SH220A washers, and
two complete M574 rods with all four clevis/pin/cotter/nut sets.

The M762 front eyes remain open for the actual selector connections. This is a
checked receiving linkage and rod increment, not completed operator controls.

Source review separates the overlapping M784 and M763 eyes that were partly
conflated in the preceding clutch reconstruction. See the
[reviewed local picks](../low_source_landmarks01.json). The fixed source
registration is unchanged. Seven driver/support/floor/clutch definitions and 59
occurrence frames are explicitly revised; rear and intermediate controls stay
fixed. All 608 undeclared inherited definitions are preserved.

M574 retains its printed 1257.3 mm stock, and M789B retains 320.675 mm. The revised
clutch M576 is a complete 1296.850963 mm inferred rod; its other four applications
still require family reconciliation. M772 retains 723.9 mm radial hand reach and
127 mm bell reach. The real M763 receivers now determine the driver station through
complete M574 closure, replacing the former hypothetical front points.

Main/swing shaft centers are X7579.893408/Z1300 and X7173.363024/Z1320 mm.
The selected 136-degree projected clutch arm angle gives 47.3938-degree hand
elevation, 11.4125 mm nominal nose clearance and 10.1281 px plan-tip discrepancy.
Source picks are construction evidence, not independent validation. Absolute
height, seat support, historical pose, link sections and knee stack remain
explicit estimates. Floor panels are rebuilt from originals before drilling the
new mounting pattern; stale holes are absent.

Nominal and 13 mm suspension-web variants each pass **366 local checks, 227 context
pairs without exemptions and 105 native/STEP comparisons**. Fresh full rebuilding
reproduces 1898 archived BReps and
172426 persistent properties. The
[qualification](qualification.json) binds 1169 dependencies.
[Retained diagnostics](../low_trials.md) include the rejected lateral set and the
corrected journal-area checker, which now accounts for the real oil opening.

Five inspected [views](visual_review.json) bring progression to 292:
[isometric](isometric.png), [detail](driver_detail.png),
[low-speed section](low_section.png), [source plan](source_plan.png), and
[source side](source_side.png). Section/display cuts do not alter the native.

Next resolve M756/M757 low selectors and the actual M762 front coupling. Handbook
and SNL handed names conflict; choose and record the catalogue-era convention.
Then continue high-speed selectors, operating levers, M789A short rods, brake
interconnection, M775 spacers, spring anchors, reverse pipe/lever and full seat
supports. Standard tank011 is unchanged; static checks do not qualify motion,
hand space, service access or historical exactness.

Recovery:

```sh
python3 cad/003_FullTank/experiments/drive_chains/verify_control_rebuild_checkpoint.py --candidate cad/003_FullTank/experiments/drive_chains/transmission_controls_study/driver_redo01/low_integrated01
```

Regenerate using `trial_driver_low_controls_v2.py` with `../low_controls02.json`
and a new output directory. Parts are in `driver_low_control_parts_v2.py`, with
retained driver helpers. The source-bound parameter variation, saved-material,
context, exchange, reproduction and visual checks precede full integration with
`build_driver_low_controls.py`. Use absolute worker/argument paths with the
headless launcher. Qualified files and earlier rejected trials stay unchanged.
