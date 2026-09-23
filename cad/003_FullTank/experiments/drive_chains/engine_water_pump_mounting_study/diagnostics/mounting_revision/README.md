# Mounting and drain diagnostics

These retain rejected geometry and the construction trace behind the current
revision. Diagonal ears interfered with outlets; cardinal ears with the drain
and lower-drive retaining screw. Coupled ears/outlets removed those contacts,
but the shallow drain seat intersected its fittings and raised body tolerances.
The deep-drain trace reaches8.745933e-7mm. Final native/STEP acceptance is in the
parent directory; an isolated trace does not qualify the installed pump.

The shallow native run also hit a checker error on an empty removed-material
shape; its material records are partial, not a completed acceptance report.
The later nominal and trial processes were terminated externally (exit143),
leaving native files intact. Their checks were resumed from saved files.

The exact matched tangent-radius construction was disconnected and rejected.
No tolerance reset, material-equivalence claim for casting changes, or acceptance
limit relaxation is adopted. The trace script reads the frozen deep-drain controls/module, this repository's
prior pump report and shared shape helpers. Run it with the project headless
launcher and a separate output workdir; it does not build an assembly.

The small `probe_empty_difference.py` run on FreeCAD1.1.1/OCC7.8.0 confirms
that a contained-box difference can have `isNull()==False` with no solids,
faces or volume. Its second cut succeeds, unlike the actual casing check;
this probe establishes the empty-compound distinction, not a universal failure.
The completed nominal casing check handles empty material and passes the fixed
region comparison. `empty_difference.json` retains the observed results.
