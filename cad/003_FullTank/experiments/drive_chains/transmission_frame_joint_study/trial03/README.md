# Formed frame joints and first rivet allocation — 24 September 2026

`PowertrainWithFrameJoints.FCStd` adds **32 frame rivets** and revises the receiving
geometry. The development model now has **2,505 physical occurrences, 464
definitions and 226 assemblies**. Nine definitions change; all previous
occurrence placements remain fixed. Standard tank011 is unchanged.

The eight previously flat gussets now have estimated 80 mm returns behind the
upright flanges, providing **2,880 mm²** of broad-face contact per joint. The
middle diaphragm moves forward by the 8 mm angle stock and widens to overlap
each inner upright by 32 mm. Four rivets join each overlap, leaving **17,087.872
mm²** of bearing area after the holes. Three rivets join each gusset to its
channel. Fastening the return flanges to the uprights remains unfinished.

## Source limits

SNL96–97 gives 78 frame rivets in eight size groups. This trial models the printed
32 button-head rivets of **11/16 inch diameter × 1½ inch stock length**. Allocating
24 to gusset/channel joints and eight to the diaphragm is an explicit hypothesis;
the catalogue does not locate them individually. The other **46 rivets**, four
M338 brake-suspension brackets and two M385 stops remain unpopulated.

The formed returns, diaphragm overlap, hole pattern, 8 mm stock and button-head
proportions are mechanical reconstruction estimates. SNL23 and HB126 constrain
the frame/casting arrangement, but do not resolve these hidden joints. The prior
model offered only end or edge contact at these interfaces. This trial supplies
overlapping material that can be riveted; it does not establish original factory
construction. Bend radii are not reconstructed. Source records, identifiers and
image hashes are retained in `../sources.json`.

Rivet stock length is measured below the factory head **before upsetting**.
The installed grip is 16 mm. The remaining stock forms an analytic spherical-cap
tail with **5,292.915898 mm³** volume and 11.978656 mm height. Both heads use an
estimated 30.559375 mm diameter. Independent checks preserve the complete grip,
printed diameter and total stock volume, and verify both bearing faces. Clearance
is a documented geometric allowance, not a historical manufacturing tolerance.

## Validation and retained failures

All **250 saved-geometry checks pass**, including every occurrence frame and
owner, prior assembly frames, bores, bearing faces, stock volume, eight return
contacts, two diaphragm overlaps and all earlier MX1 pad contacts. Lifted-head
and displaced-shank negative controls are included. All **238 nearby development
material pairs** and the one retained standard-context pair pass. Filtering covers
the complete development assembly and 5,316 retained standard occurrences;
acceptance is scoped to the **45 affected occurrences**.

All **55 strict STEP comparisons pass**: ten definitions and 45 installed
occurrences. `FrameJointsDefinitions.step` and `FrameJointsInstallation.step`
retain the established validity, two-way material, tolerance and centroid checks.

The first build saved its native document, then failed while accessing an assembly
name after closing the document. `../trial01/` retains that failure. The corrected
builder captures identifiers before closing. The first geometric layout put four
rivets at each gusset; its tails fouled the upright and diaphragm in sixteen
material pairs, despite passing local seat checks and STEP exchange. That rejected
layout and its results remain under `../trial02/`. The current allocation changes
geometry and locations; no acceptance tolerance was relaxed.

The fresh nominal reproduction uses deterministic UUIDs on the eleven newly
created assembly containers. The existing strict reproduction checker requires
all archived shapes, frames, hierarchy, types and persistent properties to match;
there is no UUID exclusion in this trial. Its generic report still calls the
scope a transmission-support rebuild. All **1,418 archived BReps, 9,189 object
types and 119,075 persistent properties** reproduce exactly.

All **454 unchanged definitions** match the MX1 parent: 434 exact BReps and twenty
strict material comparisons. The first preservation process terminated with exit
143 before completing the lower-engine-case comparison; its cause was not
established. The retained retry reuses hash-bound completed pairs and finishes
successfully. This interruption was not a geometric failure.

Increasing return height by 10 mm and moving the channel/gusset hole axes forward
2 mm passes the same **250 checks and 238 + 1 context comparisons**. All 454
unchanged definition BReps match the nominal candidate exactly. The variation
does not claim separate STEP or historical qualification. Its controls, changed
definition BReps and reports are retained under `parameter_trial`; its complete
native and the fresh nominal rebuild remain in `.work/transmission-frame-joints/`.

The [isometric](isometric.png), [frame interior](frame_front.png) and
[corner detail](gusset_joint.png) were inspected directly. Three new progression
images bring the total to **167**, preserving all 164 previous images and 26
recorded native baselines. Cropping and wireframe context are display choices;
the saved physical assembly is complete within this trial's stated scope.

## Rebuild and continue

Use the headless skill launcher, absolute file arguments and a fresh output
directory. Scripts are in `cad/003_FullTank/experiments/drive_chains/`:

1. `build_transmission_frame_joint_trial.py --source <MX1-trial-directory> --output <fresh>`
2. `pump_integration_worker.py extract --input <fresh>/PowertrainWithFrameJoints.FCStd --output <fresh>/isolated/manifest.json`
3. `check_transmission_frame_joint_trial.py --candidate <fresh> --standard-context <extracted-standard-directory>`
4. `exchange_transmission_frame_joint_trial.py --candidate <fresh>`
5. `render_transmission_frame_joint_trial.py --candidate <fresh>`

Use ordinary Python for `check_transmission_frame_joint_preservation.py --candidate
<fresh>` and `check_powertrain_frame_reproduction.py --candidate <first>
--reproduction <second>` after another independent build/extraction. Controls
inherited from the earlier frame packet include reference-only station values;
the builder takes all actual placement frames from its saved source. Dimensions
update by regenerating the scripts, not by editing inert native metadata.

Continue the remaining frame rivet allocations and return-flange joints, brake
supports/stops, holding feet, packer mapping and hull attachments. Full engine and
tank interior work follows. The full tank and complete installation remain
unfinished; pose variants stay deferred.
