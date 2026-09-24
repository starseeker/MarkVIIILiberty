# Transmission bracket-to-channel joints — 24 September 2026

`PowertrainWithBracketMounts.FCStd` adds twenty MX1 bolt assemblies and their
MX13 bevel washers to the four fixed transmission bearing brackets. Each joint
has a bolt, castle nut, formed split pin and separate washer: **80 new physical
occurrences**. The development hierarchy now has **2,473 physical occurrences,
463 definitions and 215 assemblies**. Four receiving definitions change; all
pre-existing occurrence placements remain fixed. Standard tank011 is unchanged.

## Evidence and approximation

SNL28 specifies twenty MX1 assemblies, each with a ¾-inch SAE castle nut and
⅛ × 1½-inch split pin. SNL96 assigns twenty of these assemblies and twenty MX13
washers. The global washer total of 24 is consistent with these twenty plus the
four existing MX5 case joints. The longer MX1 split pin has its own definition.

The **2½-inch bolt length, head dimensions, spotfaces, clearances and hole
distribution are estimates**. The selected pattern gives four bolts per inside
bracket and six per outside bracket. Source counts do not uniquely establish
that pattern. The inside casting's pad and joining web move rearward 5.805714 mm
to the outside casting's pad plane, retaining pad thickness and later features.
This equals eight source pixels, exceeding the original four-pixel edge-pick
allowance. It is a declared mechanical hypothesis, not a source correction.
No M386/M387 fiber-packer identity has been assigned to that former gap.

The [handbook comparison](source_bracket_comparison.png) uses a camera with the
forward input axis pointing upward, matching the apparent orientation of the
removed unit in HB126 Plate79. Installed CAD placements remain unchanged. The
earlier front/rear camera attempts and omitted input-housing display are retained
as diagnostics. The revised view makes the support, shaft, drum and channel
arrangement comparable; it does not establish a dimensional fit to the photograph.
The central casting and bracket webs remain visibly simplified, and channel-face
fasteners, brake equipment and holding interfaces are still incomplete.

HB209 and standalone SNL95 favor two M391 support feet, while the nested SNL42
schedule implies four. HB209 distinguishes two M389 and two M390 holding screws;
SNL205 lists four M390. These quantity/identity conflicts remain open. HB127
requires mounting to the rear bulkhead; these local joints do not complete that
attachment or validate a removal path.

## Qualification

- **257 saved-geometry checks pass:** all occurrence frames and owners, prior
  assembly frames, complete receiver bores, bearing areas, eight casting-pad
  contacts, split-pin stock length and castle-nut retention. Lifted-seat,
  displaced-shank, nut-motion and altered-bearing negative controls are included.
- All **418 nearby development material pairs** and the one possible retained
  standard-context pair pass. Spatial filtering covers all development parts and
  5,316 retained standard occurrences. The scope is the 86 affected occurrences,
  not full powertrain or full-tank qualification.
- **94 strict STEP comparisons pass:** eight definitions and 86 installed
  occurrences. Both STEP files are retained, with surface curves enabled.
- All **457 unchanged definitions** match the immediate parent: 429 exact BReps
  and 28 strict material comparisons. The casing parent's 449-definition check
  and the preceding frame's 461-definition direct-source check also finished.
- Moving the transverse hole patterns outward by 4 mm and lengthening estimated
  bolt stock by 3.175 mm passes the same 257 checks and 418 + 1 context pairs.
  This is a regeneration test; it does not select a historical alternative or
  claim a separate STEP qualification for the variation.
- A fresh nominal build reproduces **1,415 archived BReps, 9,048 object types,
  117,408 stable properties**, all definitions, placements and assembly trees.
  Only the 24 automatically generated UUID values on newly created `App::Part`
  containers may vary. Both UUID sets are valid and unique; inherited UUIDs and
  every other persistent property must match. The initial strict-UUID failure
  and exact differences are retained in `diagnostics/initial_reproduction`.

The first geometry checker omitted the two new library definitions from its
allowed children and used a bearing witness containing the intentionally changed
web. The second narrowed witness still included 642.996876 mm³ of that web and
then failed during chained Boolean subtraction. Diagnostics locate that difference
entirely within the declared web change. The final checker separately preserves
the bearing annulus, backbone and stud lugs, and checks **the complete casting**
for any material change outside the pad/web revision and drilled/spotfaced regions.
A union-based equivalent set difference avoids the kernel error. Deliberately
damaged bearing material and filled bores fail the checks. The saved model did
not change during these measurement corrections; no tolerances were enlarged.

## Rebuild and continue

Run project scripts through `skills/freecad-reconstruction/scripts/freecad_headless.py`
with absolute arguments and fresh output directories. From the drive-chains
script directory, the sequence is:

1. `build_transmission_bracket_mount_trial.py --source <casing-trial-directory> --output <fresh>`
2. `pump_integration_worker.py extract --input <fresh>/PowertrainWithBracketMounts.FCStd --output <fresh>/isolated/manifest.json`
3. `check_transmission_bracket_mount_trial.py --candidate <fresh> --standard-context <extracted-standard-directory>`
4. `exchange_transmission_bracket_mount_trial.py --candidate <fresh>`
5. `render_transmission_bracket_mount_trial.py --candidate <fresh>`

Use ordinary Python for `check_transmission_bracket_definition_preservation.py
--candidate <fresh>` and, after a second independent build/extraction,
`check_transmission_bracket_reproduction.py --candidate <first> --reproduction <second>`.
The parameter trial uses `--controls <this-directory>/parameter_trial/controls.json`.
Frozen inputs, validation scripts, extraction manifests and result hashes retain
the checked versions. BRep-cache paths in manifests are regenerable caches, not
native document dependencies. Parameter and reproduction natives remain in the
durable `.work/transmission-bracket-mounts/` workspace; parameter changed-definition
BReps and reports are retained here.

Continue with the remaining transmission holding interfaces, support feet and
frame hardware, while improving source-visible casting profiles. Then continue
the oil manifold, engine cylinders and remaining tank interiors. Historical
station and complete installation remain unqualified; pose variants stay deferred.
