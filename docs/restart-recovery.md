# Restart recovery

The 20 September 2026 restart did not block the tank workflow. Current authored
sources, native models and progression images survived or were recovered.
Some temporary execution logs and the older complete generated stage009 archive
were lost. The stage009 images survive; its complete native archive does not.

The recovery audit checked both current builds against their recorded authored
fingerprints and all 20 native-document hashes in each build. It also verified
15 earlier progression-image hashes and the private pinion experiment's passing
37-test receipt against its current source, test files and actual test log.
These checks establish that the recovered artifacts match their records. Full
CAD validation remains a separate, resumable operation.

## Durable locations

| Work | Location |
| --- | --- |
| Current standard model | `cad/003_FullTank` |
| Isolated pinion model | `.work/roller-pinion-integration/cad/003_FullTank` |
| Chain experiments, native fixtures and reports | `cad/003_FullTank/experiments/drive_chains` |
| Main validation status and log | `cad/003_FullTank/build/verification/runs` |
| Private qualification status and source-test receipts | `.work/roller-pinion-integration/runs` |
| Private validation status and log | `.work/roller-pinion-integration/cad/003_FullTank/build/verification/runs` |
| Current handoff and job handles | `.work/WORKFLOW_HANDOFF.md` |
| Recovery integrity audit | `.work/recovery/current_artifact_audit.json` |
| Numbered progression images and descriptions | `cad/VISUAL_PROGRESSION.md` |

Keep ongoing execution records and experiment inputs in these workspace
locations. `.work` is intentionally ignored by Git: it survives process restarts,
but it is not a repository backup. Main source and selected experiment evidence
have local commits. The `experiment/roller-pinions` branch separately preserves
the private model's authored data, libraries, tests and validation tools.

## Resuming validation

First check the current handoff, job handle and status files. A slow stage or a
tool observation timeout does not mean the worker stopped. Do not start another
worker while the original one is active. Keep each model's authored inputs
unchanged while its validation runs.

After a confirmed interruption, the main validation resumes with:

```bash
python3 cad/003_FullTank/tools/resume_validation.py --stages-per-worker 1
```

Once the private native build and its inventory/review steps are present, its
CAD validation can resume directly with:

```bash
python3 .work/roller-pinion-integration/cad/003_FullTank/tools/resume_validation.py --stages-per-worker 1
```

The runner verifies authored inputs, native files, runtime binding and saved
stage artifacts before reusing a completed stage. It reruns interrupted or
invalid stages. Existing output directories alone are not proof of completion.
The main run has 27 stages and 15 parameter trials; the private pinion run has
29 stages and 17 trials. Their current status files, rather than this dated
recovery note, determine whether they have finished.

The durable main finalizer waits for successful bound validation, verifies the
reviewed results and saves the next numbered milestone. Its script and status
are `.work/watch_finalize_drive_mounts.py` and
`.work/drive-mount-finalizer-status.json`. Resume that watcher only after checking
that an existing instance is no longer running.

## Work after recovery

Continue standard geometry before poses. Drive-mount qualification has now
passed all 27 stages and 15 parameter trials, and snapshot010 is saved. Its
complete 161-file delivery is archived and checksum-verified at
`.work/deliveries/010-drive-mounts.zip`; the versioned record is
`cad/003_FullTank/releases/010-drive-mounts.json`. The archive is intentionally
outside Git and must travel with workspace backups.

The private pinion assembly still needs its full qualification and promotion.
Separate chain/casing work continues, followed by the remaining transmission,
exterior fittings and interior systems in the complete-tank workflow.

The chain fixtures are isolated reconstruction studies. Their source quantity
conflict, approximated tooth/hub details and installation checks are documented
in [the drive-chain packet](../cad/003_FullTank/packets/R02-drive-chains.md).
A passing isolated fixture is not a finished or promoted tank subsystem.

## Continuation integrity check

A fresh check after resuming verified 64 main and 68 private authored files,
all 20 native documents in each build, the milestone010 archive and all 18
preserved progression images. It also verified the 698 inherited source-lock
files and the new chain-detail candidate against its saved input/native hashes.
The receipt is `.work/recovery/continuation_artifact_audit.json`.

Work has continued: the isolated chain candidate now includes formed split-pin
tails and link oil passages, with passing static geometric checks and inspected
native sections. It remains separate from the delivered standard model. The
pinion qualification continues from its existing worker; no replacement process
was started merely because the conversation resumed.
