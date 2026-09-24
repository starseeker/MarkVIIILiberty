# Transmission supports with a fixed frame — 23 September 2026

This trial restores local transmission mounting interfaces while holding the
existing frame planes fixed. **Mechanical checks pass, but the source overlay
worsens the frame's position relative to the shaft.** Retain this hypothesis for
comparison; it is not an accepted historical installation. Compare a frame that
follows the shaft before selecting the station or rebuilding the chain cases.

`PowertrainWithRebuiltTransmissionSupports.FCStd` retains 2,393 physical
occurrences. Three casting definitions change: inside and outside fixed-bearing
brackets, each used twice, and the central bevel case. Sixteen constituents of
the four MX5 case/frame joints move back to their retained frame seats. Other
occurrence frames and all frame/floor member geometry are preserved.

## Source constraints and construction

HB125 Plate78, HB126 Plate79 and SNL Plate23 show the channels behind the case
and bearing supports. The earlier frame planes and sections remain conditional
reconstruction dimensions. Bracket feet retain their original world planes,
widths and stock; the cast webs connect them to the trial shaft. The 5.805714 mm
inner-bracket packing gap remains unresolved. MX1 bracket bolts, packing,
complete frame/hull attachments and the remaining brake system are still required.

Detailed bearing saddles, studs, blind receiving bosses and pockets survive
the web reconstruction. The pre-MX5 detailed case is rebuilt first, then its four
MX5 bosses and receivers are regenerated at the frame joints. All sixteen
stud/nut/pin/washer occurrences follow those joints. Printed 142.875 × 19.05 mm
studs and existing hardware definitions are retained. The alternative printed
139.7 mm length, long cast-boss approximation and conditional washer allocation
remain documented in the [original packet](../../../../../packets/I03-case-mount-trial.md).

The first attempt, retained in `../native_frame_trial01`, kept the old MX5 bosses
with the moved shaft. Its upper bosses detached from the rebuilt webs, producing
three solids. This exposed the missing frame-joint dependency; no faulty native
was saved. The successful trial rebuilds the actual attachments.

## Verification

- **125 native checks and all 279 affected/context material pairs pass.** Spatial
  filtering covers all 2,393 saved context occurrences. Checks include retained
  details, material/void differences, pad areas, packing gaps, liner/cap interfaces,
  frame bores, washer seats and blind ends.
- **26 strict STEP comparisons pass:** three rebuilt definitions, five installed
  castings, sixteen MX5 joint constituents and two unchanged frame channels.
  Validity, solid count, both material directions, tolerances and centroids are
  checked. This is a local exchange, not a whole-tank export.
- Local X/Z variations of (−2,−10) and (+2,+10) mm each pass **37 checks**.
  These test regeneration and seats; variant whole-assembly/chain/STEP
  qualification is not claimed.
- A fresh nominal rebuild matches **1,409 archived BReps, 8,732 object types and
  113,545 persistent object properties**, plus all 461 definition, 2,393 occurrence
  and 191 assembly records.

The initial checker mistook the stud's non-tight bounding-box width, 19.058984 mm,
for its diameter. Actual axial cylinder faces have radius 9.525 mm and all material
fits inside the printed 19.05 mm stock. Corrected checks measure those surfaces
and material; the nominal dimension and tolerance are unchanged. Both checker
versions and the failure are retained under `diagnostics`.

Nineteen unchanged definition BReps differ from the immediate parent after native
save normalization. Their strict preservation checks and predecessor gates remain
open; affected-region checks do not close those independent gates.

## Visual/source review and disposition

The [isometric](isometric.png), [support view](transmission_supports.png),
[MX5 detail](case_mounting.png) and [source overlay](source_frame_comparison.png)
were directly inspected. The detail crops channel ends for display only. The
overlay sections the actual case at Y118 mm through the prior independent
bearing-based SNL23 calibration. Previous case geometry is red, revised geometry
blue, and the retained frame gray. No source warping or fitting is applied.

Both channels project about 55.8 pixels lower relative to the shaft than their
previous relationship. Revised web projections fall roughly 36–60 mm below broad
manually inspected source bands under that conditional scale. Drawing accuracy,
cutting plane and calibration residuals remain uncertain; these observations are
not machining tolerances. Nevertheless, the disagreement prevents treating local
fit as evidence for the historical station. Long bosses also remain forward of
the visible casting-wing silhouette.

Moving the frame with the shaft would restore the previous relative projection
mathematically; its hull/floor attachment consequences still need geometry checks.
`source_comparison.json` records this next decision. Standard tank011 is unchanged
at 5,326 physical occurrences. Three progression images preserve this experiment
and its source disagreement: 155 total, with all 152 earlier images and 24
recorded native files preserved.

## Reproduction

Run the scripts under `experiments/drive_chains` through the repository headless
launcher, with absolute file arguments and separate work directories:

1. `build_powertrain_frame_trial.py --source <native_support_trial01> --output <fresh_frame>`
2. `pump_integration_worker.py extract --input <fresh_frame>/PowertrainWithRebuiltTransmissionSupports.FCStd --output <fresh_frame>/isolated/manifest.json`
3. `check_powertrain_frame_trial.py --candidate <fresh_frame>`
4. `exchange_powertrain_frame_trial.py --candidate <fresh_frame>`
5. `probe_powertrain_frame_variants.py --candidate <fresh_frame>`
6. `render_powertrain_frame_trial.py --candidate <fresh_frame>`

After a second fresh build/extraction, use ordinary Python for
`check_powertrain_frame_reproduction.py --candidate <first> --reproduction <second>`.
Input native, source, generator and baseline BRep hashes are in `report.json`.
Saved manifests reference regenerable extraction caches; those paths are not
external dependencies of the native document.
