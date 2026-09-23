# CAD packet controller and tool-enabled trials

The CLI controller is implemented and the six baseline trials are complete.
The evidence supports **experimental medium effort for reviewed, bounded
implementation**, with independent checks and review. It does not justify
automatically reducing effort for unresolved research or new mechanisms.

The controller routes those uncertain cases to xhigh, preserves failures, and
keeps all candidates in shadow mode. The new FreeCAD skill captures reusable
runtime and assembly knowledge so workers need not rediscover it in each packet.

## Baseline: one paired trial per task

Requested model: GPT-6 Astra. Each fresh session could use local tools, with an
eight-minute CLI limit. No new FreeCAD skill was discoverable during these six
trials. See the frozen [protocol](PROTOCOL.md) and
[machine-readable summary](results/summary.json).

| Task | Medium | Xhigh |
| --- | --- | --- |
| Parameterized nested stack | Completed in 290.7 s; 70/70 checks | Timed out at 480.0 s; final CAD files absent |
| Cross-assembly placement repair | Completed in 131.9 s; 94/94 checks | Timed out at 480.0 s; saved files passed 94/94 in a separate diagnostic |
| Historical source conflict | Completed in 102.3 s; 16/16 checks | Completed in 238.3 s; 16/16 checks |

Medium completed 3/3 within the limit; xhigh completed 1/3. These are **delivery
results under a fixed budget**, not evidence that xhigh generated wrong geometry.
The five available complete artifact sets passed the applicable independent
geometry/source checks. The xhigh mount record remains failed because its CLI
session did not finish; its subsequent
[geometry diagnostic](results/timeout_diagnostics/shadow01_mount_xhigh/grade.json)
does not replace or erase that timeout. The unfinished xhigh stack cannot be
assessed as a completed model.

The stack trials exposed GUI initialization/view fitting and API-discovery costs.
Both investigated an unavailable `App::Link.getGlobalPlacement()` method and
offscreen GUI behavior. The xhigh mount candidate also spent effort preserving
native archive bytes across FreeCAD serialization, beyond the semantic geometry
and placement requirements. Its repair was geometrically correct. Medium used
geometric comparisons after reopening instead of rewriting archive internals.

Both source candidates correctly identified M1336 around M1333, retained the
printed spring **outside** diameter, rejected the inserted memo, and left
historical dimensions unresolved. Under the stipulated wire assumption, both
computed -23.8125 mm literal radial clearance and +1.5875 mm for the alternative
ID interpretation. Positive clearance was not treated as historical proof.
The xhigh explanation included additional provenance distinctions, but both
satisfied the defined source criteria.

## Usage and interpretation

Medium's three sessions reported 772,362 input tokens (701,056 cached input),
13,955 output tokens and 997 reasoning-output tokens. Its summed CLI time was
524.9 seconds. Xhigh's observed CLI time was 1,198.4 seconds, including the two
480-second limits; its uncapped completion times for those tasks are unknown.

**The two timed-out xhigh sessions did not emit completion usage. Their token
use is unknown, not zero.** Only its completed source session reported usage:
197,580 input tokens (172,416 cached), 7,053 output and 1,321 reasoning-output.
Therefore this experiment cannot establish an aggregate token-cost ratio between
efforts. No monetary estimate is inferred from ChatGPT-authenticated CLI usage.

These are cumulative multi-turn token fields, unlike the first pilot's single
no-tools responses. Controller implementation, fixture qualification, primary
reviewer effort and the separate skill test are outside these six CLI timings.
One repetition per task, two synthetic geometry fixtures, a supplied source
conflict and the fixed deadline are substantial limits. This is still an effort
comparison within Astra, not a comparison of different model families or a
qualification of general NURBS reconstruction.

## What the implementation protects

The [controller guide](../../tools/cad_packets/README.md) documents its commands.
Candidates can edit only their own workspace; supplied inputs are read-only.
Validators, controller records, sibling candidates and production CAD are outside
candidate access. A preflight checks each run's boundary before inference.
Independent validators consume saved CAD/data and never import the candidate's
builder. Review and staging are separate, and staging cannot overwrite a bundle
or update the main assembly.

The baseline audit verified six independent thread IDs, actual command use,
record/input hashes and all 249 pre-existing native FCStd files under `cad/`
(the delivery and existing experiments) unchanged. The CLI records requested
model/effort, but does not attest the model served. Candidate notes describe image
inspection and correctly report image-only details; this CLI event format did
not expose distinct image-view events. The primary reviewer independently
inspected the supplied originals rather than treating that claim as attestation.

Ten controller/review-gate tests passed. The CAD evaluator passed three reference
cases and rejected four deliberate defects before inference. Both completed
medium CAD builders also regenerated passing documents in fresh, restricted
workspaces. Saved installed and section views were inspected: they show the
expected stack arrangement and both repaired mounts. Numerical fit/clearance
acceptance comes from the CAD checks; preview tessellation alone cannot establish
submillimetre clearance.

## Reusable FreeCAD skill

[freecad-reconstruction](../../skills/freecad-reconstruction/SKILL.md) contains
focused instructions, runtime/assembly/source references, a headless launcher,
rigid link helpers and a real FreeCAD self-test. Nine helper checks passed,
including nested transforms, bores, native/STEP reopening, headless visibility
and rejection of unsupported scaled links or definition frames.

The skill distinguishes runtime failures from geometry failures, avoids needless
GUI startup for kernel work, preserves source uncertainty, and documents its
helpers' narrower contract. It does not claim support for arbitrary linked
assembly traversal or validated freeform fitting. Skill files are versioned and
can be supplied as hashed packet inputs; changing guidance creates a distinct
trial instead of silently changing an active comparison.

A separate [skill-assisted stack trial](results/skill01_stack_medium/result.json)
passed all 70 independent checks and a
[fresh sandbox rebuild](results/reproduction/skill01_stack_medium/result.json).
It read the supplied guidance, used the canonical world-shape helper and stayed
headless. Its CLI runtime was 285.5 seconds versus the baseline medium's 290.7;
command executions were 15 versus 19, and output tokens 7,369 versus 7,410.
It also chose to generate additional section views. These nearly equal runtimes
do **not demonstrate a speed gain**: this was one fresh session with changed
guidance, outside the frozen baseline comparison. Its reported usage was 404,018
input tokens (354,432 cached), 7,369 output and 990 reasoning-output tokens.

The skill is installed through the repository's `.agents/skills` symlink and was
discovered in the active Codex session without a restart. It can be invoked as
`$freecad-reconstruction`. The five completed sessions have result-bound
`benchmark_only` source/visual reviews by the primary AI reviewer; the timed-out
mount has a separate diagnostic review that preserves its failure status.
These reviews qualify benchmark evidence, not historical tank geometry.

The [final verification](results/verification.json) checks all seven independent
run records, unchanged inputs and native tank files, skill-resource hashes and
three successful fresh rebuilds. Repeating all seven completed commands reused
their records without inference or changing saved run evidence. An attempted
stage of a benchmark-only result was correctly rejected.

## Operating decision

Use this controller with reviewed work packets and the qualified FreeCAD helpers.
Keep medium experimental for explicit dimensions/interfaces and known part
families. Retain xhigh for source conflicts, new mechanisms and difficult
diagnosis, with a task-appropriate time budget. Review source interpretation and
relevant views before integrating any real tank geometry. The next useful
efficiency measurements should include delivery failures, correction cost and
the benefit of shared runtime knowledge, rather than reasoning tokens alone.

The CLI remains adequate for this workflow. App Server is not required by these
results; it remains an option if persistent threads or finer interaction become
necessary. No experimental tank geometry was promoted by this work.
