# Coupled driver station — 27 September 2026

The [saved native](trial02/ControlRebuildTrial.FCStd) now carries the proposed
driver station through the complete existing front rods, intermediate controls,
clutch swing, rear rods and real floor attachments. It contains **394 local
occurrences / 125 definitions**. Nominal and +5 mm main-X builds pass saved-solid,
joint, full-context, STEP and reproduction checks. This is a mechanically checked
construction hypothesis; source-profile discrepancies and remaining controls
still need work before a complete driver installation can be accepted.

- [Driver/seat isometric, wireframe bow](trial02/visual01/isometric.png).
- [Connections with upholstery hidden](trial02/visual01/connections.png).
- [Complete control-route overview](trial02/routes_visual01/isometric.png).
- [Fixed whole-section comparison](trial02/visual01/source_section.png).
- [Fixed clutch plan/side comparison](trial02/visual01/clutch_source_comparison.png).
- [Installed changed geometry STEP](trial02/exchange01/RebuiltControlAdditionsInstalled.step).

## Complete stock and connected geometry

The conditional shaft pair from the preceding station review gives main
X7461.419 / Z990.022 mm. The existing 406.530 mm shaft separation remains fixed.
All 72 internal driver occurrences move together from the accepted development
station. The seat, stays and their upper/lower fastening stock retain their
source-derived positions.

The two printed **1257.3 mm M574 cores** determine a **165.521 mm aft shift** of
the intermediate mechanism. All 22 intermediate parts and 37 clutch-swing/center
rod parts move together. The complete **2362.2 mm / 93-inch SH229A rod** undergoes
only rigid translation. Its length, shape, joints and receiving stock are retained.
No printed rod or fastening stock is shortened.

Five existing front rods close on the true receiving bores with full joints.
The three currently populated M576 applications share the regenerated estimated
1298.281517 mm core; the two foot applications remain to be built. Seven complete
unprinted rear/center rod routes are regenerated to the fixed rear connections.
The actual six intermediate and four clutch-swing floor bores move with their
mounts; obsolete holes are restored from original stock. The driver support webs,
separate M788 angles, sixteen mounting stacks and eight bow-floor holes regenerate
on the actual sloped floor faces.

The 113 occurrences added relative to the local seat-support prototype are
**existing retained control/context parts**, not 113 new parts in the tank BOM.
The seat/support studies account for 92 physical additions relative to accepted
development. This local union has not been substituted for the full assembly.

## Clutch profile decision and source limits

`trial01` retained the earlier straight outward splay. The complete coupled audit
found three actual intersections with the port support plate, front stay bolt
and nut. The failed native and report remain saved.

`trial02` retains the complete M772 hub, bell crank, grip and the printed
723.9 mm hand reach / 127 mm bell arm. Only the middle blade's transverse set
changes: ruled sections delay its outward bend, with a maximum 60 mm inboard
shift. A nine-case probe found collisions through 50 mm setback; 55 mm clears
with only 2.327 mm nearest bolt clearance, while 60 mm gives 7.124 mm. The retained
60 mm choice leaves more clearance at the cost of 1.656 px additional plan
departure compared with 55 mm.

**This bend is an interface-derived approximation.** It departs from the nearly
straight schematic plan by up to 19.871 px; the side silhouette and grip remain
unchanged. HB6 does not positively identify this bend. Sharp ruled transitions
and projected-Y stock do not establish manufacturing radii or constant-normal
forging thickness. All source projections remain fixed; no camera is refitted.

The source section also shows a more nearly vertical support fore-edge than the
current shaft-derived diagonal footprint. Seat cushion/back curves and shaft-end
identities remain conditional. These differences are recorded in the
[visual review](trial02/visual01/visual_review.json); successful mechanical tests
do not resolve them. The support outline should be revisited with the remaining
adjustment fittings before full integration. Documented approximations may be
retained, but source agreement is not claimed where it is absent.

## Verification

| Check | Nominal | Main X +5 mm |
|---|---:|---:|
| Saved material, complete stock, actual joints and mounts | 1,075 pass | 1,075 pass |
| Supplementary contact/floor preservation checks | 31 pass | 31 pass |
| Nearby pairs in full retained context, no exemptions | 1,168 clear | 1,166 clear |
| Strict STEP comparisons: 39 definitions + 290 installed | 329 pass | 329 pass |

Both context audits include 8,987 physical occurrences. The revised targets
number 290; broad-phase bounds exclude distant pairs. A fresh nominal build
reproduces **391 archived BReps and 20,529 persistent properties**, with no
persistent-property differences in this run. Native/STEP acceptance retains the
existing material, tolerance, mass-error and convergence limits.

The first general contact-area checker can count coplanar face groups repeatedly.
`check_coupled_mount_material_v3.py` therefore supplements it with each opposed
face pair counted once. It verifies the original area criteria and independently
compares complete original bow floors minus the eight new bores in both material
directions. Its first two retained diagnostic versions incorrectly demanded all
contact disappear when a plate slides sideways: the horizontal foot legitimately
stays in contact. V3 tests the faces affected by that displacement. Neither model
geometry nor acceptance tolerances change. Both failed diagnostic reports remain.

These are static checks. Adjustment travel, operating motion, force and removal
paths remain unqualified. Physical thread helices, exact forgings, seat adjustment
and the remaining foot/reverse controls are unfinished.

## Recovery and continuation

Run `python3 cad/003_FullTank/experiments/drive_chains/verify_coupled_driver_station_study.py`
to verify the frozen checkpoint and dependency hashes. Regenerate with
`build_coupled_driver_station_v2.py --output NEW_PATH --main-x-offset 0` through
the existing headless launcher using absolute paths. Extract with
`pump_integration_worker.py`, run the coupled checker, supplementary V3 checker,
full-context checker and coupled exchange worker. Repeat at offset 5 mm and
compare a fresh nominal build with `check_control_rebuild_reproduction.py`.

Next reconcile SH291C and the newly discovered SH291D/SH291F references, revisit
the support outline, then add the foot and reverse controls. Preserve the complete
stock and this coupled closure when doing so. Accepted `operating_integrated01`,
standard tank011 and accepted progression 308 remain unchanged; the new
isometric is a separately named diagnostic snapshot.
