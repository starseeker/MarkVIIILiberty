# Rear high-speed brake joints

[PowertrainWithHighBrakeJoints.FCStd](PowertrainWithHighBrakeJoints.FCStd) contains
**3,039 physical occurrences, 511 definitions and 306 assemblies**.
Both high-speed brakes now include an M361 anchor end, six steel countersunk
rivets and six coupling screws. M367 owns the component assemblies and adds no
solid. The printed long/short lining dimensions remain unchanged.

The [qualification](qualification.json) records all 14 deterministic stages:
406 saved-model checks, 240 development pairs,
504 inherited definitions preserved (486 exact BReps,
18 strict material comparisons), 41 STEP comparisons,
retained standard context, exact fresh reproduction and a 1 mm anchor-stock
variation. The actual screw length and rivet grip follow the variation; printed
lining stock and inherited material stay fixed. Named-component STEP files cover
the seven definitions and 34 added occurrences.

The stepped anchor section, reinforced long-band terminal, eye profile, head
forms and screw lengths remain estimates. Threads use nominal solid envelopes.
The source lining variant is explicit: SNL long/short continuous strips differ
from the handbook's six-segment nomenclature. Forward fittings, lining fasteners,
external anchor supports, levers, adjustment and stops remain unfinished; full
lining support and the completed mechanism require further checks. Standard
tank011 is unchanged. This is a local static development checkpoint.

The [isometric](isometric.png), [joint detail](high_brake_detail.png) and
[source overlay](high_brake_source.png) were inspected and saved in the visual
progression: 204 images, with all 201 earlier images preserved. Detail clipping
changes display only. The HB133 planar registration remains fixed; the anchor-eye
residual is approximately +9.16, +2.50 pixels. This illustration is not a calibrated
photographic camera, and its printed-radius scale cannot independently validate
the model radius. See [visual review](visual_review.json).

[Diagnostics](diagnostics/README.md) retain the rejected Boolean construction and
initial mass-integration failure. The corrected cutter parameterization preserves
its circular geometry. Verified section integration measures the unchanged
anchor for STEP comparison; material and tolerance criteria remain unchanged.

The pipeline is `tools/cad_pipeline/plans/high_brake_joint_development.json`, run
`high_brake_joints01`. [Publication checks](publication_checks.json) bind all
published definitions to the saved native archive. The receipt-bound original
manifest is retained separately; only BRep paths change during publication.
The native SHA-256 is `d6a48759522cde42e0444f810f892a56120d068aac59d4343a49ebd0212e95a2`.
