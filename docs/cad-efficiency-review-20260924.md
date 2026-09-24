# CAD workflow efficiency review — 24 September 2026

These recommendations preserve the full-tank scope and independent acceptance
checks. They do not authorize a general reduction in reasoning effort or turn
passing geometry checks into proof of historical accuracy.

## Evidence from the current work

The brake-stop revision now passes 55 mounting, 71 joint/ownership and 89 STEP
checks, with 490 unchanged definitions preserved. The STEP discrepancy was an
export representation issue: changing the writer's component representation
resolved it without changing the native geometry or loosening acceptance limits.
A fresh build exactly reproduced all archived BReps and persistent properties.
These results are retained in the
[trial04 qualification](../cad/003_FullTank/experiments/drive_chains/transmission_brake_stop_study/trial04/qualification.json).

Manual command orchestration, repeated context reads, cloned validation setup
and oversized output are avoidable costs. This turn included an unnecessarily
broad file listing and a whitespace check that printed generated STEP records.
Future source checks should target source extensions and report counts/failed
locations; generated exchange files retain their exact verified bytes.

## Recommended order

1. Automate the existing build, extraction, validation, export, rendering and
   report stages in a deterministic runner. Preserve source/visual review as an
   explicit judgment. Reuse the current controller's durable records and locks;
   its present shadow CLI packets do not orchestrate these real development
   checkpoints. Share orchestration helpers, not geometry construction logic
   between builders and independent validators.
2. Emit compact machine-generated status and recovery records. Report current
   parent/candidate hashes, terminal results, failed checks, unresolved source
   decisions and the next action. Full logs remain accessible. A recorded job
   handle is a pointer to poll, not evidence that the job is still running.
3. Reuse evidence only when the relevant native/BRep inputs, composed frames,
   checker code, numerical settings and runtime match. Separate definition-only
   checks from assembly-context checks. Placement or neighboring-geometry changes
   invalidate context checks even when the part's shape is unchanged. Existing
   whole-checkpoint and definition-pair caching are starting points; do not bypass
   required final integration checks through an unqualified cache.
4. Use a completion rule for documented approximations. Once source review,
   geometric interfaces, stated uncertainty and applicable checks are complete,
   record the disposition and proceed. Reopen it for new evidence, a contradiction
   or a changed interface. Unresolved identity/quantity decisions remain visible
   in inventory reconciliation; repeated speculation is not stronger evidence.
5. Measure cost through acceptance: tokens, elapsed time, repairs, failed runs
   and reviewer work. Trial lower effort only on bounded, explicitly reviewed
   implementations through the existing conservative routing. The
   [benchmark](../benchmarks/cad_work_packets/REPORT.md) has one paired run per
   task and missing usage for two timeouts; it cannot establish an aggregate
   token-cost ratio or justify a broad model/effort change.

The deterministic runner, compact status/recovery records, dependency-bound reuse,
decision ledger and approximation/reopening rule are now implemented. The
[real replay](../benchmarks/cad_pipeline/20260924/README.md) passed all 18 stages,
selectively reran one corrected comparison dependency, then reused all 18; its
geometry/properties exactly match the prior qualified trial. Eleven runner tests
cover failure, invalidation and recovery. The existing model-routing controller is
unchanged; no lower reasoning effort was adopted.

The [camera workflow](../tools/source_camera/README.md) now retains immutable fits,
native-bound landmark locations and independent holdouts. Controlled numerical,
native and raster tests pass; the first historical camera still needs a trusted
landmark review. Numerical fitting itself was milliseconds in the noise-free
control, so preserving source/landmark reasoning is likely the larger benefit.

Stage execution/reuse/failure metrics are recorded. End-to-end assistant token
cost and reviewer time remain unmeasured; no percentage saving is claimed.
