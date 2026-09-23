# Completed screen comparisons reused without changing acceptance limits

The original 35-part study completed its four strict screen-definition checks.
The saved native/STEP BRep inputs to those comparisons are preserved here with
the completed per-part results and source file/checker hashes. The source run's
whole-assembly completion is a separate state; no unfinished comparison is used.

The current candidate's four definitions and four occurrences match those exact
geometry pairs. Each installed screen has an identity definition placement,
identity composed parent/link placement and unit link scale. The checker rejects
other placements/scales instead of canonicalizing them. At identity placement,
the saved definition is the installed geometry, so no OCC copy is necessary.
A prior diagnostic showed that copying these shapes changes BRep bookkeeping
bytes; that mismatch by itself was not accepted as reusable evidence.

The combined `exchange_checks.json` binds the actual native document and both
STEP files. It accounts for every definition and occurrence exactly once:
135 direct strict comparisons plus eight exact-pair reuses. Changes to either
member of a pair, an unpassed source comparison or a nonidentity pose are
negative controls. No volume, centroid, tolerance or material acceptance limit
has been widened.

To reproduce this proof from the repository root:

```bash
python3 cad/003_FullTank/experiments/drive_chains/check_engine_oil_pump_screen_reuse.py --candidate cad/003_FullTank/experiments/drive_chains/engine_oil_pump_relief_lock_study --reference cad/003_FullTank/experiments/drive_chains/engine_oil_pump_development
```

That command currently uses the original run's `exchange_progress.json` and
`exchange_runtime/mass` files to establish the reference. The frozen evidence
here preserves the result for review, but is not yet a standalone cache loader.
The ordinary full checker remains available when those runtime inputs are absent.
This is a scoped reuse mechanism for the current unchanged screens, not a general
replacement for STEP or assembly validation.
