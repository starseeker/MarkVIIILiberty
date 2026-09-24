# Rear control-channel stock study

This is an **unfinished M4128 stock hypothesis**, saved separately from the
qualified powertrain. The standard tank and 3,173-occurrence development assembly
remain unchanged. Mounting holes, cleats, rivets, spring brackets and brake
fulcrums must be developed before integration.

The [native stock](RearControlChannelStock.FCStd) is a downward-open channel,
152.4 mm fore-and-aft by 50.8 mm deep, 2,200 mm long, with 6.35 mm stock. Its
center is X = 2,400 mm, Y = 0; both lower flanges rest on the measured floor
surface at Z = 533.05 mm. These section dimensions and station are approximations.
The generator uses an extruded planar section with sharp corners; rolled corner
fillets and finish remain pending. Edit the versioned controls and regenerate;
the native dimension properties are descriptive metadata, not live constraints.

The [local source overlay](../channel_projection01/rear_side_detail.png) retains
the reviewed SNL6 rear side segment. The inner-circle interpretation supplies
the printed 381 mm high-speed drum diameter as a conditional scale. Three outer
drum checks differ by 1.8–2.8 pixels. They are correlated checks of one silhouette,
not three independent depth landmarks. The saved high-speed control bore differs
by 21.867 pixels, beyond the six-pixel picking allowance. This discrepancy stays
open for lever/rod/illustration review; the registration was not refitted to it.
The channel outline comes from the same figure and is not an independent check.

[Nominal checks](independent_checks.json) and the
[0.5 mm thicker-stock variation](../channel_stock_variation01/independent_checks.json)
each pass 13 native/section/interface checks, including three nearby material
pairs, full two-flange floor bearing, and lifted/intruding negative controls.
The context probe shortlisted 492 saved occurrences in an enclosing region;
the complete stock lies inside it. Both variants pass two strict STEP comparisons,
in definition and installed coordinates. These checks qualify this limited stock
trial only, without establishing a historically correct mount or installation.

The initial single-object STEP export lost the installed translation. The
[retained failure and three-case setting probe](diagnostics/single_object_placement_default/README.md)
identify the task-local `Mod/Import/ExportKeepPlacement` setting. With it enabled,
the unchanged solids pass the original material, mass and tolerance criteria.

[Source review](../channel_sources01/source_review.json) preserves the handbook's
two left cleats/five fulcrums and the SNL's four/four. Original scans confirm the
printed difference. SNL is internally consistent for the next rear assembly
hypothesis: four M4130, two M4129, four M4131. HB189 additionally lists a center
M4131, while the diagram labels M1431; that identity relationship remains open.

Next, resolve transverse bracket stations from the intact local plan and the
photo, and construct the cleats with real floor bolts and channel rivets. Reconcile
stock lengths with finished grip; retain the channel's narrow clearance below
the existing left clutch support. Then populate the four fulcrums and spring
supports, review the M581 route/lever identity, and route M575 to the fixed brake
bores. Reuse this registration for new comparisons and reverify only affected
anchors or contradictory evidence.

Freshness check from the repository root:

```sh
python3 cad/003_FullTank/experiments/drive_chains/verify_rear_control_channel_study.py
```
