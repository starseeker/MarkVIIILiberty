# Chain casings rebuilt at the revised shaft station — 23 September 2026

`PowertrainWithRebuiltChainCasings.FCStd` regenerates the casing bodies, removable
caps, wall collars, cap cleats/packing and bulkhead passages around the conditional
mean-axis chain route. It starts from the following-frame trial and retains
**2,393 physical occurrences, 461 definitions and 191 assemblies**. Twelve
definitions are rebuilt, 134 fastening occurrences repositioned, and 157 installed
occurrences are affected. The standard tank011 remains unchanged.

The generators retain **3 mm normal sheet stock** and the handbook's **6⅝ inch
(168.275 mm) maximum width**. They rebuild the dependent openings and joints from
their controls. Before changing the route, all twelve original definitions are
regenerated and compared with the saved parent: both material differences are
zero. Original trim and supporting-bracket interfaces are also retained. No
affine deformation of finished stock is used.

## Saved geometry and exchange

- **326 independent checks pass**, including all occurrence frames/owners,
  assembly frames, 16 stock witnesses, complete bores, fastener seating and
  packing bearing areas. A 0.01 mm lifted-packing negative control loses contact.
- **1,340 nearby development material pairs pass**, after filtering the full
  development context. **27 standard-context material pairs pass**, after
  filtering 5,316 retained physical occurrences. Ten explicitly listed standard
  occurrences are superseded by development geometry; fifteen layout envelopes
  are nonphysical. This qualifies the affected casing parts in those contexts,
  not the entire powertrain installation.
- Both casing-body/drum gaps are **2 mm**. Chain/casing comparisons pass; the
  reported minimum body/chain distance is also 2 mm.
- **169 strict STEP comparisons pass**: twelve definitions plus 157 installed
  occurrences. `ChainCasingsDefinitions.step` and `ChainCasingsInstallation.step`
  retain the established material, tolerance, validity and centroid criteria.
- Both alternative solved source-axis stations pass **63 local regeneration
  checks each**. These variations qualify local stock, openings and joints;
  their complete chain/context/STEP acceptance remains outside this test.
- A fresh nominal build reproduces all **1,409 archived BReps, 8,732 object
  types and 113,542 persistent properties**, plus every extracted definition,
  occurrence and assembly. No persistent properties were excluded. The existing
  `check_powertrain_frame_reproduction.py` is reused; its generic receipt still
  calls the scope a transmission-support rebuild.

Sixteen otherwise unchanged definitions serialize differently on saving and still
require strict material-preservation checks. The parent following-frame model
also has an inherited direct-source comparison running. Passing the local casing
checks does not close either pending preservation gate.

The initial checker incorrectly required a rivet shank to touch the intermediate
packing bore. Its 0.25 mm radial clearance equals the retained 0.5 mm diametral
hole allowance and matches the parent. The corrected checker measures that
clearance and independently verifies the complete packing bearing faces. Geometry
was unchanged. The first failure, checker and finished material results are
retained in `diagnostics/initial_check`; reused material results are bound to the
exact native, source, context and pair-set hashes.

## Source and visual review

HB134 describes sheet-steel casings, their maximum width, supporting angles and
removable cap. It requires the main casing to be installed before the epicyclic
gear. The **3 mm thickness, detailed profiles, local taper, seam and hole pattern
remain documented estimates**; no removal path is qualified here.

The [source overlay](source_casing_comparison.png) compares the old red and revised
blue central sections using the original SNL2 global calibration. The roller end
stays fixed while the small end rises. The drawn small-gear center remains below
the revised station: this is visible disagreement, not proof of correct shaft
height. The conditional mean-axis study and its ±35.57 mm source-pick uncertainty
remain applicable.

The selected seven cap-bolt sets per side, nested rivet schedule, trim identities
and wall rivets are retained. Conflicting SNL totals, M1585/M1586 identities and
the handbook's bolted mounting versus SNL wall-rivet allocation remain open.
`source_review.json` preserves the source records and qualifications.

Four views were directly inspected: [isometric](isometric.png),
[display-only section](casing_section.png), [joints](casing_joints.png) and the
source overlay. Three new progression images bring the total to **161**, with all
158 earlier images and 24 recorded native files preserved by hash. Sections alter
the review display only. `visual_review.json` and `render_receipt.json` bind the
review to the saved model and images.

## Reproduction and next work

Use the repository headless launcher with absolute file arguments and a fresh
output directory. Run `build_powertrain_casing_trial.py` with `--source` pointing
to the following-frame native, `--standard-context` pointing to the extracted
standard context, and `--output` pointing to the new directory. Its original
generator dependencies and controls are frozen in `frozen_inputs`.

Extract the saved result with `pump_integration_worker.py extract --input
<native> --output <fresh>/isolated`. Then run `check_powertrain_casing_trial.py
--candidate <fresh> --standard-context <context>`,
`exchange_powertrain_casing_trial.py --candidate <fresh>` and
`probe_powertrain_casing_stations.py --candidate <fresh>` through the launcher.
Omitting `--reuse-material-from` recomputes the material comparisons. The renderer
uses `render_powertrain_casing_trial.py --candidate <fresh>`. After a second fresh
build/extraction, run the reproduction checker with ordinary Python and
`--candidate <first> --reproduction <second>`.

The extraction manifests retain regenerable cache paths; those paths are not
native-document dependencies. Frozen validation scripts and manifests identify
the actual checked versions. Existing standard extraction uses
`extract_standard_tank_context.py` and the established external-link traversal.

Continue source-led transmission holding interfaces, feet, packing and hardware.
Complete the preservation checks before standard promotion, then continue the oil
manifold, engine cylinders and remaining tank interiors. Historical station,
complete installation and full-tank completion are still unqualified; poses
remain deferred.
