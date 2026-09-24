# Rebuilt engine supports — 23 September 2026

The three engine suspension castings now connect the unchanged floor attachments
to the trial mounting plane at Z900.602941 mm. The saved development assembly
retains 2,393 physical occurrences and the preceding coupled planetary phases.
This is a locally checked reconstruction at a provisional station, not an
accepted whole-tank installation.

The rear bracket bases and front pivot hub retain their original receiving
interfaces. Bracket webs/arms are regenerated using the existing suspension and
front-yoke generators. The rails retain their stock, bores and X2940..4120 mm
stations; only their height changes. Their earlier diagnostic X translation is
removed. Floor, crossmember and cleat receiver shapes are unchanged. All hardware
dimensions are retained. Three definitions are replaced, 61 support occurrences
are assigned their required frames, and 39 occurrences change shape or placement.

The original support packets distinguish printed hardware sizes from estimated
casting profiles, rail stock and installation dimensions. These estimates remain
estimates. The source's tank-versus-aviation engine mounting-hole/bolt-count
ambiguity remains unresolved; this trial does not claim complete engine mounting
fastening or structural strength.

The saved native passes **191 independent checks and 102 affected-part material
comparisons** against all 2,393 context occurrences. Four rail/bracket contacts
are restored with zero gap and zero volumetric overlap. Floor/packing/pivot seats,
bores, clamped shaft material, retained base/hub regions, lock seating and blind
floors pass. Actual rail/flange bearing area is 52,454.767 mm² per side.

All **64 strict STEP comparisons** pass: three rebuilt definitions and 61 installed
support constituents. The comparison uses validity, solid count, both material
differences, kernel tolerances and centroids. `EngineSupportDefinitions.step`
and `EngineSupportInstallation.step` cover that scope, not the entire powertrain.

A fresh nominal build matches all **1,409 archived BReps, 8,732 object types and
113,542 persistent object properties**, as well as the 461 definition records,
2,393 occurrence records and 191 assembly records. No properties were excluded
from the object-property comparison. This reproduction is not a new parameter
variation or independent confirmation of historical dimensions.

## Inspected views and retained diagnostics

The [isometric](isometric.png), [engine-support detail](engine_supports.png) and
[planetary detail](planetary_phases.png) were directly inspected. They show actual
saved geometry at its installed coordinates. Omitted machinery and outlined
floor/casings are display choices. The supports visibly reach their rails and
retained floor seats; both planetary stages retain three planets and their
receiving carriers. The old chain cases and transmission frame remain visibly
out of alignment and require coordinated rebuilding. No pose variant is added.

The initial checker incorrectly used solid/solid intersection area to measure
touching planar seats. On this runtime it returns zero even for touching boxes.
`contact_probe.py` verifies the expected 100 mm² through actual coincident faces,
then applies that measurement to the rails. A 0.01 mm flange lift removes the
contact and fails the unchanged 1,000 mm² criterion. The initial STEP checker
also assumed `CenterOfMass` exists on a generic imported shape; it now verifies
one solid and reads the constituent solid's centroid. Both failed runs and
their implementations are retained under `diagnostics/initial_checks`.

## Remaining acceptance gates

- Strict preservation checks for save-normalized unchanged definitions remain
  open: 16 differ from the phase parent, with the predecessor gates inherited.
- The mean-axis location is still a hypothesis with ±35.57 mm source-pick height
  uncertainty. The pump's 7.494 mm floor-envelope clearance is conditional on it.
- Chain casings, transmission bearing/frame seats, controls, pipework and nearby
  hull interfaces need reconstruction and complete installation checks.
- Engine mounting holes, remaining engine components and the full tank are
  incomplete. Standard tank011 remains unchanged at 5,326 physical occurrences.

## Reproduction

Run the following scripts from `experiments/drive_chains` through the repository's
headless launcher, using absolute file arguments and separate work directories:

1. `build_powertrain_support_trial.py --source <qualified_local_phase_trial> --output <fresh_support>`
2. `pump_integration_worker.py extract --input <fresh_support>/PowertrainWithRebuiltEngineSupports.FCStd --output <fresh_support>/isolated/manifest.json`
3. `check_powertrain_support_trial.py --candidate <fresh_support>`
4. `exchange_powertrain_support_trial.py --candidate <fresh_support>`
5. `render_powertrain_reconstruction_trial.py --candidate <fresh_support>`

The source phase trial also needs its extracted manifest and BReps. For a second
fresh build, run `check_powertrain_support_reproduction.py --candidate <first>
--reproduction <second>` with ordinary Python after extracting both. The checked
in saved manifest records provenance; its absolute BRep paths are regenerable
working files, not external dependencies of the native document.
