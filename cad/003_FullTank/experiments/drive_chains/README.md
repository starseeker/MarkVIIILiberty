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

Native probes accept `--stage` pointing to the authored pinion experiment and
an optional `--output`. They do not modify that stage. The complete chain
candidate includes bars, bushes, pins and unsplayed cotters; the older circular
clearance probe contains only diagnostic annuli. Casing shells and their wall
attachments and cap cleats are now separate candidates. Beading, register plates,
support brackets, remaining fasteners, the transmission shaft, formed chain
retention and lubrication still need population. Full inventory, moving
engagement and historical-fit claims remain false.
