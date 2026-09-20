# I03 — large planet pins and supports

This extends the paired large planetary trains with separate journals, pins,
pin rings and retaining hardware. It is an isolated transmission candidate;
the standard tank remains milestone 011 pending complete transmission and
mounting integration.

## Source identity and installation

| Mark | Component | Installed quantity | Survey identity |
|---|---|---:|---|
| M282 | Large bronze planet bush | 6 | P_9f6f2eb31c5c4b60 |
| M283 | Steel planet sleeve | 6 | P_0cf9a3623c685d0b |
| M284 | Large planet pin | 6 | P_2058f44955acfa97 |
| M313 | Pin nut | 6 | P_a97264077d0da970 |
| — | 3/16 × 2½-inch split pin | 6 | P_190577f876bb1fb5 |
| — | ½-inch expansion plug | 6 | P_5e252f5a8c42b3d3 |
| M285 | Large planet pin ring | 2 | P_ed6f18aee0b743df |
| M318 | Ring bolt | 6 | P_2425a8e3b4c20e53 |
| — | SAE ⅞-inch castle nut | 6 | P_59ef590bc721f4e8 |
| — | ⅛ × 1¾-inch split pin | 6 | P_016858b8ef5c1763 |

Each `PortPlanetSupports` / `StarboardPlanetSupports` belongs to the corresponding
transmission core. Ten shared definitions supply 56 physical occurrences.
Assembly catalogue records organize their children without duplicating pin or
bolt mass. The M313 catalogue quantity of eight includes two M782 shaft nuts
outside this installation.

SNL43 and HB122 callout23 identify the large bronze bush as M282; SNL44 and
HB122 callout32 identify the small bush as M272. SNL251/252 appear to transpose
these marks. The model uses the component catalogue and handbook identities
while retaining the conflicting assembly-list rows and their distinct survey
IDs in `transmission_pin_sources.json`.

Rotated original SNL137, checked against SNL126/156, correct two earlier research
transcription errors: **M313**, not M1313, and **½-inch** expansion plug, not
1½-inch. No earlier accepted geometry used the incorrect plug diameter. Source
rows and hashes also cover SNL24/165, the related assembly lists, Plate22 and
HB Plate73/legend. The survey itself remains unchanged.

## Geometry and physical receivers

The bronze bush occupies each existing 54 mm gear bore and has one inboard
flange. A separate steel sleeve has one outboard flange and a 28 mm pin bore.
The sleeve-to-bronze radial clearance is 0.1 mm; the gear-to-steel thrust gap
is 0.2 mm. The ring-to-bronze flange gap is 0.5 mm. These are nominal modeling
assumptions, not historical running or press fits. Single flanges permit
geometric insertion before closing the ring/carrier stack.

The 28 mm pin diameter follows an approximate 38-pixel Plate22 trace, which
scales to 27.577 mm. The 44 mm nut across flats and 14 mm axial height similarly
follow approximate picks. Each pin has an integral head, blind axial drilling,
cross-drilled cotter hole and separate domed expansion plug. The plug's 12.7 mm
diameter is printed; its dished section, insertion depth and inferred bore
remain approximate. No complete pin oil feed or sealing behavior is established.

The first trial placed nuts on projecting carrier pads. Source inspection showed
that these seats should be recessed. The revised nut plane follows approximate
Plate22 x849, or local Y529.227 mm under the inherited calibration. Added bearing
stock is clipped to the prior traced carrier exterior; 35 mm radius access
pockets expose the nuts. Local boss radius 42 mm, pocket contour and transitions
are inferred. The central carrier hub inside radius 100 mm is protected from
these edits.

M285 is reconstructed as an annular plate with three integral stand-offs,
fastened at alternate 120-degree stations by M318 bolts. The carrier has real
flat receiving faces, bores and post spotfaces. Exact casting contours, stand-off
form and bolt-circle dimensions remain assumptions. This topology is not a claim
to reproduce the original casting drawing.

The SAE ⅞-inch nut designation controls the 22.225 mm bolt shank. Nut and bolt
threads use smooth nominal envelopes. Printed split-pin sizes control the
straight envelope diameters and leg centerline stock lengths; paired round
legs and a segmented eye approximate their formed sections. The modeled 90-degree
leg bends fit the recessed installation. Exact stock volume, clamping, preload,
thread engagement and assembly-tool access are not qualified.

## Validation and review

Reproduce from the repository root:

```sh
python3 cad/003_FullTank/experiments/drive_chains/transmission_pin_probe.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/check_transmission_pins.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/render_transmission_pin_review.py --stage cad/003_FullTank
```

The probe reopens the saved native assembly, checks owning placements and source
quantities, preserves prior occurrence signatures outside the two carriers,
tests material against retained physical context, and checks specified seats
and clearances. It exports the 56 new and two changed occurrences together.

Native/STEP comparison checks material in both directions, requiring empty
Boolean differences and valid solids. Native maximum subshape tolerance must be
below 0.1% of the smallest specified positive assembly clearance, and STEP import
must not increase it. It records volume and center-of-mass differences separately.
Earlier mass-property checks flagged small discrepancies even though all 58
native/imported pairs had empty material differences. No geometric tolerance
is altered to obtain a pass. Independent 0.01 mm displacement trials must be
detected for every new definition and the revised carrier.

The independent checker also tests pin/gear axes and printed hardware sizes,
then moves retention parts into their physical stops and misclocks nuts against
their cotters. These are local failure-detection trials, not motion or strength
qualification. Final checkpoint results and inspected raster hashes accompany
the saved candidate.

The nominal candidate contains **1,013 valid single-solid occurrences**: 56 new,
two revised carriers and 955 unchanged prior occurrences. All 332 potentially
contacting material pairs are clear and all 108 specified contact/gap checks
pass. The carrier hub protected inside radius 100 mm has zero material change.
All 58 exported occurrences have empty native/STEP material differences.
Maximum native subshape tolerance is about 0.0000234 mm, below the 0.0001 mm
clearance-derived budget; maximum STEP tolerance is 0.0000001 mm. Twenty of the
58 pairs differ beyond the former volume/center thresholds despite preserving
material. These numerical property differences remain recorded in the report.

All 50 local support/thrust/retention trials pass their expected collision
outcomes; six pin-to-gear axis checks and four printed nominal diameter checks
pass. Each of the eleven definition-level 0.01 mm STEP displacement trials
produces added and missing material, confirming that the comparison rejects
real movement. The independently reopened canonical candidate is unchanged.

Seven rasters were actually inspected and bound to the native/report hashes in
`transmission_pin_build/visual_review.json`. Preserved
[supported-planet isometric](../../intermediate_snapshot_iso_transmission_supports_001.png)
and [pin-axis section](../../intermediate_snapshot_detail_transmission_pins_001.png)
record this partial interior checkpoint separately from standard tank milestones.

## Source comparison and remaining work

The actual horizontal assembly section is retained alongside a separate section
through one pin axis. The latter transforms only the inspection coordinates;
saved occurrence placements are unchanged. A three-planet train at 120 degrees
cannot reproduce both illustrated pins in a single section plane.

The recessed nut seat now follows the selected axial source pick. This does not
resolve the radial discrepancy: the printed tooth counts and pitch imply
142.875 mm planet-center radius, versus approximately 131.354 mm from the lower
pin illustration under the inherited scale. That 11.521 mm difference remains
visible. The inherited gear-face station residual, sun-outline discrepancy,
high-speed drum diameter conflict and central-input offset also remain open.

The upper M318 bolt in the pin-axis section lies substantially closer to the
shaft than the illustrated bolt: modeled radius 202 mm versus approximately
261.257 mm from a source pixel y200 pick. Its image station is 281.654 pixels,
about 81.654 pixels from that pick. The source outer carrier/ring region needs
reconciliation with the existing carrier rim and gear-case envelope before
enlarging the bolt circle. This discrepancy exceeds plausible line-picking
uncertainty; the current ring/bolt placement is an explicit provisional form.

Source casting transitions, ring bolt station/profile, bearing fit, pin oil
passages and complete case fastening require further work. Review the outer
carrier/ring contour and ring-bolt station next, then populate the small
planetary train and central bevel/input assemblies, and finish brakes,
controls, mounting and lubrication before integrating the transmission into
the standard tank. This checkpoint cannot establish a complete drivetrain or
complete tank.
