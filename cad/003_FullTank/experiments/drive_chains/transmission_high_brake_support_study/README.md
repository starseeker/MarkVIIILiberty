# High-speed brake supports and stops — evidence and receiving-context study

The next geometry packet comprises two M362 anchor brackets, two M363 retained
pins, two M365 clips, two each of M366/M398/M399 stops, six M400 stop screws,
and their attachment hardware. The locally qualified parent remains the
[operating-mechanism checkpoint](../transmission_high_brake_mechanism_study/trial01/README.md):
3,121 physical occurrences, 529 shared definitions and 322 assemblies. This
study has not added physical geometry or qualified the supports.

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

## Next construction and qualification

1. Establish upper/lower receiving planes and bolt axes against the actual case
   and frame. Test an explicit integral-case-web hypothesis; record any bounded
   case revision and preserve all existing bearing and hardware interfaces.
2. Build the M362 fork around the retained M361 eye, then M363 and its source-sized
   cotter. Check both pin retention and the stated removal direction.
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

The [report](context01/report.json) binds the completed probe, runtime and images.
The qualified native and standard tank011 remain unchanged; there is no new
progression image for this evidence-only stage. The complete tank goal is active.
