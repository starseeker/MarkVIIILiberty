# Driver controls — active continuation

Current checkpoint: [driver support foundation](mount_integrated01/README.md),
**3,475 occurrences / 611 definitions / 414 groups**. The preceding
[completed withheld-control redo](../redo01/clutch_swing_integrated02/README.md)
remains intact. The original driver draft is preserved on
`review/gemini-front-controls-20260926`.

The foundation adds 36 driver components: two transverse shafts, four reused
nuts, four source-length split pins, two partial seat-support plates and eight
three-part floor mounting sets. Two existing standard floors are imported with
four receiving bores each. Nominal/variation each pass144 local checks,
123 context pairs and47 STEP comparisons. Full reproduction and inherited
material preservation pass; four inspected views extend the visual progression.

[Source review](mount_source_review03.json) corrects the initial assignment:
M746/M747 are operating-lever fulcrums, while M786/M787 are paired seat-support
plates. HB148 also distinguishes the two37-inch operating levers from the four
shorter selector bodies. Do not copy the preserved draft's four full-length
selector handles or invented floor blocks.

The [local SNL6 registration](mount_registration01.json) is reused for driver
plan comparisons. Its three construction picks determine local scale, orientation
and shaft separation; they are not validation holdouts. Broken long rods prohibit
whole-layout scaling. Heights, floor mounting, full plate profiles and actual
seat attachment remain estimates/open interfaces.

The earlier [M782 part study](shaft01/part_qualification.json) remains a valid
**uninstalled** five-part experiment with28 checks,9 context pairs and7 STEP
comparisons per setting. Its X7280/Z1020 station and19.05mm future support grip
are superseded by the installed foundation hypothesis. Its frozen source notes
are retained as history, including the subsequently corrected M746/M747 assignment.

Next: reconstruct actual M784 swing-link and M760 low-speed suspension receivers,
then M789A/B connections and the driver lever/selector/brake interconnection.
Use the retained printed M574 length and actual receiving geometry to confirm or
reopen the provisional driver station. M775 is a spring-link distance piece;
HB12 oil points do not establish separate grease nipples. Complete seat support,
M785 spring anchor, remaining controls and front rods are still required.

Read-only recovery:

```sh
python3 cad/003_FullTank/experiments/drive_chains/verify_control_rebuild_checkpoint.py --candidate cad/003_FullTank/experiments/drive_chains/transmission_controls_study/driver_redo01/mount_integrated01
```

Standard tank011 and the original Gemini files remain preserved. This checkpoint
qualifies local static geometry and reproducibility; it does not establish
historical exactness, complete driver controls or finished tank geometry.
