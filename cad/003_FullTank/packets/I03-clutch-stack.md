# I03 — nested clutch bearing, sleeve, keyed support and retention

Status: **qualified partial reconstruction with documented approximations**, 22 September 2026.
[Native assembly](../experiments/drive_chains/clutch_stack_build/TransmissionWithClutchStack.FCStd) ·
[source comparison](../experiments/drive_chains/clutch_stack_build/source_review/index.html).
This stage populates the previously vacant main collar with the bearing, sleeve
and thrust collar, and adds the four keys, outer cone support and external snap ring.
The combined transmission/pump candidate contains **1,549 physical components**.
Nine are new; SH999A changes to receive them. The other 1,539 parent components
retain their geometry and placement. The complete clutch and tank remain unfinished.

## Source correction

The first 1,548-component candidate assigned the large bearing-end collar to
SH861E. Its geometric checks passed, but tracing the leaders on the **full SNL
Plate21** disproved that identity. Callout28 identifies SH998B thrust collar;
callout30 identifies a separate external SH861E snap ring farther aft.
The [rejected first candidate](../experiments/drive_chains/clutch_stack_build/rejected_trials/initial_ring_mapping/REVIEW.md)
and its native, inputs, receipts and images remain preserved. Its earlier
qualification is superseded by this source evidence and it is not a modeling parent.

The corrected candidate returns to the qualified 1,540-component collar-joint
parent. It replaces the erroneous end ring with SH998B, adds the external ring
in its own outside groove, and removes the unsupported internal retention groove.
The comparison includes the entire catalogue plate and the rejected section.

## Arrangement and source decisions

The SNL section shows a long bearing with an enlarged middle bore, a larger rear
bore surrounding the sleeve, and a smaller forward journal bore. The sleeve
overlaps the rear bearing band and extends into the middle relief. Placing the
sleeve and bearing end-to-end would contradict this arrangement.

The comparison preserves the original opposite HB/SNL orientations and shows
the corrected and rejected first-core sections. Panel scales are
independent. The original pages 17, 67, 114, 165 and 217 confirm the selected
marks and quantities. Pages 164 and 165 also retain the next ball/stop-ring inventory; those items
are not counted as installed in this checkpoint.

| Item | Survey identity | Quantity | Source |
|---|---|---:|---|
| SH998D clutch bearing | P_7e7e2f4d73a753b8 | 1 | SNL17:016, callout33 |
| SH861B clutch sleeve | P_ce54085890d9de74 | 1 | SNL217:024, callout32 |
| SH869A cone-supporting collar | P_93eebe77f54604d6 | 1 | SNL67:018, callout9 |
| SH861D sliding-collar keys | P_3ea9dadf951b974d | 4 | SNL114:024, callout10 |
| SH998B thrust collar | P_e9e98ebf6818bacd | 1 | SNL67:020, callout28 |
| SH861E external snap ring | P_b69b4e7f361bb8c7 | 1 | SNL165:001, callout30 |

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
| Revised SH999A | Body radius88, main bore76 mm | Receives the larger bearing, key beds and external ring groove; six-hole rear lip preserved |
| Four keys | 107.95 × 19.05 radial × 9.525 tangential mm | Literal HB4.25in length,0.75in thickness,0.375in width; applicability/axis interpretation unresolved |
| Key engagement | Bed radius78.475, 0.1 mm side/roof gaps | 2.475 mm radial wall remains below each bed; four receiving grooves in support |
| Cone support | Body radius103, front flange111 mm; X865.95–980.95 | Cast contour and eventual cone/rivet joint remain inferred |
| Support clearance | 0.15 mm to collar; about2.97 mm to locking wire | Actual nominal surfaces checked |
| Thrust collar | Bearing-end plug radius76, front disk radius96, outer guiding lip | Forward face X1010.95; inferred attachment and unfinished ball reaction |
| External snap ring | X987.95–990.95, inner radius86, outer92 mm | Actual outside groove; profile, split and elastic installation inferred |

HB4.684in bearing OD is **not** applied to the different SNL bearing profile.
The new key bands appear thicker than those in the source section. The literal
thickness interpretation is retained explicitly; the exact section axes and
identity transfer remain open. Source comparison supports the nesting and
component order, not exact contour or scale agreement.

The sleeve's rear flange has a nominal fitted surface in the collar. Its exact
drive attachment is unresolved; zero nominal clearance does not qualify torque
transmission. The eventual engine crankshaft and nut are absent. The sleeve's
internal spline form is a straight-groove approximation, with no claim of
positive engagement, load capacity or manufacturing fit. The thrust collar
uses a nominal fitted plug and outer guiding lip; exact attachment to SH999A
and the ball reaction mechanism remain unfinished. The external ring provides
a forward stop for the cone-support collar, with 7 mm nominal axial clearance.

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
only ten affected placed solids; the definition STEP contains seven definitions.

Checks cover ownership and source quantities, unchanged collar-lip geometry and
screw seats, bearing/sleeve nesting, all 24 spline grooves and lands, actual key
beds, support clearance, external ring/groove and separate thrust collar and deliberately displaced
parts that must interfere. Two coherent radial-stack/rear-bearing-station
trials retain the printed HB key and sleeve dimensions. They sample uncertainty;
they do not qualify historical dimensions, loads or elastic installation.

The corrected native now passes 75 independent checks, seven definition STEP
comparisons, ten placed-solid exchange checks and 29 material pairs against the
combined assembly and standard physical context. Both coupled size trials pass
29 pairs and 24 contacts. Eight regenerated images were inspected against the
full source figures. The qualifier binds those receipts to the exact native and
current builder inputs.

The first smaller-radius trial exposed a surviving rim from the previous collar:
fusing a smaller body onto that parent could not remove the old larger rim. The
builder now preserves only the qualified six-hole rear lip and reconstructs the
remaining body from its current controls. The failed variant and old records
remain under `rejected_trials/radial_variant_overlap`. A complete regeneration
and the above checks qualified the fix; no clearance threshold was relaxed.

Next are the SH998C ball retainer and 30 quarter-inch balls and their reaction
surfaces on the thrust collar,
SH998A stop ring, cones/linings/rivets, six spring-plunger sets and SH849C ring,
then engine engagement and the clutch-stop band. Pump air circuit, separate
supports, lubrication, brakes/controls and standard integration remain ahead.
Standard tank011 retains its opaque and transparent hull views.
