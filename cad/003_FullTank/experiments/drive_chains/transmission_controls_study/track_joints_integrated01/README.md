# Installed rear track-brake end joints

[PowertrainWithRearTrackJoints.FCStd](PowertrainWithRearTrackJoints.FCStd) is the
current full development native: **3,262 physical occurrences, 567 shared
part definitions and 359 assembly groups**. Four M569C forks, four M568C pins,
four split pins and four plain nuts add 16 parts. New port and starboard
`TrackShortConnection` groups each own two end-joint groups beneath
`RearControlChannel`. The four nuts reuse `Def_USStdControlNut`; the other
three definitions are shared across all four joints. No inherited receiver
geometry or part placement was changed.

The [prototype dossier](../track_joints02/README.md) separates source quantities
and listed hardware lengths from estimated fork/pin form. The first fork throat
collided with all four lever eyes; the revised estimated throat and socket clear
them while retaining the listed pin length. The failed trial is preserved.
The joints are an intermediate static arrangement: SH946D rod bodies and final
fork angles remain unfinished.

Nominal and thicker-ear prototypes each pass 76 native/interface checks,
28 local material pairs, 30 surrounding pairs and 20 strict STEP comparisons.
The integrated native passes 33 checks covering all inherited frames/owners,
persistent properties, relocated local links and strict transfer of four
definitions and 16 installed shapes. All 564 inherited definitions
are preserved: 540 have exact BRep bytes and 24 pass strict
material comparison. Sixteen prior comparisons were reused only for identical
ordered BRep hashes and unchanged worker code. Full integrated STEP was not
repeated; strict prototype transfer bounds the STEP evidence to these joints.

A fresh full rebuild reproduces all 1,733 stored BReps,
156,452 persistent properties, 3,262 occurrence
records and 359 assembly records. The native is self-contained; identical
extracted analysis BReps use relative links to prior evidence to reduce disk
usage. Regeneration controls and source bindings remain in the prototype.

The inspected [isometric](track_joints_isometric.png), [fork detail](track_joint_detail.png)
and [source comparison](source_detail.png) are retained in the visual progression:
**241 images**, including all 238 earlier images. The same SNL6 camera is reused.
Inherited lever silhouettes, spring height/inclination and the earlier 21.867 px
high-speed control-bore discrepancy remain unresolved. Estimated new edges are
not camera-fit landmarks. Standard `tank011` remains unchanged; these are selected
subsystem views from the full development model.

The next physical task is a common SH946D rod geometry with compatible joint
angles and engagement on both sides. A separate source conflict needs resolution
before low-speed joints: SNL136 assigns the same M568A to M569A and M569B, while
the current high-speed pin is 15.875 mm and the low-speed eyes are 13.0 mm.
The [constraint probe](../short_joint_sources01/constraint_probe.json) preserves
actual saved measurements. M567 washers, M564 springs, M575 and long M573/M578
rods, center/front controls and remaining interiors follow. Poses remain deferred.

Recover without rerunning unchanged CAD checks:

```sh
python3 cad/003_FullTank/experiments/drive_chains/verify_rear_track_joint_checkpoint.py
python3 tools/cad_pipeline/decisions.py cad/003_FullTank/decision_ledger.json
```

For regeneration, use `build_rear_track_joints.py --output <new absolute directory>`
through the headless launcher after the prototype evidence is current. Extract,
run `check_rear_track_joint_installation.py`, then seed exact prior comparisons
with `seed_rear_track_joint_preservation.py` and run
`check_rear_track_joint_preservation.py`. Fresh integration is compared with
`check_powertrain_frame_reproduction.py`. The fixed checkpoint qualifier freezes
completed evidence once; changed geometry requires a new checkpoint.
