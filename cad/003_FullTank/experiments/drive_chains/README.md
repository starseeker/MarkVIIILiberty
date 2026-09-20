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
