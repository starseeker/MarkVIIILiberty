# I03 — outer clutch drum and engine flywheel

Status: accepted approximate for continued development, 23 September 2026.
Parent is the qualified 1,653-component plunger-retention
checkpoint `5023f3c`. Configuration remains the Rock Island first 100, in the
standard assembled position.

This packet adds SH866A drum, SH868A flywheel, six SH866B cap screws sharing one
definition, and one SH866C locking wire. It reroutes the existing SH861K plunger
wire to clear the flywheel, preserving the other 1,652 parent occurrences. The
isolated transmission/pump candidate contains 1,662 physical components. This
local count is not additive to the standard tank inventory.

## Evidence and selected interpretation

Full HB Plates 71 and 111, SNL Plate 21, the original handbook specification and
starter pages, and the relevant SNL inventory pages were inspected. The source
dossier retains the exact survey records and original-image hashes.

| Feature | Evidence | Selected reconstruction and limits |
| --- | --- | --- |
| Outer drum | SNL83:034, SH866A, one, Plate21 callout2 | Revolved carbon-steel drum mating to the qualified cone lining in the engaged position. Normal stock 6mm, bend 25mm and flange profile are estimates. |
| Drum screws | SNL201:002, six SH866B, 5/8×1¼in, threaded 1in, drilled hex head | Diameter 15.875, underhead 31.75 and nominal threaded length 25.4mm. Estimated head, 188mm pitch radius, 3mm drill and smooth thread envelopes. |
| Drum locking wire | SNL276:004, SH866C, 48in soft steel, W.&M.No16 | One 1,219.2mm centerline through all six heads. Diameter 1.5mm and route are estimates, not a verified gauge conversion. |
| Flywheel | SNL95:015, SH868A, one; HB115 largest diameter 19.811in | Largest diameter 503.1994mm. The uncalibrated SNL dashed outline is proportionally larger; the printed dimension is selected conditionally. |
| Starter teeth | HB162–165 describes engagement with the flywheel teeth | 124 teeth with estimated 20° involute form. No historical tooth-count, tooth-strength or starter-mesh qualification. HB165's 3/8in disengaged edge gap is reserved for starter installation. |
| Long hub and positive drive | HB71/111 section, tapered/keyed mounting and removal geometry | The positive-drive splines are placed on the removable flywheel hub extension. HB prose calls them crankshaft teeth. This mechanically plausible interpretation remains uncertain. |
| Taper and keyway | Source section and crankshaft/key inventory | Through taper and keyway permit later shaft/key insertion. Both taper endpoints and keyway dimensions are estimates. The front radius 33.3375mm is inferred from the nominal 2.625in shaft journal, not a printed bore dimension. |
| Flywheel callout conflict | SNL95 says callout 16 Plate21 | The actual SNL21 leader 16 identifies stop drum 870/M858; HB71 callout 16 identifies the flywheel. Keep the identities separate. |
| Key screw conflict | SNL203:019 and212 specify one No10 (3/16)-24×3/4in flathead screw; HB201 specifies two SH64JH | Select the SNL count for future key installation, retain the handbook alternative. Neither key nor screw is added prematurely. |

The aeroplane propeller hub in HB61 is not the tank flywheel. Engine sections
HB40/SNL14 omit the tank flywheel and cannot establish its finished mounting
dimensions. A separate starter ring is not counted: the inventory identifies one
flywheel and does not establish a separate ring component.

## Geometry and ownership

Units are millimeters. The inherited TransmissionCore frame remains unchanged;
local X points toward the engine. `ClutchOuterDrumAssembly` belongs to Drivetrain.
`EngineFlywheelAssembly` belongs to Powerplant and shares the established shaft
axis. Definitions remain hidden, and repeated screws are native links.

The qualified lining controls the drum friction face. Its 25mm internal bend
turns into the annular mounting flange at X1038.575; the 6mm flange ends at
X1044.575. The flywheel's rear mounting face supports the complete flange from
radius 168mm outward. The 32mm rim places its front at X1076.575. Each screw enters
the flywheel 25.75mm: 25.4mm of nominal thread plus 0.35mm of plain shank. The blind
hole has 1mm tip clearance and 5.25mm remaining axial stock.

The flywheel hub extends from X843.2 to its dished web. Its 24 positive splines
engage the inherited sleeve; the bearing journal has 0.15mm radial allowance.
The hub, dish and toothed rim form one solid. The starter tooth flanks use cubic
B-splines fitted to the chosen involute, with a held-out fitting residual below
0.001mm; this numerical accuracy does not improve the historical certainty of
the selected tooth form.

The earlier 30in SH861K wire projected axially into the new dished flywheel by
58.239mm³. Its paired ends now turn radially inward in the head plane. The six
head passages and source length remain unchanged. The new 48in wire uses the
same inward-tail construction at the drum screws. These are two separate
continuous solids; orange in review views is a highlight, not a material claim.

The full crankshaft, shaft key and screw, SH136A nut and retention, engine thrust
bearing, starter installation and clutch-stop brake remain required. No short
shaft placeholder is counted as a completed crankshaft.

The native section shows a steeper hub-to-rim flare than the handbook sketch.
This provisional dish clears the inherited bearing and plunger geometry; it is
not a recovered manufacturing profile. The complete engine/crankshaft installation
must revisit that discrepancy along with the uncertain spline ownership.

## Validation and artifacts

The nominal native file reopens with 1,662 physical occurrences. All 262 affected
interference pairs and 270 independent geometry checks pass. Checks inspect
friction contact, full flange support, actual tooth tips and spaces, taper and
keyway material, journal clearance, spline drive-face engagement, all drilled
heads, the full blind-hole bottoms, both wire lengths and material volumes.
The old axial wire is retained as a negative clearance witness.

The first fit candidate exposed unsupported flange material and minute contact
between screw-head corners and the drum bend. The receiving flywheel face was
extended, the rim transition revised to preserve blind-hole floors, and the
heads clocked 30°. These changes retain the printed fastener dimensions. Failed
reports and input geometry scripts are retained under `diagnostics/first_fit/`.

Five definition and ten installed STEP solids pass explicit-accuracy mass,
centroid and two-way material comparisons. Two saved parameter trials vary drum
stock (5.5/6.5mm), bend radius (24/26mm) and tooth count (122/126). Each passes
68 checks and 262 interference pairs. A fresh build repeats the nominal 270
checks, 262 pairs and 15 STEP comparisons with identical inputs and datums.

Six native/source images were inspected. Four new progression images preserve
the installed isometric, axial section, flywheel detail and exposed wire routes;
all 95 earlier images are unchanged. The noted profile/source discrepancies remain
explicit limits of this acceptance. Controls require builder regeneration; the
native metadata is not a live parametric expression system.

- [Native candidate](../experiments/drive_chains/clutch_drum_build/TransmissionWithClutchDrum.FCStd)
- [Qualification](../experiments/drive_chains/clutch_drum_build/qualification.json)
- [Source dossier](../experiments/drive_chains/clutch_drum_sources.json)
- [Native/source views](../experiments/drive_chains/clutch_drum_build/source_review/index.html)
- [Independent checks](../experiments/drive_chains/clutch_drum_build/independent_checks.json)

Rebuild from the repository root:

```sh
python3 cad/003_FullTank/experiments/drive_chains/clutch_drum_build.py
python3 cad/003_FullTank/experiments/drive_chains/check_clutch_drum_interfaces.py
python3 cad/003_FullTank/experiments/drive_chains/check_clutch_drum_exchange.py
python3 cad/003_FullTank/experiments/drive_chains/check_clutch_drum_variants.py
python3 cad/003_FullTank/experiments/drive_chains/render_clutch_drum_review.py
```

Qualification additionally requires recorded source/visual review, the fresh
build and its checks, and preserved snapshots bound to the actual artifacts.

Standard tank011, its 20 native files and transparent-hull view remain unchanged.
Complete engine/drivetrain geometry, air circuits, remaining interiors, integration,
coverage reconciliation and later selected poses remain part of the full goal.
