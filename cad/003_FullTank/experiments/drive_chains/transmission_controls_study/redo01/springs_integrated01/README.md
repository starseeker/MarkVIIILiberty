# Rebuilt M564 return springs and M567 washers

This development checkpoint adds **four installed spring states and eight washers**
to the reviewed Gemini prefix: **3,294 physical occurrences / 575 definitions /
365 assembly groups**. The four spring definitions are installed configurations
of the same source family M564. The eight washers share one M567 definition.

[Open the native assembly](PowertrainControlRebuild.FCStd) or inspect the
[isometric](isometric.png) and [attachment detail](spring_detail.png).
The source-supported counts and estimated geometry are separated in
[the source review](../spring_source_review.json). Each front spring eye wraps the
existing fork socket behind its jam nut. Each rear end crosses the actual M4136
bracket hole and turns outside the cheek. These are explicit static mounting
hypotheses; the drawings do not recover their exact hook shapes or spring rate.

Nominal 2.6 mm wire / 1.5 mm compressed washer stock and a 2.4 / 1.4 mm variation
each pass 186 independent interface/stock checks, 68 context-pair comparisons with
no mating exemptions, and 17 strict definition/installed STEP comparisons. The
actual exported solids retain material in both directions and independently
converged volume/centroid measurements. Failed sweep/export/measurement controls
are retained; acceptance thresholds were not relaxed.

Integration passes 89 checks, preserves every inherited definition, frame, owner
and persistent property except declared group additions/checkpoint descriptions,
and reproduces all 1,757 archive BReps and 158,368 persistent properties exactly.
The inspected prototype views are reused through those strict transfer checks;
they are not presented as newly rendered images. Four uniquely named progression
files bring the accepted sequence to 258; Gemini's experimental 255–286 retain
their separate provenance.

The fixed SNL6 camera still exposes inherited lever/profile and spring-height
disagreements. Successful local fit does not establish historical spring geometry.
The full withheld commit is **not yet redone**: M575/M563, center/forward controls,
shaft supports and clutch links remain. The latest source review also rejects the
draft intermediate-shaft station because it contradicts the printed 49½-inch
M574 front-rod length. See [route reconciliation](../long_controls_sources/README.md).
Standard tank011 and pose work remain outside this checkpoint.

Recover/verify without rerunning the kernel:

```sh
python3 cad/003_FullTank/experiments/drive_chains/verify_control_rebuild_checkpoint.py
```

Regeneration uses `trial_control_rebuild_springs_v3.py` with the nominal/variation
JSON controls, then `build_control_rebuild_additions.py`. Dimensions require
regeneration; metadata is not a live constraint system. `qualification.json`
binds the native, source evidence, checks, frozen scripts and progression files.
