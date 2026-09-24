# Rear control channel — four M4130 mounting sets

[PowertrainWithRearChannelMounts.FCStd](PowertrainWithRearChannelMounts.FCStd)
contains **3,202 physical occurrences, 551 used definitions and 343 assembly
groups**. It adds 29 occurrences to the preceding powertrain: the M4128 channel,
four M4130 cleats, four bolt/lockwasher/nut sets and twelve rivets. Four floor
holes revise the existing receiver in place. The nuts share the existing classic
U.S. Standard definition. Standard tank011 remains unchanged.

The [qualification](qualification.json) covers this local mounting increment.
The complete channel, operating controls and full tank remain unfinished.
Source dimensions, inference and unresolved alternatives are recorded in
[the mounting review](../channel_mount_source_review01.json),
[nominal controls](../channel_mount_controls02.json) and
[visual review](../channel_mount02/visual_review.json).

## Geometry and evidence

The downward-open channel retains the preceding estimated 152.4 × 50.8 mm section,
6.35 mm stock and 2,200 mm span at world [2400, 0, 533.05] mm. Four triangular
cleats, nominally 9.525 mm thick, attach to its rear flange at Y = −710, −450,
450 and 710 mm. Their same-hand orientation, profile and stations are estimates.
HB104 supports a triangular foot, vertical floor bolt and three upright heads;
its perspective photograph does not establish exact proportions or piece mark.

SNL quantities give four M4130 cleats and twelve ½ × 2 inch rivets. The handbook's
two-cleat count remains a source difference. The rivets preserve the interpreted
unformed stock volume with an explicitly larger upset head; the stock-length
datum, cleat thickness and unseen head form remain open. Source ¾ × 2 inch floor
bolts have nominal thread cylinders, separate compressed lock washers and nuts.
No mechanical strength, torque or riveting-process qualification is claimed.

The first layout in `channel_mount01` and `channel_mount_variation01` collided
with each nearest rivet head by 33.294 and 60.295 mm³ respectively. Those failures
are preserved. The revised estimated foot is 88.9 mm deep, with its bolt shifted
to local [−44.45, −31.75] mm. Both variants have full head bearing and clear a
conditional 25 mm radius, 60 mm high socket envelope. This is a local access
allowance, not a complete removal sequence.

## Checks and reproducibility

| Scope | Result |
| --- | --- |
| Nominal and +0.5 mm cleat stock | 75 native/interface checks, 57 material pairs each |
| Surrounding development and retained standard solids | All 29 additions and four socket envelopes screened; three actual candidate pairs per variant pass |
| Prototype STEP | Seven definitions and 30 installed shapes per variant pass all 37 strict comparisons |
| Integrated native | 50 checks; all 3,202 links reopen after relocation; seven definitions and 30 installed shapes match the tested prototype |
| Inherited material | 545 unchanged definitions: 528 identical BRep hashes and 17 strict comparisons; revised floor checked separately |
| Fresh prototype generation | All shapes, frames and stable properties agree; only seven generated assembly UUIDs differ |
| Fresh integration | All 1,685 archive BReps, frames, object types and 152,474 persistent properties agree |

Ten previously completed strict comparisons were reused only after matching both
ordered BRep hashes and the worker hash. Duplicate extracted shapes use relative
links to the durable parent; the native document is self-contained. The floor
feature now stores the revised canonical shape at identity placement; its body's
installed frame and inherited source metadata remain intact.

Read-only recovery, without rebuilding CAD:

```sh
python3 cad/003_FullTank/experiments/drive_chains/verify_rear_control_mount_checkpoint.py
```

The producer is `build_rear_control_channel_mount.py`; start a new output directory
with `--output`. The isolated builder is `trial_rear_control_channel_mount.py`
with `--controls` and `--output`. Use the FreeCAD headless launcher and absolute
arguments. Frozen builders/checkers and exact input hashes accompany the artifacts.
Parameter changes require regeneration.

## Source view and next increment

The [installed isometric](channel_installed_isometric.png) shows the local mounting
and nearby clutch/engine-frame context, with the floor in outline. The
[detail](../channel_mount02/cleat_mount_detail.png) uses labeled display sections.
The [source overlay](../channel_mount02/source_detail.png) reuses the same local
SNL6 registration. It is not a photographic calibration, cannot establish
transverse spacing, and retains the 21.867 px high-speed control-bore disagreement.
No camera was refitted. Three new progression images preserve these views.

Next determine the two M4129 attachments, four M4131 fulcrums and M4135/M4136 spring
brackets, then construct M575 and the other rear control routes. No M4129 rivet
application has been identified; do not invent extra rivets. The channel is only
about 0.57 mm below the current left clutch-support lower envelope, so subsequent
upper brackets require actual-surface checks. M581 lever identity, the handbook's
fulcrum quantity and M4131/M1431 center identity remain unresolved. Add useful new
source landmarks as holdouts before considering a versioned camera revision.
