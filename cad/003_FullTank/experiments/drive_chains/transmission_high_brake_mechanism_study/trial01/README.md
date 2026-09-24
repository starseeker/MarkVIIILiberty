# High-speed operating mechanism checkpoint — 24 September 2026

[Native FreeCAD assembly](PowertrainWithHighBrakeMechanism.FCStd): **3,121 physical
occurrences, 529 shared definitions and 322 assembly groups**. This is a locally
qualified development checkpoint; the complete tank and high-speed brake system
remain unfinished. Standard tank011 is unchanged.

The new geometry comprises four M355A/B lever members, eight source-sized joining
rivets, four M356 free-end pins, four estimated cotters, and two screw/nut/spring
assemblies with four source-bore washers. Curved lever profiles retain cubic
B-spline boundaries; cylinders, planes and rounded eyes remain analytic.
The [packet](../README.md) records source interpretation and unprinted dimensions.

All 15 stages pass: 61 saved component/interface checks,
98 development neighbor comparisons, 519
preserved definitions (491 exact BRep payloads and
28 strict material comparisons),
40 STEP round-trip comparisons and retained
5,316-component standard context. A fresh build
reproduces 1,619 archive BReps and
147,101 persistent properties. A 1 mm installed
spring-height change moves its upper washer and receiving lever seat while
retaining printed stock and attachment frames. This is regeneration sensitivity,
not simulation of spring compression or operating motion.

- [Qualification](qualification.json), [component checks](independent_checks.json)
- [Preservation](definition_preservation_checks.json), [STEP checks](exchange_checks.json)
- [STEP definitions](HighBrakeMechanismDefinitions.step), [STEP installation](HighBrakeMechanismInstallation.step)
- [Standard context](standard_context_checks.json), [reproduction](reproduction_checks.json)
- [Parameter sensitivity](variation_checks.json), [publication verification](publication_checks.json)
- [Isometric](isometric.png), [mechanism detail](high_brake_mechanism_detail.png),
  [fixed HB133 overlay](high_brake_mechanism_source.png), [visual review](visual_review.json)

The source registration is unchanged. New joining-rivet and rod-eye diagnostic
residuals are small; the screw-tip discrepancy is approximately 4.11 pixels.
These are not independent validation because the same illustration helped set
estimated profiles. SNL Plate30 repeats the handbook view and supplies no new
transverse section. Hidden lever saddle, member width, fastener head forms and
spring dimensions remain explicitly conditional.

Three reviewed images were added to the progression, preserving all 208 earlier
images. The [retained diagnostics](diagnostics/README.md) explain the pin envelope,
cotter frame and screw-saddle construction revisions. No source camera was refitted.

Next populate M362/M363 anchor supports and high-speed stops, then control rods
and remaining frame/hull interfaces. Continue engine and interior population,
inventory reconciliation and full standard integration before poses. Complete
removal paths, manufactured profile accuracy and load strength are not qualified.
