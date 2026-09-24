# Forward high-speed brake checkpoint — 24 September 2026

[Native FreeCAD assembly](PowertrainWithHighBrakeFront.FCStd): **3,091
physical occurrences, 519 shared definitions and 314 assemblies**.
[Qualification](qualification.json) covers this local reconstruction, not completion
of the tank or its high-speed brake mechanism. Standard tank011 remains unchanged.

## Added components and bounded revisions

| Components | Installed count | Evidence and approximation |
| --- | ---: | --- |
| Separate forward fittings | 4 | Inferred riveted fittings within M359/M360 identities; profile and fork width estimated |
| Steel countersunk rivets | 12 | Three 5/16 × 1⅛ inch rivets per band; heads and formed tails estimated |
| Copper lining rivets | 34 | Source lengths and per-band allocation retained; formed tails conserve the selected under-head stock model |
| Brass flathead lining screws | 2 | No.14 (¼)-20 × ¾ inch; nominal shank without thread helices |

Both backings gain the receiving holes and tail seats. The estimated M361 foot
extends from 255° to 261° to receive the first short-lining rivet; its eye and rear
coupling frames are retained. The existing coarse M263 rear bridge gains a
continuous R208 mm recess over each lining width plus 1 mm per side. This is an
interface-driven estimate: SNL22 does not establish the unseen bridge profile.
The source-sized rivets exposed this missing clearance; they were not shortened.

Checks preserve all case material outside the two bounded recesses, including
bearing seats/receivers, and demonstrate a continuous 15.98 mm bridge-stock witness.
That geometric witness does not establish structural strength. No printed lining,
drum or fastener stock size changes. All inherited occurrence frames and owners
remain in place; eight new groups own the forward joints and lining fasteners.

## Evidence and validation

All 16 deterministic stages pass: 104 component checks,
28 bounded-material and lining-support checks,
504 development pairs, 507 preserved
definitions (487 exact payloads and
20 strict material comparisons),
71 STEP comparisons and retained
5,316-component standard context.
A fresh build reproduces 1,585 archived BReps and
144,937 persistent properties. The one-millimeter
forward-foot variation follows the actual outer radius and rivet grips while
retaining printed stock, occurrence frames and qualified support/clearance checks.

- [Native component checks](independent_checks.json)
- [Bounded changes and whole lining support](material_checks.json)
- [Unchanged-definition preservation](definition_preservation_checks.json)
- [STEP checks](exchange_checks.json), [definitions](HighBrakeFrontDefinitions.step),
  [affected installation](HighBrakeFrontInstallation.step)
- [Standard context](standard_context_checks.json), [fresh reproduction](reproduction_checks.json),
  [parameter sensitivity](variation_checks.json)
- [Visual review](visual_review.json), [archive-bound publication](publication_checks.json)

Whole lining contact is qualified with explicit exceptions: the printed strip
projects 0.589643 mm beyond each drum edge (97.5238% axial overlap), and three recessed
steel heads interrupt backing contact locally per band. The remainder of the
complete cylindrical faces is covered. Displaced backing/drum negatives fail.

## Source comparison and retained diagnostics

[Isometric](isometric.png), [fitting detail](high_brake_detail.png),
[fixed HB133 overlay](high_brake_source.png) and
[case-clearance section](high_brake_case_clearance.png) were directly inspected.
No source camera was refitted. Upper and lower free-pin residuals are approximately
(+0.44,-0.46) and (-4.56,+2.08) pixels. The inherited rear-anchor residual remains
(+9.16,+2.50). Printed lining radius supplies the scale; these are illustration
comparisons with local depth conventions, not independent dimensional validation.

The [diagnostics](diagnostics/README.md) retain failed fitting/backing intersections,
rivet/case clashes, a misleading curved-face trim, the initial support-mask error
and a missing pipeline dependency path. The actual definitions were repaired or
the measurement diagnosed; acceptance tolerances were retained.

## Remaining work and limits

Unprinted fork depth, free-end profiles, rivet head forms, stock-length datum,
M361 extension and rear bridge relief remain documented approximations. SNL's
continuous MX109/M364 lining composition differs from the handbook's six-M364
arrangement. Source lining-end profiles and reserved fork interfaces must be
revisited against the completed mechanism if evidence warrants it.

M356 pins/cotters, M355A/B paired levers with four joining rivets per lever,
adjustment, M362/M363 anchor supports and high-speed stops remain. Complete controls,
frame/hull joints, engine/interior population, inventory reconciliation and standard
integration follow. Full removal paths and structural strength are not qualified.

The repeatable pipeline is `tools/cad_pipeline/plans/high_brake_front_development.json`.
Run/status/verify use ID `high_brake_front01`. All builders use the existing headless
FreeCAD launcher; no GUI fitAll or source-image warp is used.
