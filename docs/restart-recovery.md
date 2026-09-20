# Restart recovery

The 20 September 2026 restart was recovered. Current authored sources, native
models, selected experiment fixtures and progression images survived or were
recovered. Some temporary execution logs and the older complete milestone009
native delivery archive were lost. Its progression images survive.

## Current standard delivery

Milestone011 is now saved in `cad/003_FullTank/build`. It includes the qualified
roller-pinion integration: 252 definitions, 5,341 assembly leaves, 5,326 physical
components and 15 layout occurrences. All physical definitions remain partial;
the complete-tank goal remains open. Open `build/native/MarkVIII.FCStd` with its
library and subsystem directories present.

The original private pinion build passed 29 validation stages, 17 parameter
trials and 37 record/renderer tests. Its exact authored geometry and all 20 native
files were transferred to the main build. A fresh FreeCAD check there verified
all 20 local dependencies, 252 definitions, 5,341 placements and the original
geometry signatures. The 754-file source lock also passed. The trial suite was
not rerun at the main path: the
[transfer receipt](../cad/003_FullTank/releases/011-roller-pinions-transfer.json)
explicitly binds the original qualification to the fresh native checks.

The original build/validation records remain byte-identical under
`build/reports/qualified_origin`. Only the main build report's top-document path
was changed. Older pending/private wording in preserved origin records describes
their original time and scope; the transfer receipt supplies the current status.
Do not silently rewrite a report that is bound by an earlier checkpoint hash.

The 187-file delivery manifest and all archive contents were checksum-verified.
[The release record](../cad/003_FullTank/releases/011-roller-pinions.json) identifies
`.work/deliveries/011-roller-pinions.zip`. The exact private origin is also archived
at `.work/deliveries/roller-pinions-qualified-origin.zip`. Milestone010 remains at
`.work/deliveries/010-drive-mounts.zip`, with its previous expanded build preserved
in `.work/pinion-promotion/previous_build_010`.

Milestone011 preserves an opaque isometric, a transparent-hull companion and two
pinion close-ups. All four were inspected. The previous 18 progression images
remain byte-identical. The [progression viewer](../cad/visual_progression.html)
offers opaque and transparent hull display; the transparent mode begins at 011.

## Durable locations

| Work | Location |
| --- | --- |
| Current standard model and generated reports | `cad/003_FullTank/build` |
| Main authored sources | `cad/003_FullTank/data`, `lib`, `manage.py` |
| Isolated pinion origin | `.work/roller-pinion-integration/cad/003_FullTank` |
| Original qualification checkpoints and logs | `.work/roller-pinion-integration/cad/003_FullTank/build/verification/runs` |
| Pinion promotion preparation, verification and final audit | `.work/pinion-promotion` |
| Chain/casing/transmission experiments and evidence | `cad/003_FullTank/experiments/drive_chains` |
| Preserved generated delivery archives | `.work/deliveries` |
| Current handoff and active job handles | `.work/WORKFLOW_HANDOFF.md` |
| Numbered images and their hashes | `cad/VISUAL_PROGRESSION.md` |

`.work` is intentionally ignored by Git. It survives process restarts but must
travel with workspace backups; a Git clone alone does not include these delivery
archives. Local commits preserve authored sources, selected experiment evidence,
release records and progression images. The private source branch
`experiment/roller-pinions` remains available independently.

## Safe continuation

Check the current handoff, job handle and status files before resuming an
operation. A slow stage or tool observation timeout is not proof that a process
has stopped. Do not start a replacement worker while the original is active.
Keep source inputs fixed during an active qualification.

The stage011 promotion, main-path verification, transparent rendering and archive
finalization are complete. Do not rerun promotion preparation or the older010
finalizer against this delivery. The versioned tools document the completed
sequence: `tools/promote_roller_pinions.py` and `tools/finalize_roller_pinions.py`.
They check original hashes and refuse incompatible replacements.

For a subsequent changed model, rebuild first and qualify that new revision:

```bash
python3 cad/003_FullTank/manage.py build
python3 cad/003_FullTank/tools/resume_validation.py --stages-per-worker 1
python3 cad/003_FullTank/tools/transparent_isometric.py
```

A new qualification checks its own authored/native/runtime bindings. Completed
stages can be reused only when those bindings and stage artifacts match. Existing
output folders alone do not establish success. Rendering transparency changes
only the inspection display; it does not resave native geometry.

Continue standard geometry before poses. The next work is chain/casing and
remaining transmission integration, followed by remaining exterior fittings and
identifiable interior systems. The latest isolated chain/casing/output-shaft
fixture has 813 physical leaves and inspected native views; it is not yet part
of the delivered tank. Source conflicts and inferred dimensions remain in the
[chain packet](../cad/003_FullTank/packets/R02-drive-chains.md).

The earlier recovery integrity audits remain under `.work/recovery`. They record
what was present at their dates; their older main counts describe milestone010,
not the subsequently promoted milestone011.
