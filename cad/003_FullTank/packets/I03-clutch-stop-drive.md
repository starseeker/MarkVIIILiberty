# I03 — clutch-stop coupling, cardan shaft and pump belt

Status: **checked approximate clutch-stop drive for continued reconstruction**,
21 September 2026. [Native assembly](../experiments/drive_chains/clutch_drive_build/TransmissionWithClutchDrive.FCStd) ·
[qualification](../experiments/drive_chains/clutch_drive_build/qualification.json) ·
[HB/SNL comparison](../experiments/drive_chains/clutch_drive_build/source_review/index.html).
The reconstruction adds 30 physical occurrences to the checked 1,490-piece
transmission/pump parent. The full compound clutch, spring/front coupling,
clutch-stop brake band, air circuit and standard tank integration remain open.

## Identity and ownership

| Selected item | Survey identity | Quantity | Source |
|---|---|---:|---|
| M855 coupling box | P_5315209b9e51cbeb | 1 | SNL34:012 |
| M856 cover half | P_fc1898fbe894546d | 2 | SNL74:027 |
| M858 clutch-stop drum | P_a98bc93044bb4290 | 1 | SNL83:035 |
| SH1000A cardan shaft | P_6bc6b194198fd225 | 1 | SNL211:031 |
| US 1/2 × 2-7/8in bolt/plain nut/lock washer | P_9e131e650ec739da | 8 sets / 24 pieces | SNL31:013, M855 allocation |
| SH900G linked V belt | P_dcb795c5f886ca95 | 1 assembly representation | SNL18:011 |

The first 29 pieces belong to Drivetrain/ClutchStopDrive; the belt belongs to
FuelPressure/AirPumpBeltDrive. Each hardware set expands into three physical
pieces, with no extra set solid. The half covers reuse one definition through
opposed placements. Existing M246 retains its original identity and shaft fit;
eight new holes replace its earlier six inferred holes. HB118 independently
specifies eight coupling-box bolts; its six front-clutch bolts belong to a
different joint.

SH1000A is not silently merged with handbook SH864A, survey
P_5aba1bf2508ce8a2. HB116's 11-1/4in length, 2in body, ten splines and
4.359in enlarged diameter are provisional transfers to the selected catalogue
shaft. Their exact transcription does not establish applicability. Configuration
membership is absent for these survey records; this is not evidence of universal
applicability. Original catalogue and handbook evidence remains distinguished.

## Construction and interfaces

The controls and source dossier are
[clutch_drive_controls.json](../experiments/drive_chains/clutch_drive_controls.json)
and [clutch_drive_sources.json](../experiments/drive_chains/clutch_drive_sources.json).
All unprinted/untransferred dimensions are reconstruction estimates.

The existing transmission flange occupies local X475–490. A six-millimetre drum
web and six-millimetre half covers close the coupling at X502. The covers have
an estimated 30mm central bore radius. Eight fasteners
lie on an inferred 68mm radius, clocked22.5degrees to avoid cover seams. Their
heads seat at X475; washers seat in the box at X530. Bolt length remains the
printed73.025mm under the head, with about4.41mm protruding past each nut.
Deep axial access pockets permit placement of the nuts. Their hidden shape and
actual wrench form are unverified.

The shaft has an inferred rounded-square drive head and matching pocket, with
0.15mm radial clearance and0.20mm axial endplay at both ends. These clearances
support static geometric inspection; they are not manufacturing tolerances or
an articulated universal-joint model. Smooth thread representations establish
envelopes and clearances, not screw strength or thread compatibility.

The initial76mm head section was visibly smaller than both source sections.
Coarse scaling from the transferred2in shaft diameter suggests about111mm in
HB71 and95mm in SNL21. The revision uses100mm across flats and36mm corner
radii. The transverse profile remains unknown; the source sections cannot prove
that it was square. Body-span endpoint uncertainty is at least±8pixels, before
unknown scan and figure distortion. The initial mechanically passing native and
its checks remain in `.work/clutch-drive/narrow_head_passed_mechanics`.

The stop drum has an estimated228.6mm outside diameter and99mm axial extent.
Rough source proportions suggest diameters241mm/227mm and lengths84mm/96mm
for HB/SNL respectively. The longer-than-HB cup remains a documented discrepancy;
the SNL proportions are closer. No pixel-for-pixel or manufacturing agreement is
claimed. The front spline profile is an approximation bounded by the transferred
outside diameter. Its mating front clutch assembly remains to be reconstructed.

## Belt and coupled mounting update

SH900G is printed as54in long,5/8in wide and28degrees. The saved belt has a full
trapezoidal cross-section, analytic pulley arcs and tangent spans. The selected
length convention treats54in as pitch length with the pitch line5mm below the
outer face. Actual groove fit gives nominal pitch radii about108.047mm and
88.997mm. The closed-loop equation places the pump centre375.802mm above the
transmission axis, an increase of about0.797mm from the preceding mount study.
The pump, brackets, stepped studs and clamping stacks update together.

The 108 shallow transverse scores suggest the linked construction. They are
not evidence of108 historical links. Individual proprietary link construction,
count and material remain an explicit inventory gap. The belt is one physical
assembly representation, with no load, elasticity or tension-life qualification.

## Reproduce and review

Run from the repository root:

```sh
python3 cad/003_FullTank/experiments/drive_chains/clutch_drive_build.py
python3 cad/003_FullTank/experiments/drive_chains/check_clutch_drive.py
python3 cad/003_FullTank/experiments/drive_chains/check_clutch_drive_variants.py
python3 cad/003_FullTank/experiments/drive_chains/render_clutch_drive_review.py
python3 cad/003_FullTank/experiments/drive_chains/qualify_clutch_drive.py
```

The final qualifier requires a visual-review receipt for the exact rendered
images. A geometry-changing rebuild needs fresh visual inspection before that
receipt can be updated; the renderer alone does not approve its output.

The builder saves a combined native assembly, a114-solid affected installation
STEP and22 local definitions. The installation STEP is not the full1,520-leaf
model. Saved-native checks cover identities, counts, retaining surfaces, bore
continuity, seated hardware, belt groove contacts and deliberate displacement
failures. Definition exchange checks include Boolean geometry and explicit OCC
mass integration; placed exchange checks cover count, validity, mass and centroid.
Two coupled radius/profile and shaft-size scenarios test sampled uncertainty,
with the rest of the transmission and the standard tank's physical context.

The final candidate passes **474 material pairs, 148 independent interface checks,
22 detailed definition STEP comparisons and 114 placed-solid exchange checks**.
Two coupled size scenarios pass 450/474 material pairs and 27 contacts each.
Six final views were inspected. The preserved source comparison records the
wider head and remaining casting, shoulder and identity-transfer differences.
All 20 standard native files and 66 earlier progression PNGs remain unchanged;
three new component-stage snapshots have been added.

The native assembly has no external file references. Qualification accepts it
for continued front-clutch reconstruction, with historical fit, complete clutch,
pressure circuit and proprietary belt-link inventory still unqualified.
The first narrow-head model and the export/report-writer failures are retained
as diagnostics; passing mechanics did not establish source-profile acceptance.
Standard tank011 and its opaque and transparent views remain the current
integrated tank checkpoint.

The subsequent [front-clutch packet](I03-front-clutch.md) adds the external
spring, split flange and front coupling, and refines both shaft shoulders.
Its 1,530-piece native preserves this earlier checkpoint. Main clutch
construction and standard integration continue.
