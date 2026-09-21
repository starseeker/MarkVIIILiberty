# Drive-chain research and isolated native studies

These studies prepare the next drivetrain increment. They do not populate the
delivered assembly or reconcile the catalogue's chain component quantities.

- `source_rows.json` and `source_review.json` retain source records and inspected
  image hashes. HB130 directly documents 12 driving-sprocket teeth.
- `pitch_route_probe.py` tests discrete 50-pitch closure and a literal 25-axis
  interpretation. `installed_pitch_route_probe.py` aligns the 50-pitch route
  with the existing roller-pinion relief phase.
- [Source overlay](route_comparison.html) compares that mathematical candidate
  with unchanged SNL Plate2 pixels. It was browser-rendered and inspected.
- `roller_clearance_probe.py` tests the source-sized roller envelopes against
  the casting. `roller_clearance_build/report.json` and the saved/reopened
  native fixtures retain both failed cases: 16 overlaps at the current relief,
  three at the enlarged candidate. These failed circular-pocket cases remain
  preserved even after the later tangent-flank candidate passes.
- `flank_clearance_probe.py` and `sprocket_geometry.py` test repeated root seats
  and tangent straight flanks. The selected 20-degree candidate preserves a
  0.25 mm static roller gap. Its profile is a reconstruction assumption.
- `build_chain_candidate.py`, `chain_parts.py` and the explicit controls create
  a saved/reopened 252-leaf native fixture: 250 chain components and two sprockets.
  All 443 candidate material pairs pass; bar/pin/cotter details remain partial.
- `installed_chain_probe.py` places both handed chains against the current tank.
  Its 504 new leaves replace two existing castings for comparison. The 886 internal
  and 260 external candidate pairs have 18 overlaps, all with the provisional
  M2003 engine-room back plate. This failed installation is retained.
- `casing_passage_probe.py` independently tests an M2003 opening hypothesis.
  HB134's casing width and SNL60/170's M1592-to-M2003 connection motivate the
  passages. The reopened 505-leaf fixture passes 904 internal and 255 external
  candidate pairs with zero overlap; the existing 77-plate hull checks also
  pass. The detailed opening shape and clearances remain inferred. Later
  studies below check the actual casing bodies and wall attachments.
- `casing_source_rows.json` identifies the body/cap assemblies and their named
  components. `casing_joint_review.json` preserves newly inspected cap-bolt
  allocations and conflicts between nested rivet counts and joint tables.
- `casing_parts.py` and `casing_shell_probe.py` build separate M1590 bodies and
  M1591 caps. The initial `casing_shell_build` retains two 21.609290 mm³ wall-corner
  overlaps and its exact input snapshot. Its original half-section raster has
  a documented rendering error and must not be used as geometry evidence.
- `casing_shell_passage_build` uses the actual casing section to enlarge the
  inferred wall openings. Its 509-leaf fixture passes 638 casing-related material
  pairs, with 2.304985 mm minimum wall clearance and 2 mm hub clearance. The
  corrected [half section](casing_shell_passage_build/casing_half_section.png)
  was inspected. The cap seam and detailed shell contour remain inferred.
- `casing_wall_mount_probe.py` adds two M1592 angles, 22 wall rivets and 34 casing
  rivets to the fixture. Its 567 reopened leaves pass 697 new/changed material
  candidate pairs, 56 receiving bores and 56 two-receiver seating checks.
  The [attachment detail](casing_wall_mount_build/wall_joint_detail.png) was
  inspected. Angle form, section and hole pattern remain explicit assumptions.
- `casing_cap_parts.py` and `casing_cap_probe.py` add 94 leaves: eight M1583 side
  cleats, four M1593 roof cleats, four M1584 packing strips, 36 cleat rivets and
  fourteen separate bolt/nut/lock-washer sets. Original SNL128/270 inspection
  supports the separate nut and washer identities; SNL31 supplies the set count.
  `casing_cap_build` preserves a rejected centered roof-rivet pattern with four
  bolt/nut intersections. Its exact inputs and inspected images are retained.
- `casing_cap_clearance_build` offsets the middle roof rivet by an inferred
  24 mm. Its 661 saved/reopened leaves pass 914 new/changed material pairs,
  50 receiving bores, 50 seating checks and 14 fastener-envelope retention
  checks. The [joint detail](casing_cap_clearance_build/cap_joint_detail.png)
  was inspected. Detailed threads, spring action and clamp loads are unqualified.
- `casing_cap_packing_build` supersedes that candidate's packing location.
  Original HB185 explicitly puts M1584 under the cleats. The revised strips sit
  between each body side-cleat foot and the sheet; mating flanges meet directly.
  Its 661 leaves pass 914 material pairs, 50 bores, 50 seats, 14 retention checks
  and four packing-contact checks. Earlier passing geometry is retained as a
  rejected source interpretation, not promoted as the current reconstruction.
- `casing_trim_parts.py` and `casing_trim_probe.py` add eight register plates,
  eight beading strips, 32 button rivets and 40 countersunk rivets. The 749-leaf
  `casing_trim_build` passes 1,088 material pairs, 72 bores, 72 seats, eight lap
  contacts and 40 flush-head checks. Its [native rivet section](casing_trim_build/beading_rivet_section.png)
  and inner/outer views were inspected. Profiles and exact edge assignments are
  inferred. `casing_trim_sources.json` retains the HB M1586 alternative and the
  SNL global/nested beading-rivet quantity conflict.
- `casing_support_probe.py` adds four M1587/M1588 brackets, 28 case rivets and
  eight assumed three-part hull fastening sets. Four drilled hull receivers
  join the isolated fixture. Its 809 reopened leaves pass 920 material pairs,
  36 bores, 36 fastener seats, four bracket contact checks and eight retention
  checks; existing 77-plate hull validation also passes. The
  [support installation crop](casing_support_build/casing_support_detail.png)
  was inspected. Bracket forms and hull bolt size/count/placement are assumptions.
- `audit_casing_inventory.py` independently reads saved native link ownership.
  The fixture contains 300 selected casing occurrences, including 42 named
  components across all twelve selected SNL casing marks. The audit reports
  actual hardware counts and retains every known quantity/identity conflict;
  it does not declare historical inventory reconciliation or standard promotion.
- `chain_detail_probe.py` forms 100 split-pin tails and drills 400 inferred oil
  passages through the 200 link-bar occurrences. The saved/reopened 809-leaf
  fixture passes 274 new material pairs, 100 cotter capture checks, 100 pin
  retention checks, 400 oil-to-journal paths and 200 orientation checks. Unformed
  cotters and undrilled bars supply negative controls. HB24/132/134 establish the
  functional features and split-pin size; passage dimensions and tail form remain
  assumptions. The [joint detail](chain_detail_build/chain_joint_detail.png) and
  [bar-aligned oil section](chain_detail_build/oil_sections/inner_bar_oil_section.png)
  were inspected. `inspect_chain_oil_sections.py` supplies separate local sections
  because the joint overview cuts obliquely across the individual oil passages.
- `transmission_output_probe.py` adds two M289 output shafts and two M292 brake
  drums. HB122 and SNL215 distinguish M289 from the central M255 cross shaft.
  A conditional scale from HB132's four-inch sprocket hub controls the adjoining
  proportions. The [native/source overlay](transmission_output_build/source_section_overlay.png)
  was inspected. Four spline fits and two hub seats pass, but the 813-leaf
  candidate retains two 23,938.321999 mm³ drum/casing clashes.
- `casing_front_probe.py` tests a symmetric small-end taper from the retained
  168.275 mm maximum width to an inferred 132 mm. The 813-leaf candidate passes
  764 material pairs, eight three-mm normal sheet-thickness witnesses and both
  chain/drum clearance checks. Its [native section](casing_front_build/casing_output_plan_section.png)
  was inspected. The rear attachment region is geometrically unchanged. The
  taper and stations are assumptions; the earlier failed candidate is preserved.

- `transmission_bush_probe.py` adds two M296 inner sleeves, two M299 outer sleeves,
  four separate M300 bronze dowels and four M290 retaining rings to the saved
  casing/output fixture. The two shared M289 shafts gain inferred grooves and
  blind dowel pockets. All 825 reopened leaves are valid single solids; 26
  changed/new material pairs have no overlap. Four journal-clearance, four
  dowel-capture and four bidirectional ring-capture checks pass, including
  undrilled/ungrooved controls. The
  [axial section](transmission_bush_build/output_bush_section.png) and
  [source overlay](transmission_bush_build/source_bush_overlay.png) were inspected.
- `qualify_output_bush_interfaces.py` independently reopens that fixture and
  checks all four sprocket/drum spline interfaces. The engagement regions have
  zero material difference from the original shafts; clearances and twist
  capture remain valid. This is separate from complete axial-stack retention.
- `transmission_support_research.json` records inspected fixed-bracket/cap source
  lists. SNL309 requires poured babbitt; HB209 separately names brasses and shims.
  Their relationship remains open. The M391 foot schedule conflicts (four nested,
  two standalone); cap wool waste is a mass quantity, not a count of two parts.
  These questions remain explicit for the next fixed-support increment.
- `transmission_support_probe.py` now constructs two each M293/M297 brackets,
  M294/M298 caps, four common M295 oil-box lids and eight separate poured-lining
  half regions. The latest `transmission_support_clearance_build` has 845 valid
  reopened solids and retains all 825 prior occurrence signatures. Four local
  bearing fits pass, and all twenty additions survive STEP export/reimport.
  **The installation is rejected for integration:** each outer bracket meets
  the casing wall and one wall-angle rivet. Seventy material candidate pairs
  yield four overlaps. See the [interference view](transmission_support_clearance_build/support_interference.png)
  and [source overlay](transmission_support_clearance_build/source_support_overlay.png).
  Two earlier native trials preserve a lid/cap overlap and a touching lid-seat
  edge; the latest adds a flat seat with perimeter clearance. Six latest rasters
  were inspected. The bracket vertical profiles remain provisional.
- `transmission_frame_research.json` records inspected SNL96/97 frame members and
  HB/SNL orientation evidence. The next study must reconstruct the top/bottom
  channels, angles and gussets, then resolve the bracket/casing relationship.
  Source drawings support aft-facing feet and upward-opening cups; no unsupported
  casing opening or bracket rotation is used to force the candidate to pass.

Native probes accept `--stage` pointing to the current standard model or its
byte-identical authored pinion origin and
an optional `--output`. They do not modify that stage. The complete chain
candidate includes bars, bushes, pins and initially unsplayed cotters; the detail
candidate adds formed tails and oil passages. The older circular
clearance probe contains only diagnostic annuli. Casing shells and their wall
attachments, cap cleats, beading, register plates and supports are now separate
candidates. Partial output shafts and brake drums now have a tested static
interface. Shaft sleeves, dowels and groove-seated rings pass their local checks.
Fixed bearing housings/lining are now modeled in a candidate needing interface
revision. Source reconciliation, frame attachment and complete axial retention,
brake bands, lubrication performance and full-model integration/parameter
qualification remain. Full
inventory, moving engagement and historical-fit claims remain false.

The subsequent `transmission_frame_probe.py` study adds fifteen separate frame
members and revises the four bracket webs. The first `transmission_frame_build`
has nineteen interferences and is retained as rejected evidence. The revised
[frame candidate](transmission_frame_clearance_build/TransmissionFrameCandidate.FCStd)
has 860 valid leaves, 126 material pairs without overlap and 34 passing contact/gap
checks; 841 earlier occurrences are unchanged. Five rasters were inspected.
The source comparisons distinguish projected mounting pads from the actual
shaft-height section. Outside angles are now at the frame ends, overriding the
earlier generic controls wording about bearing stations.

This is only a nominal fit: the outer casing gap is 0.236 mm and nearby assumed
stem shapes collide. `check_transmission_frame_sensitivity.py` preserves those
negative witnesses and rechecks four bearing interfaces; its expected outcomes
pass, but parameter-envelope and historical qualification remain false. The
5.806-mm inner pad/channel gap still needs an evidenced attachment. Main/additional
fiber packers are recorded in `transmission_mounting_research.json`; their source
quantity conflict and unknown receiver prevent treating them as this gap's filler.
Frame rivets/bolts, hull mounting, brake attachments and central bevel case remain
pending. Main standard 011 is unchanged.

`transmission_lid_probe.py` continues from that saved frame. The latest
`transmission_lid_clearance_build` has 864 valid leaves, adding four source-size
steel pins and integral hinge features on four caps and four covers. The other
852 occurrences are unchanged. Thirty new/changed material pairs, four static
hinge/retained-bearing checks and twelve-solid STEP reopening pass. The rejected
`transmission_lid_build` preserves four cup-rim interferences with the lower
hinge-axis assumption. Covers remain closed; pin retention and motion are not
qualified. See the [cap detail and handbook comparison](transmission_lid_clearance_build/hinge_review/source_hinge_detail.png).

Pin dimensions use exact cylindrical surfaces and volume, not tessellation-cached
bounding widths. The new material filter removes display triangulation first.
`check_transmission_frame_bounds.py` independently rechecks all nineteen earlier
frame/bracket changes with cleaned bounds: the same 126 pairs, no new overlap.
`transmission_stud_research.json` records the physical stud identities, nuts and
split pins from original SNL241/124. Bare stud identities differ from nested stud
assembly identities. The existing estimated ear depths cannot override the
printed 3⅝-, 4⅞- and 5½-inch stud lengths. Cap fastening and lubrication are next.

`transmission_stud_probe.py` now installs those sixteen studs, sixteen castle
nuts and sixteen formed split pins in fixed-bearing subassemblies. The latest
`transmission_stud_clearance_build` has 912 valid leaves, with eight changed
receiving castings and 856 unchanged earlier occurrences. All sixteen fastening
checks, four retained bearing/hinge checks and the 56-solid STEP reopening pass;
262 material candidate pairs have no overlap. The preserved first trial has two
small port cotter-eye/casing overlaps. Rotating the port pins about the stud axes
points their eyes outboard and clears those overlaps.

The printed stud lengths constrain inferred blind bosses and spotfaced nut
seats. Threads remain cylindrical envelopes, and nut dimensions and split-pin
form are estimates. `check_transmission_stud_allocation.py` swaps MX10/MX36
between the inner upper/lower corners: its 41 candidate pairs also clear.
Neither feasible arrangement establishes the historical allocation. See the
[source comparison](transmission_stud_clearance_build/source_review/source_fastener_detail.png)
and candidate `visual_review.json` for the remaining visible discrepancies.

`transmission_oil_fitting_research.json` records the next SH664A elbow, SH664B nut
and SH664C sleeve inventory. Original SNL67 also lists a distinct A16323 brass
collet; its relationship to the sleeve is unresolved. Complete lubrication,
frame attachment, the central transmission and integration remain open.

`transmission_oil_probe.py` now populates one SH664A elbow, SH664B nut and SH664C
sleeve per cap, plus four separate porous wool volumes and low galleries through
the caps/front linings. `transmission_oil_build` reopens with 928 valid solids:
twelve new fittings, four material envelopes, eight changed cap/lining
occurrences and 904 unchanged prior occurrences. Its 104 material pairs have no
overlap. Four fitting/passage checks, four retained interface checks and the
24-solid STEP reopening pass. All sixteen existing nut seats and their protected
cap material remain unchanged.

The local [fitting section](transmission_oil_build/oil_fitting_section.png) and
[bearing section](transmission_oil_build/bearing_oil_section.png) expose the
inferred connection. The [handbook comparison](transmission_oil_build/source_review/source_oil_detail.png)
records the remaining rounded-casting and upper-opening differences. Original
SNL261/262 supplies the explicit ¼-inch tube outside diameter; original SNL274
confirms eight ounces of wool total, represented as four two-ounce material
envelopes rather than eight discrete parts. The packing conforms to cap hinge
intrusions. Thread form, sealing, full feed lines and oil performance remain
unqualified. All source rows, assumptions and exact build inputs accompany the
native candidate; no new standard milestone has been promoted.

`check_transmission_oil_gallery.py` adds twelve local trials. Nominal, height and
bore variations retain the specified 1-mm wall and open route; the two lowered
negative cases miss the reservoir. All expected outcomes pass. The test bounds
are diagnostic assumptions, with historical route and whole-assembly parameter
qualification still open.

`transmission_core_probe.py` adds eleven major central parts to that fixture:
the M263/M264 bevel case and cover, M255 cross shaft, and two each M278/M277
case halves, M286 carriers and M269 high-speed drums. The
[saved native candidate](transmission_core_build/TransmissionCoreCandidate.FCStd)
has 939 valid single-solid leaves, with all 928 earlier occurrences unchanged.
Thirty-three material pairs have no overlap; nine specified interface checks
pass, with five additional diagnostic distances recorded. Eleven new solids
pass STEP roundtrip. Twelve local source-trace/phase/end-position trials have
their expected outcomes, including deliberate collision cases.

The [oblique view](transmission_core_build/transmission_core_oblique.png),
[cutaway](transmission_core_build/core_horizontal_cutaway.png),
[Plate22 overlay](transmission_core_build/source_plate22_overlay.png) and
[Plate23 comparison](transmission_core_build/source_review/source_plate23_overlay.png)
were actually inspected. The latter records a visible mounting-plane mismatch;
input centering differs by about32mm between the local Plate22 projection and
the assumed tank centerline. Printed M269 diameter381mm is retained despite a
larger scaled scan extent. Gears, bearings, brake bands, joint hardware and full
lubrication remain open. This remains an isolated partial reconstruction; see
the [central transmission packet](../../packets/I03-transmission-core.md).

`transmission_planet_probe.py` extends that fixture with the paired large
planetary trains and retention: eighteen new occurrences, five revised case/shaft
occurrences and 934 unchanged components. The
[saved native candidate](transmission_planet_build/TransmissionPlanetCandidate.FCStd)
contains 957 valid solids. All 110 material candidate pairs are clear; 24
specified interface checks, ten native gear-tooth counts and six planet mesh
checks pass. All 23 new/changed solids survive STEP roundtrip.

The [gear detail](transmission_planet_build/large_gears_oblique.png),
[cutaway](transmission_planet_build/transmission_gear_cutaway.png) and
[source comparison](transmission_planet_build/source_review/source_detail.png)
were inspected. HB126 supplies 18/27/72 teeth at 4–5 DP; pressure angle, root
form, backlash, axial details and enlarged case seats remain approximations.
The comparison records a 5.129 mm axial station discrepancy and a substantial
sun-outline difference. `check_transmission_planets.py` confirms 28 expected
local outcomes, including deliberately incorrect tooth phases and axial stops.
These do not qualify historical fits, full motion or the uncertainty envelope.
See the [large-gear packet](../../packets/I03-large-planetary-gears.md) for source
identities, remaining pin/bush work and reproduction commands.

`transmission_pin_probe.py` adds 56 pin, bush, sleeve, ring and fastening
occurrences from ten source identities. The
[saved candidate](transmission_pin_build/TransmissionPinCandidate.FCStd) has
1,013 valid solids; two carriers change and 955 prior occurrences are unchanged.
The carrier nuts sit in source-scaled recessed seats. All 332 material candidate
pairs are clear and 108 specified interface checks pass. All 58 exported solids
have empty native/STEP material differences; mass-property deltas remain recorded.

`check_transmission_pins.py` confirms 50 expected retention failures, six axis
alignments, four hardware sizes and 11 deliberate export-displacement failures.
The [pin-axis section](transmission_pin_build/source_review/pin_axis_section.png)
and [source comparison](transmission_pin_build/source_review/source_pin_comparison.png)
expose the bearing stack and the unresolved source radial discrepancies. The
ring-bolt position requires a carrier-rim/pin-ring review before integration.
See the [support packet](../../packets/I03-large-planet-supports.md) for source
corrections, bush identity conflict, approximations and reproduction commands.

The subsequent [ring-support revision](transmission_ring_support_build/TransmissionRingSupportCandidate.FCStd)
corrects the M318 source feature and station. Callout15 identifies the inner
bolt; the prior comparison used an unrelated outer case-joint bolt. Twenty-two
occurrences change, with 991 retained unchanged in the 1,013-solid fixture.
All 166 material pairs, 108 interfaces and 22 STEP material comparisons pass.
Fifty local access/stop trials, six radius/diameter checks and five deliberate
STEP displacement checks pass. The
[source comparison](transmission_ring_support_build/source_review/source_pin_comparison.png)
and [bolt section](transmission_ring_support_build/source_review/bolt_axis_section.png)
show the corrected station and inferred recessed receivers. See the
[revision packet](../../packets/I03-ring-bolt-station.md); exact cast contours,
case fastening, small gears and central bevel/input work remain open.

The preceding [small planetary candidate](transmission_small_build/TransmissionSmallCandidate.FCStd)
adds 46 occurrences: both small gear sets, separate sun bushes, input disks,
rings and 32 rivets. One cross shaft receives smooth sun-bush journals, while
1,012 earlier occurrences remain unchanged. All 166 material candidate pairs,
182 interfaces, ten native tooth counts, six gear meshes and 47 STEP material
comparisons pass. Thirty local trials, eight native dimension checks and seven
intentional STEP-displacement checks also pass. The [small-train packet](../../packets/I03-small-planetary-gears.md)
records the inferred 24-tooth planets, printed M276 row conflict and open source
profile discrepancies. The [source comparison](transmission_small_build/source_review/small_train_comparison.png)
and [combined cutaway](transmission_small_build/source_review/coupled_trains_cutaway.png)
show how the new gears fit the retained assembly; small supports, brake bearings,
retention and standard integration remain unfinished.

The preceding [small-support candidate](transmission_small_support_build/TransmissionSmallSupportCandidate.FCStd)
adds 56 support occurrences and revises 38 case/disk/ring/rivet occurrences.
It contains 1,115 valid solids. All 416 material pairs, 296 interfaces, six gear
meshes, ten tooth counts and 94 bounded native/STEP material comparisons pass.
Independent retention, dimension, shared-definition and deliberate export-offset
checks also pass. The [source comparison](transmission_small_support_build/source_review/small_train_comparison.png)
shows the cubic swept disk and source-positioned rivets alongside the new
planet-pin and ring-bolt supports. The [packet](../../packets/I03-small-planet-supports.md)
records the source discrepancies, flat rivet-seat correction and limits.
Brake bearings/retention, central bevel/input and standard integration remain open.

The preceding [sun-retention candidate](transmission_sun_retention_build/TransmissionSunRetentionCandidate.FCStd)
adds the two M290 rings assigned to the small sun pinions. All six catalogue
rings now share one definition. Four sleeve/drum occurrences receive complete
groove collars, smooth shoulders and counterbores; 1,111 earlier occurrences
remain unchanged in the 1,117-solid fixture. All 30 affected material pairs,
300 interfaces, 12 capture trials and six native/STEP comparisons pass.
Independent checks confirm eight capture directions, 20 radii, ring stations,
definition reuse and three deliberate export-displacement failures.

The [section comparison](transmission_sun_retention_build/source_review/sun_retention_comparison.png)
and [work packet](../../packets/I03-sun-retention.md) preserve the inferred fits
and unresolved cap/bush ownership. `transmission_brake_bearing_research.json`
records the next M265/M266/M300 source interpretation. The split angle is assumed,
elastic installation is unqualified, and standard tank 011 remains unchanged.

The preceding [bevel-support candidate](transmission_bevel_sleeve_build/TransmissionBevelSleeveCandidate.FCStd)
adds twelve M259/M261/M262/M310/screw/M300 occurrences and revises seven
shaft/case/cover/sun/bush occurrences. The 1,129-solid fixture passes 117 affected
material pairs, 326 interfaces and nineteen native/STEP material comparisons.
An independent checker passes 83 dimension, passage, capture, source-station,
shaft-section and deliberate-failure checks.

The earlier root-diameter bush trial had static clearance but no spline passage.
Larger journals and corresponding bores correct that limitation, with a larger
central spline reserving a future clutch interface. The [comparison](transmission_bevel_sleeve_build/source_review/bevel_support_comparison.png)
shows the unresolved 32.113 mm source-datum conflict. The [packet](../../packets/I03-bevel-sleeve-supports.md)
retains exact approximations and the 31.387 mm sleeve-end gap. Six inspected
images show the supports and stepped shaft. Complete bevel gears, clutch,
shims, brake bearing, remaining fastening and standard integration remain open.

The latest [bevel-drive candidate](transmission_bevel_gear_build/TransmissionBevelGearCandidate.FCStd)
adds 70 leaves for 46-tooth wheels, 14-tooth input pinion, four-dog clutch, clutch
rings, 24 rivets, shims and two thrust-bearing assemblies. It revises 13 earlier
support/shaft/case leaves and retains 1,116 unchanged, totaling 1,199. The printed
105 × 155 × 40 mm bearing envelope constrains the axial stack; its internal 19
parts per bearing are inferred and count as two catalogue assemblies.

All 458 material pairs, 497 interfaces, 83 STEP material comparisons and 109
independent checks pass. The [source comparison](transmission_bevel_gear_build/source_review/bevel_drive_comparison.png)
retains both axial registrations and their 32.113 mm discrepancy. The old sleeve
gap is superseded by a 0.2 mm fit to the sun datum. The
[packet](../../packets/I03-bevel-drive.md) records assumptions, rejected rivet/cage
trials and remaining input/brake/fastening/control/lubrication work. Standard
integration and the complete tank remain unfinished.

- The latest [input assembly](transmission_input_build/TransmissionInputCandidate.FCStd)
  adds88 source-linked/inferred leaves: opposed Timken bearings, M250 housing,
  M246 coupling, packing/gland, spacer/shims and retaining/gland hardware.
  Its1,287 leaves pass749 material pairs,578 interfaces,90 STEP comparisons
  and181 independent checks. Six inspected rasters retain both source scales.
  The [packet](../../packets/I03-input-assembly.md) records quantity conflicts,
  corrected insertion passages and Plate22 detached-coupling interpretation.
  Housing attachments, controls, lubrication and integration remain open.

- The current [input installation](transmission_input_installation_build/TransmissionInputInstallationCandidate.FCStd)
  adds sixteen leaves for four MX25 sets and the hollow grease-cup feed.
  It revises nineteen receivers/spacer/shim occurrences and repairs seventeen
  older cotter occurrences. The 1,303-solid candidate passes 653 affected
  material pairs, 52 STEP comparisons, 344 independent checks and four local
  parameter trials. Seven inspected views include the source overlay and both
  repaired pin forms. The [packet](../../packets/I03-input-installation.md)
  records the source conflicts and constituent-loss defect; use the
  [combined qualification](transmission_input_installation_build/qualification.json)
  for the completed review status. Standard integration remains pending.

- `transmission_brake_bearing_probe.py` extends the input-installation candidate
  to1,321 solids with paired M265/M266 supports, two shared M300 dowels and four
  MX14 sets. Rear saddles and common journals are documented hypotheses.153
  affected material pairs,21 exact-material STEP comparisons,109 independent
  checks and four local trials pass. Seven source-review views and the
  [packet](../../packets/I03-brake-bearings.md) retain the casting/registration
  uncertainties and conflicting MX14 lengths. Use its `qualification.json` for
  combined status; its builder report remains immutable.

- `transmission_reversing_probe.py` extends the qualified case-joint candidate
  to 1,372 solids with M301 fork, M302 rod assembly and M307–M309 detent.
  It corrects the continuous clutch groove and both ring-dog free tips, and
  adds bounded case receivers. All 168 affected material pairs, 11 STEP
  comparisons, 63 independent checks and three local trials pass. Six inspected
  views compare the widened fork arm against SNL23 and expose the spring/cap
  section. The [packet](../../packets/I03-reversing-controls.md) records source
  counts, inferred dimensions and the spring-envelope checking correction.
  Use `transmission_reversing_build/qualification.json` for combined status.
  M303–M306 vertical linkage, its two MX11 and two MX12 sets, mounts, pump,
  brakes, lubrication and standard integration remain pending.
