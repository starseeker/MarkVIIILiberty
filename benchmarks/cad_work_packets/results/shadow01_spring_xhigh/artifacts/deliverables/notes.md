# Spring/tube source assessment

Decision: **needs_source_review**. The unreviewed draft memo is unsupported.
The literal dimensions cannot fit under the stipulated circular-wire assumption.
An alternative ID interpretation fits nominally, but historical dimensions are
not proven. No final CAD, geometry, drawing, or manufacturing release is produced.

## Source evidence and identity

Both full input images were opened and inspected with the image-viewing tool,
without cropping, rescaling for measurement, or altering the originals:

- [HB140-141.jpg](../inputs/HB140-141.jpg): the full spread has printed page 141
  on the right. Under “LOWER ROAD-TRACK ROLLERS WITH SPRING PLATES,” it reads:
  “Between these plates are the road-track-roller springs, 1 inch in diameter,
  having three coils 6.652 inches long under a load of 2,500 pounds. The spring
  has an outside diameter of 3.937 inches.” The tube paragraph reads:
  “The road-track-roller tube or sleeve is 21½ inches long, 3.812 inches outside
  diameter, and 2.75 inches inside diameter.” It also states that the tube carries
  the rollers, spring plates, and spring, which revolve as a unit with the tube.
  Line breaks are normalized in these transcriptions. The page 140 figures are
  the road-track adjusting wheel (Plate No. 87) and top road-track roller
  (Plate No. 88); neither is substituted for the lower-roller spring section.
- [HB-plate138.png](../inputs/HB-plate138.png): the complete extracted section
  shows **M1336** pointing to a coil section and **M1333** pointing to the tube
  surrounding the central pin. Coil sections lie outside the tube, between the
  plates labeled M1334. M1335 denotes the separate retaining spring ring, not
  the helical spring assessed here. The marks are preserved as drawn. The
  arrangement supports a spring surrounding this tube, but provides no readable
  dimension callout establishing 3.937 inches as an ID, no calibrated scale,
  and no tolerance or erratum. Apparent drawing clearance is qualitative only.
- [spring_evidence.md](../inputs/spring_evidence.md) attributes the sources to
  *Preliminary Handbook of the Mark VIII Tank*, 6 March 1925, identifies the
  section as a complete extraction, and explicitly makes the wire interpretation
  conditional. That attribution is supplied provenance; the extracted image has
  no visible title/date or caption independently authenticating it. Its filename
  is retained, not treated as proof of a printed plate number.

## Nominal calculation

Use exactly 25.4 mm/in. Assume the ambiguous “1 inch in diameter” means a
circular wire diameter d = 1.000 in = 25.4 mm, solely as the packet requests.
This is not independent proof of wire shape or size. For an ideal circular-wire
spring envelope about a common axis with the tube:

    spring ID = spring OD - 2d
    signed radial clearance = (spring ID - tube OD) / 2

Positive clearance means nominal radial space; negative clearance means radial
interference. These are envelope checks, not a full helical or assembly model.

| Quantity | Literal printed OD reading | Alternative ID reading |
| --- | ---: | ---: |
| Spring OD | 3.937 in = 99.9998 mm | 5.937 in = 150.7998 mm |
| Spring ID | 1.937 in = 49.1998 mm | 3.937 in = 99.9998 mm |
| Assumed wire diameter | 1.000 in = 25.4 mm | 1.000 in = 25.4 mm |
| Tube OD | 3.812 in = 96.8248 mm | 3.812 in = 96.8248 mm |
| Diametral clearance | -47.6250 mm | +3.1750 mm |
| Radial clearance | **-23.8125 mm** | **+1.5875 mm** |

The literal spring bore is smaller than the tube by 47.6250 mm in diameter.
It cannot surround the tube under these assumptions. The alternative reuses the
printed number 3.937 as an ID and adds twice the assumed wire diameter for its OD.
**The ID assignment and 5.937-inch OD are inferred, not printed dimensions.**
The 3.937-inch source value remains explicitly classified as printed OD in
assessment.json. No source table is corrected and no identity is changed.

The extra decimal places are exact conversion/arithmetic results for the supplied
nominal values, not evidence of manufacturing accuracy. No fit tolerance is
supplied, so the positive alternative clearance does not establish a tolerance
margin, operational suitability, or acceptance. The common-axis envelope is an
analytical assumption suggested by the section, not a newly reviewed datum.
No scan dimensions, pitch, end form, deformation, runout, spring stresses, or
dynamic behavior are inferred. The printed three-coil count, loaded length and
load are context only; no free-length or loaded-envelope reconstruction is made.

## Memo decision and missing evidence

The memo's claim that INSIDE diameter was confirmed contradicts the visible
“outside diameter” wording. Its request to relabel the spring historically exact
and remove all unresolved issues is unsupported. The schematic arrangement
motivates investigation, but cannot select which source dimension or interpretation
is wrong. Nominal geometric fit alone proves neither historical identity nor
historical dimensions. Accordingly memo_supported = false and
historical_dimensions_proven = false.

No erratum, original dimensioned manufacturing drawing, independently verified
wire section, measured surviving spring, or fit tolerances are supplied. Useful
follow-up evidence includes:

- An authenticated handbook erratum or corroborating edition explicitly resolving
  whether 3.937 inches denotes OD or ID.
- Dimensioned drawings and revision records tied specifically to M1336 and M1333,
  including wire section, OD/ID, tolerances, and free/loaded condition.
- Measurements of an authenticated surviving M1336 spring with a matched M1333
  tube, documenting provenance, condition, wire section, bore/envelope dimensions,
  and measurement uncertainty.

The packet's reviewed dimensions, interfaces, and sources flags all remain false.
Independent acceptance and source/visual review remain outstanding. This report
resolves the conditional arithmetic and rejects the memo; it does not resolve
the historical dimensional conflict by inventing an erratum.

## Reproduction and checks

From the workspace root, run:

    python3 freecad_python.py deliverables/build_assessment.py

The builder verifies every supplied evidence-file SHA-256 against packet.json,
uses decimal arithmetic, independently cross-checks the calculations with installed
FreeCAD's unit engine, verifies required field types and decision semantics, and
writes assessment.json, notes.md, and checks.json in deliverables/. It imports
FreeCAD only for unit checks; it creates no document or geometry. checks.json
records the actual check outcomes, FreeCAD version, and input/runner hashes.
The script checks all inputs and the read-only runner remain byte-identical during
the run. Reproduction does not automate or replace the manual image review above.
