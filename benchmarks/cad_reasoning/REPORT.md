# Astra reasoning-effort pilot — 21 September 2026

**The CLI experiment worked. All three effort settings passed all nine of their
trials. Medium used 68% fewer output tokens and 62% less CLI time than xhigh on
these bounded tasks.** This supports a controlled trial of lower effort for
explicitly specified work. It does not establish equal reliability for discovering
the specifications, reconstructing a new mechanism or integrating the tank.

## Results

Three distinct cases were repeated three times at each setting: 27 independent
GPT-6 Astra sessions. No other model was tested. Each case is all-or-nothing against
fixed hard requirements; repetition is not additional problem diversity.

| Requested Astra effort | Passed trials | Mean CLI time per trial | Total output tokens | Total input tokens |
|---|---:|---:|---:|---:|
| medium | 9/9 | 27.4 s | 6,457 | 133,512 |
| high | 9/9 | 37.8 s | 9,121 | 133,512 |
| xhigh | 9/9 | 71.9 s | 20,074 | 133,530 |

Every setting passed 3/3 trials on each case. The direction of the time/output
difference was consistent across all three cases:

| Case | Medium: mean seconds / output tokens | High | Xhigh |
|---|---:|---:|---:|
| Source interpretation | 19.8 / 440 | 23.4 / 590 | 45.4 / 1,327 |
| Prescribed CAD construction | 30.9 / 856 | 43.2 / 1,087 | 87.0 / 2,754 |
| Collar defect repair | 31.5 / 856 | 46.8 / 1,363 | 83.2 / 2,610 |

Token fields come from CLI completion events. The output/latency reduction is not
a billing reduction: all runs reported zero cached input, and input overhead was
almost identical. Input plus output counts fell by approximately 9% from xhigh
to medium. No monetary savings are inferred from ChatGPT-authenticated CLI usage.
Reasoning-token fields are retained separately in the detailed summary and must
not be added again to output counts to estimate a bill.

The matrix used 400,554 input tokens and 35,652 output tokens. Summed CLI time was
20.6 minutes; first-trial start to last-trial completion was 23.4 minutes including
the original grading and launch intervals. Benchmark preparation, subsequent
grading correction, auditing and report work are outside those timings. These
are CLI completion measurements, not fully integrated CAD delivery timings.

## What was actually checked

- **Source interpretation:** full SNL Plate 21, with two catalogue-row
  transcriptions. Correctly identify the thrust collar and separate external snap
  ring, trace their leaders, and avoid inventing exact dimensions or historical
  fit. Nine hard criteria, including approximate endpoint windows. All nine
  explanations were also read against the supplied figure. The catalogue marks
  were supplied; this did not test finding/transcribing them from the archive.
- **Construction:** a prescribed stepped bearing and nested sleeve with 24
  rectangular grooves, under a supplied installation transform. Three coherent
  size/placement scenarios, 33 checks per trial, including 1,476 material/void
  witnesses, topology, nesting, extents and STEP checks. Actual FreeCAD native and
  STEP files were produced from each candidate's code. No NURBS surface fitting
  or complex casting interpretation was tested.
- **Repair:** the historical Boolean-union defect that retained an old collar
  rim when reducing body radius. Five sizes and 60 checks per trial assess the
  entire receiving body, retained mounting lip and six holes, untouched input
  shape, thrust-lip clearance and STEP exchange. The symptom and relevant parent
  dimensions were supplied; this was not an open-ended fault search.

The grader was checked with reference implementations and deliberately wrong
source/geometry answers. The wrong source mapping, old rim, missing groove and
missing installation transform were all rejected.

## Grading correction, retained in the evidence

The initial Python wrapper omitted the normal `all()` builtin. Five repair
answers used it for legitimate parameter validation and therefore failed before
their CAD could be evaluated. This was a benchmark defect, not a model error.

[Grader v2](grade_v2.py) adds `all` and `any` and resolves explicitly supplied
output paths before configuring FreeCAD. All source/geometry criteria and
tolerances remain unchanged. Every one of the 27 original answers was re-scored
with v2, with no replacement model calls or edits to candidate code. All passed.
Original events, answers and grades remain beside the corrected results.
The exact change is recorded in [grader_amendment.json](results/grader_amendment.json).

This illustrates a useful evaluation principle: a failed test needs diagnosis
before it is attributed to the model. More defensive generated code happened to
expose an omission in the test harness.

## Recommendation for the tank workflow

**Proceed toward a small controller that selects effort by work type. Keep the
CLI as its first execution backend; App Server is not yet necessary.** We have
demonstrated automated selection, fresh sessions, structured answers, usage
capture and external validation with the installed CLI. A backend abstraction
can allow App Server later if persistent threads, per-turn switching or richer
interaction becomes necessary.

The initial policy should be conservative:

| Work category | Proposed routing | Required evidence before integration |
|---|---|---|
| Implement an accepted dimension/interface specification; expand a qualified family | Trial medium | Fixed specification, source mapping already reviewed, independent CAD checks and relevant visual review |
| New mechanism, uncertain source applicability, major datum or interface changes | Keep xhigh | Original sources, explicit competing interpretations, reviewed assumptions and full interface checks |
| Failed lower-effort implementation or contradiction with its specification | Escalate to xhigh for diagnosis | Preserve the failed output; determine whether the code, specification or checker is wrong |
| Rebuilds, inventory counts, hashes, exports and routine checks | Scripts | Recorded inputs and actual execution receipts |

The pilot found no measured quality advantage for high over medium on its three
tasks. It provides no basis for a claim that high lacks value on other tasks.
Keep all model/effort choices configurable and assess additional task families.

The controller should maintain the following boundary:

1. A work packet supplies a qualified parent, the relevant full source figures,
   dimensional table, local frames, neighboring interfaces and unresolved issues.
2. Routing follows explicit packet classification, rather than a candidate's
   self-reported confidence. Unknown or ambiguous categories retain xhigh.
3. Candidate changes go to an isolated workspace. Validators and acceptance
   criteria are outside the candidate's write authority.
4. Scripts check actual CAD and dependency changes. Source/visual review remains
   a separate requirement when interpretation is involved; a good fit cannot
   prove historical identity.
5. A single integration step promotes only the reviewed, checked artifacts and
   records exactly what changed. A failed check cannot be bypassed by changing a
   tolerance, source identity or parent datum inside the candidate task.

Before enabling automatic promotion, run tool-enabled work packets in shadow
mode: compare lower effort and xhigh on additional *distinct* tasks, without
promoting the experimental outputs. Measure escaped errors and correction cost,
not just first-attempt speed. In particular, test incomplete evidence, source
conflicts, geometry requiring diagnostic tool use and changes across assemblies.

## Limits

This is three problems repeated, not a broad accuracy benchmark. All necessary
inputs were supplied, tools were prohibited and every event stream was audited
for tool use. The result does not cover autonomous retrieval, FreeCAD debugging
loops, long conversation state, freeform geometry or whole-vehicle integration.
The clean inputs are materially easier than the original reconstruction episodes.

The reference source interpretation is a reviewed project interpretation, not
physical metrology. Native validity and fit do not prove historical dimensions.
The few repetitions and possible variation in service latency do not establish
statistical equivalence between settings. No alternate model was tested.

The CLI records requested model/effort but its event stream did not attest the
served model identity. The experiment used Codex CLI 0.155.1, Python 3.12.3,
FreeCAD 1.1.1 and Open CASCADE 7.8.0. Authentication and runtime launch succeeded
after allowing the CLI its normal runtime-state and network access; each child
task itself was read-only.

## Evidence and reproduction

- [Frozen initial protocol](README.md) and [fixture manifest](manifest.json).
- [Detailed table](results/pilot_01/SUMMARY.md) and [machine-readable summary](results/pilot_01/summary.json).
- [Audit](results/pilot_01/verification.json): 27 separate threads, zero candidate
  tool use, fixture/answer/grade hashes consistent, and all 21 recorded production
  CAD documents unchanged. Tracked production files were also unchanged.
- [Runtime record](results/runtime.json).
- Per-trial directories under `results/pilot_01/` retain requests, raw CLI events,
  original answers, original grades, corrected grades and native/STEP geometry.
- [Rescoring utility](rescore.py) applies the documented amendment uniformly;
  [verification utility](verify.py) audits the complete result chain.

The initial runner is frozen for this specific matrix. Re-running it reuses its
recorded completed trials; it does not silently spend tokens or overwrite them.
Changed models, tasks or protocols should receive a new experiment identity.

After running the initial commands from the frozen protocol, reproduce the final
scoring and audit with:

```sh
python3 benchmarks/cad_reasoning/grade_v2.py --self-test --output benchmarks/cad_reasoning/results/self_test_v2
python3 benchmarks/cad_reasoning/rescore.py
python3 benchmarks/cad_reasoning/summarize.py
python3 benchmarks/cad_reasoning/verify.py
```
