# Ground-end spring mass integration diagnostic

FreeCAD 1.1.1 / OCCT 7.8.0. The initial 142-pair exchange passes all material,
validity and tolerance comparisons, but its five spring pairs fail the reported
integration-error requirement. The unchanged spring's whole-face Gauss result
stabilizes while reporting roughly 3.55e-10 error against a 1e-12 target.
Gauss-Kronrod also does not reach that target. These results remain failures;
stability alone is not substituted for convergence.

The retained experiment partitions the original solid into adjacent Z slabs.
Any nonconverged section is subdivided. Every accepted section must pass the
existing `AdaptiveMass` criteria. A second partition independently bisects all
accepted sections, with further subdivision where required. Each partition's
union has zero missing/added material and no adjacent overlap. Aggregate volume
and centroid must also converge under both integration precision and geometric
refinement. The original BRep and STEP files are unchanged.

For the isolated native and STEP springs, 15 initial sections and 39 refined
sections pass. Their refinement volume differences are approximately 1.90e-6
and 2.08e-6 mm³, below the unchanged 1e-5 mm³ requirement. Centroid refinement
differences are below 5e-9 mm. `mass-adaptive-partition/report.json` retains
all section results. The reusable implementation is
`cad/003_FullTank/lib/partitioned_mass.py`.

`partition-qualification/report.json` records box, rigidly placed box and cylinder
controls with analytic volume/centroid values. Deliberately missing, duplicated
and displaced sections fail the material certificate as required. The scripts
`mass_adaptive_partition.py` and `qualify_partitioned_mass.py` retain these probes.

`initial_exchange_checks.json` and `initial_exchange_checker.py` preserve the
original failed run. The targeted requalification checks all geometric criteria
again for the five springs and uses partition integration on their actual saved
native and imported STEP solids. The other 137 passing records are retained
unchanged, guarded by the native, STEP and initial-report hashes. Completion is
recorded only when the trial's `exchange_checks.json` reports all 142 passing.
