# Initial installation-layout visual review — 19 September 2026

Inspected the generated isometric, the native-edge SNL longitudinal overlay and
the independently rotated handbook cutaway. Also inspected HB Plates 35–36,
SNL Plate 24, and the accompanying handbook descriptions of the cooling system.
This review covers the initial layout, not finished tank parts.

## Findings and disposition

| Subject | Observed result | Disposition |
|---|---|---|
| Overall arrangement | Forward upper structures and fighting space, middle/rear engine, aft transmission and rear fuel space follow the broad longitudinal arrangement. The model is still a collection of installation envelopes and reference guides. | Useful basis for the next parts; complete platework and running gear remain required. |
| Upper widths | Driver and lookout widths are now independent of the main enclosure. | Improvement over the pilot. Verify transverse sections and reconcile main-enclosure length/height before detailing its plates. |
| Source overlay | Traced envelope edges coincide with their originating SNL profiles; independent wheel diameters remain visibly comparable to the drawing. The idler is a coarse annulus and the track route is a polygonal guide. | Do not count trace coincidence as independent proof. Wheel sections, teeth, track units and constant-pitch closure remain open. |
| Independent HB cutaway | Rotation now places the front on the left and the upper structures above the hull, matching the model review direction. The broad machinery order is comparable without scaling the HB image into an assumed metric drawing. | Retain as a separate qualitative check; source differences and scan distortion remain possible. |
| Cooling | The radiator is now on the port side and the fan spindle is transverse, consistent with HB pp. 97–98. Its current longitudinal/vertical reservation still overlaps the transmission envelope. | **Unresolved material layout conflict.** Inspect the fan/radiator installation in transverse views before fixing mounting datums. |
| Engine/clutch | Their envelope regions intersect; the clutch also intersects the transmission reservation. | Resolve the true axial interfaces and the amount of casing/envelope represented on each side. These are not accepted physical overlaps. |
| Carburetor | A small reservation is present in the engine package. Its appearance is not a reconstructed Ball and Ball casting, and its installed quantity remains unresolved. | Obtain production-specific arrangement evidence and refine the package before claiming that component complete. |
| Fuel tanks | Three separate transverse occurrences are present behind the engine compartment. | Arrangement is provisional; the profiles do not establish production shell form or capacity. |
| Rendering | Faint hull/track guides restore whole-vehicle context while exposing the colored machinery envelopes. Source comparisons use native geometry and do not optimize image registration against the CAD edges. | Suitable for discrepancy review, not a finished appearance render. |

## Geometric review prompts

The validation report currently identifies four unresolved layout-overlap pairs:
engine/clutch, engine/carburetor reservation, transmission/clutch and
transmission/cooling fan. These may reflect broad package reservations or incorrect
placement. Their resolution requires component geometry and source interpretation.
The technical pipeline checks pass independently of these open historical/fit
questions; physical fit and complete-tank acceptance remain false.

## Reviewed artifacts

Paths are relative to build. Hashes identify the actual viewed raster artifacts:

| Artifact | SHA-256 |
|---|---|
| previews/isometric.png | 887e5400000dceb1dd1d5a2afb7dffd7ff53b60a16e94c51f407c1366d1208e1 |
| comparisons/snl_longitudinal_overlay.png | 3585ca630e728dad87194c6eacfeb6ef377f5cfb97f0d5ca4f0950cf58cfe9b0 |
| comparisons/hb_longitudinal_source.png | 5ccd1dbcf18d77b72cc1adc3f39718d92ff789073aa21b4debda31fd245085c1 |

The interactive HTML comparison is generated beside these files. A later geometry,
calibration or renderer change requires a new visual review; this document does
not automatically approve regenerated artifacts.

## Track-component iteration — 19 September 2026

Inspected the new top, oblique and side track views and the whole-model isometric
against HB Plate84 and SNL Plate26. The source photographs show the same general
three-shoe view; they are not independent metric measurements.

The four bars form the two paired channels seen in the source. Each plate has
eight heads, an overlapping edge and a central pressing. The pins/bushings and
retainers now complete the SNL composition. The first lap-clearance sign error
was found by exact material-intersection checks and corrected.

The modeled forging has abrupt, regular web/foot transitions and the pressing is
localized to a mathematically smooth patch. The source appears to have broader,
less regular formed transitions. These differences remain open refinement items;
the photograph does not establish exact section shapes or spacing. The rectangle
visible around the pressing is a native surface boundary in the edge-rendered
view, not a physical seam or a separate plate.

The side view exposes the documented two-button rivet approximation. The ground
datum is at the underside buttons. This conserves the printed stock volume, but
the photograph does not show the underside; this particular formed-head choice
is not historically confirmed. The inherited overall layout is still visibly
incomplete and is not presented as a completed tank.

The straight joints are clear. Sampled negative bending reaches plate contact at
−10°, while the tested −5°, 0°, 10°, 20°, 30° and 35° positions are clear. The
full track path must establish the actual angles before these parts can be
accepted for a closed track.

Reviewed final iteration artifacts, relative to build:

| Artifact | SHA-256 |
|---|---|
| comparisons/track_top.png | af363c8b08d64596bb63aab941132e8342b4e4f26e1ade541dcc9fa90acf1652 |
| comparisons/track_oblique.png | 3d43082e825d5f9a27729920396fe0f94be12e9b3fe692e68e4a3a1ccb2a5fb9 |
| comparisons/track_side.png | f315209f33db8b4ae772c2579ecac47d3f100079b6d4a4b6225fcb74fcfdda09 |
| previews/isometric.png | 061023217f556579ce15e3a7f9824a1aa8221ff0e255e598e03ac6784ceaffa4 |

These findings correspond to the explicit source/geometry issues in the R01
packet. The previous layout-image hashes above remain a historical record.

## Closed-track iteration — 19 September 2026

Inspected the regenerated whole-vehicle isometric, fixed-calibration SNL overlay
and three-unit oblique close view. Both 78-unit loops are continuous and their
longitudinal silhouettes follow the broad SNL outline. Their source-derived
construction is not an independent confirmation of the historical route.

The source overlay still exposes disagreement around the drive/idler ends and
upper/lower transitions. The coarse wheel annuli are visibly separated from the
paired track-bar contact surfaces in the isometric. Their transverse section and
engagement remain R02/R03 work. Most central equipment remains layout geometry;
there are no finished hull plates or rollers in this view.

The three-unit close view retains the paired bars, connecting hardware and eight
heads per shoe. The pressing is a smooth native patch with a visible surface
boundary, not a separate sheet or seam. Forged contours and underside head form
remain provisional. Whole-vehicle views omit small track hardware for readability;
the close view, native assembly and physical STEP retain it.

Reviewed artifacts, relative to build:

| Artifact | SHA-256 |
|---|---|
| previews/isometric.png | 57cadf081dcbb3ee32ed789b1b1ef95364bf9da96c91f740131afa94a0796506 |
| comparisons/snl_longitudinal_overlay.png | bc5dbb6964e635ed446c7686288df491f159c4e4f751cebdad7465b94dfcbccd |
| comparisons/track_oblique.png | 24b47b1437e29ad420a49cac673c79a822e1a10a0048089455b66f173b56d567 |

These hashes identify this review only. Wheel-contact acceptance, full interior
coverage and the selected static poses remain open.

## Standard upper plate population — 19 September 2026

Inspected the integrated native isometric, fixed-calibration SNL2 overlay and
close rear view after replacing three upper enclosure blocks with 26 individual
plate/leaf solids. Earlier subsystem front and underside views confirmed the
open interiors and the five main mount apertures. No component was moved for
these inspection cameras. Compared against HB Plate30 and SNL Plate7.

The main, driver and lookout enclosures now have recognizable plate divisions,
closed side/front/roof leaves and viewing/periscope apertures. The original
port/starboard rear side opening sequence was found reversed during source
rechecking; it is corrected and now checked against HB43's explicit ordering.
The integrated view shows 31.75 mm transverse bounding separation between upper
armor and each physical track loop, without claiming any lower hull attachment.

The calibrated overlay retains the disagreement between HB35 printed dimensions
and the SNL2 trace: main length +370.510 mm, height -86.538 mm. The shell is centered
on the traced base, so its front and rear stations both differ visibly. The
lookout's height/station consequently differ too. The photographed rounded aft
roof transition is still a planar miter, and angle irons, rivets, covers, hinges
and brackets remain visibly absent. These are open source/form issues, not
finished coverage. The wider model still shows unfinished hull, wheel and interior
layout geometry. Standard geometry population remains the priority.

Inspected integrated artifact hashes:

- `previews/isometric.png`: `c68365214418aca1b9c8dae4ffc355e9871d955b6bb6c57d57dbe9a03266f31f`
- `comparisons/snl_longitudinal_overlay.png`: `fb109768234c07a16b1b64c1199f7390f73558416b67272a0b986450abf93adb`
- `comparisons/upper_rear.png`: `b45ff303c18fc2341a8d02093994d3aa29e1cccc608408bcda15bbc3d026a0a6`

Also inspected the final integrated front and underside views after the handed
opening correction:

- `comparisons/upper_front.png`: `63262849efe7ebf7abd8bb85274283fb3678e501ff33bdfceb78d6910386d2ed`
- `comparisons/upper_underneath.png`: `3c5fa90917dce356a5968086f0568a86a7fb514658113783d2b8ed92b19c91e3`

Additional dimensional cross-check: the installed lookout roof is at
Z = 3,011.322 mm, 112.878 mm below HB9's overall height. HB35 shell dimensions
and the current SNL2 base registration do not jointly satisfy that independent
height. Re-examine the traced base pick and actual hull roof interface during
H01; preserve this as an open installation issue rather than silently shifting
the model to improve the overlay.

## Standard main hull plate population — 19 September 2026

Inspected the integrated isometric and fixed SNL2 overlay, plus the isolated hull
oblique, right-side and underside projections. Compared the hull directly with
SNL Plates 1 and 7. Inspection cameras preserve the standard component placements;
the isolated views hide other systems without moving the plates.

The broad arrangement now follows the armor illustration: front and rear inner
walls, divided exterior sides, split side doors, skirts and individual floor and
roof plates. The sponson apertures are open; the full view still contains coarse
sponson layout blocks. The underside exposes the broad central floor and narrower
end compartments. Polygonal ends, inferred internal seams, missing rounded roof
transitions, local roof-to-side gaps, missing louver blades and missing structural
and fastening detail remain visible. These views do not establish a watertight
or historically complete hull.

Integration detected 80 material intersections between the newly modeled roof
plates and the earlier upper-run track hardware. The recorded smooth route
correction removes those intersections while preserving 78 units per side, the
printed pin pitch and the image calibration. The rebuilt native assembly passes
1,135 candidate hull material-pair checks, including 868 hull/track pairs, with
zero overlap. Both loops also pass their 1,958 selected track contact pairs.
The route correction is a bounded reconstruction assumption; wheel engagement
and rail support remain unqualified. The pin residual against the uncorrected
source construction is now 191.722 mm RMS / 300.847 mm maximum. It is not a
direct silhouette-error measurement.

The overlay retains the earlier upper-enclosure dimensional disagreement and
112.878 mm overall-height discrepancy. No source was rescaled to conceal these
issues. Repeated track hardware accounts for most of the 3,067 physical instances;
the 103 upper/main hull plates and seven track definitions remain partial, and
the missing unique systems remain visible in the coverage report.

Inspected integrated artifact hashes:

| Artifact | SHA-256 |
|---|---|
| previews/isometric.png | 319098de4921f8e801cffaf1895aa0092a2e7445fbe80f91fa93d73a28ac60dd |
| comparisons/snl_longitudinal_overlay.png | c5c27eab553e588c5fd0a7f3e28ba47a7672bf74a95fbbff7aa81a25f9ca02bb |
| comparisons/hull_oblique.png | 93ca2fbdd190c5ce2425d741723d8050a992485f23ff76a03d4202cfff657bc7 |
| comparisons/hull_right_side.png | d15b18ba51a0f4ec0762aa3c48e0545dfd00d98d49cebf14dedae305a6c61baa |
| comparisons/hull_underside.png | 20596d8b6d3a05dfd514e9776b9732a9f160041d7b62a96425b6902a0d4711e1 |

## Standard sponson shells — 19 September 2026

Inspected both standalone handed shells from outside, the port interior, the
underside, and the integrated isometric and side view. Compared with SNL7's armor
assembly and the SNL1/HB1 right-side photograph. The photograph pair is related
source imagery, not two independent dimensional confirmations. The CAD cameras
preserve installed placements and are not fitted to the perspective illustration.

The old solid blocks are replaced by 39 individual roof, floor, wing, side, back
and shield-infill pieces. The shells have the source's broad tapered form and
sloping lower skin. The front/outboard bays remain open for rotating shields and
mounts, so the integrated view exposes the unfinished interior layout blocks
through them. The exterior is visibly more complete, but this remains an empty
plate reconstruction with inferred seams and angular contours. Source-specific
shield recesses, formed lips, attachments, covers, stowage and fittings are absent.

The new width follows HB9's 3,657.6 mm envelope. The earlier layout block's size
and location were not retained as plate dimensions. The current hull aperture
provides the shell's X/Z installation; this remains inferred and will need
rechecking against the actual mounting and rail geometry. The nominal 1 mm
installation gap prevents metal overlap but does not establish an attached joint.
All 3,067 other physical components were considered by the contact validator;
only the 97 internal sponson pairs passed its bounding-box candidate filter.
Their exact material intersections are zero. Hollow, handed opening/absence and
normal-thickness checks also pass.

The inspected isometric was preserved byte-for-byte as
`cad/intermediate_snapshot_iso_003.png`, alongside the two user-saved stages.
The earlier images remain unchanged. See the [progression index](../VISUAL_PROGRESSION.md).

| Artifact | SHA-256 |
|---|---|
| previews/isometric.png | 172008f6c40ce8e1c944c9aae3d3cff3300b5cef77106167ad6900203fbacbbd |
| previews/side.png | 8411325efcf25c96858bf575402efd6717ebb220a960907444f551a5d4ec009f |
| comparisons/sponson_port.png | eff11165bd2dfcc7d8ffe2d172a3952dcb871f1d0f66c6e08d06d064215f729c |
| comparisons/sponson_starboard.png | 6d53cd8bb7710602b536a5dce00d7e1e47b12c464b56082a87a20ce16108eb21 |
| comparisons/sponson_inside.png | 7320a18a3796fe4ed0ea290046c1aaa4607e641265860ddd242ff27f82469598 |
| comparisons/sponson_underneath.png | dc19ba6050a17bede687a0e85aba4e4870496fd216f9d4b381d0471d9ff05f20 |
## 20 September 2026 — roof louver blade/frame milestone

Inspected the delivered integrated isometric and orthographic top, plus the
standalone/integrated louver oblique, top and three-blade section views. Compared
the broad roof arrangement with the SNL4 photograph and SNL7 armor drawing.
Lengthwise repeated slats and the two distinct aperture footprints now populate
the previously empty openings. HB41 guard height is retained; the exact tall
guard-to-side-frame assignment is provisional. The source camera was not fitted
and no calibration control was moved to obtain agreement.

The corrected close-section camera looks along the actual sloping blade axis,
revealing three separate rounded chevrons and their passages. Coarse curve
faceting in the raster is tessellation only; the native sections have tangent
circular arcs and independently checked 6 mm normal stock. The image does not
resolve whether the handbook intended an inside bend radius or this section
orientation, and does not qualify spacing/support hardware.

The full isometric still exposes interior layout blocks through the sponson bays
and at the unfinished rear roof. Rear deflector channels, louver spacers, end
packings, saddles, securing cleats and fasteners remain absent. The visible slats
are a partial population milestone, not completed cooling-system coverage.
Saved the delivered isometric without modification as
[snapshot 004](../intermediate_snapshot_iso_004.png); 001–003 remain unchanged.

| Inspected artifact under `build/` | SHA-256 |
|---|---|
| `previews/isometric.png` | `aee4cf8abdc73d6e7685c62665c730b496726d7c4f67ecaf342d208bb30f8cf6` |
| `previews/top.png` | `a6bdc8e3aff46b796eefe1f28e55d51f43d9d358a9b0f733cebbc75084abb416` |
| `comparisons/louvers_oblique.png` | `9e5328eb40ddb280e89f805275ce2f8425eca87d6c20ff3f586a0a01ca907e4a` |
| `comparisons/louvers_top.png` | `c9145af86cd94b863cff480ee77589b7108816c66ae9b0cc34549acbfd93a943` |
| `comparisons/louver_blade_section.png` | `076ccbba814c746b117905bbc57d1e531c6258036f2fce7783b20478ce43b2c8` |

## Roller-stack iteration — 20 September 2026

Inspected the standard isometric, upper stack, spring-stack transverse section,
installed roller/rail side view and unchanged-calibration SNL2 overlay against
HB88/89 and SNL29. The new lower rollers and external clamps are visible around
the front bend and along the lower shell. The rest of the tank remains partial.

The paired lower recessed profiles and single-sided inward upper flanges follow
the source topology. The spring/tube diameter conflict is explicit. The model's
spring plate uses a tapered inner web and flat outer flange; SNL29 shows a more
continuously formed contour. Curves, bushing length, ground spring ends, threads
and supports remain unresolved detail rather than visually certified geometry.

A service-instruction check changed the upper station: HB144 puts access to its
inner ends in the engine room. The SNL2 feature at (1025,248), at the rear roof
bend, supports that arrangement. The earlier forward trial was rejected and its
roof cuts removed. The final overlay retains fixed source X coordinates and
shows the reported vertical station offsets, including −31.957 mm at the upper
station. It was not refitted to conceal them.

The static rail-gap checks are 0.5 mm at all 120 rollers; they do not establish
loaded contact or continuous motion. Source-derived pick agreement in X is by
construction. Long support angles, upper covers, drive/idler and adjustment
geometry remain required before this running-gear packet can be accepted.

Snapshot 005 preserves the inspected standard isometric byte for byte.
Artifacts reviewed in this iteration, relative to build:

| Artifact | SHA-256 |
|---|---|
| previews/isometric.png | 494ec7acb1b08eb732de906249f96ede93f0d9dca7ab097bd531e4ca440c4701 |
| comparisons/roller_spring_section.png | 2d038ea0962dab267256ec731f113e953666c2a38168aad06b80943b0b5964c0 |
| comparisons/roller_upper.png | e89fcca2f50cce283f7281a70782b7268e3cbb169ee3b21fcc8947e2a6db0cb4 |
| comparisons/roller_rail_installation.png | 46e7b28be92efa5f655d3ac1ac27638b0422e9b6a6a142cce8dd24f1291a7043 |
| comparisons/snl_longitudinal_overlay.png | 05830e21e6d1004275495d02e83be1c0d52b81b08c3a0ab7775beeb11ca4eb90 |

The lower-pick allowance is ±35.570 mm vertically. Lower00/05/06/07/08/25/27/28
exceed it on each hand after native rail fitting. This is a retained geometry-to-
source discrepancy; the zero-overlap result does not resolve it.


## Upper support interface — 20 September 2026

Inspected the standard isometric, upper oblique and newly added transverse
section, revised spring section, installed roller/rail side view and fixed SNL2
overlay. Compared the upper section directly with HB asset plate88 and the
shared pin/clamp topology with plate89 and SNL29. M2092 now provides the flange
under the washers and a descending toe contacting the upper pin flat. The
earlier bottom-flat construction was reversed. The exact stepped end contour
is still approximated by a broader flat; angle length, stock, root radius and
attachment drilling are unprinted estimates.

The native fit report distinguishes four pin/toe and eight washer/flange
bearing faces from hull attachment: the outer angles meet the shell, while
the two inner angles remain 1 mm from the inferred roof opening. Neither a
complete attachment nor a qualified load path follows from this local fit.
The lower supports and SH294A covers are still absent. Source station offsets
and earlier tank-outline discrepancies remain; no source calibration was
refitted.

The whole-vehicle view changes only locally. Snapshots 001–005 are preserved;
006 remains reserved for the next significant visual population stage.

| Artifact | SHA-256 |
|---|---|
| previews/isometric.png | f7d66530c5fe4382d3f86cec4caaa69a8770da00ff4f50a00a2b86b903cb2c80 |
| comparisons/roller_upper.png | 918d5b41ec6d353c205238ac345628e8c50d3f9bbb483698a6766c5efd8cd058 |
| comparisons/roller_upper_section.png | bf81cdbb59714f2e6574f3febbcb10ffc16e738bc0fead11ff91d43419623bc5 |
| comparisons/roller_spring_section.png | 5d4d319bedacfe0dcb6b5a659d6c7434ae0808e39f1d20e1098fcb71c04a6e1a |
| comparisons/roller_rail_installation.png | f6767d3d6b36d450ed249bce90ab0844dc2ac8f8b49744e06171690b4c994a5f |
| comparisons/snl_longitudinal_overlay.png | 66a82c65f30021aea6cc509f14d9e8fbd117358bf499305ee9f9bd9a70d95cbc |

## Partial idler wheel stage — 20 September 2026

Inspected saved-build standard isometric, idler oblique/elevation/transverse half section, installed track/foremost-roller view and fixed-calibration SNL2 overlay against HB87 and SNL28.

- Separate paired rims/disks, six lightening holes, boss and relieved diaphragms reproduce the broad depicted construction; most detail is enclosed in the standard exterior view.
- The modeled diaphragm has a smooth rounded waist; the drawing depicts a flatter central trough and steeper shoulders. Exact formed section and X/Y distinction remain open refinement items.
- Rivet locations, stock, clearances and head profiles are inferred. The shaft, bracket and guard are visibly absent and remain unpopulated.
- The front-roller source point is preserved but its installed X moves 45 mm rearward, 8.838 mm beyond initial horizontal pick uncertainty. This is a documented reconstruction discrepancy.
- The narrow-rim/bushing interface is a provisional static interpretation, not continuous engagement or historical-fit qualification.

| Reviewed artifact | SHA-256 |
|---|---|
| `previews/isometric.png` | `e375e9e2aad2f6a449a3191e5ce42c73d53a5e250c62217847381dea2b52c7d6` |
| `comparisons/idler_oblique.png` | `4579c66d788ca9bbe532992b05639c7f4cc76690884d70db317fe256d00237ec` |
| `comparisons/idler_elevation.png` | `a18d808c9eed2c73724342d3a04c3a772784f5ecd63698e9d5875e40e7412484` |
| `comparisons/idler_section.png` | `833f261ea7393de3c4e1424a6d717e27f6355308e2d81aafced202b3baf86760` |
| `comparisons/idler_installation.png` | `e22882299b5636643ada07fdb3f26011b0d1c028db0d5fc2d3121e9498868035` |
| `comparisons/snl_longitudinal_overlay.png` | `e3eeed0c104873cd74375378f29ab44435a55769a8895710cb7819a971280cbe` |

Further section-reading issue: The provisional disk/rim attachment land is outboard; the original section may support an inboard arrangement. Its axial interpretation requires further source and full-interface checks before historical qualification. See the retained idler research packet.

## 20 September 2026 — idler mounting stage

Standard isometric now visibly includes both front adjustment brackets; previous snapshots remain independent.

Nested disk/rim land and flattened central diaphragm trough better follow the HB87 section reading. Exact stock, shoulders, X/Y difference and underside web relief remain approximate.

Separate shaft, bracket, plate, guard and screw topology is visible in the new detail and axis-section views. Printed screw/opening dimensions are retained; cast profiles, U bezel and reinforcing outline remain inferred.

Source eight-head pattern is not resolved by the four listed cap screws plus five allocated outer rivets. The inferred three-rear/two-front reinforcement layout is explicit, with inner plate retention still open.

Fixed SNL overlay preserves the source calibration and existing outline/station discrepancies; no raster matching or pixel-perfect claim. Static wheel/bushing contact is provisional.

HB87 shows a level assembly from a different viewing side; the native elevation retains the installed inclined axis. Head-window direction and inclination are therefore not pixel-aligned comparisons.

Inspected raster SHA-256 values:

- `previews/isometric.png`: `c9f03efc751c3d84b504946ece85c731757ad76dc88d167c42ce3716d7f98073`
- `comparisons/idler_oblique.png`: `357c8b77fc3a2e8bd3ee84ec0aec51802c7c4ead6d99e43f4bc28400bd05b5a5`
- `comparisons/idler_elevation.png`: `cf279dfd6bfa6d33c28c29c71428e31c98f189b788d7a8ca38cb3d5c23ccd8ed`
- `comparisons/idler_section.png`: `e3cb6c7da27ce178ea84b19dd2e89418f4068915b16730aec0921f0572c56c2f`
- `comparisons/idler_installation.png`: `a7adc421acc81084c685532306044bf2062e7ab97bcb956e500e7772bfa5d38f`
- `comparisons/idler_mount_detail.png`: `10a8bffb339466f2cb7cc630bd1490791a9e51e660c37490912ba5116c48a234`
- `comparisons/idler_mount_section.png`: `e8a6ac311e18b8fefb8cdd5854edc6e5e2796b258b2f48690881593ac5345cce`
- `comparisons/snl_longitudinal_overlay.png`: `e5753f4a3e829b4c88f1909720f27e4a52658bb214485ad544fc05319fe4d7e3`

Full saved-native qualification passes, including ten parameter trials. Snapshot 007 and idler/adjuster details preserve this partial stage. Complete-tank and historical-fit flags remain false.

## 20 September 2026 — lower support integration

Standard isometric shows continuous lower support runs, separate attachment heads, inclined front supports and the revised skirt border. Main enclosures/tracks remain coherently assembled. Layout machinery and incomplete fittings remain visible; this is not a complete tank.

The diagnostic crop exposes three inclined angle pairs against the front skirt; visible bolt heads and pin/clamp seats align with the revised lower border. The crop only removes viewing context and is not a pose.

Separate pin ends, U-bolts, washers and the first six complete roller units follow their paired inclined angles. The source transverse arrangement remains recognizable; exact flange sections and detachable retention remain unresolved.

The port bank shows paired inclined front pieces, separate level runs and the rear rising contour. This image shows 17 angles and 38 bolts; the heading quotes the whole-vehicle totals of 34 and 76. The source allocation of the final two rear roller outlines remains unresolved.

The rear close-up shows continuous cubic transitions between level pin seats and separate fasteners. Their contour and assignment to all six rear stations are inferred; the visual does not qualify historical retention or constant normal stock.

The blue source trace follows the lower front skirt below the support fittings more closely than the retained red coarse polygon. The transition beyond the reviewed front picks is explicitly inferred; the 6 mm installed nose setback is separate from the pixel trace.

Revised front skirts and owned attachment/pin openings remain visible in the plate-only assembly. Main enclosures, floors and apertures retain their arrangement. Middle/rear lower-edge profiles and local clearance breakouts remain approximate.

The underside retains separate floor plates and hollow side housings. Revised front skirts continue onto the older middle/rear outline; unmodeled structural angles, brackets and local lower-edge clearances remain visible limitations.

The foremost roller keeps its static idler/track clearance after its pin and clamp frame rotates onto the new inclined support. The view does not qualify continuous track engagement or adjustment travel.

Inspected raster SHA-256 values:

- `previews/isometric.png`: `123536379dc393e79d8572a9d0f1c578c231b0462666c03ebcbb369ef6aa7558`
- `comparisons/lower_support_front_in_hull.png`: `a075f2aab36ae0256702529358e43ca696f9d884b24f56a951eac2c3da8be710`
- `comparisons/lower_support_front.png`: `0b1de6f1e366e61cc0abf2d5d74843316260fe50f929e73724cf9c4541b87537`
- `comparisons/lower_support_bank.png`: `9ec0cebf9917ff02d375e5001c139f95624db5f29ecc2ee83f8663dcd059612a`
- `comparisons/lower_support_rear.png`: `eec85fe76aa97a53cb8de2dc4fcc129072e95285db16979a56ccaf5b31107150`
- `comparisons/lower_front_border_review.png`: `9e43aeec7f14e3144529177095205e3842444ddd5b3ea5b4c3f04579402ce99d`
- `comparisons/hull_oblique.png`: `e93bc70bce2f370049ae6d2847867750993ea2522b6e45ff1bcb11b524285ce1`
- `comparisons/hull_underside.png`: `2162cad5b75e4c1b2056656d8b56a1ae1ae2cf84c5fc28782f257b6b5c27669e`
- `comparisons/idler_installation.png`: `5c2e0c0cdc8f273da0afdc75f3e747b158e213172309fbfa2399c29faabd4c5a`

## 20 September 2026 — driving-wheel integration

The standard isometric exposes detailed rear drive wheels through the track openings. Paired aligned M1401 rings, six lightening openings, common bosses and formed diaphragm troughs follow the broad HB86, HB125 section and SNL27 construction. Exact sections and tooth profiles remain inferred.

The final negative-Y rim placement preserves the same groove phase on both rings. The first build reflected odd tooth phases and was rejected; a saved native phase regression now checks corresponding groove axes.

The drive section nests the common disks inside the rim lands and retains the flat central diaphragm trough. Common dimensions are shared by all four wheels; idler sections and adjustment hardware remain present after this change. Rivet-head land overhang, X/Y diaphragm distinctions and structural adequacy remain open.

Four installed drive rims have about 15.95 mm nearest track-bush clearance. This visible gap is retained and reported; static noninterference does not establish track engagement. Source-calibrated shaft axes and source image scales were not moved to close it.

The nominal 35-tooth reading follows HB130/HB133. The HB119 9:37 statement remains contradictory; the model exposes a 37-tooth sensitivity trial. The printed 39.237-inch OD, 32.75-inch ID and 2-inch tooth width remain controlled, with the ID-to-bore interpretation provisional.

Shaft assemblies currently contain two bushes each. Shafts, keys, end nuts, oil plugs and their bearing attachments are still absent from the delivered drive stage. The lower-support bank remains 17 angles and 38 bolts per side, 34 and 76 per vehicle.

Inspected raster SHA-256 values:

- `previews/isometric.png`: `040eea4a40408f37e55b384c9c4160289dee173f48ec181c9aba6dea333a89d6`
- `comparisons/drive_oblique.png`: `d150f4d4e33294c392aadb085cfb3e14a146debc0e2f456d50c17c45dcb3be1d`
- `comparisons/drive_section.png`: `df271134a01d7ef1409ba4d73f6de3a17bd76af9d106aa96ceff5ac8fc875a5e`
- `comparisons/drive_installation.png`: `ae0f1d0b65aacc191e7e302ec0a8c02699e99af3923856f93e54da47fa829980`
- `comparisons/drive_elevation.png`: `d0ef17690c08d5f656bcd534bc85c32a4d487199de7798cf79fbbd3157a54f30`
- `comparisons/idler_section.png`: `d82e6bfcce619b36c4ad614c143932c0c59e3be79913e6196bfcd46fc6278f5b`
- `comparisons/idler_installation.png`: `502eb072dc7f1ed6eba22b00f8137438818ac9cb5893396eac262250b3adb57f`
- `comparisons/lower_support_bank.png`: `44d4d4133cd7bce98f4501f5254e47f5d76a28c7b6dd9d2e684a1e3e20732a95`

## 20 September 2026 — driving shafts and bearings

The standard isometric shows the new external drive-bearing faces at the unchanged rear axes and the revised rear skirt border. The original camera and subsystem colors remain consistent with prior progression snapshots.

The shaft detail exposes separate inner/outer bearings, end nuts, locking plates, attachment fasteners and the oil fitting. The transverse section preserves the common wheel/bush stack and shows the axial/radial shaft oil passage.

HB Plate125 and86 support the support/nut/key/plug topology. Exact casting outlines, flange contours, locking-plate shape/orientation, threading, sealing and retention strength remain inferred or unqualified; the schematic CAD is not a metric match to the source artwork.

The source-identified receiver view shows the drive bearing seated in M1977 inside and M1975 outside. The inferred seam and lower-border reconstruction clears the complete bearing footprint; identity correction is supported separately by the SNL189/169/178 joint rows.

The opposed drive rims remain aligned. The unchanged visible track gap is retained, and no continuous track/roller-pinion engagement is claimed. The roller pinions and chains remain unpopulated.

The idler transverse section and lower-support bank retain their reviewed arrangement after the twelve rear-panel changes. Native interfaces pass in the nominal build; both additional parameter preflights now pass, including the full spacing-dependent hull/roller/support context.

The small Q52C head is not a qualified bolt shoulder. Native checks confirm only its 12 mm plain-envelope insertion and inferred0.2 mm radial gap; the rejected generic shoulder-seat assumption is preserved.

- `previews/isometric.png`: `7544be5660dde9e57c1386175eefb367ed12d062a66afe1c8ffd5e866913fbbe`
- `comparisons/drive_mount_detail.png`: `84d734370c5bd753c85f3d37e5714926b714e0632ab6d1ed23eb7af756321244`
- `comparisons/drive_mount_receivers.png`: `a0ce11e556ecdcfce986973c7357a4a7541249f1c8f7dd5d42416ed21ee04603`
- `comparisons/drive_oblique.png`: `81c3b41b5aabe69e3a997df99fc67f4ee199c908e2bb2cdfae7341ecc2b95cdc`
- `comparisons/drive_section.png`: `ec3d37cf5a603e1c5b4143e2c8c0dfa3dd46c1b93df16ae97743068966420fa7`
- `comparisons/drive_installation.png`: `42e23b7b9c31ab5c891acd1f215568caa5a50fbe87988b9bfbb89fb9a8082df3`
- `comparisons/idler_section.png`: `5d873909d7f6656c3f7ceaced0f84197da522289cc1badfb71501915f67e2607`
- `comparisons/lower_support_bank.png`: `10e9e4067750071eb5cb7d4c6305956fa272cad10c0f4847bb65771296f1a863`
