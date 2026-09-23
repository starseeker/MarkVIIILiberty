# I01 / P01 — engine suspension and longitudinal supports

Status: **development geometry; historical mounting remains provisional**,
23 September 2026. This extends the [crossmember checkpoint](I01-engine-crossmembers.md)
with the remaining 61 physical children of the SNL242 engine-support assembly.
Complete standard geometry and identifiable interiors remain ahead of poses.

## Scope and ownership

The [native candidate](../experiments/drive_chains/engine_suspension_build/DrivetrainWithEngineSuspension.FCStd)
contains **1,909 physical occurrences**: 1,848 inherited plus 61 new. The rear
crossmember M180 and front cleat M189 receive mounting revisions; all 1,846 other
inherited shapes and placements, including the three floor contexts, are preserved.
There are 18 new reusable definitions. Candidate totals include replacement
contexts and must not be added to the standard tank inventory.

| Group under PowerplantDevelopment / EngineMounts | Physical components |
| --- | ---: |
| FrontCrossmember, inherited channel/cleat/rivets | 4 |
| RearCrossmember, inherited channel/gussets/rivets | 7 |
| LongitudinalSupports, M179/M178 rails | 2 |
| FrontSuspension, M184/M187 and mounting hardware | 15 |
| LeftRearSuspension, M182/M188/M190 and hardware | 22 |
| RightRearSuspension, M183/M188/M190 and hardware | 22 |
| FloorAttachments, inherited direct floor rivets | 14 |
| **Total support inventory plus direct floor rivets** | **86** |

The first six groups populate all **72 SNL242 catalogue children**. This inventory
coverage does not prove their shape or installed arrangement. Seven additional
shared floor/channel/hull-angle rivets and twelve longitudinal-support bolt sets
(36 pieces) remain pending their other receivers. The engine case, mounting
flanges and internal components remain to be reconstructed.

## Evidence and retained conflicts

The [dossier](../experiments/drive_chains/engine_suspension_sources.json) retains
159 literal records and hashes for 25 source assets. It inherits the crossmember
source record and adds the original handbook engine outlines and Liberty manual
base-chamber evidence.

HB66 Plate44 shows mounting rows 8-1/2in each side of the engine centerline,
14-7/8in minimum bearer clearance, and seven mounting positions per side at
6-1/2in pitch. These are **aviation dimensions**, provisionally transferred only
as engine-interface constraints. Inch conversions are selected over slightly
different printed metric conversions: 215.9mm half spacing, 377.825mm minimum gap,
and 165.1mm aviation pitch. They do not specify the tank rail section.

The Liberty manual's printed page 18 (PDF page 20), BASE CHAMBER, describes the
upper-case overhanging mounting flange and places the case joint at the main
bearing centers. Its figure 105 and the handbook front elevation corroborate
that datum qualitatively. The **lower circular bearing at the case joint is the
mainshaft axis**; the upper big-end/crankpin circle is offset by crank throw and
must not be mistaken for it. The provisional rail tops therefore use the existing
crankshaft-axis elevation, Z849.233510mm, without a crankpin-derived offset.

SNL30 allocates six 3/8 × 2in bolt/nut/lock-washer sets to each tank support,
whereas HB44 and the aviation manual show seven engine mounts per side. The
other tank receivers and any omitted position remain unproven. No speculative
engine bores or seventh tank bolt set have been added.

The individual SNL entries and HB205 identify M184 as single-point suspension and
M188 as double-point packing, conflicting with descriptions on SNL242. Both
alternatives remain recorded. M179 left / M178 right follows SNL242; the opposing
handbook handedness remains unresolved. Drawing numbers 70/71 are references,
not recovered fabrication plates.

## Static mechanical hypotheses

Each rear bracket has four 1/2 × 1-3/4in bolts through its upper pad and the lower
rail flange, and two 5/8 × 2-1/2in base bolts through bracket, packing and rear
channel. Four M190 bevel washers seat below an estimated 6-degree tapered upper
channel flange. Their association with that flange is a hypothesis. The lower
flange remains parallel; no exact rolled-section specification is claimed.

The front M184 yoke rests on M187 packing and connects through an estimated
upright extension of M189 with a longitudinal 3/4 × 2-1/2in bolt. Each rail receives
one 1/2 × 1-3/4in through bolt and one 1/2 × 1-1/2in cap screw into an estimated
blind casting boss. This allocation of the mixed bolt/cap inventory is unproven.
The longitudinal pivot interpretation is static; no motion or strength is qualified.

| Interface/control | Current estimate |
| --- | --- |
| Rails | X2940–4060, Y±215.9; C section open inward, 50.8mm wide ×76.2mm high, 6.35mm web and 9.525mm flanges. Inner gap 381mm. |
| Rear bracket | Base68 ×120 ×12.7mm, upper pad160mm long ×12.7mm stock, estimated web/gussets; two base bolt rows Y±42mm about each rail. |
| Packings | 6.35mm stock; all profiles and hole stations estimated. |
| Bevel washers | 36mm square, 6.35mm center stock, 6-degree slope; flat nut-side seat. |
| Front yoke | Estimated transverse arms, central block and two blind cap bosses; engine-sump clearance remains untested. |
| Hardware | Catalogue diameters and under-head lengths; nominal cylindrical thread envelopes, estimated hex heads/nuts, compressed split washers and fit allowances. |

The fixed SNL2 mapping has not been refitted. It places the rail/foot region broadly
within the drawing's support region, but cannot establish the casting profiles,
transverse stations or exact engine/flywheel axial relationship. The existing
crankshaft elevation is about 21mm below a conditional source-axis pick. The source
picks carry calibration, feature-identification and configuration uncertainty;
agreement with points used to select the stations is not independent validation.

## Verification and continuation

The saved native model passes **202 independent checks and 159 affected material
pairs including standard-tank context**, with no overlaps. All **83 STEP comparisons**
pass: 20 definitions and 63 installed shapes. These include analytical mass/centroid
checks for the bevel-washer definition and four occurrences. Checks inspect real
receiver material, bores, seating, open rail sections, ownership and source-sized
hardware while confirming preservation of all 1,846 unaffected parent occurrences.

A coupled trial increases rail height 76.2→82.55mm, reduces width 50.8→49mm, moves
front pads 70→65mm, shifts rear base bolts −5→−8mm, increases flange taper 6→6.5degrees,
and changes the four rear rail bolt stations. Printed engine spacing and nominal
hardware remain fixed. It passes **202 independent checks and 159 material pairs,
including standard context**. Variant STEP was not checked; a fresh nominal
reproduction and combined drivetrain qualification remain pending.

Seven native views and the unchanged source crop/fixed SNL2 overlay were visually
reviewed in the [review bundle](../experiments/drive_chains/engine_suspension_build/source_review/index.html).
The [checkpoint receipt](../experiments/drive_chains/engine_suspension_build/development_checkpoint.json)
ties the saved native, checks, parameter trial and visual review to exact hashes.
Three new snapshots preserve this stage: [isometric](../../intermediate_snapshot_iso_engine_suspension_001.png),
[exposed supports](../../intermediate_snapshot_detail_engine_suspension_001.png),
and [front mount](../../intermediate_snapshot_detail_engine_front_mount_001.png).
There are 117 progression images; all 114 earlier images and 20 standard native
files are unchanged. Standard tank011 and its transparent-hull companion remain
the existing integrated baseline.

The default STEP writer omitted surface trimming curves and produced a small
bevel-washer mass discrepancy despite zero Boolean material differences. The
separate exporter preserves those curves with `write.surfacecurve.mode=1`.
Failed exports and diagnostics are retained; strict tolerances are unchanged.
Round-trip checks also compare washer mass and centroid with closed-form wedge
minus circular-bore integrals. This numerical correction does not improve the
historical certainty of the washer profile.

```sh
python3 cad/003_FullTank/experiments/drive_chains/engine_suspension_build.py
python3 cad/003_FullTank/experiments/drive_chains/export_engine_suspension.py
python3 cad/003_FullTank/experiments/drive_chains/check_engine_suspension.py
python3 cad/003_FullTank/experiments/drive_chains/check_engine_suspension_exchange.py
python3 cad/003_FullTank/experiments/drive_chains/render_engine_suspension.py
```

The builder accepts `--output` and `--controls`; other tools accept `--candidate`.
The geometry checker supports `--local-only`; qualification includes standard
context. Controls require regeneration, not merely editing custom native metadata.

Next establish the engine casing, flange receivers and sump, reconcile the six
versus seven mounts, and check the provisional suspension against them. Then
complete shared hull-angle joints, engine/clutch registration and forward M581
controls. Fresh nominal reproduction and combined drivetrain qualification remain
required before standard integration. Full engine interiors and remaining tank
systems continue under the complete-tank workflow.
