# Bow and enclosure reconstruction study — 27 September 2026

**`trial02` is the current diagnostic prototype. It is not integrated.** It
contains 40 proposed replacement plates and eight retained context occurrences
in a linked FreeCAD assembly, with a STEP export of the 40 proposed plates.
The accepted `operating_integrated01` development and standard tank011 remain
unchanged. No tank component is counted as newly finished by this study.

- [Native assembly](trial02/BowEnclosureHypothesis.FCStd)
- [STEP](trial02/BowEnclosureHypothesis.step)
- [Fixed section comparison](trial02/visual01/section_comparison.png)
- [Transparent local isometric](trial02/visual01/isometric.png)
- [Saved-material, joint and context checks](trial02/checks01/report.json)
- [All four complete handle rechecks](trial02/handle_recheck01/report.json)
- [Source interpretation](source_review.json)

## Geometry and dimensional interpretation

The prior wall rose forward at 61.93 degrees; the original SNL2 central bow wall
rises aft at approximately 120.48 degrees. This prototype uses a source-derived
lower corner and a bow upper corner driven by the enclosure, giving **119.53
degrees**. Its upper corner projects to **(402.368,237)** versus the reviewed
source **(404,240)**. The 3.415 px discrepancy is a hypothesis-selection diagnostic,
not independent validation. The camera/calibration and main enclosure center
were not changed.

Original HB35 prints main turret length **10 ft 3.5 in (3136.9 mm), over all**,
and driver turret length **27 in (685.8 mm)**. The original scans of HB35 and
HB43 were inspected. Neither explicitly locates both endpoints of the main
length. The prototype tests whether 3136.9 includes the driver projection:
the main body becomes **2451.1 mm**, followed by the unchanged 685.8 mm driver
body. This fits the drawn combined envelope much better than the baseline
additive interpretation. It is still a hypothesis, not a new historical fact.

Printed widths, heights, plate thicknesses and aperture sizes remain unscaled.
Previously inferred longitudinal feature stations preserve their fractions of
main-body length. Existing main-body center, ground clearance and transverse
track/frame datums remain fixed. The floor has an explicitly approximate faceted
route, 6 mm normal stock and a provisional two-part allocation. The bow has the
inherited, unproven 12 mm stock. Mathematical miters establish actual shared
faces at the bow/floor, floor/floor and bow/roof joints without trimming against
the controls. Angles, reinforcements, bends, attachments and complete closure
remain unfinished.

M2033 (SNL149:007), M2014 (SNL153:009), M1931/32 (SNL148:020/021) and M2073
(SNL155:003) are distinct source identities. The rivet row SNL169:009 associates
M2014, M2033 and M3068. It does not locate their boundaries or prove that M2014 is
an alternative name for M2033. This prototype does not silently populate the
missing identity or declare its floor allocation resolved.

## Results and limits

All **255 construction/export/preservation/variation checks** pass. The native
reopens with valid closed solids, and all **40 STEP solids** preserve material
and world placement. All **six tested joints** have physical face contact and
zero overlapping volume; contact areas range from 2432.69 to 16040.65 mm².
The 14 mm wall / 8 mm floor variation remains valid and preserves the tested
miters. These are geometric tests, not a structural-strength qualification.

The context audit considers all 40 proposed plates, 3582 retained development
occurrences and 5277 remaining physical standard occurrences. Actual Boolean
checks cover **685 bounding-box-nearby pairs**. There are **two failures**, both
unchanged operating handles against the revised wall, **4436.15 mm³ per side**.
There are no candidate-to-candidate intersections or other discovered material
intersections in this scope. No mating exemptions, collision-shaped reliefs,
camera refits or driver relocations were introduced.

All four previously built complete handle profiles also fail at this wall:

| Profile | Wall overlap per handle, mm³ |
|---|---:|
| Overall-length baseline | 4436.15 |
| Pivot-to-pole reach | 2184.82 |
| Functional radius, current return | 2096.68 |
| Functional radius, source-inferred return | 2018.44 |

Thus this shell correction improves the historical outline but **does not solve
the driver layout**. The next work must reconcile absolute shaft/seat/support
datums, depicted control state, and complete source-length connecting rods.
Keep all historical placement and final-installation claims open meanwhile.

The inspected section comparison retains visible main/driver-height, lookout,
aperture-station and floor-profile differences. HB5/HB6 provide qualitative
context only; no camera calibration or metric claim is made for those images.
The isometric is a local diagnostic, with three long rear roof panels omitted
from that view only. Orange indicates retained development material, including
the floor3 context. This is not a new standard-tank progression checkpoint;
the accepted image count remains 308.

## Reproduction and diagnostic history

Run `build_bow_reconstruction.py` with **controls02.json**, followed by
`check_bow_reconstruction.py`, `render_bow_reconstruction.py` and
`check_bow_handle_hypotheses.py`, through the project's headless launcher.
Use fresh output/runtime directories and absolute paths. Geometry is regenerated
from the source-bound worker/controls, not updated through live expressions.
The native part-level regeneration string refers to controls01, whose 40 plate
geometries are the same; controls02 is authoritative for assembly context.

Trial01 is retained as a diagnostic. It used the older standard floor3 instead
of the development panel with receiving holes; the saved-material checker caught
the difference. It also attempted to measure contact from solid `Common`, which
can omit touching faces. The final checker measures coincident planar faces
directly. The original checker is saved beside its failed report with matching
SHA256. Trial02 uses current floor3 and the corrected contact measurement.

Verify the frozen study with:

```bash
python3 cad/003_FullTank/experiments/drive_chains/verify_bow_reconstruction_study.py
```
