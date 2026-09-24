# Curved brake mass-property integration — 24 September 2026

The native and STEP brake solids pass validity, bidirectional material differences
and kernel tolerance checks, but default FreeCAD mass properties disagree. For
example, the low-speed steel band reports 592,815.2466 mm³ before export and
593,730.0685 mm³ after import. Neither is the converged result.

On FreeCAD 1.1.1 / OCCT 7.8.0, adaptive Gauss integration of the **unchanged BReps**
converges to 593,632.445071 mm³ in both files. Gauss-Kronrod at 1e-12 independently
agrees to 0.0000004 mm³ and about 0.0000000003 mm in centroid. The source for both
methods and their convergence records are retained here. The method overloads
are documented in the installed `BRepGProp.hxx` header.

`lib/mass_properties.py` compiles the small C++ adapter against that same snap.
It checks runtime version, finite results, reported integration errors and
convergence at relative integration requests 1e-10 and 1e-12. Its helper test
checks an analytically known, translated/rotated sleeve, four native/STEP brake
pairs, and four deliberately displaced centroid failures. All nine pass.
The four native/STEP adaptive volume differences are below 0.000005 mm³ and
centroid differences below 0.000000009 mm. This changes measurement, not geometry.
The independent material, tolerance and saved-hierarchy gates remain required.

The initially failed exchange report remains a diagnostic; do not treat its
centroid failures as accepted until the adaptive full-installation check passes.
The probe BReps remain under `.work/transmission-brake-bands/probe01`; the same
candidate definitions can be extracted from the saved native document.


`replay.py --output <fresh-directory>` runs through the FreeCAD headless launcher
and reads the retained native and STEP files directly. Its nine analytic,
round-trip and negative-control checks pass (`replay_checks.json`), so this
reproducer does not require the earlier `.work` probe BReps.

The completed original exchange has 36 default-centroid failures among 259
comparisons, with no material or tolerance failures. The combined adaptive
report passes all 259 under the original spatial material, centroid and kernel
tolerance criteria. The extra net-volume diagnostic on four large drums and
its centered replay are retained under `world_coordinates/`.
