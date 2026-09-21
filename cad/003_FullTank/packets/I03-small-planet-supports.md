# I03 — small planetary supports and swept input disks

Status: visually reviewed nominal static reconstruction; checks passed. This packet continues
[the small gear train](I03-small-planetary-gears.md); it does not complete the
transmission or the full-tank coverage gate.

## Physical scope and source decisions

Both small trains receive their planet-pin supports and separate ring fastening.
The 56 new occurrences use nine new definitions and the existing half-inch
expansion-plug definition. Catalogue assembly entries do not create extra solids.

| Part | Installed here | Source |
|---|---:|---|
| M272 bronze planet bush | 6 | SNL44:005 |
| M271 steel sleeve | 6 | SNL44:006 |
| M274 hollow planet pin | 6 | SNL140:004 |
| M314 pin nut | 6 | SNL140:003 |
| 3/16 × 2 inch split pin | 6 | SNL140:005 |
| Half-inch expansion plug | 6 | SNL140:006; existing shared definition |
| M273 pin ring | 2 | SNL165:015 and SNL252:009 |
| M317 ring bolt | 6 | SNL25:034 |
| SAE 5/8 inch castle nut | 6 | SNL25:035 |
| 1/8 × 1¼ inch split pin | 6 | SNL25:036 |

Original SNL pages 25, 44, 140, 165 and Plate22 were inspected, with the HB122 legend.
M272 follows the small-bush entry on SNL44; contradictory bronze-bush marks in
the transmission assembly lists remain recorded. HB122 calls M273 “large,”
while SNL165/252 identify it as the small ring. The small train follows the latter.

Plate22's upper fastener is the M317 ring bolt; the lower is M274. They enter
from opposite sides. The ring bolts alternate with the three tooth-controlled
planet axes. Source picks set approximate head/nut stations; pin diameters,
shoulders, nut dimensions and local cast pads remain documented approximations.
The shorter printed ring-bolt cotter uses a 2.5 mm assumed bend radius, preserving
its nominal leg-centerline length. Its eye/leg section is simplified.

## Geometry and hierarchy

`PortSmallPlanetSupports` and `StarboardSmallPlanetSupports` sit beneath their
existing transmission-core groups. Shared native definitions have linked physical
occurrences and source identities. The case receives local pin thrust/nut faces,
ring-post seats and through bores; its inner hub and outer rim are protected.
Steel sleeves carry the bronze-bushed planets. Head, flange, nut and cotter
interfaces remain separate physical parts. Threads are nominal envelopes.

The M276 disk changes from a flat web to two translated cubic B-spline profile
curves revolved about the shaft. Poles, degree, knots, multiplicities and axial
stock are retained in the report and generator. The hub and inner web remain at
their previous stations. The outer transition runs between radii 174 and 204.5 mm;
those radii and the curve shape are inferred, not manufacturing dimensions.

The disk rim, M275 attachment lap and all 32 rivets move together to approximate
Plate22 rivet-center pixel 1065. The printed 47.625 mm rivet blank, inferred 8 mm
upset allocation, formed-head volume and 39.625 mm grip are retained. Gear tooth
geometry and mesh phases are retained. This corrects the earlier 15.022 mm axial
rivet-center discrepancy without changing the source calibration.

A direct material check overturned the previous concern that this shift must
collide with the case: the nominal rivet-to-case gap is about 0.570 mm. A bounding
profile estimate alone had been too conservative. The first combined trial
exposed about 0.023 mm³ of overlap beneath each
rivet head where the curve reached into its seating footprint. Ending the
transition at radius 204.5 mm leaves a flat land below the entire head. The
revised joint passes the combined material check; this is not a historical running
clearance or structural qualification.

## Validation and visual review

The reopened native candidate contains **1,115 valid single-solid occurrences**:
56 new, 38 revised and 1,021 unchanged. All 416 candidate material pairs are clear.
All 296 specified interfaces, six small-gear mesh checks, ten native tooth counts
and 94 native/STEP material comparisons pass. Case material outside the local
support region is unchanged, and the reused plug has zero material difference.
The relevant physical standard-tank context is included in the overlap checks;
the same seven superseded objects remain excluded as in preceding fixtures.

The support-only trial had no material overlaps and passed its specified
interfaces. One cotter produced a spurious large Boolean difference between
nearly coincident native/STEP faces despite a tiny mass-property difference.
The combined verifier retains raw differences and also compares material with
a fuzzy tolerance bounded by the saved solids' tolerances and 0.0001 mm, one
thousandth of the smallest nominal interface gap. It never enlarges the stored
shape tolerances. Deliberately shifted exports must still fail comparison.

The independent checker passes 48 local retention trials, 24 native radius
checks, six shared-definition checks, eight deliberately displaced STEP trials,
two native spline checks and two source-station checks. The maximum fuzzy
comparison tolerance used is 0.000027409 mm; a 0.001 mm export displacement
remains detectable. These are local checks, not full motion or load analysis.

Seven final rasters were inspected. The [source comparison](../experiments/drive_chains/transmission_small_support_build/source_review/small_train_comparison.png)
shows the source-scaled rivet center aligned and the retained planet-center
residual. The [combined cutaway](../../intermediate_snapshot_iso_transmission_small_supports_001.png)
and [pin section](../../intermediate_snapshot_detail_transmission_small_pins_001.png)
are preserved as new snapshots. Matching the rivet center does not establish
its exact head profile or grip: the illustrated overall outline remains shorter
than the printed-stock reconstruction. All 31 earlier snapshots remain intact.

The [native candidate](../experiments/drive_chains/transmission_small_support_build/TransmissionSmallSupportCandidate.FCStd),
[build report](../experiments/drive_chains/transmission_small_support_build/report.json),
[independent checks](../experiments/drive_chains/transmission_small_support_build/interface_checks.json)
and [visual receipt](../experiments/drive_chains/transmission_small_support_build/visual_review.json)
bind the reviewed artifacts. Standard tank 011 remains unchanged.

## Reproduce

```sh
python3 cad/003_FullTank/experiments/drive_chains/transmission_small_support_probe.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/check_transmission_small_support.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/render_transmission_small_support_review.py --stage cad/003_FullTank
```

Use `--output` on the builder and `--candidate` on the checker/renderer for an
isolated rebuild. These commands consume the saved, verified small-gear candidate
and retained source/parameter files. They leave standard tank 011 unchanged.

## Remaining work

The source planet-center residual 7.257 mm remains; printed tooth counts/pitch
control that geometry. Exact cast contours, rivet head/blank interpretation,
M276's contradictory printed tooth row and earlier large-gear/drum discrepancies
remain open. No full-motion, clamp-load or parameter-envelope qualification is
claimed. M265/M266 brake bearings, M290 sun retention, central bevel/input,
case fastening, brake controls, mounting/lubrication and standard-tank integration
remain necessary. Subsequent standard milestones must retain opaque and 18%
transparent hull views alongside the historical snapshots.
