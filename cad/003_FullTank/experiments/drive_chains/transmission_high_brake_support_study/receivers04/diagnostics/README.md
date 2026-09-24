# Receiving-case mass convergence

FreeCAD 1.1.1 / OCC 7.8.0, 24 September 2026. The receiver case is an unchanged
valid single solid during these measurements; no geometry or tolerance repair
is applied to make numerical mass values agree.

The initial [exchange report](../exchange_checks.json) passes native/STEP
material preservation and tolerance bounds, but the whole-face Gauss calculation
fails its reported-error predicate. The native case tolerance is approximately
5.05223e-6 mm and the imported STEP tolerance 3.51897e-7 mm. Both material
directions are empty under the original comparison criteria.

[case_mass/measurements.json](case_mass/measurements.json) records a separate
span-aware Gauss–Kronrod probe. Requests at 1e-10 and 1e-12 meet their reported-error
targets but differ by about 4.645e-5 mm³, exceeding the existing absolute
convergence threshold of 1e-5 mm³. A small relative error is insufficient for
that absolute criterion on this approximately 10.3 million mm³ part.

[refinement_measurements.json](case_mass/refinement_measurements.json) retains
requests through 1e-14. The 1e-12 /1e-13 pair meets both reported-error targets
and converges to about 2.3e-6 mm³ in definition and installed frames. The 1e-14
request fails its reported-error requirement and is not accepted.

`cad/003_FullTank/lib/refined_kronrod_mass.py` generates a separate versioned
adapter with these two tighter requests. `AdaptiveMass.measure` predicates,
default adapters, CAD BReps, material limits and tolerance bounds are unchanged.
The [nine controls](refined_mass_controls/qualification.json) cover analytic
boxes, annuli and exact quadratic B-spline prisms at two scales, identity and
rigid transforms, unchanged BRep bytes and open-face rejection. All pass,
including a 13.33 million mm³ curved solid. These controls qualify the measurement
option; they do not establish a historical shape.

The completed [exchange rerun](../exchange_refined02/exchange_checks.json) passes
all 13 comparisons. Only the case needs the tighter calculation; the receipt
retains its original failed Gauss measurements, actual refinement provenance
and control hash. The earlier `exchange_refined/failure_status.json` records a
precondition failure before the control receipt was ready; no STEP run completed
there. Failed controls and the initial exchange are retained.

Reproduce the independent controls with a new absolute output directory:

```sh
python3 skills/freecad-reconstruction/scripts/freecad_headless.py --workdir .work/refined-mass-runtime tools/cad_pipeline/qualify_refined_kronrod_mass.py --output /absolute/new-control-directory
```

The packet's exchange checker requires a failed baseline bound to the same
native file and a passed control receipt before `--refined-case-mass` is used.
This is an explicit diagnostic option, not a global change to numerical settings.
