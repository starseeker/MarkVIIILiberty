# Four retained rear-control fulcrum units

[PowertrainWithRearControlFulcrums.FCStd](PowertrainWithRearControlFulcrums.FCStd)
contains **3,226 physical occurrences / 558 used definitions / 347 assembly groups**.
This development checkpoint adds four M4131 bracket/journals, four horizontal
levers (two M4132, one M4133 and one M4134), four M4137 spring washers, four
¼ × 2 inch cotters and eight ½ × 2⅛ inch rivets. Eight receiving holes are added
to the existing channel. The four units belong to `Root/RearControlChannel`;
repeated components share definitions. The preceding channel/mount/floor geometry
and all its occurrence frames are retained, apart from the declared channel holes.

Native SHA-256: `d4f9a5bd2294b0e41755b3fce3e47197bf4d04f165e1c4ec918246ba2edec2c2`.

The full standard tank is still in progress. Standard tank011 is unchanged;
M4129 attachments, spring supports, rods and subsequent controls remain open.
This checkpoint establishes local static fit and reproducibility, not historically
exact casting geometry, load capacity or complete installation/removal paths.

## Evidence and the geometry revision

[Source review02](../fulcrum_source_review02.json) records the selected topology,
plan picks and the reason for changing the earlier version. HB104 suggests a
narrow vertical bearing column between the lower flange and horizontal arm.
The first broad full-thickness base/short hub is retained in
[fulcrum01](../fulcrum01/fulcrum_detail.png). Its geometry passed local checks,
but the source comparison motivated a thinner web/seat and a longer lever hub.
The updated close-up is [fulcrum_detail.png](fulcrum_detail.png).

The original SNL72–73 rear-control composition lists four M4137 washers, two
M4132 levers and one each M4133/M4134. SNL267's eight M4137 washers is a global
quantity, not the rear quantity. The original scans were inspected and hashed in
[catalogue_scan_review.json](catalogue_scan_review.json). SNL36 and170 supply
four bracket assemblies and two rivets per bracket. HB's five rear fulcrums and
the center M4131/M1431 identification remain explicit source conflicts.

The cast foot and vertical rivet axes are hypotheses: the photograph obscures
their details. The nominal web/seat is9.525mm thick, rivet bosses25.4mm, journal
diameter31.75mm, and hub height38.1mm. Lever, washer and bore profiles are estimated.
The rivet stock is interpreted as53.975mm unformed shank, with31.75mm installed
grip and a volume-conserving upset head. The flat annular washer represents its
compressed static state; free form is unknown. Cotters use the existing formed-pin
helper with50.8mm under-eye leg centerlines; overlapping eye junctions do not
establish an exact total wire-stock volume.

The outer track-brake pivots lie at X2476.2, Y±710mm; inner low-brake pivots at
X2298.4, Y±450mm. Their bases are at Z583.85mm. The inner pivots overhang the
channel rear edge by25.4mm; both rivet root pads fully bear on channel material.
These stations remain approximate. Source plan picks guided the construction
and are not independent validation landmarks.

## Camera reuse and views

The [isometric](fulcrum_isometric.png) shows the four units, existing mounts and
selected floor context. The [source detail](source_detail.png) uses the unchanged
[local SNL6 registration](../channel_local_registration01.json). The existing
21.867px high-speed control-bore discrepancy is retained. Correlated drum checks
of1.8–2.8px do not independently establish the camera. HB104 remains an uncalibrated
photograph and the segmented plan has no global calibration.

[camera_reuse_review.json](camera_reuse_review.json) records the reason for reuse
and triggers for targeted reverification. New independent landmarks are checked
with the old camera first. A proposed refit needs a recorded reason and comparison
of both cameras against identical current geometry and independent check features.
The [general camera workflow](../../../../../../tools/source_camera/README.md)
preserves numerical fits, landmark identities and interpretation separately.

All four integrated render images are byte-identical to the reviewed prototype
plus the same retained context; the renderer resolves actual nested native frames.
Four new progression images preserve the first and revised hypotheses, bringing
the archive to229 images without changing the previous225.

## Qualification and recovery

[qualification.json](qualification.json) freezes the native, controls, source
records, images, check receipts, scripts and reused evidence. Recovery requires
no new CAD computation:

```sh
python3 cad/003_FullTank/experiments/drive_chains/verify_rear_control_fulcrum_checkpoint.py
```

Nominal and +0.5mm rivet-boss stock each pass82 native/interface checks,46 local
material pairs, four surrounding material pairs and33 strict STEP comparisons
(eight definitions plus25 installed shapes). Surrounding screening includes all
3,202 parent occurrences and5,316 retained standard occurrences; only potential
material contacts advance to the Boolean checks. The channel is separately checked
for the exact eight holes and no added material.

Integration passes46 checks covering strict prototype transfer, all3,226 relocated
links, inherited frames/owners and persistent metadata. All550 unchanged inherited
definitions are preserved:529 exact and21 through strict material comparisons.
Sixteen completed comparisons were reused only for identical ordered BRep hashes
and unchanged worker code. The receiving channel and seven new definitions match
the STEP-qualified prototype; no repeat full integrated STEP export is claimed.

Fresh prototype generation reproduces24 archive BReps and1,636 persistent properties
with no permitted differences. Fresh full integration reproduces1,706 archive BReps,
11,942 object types,153,954 persistent properties and all frames/hierarchy. Whole
FCStd archive byte identity is not claimed. The native is self-contained;514 exact
duplicate extracted BReps use relative links to durable parent files.

Two checker diagnostics remain visible. The early local checker incorrectly
restricted all planar lever contact to the hub annulus; the corrected check tests
that annulus independently while allowing legitimate arm support. The first
integration metadata audit omitted the existing1e-12 Placement serialization
allowance for LinkPlacement;12 quaternion values normalized from zero to1e-16.
The corrected audit applies the same bound and XML-structure requirement. Neither
correction changes material or placement tolerances or modifies native geometry.

Reconstruction is controlled by [fulcrum_controls02.json](../fulcrum_controls02.json),
`trial_rear_control_fulcrums.py` and `build_rear_control_fulcrums.py` in the parent
experiments directory. Use the existing headless launcher with absolute script,
controls and fresh output paths. The isolated builder takes `--controls` and
`--output`; integration takes `--output` and transfers the qualified saved prototype.
Change the parameter packet and regenerate; these reconstructed features do not
claim a fully live sketch dependency graph. Early version01 builders are frozen
beside their original receipts and must not be checked against version02 code.

## Next interfaces

[operating_interfaces.json](operating_interfaces.json) measures eight new rod-eye
cylinders and reverifies four inherited brake eyes against the current saved native.
New eye centers are at Z625.125mm with vertical pin axes; the brake eyes are at
Z610.602941mm with transverse axes. Both have13mm bores and12.7mm bearing width.
Their connecting forks therefore need a quarter-turn difference in orientation.

| Proposed rear rod | Starboard eye-center chord | Port eye-center chord |
|---|---:|---:|
| M578 track/foot brake |346.102mm|350.607mm|
| M573 low-speed brake |196.776mm|180.593mm|

These chords are measurements of the reconstruction, not source rod lengths or
clearance results. SNL86 assigns M569C forks to both ends of M573/M578; do not
substitute M570 based on a generic figure label. Next establish M4129 attachment
and M4135/M4136 spring supports, then the full fork/thread/spring/rod routes and
clearances. The channel leaves approximately0.57mm below the left clutch-support
lower envelope, requiring actual-surface checks for the remaining upper hardware.
M581 identity and M575 routing remain open. Posing stays deferred.
