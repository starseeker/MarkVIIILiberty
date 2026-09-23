# Radial bearing cage STEP diagnosis

FreeCAD 1.1.1 / OCC 7.8.0. The axial-pole spherical pockets gave a valid
native cage but invalid STEP. Tangential poles also failed STEP. Radial
poles place the singularities outside the cylindrical cage stock; that
version preserves the original material in both directions and passes
unchanged strict native/STEP criteria. No physical dimensions changed.

`results.json` records all three trials. The before/after BReps and STEP
files are frozen beside it. Native maximum tolerance drops from
2.27297e-6 to 8.67872e-7 mm; reopened radial-pole STEP has maximum tolerance
2.41685e-7 mm, zero bidirectional material differences, mass difference
2.15e-6 mm3 and centroid difference 1.75e-10 mm.

The complete failed native and five reviewed images are retained in
`.work/engine-water-pump/native_pass_step_cage_failure`.


Replay `check_saved_cage.py` through the FreeCAD skill launcher using a fresh
work directory. It reads the frozen original BRep and controls beside the
script and writes all generated shapes/results into the chosen work directory.
The project ring/cleanup/mass helpers are imported from the repository.
