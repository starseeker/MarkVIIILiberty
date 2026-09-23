# Valid solid with overlapping wire strands

FreeCAD 1.1.1 / OCC 7.8.0, 23 September 2026. Both candidates follow an
estimated cage-to-bolt route with source stock length 203.2 mm and diameter
1.2065 mm. Both produce a valid single solid and pass the seven local neighbor
comparisons. Those checks alone do not establish the intended wire material.

The three-turn candidate folds the doubled tail into itself. Its nonlocal
centerline distance is 0.812878 mm and minimum bend radius 0.812551 mm. Fusion
hides the overlap, losing 6.337590 mm³ from the intended 232.310178 mm³ stock.

Using two turns gives 1.405765 mm nonlocal centerline spacing, 1.478190 mm
minimum bend radius, and 1.0e-9 mm³ stock-volume error. All eight inches remain
in the part; the solution does not trim away wire or weaken a tolerance.
Twist count, routing and holes are estimates; HB87 identifies the attachment.

The folders retain both actual BReps, centerlines, controls, neighbor results and
path checks. `replay.py` independently checks the saved geometries, expecting the
three-turn control to fail and the two-turn candidate to pass. Run from the
repository root:

```bash
python3 skills/freecad-reconstruction/scripts/freecad_headless.py --workdir .work/wire-self-contact cad/003_FullTank/experiments/drive_chains/engine_oil_pump_relief_lock_study/diagnostics/wire_self_contact/replay.py
```
