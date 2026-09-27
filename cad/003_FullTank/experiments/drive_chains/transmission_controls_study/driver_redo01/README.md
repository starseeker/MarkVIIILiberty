# Driver controls — active continuation

Active next-step trial: [operating-handle gate interfaces](handle_gates01/README.md).
Its four conditional upper-jaw revisions pass local, context and exchange checks,
but require complete handle/pivot geometry before integration. No new tank parts
are counted. Full assembly remains the checkpoint below.

Current checkpoint: [high selectors and complete rods](high_integrated01/README.md),
**3,572 occurrences / 628 definitions / 439 groups**. Both high selectors, their
source-length M789A rods and shared M576 long rods now have complete physical
joints. Every preceding shape and frame remains fixed. The high-eye source
position disagrees by 13.53 px and remains explicitly unresolved.

See [source review](high_source_review01.json), [trial record](high_trials.md)
and [current recovery state](../../../../CURRENT_WORK.json). Next build actual
operating-lever fulcrums/handles and selector engagement, then remaining controls.

The following entries are historical checkpoints and include superseded assumptions.

Current checkpoint: [low selectors and upper joints](selector_integrated01/README.md),
**3,534 occurrences / 625 definitions / 428 groups**. The two low selectors now
have complete M790 joints. M762 is corrected to the source's diagonal upper
connection; the preceding bowed profile was the foot-brake bridle outline.
Existing shaft stations, low knees and complete rods remain fixed.

See [source review](selector_source_review01.json), [trial dispositions](selector_trials.md)
and [current recovery state](../../../../CURRENT_WORK.json). Next build the high
selectors and source-length M789A rods, then the remaining driver mechanisms.

The following entries are historical checkpoints and include superseded assumptions.

Current checkpoint: [low-speed front receivers and rods](low_integrated01/README.md),
**3,528 occurrences / 622 definitions / 426 groups**. Thirty new parts complete
the hanging low links and source-length long rods. The M762 front selector
coupling is still open. Source review corrects previously conflated M784/M763
picks; old eye coordinates and driver station are superseded.

See [source review](low_source_review02.json), [retained trials](low_trials.md)
and [current recovery state](../../../../CURRENT_WORK.json). Next build the low
selectors and real front coupling, recording the HB/SNL handed-name conflict.

The following notes describe the preceding checkpoint and remain historical.

Current checkpoint: [complete driver front clutch chain](linkage_integrated01/README.md),
**3,498 occurrences / 615 definitions / 419 groups**. Its23 additions include all
four M784 links and the complete front clutch chain. The earlier
[driver foundation](mount_integrated01/README.md) and
[completed withheld-control redo](../redo01/clutch_swing_integrated02/README.md)
remain intact. The original driver draft is preserved on
`review/gemini-front-controls-20260926`.

The linkage increment passes251 local,168 context and69 STEP checks per stock
setting; full integration/preservation/reproduction pass. Revised support heights
admit the actual deeper links. [Source review](linkage_source_review06.json) and
[trial dispositions](linkage_trials.md) record the handle/nose compromise and
unresolved historical geometry. Five new inspected views bring progression to287.

The following foundation notes describe the preceding checkpoint; its shaft
station and plate heights are superseded by the new linkage hypothesis.

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

Next: build M760 low-speed suspension links and M762/M763 toggles, then close the
two M574 rods at their printed stock length. Actual receivers must confirm or
reopen the provisional driver station. Continue selectors, M789A short rods,
high/reverse and brake interconnection, M775 distance pieces, spring anchors and
complete seat support. Five M576 applications plus two M574 and one M571 reverse
pipe give eight front long connections; one M576 is now populated.

Read-only recovery:

```sh
python3 cad/003_FullTank/experiments/drive_chains/verify_control_rebuild_checkpoint.py --candidate cad/003_FullTank/experiments/drive_chains/transmission_controls_study/driver_redo01/linkage_integrated01
```

Standard tank011 and the original Gemini files remain preserved. This checkpoint
qualifies local static geometry and reproducibility; it does not establish
historical exactness, complete driver controls or finished tank geometry.
