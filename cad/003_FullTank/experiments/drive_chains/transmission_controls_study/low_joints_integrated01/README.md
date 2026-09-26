# Installed rear low-speed brake end joints

[PowertrainWithRearLowJoints.FCStd](PowertrainWithRearLowJoints.FCStd) is the
current full development native: **3,280 physical occurrences, 569 shared
part definitions and 365 assembly groups**. Four M569A forks, four M568A pins,
four split pins and four plain nuts add 16 parts. New port and starboard
`LowShortConnection` groups each own two end-joint groups beneath
`RearControlChannel`. The four nuts reuse `Def_USStdControlNut`, and the pins
and cotters reuse `Def_ControlJoint_pin` and `Def_ControlJoint_cotter`;
`Def_LowJoint_fork` is shared across all four low-speed joints. No inherited
receiver geometry or part placement was changed.

The [prototype dossier](../low_joints01/README.md) separates source quantities
and listed hardware lengths from estimated fork/pin form. The literal 1″ length
from SNL 87:002 is interpreted under the `throat_to_rod_seat` datum (providing a
25.4 mm full threaded socket meeting the ≥ 19.05 mm engagement criterion). An
estimated throat depth of 23.8125 mm (15/16″) clears the starboard fulcrum lever
arm entering at -56.89° (extending to 22.6738 mm) with 1.14 mm clean margin,
giving a 49.2125 mm pin-center to rod-seat distance. The failed 1″ pin-center-to-face
trial remains preserved as a diagnostic in records. The joints are an intermediate
static arrangement: two SH946E rod bodies and final closure remain unfinished.

Nominal and clearance/stock variation prototypes each pass 78 native/interface checks,
28 local material pairs, 46 surrounding context pairs and 20 strict STEP comparisons.
The integrated native passes 33 checks covering all inherited frames/owners,
persistent properties, relocated local links and strict transfer of four
definitions and 16 installed shapes. All 568 inherited definitions
are preserved: 547 have exact BRep bytes and 21 pass strict
material comparison. Seventeen prior comparisons were reused only for identical
ordered BRep hashes and unchanged worker code.

A fresh full rebuild reproduces all 1,739 stored BReps,
157,512 persistent properties, 3,280 occurrence
records and 365 assembly records. The native is self-contained.

The inspected [isometric](low_joints_isometric.png), [fork detail](low_joint_detail.png)
and [source comparison](source_detail.png) are retained in the visual progression:
**250 images**, including all 247 earlier images. The same SNL6 camera is reused.
Inherited lever silhouettes, spring height/inclination and photographic discrepancies
remain unresolved. Estimated new edges are not camera-fit landmarks. Standard `tank011`
remains unchanged; these are selected subsystem views from the full development model.

The next physical task is connecting the two SH946E straight rods between the
installed front and rear sockets. M567 washers, M564 springs, M575 and long M573/M578
rods, center/front controls and remaining interiors follow. Poses remain deferred.

Recover without rerunning unchanged CAD checks:

```sh
python3 cad/003_FullTank/experiments/drive_chains/verify_rear_low_joint_checkpoint.py
python3 tools/cad_pipeline/decisions.py cad/003_FullTank/decision_ledger.json
```

For regeneration, use `build_rear_low_joints.py --output <new absolute directory>`
through the headless launcher after the prototype evidence is current. Extract,
run `check_rear_low_joint_installation.py`, then seed exact prior comparisons
with `seed_rear_low_joint_preservation.py` and run
`check_rear_low_joint_preservation.py`. Fresh integration is compared with
`check_powertrain_frame_reproduction.py`. The fixed checkpoint qualifier freezes
completed evidence once; changed geometry requires a new checkpoint.
