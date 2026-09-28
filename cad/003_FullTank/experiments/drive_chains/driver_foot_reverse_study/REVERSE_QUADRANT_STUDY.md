# Mounted reverse quadrant — checked static study

The [reverse_quadrant03 native](reverse_quadrant03/ControlRebuildTrial.FCStd)
retains the complete checked reverse lever and third short-rod connection, adds
M779 and its eight mounting parts, and drills two actual attachment bores in the
starboard support plate. It contains 23 physical occurrences and 15 definitions.
Relative to the authoritative coupled station there are 19 new occurrences,
six new definitions and one changed definition. The nine-part quadrant increment
is isolated; the latch and long reverse route remain unfinished.

Nominal and +1 mm quadrant-stock builds each pass 92 independent saved-part
checks, 116 nearby-pair comparisons in a 9,006-occurrence context, and 27 strict
native/STEP comparisons. No mating exemptions, stock clipping or relaxed
material/tolerance criteria are used. A fresh build reproduces all 45 archived
BReps and 2,074 persistent properties exactly. All 13 preceding reverse-study
occurrences retain their material, frames and source metadata. The support plate
changes only at the two attachment bores and in the corresponding reconstruction
notes. Dimensions update by regeneration.

## Evidence and approximations

The [source packet](reverse_fittings_sources01/report.json) retains 28 selected
inventory rows, their enclosing pages and 20 source views. Original SNL030:010
specifies two 3/8 × 2¼ inch bolts with plain nuts and lock washers for M779;
SNL133:039 specifies two M781 distance pieces. Full 57.15 mm bolt stock is
retained, interpreting the printed length as the under-head length. Threads are
nominal envelopes. The selected stack leaves 15.31875 mm projecting beyond each
nut; historical stack dimensions and threaded length remain unresolved.

HB94 shows a curved notched quadrant and two attachments, but is schematic and
oblique. It does not supply a metric camera fit. The existing HB113 side
registration supplies two construction picks; the forward attachment is hidden
and estimated. Neither pick is an independent validation landmark. No source
camera was refitted. The assignment to the starboard support plate is inferred.
Radii 235/275 mm, 35–112° arc extent, three detents, 6.35 mm plate stock, ear
forms and mounting spacing are documented approximations. The old apparent
25.23-pixel plan hand-end discrepancy remains unresolved.

The quadrant inner face is at Y = −259 mm. M781 length derives from the actual
gap to the support: 17.225 mm nominal and 16.225 mm with the thicker quadrant.
The saved full profiles clear both the lever and the existing rear seat-stay
bolt. Static clearance does not establish historical placement or movement.

## Retained failures and review

`reverse_quadrant01` loses 2.959306 mm² of the forward spacer's support seat,
also loses part of the washer seat, and intersects the rear seat-stay bolt by
586.559520 mm³. The forward construction pick moves two source pixels aft to
place the complete seat on real support material.

`reverse_quadrant02` and its thicker-stock variant pass the local attachment
checks but intersect the unchanged reverse lever by 51.568123 mm³. The retained
[lane probe](reverse_quadrant_lane_probe01/report.json) evaluates complete
quadrant profiles between both fixed neighbors. The third trial clears them
without trimming stock or changing neighboring geometry.

Seven saved views were inspected: isometric, retained context, mounting detail,
two fixed-source comparisons and two section attempts. The first section camera
obscures its cut face; the [corrected axial section](reverse_quadrant03/section02/bolt_section.png)
exposes the full bolt, quadrant, spacer, support, lock washer and nut. Display
sectioning does not alter the physical model. The [visual review](reverse_quadrant03/visual01/visual_review.json)
records these limits. Three diagnostic snapshots preserve this stage separately
from accepted tank progression 314.

## Next construction

Use [the latch source review](reverse_latch_source_review01.json) to develop
M739 trigger, two M740 pins and their full 1/16 × 3/8 inch cotters, M778 rod,
M744 spring, M745 spring pin, M780 pawl, M742 guide, the quarter-inch nut and two
full 5/16 × 1¾ inch guide rivets. Receiving holes, spring seats, trigger pivots
and actual detent engagement must be modeled and checked with the surrounding
station. The figure's apparent M737 trigger leader conflicts with catalogue
M739; spring-seat ownership and the exact joint graph are still hypotheses.

Then reconcile the long reverse route and the separate M765/M769/M771 foot-link
conflict. The coupled station remains authoritative; tank011 is unchanged.

Verify this frozen packet with:

```sh
python3 cad/003_FullTank/experiments/drive_chains/verify_driver_reverse_quadrant_study.py
```

Regenerate into new directories with `build_driver_reverse_quadrant.py`, using
`reverse_quadrant_controls03.json` and optional `--stock-offset 1` through the
headless launcher. Extract with `pump_integration_worker.py extract`; check with
`check_driver_reverse_quadrant.py`, `check_driver_seat_context.py`,
`exchange_driver_reverse_quadrant.py` and `check_control_rebuild_reproduction.py`.
Use absolute paths and preserve the bound workers and original result folders.
