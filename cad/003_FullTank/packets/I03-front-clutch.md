# I03 — front coupling, split spring flange and external spring

Status: **checked approximate front coupling and external spring**, 21 September 2026.
[Native assembly](../experiments/drive_chains/front_clutch_build/TransmissionWithFrontClutch.FCStd) ·
[qualification](../experiments/drive_chains/front_clutch_build/qualification.json) ·
[HB/SNL comparison](../experiments/drive_chains/front_clutch_build/source_review/index.html).
This packet adds ten physical pieces and revises two receiving parts in the
combined transmission/pump candidate. The main compound clutch and standard
tank integration remain unfinished.

## Identity and inventory

| Selected item | Survey identity | Quantity | Original evidence |
|---|---|---:|---|
| SH945A clutch coupling | P_53a 7f 4b 7d 5250df 7 | 1 | SNL73:016, Plate 21 callout 12 |
| SH849A clutch spring half flange | P_aa 2979bfcb 3bde 26 | 2 | SNL94:013, callout 22; HB116:026 |
| SH849B clutch spring | P_7e 06cb 0aa 7aaec 65 | 1 | SNL219:024, callout 23; HB116:025 |
| 5/8 × 3-7/8in bolt, plain nut and lock washer | P_2a 3cb 30ed 643c 820 | 2 sets / 6 pieces | SNL33:004 |

All ten pieces belong to Drivetrain/TransmissionCore/FrontClutch. The half flanges
share one definition with opposed placements. Each hardware set expands into
three components; it is not counted again as an extra set solid.

The original catalogue prints two hardware sets and allocates one to flange
SH849A. Its flange entry lists two halves. The initial preparation's one-set
interpretation was incomplete. Both original quantity columns have been checked.

There is also a catalogue callout mismatch: Plate 21's 25 is indexed at SNL33:005
to a 3/4 × 1-5/8in bolt allocated to cleatM4129. The adjacent SNL33:004 explicitly
allocates the selected 5/8 × 3-7/8in set to SH849A but has no printed plate callout.
This packet follows the written SH849A allocation. The mismatch is retained in
the source-review supplement; it is not silently corrected in the frozen survey.

The catalogue coupling SH945A is distinct from handbook SH864B,
P_4fe 8df 4f 0f 1d 613b. Their identities remain separate. Transferring HB116's 9in
flange diameter and 5in body diameter to SH945A is an explicit applicability
assumption. Configuration membership is retained from the survey; absence of a
variant assignment is not evidence of universal applicability.

SH849C, P_4ad 519ba 5bd 5d 56b, is **not** an additional external spring seat.
SNL Plate 21 callout 8 places it at the main clutch's spring-plunger end. Its
construction remains with the forthcoming main clutch packet.

## Controls and mechanical interfaces

The source dossier and controls are
[front_clutch_sources.json](../experiments/drive_chains/front_clutch_sources.json)
and [front_clutch_controls.json](../experiments/drive_chains/front_clutch_controls.json).
Coordinates below are local to the transmission, with X forward. Dimensions
without printed or transferred support are reconstruction estimates.

| Feature | Selected geometry | Evidence and limitation |
|---|---|---|
| External spring | 7 turns: 5 free, 2 seating | HB116; SH849B identity agrees |
| Spring axial envelope | 107.95mm between X694 and X801.95 | Printed 4-1/4in coil length; installed-length reading inferred |
| Coil diameter | 136.525mm inside | Printed 5-3/8in "diameter of spiral"; inside/mean/outside convention unstated |
| Wire and end form | 12.7mm wire, near-closed end turns, ground seats | Estimated gauge and pitch law; no spring-rate or load qualification |
| Coupling | 228.6mm flange OD, 127mm body OD | Provisional HB-to-SNL transfer |
| Female spline | 10 approximate teeth, 0.15mm flank/radial clearance | Matches the preceding transferred cardan envelope; exact spline profile unknown |
| Split collar | 0.25mm split, nominal 50.8mm shaft bore | Static friction-clamp representation; no load or positive axial-lock qualification |
| Clamp fasteners | 15.875mm diameter, 98.425mm under head | SNL33:004 dimensions; head, nut, washer and lug sizes estimated |
| Clamp bolt axes | X670, Y±40, parallel to Z | Off-axis arrangement inferred; no hole through the shaft |
| Shaft shoulders | Two 8mm fillets | Rounded shoulders visible in both source figures; radius inferred |
| M855 receiving passage | Local relief around forward head shoulder | Keeps the new shaft fillet clear while retaining the head stop |
| Future collar joint | 6 empty holes, 100mm bolt-circle radius | HB118 count; circle and hole size inferred; SH999A and actual fasteners pending |

The bolts bear on the upper half; each nut bears on a split lock washer below
the lower half. About 4.7625mm of shank projects beyond each nut. Threads remain
smooth envelope representations. They establish the static stack, not thread
compatibility, clamp force or manufacturing tolerances.

The spring's inferred rear ground patch is clocked about 18degrees to straddle
the collar split and seat on both halves. The seven-turn centreline remains one
interpolated NURBS curve; its solid sweep uses seven one-turn spans for reliable
solid operations. The spans do not add extra physical spring components.

With the selected wire gauge, interpreting 5-3/8in as **mean** diameter instead
would reduce the coil's inside radius to 61.9125mm, inside the coupling's 63.5mm
body radius. The explicit competing-geometry test checks that interference.
This does not disprove every mean-diameter interpretation: different wire gauge
or coupling dimensions could produce a different result.

## Source comparison and corrections

HB71 and SNL Plate 21 show opposite orientations. The native centre section
follows HB, transmission left and engine interface right. The comparison keeps
the original scans and fits each panel independently; it makes no matched-scale
or pixel-for-pixel claim. Both figures show an external coil between the split
shaft clamp and front coupling flange, and blends at the shaft shoulders.
Hidden hub profiles and axial proportions remain uncertain.

The source centre sections project one clamp head/nut column into view. A true
centre cut of the CAD model misses the two off-axis bolts. The transverse
section exposes their actual positions and clearance from the cardan shaft.
This is a drawing-convention difference, not evidence for drilling through the
shaft. The source does not prove the exact transverse lug shape or bolt spacing.

The rejected first candidate is retained under
`front_clutch_build/rejected_trials/initial_seating`, with its native, frozen
inputs and failed receipts. Three issues were resolved:

- The rear ground contact missed the lower collar half by about 0.262mm.
  Inferred spring clocking now centres that contact across the split.
- A transformed trimmed NURBS bounding box reported 121.589mm axial length,
  although the actual end planes are 107.95mm apart and cutting away the seat
  slab leaves no material. Verification now measures those physical faces and
  checks containment between them.
- A single seven-turn swept surface silently returned an empty Boolean
  intersection for the competing smaller coil, despite common interior point
  and solid-ball witnesses. Dividing the unchanged spine into one-turn sweep
  spans restored the expected positive-volume interference. The competing
  diameter test is retained to detect recurrence.

## Reproduce and validate

Run from the repository root, checking each command succeeds before the next:

```sh
python 3 cad/003_FullTank/experiments/drive_chains/front_clutch_sources.py
python 3 cad/003_FullTank/experiments/drive_chains/front_clutch_build.py
python 3 cad/003_FullTank/experiments/drive_chains/check_front_clutch.py
python 3 cad/003_FullTank/experiments/drive_chains/check_front_clutch_variants.py
python 3 cad/003_FullTank/experiments/drive_chains/render_front_clutch_review.py
python 3 cad/003_FullTank/experiments/drive_chains/qualify_front_clutch.py
```

The final qualifier requires a visual-review receipt for the exact images.
Changing geometry requires fresh visual inspection; rendering alone does not
approve a reconstruction. The installation STEP contains the 12 affected
placed solids, and the definition STEP contains 8 local definitions. Neither
is the full 1,530-piece combined native assembly.

Validation covers source inventory, owning hierarchy, spring seating and
containment, seven-turn centreline and adjacent-turn clearance, clamp hardware,
shaft fillets and retained head stops, spline engagement, material interference,
saved-native validity and STEP exchange. Two coherent spring length/gauge trials
move the front coupling seat with the spring; they test sampled uncertainty,
not an exhaustive tolerance space or spring dynamics.

The saved and reopened candidate passes **88 material pairs, 70 independent
checks, 8 detailed definition STEP comparisons and 12 placed-solid exchange
checks**. Each size trial passes 88 material pairs and 5 contacts. The competing
mean-diameter coil produces a valid 16,110.5mm³ intersection, as expected.
All six final images were inspected against the original evidence.

The native contains 1,530 physical leaves with no external file references.
Of the 1,520 parent leaves,1,518 retain their previous geometry and all retain
their placements. Only the cardan shaft shoulders and M855 passage were revised.
All 20 standard native files and 69 preceding progression PNGs remain unchanged.
Three additional component-stage images are recorded in the progression log.

The main collar, cones, bearings, plungers and clutch-stop brake band remain
pending, along with pump air connections, B6205/MX1 supports, lubrication,
brakes, long controls and standard integration. Tank 011 is still the integrated
standard checkpoint, with its opaque and transparent companion views preserved.
