# Optional cleanup tolerance regression

On FreeCAD 1.1.1 / OCC 7.8.0, `removeSplitter()` returns a valid single-solid
case but increases maximum kernel tolerance from 5.100001e-6 to
1.01514198395e-4 mm at the screw-support/pump-bore/lug intersections. All 25
native checks, 261 material pairs and actual gear mesh/backlash had passed;
strict STEP acceptance rejected the native maximum tolerance. The builder now
retains the valid shape before cleanup. Physical dimensions and acceptance
limits are unchanged.

The frozen before/after BReps and STEP support a standalone material/STEP
replay. From the repository root, run:

```bash
python3 skills/freecad-reconstruction/scripts/freecad_headless.py \
  --workdir .work/receiver-cleanup-replay \
  cad/003_FullTank/experiments/drive_chains/engine_lower_drive_installation/diagnostics/cleanup_tolerance/check_saved_cleanup.py
```

Use a fresh work directory. The script imports the project's `case_joint_mass`,
configures the snap root, and compiles in the selected work directory's `mass`
subdirectory. The focused replay passes: both native material differences are
zero; the STEP exported before cleanup has maximum tolerance 1.27969e-7 mm
and passes the unchanged strict mass, centroid and material limits.
`standalone_replay.json` records the replay and frozen-input hashes.

The full rejected native and STEP files remain in the local archive
`.work/engine-distribution/receiver_cleanup_rejected`.
