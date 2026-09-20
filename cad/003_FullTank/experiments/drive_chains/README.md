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
  three at the enlarged candidate. These are unresolved fit diagnostics.

The native probe accepts `--stage` pointing to the authored pinion experiment
and an optional `--output`. It does not modify that stage. The diagnostic
annuli exclude bars, pin ends, cotters, casing, transmission and all associated
clearances. Full inventory and historical-fit claims remain false.
