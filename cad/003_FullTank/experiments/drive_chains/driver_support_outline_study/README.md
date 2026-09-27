# Seat-support fore-edge correction — 27 September 2026

The [saved coupled native](trial02/ControlRebuildTrial.FCStd) extends the two
support plates and separate M788 floor angles to the near-vertical forward edge
visible below the front seat stay. The preceding shaft-derived footprint left
that edge strongly diagonal. The new construction follows the fixed source
section more closely while preserving all shaft, seat, stay and rod geometry.

- [Isometric with wireframe bow](trial02/visual01/isometric.png).
- [Exposed support connections](trial02/visual01/connections.png).
- [Unchanged source-section projection](trial02/visual01/source_section.png).
- [STEP of changed installed parts](trial02/exchange01/RebuiltControlAdditionsInstalled.step).

The footprint now reaches X7696.364 mm, the existing front stay's lower joint
plus its estimated 24 mm plate margin. The angle follows the actual floor seam
and bend. In the first trial, the fourth mounting bolt head straddled that bend,
causing two **28.444475 mm³** intersections. That rejected trial is retained.
The corrected unprinted mounting pattern places the front pair 30 and 60 mm
aft of the bend. Complete bolts, locks and nuts move with the actual holes;
neither bolt stock nor receiving material is clipped to conceal interference.

Compared with the qualified coupled station, exactly **five definitions change**:
two plates, two angles and floor1. Exactly **24 mounting-hardware occurrences
move**. All 120 other definition BReps are byte-identical, and all other physical
frames and definition references remain unchanged. Local occurrence/definition
counts stay **394 / 125**. The generator's older parent-relative report still
lists nineteen revised definitions; the explicit delta checker records the five
changes relative to the immediately preceding coupled baseline.

Nominal and a **+5 mm fore-edge extension** each pass:

- 1,075 saved material/joint checks, 31 additional contact/floor checks and eight
  baseline-preservation/fore-edge/bend-clearance checks.
- All **1,174 nearby pairs** in the full retained context, with no exemptions.
- **34 strict STEP comparisons**: five changed definitions and 29 changed or
  relocated installed occurrences.

The STEP worker compares every canonical BRep hash and occurrence frame with the
bound, qualified coupled baseline. It exports the measured changes and retains
the original strict material, tolerance and converged-mass predicates. Unchanged
geometry inherits its existing qualification; a new whole-assembly STEP export
is not claimed. This avoids repeating 295 unaffected comparisons per variation.
A fresh nominal build reproduces 391 archived BReps and 20,529 persistent properties.

The three new local/source images were inspected; the clutch comparison is
byte-identical to its previously inspected image. The fore-edge is now a reviewed
local approximation suitable for full-hierarchy integration. Exact plate margins,
angle stock/pitches, shaft identities, handle datum, M772 bend and seat curves
remain approximate. [Seat-fitting review](../seat_adjustment_study/README.md)
retains SH291C/D/F as unresolved identities; it does not invent an adjusting lock.
No source camera is refitted, and no motion or historical certainty is claimed.

Verify with `verify_driver_support_outline_study.py`. Build with
`build_driver_support_outline_v2.py --output NEW_PATH --support-front-offset 0`
or offset5 through the existing headless launcher. Extract, run the coupled,
supplementary V3, context and outline-delta checkers, then
`exchange_driver_support_outline.py`. All worker/output paths must be absolute.

Next integrate the complete coupled bow/driver/seat station into the retained
development hierarchy, verifying unaffected material, ownership and frames.
Then populate the remaining identifiable foot and reverse controls. Preserve the
full printed rods and the explicit seat-fitting gaps while doing so. Accepted
development, standard tank011 and accepted image progression308 are unchanged by
this local study; a separately named diagnostic snapshot records the improvement.
