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
  passages. Their detailed shape and clearances remain inferred; consult the
  separate controls and native report before accepting any result.

Native probes accept `--stage` pointing to the authored pinion experiment and
an optional `--output`. They do not modify that stage. The complete chain
candidate includes bars, bushes, pins and unsplayed cotters; the older circular
clearance probe contains only diagnostic annuli. The casing, transmission shaft,
formed retention and lubrication remain unpopulated. Full inventory, moving
engagement and historical-fit claims remain false.
