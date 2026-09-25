# Shared M568A control-pin correction — 24 September 2026

[PowertrainWithControlPinFamily.FCStd](PowertrainWithControlPinFamily.FCStd)
contains **3,264 physical occurrences, 568 shared definitions and 359 groups**.
Four existing definitions change; no occurrences or assembly groups are added.
All installed frames and ownership remain unchanged. Standard tank011 and poses
are unchanged; the complete tank remains in progress.

The original catalogue assigns the **same M568A pin to M569A and M569B forks**.
The previous high-speed model used an estimated 15.875 mm shank against the
low-speed receivers' 13 mm bores. The selected common estimate is now a
**12.7 mm shank**, with **13 mm high-speed fork and paired M355 lever bores**.
This preserves the low-speed receiving eyes and the M330 definition shared with
the already connected track brakes. It is a consistent reconstruction estimate,
not a newly established historical diameter.

Only these canonical definitions change:

- `Def_ControlJoint_pin`: reduce the shank; preserve the complete head,
  41.275 mm under-head length and cross-hole station.
- `Def_ControlJoint_fork`: reduce the two pin bores; preserve the complete
  outside profile, slot, socket and threaded envelope.
- `Def_HighBrakeMechanism_lever_left` and `_right`: reduce the distal bores;
  preserve all material outside the old bore, all other interfaces and the
  B-spline lever profiles.

The unchanged cotter still clears the shank and blocks withdrawal. Actual saved
low-speed receiver geometry accepts this same complete pin definition; the old
pin and an eccentric new pin fail the negative controls. This does not qualify
the future low-speed fork stack or complete control travel.

## Evidence and retained uncertainty

[Source review](../pin_family_source_review01.json) records inspection of the
original SNL pages 71, 87 and 136, HB figure 104 and the local figure index.
SNL136's physical pin row gives **1⅝ inches**, while SNL71's assembly row gives
**1⅞ inches**. Both are retained; the specific physical row is selected, with
the under-head datum still inferred. Other M568A applications are unmodeled.

SNL87 gives **M569A fork length 1 inch without a datum**. The retained
[low-fork diagnostic](../pin_family01/diagnostics/low_fork_one_inch/report.json)
tests pin-centre to socket face with the current receiver-clearing profile.
It provides only **3.175 mm of full socket**, or **4.175 mm including partial
cylindrical patches in the ears**, below the chosen 19.05 mm engagement criterion.
That criterion is a modeling choice, not a sourced historical design standard.
This combination is rejected; no accepted M569A fork or SH946E rod is installed.
Resolve the source datum, estimated fork profile, pin grip and receiving geometry
together rather than silently changing the printed length.

## Verification

- Nominal and radial-clearance variant (0.15 / 0.20 mm) each pass **73 saved-native
  checks, 143 whole-material context comparisons and 25 strict STEP comparisons**.
- Independent checks confine all changes to the declared annular material.
  Pin-head and cotter retention controls pass. STEP covers nine definitions and
  all sixteen prototype occurrences in their installed coordinates.
- **37 integration checks** bind the full native to the tested prototype,
  inspect all links and inherited persistent properties, and re-open a relocated
  self-contained copy.
- All **564 unrelated definitions** are preserved: **545 exact BReps / 19 strict
  material comparisons**. Sixteen prior comparisons were reused only for exact
  ordered BRep hashes and the unchanged worker.
- Fresh full generation reproduces **1,736 archive BReps and 156,592 persistent
  properties**, all 3,264 occurrence records and 359 assembly groups. The fresh
  prototype also reproduces all 27 BReps and 1,192 properties.
- 530 identical extracted BRep files use relative links to preserved parent
  artifacts; the FCStd itself contains its complete definitions.

[Operating interfaces](operating_interfaces.json) rebinds two revised high-speed
bore diameters and four unchanged low-speed eyes to this native. The previous
[eight track-rod receiver coordinates](../track_rods_integrated01/operating_interfaces.json)
remain valid and unchanged. Use both receipts according to their scope.

The [isometric](pin_family_isometric.png) and
[display half-section](pin_family_section.png) are saved as progression views
246–247. Section clipping does not alter the physical CAD. Boundary lines around
the revised bore are BRep construction seams, not added bushings. All six full
assembly renders match the reviewed prototype images byte for byte.

The existing SNL6 local camera is reused unchanged. Its earlier lever/profile,
station and spring-height discrepancies remain visible. Bore diameters are not
image-fitting landmarks; HB104 remains an uncalibrated perspective photograph.

## Recovery and regeneration

From the repository root:

```bash
python3 cad/003_FullTank/experiments/drive_chains/verify_control_pin_family_checkpoint.py
python3 tools/cad_pipeline/decisions.py cad/003_FullTank/decision_ledger.json
```

The generating controls are [nominal](../pin_family_controls01.json) and
[clearance variation](../pin_family_variation_controls01.json).
Run `trial_control_pin_family.py` through the project's headless launcher with
absolute `--controls` and a fresh absolute `--output`; extract with
`pump_integration_worker.py extract`, then run the native, context and exchange
checkers. `build_control_pin_family.py` transfers the reviewed nominal prototype
to a fresh full document; all dimensions require scripted regeneration.
Frozen inputs, validation modules and receipts are retained with the artifacts.

Next: resolve M569A geometry and complete the two low-speed short connections,
then M567 washers, M564 return springs, M575 and longer rods, center/front
controls and the remaining interiors. Historical dimensions, complete motion,
strength and full service paths are not qualified by this checkpoint.
