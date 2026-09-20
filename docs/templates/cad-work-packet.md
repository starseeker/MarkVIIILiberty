# CAD work packet: <ID> — <part family or subassembly>

Copy this template into `cad/003_FullTank/packets/<ID>.md` when beginning a packet.
Replace the placeholders; do not interpret the template as a completed evidence
record. Keep queue status consistent with the packet's actual disposition.

## Scope and state

| Field | Value |
|---|---|
| Queue ID / milestone | |
| Status | planned / active / review / accepted / accepted_approximate / blocked |
| Configuration and selected representation | |
| Revision / author / review date | |
| Owning subsystem and installation parent | |
| Survey IDs / original piece marks | |
| Model definition IDs / occurrence IDs or pattern | |
| Required installed quantity and its scope | |
| Dependencies and affected downstream packets | |

State the concrete deliverable, required detail, excluded features and current
inventory gaps. Distinguish an intermediate envelope from a finished approximation.

## Evidence and decisions

| Feature or arrangement | Source record/page/figure and image locator | Source value/units | Interpretation and production applicability | Decision/status |
|---|---|---|---|---|
| | | | | |

Record conflicting statements, source-wide issues, scan hashes, calibration IDs,
held-out residuals and the actual evidence inspected. For a modern observation,
record vehicle, date, restoration state and viewpoint. Identify missing evidence
that could change the result and the specific follow-up action.

## Parameters and interfaces

| Parameter | Nominal / units | Bounds and reason | Evidence or assumption ID | Dependent features/parts |
|---|---|---|---|---|
| | | | | |

| Interface ID / owner | Local datum, axis or plane | Mating occurrence/interface | Fit, contact or clearance requirement | Evidence/uncertainty |
|---|---|---|---|---|
| | | | | |

Document units, orientation and transform conventions, handedness, permitted
adjustments and correlated uncertainties. Keep fit allowances, historical
uncertainty and numerical test tolerances separate.

## Native construction and installation

Describe the selected construction: sketches/features, analytic primitives,
surface sections/patches, patterns and finishing detail. For freeform surfaces,
record the defining curves, constraints and fitting residuals.

List authoritative scripts/data and generated native documents. State which
parameters update live and which require regeneration. Specify the owning
assembly, representative test installation and how repeated occurrences are
generated without adding duplicate component definitions or BOM entries.

## Verification record

| Check | Method / declared criterion | Actual result and artifact | Pass / issue |
|---|---|---|---|
| Source hashes and configuration applicability | | | |
| Native recompute and solid validity | | | |
| Definition and installed quantities | | | |
| Parent-relative transforms and handedness | | | |
| Mating interfaces, contacts and clearance | | | |
| Source projection/section comparison | | | |
| Meaningful parameter change and propagation | | | |
| Native/STEP reopening and relocation, as applicable | | | |

Checks must record actual results. An exception needs an issue, rationale and
affected scope; a planned check is not a pass. Shared runtime/release checks may
reference their existing report instead of rerunning them without cause.
For inventory, research or schema packets, mark geometric checks not applicable
and explain which data/document acceptance criteria were verified instead.

## Review bundle and disposition

Link native parts/subassembly, exchange files, relevant views/sections/overlays,
evidence tables and machine-readable validation results. Record geometry and
occurrence coverage changes separately from evidence confidence.

State whether the packet is accepted, accepted with named approximations, needs
revision, or is blocked. A blocker identifies the exact missing decision/evidence
and what independent work can continue. List the next dependent packets made
ready by this result.

## Change log

Record input changes, superseded interpretations, affected interfaces and checks
rerun. Capture useful GUI edits in authoritative inputs before rebuilding.
