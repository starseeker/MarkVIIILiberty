# Spring/tube source-conflict assessment

Decision: **needs_source_review**. The draft memo is unsupported; historical dimensions are not proven. No final CAD is created, as requested by the packet.

Both full supplied images were inspected with image tools. In `HB140-141.jpg`, printed page 141 (right side), under “LOWER ROAD-TRACK ROLLERS WITH SPRING PLATES,” the handbook states: “Between these plates are the road-track-roller springs, 1 inch in diameter, having three coils 6.652 inches long under a load of 2,500 pounds. The spring has an outside diameter of 3.937 inches.” The later tube sentence gives “3.812 inches outside diameter” and “2.75 inches inside diameter.” The source is identified by the evidence packet as *Preliminary Handbook of the Mark VIII Tank*, 6 March 1925. The assessment's source_wording joins these two relevant passages, omitting intervening text and normalizing line breaks.

The complete `HB-plate138.png` section shows spring **M1336** surrounding tube **M1333**, between plates M1334, with rollers M1332. Those source marks are retained verbatim. The left page of the spread includes the adjusting wheel and top road-track roller; its top-roller legend is not a substitute identification for the spring assembly. The section supports the surrounding relationship, but supplies no dimensioned spring diameter or wire-section proof. No dimensions were obtained by pixel scaling.

For this calculation only, the printed “1 inch in diameter” is assumed to mean circular wire diameter, d = 25.4 mm. This is stipulated by the evidence packet, not independently established by the illustration. Use exactly 25.4 mm/in and ideal concentric circular envelopes; radial clearance c = (spring ID − tube OD)/2. These are nominal arithmetic results, not measured precision or tolerance limits.

| Quantity | Literal printed OD reading | Alternative ID reconstruction |
|---|---:|---:|
| Spring ID | (3.937 − 2 × 1) × 25.4 = 49.1998 mm | 3.937 × 25.4 = 99.9998 mm |
| Spring OD | 3.937 × 25.4 = 99.9998 mm | (3.937 + 2 × 1) × 25.4 = 150.7998 mm |
| Tube OD | 3.812 × 25.4 = 96.8248 mm | 96.8248 mm |
| Radial clearance | −23.8125 mm | +1.5875 mm |

Thus the literal reading cannot fit around the tube under the stipulated wire assumption: diametral interference is 47.625 mm. Reading 3.937 inches as spring ID gives 3.175 mm diametral clearance. That ID reading is **inferred**, not printed or confirmed. It would require correction of the source wording, for which no authority is supplied. Positive nominal clearance alone cannot establish historical identity, correct dimensions, operating fit, or which printed value/interpretation is wrong. The memo's proposed source-table change and “historically exact” label are rejected.

Missing evidence includes an erratum or authoritative dimensioned drawing linked to M1336 and M1333, verified wire section and diameter, or reliable measurements of a surviving assembly with provenance. Useful follow-up would compare other handbook editions and parts drawings, then measure spring ID/OD and wire section and the mating tube, recording load state and tolerances. The printed 6.652-inch length is explicitly under 2,500 pounds; it is not evidence for a free length or a complete spring model. No pitch, end treatment, deformation, eccentricity, or service clearance allowance is inferred. No tolerances or reviewed datums are supplied; the packet marks dimensions, interfaces, and sources unreviewed, and those statuses remain unchanged.

Reproduce from the workspace root:

```sh
python3 freecad_python.py deliverables/build_assessment.py
```

The builder writes `assessment.json` and `checks.json`, verifies all three declared input SHA-256 hashes, checks decimal arithmetic against explicit expected values, and cross-checks unit conversion with installed FreeCAD. It creates no CAD document or geometry. `checks.json` records the actual run; these checks do not replace the subsequent independent source, visual, and acceptance review. Inputs and the FreeCAD launcher are unchanged.
