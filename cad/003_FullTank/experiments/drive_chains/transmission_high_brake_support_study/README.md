# High-speed brake supports and stops — receiving-web reconstruction

The next geometry packet comprises two M362 anchor brackets, two M363 retained
pins, two M365 clips, two each of M366/M398/M399 stops, six M400 stop screws,
and their attachment hardware. The locally qualified parent remains the
[operating-mechanism checkpoint](../transmission_high_brake_mechanism_study/trial01/README.md):
3,121 physical occurrences, 529 shared definitions and 322 assemblies. The new
[integrated candidate](integrated01/PowertrainWithHighBrakeReceivers.FCStd) has
**3,129 occurrences /532 definitions /324 assemblies**: revised case receiving
webs, two M362 brackets, two shared locking plates and four lower MX60 screws.
It is a development candidate; the complete support/stop packet is unfinished.

## Reviewed evidence

[sources.json](sources.json) retains literal survey rows, source hashes, handbook
service text and the original images inspected on 24 September 2026. HB133 is
the primary visible arrangement; HB100 and SNL Plate30 repeat that illustration.
HB79 is a separate exterior photograph and HB123 a separate transmission section.
Neither has been used here to claim recovered hidden bracket dimensions.

HB154's removal sequence establishes that the bottom stop fastens to the anchor
bracket, the top and back stops can be removed after undoing the top-stop tap
bolts, and the anchor bracket fastens to the epicyclic frame. M363 must have a
cotter and a drift-accessible pin. These are interface requirements for the next
builder; the complete removal path remains unverified.

| Item | Vehicle quantity / dimensional evidence | Interpretation limit |
|---|---|---|
| M362 bracket | 2, SNL41:027 | Section, mounting depth and bolt pitch unprinted. |
| M363 pin assembly | 2, SNL137:001–004 | Count the physical pin and its cotter; the assembly is not another leaf. |
| Anchor cotter | 3/16 × 2 inches, SNL137:004 | Formed shape and length datum still need review. |
| M365 clip | 2, SNL66:022 | Hidden retention and stock unprinted. |
| M366 / M398 / M399 | 2 of each, SNL223:003–005 | Source silhouette supports arrangement; hidden section remains inferred. |
| M400 screw / nut | 6 assemblies, SNL205:020–023; nut nominal 3/8 inch | Nominal screw diameter follows its mate; length and manufactured thread/head form remain estimates. |
| MX60 | Catalogue total 10; four visible per illustrated brake | Eight provisionally allocated to these two brakes; remaining two unresolved. A 5/8-inch lock-washer application supports nominal size. |
| MX76 | Catalogue total 4; two visible per bottom-stop mounting | Nominal 1/2-inch size follows the washer application spanning SNL270–271. |

HB133 labels common locking plates MX61 and MX77. SNL271 instead explicitly
lists individual lock washers for MX60 and MX76. Preserve the handbook's visible
plate arrangement as the first reconstruction hypothesis and record the later
washer configuration as an alternative. The screw size inference does not prove
the configurations identical. Do not combine both retention arrangements merely
to reconcile the documents. Exact survey identities for MX61/MX77 and the HB133
nut mark MX23 have not been found; the SNL 3/8-inch nut has its own valid identity.

[inventory_audit.json](inventory_audit.json) checks the saved native definition
metadata and installed leaves. None of the marked support/stop definitions is
already installed. Two existing definitions share the catalogue identity for
the 3/16 × 2-inch cotter (seven occurrences); review their stock convention and
installed envelope before choosing reuse. Two existing half-inch lock-washer
definitions are also identified. Identity matches alone do not qualify geometry
for these joints. Unmarked generic hardware may escape this audit.

## Reused source registration and geometry finding

[source_registration.json](source_registration.json) preserves the previous
HB133 image hash, center, scale and picks. This is a planar diagnostic for an
illustration with local depth conventions; it is not a recovered photographic
camera. New support geometry does not justify adjusting it. The separate
[camera workflow](../../../../../tools/source_camera/README.md) documents
cached fitting, current holdout checks, targeted review and reasoned refits.
Its eight numerical/cache/raster controls passed again in this session.

The read-only [probe](../probe_transmission_high_brake_support.py) independently
checks selected archive BReps and composed placements against the parent FCStd.
It produces actual M263 case sections at the brake midplane (Y = 222.25 mm) and
retained bearing midplane (Y = 279.205714 mm), shown separately in the
[fixed-registration comparison](context01/case_sections_source.png). Neither
depth is asserted to be the drawing's hidden section plane. The
[spatial context](context01/support_context.png) exposes the retained case and
brake arrangement; omitted components are deliberate display selection.

At both inspected depths the retained M263 has the rear bearing support but
lacks material around the illustrated upper and lower support-foot regions.
Approximate diagnostic points there lie 88–157 mm from the nearest case surface.
These are not bolt picks, bearing-area measurements or demonstrated fit errors;
they establish that a bracket cannot simply be drilled into the present case
at those assumed locations. The previously modeled case webs at a different
transverse station do not resolve the connection automatically.

The saved M361 eye fixes the new anchor-pin center at brake-local
(-76.270492, 0, -209.551454) mm. Preserve that frame and the retained drum,
lining and mechanism interfaces while testing the support architecture.
The case's integral side web, its connection to the epicyclic mounting frame,
and the bracket's transverse reach need an explicit geometry hypothesis.
Use the service instructions, exterior photograph and sectional evidence to
constrain it. A camera refit would not supply missing receiving material.

## Receiving geometry and completed checks

[controls.json](controls.json) records the explicit integral-case-web hypothesis.
Four inclined feet, four thin diagonal ribs and four transverse ties connect
the illustrated upper/lower seats to the retained case and frame. All old case
material is preserved; additions stay within declared receiving-stock envelopes.
Eight blind mounting holes have measured back stock. Outer ties start beyond
the existing bearing-cap stud envelopes, whose clearance is checked separately.
Top and bottom geometry uses the actual asymmetric frame heights.

M362 is a fork around the retained M361 anchor eye. The nominal 5/8-inch MX60
shanks, bracket/plate stack and blind-hole depth are coupled. The common MX61
strip has two formed locking tabs against head flats. Its stock and bend form,
bracket hidden section, web thicknesses and bolt pitch are estimates. Upper
receiving holes intentionally await the stop assembly. The new parts use shared
definitions and separate port/starboard assembly groups; MX61 has no invented
catalogue identifier.

The inspected [isometric](receivers04/receiver_isometric.png) shows the support
architecture with selected retained neighbors in outline. The inspected
[HB133 overlay](receivers04/receiver_source.png) shows case sections at the same
two transverse stations as the evidence probe and the new bracket/hardware.
The latest ribs attach nearer the illustrated bearing-cap junction than the
earlier receivers03 trial. Source registration is unchanged. Residuals at the
frame, case silhouette and bracket stock remain visible; this mixed section
illustration does not establish exact hidden depths or a photographic camera.

| Saved evidence | Result and scope |
|---|---|
| [receivers04/report.json](receivers04/report.json) | 22 checks pass, including 226 nearby development pairs, bounded case additions, retained anchor axis and positive bearing interfaces with displaced negatives. |
| [receiver_interface_checks.json](receivers04/receiver_interface_checks.json) | 28 checks pass: four new frame contacts, four displaced negatives, eight blind passages, eight back-stock witnesses and four inherited stud clearances. |
| [exchange_refined02](receivers04/exchange_refined02/exchange_checks.json) | 13 strict comparisons pass for four definitions and nine installed shapes. Case mass uses qualified tighter quadrature after a recorded convergence failure; material and tolerance limits are unchanged. |
| [variation02](variation02/report.json) | A 1 mm increase in bracket stock moves the plate/heads and updates blind-hole depth; 22 prototype and 28 saved-interface checks pass. This variation has not yet had its own STEP gate. |
| [integrated01](integrated01/independent_checks.json) | 18 saved integration checks pass: counts, hierarchy, retained frames and strict material/placement transfer from the tested prototype. |
| [definition preservation](integrated01/definition_preservation_checks.json) | All 528 unchanged inherited definitions pass: 502 exact BReps and 26 strict material comparisons. The first worker was interrupted; the completed resume retains hash-bound results. |
| [standard context](integrated01/standard_context_checks.json) | All nine affected occurrences checked against 5,316 retained tank occurrences; the one nearby material pair passes. Replaced stand-ins are explicitly excluded. |
| [fresh reproduction](integrated01/reproduction_checks.json) | All six comparisons pass, including all 1,628 archive BReps and 147,688 persistent object properties. |

The [development checkpoint](integrated01/development_checkpoint.json) binds
these scoped results. They do not establish historical accuracy, structural
strength or a complete service path. Full packet qualification and promotion remain pending.
Standard tank011 and the qualified operating-mechanism parent remain unchanged.

Retained failed trials explain the geometry changes: receivers01 had bracket-tail
interference with the seat; receivers02 had mounting holes that stopped inside
the locking plate. Both were corrected before receivers03 passed. Receivers04
improves the source silhouette and is the current geometry. Its initial STEP
failure concerned numerical mass convergence, not material preservation; see
the [measurement diagnostic](receivers04/diagnostics/README.md).

## Next construction and qualification

1. Retain the reviewed receiver/bracket candidate and its fixed source registration;
   finish the separate preservation and full-packet gates before promotion.
2. Add M363 and its source-sized cotter around the retained M361/M362 joint.
   Check stock convention, pin retention and the stated removal direction.
3. Add the M366 bottom stop and paired MX76 attachment, then top/back stops,
   M365 clip and three M400/nut pairs per brake. Keep screw adjustment clearance
   distinct from numerical Boolean tolerance.
4. Bind counts to physical identities and keep assembly identities separate.
   Reconcile eight provisional MX60 occurrences with the catalogue total ten.
5. Verify saved native material, pin/bore axes, positive support area, receiving
   stock and new/retained interference. Preserve unchanged definitions and frames;
   qualify any bounded case changes independently.
6. Check STEP exchange, fresh reproduction, a useful coupled parameter change,
   retained standard-tank context and fixed-source visual comparisons. Publish
   progression snapshots when the geometry produces a significant improvement.

Run the read-only probe with a fresh absolute output path:

```sh
python3 skills/freecad-reconstruction/scripts/freecad_headless.py --workdir .work/high-brake-support/runtime cad/003_FullTank/experiments/drive_chains/probe_transmission_high_brake_support.py --output /absolute/new-context-directory
```

The [report](context01/report.json) retains the original evidence-only probe.
The new prototype images are published separately as development progression
views. The complete tank goal is active.
