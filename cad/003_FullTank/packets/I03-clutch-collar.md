# I03 — sliding collar joint and end-bearing pocket

Follow-up: the [main-clutch core checkpoint](I03-clutch-stack.md) populates the
formerly empty bore and revises SH999A to receive the bearing, sleeve, keys and
snap ring. This earlier collar-joint native remains preserved; use the later
checkpoint for continued construction. Cones and operating parts remain ahead.

Status: **checked approximate reconstruction; main clutch construction continues**, 21 September 2026.
[Native assembly](../experiments/drive_chains/clutch_collar_build/TransmissionWithClutchCollar.FCStd) ·
[source comparison](../experiments/drive_chains/clutch_collar_build/source_review/index.html).
The combined candidate adds ten physical pieces and corrects the coupling
arrangement around the cardan head. The main internal clutch stack, cones,
operating parts and standard tank integration remain unfinished.
The saved and reopened native contains **1,540 physical components**. Ten parent
components change shape or placement; the other 1,520 retain both. The
[qualification receipt](../experiments/drive_chains/clutch_collar_build/qualification.json)
binds the native, executed inputs, source assets, STEP files and reviewed images.

## Evidence changes the coupling topology

The previous front-clutch reconstruction followed the prominent handbook
flange and transferred dimensions. Closer inspection of SNL Plate21 shows two
distinct SH945A flanges: one seats the external spring and another joins the
sliding collar, with an end-bearing pocket between the cardan tip and collar.
The old single-flange arrangement could not receive that illustrated stack.

The new coupling follows the catalogue topology. The external spring and split
clamp move 67mm aft together; the spring flange now lies aft of the enlarged
cardan head. The existing M855 coupling box and cardan shaft remain unchanged.
The clamp begins 4mm beyond the box. This is an inferred placement following
the catalogue arrangement, not a measured original station.

HB71 and SNL21 retain their original opposite orientations in the comparison.
The old and new native centre sections are both shown, along with the actual
collar joint and locking wire. Panel scales are independent. The correction
addresses a structural discrepancy; it does not establish exact proportions.
The earlier native and progression images remain preserved.

## Inventory and ownership

| Selected item | Survey identity | Quantity | Source |
|---|---|---:|---|
| SH999A sliding collar | P_0e882cdb0b86c139 | 1 | SNL67:019, callout11 |
| SH997A end-bearing ring | P_416ecc582ff2838d | 1 | SNL164:030, callout15 |
| SH997B end-bearing bush | P_da05030d3ca399a1 | 1 | SNL43:014, callout14 |
| Drilled 3/8 × 5/8in cap screw | P_5422ef2dfc584d7d | 6 | SNL200:002, callout13 |
| SH999C locking wire | P_5bebbabd7d6534e3 | 1 | SNL276:003 |

All additions belong to Drivetrain/TransmissionCore/ClutchCollar. The six screws
reuse one definition. SH999C is one continuous physical wire, not six separate
segments or an extra assembly envelope. Original pages43,67,164,200 and276 were
inspected alongside the figure.

The handbook identifies different coupling, sliding-collar and bearing marks:
SH864B, SH862A/B and SH863A/B. Those identities are retained separately in the
[source dossier](../experiments/drive_chains/clutch_collar_sources.json).
The 9in coupling flange and 5in body dimensions remain provisional transfers
to catalogue SH945A. Missing variant membership is not universal applicability.

SNL200 explicitly allocates these six short screws to SH999A. They are separate
from the six larger drum-to-flywheel screws. The preceding SNL33 callout25
mismatch remains open; external spring-clamp hardware still follows the written
SH849A allocation.

## Geometry and interfaces

[clutch_collar_controls.json](../experiments/drive_chains/clutch_collar_controls.json)
distinguishes printed controls, dimensional transfers and estimates. X points
forward in the existing transmission frame.

| Interface | Selected construction | Limitation |
|---|---|---|
| Rear spring flange | X734.95–744.95, OD228.6mm | Axial station/stock inferred; diameter transferred |
| Forward coupling joint | X821.95–834.95, OD228.6mm | Distinct from spring flange; hidden contour inferred |
| SH999A lip | X834.95–841.30 | 6.35mm stock inferred |
| Six screws | Diameter9.525mm, underhead length15.875mm | Both dimensions printed in SNL200 |
| Blind receiving holes | 9.525mm axial engagement, 1mm tip clearance, 2.475mm back wall | Smooth thread envelopes; no strength/preload qualification |
| End-bearing pocket | Starts X788.15, radius59.65mm | Inferred size; cardan tip retains0.2mm axial clearance |
| End ring and bush | Separate annular components, 0.1mm radial running gap | Profiles, stock and actual bearing fit unverified |
| Ring retention | Coupling shoulder, bush shoulder and collar face capture the ring/bush stack | Eventual crankshaft and nut fit remains pending |
| Locking wire | 660.4mm centreline through six drilled heads with paired twisted ends | Printed26in length; formed route and twist count inferred |

The catalogue specifies soft steel, W.&M. gauge16 for the wire. Its selected
1.5mm diameter is an explicit geometric approximation, **not** a verified gauge
conversion. The centreline length is solved while retaining the screw circle
and head bores. A single solid is swept over eight NURBS spans; the endpoints
remain separate at the paired twist. No locking-strength qualification is made.

The hollow collar remains partial. Its main bearing, positive sleeve, four
keys, outer cone-support collar, thrust/ball stack and related retention must
be reconstructed as connected components. In particular, the handbook sleeve
and bearing dimensions must not be assigned to catalogue parts without checking
their different identities and concentric arrangement. Vacant bore space is
not counted as a physical component.

## Reproduction and validation

Run each command successfully before the next:

```sh
python3 cad/003_FullTank/experiments/drive_chains/clutch_collar_sources.py
python3 cad/003_FullTank/experiments/drive_chains/clutch_collar_build.py
python3 cad/003_FullTank/experiments/drive_chains/check_clutch_collar.py
python3 cad/003_FullTank/experiments/drive_chains/check_clutch_collar_variants.py
python3 cad/003_FullTank/experiments/drive_chains/render_clutch_collar_review.py
python3 cad/003_FullTank/experiments/drive_chains/qualify_clutch_collar.py
```

The qualifier requires visual inspection of the exact images. A changed model
needs a fresh visual-review receipt. The native contains the combined assembly;
the installation STEP contains only20 affected placed solids, and the local
definition STEP contains8 definitions.

Checks cover source inventory, ownership, the shifted external spring and
clamp seats, separate coupling flanges, spline clearance, ring/bush capture,
actual screw seating, blind-hole bottoms, wire routing through every head,
wire length and deliberate displacement interference. Two coherent axial,
lip-stock and collar-radius trials retain the printed screw and wire lengths.
They sample uncertainty; they do not prove exhaustive tolerance or load behavior.

All 104 independent checks, 65 local material-interference pairs, 8 definition
STEP comparisons and 20 placed-solid exchange checks pass. Both size trials
pass 65 material pairs and 16 intended contacts each. Seven exact raster images
were inspected, including the source comparison and preserved prior section.
All 20 standard native files and the 72 previously committed progression images
were verified unchanged. Four new snapshots preserve the
[installed isometric](../../intermediate_snapshot_iso_clutch_collar_001.png),
[isolated mechanism](../../intermediate_snapshot_iso_clutch_collar_mechanism_001.png),
[axial section](../../intermediate_snapshot_detail_clutch_collar_001.png) and
[locking wire](../../intermediate_snapshot_detail_clutch_collar_wire_001.png).

The first assembly's export failed because it accessed a definition from the
closed FreeCAD document. That run and its executed inputs are preserved in
`.work/main-clutch/initial_export_lifetime_error`. The builder now takes its
definition names from the reopened document.

Main internal clutch construction, cones/drum, clutch-stop band, pump air
connections, separate bearing supports, lubrication, brakes, long controls and
standard integration remain ahead. Standard tank011 and its opaque/transparent
views remain the current integrated tank checkpoint.
