# Connected seat support prototype — 27 September 2026

The [saved native](trial01/ControlRebuildTrial.FCStd) contains **281 occurrences /
97 definitions**, adding 54 physical parts to the preceding seat study. Four
stays now connect the seat bearings to the support plates; separate M788 angles
connect the plates to the two real floor planes. This is a locally checked static
assembly. Historical position, adjusting/locking details and full-tank integration
remain open.

- [Isometric](trial01/visual01/isometric.png).
- [Connections with upholstery hidden](trial01/visual01/connections.png).
- [Fixed source-section comparison](trial01/visual01/source_section.png).
- [Installed STEP additions and revisions](trial01/exchange01/RebuiltControlAdditionsInstalled.step).
- [Reviewed support sources](README.md).

## Geometry and source stock

| Component or interface | Installed construction |
|---|---|
| Four SH289E bearings | Earlier 16.3 mm estimate replaced by a 19.3 mm through bore for the printed 19.05 mm bolts. Flange, rivet holes and other external material preserved. |
| Two front SH289B / two rear SH289D stays | Two shared definitions, placed by rigid transforms. Estimated dogleg strips with 6.35 mm projected transverse stock, 28 mm webs and 18/20 mm end-pad radii. |
| Four upper stay joints | Full 19.05 × 60.325 mm bolts, plain nuts and lock washers. Actual 36.35 mm bearing/stay grip; 1.75 mm bolt protrusion. |
| Four lower stay joints | Full 12.7 × 34.925 mm bolts, plain nuts and locks; actual stay/plate receiving bores and seats. |
| M786/M787 side plates | Shaft bores and frames retained; provisional outlines extended to lower stay joints. Estimated folded feet removed from these definitions. |
| Two separate M788 angles | 6.35 mm stock, 55 mm vertical leaves and a sharp longitudinal bend following the two floor planes. Form and mounting allocation remain estimates. |
| Eight plate-to-angle joints | Existing complete 12.7 × 31.75 mm bolt/nut/lock sets relocated to the vertical receiving leaves. |
| Eight angle-to-floor joints | New complete 12.7 × 41.275 mm bolt/nut/lock sets reuse the actual floor seating frames and holes. |

The upper bolt application still literally names A/B stays, whereas the stay list
and lower bolts name B/D. That printed-source conflict remains explicit. Bolt
lengths are interpreted under the head; thread envelopes, head/nut exteriors,
clearances and compressed lock shapes remain approximations. Nothing is shortened
to avoid an intersection. The dogleg web stock is measured in projected Y, not
claimed as constant-normal rolled strip thickness.

The nominal lower joints use the inherited conditional section picks. A second
complete build raises those four lower joints by 5 mm, testing regenerated stays,
plate outlines and bolt frames without moving the seat or shafts. Parameters
require regeneration; no live expression behavior is claimed.

## Verification and visual interpretation

Both builds pass **607 independent saved-material/interface checks** and **96
strict STEP comparisons**. The nominal context audit checks 269 nearby pairs;
the raised-joint variation checks 267. Both have zero intersections, with no
mating exemptions. Audits include the retained operating controls and physical
standard context. Head, lock, nut, receiver, plate/angle and angle/floor contacts
are checked as actual material interfaces. Negative controls reject the old
undersized receiver and lifted full-stock bolts.

A fresh nominal build reproduces **291 archived BReps and 15,059 stable persistent
properties**, including all definitions, frames and metadata. Unchanged inherited
geometry remains exact; the three revised definitions and 24 relocated fastener
occurrences are declared explicitly.

The inspected source overlay still has a flatter/lower cushion and differing
back curve. Stay endpoints agree by construction. Side-plate outline, separate
angle assignment, absolute shaft/seat placement and source control state remain
unproven. The source image must also be read with its foreground objects:
[original SNL35 identifies Plate 2 callout 56 as a gun-tool box](source_visibility01/source_review.json).
This raises an identification/occlusion question about earlier assumed shaft
landmarks; it does not itself prove the current shaft height or explain the
separate SNL6 grip discrepancies. No camera refit is performed.

The snapshot is retained as a separate diagnostic study. Accepted development
remains 3,582 occurrences / 635 definitions / 442 groups, and accepted image
progression remains 308. The standard tank011 model is unchanged.

## Reproduce and continue

Use absolute worker and output paths through the existing headless launcher.
Run `build_driver_seat_supports.py --output NEW_PATH --lower-z-offset 0`, extract
with `pump_integration_worker.py`, then run `check_driver_seat_supports.py`,
`check_driver_seat_context.py` and `exchange_driver_seat_v2.py`. Repeat at offset
5 mm. Compare a fresh nominal build using `check_control_rebuild_reproduction.py`.
`render_driver_seat_supports.py` generates the inspected views. Verify the frozen
study with `verify_driver_seat_support_study.py`.

Next positively identify the SNL2 shaft/lever landmarks and occluding tool-box
outline, compare them with SNL6 and HB6, and resolve the absolute driver layout
before promoting a coupled bow/driver/seat revision. Complete the remaining
adjustment/locking fittings, including the separately listed SH291C, as evidence
allows. Mechanical connectivity alone does not settle these remaining details.
