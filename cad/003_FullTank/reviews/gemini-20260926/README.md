# Gemini review and selective merge — 26 September 2026

Merged `116707ca` and `fcbca8ed` into `main` by fast-forward from `98f281b8`.
These add four rear low-speed fork joints and two shared SH946E straight rods:
18 additional occurrences, two additional definitions, and revised estimated
M4133/M4134 brake arms. The accepted development model is now
**3,282 occurrences / 570 definitions / 365 groups** in
[low_rods_integrated01](../../experiments/drive_chains/transmission_controls_study/low_rods_integrated01/README.md).
Its native SHA-256 is
`9b36e8ca2124d0314825c66b905080f770a3d709a9503eb76a882147cd4e1f04`.
This is a local static reconstruction with documented approximations; the
standard tank011 assembly and full historical qualification remain unchanged.

**Do not merge `b19e16e5` wholesale or treat the front-controls draft as qualified.**
The original `gemini` branch remains at that commit. All 121 previously
uncommitted files were preserved without alteration in recovery commit
`9bb60922` on `review/gemini-front-controls-20260926`, based on `b19e16e5`.
The pre-review SHA-256 inventory was checked against every recovery Git blob.
A second copy remains under `.work/gemini-review-20260926/uncommitted_before/`.
Nothing was pushed to a remote.

## Independent saved-material checks

| Model | Targets | Nearby material pairs | Positive intersections |
| --- | ---: | ---: | ---: |
| Accepted prefix: low joints/rods | 18 additions + 2 revised levers | 87 | 0 |
| Full Gemini tip | 158 additions + 2 revised levers | 549 | 31 |
| Uncommitted nominal front controls | 69 additions | 396 | 39 |

The workers opened the saved FreeCAD documents, checked target links and composed
frames against manifests, verified native/BRep hashes, and computed actual solid
intersections against development and retained standard assembly geometry.
A conservative bounding-box search selected nearby pairs; no mating-pair
exemptions were applied. All Boolean operations completed without errors.
Positive intersections exceed `1e-5 mm³`; this is a review threshold, not a
manufacturing clearance specification.

The full-tip recovery verifier passed before review, and the accepted-prefix
verifier passed again after merging. Those establish unchanged evidence and
recorded scope; they cannot compensate for omissions in a checker. The prefix
also has hash-bound nominal/variation native, STEP, context and reproduction
evidence. Its checkers inspect real bores, pin axes, thread engagement, nut seating,
preserved receivers and deliberate displaced-part failures. These were inspected
alongside the SNL87/SNL195 scans and saved detail and fixed-camera source views.
The fresh material scan adds complete retained context to this review; a complete
model rebuild was not repeated.

## Why the remaining commit is withheld

Later context checkers skip many fork/rod/pin/lever and clamp/key contacts as
“mating pairs.” Several skipped contacts are substantial solid intersections,
not just boundary contact. Examples from [branch-material.json](branch-material.json):

| Parts | Common material, mm³ |
| --- | ---: |
| Clutch fulcrum bracket / forward clutch fork | 4,047.327 |
| Clutch fulcrum bracket / forward clutch pin | 1,174.214 |
| Port center high rod / forward nut | 2,536.263 |
| Starboard center high rod / aft pin | 1,935.381 |
| Port forward low-rod fork / horizontal lever | 409.112 |

All 31 findings, including smaller clamp and key overlaps, need an interface
disposition. This review does not assume that every modeled interference has
the same cause. The large fork/bracket, rod/pin and rod/nut overlaps suffice to
reject this integrated state.

Source identity also needs correction. The SNL calls M574 a **front low-speed
brake rod**, M573 the **rear low-speed rod**, and M576 a **front control rod**.
The final Gemini descriptions assign M574 to a clutch center rod. Several pins
named M568C use `Def_ControlJoint_pin`, the previously reconciled **M568A**
41.275 mm definition, although M568C has its own 39.6875 mm catalogue length and
existing definition. These are different recorded parts. M638 is recorded at
`SNL:211:029`; the later packet's `SNL:170:001` attribution needs correction.
See [source_identity_evidence.json](source_identity_evidence.json).

This does not discard the entire last commit. Its washer/spring work and some
other increments may be recoverable. No intersections involving those additions
were found, but that alone does not qualify source identity, attachment,
retention or full routes. Extract and review bounded increments.

## Assessment of the uncommitted work

**Keep the inventory and layout exploration; rebuild the affected geometry and
installation logic. Do not restart the tank model.** The draft identifies driver
controls, records candidate routes, separates reusable parts from occurrences,
and includes nominal and variation files. Those provide a starting checklist,
not established dimensions or placements.

Specific defects in the saved nominal model and implementation include:

- Pedal and hand-lever bores are cut from their bosses before solid arms are
  fused on. That fusion fills part of each shaft passage again. Pedal/shaft
  common material is **12,110.273 mm³**; the six hand-lever/shaft pairs each have
  approximately **11,890–12,076 mm³** of overlap.
- The brake pedal overlaps the hull floor by **5,549.631 mm³**. Each forward
  low-rod fork overlaps floor plate 2 by **3,839.348 mm³**. These floor contacts
  are explicitly excluded in the supplied context checker.
- Aft fork pins are rotated about X by 90 degrees despite the shared pin's
  local Y axis and the fork's transverse Y bore. The resulting aft pin/rocking
  lever overlaps are approximately **2,970–3,007 mm³**. Joint frames must be
  derived from measured receiving axes and bearing widths.
- Rod/nut and selector/fork overlaps remain. Count/volume checks and exemptions
  do not establish coaxial bores, thread engagement, seating or cotter retention.
- The generator removes an existing output directory with `shutil.rmtree`.
  Repair trials must use new directories to preserve these diagnostics.

See [front-material.json](front-material.json) for all 39 intersections and
[code_evidence.json](code_evidence.json) for hashed implementation excerpts and
original line numbers. The variation is preserved, but only the nominal
front-controls geometry received this independent overlap audit.

## Recommended continuation

1. Start from merged `low_rods_integrated01`. Recover the M567 washer/M564 spring
   increment from `gemini`, reviewing interfaces and source support before
   integration. Retain useful later work in similarly small increments.
2. Reconcile rod/pin identities with actual source rows and the assembly
   inventory. Separate printed dimensions from inferred profiles and stations.
3. Repair clutch and long-rod interfaces. Measure receiving bores/seats from saved
   solids, compose local frames, and qualify one complete joint at a time. Cut
   shared bores after all relevant unions. Check full receiver and floor material.
4. Rebuild driver-control mounting and placements from those interfaces and
   source evidence. Reuse draft routes only as hypotheses. Verify nominal and
   meaningful variant states, native/STEP reopening, preservation and
   reproduction. Retain the established camera unless evidence warrants refitting.
5. Keep accepted visual progression through 254. Experimental images 255–286
   remain on `gemini`; preserve provenance rather than silently overwriting their
   numbers when recovering or replacing its work.

Raw reports, exact audit workers, original-file inventory and verifier logs are
bound by [review_receipt.json](review_receipt.json). Workers use the repository's
absolute root and existing FreeCAD helper imports. `audit_prefix.py --scope prefix`
runs with the merged checkpoint; `audit_material.py --scope branch` requires the
Gemini checkout, and `--scope front` requires the recovery checkout. Run through
`skills/freecad-reconstruction/scripts/freecad_headless.py` with absolute
script/output paths, a task-local runtime directory and a new output directory.
Do not rerun builders or receipt-writing candidate checkers over originals.
