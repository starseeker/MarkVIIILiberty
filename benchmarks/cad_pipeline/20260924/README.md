# Brake-stop replay and selective reuse — 24 September 2026

The deterministic runner completed all 18 real development stages: native build,
extraction, independent part/interface/joint/context checks, preservation, STEP
exchange, rendering/comparison, independent rebuild, and parameter variation.
The replay matches the previously qualified trial04 exactly for 1,537 archived
BReps, 139,961 persistent properties and every object type. Archive container
hashes can differ while all these contents match.

| Invocation | Executed | Reused | Recorded stage execution time |
|---|---:|---:|---:|
| Initial replay | 18 | 0 | 872.17 s |
| Corrected comparison dependency | 1 | 17 | 0.21 s |
| Unchanged replay | 0 | 18 | 0 s |

The first manifest omitted the suspension report read by the source-comparison
stage. It was added after that invocation completed. The next invocation reran
only that stage; the third reused all 18. Read-only verification then found every
stage current. This documents a manifest correction, not a claim of automatic
complete dependency discovery.

These times exclude runtime probing, hashing and orchestration; they are not
end-to-end speedup measurements. Assistant token usage and reviewer time were not
measured. The runner invoked no model. Its 11 failure/reuse/locking tests passed.
No broad change of model or reasoning effort follows from this result.

[summary.json](summary.json) binds the plan, checker results and original/replay
native hashes. Invocation records retain per-stage evidence paths. Full run logs,
outputs and immutable attempts remain in `.work/cad-pipeline/brake_stop_pipeline01`.
The [pipeline README](../../../tools/cad_pipeline/README.md) gives recovery and
freshness commands. The original trial04 remains the retained reviewed artifact;
this replay does not promote its historical interpretation or modify standard tank011.
