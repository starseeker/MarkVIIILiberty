# CAD reasoning CLI pilot

This benchmark compares GPT-6 Astra at medium, high and xhigh effort on three
bounded tasks drawn from the Mark VIII reconstruction. It is a pilot for choosing
where to spend reasoning effort, not qualification of a cheaper production model.

## Protocol (fixed before candidate runs)

- Three cases, three efforts, three repetitions: 27 independent CLI sessions.
- Source case: interpret full SNL Plate 21 with two catalogue transcriptions;
  distinguish callouts 28/30, their spatial locations, and unsupported dimensions.
- Construction case: emit a FreeCAD function for a fully specified nested bearing
  and 24-groove sleeve, including a supplied nontrivial installation transform.
- Repair case: diagnose and repair the historical collar Boolean defect while
  preserving the qualified rear mounting lip and its six holes.
- Each session receives its entire task inline, plus the source image where
  applicable. No conversation history, model answers, grading code or later
  project corrections are supplied. Tools are prohibited in the task and tool
  events are audited; any use invalidates that trial. This is prompt-enforced
  and audited isolation, not a claim that the CLI filesystem sandbox prevents
  reading every other file on this system.
- The child task is read-only and runs in a fresh empty directory. Candidate code
  is returned as structured text and executed by a separate FreeCAD grader.
  Thus this pilot measures bounded interpretation/code generation, not autonomous
  research, tool selection, long-context integration or CAD debugging loops.
- Candidate functions receive three construction scenarios or five repair sizes.
  Hidden checks evaluate material witnesses, voids, alignment, nesting, preserved
  material and independent STEP round trips. A reference implementation and
  deliberately faulty implementations check the grader before experiments.
- All hard checks must pass for a case pass. Record continuous scores as diagnostic
  detail; a high average never overrides a failed hard requirement.
- Source endpoint windows are approximate manual traces, not dimensional
  calibration. Explicit uncertainty is retained as a useful outcome but cannot
  earn a pass on a required supported identity/arrangement decision.
- Rotate effort order across repetitions. Keep model, prompts, images, runtime,
  schema and grader fixed. Repetitions are not additional distinct problems.
- Record command, requested settings, CLI version, hashes, elapsed time, exit
  status, raw events, final answer, token/cache usage, tool events and grading.
  Requested model/effort are recorded; do not claim server-side attestation when
  the event stream does not return it.
- Separate infrastructure failures from modeling failures. No automatic repair,
  retries that hide failures, model-based grading or access to reference answers.
- Existing project CAD and source files are read only. No production promotion.

## Interpretation

The main outcome is per-case hard-check success. Token usage and wall time are
secondary; cached input must be reported separately. No dollar estimates are
inferred from ChatGPT-authenticated CLI token counts. Three repetitions per case
are too few for a general reliability claim. A passing result supports another
bounded trial, not lowering effort for untested mechanisms or integration.

## Run

`python3 benchmarks/cad_reasoning/prepare.py`

`python3 benchmarks/cad_reasoning/grade.py --self-test`

`python3 benchmarks/cad_reasoning/run.py`

`python3 benchmarks/cad_reasoning/summarize.py`

CLI launches need their normal authentication, network and runtime-state access.
The child sessions themselves use a read-only sandbox. Results and grading logs
live under `results/`; durable temporary directories are under `.work/`.
