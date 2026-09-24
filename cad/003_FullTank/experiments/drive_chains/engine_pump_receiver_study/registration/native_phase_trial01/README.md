# Coupled planetary phases — 23 September 2026

This saved trial corrects the output-shaft/carrier interference exposed by the
preceding registration diagnostic. It retains 2,393 physical occurrences and
461 definition identities, changing the phase of 142 occurrences. It represents
one static assembly alignment; motion and pose variants remain deferred.

The original HB120/122 text and Plates73–75 (scans MarkVIII061/062) identify the
mechanical coupling: the cross shaft drives the large sun and small ring, the
output follows the large carrier, and the large ring/case carries the small
planet pins. The small sun follows the high-speed drum. Printed tooth counts
are 18/27/72 for the large stage and 30/78 for the small sun/ring; 24 small-planet
teeth follow from their common pitch geometry.

Holding the cross shaft and its upstream components fixed, the required output
change of +2.185742833° implies +2.732178541° for the case/small carrier,
+3.642904721° total large-planet spin, +9.835842748° for the small sun/high-speed
drum, and −6.147401717° total small-planet spin. These are rotations about global
+Y; planet centers also orbit with their carriers. Saved parent-relative frames
preserve the handed assemblies.

`independent_checks.json` passes all nine criteria, all twelve planet-mesh checks,
four spline interfaces and 832 affected-part material comparisons against the
full development context. The checker derives the required angle from the saved
shaft/carrier mismatch, then measures the resulting frames independently of the
builder's angle table. Mesh clearances and tooth material are checked together.
A half-tooth misclock and the predecessor carrier clash are rejected controls.

The builder never assigns a definition shape. Nevertheless, 16 serialized BReps
differ after saving and still require strict material-preservation comparison;
the predecessor's 60 pending comparisons also remain open. Matching identities
and successful local fit checks do not close those gates. Casings, transmission
supports, historical station choice and complete installation are unqualified.

The subsequent [engine-support trial](../native_support_trial01/README.md)
retains these phases and provides the inspected gear detail and powertrain views.
`report.json` binds the source native, generator, controls and source dossiers.
`frozen_inputs` and `frozen_validation` preserve the implementations used.

Run the following scripts through
`skills/freecad-reconstruction/scripts/freecad_headless.py`, supplying absolute
paths for all file arguments and a separate `--workdir` for each run:

1. `build_powertrain_phase_trial.py --source <native_trial01> --output <fresh_phase>`
2. `pump_integration_worker.py extract --input <fresh_phase>/PowertrainCoupledPhaseTrial.FCStd --output <fresh_phase>/isolated/manifest.json`
3. `check_powertrain_phase_trial.py --candidate <fresh_phase>`

The source trial also needs its extracted `isolated/manifest.json` and BReps.
Re-extract them from its hash-bound native with the same worker if absent.
Saved manifests are evidence; their absolute BRep paths refer to regenerable
working files and must not be treated as portable native dependencies.
