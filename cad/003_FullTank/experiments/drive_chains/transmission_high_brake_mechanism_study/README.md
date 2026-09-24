# High-speed brake operating mechanism

This packet adds the two paired M355 lever assemblies, four M356 free-end pins
and their cotters, and two M357/M358/M369 spring adjustment assemblies to the
qualified forward-fitting parent. It adds 30 physical occurrences, ten shared
definitions and eight assembly groups. Anchor brackets/pins, stops and control
rods remain subsequent work; the complete standard tank is still unfinished.

The builder is [build_transmission_high_brake_mechanism.py](../build_transmission_high_brake_mechanism.py).
Inputs, literal catalogue rows and source hashes are in [sources.json](sources.json)
and [controls.json](controls.json). The inherited HB133 registration is retained
in [source_registration.json](source_registration.json). Its radius-based planar
scale is a diagnostic for an illustration with local depth conventions, not a
recovered photographic camera or independent confirmation of the lining radius.

## Evidence and interpretation

- SNL118 identifies two complete levers. **Each** contains M355A and M355B plus
  four 3/8 by 1-3/8 inch button-head rivets: four members and eight rivets total.
- SNL137 lists four M356 free-end pins. HB154 requires their cotters. The separate
  M363 anchor-pin cotter specification does not establish this cotter's stock.
- SNL253 and SNL274 give two MX78A washers with 11/16 inch bores and two MX78B
  washers with 13/16 inch bores. Outside diameters and thicknesses are estimated.
- HB151/154 connects the screw to the short band and the lever to the long band
  and control rod. The spring lies between the screw shoulder and lever. The
  larger washer is placed on the lower guide and the smaller washer below the
  lever; this assignment is an interpretation.
- SNL Plate30 (p302) repeats the HB100/HB133 illustration. These reproductions do
  not independently establish the hidden lever section.

The lever members occupy touching half-width sections. Retained cubic B-spline
curves describe the curved elbow; analytic eyes, bores and rounded lower ends
complete the profile. A rectangular integral screw saddle continues the two flat
member sections. Its hidden section is an estimate, as are pin stock, cotter
formation, spring dimensions/turn count, nut turning bar and screw shoulders.
Threads use cylindrical envelopes. Parameter changes regenerate the parts; these
are not claimed to be live FreeCAD expression dependencies.

## Retained development findings

The first installed probe detected pin-head interference with fitting feet wider
than the fork cheeks, and a cotter definition rotation that was overwritten by
occurrence placement. The corrected pins span the full fitting width. An identity
compound preserves the cotter's rotated analytic solid, and all definitions must
now have identity frames before installation.

A circular screw-bearing barrel trial raised the lever's kernel tolerance to
about 0.00394 mm at the intersection with its curved profile. Rotating the cylinder
seam did not resolve it. The source does not establish a circular barrel; the
rectangular saddle interpretation retains the flat paired sections and the same
receiving planes, with about 0.000005 mm maximum kernel tolerance. This changes an
estimated hidden section and is not an assertion that the original manufactured
section has been recovered. The rejected construction remains diagnostic evidence.

## Qualification scope

The development pipeline checks the saved assembly, source counts and printed
stock, actual pivot axes, rivet bearing, geometric pin retention, spring end
support, adjusting-screw passage, and new material against retained components.
Positive washer/shoulder and nut/lever bearing is measured; full-area contact of
every washer face, load capacity and operating motion are not inferred. Separate
gates cover inherited definition preservation, STEP, retained standard-tank
context, fresh reproduction and a coupled 1 mm spring-height variation.

New source picks remain diagnostic because the same illustration helped establish
the estimated profiles. A visually close outline does not establish the unseen
section. Review the overlay alongside static checks and preserve old comparisons
when revising this interpretation. Full service/removal paths and control-rod
connections remain open.

The [published checkpoint](trial01/README.md) binds all 15 completed development
stages and the visual review in [qualification.json](trial01/qualification.json).
Run/status/verify use `high_brake_mechanism02`. This qualification is local and
conditional; read `CURRENT_WORK.json` for the next work.
