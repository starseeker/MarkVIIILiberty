# Preliminary high-speed brake bands

[PowertrainWithHighBrakeBands.FCStd](PowertrainWithHighBrakeBands.FCStd) contains
**3,013 physical occurrences, 508 definitions and 302 assemblies**. Eight new
leaves represent the two long and two short lining strips and their separate
steel backing blanks. Existing machinery and standard tank011 remain unchanged.

All **344 preliminary native checks and 106 development pairs pass**. These
cover actual stock dimensions, flat lengths, hole count/voids, countersink angle
and direction, hierarchy, retained occurrence frames, contact distance and axial
overlap. The centered lining has 97.52% axial overlap with its image-derived drum
face, with approximately 0.59 mm overhang on each edge.

This is a partial development model. End ears, anchors, lever members, adjustment
mechanisms, stops and hardware are absent. Full material preservation, exact face
coverage, STEP, fresh reproduction and parameter qualification remain pending;
[qualification.json](qualification.json) makes these limits explicit. The latest
locally qualified predecessor remains the brake-spacer checkpoint.

The source review selects SNL119 continuous long MX109 plus short M364 linings;
HB's six-M364 variant remains a documented difference. Steel thickness, clocking,
neutral bend datum and the repeated long-hole pattern are estimates. Initial
3/16-inch steel collided with the rear case wall. The retained current estimate
is 3/32 inch, with no case/drum alteration or axial shift. See the
[source and diagnosis record](../README.md).

The four-stage deterministic run `high_brake_bands01` passes. Its corrected
countersink checker reused the unchanged build/extraction and reran only checks
and rendering; read-only freshness verification passed. The initial positive-angle
expectation failed for OCCT's negative half-angle convention. The corrected check
also verifies opening direction; geometry and angular tolerances were unchanged.

[Publication](publication.json) binds all saved definition BReps to the native
archive and preserves manifest semantics while relocating paths. This transport
check is separate from pending parent-to-candidate material preservation.

The [isometric](isometric.png) and [detail](high_brake_detail.png) were inspected and
copied into the progression. All 199 prior images are preserved: **201 total**.
The native SHA256 is `7229b22d53e9dabf9e44615ace9a0a52058138e26348cdb32666cc80b66bf103`.
