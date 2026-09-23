# Same native wire, two STEP export settings

The retained wire.brep is the source-length analytic drain wire. replay.py reads
that identical BRep afresh for each export. With write.surfacecurve.mode=0, the
STEP has no PCURVE entities and reopens as valid, but native-minus-STEP returns
the entire 290.387722 mm³ wire. With mode 1, 1,438 PCURVE records are retained and both
material differences have zero volume and no faces. The native shape tolerance
remains 3.4425e-7 mm; imported tolerance is 1e-7 mm in both modes. No shape or acceptance
threshold is changed to make the second comparison pass.

Run through skills/freecad-reconstruction/scripts/freecad_headless.py with a fresh
work directory. The script writes both exports and an export_mode_checks.json
receipt there and asserts the reproduced difference between the two settings.
The checked local runtime is FreeCAD 1.1.1/OCC 7.8.0. This demonstrates the importance
of matching an isolated probe to the pipeline; it does not establish a universal
failure of STEP files that omit parameter-space curves.

The production pump builder already used mode 1. Its full definition and installed
STEP results are recorded at the candidate root. The diagnostic's fixture is a
local wire only, not a substitute for those complete installed checks.
