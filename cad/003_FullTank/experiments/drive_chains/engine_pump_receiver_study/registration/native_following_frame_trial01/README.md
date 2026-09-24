# Transmission frame following the shaft — 23 September 2026

This is the preferred **development placement** for the next reconstruction work.
Moving the original frame with the shaft restores its local casting and MX5
interfaces, improves agreement with SNL Plate23, and introduces no frame collisions
in either saved context. Complete hull attachment and installation remain open.

`PowertrainWithFollowingFrame.FCStd` starts from the checked engine-support trial,
retaining the original transmission castings. Only `TransmissionMountingFrame`
moves: +6.264279 mm X and +51.369431 mm Z. Its 15 physical occurrences inherit the
translation. All other occurrence frames, definition identities and ownership stay
unchanged. The model still has 2,393 physical occurrences and 461 definitions.
The separately retained fixed-frame trial is not used as this model's parent.

## Saved geometry and exchange

- **53 independent checks pass.** All 2,393 occurrence frames and 191 assembly
  records match the intended change. Every frame definition keeps exact BRep
  bytes; seated pad areas, case/channel contacts and MX5 joints are restored.
- **77 nearby material pairs pass** after filtering all 2,393 development
  occurrences. Filtering all **5,326 physical standard-tank occurrences** finds
  one possible frame/roof pair; its exact material intersection is empty. The
  other standard parts are spatially separated. Layout envelopes are excluded
  from physical collision checks and remain identified in the context manifest.
- **36 strict STEP comparisons pass:** 15 installed frame members, five castings
  and 16 MX5 constituents. `FollowingFrameInstallation.step` is a local assembly
  export, not a whole-tank export. Validity, material in both directions,
  tolerances and centroids are checked.
- Fresh reproduction matches all **1,409 archived BReps, 8,732 object types and
  113,542 persistent object properties**, along with extracted definitions,
  occurrences and assemblies. No object properties were excluded.

Nineteen definition BReps normalize differently from the immediate parent on save.
The separate `check_following_frame_preservation.py` job compares all final
definitions directly with the already checked merged-pump source, except the three
intentionally rebuilt engine brackets, which are compared with their checked
support source. Its final `definition_preservation_checks.json` is the authority
for closing that gate; an unfinished progress file is not qualification.

## Sources and remaining interfaces

The [source overlay](source_frame_comparison.png) keeps the prior bearing-based
SNL23 calibration. Fixed-frame channels are red, following-frame channels blue,
and the retained case gray. The lower following web falls inside the manually
inspected source band. The upper web is about 3.606 mm above its nearest edge,
under this conditional scale. This is closer than the fixed-frame result, but
source distortion and section uncertainty remain; the bands are not tolerances.

The [hull side view](hull_attachment.png) uses the actual saved standard bulkhead
and floor. Channel-to-bulkhead separation changes from 12.507 to **18.771 mm**;
lower-channel-to-floor separation changes from 3.849 to **55.218 mm**. Neither
hypothesis currently supplies the complete mounting interfaces.

HB127 explicitly identifies the rear bulkhead as the holding interface. Directly
inspected SNL27 lists two M388 holding bolt assemblies, each with a 3/4-inch nut
and lock washer; SNL205 lists four M390 holding screws. Their lengths, locations
and receiver profiles remain to be reconstructed. Their names alone do not prove
an adjustable spacing arrangement. SNL95 lists two M391 feet with 1-inch jam nuts;
the previously recorded nested SNL42 quantity conflict remains. The 5.806 mm
inner-bracket packing gap, twenty MX1 joints, frame rivets and brake supports are
also unfinished. Long MX5 bosses still differ from the visible cast-wing outline.

Use this placement to continue the mounting and chain-casing work, documenting
the missing geometry rather than filling gaps arbitrarily. The mean shaft station
remains provisional. Full drivetrain/hull clearance, service access and historical
configuration qualification are not established by these frame-only checks.

## Visuals and reproduction

The isometric, support view, hull side view, case detail and source overlay were
directly inspected. Three progression snapshots bring the total to **158**,
preserving all 155 previous images and 24 recorded native files. Standard tank011
remains unchanged at 5,326 physical occurrences; poses remain deferred.

Run FreeCAD scripts through `skills/freecad-reconstruction/scripts/freecad_headless.py`
with absolute arguments and distinct work directories:

1. `build_powertrain_following_frame_trial.py --source <native_support_trial01> --output <fresh>`
2. `pump_integration_worker.py extract --input <fresh>/PowertrainWithFollowingFrame.FCStd --output <fresh>/isolated/manifest.json`
3. `extract_standard_tank_context.py --native <build/native/MarkVIII.FCStd> --output <standard-context>`
4. `check_powertrain_following_frame_trial.py --candidate <fresh> --standard-context <standard-context>`
5. `exchange_powertrain_following_frame_trial.py --candidate <fresh>`
6. `render_powertrain_following_frame_trial.py --candidate <fresh> --standard-context <standard-context>`

Use ordinary Python for `check_following_frame_preservation.py --candidate <fresh>`;
it starts one isolated native worker per distinct comparison. After a second
fresh build/extraction, use `check_powertrain_frame_reproduction.py --candidate
<first> --reproduction <second>`. Saved manifests reference regenerable extraction
caches; those paths are not native-document dependencies. The standard context
extractor follows the existing external-link traversal and checks that all source
native files remain unchanged.
