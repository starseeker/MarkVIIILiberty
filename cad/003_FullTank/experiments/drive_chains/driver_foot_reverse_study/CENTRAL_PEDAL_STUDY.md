# Central pedal and bridle — checked CAD study, connections still unresolved

The [central03 native](central03/ControlRebuildTrial.FCStd) contains ten new
physical occurrences and two exact retained shafts. Seven new definitions form
the pedal, bridle, suspension, sleeve, distance tube, bolt and cotter. The front
M790 pin/keeper and rear nut reuse complete existing definitions and metadata.
Two bridle spline guides remain outside the physical hierarchy.

Both nominal and +1 mm bridle-stock/fork-throat builds pass 63 saved-material,
dimension, joint and metadata checks, 34 nearby-pair comparisons in an
8,997-occurrence context, and 17 strict native/STEP comparisons. A fresh nominal
build reproduces all 40 archive BReps and 1,501 persistent properties exactly.
These are CAD checks of a selected hypothesis, not historical proof of the joints.

HB149's 35¼-inch overall length and 8-by-5-inch pad are retained. Transferring
those dimensions to later M764A and measuring overall length along the unrotated
long-arm axis are explicit interpretations. The pedal angle, sections, forked
bell arm, U-bridle profile, pin assignment, sleeve position and hidden journal
stack are estimates. Dimensions update by regenerating the document, not by live
FreeCAD expressions.

The proposed chain is M782 → pedal → M790 → M765 → M767/M766 → M770 → M795/M783.
Actual shafts, bores, pin/head seating, rear nut/head seating, spacer-end contact
and complete source-length cotter material are checked. The M767 bolt length is
estimated; the printed 1½-inch cotter length is retained as formed leg centerline
length. HB190 and SNL137 list three M790 pins without identifying this application.
The third pin's assignment is therefore provisional. HB190's M776 “foot-brake
bridle pin” wording conflicts with the specific SNL control-lever application;
the existing pair is preserved and no extra M776 pair is added.

Five [inspected saved-native views](central03/visual01/visual_review.json) show
the group, retained control context, rear joint and fixed HB113/SNL6 comparisons.
The plan broadly follows the U layout, but the pad is shifted and the side-view
pedal angle differs substantially. No source camera was refitted. Experimental
isometric snapshots are recorded separately from accepted progression 314.

The [combined-study diagnostic](central_compatibility01/report.json) checks all
20 pairs between the central group and earlier M769 profiles. Each M769 profile
intersects the bridle by approximately 4,678.809 mm³. Both hypotheses cannot be
used together unchanged. This is a part-boundary/joint-graph question; moving
the profiles sideways merely to eliminate interference would not resolve it.
The eight M771 members, rear M769 attachment and SH946F connection remain open.
No complete braking function, installation path or assembly integration is claimed.
`coupled_driver_integration/integrated01` remains authoritative; tank011 is unchanged.

Next trace the source leaders and distinguish M765 from M769 outlines before
revising either profile. Constrain the connection graph by the eight M771 pieces,
existing selector eyes, complete pin inventory and HB148's neutral-selective
action. Then locate the special forks and full shared M576 rods using the free
66.675 mm intermediate eyes. Preserve the earlier stock/closure constraints.
Qualify the connected union before integration; reverse controls follow.

Reproduction uses the established headless launcher and absolute paths:

```text
build_driver_central_pedal_v3.py --controls .../central_controls01.json --output NEW
pump_integration_worker.py extract --input NEW/ControlRebuildTrial.FCStd --output NEW/isolated/manifest.json
check_driver_central_pedal_v2.py --candidate NEW
check_driver_seat_context.py --candidate NEW
render_driver_central_pedal.py --candidate NEW
exchange_control_rebuild_clutch_swing.py --candidate NEW
```

Use `--stock-offset 1` for the tested variation. The existing generic exchange
worker selects standard Gauss for all central-group parts. The retained diagnostic
exchange sequence was `exchange_driver_central_pedal.py` followed by
`exchange_driver_central_pedal_v3.py`; the first retains its diagnosed specialized
integration failure, and the latter checks its unchanged STEP bytes with standard
adaptive Gauss. All numerical/material acceptance criteria remain unchanged.
`check_control_rebuild_reproduction.py` compares a fresh build.
`verify_driver_central_pedal_study.py` verifies the frozen study receipt.

Retained failures are useful controls. `central01` has three rear-joint clashes;
flat rear seating stock and a full-length cotter routed through the actual crown
slots resolve them in `central02`. Its pedal's general geometry transform converts
all 40 surfaces to splines and gives conservative bounds; `central03` retains
analytic definition surfaces and places the rigid rotation on the occurrence.
The old/new installed pedal has zero material differences in both directions.
The first cotter witness incorrectly centered spheres on flat ends. Its successor
checks interior witnesses, complete straight/tail stock and actual end-face area,
and rejects shortened legs. See [measurement diagnostics](central_mass_diagnostics01/README.md).
