# Same material, more reliable rounded-window construction

The rejected housing used a rounded window tool made by uniting boxes and four
cylinders. STEP reopening increased maximum kernel tolerance from approximately
2.84e-7 to 3.13e-7 mm. Both material differences were zero; the original maximum-
tolerance rule still rejected the result. Full rejection receipts are retained.

Replacing that tool with a single planar wire of tangent lines and circular arcs,
extruded once, preserved material in both directions. The corrected housing
exports reopened at 1e-7 mm maximum tolerance. No fit or validation tolerance was
changed. Both cut-order trials passed; the adopted fix retains the original cut
order. `arc_prism.py` records the tested construction, and `result.json` its two
trials.

`check_saved_shapes.py` is a standalone comparison of the adjacent rejected and
corrected BReps/STEP files. From the repository root:

```sh
python3 skills/freecad-reconstruction/scripts/freecad_headless.py --workdir .work/replay-lower-housing cad/003_FullTank/experiments/drive_chains/engine_lower_drive_study/diagnostics/housing_window_prism/check_saved_shapes.py
```

The other scripts preserve the original experiment and its local working paths;
use the command above for a replay independent of those archived work directories.
`receiving_envelope.json` separately records why the estimated housing radius was
increased from 37 to 43 mm. It proves a necessary gear-passage condition, not a
complete casing-removal path.
