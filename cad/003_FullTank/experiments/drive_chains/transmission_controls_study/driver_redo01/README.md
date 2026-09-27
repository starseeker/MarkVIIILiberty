# Driver controls resumed after the withheld control redo

The accepted full assembly remains [clutch_swing_integrated02](../redo01/clutch_swing_integrated02/README.md):
3,437 physical occurrences,602 definitions,409 groups. Its six corrected increments
close the functional scope of withheld `b19e16e5`. The driver controls are a separate
continuation of the preserved draft on `review/gemini-front-controls-20260926`.

The first [native part study](shaft01/ControlRebuildTrial.FCStd) contains M782,
two shared M313 nuts and two 3/16 × 1½-inch split pins. HB148 specifies a24¾-inch
shaft length and1.497-inch diameter; SNL213 supplies identity and retainer counts.
[Source review](source_review02.json) distinguishes these from estimated end forms.
The existing M313 definition is reused unchanged. The19.05mm space between each
shoulder and nut is a future receiver interface, not a physical part.

Both nominal and receiver-grip/bend variants pass28 saved-stock checks,9 neighboring
material pairs and7 strict STEP comparisons. A fresh nominal build reproduces the
saved geometry and persistent properties. [Isometric](shaft01/isometric.png) and
[end detail](shaft01/end_detail.png) were inspected. The63-dependency
[part qualification](shaft01/part_qualification.json) explicitly excludes mounting,
full assembly integration and final historical end-retainer interpretation.

The short keeper is outside the nut face; no castle-slot engagement is claimed.
Final M746/M747 grip, real floor contacts and M783 second-shaft layout must be
resolved together before this study can enter the full model. The source controls
show two long operating handles and four separate shorter selector forms; the
preserved draft's four37-inch selectors must not be copied.

Next: reconstruct M746/M747 and M783 supports from HB12/HB92/SNL6, establish actual
front rod receiving axes, then retain printed M574 stock length while closing the
forward controls. Floor1/2 slope toward the driver; the draft Z940 feet and Z890
low-rod target do not establish physical mounting or clearance. Threads remain
nominal smooth envelopes. No full-tank or progression checkpoint is changed by
this uninstalled study.

Read-only recovery:

```sh
python3 cad/003_FullTank/experiments/drive_chains/verify_driver_fulcrum_shaft.py --candidate cad/003_FullTank/experiments/drive_chains/transmission_controls_study/driver_redo01/shaft01
```

Builder `trial_driver_fulcrum_shaft.py`, controls `shaft_controls01.json`, variation
`shaft_variation01.json`. Run with the established FreeCAD headless launcher and
new output directories; saved evidence refuses overwrites.
