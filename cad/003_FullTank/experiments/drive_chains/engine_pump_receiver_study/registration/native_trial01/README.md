# Powertrain placement diagnostic — 23 September 2026

This is a **development diagnostic with unresolved installation interfaces**.
It is not an accepted station or an update to the standard tank. It retains all
2,393 occurrence identities from the coupled-pump development assembly.

The common-horizontal-axis hypothesis moves engine, clutch, transmission,
output bearings and engine rails +6.264279 mm in X and +51.369431 mm in Z.
Both 50-pitch chains are reposed around the unchanged roller-pinion axes and
17.21° phases. The small pinions, output shafts and brake drums receive a
2.185743° phase change. Existing casing stock, floor attachments, suspension
brackets and transmission frame remain in place to expose required changes.

## Saved-file findings

- All 2,393 composed frames, identities and owning parents match the declared
  changes; maximum frame error is 1.19e-12 mm.
- The 700 saved bar-end/joint witnesses preserve both 76.2 mm pitch loops.
  All **886 actual chain material pairs pass**, including both pinions.
- Rephased output shafts clear their brake drums and small pinions. The negative
  control retaining the old shaft phase overlaps the pinion by 7,708.264 mm³.
- The actual oil-pump envelope changes from **43.876 mm below the floor** to
  **7.494 mm above it**. The three saved floor plates retain their source frames
  and BReps. The drawing-pick height bound remains ±35.57 mm; this clearance
  does not establish the historical engine height.
- The shifted shafts interfere with their internal planet-carrier disks by
  **2,038.844 mm³ per side**, versus the source's 0.1 mm clearance. Internal
  carrier, planet and receiving-spline phases must be solved together.
- **128 of 616 nearby chain/casing pairs interfere** with the obsolete casing
  geometry. Casings and their wall, cap, trim and support interfaces need
  regeneration from their stock and joint controls.
- All four tested engine rail/bracket contacts separate by **51.369431 mm**;
  the source contacts had zero gap and zero overlap. Rebuild suspension geometry
  against the unchanged floor receivers. Transmission bearing feet and their
  frame attachments also need coordinated revision.

The nine placement/selected-interface criteria pass. **Full material preservation
is pending:** 401 of 461 definition BReps remain byte-identical after ordinary
native saving; 60 have different bytes. All definition identities and source
metadata match. Sample differences include signed zeros and last-digit changes,
but that observation does not qualify every changed BRep. Require the established
strict bidirectional material/tolerance comparisons before accepting them. The
source assembly's own remaining material checks are still running. Its separate
source-profile oil-pump STEP check completed after this trial was built: all 186
comparisons pass, bound to native `cbe470a469e90f179814cb2d8148da382135c7af8cfd9f44a0c9fc663ae22aad`.
The build report retains the pending status at construction time. No combined
STEP export is qualified here.

`independent_checks.json` records chain, placement, floor and diagnostic interface
results. `support_contacts.json` measures the actual mating rail/bracket solids;
the earlier measurements against packing pieces are reference distances, not
assertions that those pieces directly contact the rails. `diagnostics/initial_check`
retains a checker failure caused by looking up an object name in an occurrence-ID
map and the initial BRep-byte comparison. The ID lookup was corrected; pending
material comparisons remain explicit.

The [isometric](isometric.png) and [chain elevation](chain_elevation.png) were
directly inspected. They display selected actual saved solids, with old casings
and floor in outline. Omitted internals remain in the native document; the views
do not represent component coverage or a finished installation. These are
diagnostic images, outside the accepted visual-progression sequence.

## Continue from this trial

1. Solve the internal transmission carrier/planet phases needed by the new
   output shaft orientation, preserving bearing interfaces and gear engagement.
2. Regenerate the casing route and support geometry with existing stock sizes,
   joints, fasteners and hull receivers; do not affine-warp finished parts.
3. Recheck controls, lines, nearby equipment, source silhouettes and alternative
   height interpretations. Complete pending definition and STEP validation before
   promotion to the standard assembly.

## Reproduce

Run the scripts in `cad/003_FullTank/experiments/drive_chains` through
`skills/freecad-reconstruction/scripts/freecad_headless.py`. Use a fresh absolute
output path for `build_powertrain_registration_trial.py --output OUTPUT`; the
builder refuses to overwrite an existing native.

Then run `pump_integration_worker.py extract --input OUTPUT/PowertrainRegistrationDiagnostic.FCStd
--output OUTPUT/isolated/manifest.json`, followed by
`check_powertrain_registration_trial.py --candidate OUTPUT --chain-material` and
`render_powertrain_registration_trial.py --candidate OUTPUT`. The checker also
requires the source assembly's extracted manifest; regenerate it from the bound
source native with the same extractor if its cache is absent. All file arguments
must be absolute because the launcher changes working directory. The focused
`support_contact_probe.py` is specific to this retained directory layout.
