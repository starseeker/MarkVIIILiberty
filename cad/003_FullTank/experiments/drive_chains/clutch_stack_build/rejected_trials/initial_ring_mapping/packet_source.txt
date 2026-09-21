# I03 — nested clutch bearing, sleeve, keyed support and retention

Status: **checked approximate main-clutch core; operating mechanism incomplete**, 21 September 2026.
[Native assembly](../experiments/drive_chains/clutch_stack_build/TransmissionWithClutchStack.FCStd) ·
[source comparison](../experiments/drive_chains/clutch_stack_build/source_review/index.html).
This stage populates the previously vacant main collar with the bearing, sleeve
and retaining ring, and adds the four keys and outer cone-supporting collar.
The combined transmission/pump candidate contains **1,548 physical components**.
Eight are new; SH999A changes to receive them. The other 1,539 parent components
retain their geometry and placement. The complete clutch and tank remain unfinished.

## Arrangement and source decisions

The SNL section shows a long bearing with an enlarged middle bore, a larger rear
bore surrounding the sleeve, and a smaller forward journal bore. The sleeve
overlaps the rear bearing band and extends into the middle relief. Placing the
sleeve and bearing end-to-end would contradict this arrangement.

The comparison preserves the original opposite HB/SNL orientations and shows
both the newly populated and preceding empty sections. Panel scales are
independent. The original pages 17, 67, 114, 165 and 217 confirm the selected
marks and quantities. Pages 164 and 165 also retain the next thrust/ball/stop-ring
inventory; those items are not counted as installed in this checkpoint.

| Item | Survey identity | Quantity | Source |
|---|---|---:|---|
| SH998D clutch bearing | P_7e7e2f4d73a753b8 | 1 | SNL17:016, callout33 |
| SH861B clutch sleeve | P_ce54085890d9de74 | 1 | SNL217:024, callout32 |
| SH869A cone-supporting collar | P_93eebe77f54604d6 | 1 | SNL67:018, callout9 |
| SH861D sliding-collar keys | P_3ea9dadf951b974d | 4 | SNL114:024, callout10 |
| SH861E snap ring | P_b69b4e7f361bb8c7 | 1 | SNL165:001, callout30 |

All additions belong to Drivetrain/TransmissionCore/ClutchStack. Four keys reuse
one definition. SH869A agrees between the handbook and catalogue, but the
bearing, sleeve and snap-ring marks differ. The
[source dossier](../experiments/drive_chains/clutch_stack_sources.json) retains
the original identities and configuration membership; absence of membership
does not establish universal applicability.

## Geometry and uncertainty

[Controls](../experiments/drive_chains/clutch_stack_controls.json) distinguish
printed quantities, provisional HB transfers and inferred geometry. X increases
forward in the existing transmission frame.

| Interface | Selected reconstruction | Evidence or limitation |
|---|---|---|
| Main bearing | X853.15–994.95, OD152 mm | Profile follows SNL; dimensions estimated |
| Bearing bores | Rear radius57.3, middle relief69, front50.8254 mm | Front bore transfers HB4.002in ID; other radii estimated |
| Middle relief | X893.15–969.95 with 5 mm internal blends | Source shows relieved profile; stations and blends inferred |
| Positive sleeve | 68.2498 mm long, minimum ID89.6874 mm, 24 internal grooves | Provisional HB2.687in,3.531in and24-spline transfers to a different mark |
| Sleeve bearing fit | Barrel radius57.15; 0.15 mm radial clearance | Estimated; rear flange nominally seats in SH999A |
| Revised SH999A | Body radius88, main bore76 mm | Receives the larger bearing, key beds and ring groove; six-hole rear lip preserved |
| Four keys | 107.95 × 19.05 radial × 9.525 tangential mm | Literal HB4.25in length,0.75in thickness,0.375in width; applicability/axis interpretation unresolved |
| Key engagement | Bed radius78.475, 0.1 mm side/roof gaps | 2.475 mm radial wall remains below each bed; four receiving grooves in support |
| Cone support | Body radius103, front flange111 mm; X865.95–980.95 | Cast contour and eventual cone/rivet joint remain inferred |
| Support clearance | 0.15 mm to collar; about2.97 mm to locking wire | Actual nominal surfaces checked |
| Snap ring | Separate split annulus with ridge at X997.95–1000.95, radius79 mm | Receiving groove captures the ridge; historical section, split and installation deflection unqualified |

HB4.684in bearing OD is **not** applied to the different SNL bearing profile.
The new key bands appear thicker than those in the source section. The literal
thickness interpretation is retained explicitly; the exact section axes and
identity transfer remain open. Source comparison supports the nesting and
component order, not exact contour or scale agreement.

The sleeve's rear flange has a nominal fitted surface in the collar. Its exact
drive attachment is unresolved; zero nominal clearance does not qualify torque
transmission. The eventual engine crankshaft and nut are absent. The sleeve's
internal spline form is a straight-groove approximation, with no claim of
positive engagement, load capacity or manufacturing fit.

The cone support includes a provisional flange. The cones and their six
SH869A-allocated rivets must be built together with the actual receiving joint.
No unsupported extra rivets or permanent phantom shaft are included.

## Reproduction and checks

Run each command successfully before the next:

```sh
python3 cad/003_FullTank/experiments/drive_chains/clutch_stack_sources.py
python3 cad/003_FullTank/experiments/drive_chains/clutch_stack_build.py
python3 cad/003_FullTank/experiments/drive_chains/check_clutch_stack.py
python3 cad/003_FullTank/experiments/drive_chains/check_clutch_stack_variants.py
python3 cad/003_FullTank/experiments/drive_chains/render_clutch_stack_review.py
python3 cad/003_FullTank/experiments/drive_chains/qualify_clutch_stack.py
```

The qualifier requires a visual-review receipt for the exact model images.
The native contains the combined assembly. The installation STEP contains
only nine affected placed solids; the definition STEP contains six definitions.

Checks cover ownership and source quantities, unchanged collar-lip geometry and
screw seats, bearing/sleeve nesting, all 24 spline grooves and lands, actual key
beds, support clearance, retaining ridge/groove and deliberately displaced
parts that must interfere. Two coherent radial-stack/rear-bearing-station
trials retain the printed HB key and sleeve dimensions. They sample uncertainty;
they do not qualify historical dimensions, loads or elastic installation.

All 68 independent checks, 27 local interference pairs, six definition STEP
comparisons and nine placed-solid comparisons pass. Both size trials pass
27 pairs and 22 contact/clearance checks each. Eight exact PNGs were inspected.
The [qualification receipt](../experiments/drive_chains/clutch_stack_build/qualification.json)
binds the native, input files, source assets and review/exchange receipts.
All 20 standard native files and 76 prior progression images were preserved.
New snapshots retain the [installed isometric](../../intermediate_snapshot_iso_clutch_stack_001.png),
[mechanism](../../intermediate_snapshot_iso_clutch_stack_mechanism_001.png),
[axial section](../../intermediate_snapshot_detail_clutch_stack_001.png) and
[exposed keys](../../intermediate_snapshot_detail_clutch_stack_keys_001.png).

Next are the SH998B thrust collar, SH998C ball retainer and 30 quarter-inch balls,
SH998A stop ring, cones/linings/rivets, six spring-plunger sets and SH849C ring,
then engine engagement and the clutch-stop band. Pump air circuit, separate
supports, lubrication, brakes/controls and standard integration remain ahead.
Standard tank011 retains its opaque and transparent hull views.
