# Resumable delivery validation

Run `python3 cad/003_FullTank/tools/resume_validation.py` from the repository.
The current worker's 27 stages include its nominal geometry checks, STEP round
trips, relocation, independent rebuild/cache checks and 15 parameter trials.
Three newly completed stages end a worker cleanly; the coordinator starts the
next worker. Re-run the same command after an interrupted coordinator.

Completed stages are reused only when their authored inputs, runtime versions,
nominal native hashes, runner code and exact output file sets still match.
Failed or interrupted stages have no successful receipt and run again. The
original worker is wrapped in memory; every original check expression is
retained, and the transformed source and audit are saved with the checkpoints.
The runner rejects an unrecognized stage structure instead of silently omitting
new checks. Geometry, source data and the nominal build are not edited.

Checkpoints and the durable coordinator log/status live in
`build/verification/checkpoints` and `build/verification/runs`. Successful final
validation adds `reports/resumable_validation.json` and regenerates the delivery
manifest. Partial directories alone are never evidence of a completed check.

Regression checks: `python3 -m unittest discover -s cad/003_FullTank/tools -p 'test_*.py' -v`.
