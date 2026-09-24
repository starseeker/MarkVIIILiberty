# Rear track-brake rod end joints

[RearTrackRodJoints.FCStd](RearTrackRodJoints.FCStd) contains four linked end
joints: four M569C forks, four M568C pins, four split pins and four plain U.S.
Standard nuts. These 16 occurrences use four shared definitions. The nut is a
copy of the full development assembly's existing definition for prototype tests;
integration reuses that definition directly.

Original SNL86/136/194 scans establish two forks per SH946D short connecting rod,
M568C pins of 1 9/16-inch listed length, 1/8 × 1-inch split pins, and two 3/4-inch
nuts per rod. The pin's length datum is assumed under its head. The fork outline,
ear stock, socket, pin diameter/head and installed angles are estimates, recorded
in [the source review](../track_joint_source_review02.json). Threads use nominal
cylindrical envelopes; the 19.05 mm minimum engagement is a modeling criterion.

The first version had coaxial pin holes but its 16.5 mm fork throat struck all
four receiver outlines. The preserved [failed trial](../track_joints01/independent_checks.json)
records the collisions. The revised estimated throat is 22.225 mm and socket
face is 44.45 mm from the pin axis, retaining 22.225 mm of available thread
engagement. Receiver geometry and listed pin length did not change.

Nominal and +0.5 mm ear stock each pass 76 saved-native/interface checks, 28 local
material pairs, 30 surrounding-material pairs and 20 strict STEP comparisons.
Checks include actual cylindrical eyes, full pin engagement, head/nut bearing,
cotter retention with displaced negative controls, socket wall/engagement and
all saved development/retained-standard surroundings. A fresh nominal build
reproduces all 12 stored BReps, 1,098 persistent properties, frames and identities.

The [isometric](track_joints_isometric.png), [detail](track_joint_detail.png) and
[fixed-camera comparison](source_detail.png) were inspected. SNL6 registration
is unchanged; known inherited lever/profile discrepancies remain. New estimated
fork edges were not used as fitting landmarks, and handbook photographs remain
uncalibrated. The [full integrated checkpoint](../track_joints_integrated01/README.md)
records assembly transfer and preservation.

No physical SH946D rod, M567 washer or spring is added. The end-pin axes are
perpendicular and the two installed endpoint vectors differ. Solve a common rod
shape with appropriate joint angles and engagement before accepting complete
connections. The initial horizontal fork axes are provisional.

A separate source conflict prevents accepting low-speed M569A joints yet:
SNL136 assigns the same M568A pin to M569A and M569B, but the current high-speed
pin is 15.875 mm diameter while the modeled low-speed eyes are 13.0 mm. The
[measured constraint probe](../short_joint_sources01/constraint_probe.json) preserves
this conflict. Reconcile the shared definition and receiver estimates; do not
invent unexplained diameter variants of the same catalogue mark.

Regenerate with `trial_rear_track_joints.py --controls <absolute path to
track_joint_controls02.json> --output <new absolute directory>` through the
project headless launcher, then extract with `pump_integration_worker.py extract`
and run the native, context and STEP checkers. Use a fresh output directory to
preserve this evidence. Parametric dimensions update by regeneration.
