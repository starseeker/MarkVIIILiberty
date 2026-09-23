# I03 — clutch thrust balls, retainer and spring-stop ring

Status: **qualified partial reconstruction with documented approximations**,
22 September 2026. Parent is the qualified,
corrected 1,549-component clutch core; the rejected first core is not a parent.

[Native assembly](../experiments/drive_chains/clutch_thrust_build/TransmissionWithClutchThrust.FCStd) ·
[source comparison](../experiments/drive_chains/clutch_thrust_build/source_review/index.html) ·
[qualification](../experiments/drive_chains/clutch_thrust_build/qualification.json)

Add SH998C retainer, thirty quarter-inch steel balls and SH998A spring-stop ring
as 32 separate physical occurrences. Reuse one ball definition. SNL164:002 is
the retainer **assembly** heading, not another physical part. Refine the existing
SH998B thrust collar with receiving race geometry, preserving its bearing seat,
shaft bore, housing fit and separation from the external SH861E ring.

## Evidence and interpretation

Full SNL Plate21, original pages 164 and 165, and HB116–117 were inspected.
An enlarged inspection of the lower section retains the full figure as context:
callout 28 identifies the thrust collar, 29 the ball-retainer assembly between
the opposing members, and 4 the spring-stop ring carrying the plunger end.
The catalogue prints one SH998C retainer and thirty steel balls of 1/4-inch
diameter. SH998A is distinct from the SH861E external snap ring. The handbook
uses different marks for the corresponding mechanism; no universal identity
equivalence is inferred.

The next native will use a forward-facing annular race pocket on SH998B and an
opposing annular boss on SH998A. Thirty balls share a pitch circle and a thin
perforated cage. Rounded race grooves maintain static axial contact while the
cage clears the balls. Groove radius, pitch circle, cage construction, ring
contour, stock and clearances are reconstruction estimates. The source does not
establish a manufacturing drawing, preload, load capacity or cage assembly method.

The stop ring has six provisional plunger holes; their diameter transfers the
HB115 3/8-inch plunger size with an inferred clearance. The hole circle and phase
must be revisited with the six spring/plunger sets and cone support. Those
interfaces remain unfinished; a fitted ball mechanism does not close that work.

## Acceptance

- Correct native hierarchy, shared ball definition, source identities and 32
  new occurrences; only the named thrust-collar definition may change.
- Valid single solids, actual cage pockets and six actual stop-ring holes.
- Printed ball diameter and count; all ball centers on the documented circle.
- Material and void checks, opposite axial race contacts and no cage interference;
  displaced balls must hit the appropriate race to exercise the negative controls.
- Full affected-part interference against the combined native and standard
  physical tank context, preserving the qualified parent and standard delivery.
- Native save/reopen, definition and installed STEP comparison, coherent size
  variations and a fresh builder run bound to source/input hashes.
- Installed, race, cage and axial-section views compared with the original full
  figure. Preserve a new numbered progression image at the accepted visual stage.

## Implemented geometry and verification

The saved combined assembly now has **1,581 physical occurrences**, including
the 32 additions. The existing thrust collar is refined; all 1,548 other parent
occurrences retain their geometry and placement. `ClutchBallRetainer` is a native
assembly container with one cage and 30 links to one ball definition. The
spring-stop ring belongs to the adjacent thrust assembly. No external native
dependencies are required by this combined document.

| Interface | Selected geometry | Evidence or limitation |
| --- | --- | --- |
| Balls | 30 × 6.35 mm diameter | SNL8:016 and 164:005 describe the same set |
| Ball circle | 174 mm diameter, X1008.125 mm | Estimated in the existing transmission frame |
| Cage | 1.5 mm stock; 30 × 6.6 mm holes | Section and clearance estimated; one solid |
| Rear race bottom | X1004.95 mm | 2 mm stock remains ahead of the housing front |
| Groove radius | 3.4 mm with offset centers | Approximate concave surfaces giving axial tangent contact |
| Stop-ring rear face | X1011.30 mm, 6 mm plate | Boss projects aft to X1010.225 mm |
| Stop-ring outer diameter | 248 mm | Estimated pending complete plunger/cone interfaces |
| Plunger holes | Six × 9.825 mm on 228 mm circle | HB diameter transfer plus inferred clearance/phase |

All 95 affected material pairs pass against the full combined model and standard
physical tank context. The saved model passes 460 independent checks; four
definition STEP comparisons and 33 placed-solid mass/centroid comparisons pass.
Two coupled pitch-radius (±0.5 mm) and race-depth (±0.2 mm) trials each pass 95
pairs and 90 contacts while retaining the printed ball size and quantity. A fresh
output-directory rebuild passes the same saved-model and STEP checks. Seven fine
native/source views were inspected. These checks qualify the stated static
approximation, not manufacturing fit or operating loads.

Two whole-solid ball/race distance queries returned about 0.075288 mm despite
shared boundary points within 3e-14 mm. A diagnostic verified material behind
those points and positive interference after a 0.01 mm axial shift. The failed
reports and reproducer remain in `diagnostics/whole_shape_distance`. Acceptance
now requires the expected contact point on **both actual saved surfaces**, race
material immediately beyond it, and zero nominal overlap. Whole-solid distances
remain recorded diagnostics; no clearance or Boolean tolerance was relaxed.

The detail-render adapter refines tessellation to 0.04 mm for clearer balls and
pockets while retaining the established projection and placement checks. The
standard delivery renderer and native geometry remain unchanged.

Reproduce the packet in order:

```bash
python3 cad/003_FullTank/experiments/drive_chains/clutch_thrust_sources.py
python3 cad/003_FullTank/experiments/drive_chains/clutch_thrust_build.py
python3 cad/003_FullTank/experiments/drive_chains/check_clutch_thrust.py
python3 cad/003_FullTank/experiments/drive_chains/check_clutch_thrust_variants.py
python3 cad/003_FullTank/experiments/drive_chains/render_clutch_thrust_review.py
```

Qualification additionally requires actual visual review and a receipt for a
fresh build/check in a separate output directory; prior receipts do not cover
regenerated native files. `qualify_clutch_thrust.py` verifies those bindings.

Cones/linings/rivets, spring-plunger sets, crankshaft/flywheel engagement and the
clutch-stop band follow; standard geometry remains the priority before poses.
The current stop ring lacks its future plungers and their complete retaining
interfaces. Tank milestone011 and its transparent-hull companion are preserved.
