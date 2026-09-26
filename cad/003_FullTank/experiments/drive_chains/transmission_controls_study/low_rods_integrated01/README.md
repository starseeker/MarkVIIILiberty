# Installed rear low-speed brake straight connecting rods

[PowertrainWithRearLowRods.FCStd](PowertrainWithRearLowRods.FCStd) is the
current full development native: **3,282 physical occurrences, 570 shared
part definitions and 365 assembly groups**. Two SH946E straight connecting rods
(`Def_RearLowRod`) are installed, spanning front brake lever distal eyes and
rear fulcrum horizontal lever brake eyes. Horizontal fulcrum levers M4134
(Starboard) and M4133 (Port) brake arm profiles are reconciled symmetrically to
`[39.6875, ∓85.395714] mm` for straight-rod closure at `Y = ±535.395714 mm`,
`Z = 625.125 mm`. Both front-arm vectors, hub/journal, and mounting hardware
remain unchanged.

The [prototype dossier](../low_rods01/README.md) establishes straight-rod kinematic
closure: solid 19.05 mm (3/4″) cylindrical stock spans the 89.4866 mm socket face gap
with 20.6375 mm (13/16″) nominal thread engagement (≥ 19.05 mm required, < 25.4 mm throat),
giving 130.7616 mm overall length. Longitudinal arm offset xb = 39.6875 mm (1-9/16 in)
is the exact midpoint between prior provisional Starboard (47.625 mm) and Port (31.75 mm)
plan picks, adjusting each symmetrically by ±7.9375 mm (5/16 in).

Nominal and insertion variation prototypes each pass 81 native/interface checks,
127 surrounding context pairs (0 collisions, > 7.68 mm clearance to M4136 spring brackets)
and 30 strict STEP comparisons. The integrated native passes 47 checks covering all
inherited frames/owners, persistent properties, relocated local links, and strict
transfer of 8 definitions and 22 installed shapes. All 567 unchanged inherited definitions
are preserved: 549 have exact BRep bytes and 18 pass strict material comparison.

A fresh full rebuild reproduces all 1,742 stored BReps, 157,648 persistent properties,
3,282 occurrence records and 365 assembly records. The native is self-contained.

The inspected [isometric](low_rods_isometric.png), [detail](low_rod_detail.png),
[plan view](low_rods_plan.png), and [source comparison](source_detail.png) are retained
in the visual progression: **254 images**, including all 250 earlier images. The same
SNL6 camera is reused. Inherited lever silhouettes, spring height/inclination and
photographic discrepancies remain unresolved. Standard `tank011` remains unchanged;
these are selected subsystem views from the full development model.

The next physical task is continuing M567 washers, M564 return springs, M575 and long
M573/M578 rods, center/front controls, and remaining interiors. Poses remain deferred.

Recover without rerunning unchanged CAD checks:

```sh
python3 cad/003_FullTank/experiments/drive_chains/verify_rear_low_rod_checkpoint.py
python3 tools/cad_pipeline/decisions.py cad/003_FullTank/decision_ledger.json
```

For regeneration, use `build_rear_low_rods.py --output <new absolute directory>`
through the headless launcher after the prototype evidence is current. Extract,
run `check_rear_low_rod_installation.py`, then `check_rear_low_rod_preservation.py`.
Fresh integration is compared with `check_powertrain_frame_reproduction.py`. The fixed
checkpoint qualifier freezes completed evidence once; changed geometry requires a new checkpoint.
