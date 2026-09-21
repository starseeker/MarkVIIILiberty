# I03 — small-sun retention

This increment installs the two M290 rings assigned to the M267 small sun
pinions by original SNL165. Together with the four existing M289 shaft rings,
the candidate now contains all six catalogue occurrences, linked to one shared
definition. It continues the [small-support reconstruction](I03-small-planet-supports.md).
The complete transmission and full-tank coverage gates remain open.

## Geometry and source interpretation

SNL Plate22 and HB Plate73 identify the small-sun ring as callout40. The retained
calibration places its approximate center at source x1285, or port Y212.816 mm.
Neither that pick nor the previous ring profile is a manufacturing dimension.
The common ring has a 46.2 mm bore radius, 57 mm outside radius and 5.806 mm
width. Its split is rotated out of the shaft-height section, consistent with
the source showing material on both sides; its exact angular position is unknown.

The old M267 spline root lay inside the ring bore. Each sleeve therefore receives
a complete circular collar with a 46 mm groove root and 0.15 mm axial clearance
at each ring face. The collar outside radius is 50.8 mm. A smooth 57.8 mm radius
shoulder replaces the unnecessary spline exterior between the drum hub end and
the sun gear. The remaining spline engagement is approximately 70 mm long.
These are documented mating-shape assumptions.

Each M269 drum receives a 57.2 mm radius ring counterbore and a smaller collar
relief. Its ring seat has 0.3 mm nominal axial clearance; the opposite hub end
has 0.2 mm clearance to the sun shoulder. Its existing outside profile, printed
381 mm diameter and hub end are retained. The sun tooth band, internal bush,
cross shaft, planetary meshes and previously qualified support hardware remain
unchanged. The original model's rectangular spline form remains approximate.

The [source comparison](../experiments/drive_chains/transmission_sun_retention_build/source_review/sun_retention_comparison.png)
uses the actual saved native section and unchanged source scale. It shows the
ring at the selected axial station while exposing the continuing differences in
the hub and sleeve outlines. The original top and bottom representations differ;
their boundaries do not establish every cap/bush interface unambiguously.
M265/M266 ownership, cap fastening and the adjoining M277 neck still need a
separate reconstruction. A thin annulus placed in the remaining void would not
resolve those questions.

## Verification and artifacts

The reopened [native candidate](../experiments/drive_chains/transmission_sun_retention_build/TransmissionSunRetentionCandidate.FCStd)
contains **1,117 valid single-solid occurrences**: two new rings, four revised
sun/drum occurrences and 1,111 earlier occurrences unchanged. All 30 affected
material pairs have zero overlap. All 300 specified interfaces and 12 local
axial/twist capture trials pass. Removing the sun groove deliberately produces
ring interference. Direct material comparisons protect the sun teeth, drum
exterior and reused ring definition.

All six new/revised solids survive native-to-STEP material comparison, both raw
and with a tolerance bounded by the saved shapes' tolerances and 0.0001 mm.
The independent checker confirms eight capture directions, 20 native radii,
two source stations, two shared-definition identities and three deliberate
0.001 mm STEP displacement failures. These checks establish nominal static
interfaces; they do not qualify elastic ring installation, service loads,
historical fits or a complete operating transmission.

The [build report](../experiments/drive_chains/transmission_sun_retention_build/report.json),
[independent checks](../experiments/drive_chains/transmission_sun_retention_build/interface_checks.json)
and [visual receipt](../experiments/drive_chains/transmission_sun_retention_build/visual_review.json)
bind the deliverables. Four final images are reviewed, including the close
section and combined planetary cutaway. Standard tank 011 and its opaque and
transparent snapshots remain unchanged; this fixture awaits integration.

## Reproduce

```sh
python3 cad/003_FullTank/experiments/drive_chains/transmission_sun_retention_probe.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/render_transmission_sun_retention_review.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/check_transmission_sun_retention.py --stage cad/003_FullTank
```

Use `--output` on the builder and `--candidate` on the renderer/checker for
isolated rebuilds. Visual assessment remains a separate review of the generated
images. Original inputs and all preceding candidates remain preserved.

## Next

Resolve and populate M265/M266/M300 at the brake bearing. Then complete central
bevel/input, case fastening, brakes and controls, lubrication and mounting before
standard assembly integration. The full workflow's remaining tank systems,
coverage reconciliation and release checks are still required. Preserve opaque
and 18% transparent views at subsequent standard geometry milestones.
