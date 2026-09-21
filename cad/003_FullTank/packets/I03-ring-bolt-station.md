# I03 — corrected pin-ring bolt station and receivers

This revision corrects the source attribution and installation of the M318
large planet pin-ring bolts. It retains the 1,013-component transmission
fixture and changes 22 occurrences: both M286 carriers, both M285 rings, and
six each M318 bolts, castle nuts and split pins. The other 991 occurrences,
including all planet gears, pins and bearing sleeves, retain their geometry
and placement. Source identities and installed quantities are unchanged.

## Corrected source reading

The previous pin-support comparison misidentified the outer bolt near Plate22
pixel y200 as M318. That bolt traverses the case joint. The original SNL24
assembly entry explicitly identifies the M318 assembly as callout15 on Plate22;
HB122 independently maps callout15 to M318. Tracing that leader in both SNL
Plate22 and HB Plate73 identifies the **inner** bolt, near pixel y355.

The prior claimed 59.257 mm outward discrepancy and the proposed enlargement
of the carrier rim are withdrawn. The earlier rendered images and hashed
receipts remain preserved as superseded review history. This correction is
recorded in `transmission_ring_support_sources.json`; the underlying frozen
survey has not been changed.

This also corrects the earlier description of two illustrated planet pins:
the upper inner feature is the M318 ring bolt and the lower is the M284 planet
pin. The earlier composite-section hypothesis is unnecessary for this pair.
A section through one pin and the opposite ring bolt gives a meaningful
comparison while retaining the modeled three-planet arrangement.

The corrected source picks are:

| Feature | Approximate Plate22 pixel coordinate | Conditional model coordinate |
|---|---:|---:|
| Bolt axis | y355 | radius 148.771 mm |
| Head seat | x906 | local Y487.861 mm |
| Nut seat | x842 | local Y534.307 mm |

These use the inherited 0.725714 mm/pixel scale and output datum. Four pixels
are allowed for manual picking; that allowance does not cover illustration or
calibration distortion. Agreement with the chosen picks is construction
evidence, not independent dimensional validation. The former inferred bolt
radius was 202 mm.

## Revised geometry

The three fastening stations on each side remain alternated with the planet
pins at 120-degree intervals. Their radius now follows the identified source
bolt. The bolt shank between the head seat and tip is 65.446 mm long. The printed
SAE ⅞-inch nut designation still controls the 22.225 mm shank diameter; it is
not reduced to force agreement with the illustrated thickness.

Each M285 projecting boss has an inferred axial counterbore, allowing the shorter
bolt head to reach its source-positioned seat. Boss radius 23 mm and access
radius 21 mm leave 2 mm nominal wall. The M286 nut sits in a radius 26 mm recess;
the surrounding radius 33 mm local boss is clipped to the inherited outer dish
silhouette. Those dimensions, cavity contours and cast transitions are explicit
reconstruction choices. Exact casting form, strength and wrench clearance have
not been established.

The carriers are rebuilt from the saved pre-support carrier, so the obsolete
radius 202 mm bosses and bores do not survive. Existing planet-pin receivers are
regenerated with unchanged controls. The central hub inside radius 100 mm is
protected. Case envelopes and the source-traced carrier outer rim are retained;
the unrelated outer case-joint bolts remain to be populated.

## Checks and review

Reproduce the isolated revision with:

```sh
python3 cad/003_FullTank/experiments/drive_chains/transmission_ring_support_probe.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/check_transmission_ring_supports.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/render_transmission_ring_support_review.py --stage cad/003_FullTank
```

The reopened native candidate has 1,013 valid single-solid occurrences. All 166
material candidate pairs involving the changed parts are clear; all 108 previous
specified contacts and gaps still pass. The protected carrier hub has zero
material change. The 22 changed solids pass native/STEP comparison with empty
Boolean material differences, bounded native tolerance and no tolerance
inflation on import. Small numerical mass-property differences are recorded.

The independent checker tests physical head/nut stops, radial interference and
cotter locking, then checks the bolt's axial extraction path at four stations
with nut and cotter removed. It also checks retained bush thrust stops, actual
bolt radii and printed shank diameters, and whether deliberately shifted STEP
solids are rejected. These are local geometric checks, not finished service
poses, complete motion, tooling or load qualification.

All 50 local trials pass: 24 clear extraction stations and 26 intended stop,
cotter or thrust collisions. Six native radius/diameter checks and five
deliberate STEP-displacement failures also pass. Seven rendered images were
actually inspected and their hashes are retained in `visual_review.json`.
The preserved [carrier-side isometric](../../intermediate_snapshot_iso_transmission_supports_002.png)
and [bolt-axis section](../../intermediate_snapshot_detail_transmission_ring_bolts_001.png)
record this revision separately from standard tank milestones.

The actual local section passes through a planet pin below the shaft and an
M318 bolt above it. Separate pin and bolt cutaways expose the retained bearing
stack and revised access counterbore. The source comparison explicitly
distinguishes the inner ring bolt from the outer case-joint bolt. No saved
assembly placement is altered to create the inspection views.

The planet-center discrepancy of 11.521 mm under the inherited illustration
scale remains, as do the earlier gear-outline and face-station differences.
Exact ring/casting details, complete oil paths, threads and case fastening remain
unfinished. Continue with the small planetary train and central bevel/input
assemblies, then brakes, controls, mounting and lubrication. Full transmission
integration and standard tank milestone 012 remain open.
