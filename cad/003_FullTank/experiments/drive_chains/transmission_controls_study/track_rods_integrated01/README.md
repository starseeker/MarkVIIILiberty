# Installed straight rear track-brake connections

[PowertrainWithRearTrackRods.FCStd](PowertrainWithRearTrackRods.FCStd) is the current
full development native: **3,264 physical occurrences, 568 shared definitions
and 359 assembly groups**. Two SH946D rods use one definition and are linked under
the existing port and starboard `TrackShortConnection` groups. Both are
296.0460545 mm long with 20.6375 mm nominal insertion at each end.

The [prototype dossier](../track_rods02/README.md) records why previously estimated
receiver geometry changed. Straight rods shown in the source could not join the
old eye centers using their perpendicular pin axes. The shared M330 lower arm
was shortened to raise all four distal eyes by14.5220588 mm; its pivot/swivel
bearing faces and upper hardware placements remain. The shared M4132 short arm
was shortened from76.2 to64.8209311 mm while preserving the full long arm and
journal bearing. Both installed M4132 angles change1.85°. These are documented
reconstruction approximations, not newly discovered source dimensions.

A first trial used larger lever rotations. It closed the rods but collided with
the adjacent low-speed levers and the fork throats. Its native, images and failed
context checks are retained. The final nominal and insertion variant each pass
90 native/interface checks,156 whole-material comparisons and31 strict STEP
comparisons. Rods, forks and real eyes are coaxial; full nut passages and minimum
engagement are checked, with displaced and withdrawn rod negatives.

The full integration passes48 checks. All3,262 inherited occurrence identities
and owners remain; only18 declared occurrence frames change. Two shared receiver
definitions change, and all565 other definitions are preserved:
545 exact BReps and20 strict material comparisons.
Sixteen completed comparisons were reused for identical ordered BRep hashes and
unchanged worker code. Seven prototype definitions and24 installed shapes
transfer strictly; a full integrated STEP export was not repeated.

A fresh full rebuild reproduces1,736 stored BReps,
156,588 persistent properties,3,264 occurrence
records and359 assembly records. All native links reopen after relocation.
The one topology-naming metadata change on the deliberately rebuilt M330 tip is
explained in [the retained checker diagnostic](diagnostics/shape_serialization/README.md).
No shape or tolerance was changed to satisfy that metadata check.

The [operating interfaces](operating_interfaces.json) bind eight remeasured eyes
to this new native: four M330 distal eyes and both eyes of each M4132. Their old
coordinate values are superseded; remaining inherited interfaces are unchanged.
The M4132 long-arm shape is preserved but its eye moves with the declared small
rotation. Future long-rod work must use the new coordinates.

The inspected [isometric](track_rods_isometric.png), [connection detail](track_rod_detail.png),
[top view](track_rods_plan.png) and [source comparison](source_detail.png) bring
visual progression to **245 images**, preserving all241 earlier views. All five
integrated image files match the inspected prototype byte for byte. The SNL6
camera remains fixed; inherited lever silhouettes, positions and spring-height
disagreement remain visible. These selected subsystem views do not replace the
whole-tank standard render. Standard `tank011` remains unchanged.

The solid19.05 mm rod section is provisional. HB calls the corresponding M577 a
tube, while SNL identifies SH946D as a rod; internal section needs better evidence.
Threads use nominal cylindrical envelopes. No full motion, strength or service
claim is made. Low-speed M568A/receiver-diameter reconciliation and SH946E joints
are next, followed by M567 washers, M564 springs, M575 and longer rear rods,
center/front controls and remaining interiors. Standard geometry remains the
priority before pose variants.

Recovery:

```sh
python3 cad/003_FullTank/experiments/drive_chains/verify_rear_track_rod_checkpoint.py
python3 tools/cad_pipeline/decisions.py cad/003_FullTank/decision_ledger.json
```

Regenerate with `build_rear_track_rods.py --output <new absolute directory>`
through the headless launcher after prototype checks are current. Extract, run
`check_rear_track_rod_installation.py`, seed exact prior results with
`seed_rear_track_rod_preservation.py`, then run `check_rear_track_rod_preservation.py`.
Use `check_powertrain_frame_reproduction.py` for the independent full rebuild.
The checked native is self-contained; identical extracted BReps use relative
links to earlier analysis artifacts to reduce disk usage.
