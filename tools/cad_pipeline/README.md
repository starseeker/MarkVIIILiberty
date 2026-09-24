# Deterministic CAD development pipeline

Run existing builders and independent validators as a declared sequence. This
runner invokes no model and never promotes a candidate. Source interpretation,
visual review, approximation disposition and final integration remain explicit.
It shares orchestration helpers with `tools/cad_packets`, not builder geometry
with independent checkers; existing model-routing benchmarks are unchanged.

From the repository root:

```sh
python3 tools/cad_pipeline/pipeline.py run tools/cad_pipeline/plans/brake_stop_replay.json --id brake_stop_pipeline01
python3 tools/cad_pipeline/pipeline.py status brake_stop_pipeline01
python3 tools/cad_pipeline/pipeline.py verify brake_stop_pipeline01
python3 tools/cad_pipeline/test_pipeline.py
```

Use a fresh ID for changed native builder inputs. Repeating an unchanged run
reuses passed stages only if their inputs, code, runtime, outputs and declared
receipt assertions still match. A changed reentrant checker reruns with prior
outputs preserved. An altered/unfinished immutable builder refuses reuse and
requires a fresh ID; there is no automatic adoption of untracked outputs.

`status` checks the actual worker lock and summarizes saved results. It does not
revalidate evidence. `verify` hashes current dependencies/outputs and checks
receipts without running CAD. Its runtime audit covers declared binary hashes,
resolved aliases and the host Python version; it does not re-execute the stored
numerical-package version probe. `run` re-probes that actual headless stack before
any reuse, so use it after package/system updates. Do not restart a live worker after a controller
interruption: its inherited kernel lock prevents duplicate work. Once that lock
is released, a missing terminal receipt remains unfinished, not a pass.

## Plan contract

Version 1 plans use `mode: local_development`, a stable plan `id`, and ordered
`stages` with `id`, `needs`, argv `command`, `inputs`, `outputs`, `reentrant`, and
`timeout_seconds`. Paths support `{root}`, `{run}`, `{python}`. Outputs stay within
the run directory. Inputs and outputs must be regular files, not symlinks/hardlinks.
Runtime aliases such as snap `current` are resolved and their targets hashed.

`python_sources` plus plan `python_paths` identify the static local import closure.
**Audit dynamic imports, data files, BRep references, external helpers, numerical
settings and environment variables explicitly.** AST discovery cannot establish
all dependencies. Broad dependencies may cause extra reruns; missing dependencies
can cause incorrect reuse. The brake-stop replay manifest is an audited example,
not a generic automatic dependency detector. Avoid globbing unrelated generations.

Bind independent checker receipts to both a true success flag and the candidate
native hash. JSON-pointer checks distinguish `true` from `1`. Zero process exit
alone is insufficient where a checker supplies a structured result. The runner
rechecks declared inputs after execution and rejects changes during a stage.
Plans are loaded once at invocation start; edits take effect on the next run.

Records, full logs, attempts and invocation metrics live under
`.work/cad-pipeline/<id>/records`. `state.json` is the compact recovery pointer;
`latest.json` per stage points to evidence. Preserve these with promoted review
bundles; `.work` alone is not a final deliverable. Hash checks protect accidental
staleness, not an adversary who rewrites code and all records together.

## Cost and routing

Metrics count executions, reuse, failure and recorded stage execution time.
Previously spent execution time is a useful workload measure, **not a measured
end-to-end speedup**: hashing, runtime probes and orchestration still take time.
The runner's model invocation count is zero; the supervising assistant's token
usage is **unmeasured**, not zero. Include failed runs and review/repair work in
future acceptance-cost comparisons. Continue using the conservative reviewed
packet routing in `tools/cad_packets`; do not reduce reasoning effort for new
mechanisms, source conflicts, spatial interpretation or acceptance decisions.

## Deliberate limits

Plans are trusted project code, not a security sandbox. Dependencies on current
placements/neighbors must be declared for context checks. Definition-only results
do not qualify installation. The current replay covers local brake-stop checks,
rebuild and parameter variation, but it does not accept historical part aliases,
verify complete service paths, reconcile the tank inventory or release the full
standard assembly. Final integration checks remain required.
