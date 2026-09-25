# Shared straight rear track-brake connecting rods

[RearTrackConnectingRods.FCStd](RearTrackConnectingRods.FCStd) is a 24-component
trial containing two new SH946D rods, the 16 existing end-joint parts and six
revised receiver instances. Seven definitions are shared. The selected two rods
use exactly the same solid and length, **296.0460545 mm**, with 20.6375 mm nominal
insertion at each end. Catalogue SNL194 supplies identity, quantity and two
3/4-inch plain U.S. Standard nuts per rod; it does not print the rod length.

The original [source packet](../track_rod_sources01/sources.json) and
[review](../track_rod_source_review02.json) distinguish evidence from estimates.
SNL6 shows the short connections as straight in plan and side views. HB104 adds
qualitative photographic context. HB188 calls the corresponding M577 a tube;
that does not establish the internal section of the selected SNL SH946D version.
The solid 19.05 mm section remains an estimate based on the nominal thread size.
Threaded regions are cylindrical envelopes, without a thread helix.

The old fork axes could not accept a common straight rod: their perpendicular
pin axes required a world-X rod, but their eye centers differed in both Y and Z.
The shared M330 lever's estimated distal Z is revised from -220 mm to
-205.4779412 mm. All four low-speed/track occurrences consequently rise14.5220588 mm
at that eye. Their upper pivot/swivel bearing faces and hardware frames remain.
This changes the lower arm profile; it is not a historical length measurement.

The first trial retained the M4132 profile and rotated its lever farther to close
the rod. It passed local axis and engagement checks but failed four whole-material
pairs: both long arms struck adjacent low-speed levers and both short arms struck
their forks. [That failed native and checks](../track_rods01/context_checks.json)
are retained. The final M4132 brake-arm radius is64.8209311 mm, shortened from
76.2 mm, with its whole front arm and journal bearing preserved. The selected
21.85°/158.15° poses each differ1.85° from the preceding approximation and minimize
the squared angular change for a symmetric straight-lever solution.

Both rods now join X2156.6538668 and X2500.3249213 eye centers at Y±770.1642857,
Z625.125 mm. Fork, pin, cotter and nut shapes remain unchanged. Eight actual
[operating-eye coordinates](operating_interfaces.json) are measured from the
saved revised receivers, including the two long-front-rod eyes affected by clocking.
Older corresponding coordinate receipts are superseded only for this revision.

Nominal and 19.55 mm insertion variants each pass90 saved-native/interface checks,
156 whole-material comparisons against current development and retained-standard
geometry, and31 strict STEP comparisons. Checks cover full cylindrical bearing
faces, shared stock volume, real receiver axes, socket engagement, nut passages,
and displaced/withdrawn-rod negatives. A fresh nominal build reproduces21 archive
BReps and1,716 persistent properties with no differences.

The inspected [isometric](track_rods_isometric.png), [connection detail](track_rod_detail.png),
[top view](track_rods_plan.png) and [source comparison](source_detail.png) show the
result. The SNL6 side camera is reused unchanged. Inherited lever silhouettes,
positions and spring-height disagreement remain visible; new geometry is not a
camera-fit landmark. Static fit does not prove historical dimensions or motion.

[Full integration](../track_rods_integrated01/README.md) propagates the two shared
receiver revisions and installs the rods under the existing short-connection
assemblies. Low-speed M568A versus receiver-diameter reconciliation, SH946E rods,
M567 washers, M564 springs, longer rods and full standard integration remain open.

Regenerate into a fresh absolute output directory with
`trial_rear_track_rods_aligned.py --controls <track_rod_controls02.json> --output <new directory>`
through the project headless launcher. Then extract and run
`check_rear_track_rods_aligned.py`, `check_rear_track_rod_context.py` and
`exchange_rear_track_rods.py`. Controls update geometry through regeneration;
custom metadata does not create live FreeCAD expressions.
