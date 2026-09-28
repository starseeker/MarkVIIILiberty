# Reverse latch — source graph and nonphysical route probes

This packet starts the next construction step after the mounted quadrant. It
does **not** add accepted latch parts. The [route report](reverse_latch_routes01/report.json)
uses the unchanged `reverse_quadrant03` geometry, the authoritative coupled
station and standard context, totaling 9,006 physical occurrences. It tests
clearance witnesses without modifying any receiver or source camera.

The [source review](reverse_latch_source_review01.json) binds the original
inventory and inspected HB113 trigger detail. M739, M740, M742, M744 and M745
are shared by the reverse and both speed handles. The drawing shows the speed
handle's trigger and rod beside its blade; applying that arrangement to the
reverse lever is an inference. Its apparent M737 leader remains inconsistent
with catalogue M739. Upper pin assignments and the fixed spring seat are open.

## Corridor results

The retained lever definition frame supplies local coordinates: Z runs up the
hand side, Y is transverse to the tank, and X crosses the blade in its side
plane. A 6.35 mm diameter cylinder from Z310 to Z560 models a possible straight
rod envelope. That diameter follows the quarter-inch nut application; the rod
length, slope, endpoints and lateral offset remain construction estimates.
The slope follows the earlier unprinted upper-hand outward inclination.

| Local X offset | Saved-material result |
|---|---|
| 0 mm | Rod intersects the blade by 2,339.472513 mm³ and the front stay bolt by 213.707737 mm³; lower offset path also hits that bolt by 51.580537 mm³. |
| +20 mm | Rod and lower offset cylinders clear all tested physical context; promising construction candidate only. |
| −20 mm | Rod intersects the front seat stay by 3.435869 mm³. |

The positive-X candidate spans `[20, −32.405688, 310]` to
`[20, −69.767742, 560]`, a 252.776429 mm cylindrical envelope. Its rod clears the
lever by 3.457552 mm and the tested stay by 5.330548 mm. The lower offset path
clears the lever by 2.552345 mm and quadrant by only 0.576259 mm. These are
distances to the named saved solids, not a global minimum-clearance guarantee
for a larger finished assembly. All dimensions are in millimeters.

A separate 5.85 × 5.85 mm tooth witness enters the selected 6.35 mm detent with
0.25 mm lateral clearance and 1.5 mm bottom clearance. It has 11 mm radial
height and passes four context pairs. Moving it 2 mm below its position or
0.6 mm across the notch wall produces actual quadrant intersections, confirming
that the checks distinguish engagement clearance from penetration. No locking
strength, spring force, sliding stroke or moving-envelope claim follows.

## Visual review and next build

The first three renders conceal the selected route behind the blade. Three
opposite-side views expose it; all six are retained and inspected. The
[outboard isometric](reverse_latch_routes01/visual02/isometric.png) shows the
estimated straight path; the [detent detail](reverse_latch_routes01/visual02/detent_detail.png)
shows its lower offset beside the front stay and actual notch. Purple shapes
are nonphysical witnesses, with no BOM count or STEP qualification. There is no
new accepted visual-progression image for this probe.

Build the actual M780 pawl and M742 guide together around this candidate before
committing to the upper trigger dimensions. The guide, its real receiving bores
and two complete 5/16 × 1¾ inch rivets require more space than the cylinders.
Check rivet length-datum/formed-tail interpretation explicitly; do not silently
equate raw rivet length with assembled grip or remove stock to make the fit pass.
Shared M742 geometry must also remain applicable to the two speed handles.
The nearby stay and small quadrant clearance may require a coupled revision.

Then add the actual M778 end/quarter-inch nut, M739 trigger, two M740 pins with
full 1/16 × 3/8 inch cotters, M744 spring and M745 pin. Resolve integral pivot
and spring-seat ownership, preserve the source hand/bell reaches and complete
short rod, and recheck actual saved material, context, source views, STEP and a
useful parameter variation. The existing source-profile and foot-link conflicts
remain open. The accepted tank assembly is unchanged.

```sh
python3 cad/003_FullTank/experiments/drive_chains/verify_driver_reverse_latch_routes.py
```

Reproduce the probe with `probe_driver_reverse_latch_routes.py --controls
reverse_latch_routes_controls01.json --output NEW_DIRECTORY` through the
headless launcher, using absolute paths. Render the results with
`render_driver_reverse_latch_routes_v2.py --probe NEW_DIRECTORY`. Keep the
bound inputs, failed alternatives and original outputs unchanged.
