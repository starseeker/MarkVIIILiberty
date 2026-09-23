# Tool-enabled CAD work-packet trial 01

Frozen before inference, 22 September 2026. This is a second, distinct experiment;
the earlier no-tools pilot remains unchanged.

Compare requested GPT-6 Astra medium and xhigh once each on three work packets,
using fresh CLI sessions with local tools and the same inputs per pair. Run
stack medium/xhigh, mount xhigh/medium, spring medium/xhigh, sequentially.
Each candidate gets 480 seconds, followed by up to 180 seconds of independent
validation. A failure remains in the results. Diagnosis, if needed, is a separate
xhigh run whose time/tokens are additional correction cost, not a replacement score.

- Stack: synthetic, internally reviewed pin/tube/bush specification, two parameter
  sets, nested transformed assemblies, shared definitions and four installed links.
  Several major dimensions derive from HB141; bush fits and pin hollow are fixture
  assumptions. Passing cannot qualify this simplified stack as historical tank CAD.
- Mount: synthetic native assembly with two damaged occurrence placements, two
  differently oriented parents, shared shapes and ten physical occurrences. The
  candidate must diagnose it through FreeCAD, preserve the qualified fixture shapes
  and all undamaged placements, and export the repaired installed geometry.
- Spring: original HB141 spread and full extracted section plate 138, a conditional
  wire interpretation and a deliberately false draft memo. Preserve printed wording,
  derive literal and alternative clearances, identify parts and retain the unresolved
  evidence gate. No final spring geometry is requested.

Acceptance is implemented outside candidate write/read access. Validators consume
saved CAD or JSON, never import candidate builders. Before trials, three reference
answers must pass, and four intentional defects must fail. Each run probes its
filesystem policy, records requested settings, input/controller/validator hashes,
raw events, usage, timing, artifacts, checks and production CAD hashes. Shell
network access is disabled. Source/visual review is an additional recorded gate.

Report mechanical pass rates, tool use, source/visual findings, total input and
output tokens, and CLI time separately. Count diagnosis overhead when present.
There is no automatic integration or claim that one trial establishes reliability.
This is still an effort comparison within Astra, not a comparison with cheaper
model families. CLI events do not attest the model actually served. Do not infer
billing from these token fields.
