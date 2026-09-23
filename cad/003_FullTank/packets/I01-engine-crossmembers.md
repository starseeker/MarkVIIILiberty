# I01 / P01 — engine transverse supports and floor joints

Status: **development geometry, historical qualification pending**, 23 September 2026.
This extends the [clutch-stop checkpoint](I03-clutch-brake-linkage.md) toward the
engine installation. Complete standard geometry and identifiable interiors remain
the priority, before pose variants.

## Constructed scope and ownership

The [native candidate](../experiments/drive_chains/engine_crossmember_build/DrivetrainWithEngineCrossmembers.FCStd)
contains **1,848 physical occurrences**: the previous 1,821, plus 25 new engine-frame
components and two replacement floor contexts. Floor 7 changes; 1,820 inherited
occurrences retain their geometry and placement. Floors 5, 6 and 7 replace the
corresponding standard plates when integrated; they are not additional tank plates.
Local candidate totals are not additive to the standard tank inventory.

| Native group under PowerplantDevelopment / EngineMounts | Components |
| --- | ---: |
| FrontCrossmember: M181 channel, M189 cleat, two 5/8 × 2-1/8in button rivets | 4 |
| RearCrossmember: M180 channel, M186/M185 gussets, four 11/16 × 2-1/8in button rivets | 7 |
| FloorAttachments: five rivets per channel and two per rear gusset | 14 |

The 14 floor rivets are **11/16 × 1-7/8in**, following the heading on SNL174 into
the allocations on SNL175. They are additional to the nested channel assemblies.
All rivets are physical occurrences linked to reusable definitions. The four
different rivet definitions retain their individual grip lengths and formed tails.

The complete SNL242 support assembly expands to 72 physical components, including
the 11 channel children above. **61 support components remain**: three suspension
brackets, three packings, four bevel washers, two longitudinal rails, 45 bolt/nut/
lock-washer pieces, two cap screws and two lock washers. Seven additional shared
floor/channel/longitudinal-angle rivets and twelve bolt sets allocated to the
longitudinal supports (36 pieces) also remain. An engine-flange connection is a
working hypothesis; the catalogue does not identify the other receiver. Their
receiving structures must be established before placement. This checkpoint does
not claim a complete mounted engine frame.

## Evidence and approximation decisions

The [source dossier](../experiments/drive_chains/engine_frame_sources.json) retains
159 literal records and hashes for 18 source assets. Original SNL37, 63, 131, 174,
175, 184 and 242 were visually reviewed. SNL63 identifies the two nested channel
assemblies. SNL175 establishes M181-to-floor-M1936 and M180/M185/M186-to-floor-M1937
connections. SNL184 lists four rear and only three front shared longitudinal-angle
joints; the apparent asymmetry remains recorded rather than filled by assumption.

Individual entries identify M184 as the single-point suspension bracket and M188
as double-point packing. SNL242 uses conflicting descriptions. The working
interpretation follows the individual entries and handbook nomenclature while
retaining both literal alternatives. M179 left / M178 right follows SNL242;
the handbook's opposing handedness remains unresolved.

The source names channels, a cleat and gussets without their fabrication dimensions.
This candidate uses parallel-flange C sections open aft, a central front angle
cleat, and two rear gussets with upright and floor flanges. These profiles, transverse
positions and handed shapes are **engineering approximations**. Rolled-section
taper and the four M190 bevel-washer interfaces remain to be resolved with the
remaining suspension hardware. The cleat's future bracket interface is not drilled
until that connection is established.

| Control | Current estimate and limitation |
| --- | --- |
| Crossmember stations | X3850 front / X3000 rear, in tank coordinates. Conditional SNL2 foot-region picks imply X3851.7 / X3015.6; they do not prove the channel center datums. |
| Crossmember span, section | 2200mm span, 88.9mm depth, 76.2mm height, 9.525mm web, 12.7mm flanges. No recovered section designation. |
| Floor geometry | Existing Z527.05–533.05mm and full combined outline retained. Estimated seams move to X3970 and X3190 to accommodate source-named joints. |
| Gusset placement | Y±980mm; attachment spacing and plate stock estimated. No transverse source scale is inferred from the longitudinal drawing. |
| Rivet blanks | Nominal diameters and lengths from SNL63/174–175. Length treated as under-head stock; factory and upset-head forms estimated. Tail forming conserves the selected blank-shank volume. |
| Bore allowance | 0.1mm radial construction allowance. This is a fit assumption, independent of numerical check tolerances and historical uncertainty. |

The approximate source picks have about 18mm pick uncertainty plus unquantified
calibration, feature-identification and configuration error. The established floor
elevation is retained; it is not moved to match an ambiguous lower line in the
scan. Aircraft wooden bearers and obscured museum mounting details are not used
to dimension these parts. Neither structural capacity nor movement is qualified.

## Verification and visual review

The saved native file reopens with valid single-solid components and hidden
definition storage. **151 independent geometry checks and 93 affected material
pairs including standard-tank context pass.** Checks inspect source-sized rivet
shafts, retained blank volumes, real receiver holes and seating, nested inventory,
open channel sections, preserved parent shapes and the complete floor material
difference. The only combined floor material removed is the 14 new rivet bores;
existing clutch holes remain intact.

**40 STEP comparisons pass**: 12 definitions and 28 installed shapes, including
the three replacement floors. Comparison checks material in both directions,
solid counts, volume and centroids after reopening the STEP exports.

The [review bundle](../experiments/drive_chains/engine_crossmember_build/source_review/index.html)
contains native isometric, underside and joint views, an unchanged source crop,
and native edges projected through the fixed SNL2 calibration. No fitting is
applied to improve agreement. Source placement and profile qualification remain
separate from passing CAD checks.

A coupled parameter trial shifts both crossmembers forward 10mm, increases the
half span and gusset stations by 20mm, and changes channel depth from 88.9 to 95mm.
It passes **151 checks and 93 material pairs including standard context**. Variant
STEP exchange was not checked. Six native views and the fixed source overlay were
visually inspected; the existing flywheel's axial relationship to the drawn rear
crankcase remains unresolved. Agreement with the selected foot regions is not an
independent validation of the stations inferred from those regions.

The [development checkpoint](../experiments/drive_chains/engine_crossmember_build/development_checkpoint.json)
records exact native, validation and review hashes. Three new progression images
bring the total to 114; all 111 earlier images and all 20 standard native documents
remain unchanged. The new
[isometric](../../intermediate_snapshot_iso_engine_crossmembers_001.png),
[crossmember view](../../intermediate_snapshot_detail_engine_crossmembers_001.png)
and [gusset detail](../../intermediate_snapshot_detail_engine_gusset_001.png)
preserve this stage. A fresh nominal reproduction and combined drivetrain
qualification remain required before standard integration. The accepted qualified
drum/flywheel baseline and standard tank011, including its transparent-hull view,
remain unchanged.

## Continue and reproduce

Next establish M182/M183 rear and M184 front suspension interfaces, M187/M188
packings, M190 bevel washers and M178/M179 longitudinal rails. Add their catalogue
hardware and the engine mounting flanges. Revisit channel section taper, floor
seams and attachment locations against those interfaces. Then resolve the shared
hull-angle joints, provisional clutch feet, crankshaft/complete-clutch registration
and forward M581 control connection before combined qualification and integration.

```sh
python3 cad/003_FullTank/experiments/drive_chains/engine_crossmember_build.py
python3 cad/003_FullTank/experiments/drive_chains/check_engine_crossmembers.py
python3 cad/003_FullTank/experiments/drive_chains/check_engine_crossmember_exchange.py
python3 cad/003_FullTank/experiments/drive_chains/render_engine_crossmembers.py
```

The builder accepts `--output` and `--controls`; checkers and renderer accept
`--candidate`. The geometry checker supports `--local-only`. Controls require
regeneration; custom native metadata does not implement live feature dependencies.
Preserve earlier native checkpoints and progression images when refining this
development hypothesis.
