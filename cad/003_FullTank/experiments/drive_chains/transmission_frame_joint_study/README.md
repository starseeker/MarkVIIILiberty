# Transmission frame connection study

The current development checkpoint is [trial03](trial03/README.md): formed
gusset returns, diaphragm overlaps and 32 source-sized rivets. This remains a
documented mechanical approximation with incomplete frame and hull fastening.

- `trial01` saved geometry but failed while constructing its report after closing
  the document. The failed builder, log and status preserve the object-lifetime
  error; this is not a qualified candidate.
- `trial02` used four rivets at every channel/gusset joint. Local seats and STEP
  checks passed, but sixteen material pairs failed because upset heads fouled
  uprights and the diaphragm. Its reports, changed-definition BReps, frozen inputs
  and diagnostic views are retained. Its complete native remains locally in that
  directory and is not included in the checkpoint commit.
- `trial03` uses three rivets per channel/gusset joint and eight on the diaphragm.
  Native/contact/context, STEP, preservation, reproduction and parameter checks
  pass. Its native, STEP files and review records are included in the checkpoint.

`sources.json` preserves the SNL96–97 records and source hashes. `controls.json`
records the current estimated joint construction. Each saved trial retains the
input versions used to produce it; older trial inputs differ from current files.
Restore frozen inputs to their original repository-relative locations in an
isolated workspace when reproducing a superseded trial.
