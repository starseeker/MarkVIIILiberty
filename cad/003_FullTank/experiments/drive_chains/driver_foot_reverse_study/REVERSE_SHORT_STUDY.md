# Reverse lever body and third short rod — checked static study

The [reverse_short03 native](reverse_short03/ControlRebuildTrial.FCStd) adds a
reverse lever body, the third shared M789A short rod and two complete four-part
clevis joints. Three unchanged receivers preserve the actual driver shafts and
M784 swing link. There is one new definition and ten new physical occurrences.
Trigger, pawl, quadrant, their attachment features and the long reverse route
remain unfinished. This is an isolated study, not an integrated reverse mechanism.

Nominal and −1 mm blade-stock builds each pass 75 saved-material, source-property,
dimension and joint checks, 53 nearby-pair comparisons in an 8,997-occurrence
context, and 11 strict native/STEP comparisons. A fresh nominal build reproduces
all 27 archive BReps and 1,291 persistent properties exactly. Inherited material
and frames remain unchanged. Only the M789A reconstruction note changes, to
acknowledge its third application; all other source/approximation metadata survives.
Dimensions update through regeneration, not live FreeCAD expressions.

Original HB150 gives 27.968 inches on the hand side and six inches on the bell
arm. These are interpreted as hub-center-to-grip-extreme radial reach (710.3872 mm)
and hub-to-eye radius (152.4 mm). The latter closes the full 269.875 mm M789A stock
against the retained M784 eye, using existing complete clevises and estimated
19.05 mm socket insertion. Both mathematical circle solutions are retained;
the lower eye is selected. The unprinted included angle is consequently inferred,
not a measured source angle. Original SNL118 prints M177, whereas the figure
family suggests M777. Both identities remain visible.

The 47.4-degree upper-hand elevation, 105 mm outward set, 30 mm delayed set,
blade sections, hub and grip are estimates. Four inspected [native/source views](reverse_short03/visual01/visual_review.json)
retain the fixed HB113 and SNL6 registrations. The apparent SNL6 hand endpoint
is about 25.23 pixels from the saved-solid projection, exceeding the five-pixel
pick uncertainty. The schematic/mixed view and provisional endpoint identity
prevent treating this as an exact dimensional error, but it remains an unresolved
source discrepancy. No camera was refitted. HB94's quadrant and trigger silhouette
still require reconstruction; the bare lever is not claimed to reproduce that view.

The rejected cases expose actual constraints:

- `reverse_short01`: borrowing the clutch's 60 mm delayed bend intersects the
  low-speed selector by 45,247.507 mm³. A separate checker error expected an
  uninterrupted cylindrical journal despite its oilway; the corrected check
  measures the full axial span, open bore and real shaft fit.
- `reverse_short02`: a straight outward blade clears the selector but intersects
  four seat/support components. The final smaller bend clears both sides of
  this corridor, retaining full material and all endpoints.
- `reverse_short_variation02`: +1 mm blade/eye stock also intersects the unchanged
  clevis by 304.035 mm³. It is a retained failed limit. The qualified −1 mm
  variation does not imply that thicker stock fits.

The [external-source screening](external_controls01/source_screening.json)
preserves a surviving-tank photograph and public IWM1194 preview frames. They do
not resolve the hidden M765/M769/M771 joints, and no dimensions are taken from
them. The front-unit eight M568C pins cover three M789A plus one M789B short rod;
driver-to-intermediate rods belong to another inventory level. Do not use that
front-unit count to invent the foot-link endpoint graph.

Continue with M779 quadrant, M781 distances, M780 pawl, M778 trigger rod and the
SNL118 trigger/guide/spring hardware, including real receiving holes and seats.
Revisit the blade and apparent source pose as those constraints become available.
Then reconcile HB150's 52-inch nominal 3/4-inch pipe with M571 and its actual
forks; it is not the short M789A. The incompatible foot studies remain open and
must be reconciled before their combined integration. The authoritative coupled
station and standard tank011 are unchanged; accepted visual progression stays314.

Reproduction uses the existing headless launcher and absolute paths:

```text
build_driver_reverse_short_v2.py --controls .../reverse_controls03.json --output NEW
pump_integration_worker.py extract --input NEW/ControlRebuildTrial.FCStd --output NEW/isolated/manifest.json
check_driver_reverse_short_v2.py --candidate NEW
check_driver_seat_context.py --candidate NEW
exchange_driver_reverse_short.py --candidate NEW
render_driver_reverse_short.py --candidate NEW
```

Use `--stock-offset -1` for the qualified variation. STEP checks retain strict
material, tolerance and converged mass/centroid criteria with standard adaptive
Gauss integration. `check_control_rebuild_reproduction.py` compares a fresh build;
`verify_driver_reverse_short_study.py` verifies the frozen receipt.
