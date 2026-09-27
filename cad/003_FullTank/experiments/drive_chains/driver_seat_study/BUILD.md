# Adjustable seat-side prototype — 27 September 2026

**`trial06` is the current saved prototype. Support installation is unfinished.**
It adds 38 physical occurrences and seven definitions to the conditional bow/driver
context, giving a local native of 227 occurrences / 88 definitions. The accepted
development and standard tank011 remain unchanged; this is not a complete driver
assembly or a new accepted tank checkpoint.

- [Native assembly](trial06/ControlRebuildTrial.FCStd).
- [Isometric](trial06/visual03/isometric.png) and [underside](trial06/visual03/underside.png).
- [Fixed source-section comparison](trial06/visual03/source_section.png).
- [Installed STEP](trial06/exchange04/RebuiltControlAdditionsInstalled.step).
- [Actual spline control nets and section records](trial06/surface_records/report.json).
- [Nonphysical section-guide native](trial06/surface_records/SeatBackSectionGuides.FCStd).
- [Reviewed source packet](README.md).

## Populated geometry

The one catalogued M791 seat is represented by a fabricated pan/back frame and
two homogeneous upholstery bodies. These three modeled constituents do not count
as three catalogue seats. Hidden upholstery layers and fabrication joints are
not independently identified. The prototype also contains:

- Four SH289E bearings with physical 16.3 mm receiving bores.
- Two estimated SH291X edge clips, kept distinct from SH291C.
- Eight 3/8 ×1⅛-inch bearing rivets, with full source stock retained through
  volume-conserving upset tails and both heads seated on actual material.
- Twenty-one complete half-inch upholstery nails, with receiving holes and
  actual head seats; the estimated back-tack pattern follows the edge seams.

Pan depth 397.782 mm and underside Z1517.638 mm come from the conditional SNL2
section picks. Width 480 mm is an estimate; 490 mm is the tested variation.
Pan stock is 3.175 mm. The back shell uses 3.175 mm projected X thickness and the
padding 24 mm projected X thickness, **not constant normal thickness**. The back
has an explicit quadratic transverse bow and a smooth longitudinal spline loft.
Frame and back padding share one master surface, giving exact supporting geometry.
Their complete saved spline nets, degrees, knots, weights and trims are retained
in native BReps and the surface report. Ten section curves are separate nonphysical
guide geometry. Parameters require regeneration; there are no live expressions.

The bearing flanges, bore size, head profiles, clip form, tack locations and seat
width remain unprinted reconstruction choices. The four bores are open interfaces
for the next support reconstruction. M786/M787 seat extensions, the two M788
angles and their eight 41.275 mm bolts/nuts/locks are not yet added here. SH291C's
application, adjustment travel and the historical shaft/seat relationship remain
open. A collision-free seat above the controls is not proof of support attachment.

## Validation and source comparison

Both widths pass 447 saved-material/interface checks and 96 nearby context pairs
without intersections or mating exemptions. Context includes the complete saved
bow/driver hypothesis, full retained operating-controls development and physical
standard geometry. All 189 inherited context occurrences retain their material,
definitions and frames within the existing 1e-7 mm/matrix tolerance.

A fresh nominal rebuild reproduces 264 archived BReps and 12,878 stable persistent
properties, including all frames and metadata. The native and STEP solids are
checked for actual material differences, validity, closedness, tolerances and
converged mass properties. The initial default Gauss integration failed convergence
for the spline frame and back padding despite zero STEP material differences.
The subsequent Gauss–Kronrod run also failed its reported error bounds.
Independent surface integration exposed missing knot breaks on two extruded
spline faces. V6 includes the surface adaptor continuity intervals; all **39
analytical and invalid-input controls pass**, including an exact two-span spline
extrusion, NURBS conversion and a rigid transform near the installed seat.
`exchange_driver_seat_v2.py` uses that qualified adapter for the frame and back
padding. **All 45 comparisons pass at both widths** (nominal `exchange04`,
variation `exchange02`); acceptance limits and saved geometry are unchanged.

The inspected fixed-section view shows the source-derived pan station and depth,
a flatter/lower cushion crown and remaining back-curve differences. Construction
picks are not independent validation. HB6 remains an uncalibrated perspective
topology reference; no photographic fit, historical position or adjustment-motion
qualification follows from this prototype.

## Diagnostic history and reproduction

The failed initial builds, trial05 and their workers/receipts are retained:

1. A reversed-edge endpoint assumption crossed the backrest loft wire. Explicit
   endpoints corrected it; validity failed before a native could be accepted.
2. Counterbores in the curved back raised kernel tolerances. A shared master
   surface and edge-seam tack placement retain the curved form, 21 full nails and
   original tolerance limits. Earlier tolerance failures remain recorded.
3. Trial05 exposed cushion/back overlap and 8.289 mm³ rivet-tail/web interference
   per rivet. V2 locates the padded front relative to the source curve, revises
   the cushion seam and widens estimated rivet pitch/flanges; no hardware is clipped.
4. Three inherited nut frames differed only through save-time quaternion
   normalization. V2 uses the established1e-7 frame comparison instead of byte
   equality; independent saved-native binding and material checks remain required.
5. Matplotlib's depth sorting produced false surface visibility. Visual03 uses
   the existing depth-buffered native renderer. The original section-plane span
   was also corrected; visual03 reuses the correctly rendered visual02 section.
6. Exchange02's exact serialized-BRep reuse guard failed. It accepted no reused
   comparisons; exchange03 repeats every comparison with GK and fails four mass
   error bounds. Exchange04 passes every comparison using the qualified V6
   adapter; the failed receipts remain intact.

Use absolute worker/output paths through `freecad_headless.py` and fresh output
directories. Run `build_driver_seat_v2.py --output PATH --width 480`, extract with `pump_integration_worker.py`,
then run `check_driver_seat_v2.py`, `check_driver_seat_context.py` and
`exchange_driver_seat_v2.py`. Qualify its mass adapter with
`qualify_control_trimmed_mass_v6.py` before exchange. Generate source views with `render_driver_seat_v2.py`
and depth-buffered views with `render_driver_seat_v3.py`. Record curves with
`record_driver_seat_surfaces.py`. The initial native metadata names the unversioned
builder; **the V2 builder and V2 parts module recorded in input hashes are
authoritative**. Repeat at width 490 and compare a fresh nominal run with
`check_control_rebuild_reproduction.py`.

Next complete the real support-to-bearing chain and reconcile it with the source
section and driver mechanism before integrating this geometry. Keep standard
progression at 308; the separate seat-study snapshot is explicitly diagnostic.

Verify the frozen receipt with `python3 cad/003_FullTank/experiments/drive_chains/verify_driver_seat_study.py`. The diagnostic snapshot is [saved separately](../../../../intermediate_snapshot_iso_seat_study_20260927.png); no accepted tank image is replaced.
