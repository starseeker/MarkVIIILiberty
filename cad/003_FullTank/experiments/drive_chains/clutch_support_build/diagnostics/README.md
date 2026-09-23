# Split-pin exchange diagnostic

Tested23September2026 with FreeCAD1.1.1/OCC7.8.0.

The first candidate used transmission_stud_parts.split_pin: swept circular legs
and a polygonal eye with fused spheres. It produced valid native solids, but the
definition STEP difference reported62.9614mm3 missing and the definition/auxiliary
installed centroids differed by2.64e-6mm. Other definition/installed comparisons
passed. These are retained failures, not current acceptance results.

The replacement uses transmission_input_installation_parts.formed_pin: explicit
cylinders/torus bends and a semicircular eye with overlapping leads. The focused
probe checks a definition and two rigid installed orientations. Missing/extra
material is zero; centroid differences are below9e-9mm. Nominal source diameter
and7/8in leg-length budget remain unchanged. No tolerance was relaxed.

The complete first native and the discarded outward-jog trial remain in
.work/clutch-supports; their geometry is not the current candidate. The three
first-fit interference failures also show the original inward lever intersecting
the cone/drum/flywheel before full-source orientation review.

Run the committed probe with the project headless launcher, from the repository root:

```sh
python3 skills/freecad-reconstruction/scripts/freecad_headless.py --workdir .work/clutch-supports/probe-reproduction cad/003_FullTank/experiments/drive_chains/clutch_support_build/diagnostics/cotter_probe.py
```

The probe loads frozen helper copies from this build's inputs directory and writes
only into its chosen working directory. It is a geometric/export reproducer, not
a claim about the historical split-pin head form or original manufacturing stock.
