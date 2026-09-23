# CAD work-packet controller

This controller runs bounded CAD work through Codex CLI and records independent
validation. It currently operates in **shadow mode**: it cannot overwrite the
tank's accepted native documents. The first backend uses the existing CLI login;
there is no API key setup or App Server dependency.

## Routing

Medium is experimental and eligible only for `reviewed_implementation` or
`qualified_family` packets with all three reviews explicitly true (dimensions,
sources, interfaces) and no risks. New mechanisms, source conflicts, missing
reviews, interface changes and unknown categories route to xhigh. Failed work
offers a separate xhigh diagnosis. An explicit `--effort` override is recorded
as a shadow comparison, never as permission for automatic integration.

```bash
python3 tools/cad_packets/controller.py route benchmarks/cad_work_packets/packets/stack.json
python3 tools/cad_packets/controller.py run benchmarks/cad_work_packets/packets/stack.json --id my_stack_trial
python3 tools/cad_packets/controller.py status my_stack_trial
```

An identical completed command verifies its inputs and saved evidence, then
reuses the result without inference. Changed inputs, code, CLI version, timeout
or effort require a new run ID. Interrupted runs preserve their records and
workspace; start a new run ID rather than overwriting partial evidence. Workspaces
live in `.work/cad-packets/runs`, while durable requests, outputs, events and
results live in `benchmarks/cad_work_packets/results`.

```bash
python3 tools/cad_packets/controller.py run path/to/packet.json --id repair_diagnosis --diagnose-from failed_run
```

Diagnosis requires the same packet and a failed prior run, copies its declared
artifacts and validation feedback as read-only inputs, and forces xhigh. Its
latency and tokens are recorded separately so failure costs stay visible.

## Packet and validation contract

Use the three JSON examples as executable packet templates alongside the fuller
[CAD work-packet template](../../docs/templates/cad-work-packet.md). A packet needs:

- ID, version 1, `mode: shadow`, category, explicit review flags and risk list.
- Instructions with units, source applicability, dimension assumptions, local
  frames, qualified parents, interfaces, required outputs and unresolved issues.
- Explicit input files: repository-relative source, candidate-relative destination,
  SHA-256. Include full figures and relevant qualified native/STEP/BRep parents.
- Declared files under `deliverables/`; a reviewed validator under `validators/`
  and a passing, current qualification record for that validator.

Validators are authored and qualified before candidate execution. They run in a
separate process and consume saved CAD/data, without importing candidate builders.
Source interpretation and visual comparisons need a separate review: a Boolean
intersection check cannot prove the correct historical part was modeled. Add a
new validator and negative controls when a packet requires new acceptance logic.
The included validator is specific to the three benchmark cases, not a universal
tank-model certifier. Builders also need a reproducibility review before any real
model integration; the current mechanical gate checks their saved outputs.

The project's [FreeCAD reconstruction skill](../../skills/freecad-reconstruction/SKILL.md)
captures tested runtime, placement and evidence-handling guidance. Supply the
skill and relevant resources as hashed packet inputs for isolated workers, as in
`benchmarks/cad_work_packets/packets/stack_with_skill.json`. This makes the intended
guidance readable within the candidate's restricted workspace and records its
revision. Keep the skill/discovery environment fixed during paired comparisons;
the controller records requested CLI settings, not every server-side instruction.

## Isolation and failure handling

The CLI profile grants candidate commands only minimal platform reads, `/snap`
runtime reads, and writes to their own absolute workspace. Packet inputs and the
FreeCAD launcher are read-only. Controller results, validators, other candidates
and production files are outside candidate read/write access. The controller
probes each profile before inference; a hidden sandbox ancestor can accept an
ephemeral write, so the probe also checks the real host canary remains unchanged.
Shell network access is disabled, web search is disabled, and escalation is not
available to candidate commands. The CLI itself still needs its normal saved-login
and runtime access; an outer sandbox may require an approved launch for that.

Independent validation has read access to only its inputs, artifacts and trusted
controller code, and writes to its validation directory. Timeouts terminate the
process group. Missing outputs, malformed events, changed inputs, failed checks,
tampered records and stale validators fail closed. Symlink/hardlink output files
and paths escaping their workspace are rejected. A lock prevents overlapping
controller mutations. Production native CAD hashes are compared before and after.

These are local workflow boundaries, not an adversarial security certification of
FreeCAD or the operating system. Permission profiles are currently a beta Codex
feature; keep the preflight checks when upgrading the CLI. See the official
[permission-profile documentation](https://learn.chatgpt.com/docs/permissions) and
[configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference).

## Review and staging

Passing mechanical checks leaves the run `awaiting_review`. Record actual source
and visual findings with `review`; no automated process calls it on a candidate's
behalf. `benchmark_only` keeps synthetic qualification fixtures out of integration.

```bash
python3 tools/cad_packets/controller.py review RUN_ID --reviewer REVIEWER \
  --disposition benchmark_only \
  --source-note 'Describe the evidence actually checked and remaining assumptions.' \
  --visual-note 'Identify views checked, findings, and any limits to this review.'
```

For real work, `accepted_for_review_bundle` allows `stage RUN_ID` to copy the
reviewed artifacts and provenance into a new, immutable
`cad/003_FullTank/review_bundles/RUN_ID` directory. Staging checks that inputs,
artifacts, review and production parents still match. It never updates the main
assembly or overwrites an existing bundle. Integration into that assembly remains
the established full-tank workflow's separate dependency/visual validation step.

## Checks and extension

```bash
python3 tools/cad_packets/test_controller.py
python3 benchmarks/cad_work_packets/test_review_gate.py
```

CAD qualification runs through `freecad_python.py` in a scratch working directory;
see [the tool-enabled benchmark protocol](../../benchmarks/cad_work_packets/PROTOCOL.md).
The launcher uses installed FreeCAD and Qt snap paths, with settings/cache in that
workspace. `CLIBackend.command()` isolates the execution backend, so a later
App Server implementation can keep packet, routing and acceptance logic intact.
