# I03 — transmission brake-bearing supports

The [candidate](../experiments/drive_chains/transmission_brake_bearing_build/TransmissionBrakeBearingCandidate.FCStd)
adds two M265 bushes, two M266 caps with M300 dowels, and four MX14
stud/nut/cotter sets to the [input-installation checkpoint](I03-input-installation.md).
It contains **1,321 valid single-solid occurrences**: eighteen new, three
revised and 1,300 retained unchanged. Four definitions are new; the existing
source-sized dowel and repaired cotter definitions are reused.
The transmission remains isolated pending standard-tank integration.

## Evidence and interpretation

The [source register](../experiments/drive_chains/transmission_brake_bearing_sources.json)
retains literal catalogue rows and hashes of inspected images. SNL44 identifies
two M265 brake-bearing bushes. SNL56 identifies two cap assemblies, each owning
one M266 cap and one bronze M300 dowel, 5/8 inch diameter by 1/2 inch long.
The assembly identity lives on each native cap container; its two physical
children are counted separately. With these two additions, the candidate has
all eight SNL83 M300 dowels, sharing one definition.

SNL59 assigns four MX14 stud assemblies to M263. SNL240 supplies the detailed
stud, half-inch SAE castle nut and 3/32 × 1 inch split-pin entries. Its stud
length is **1-11/16 inches, 42.8625 mm**; SNL59's owning assembly instead gives
**1-9/16 inches, 39.6875 mm**. Both specify half an inch of U.S. Standard thread
and 7/8 inch of SAE thread. This candidate selects the detailed component
length and retains the discrepancy. A local trial of the shorter length also
fits the inferred joint, so geometry does not settle which source is correct.
Unlike the earlier MX25 nut, this nut has a directly supported half-inch
catalogue identity; its exact flats, crown, slots and clearance remain inferred.

Original SNL44/56/59/240 catalogue photos, SNL Plate22, handbook Plate73,
the part-marked Plate123 section, and the Plate79 exterior were inspected.
They support the position and constituent identities, but do not establish a
complete three-dimensional casting or a manufacturing fit. The selected
**architecture is a reconstruction hypothesis**:

- One continuous flanged M265 bush supports the adjacent M277 case-neck and
  M269 high-speed-drum journals. Their existing 4.3543 mm axial gap remains.
- A forward semicircular M266 cap closes against a rear saddle reconstructed
  as an integral extension of the stationary M263 case. Two MX14 sets retain
  each cap. A radial M300 dowel engages the bush and cap.
- The formerly estimated R58 M269 hub is thickened to the inherited R76.2
  M277 neck journal. The drum's printed 381 mm outside diameter and all
  internal spline, shoulder and retaining-ring-pocket material are preserved.

The source images do not independently prove this interpretation. In particular,
the transverse shape of the rear bridges, cap ears and dowel placement remain
assumptions. The bridges currently have simplified webs and sharp cast transitions;
they need refinement if further evidence establishes their form. Bronze shading
for M265 is a display/material assumption; the cited catalogue explicitly calls
only M300 bronze. The model does not qualify lubricant delivery to these bushes,
loads, bearing wear, press fits or the complete transmission installation sequence.

## Geometry and ownership

The [controls](../experiments/drive_chains/transmission_brake_bearing_controls.json)
retain the existing local frame: X forward, Y port, Z up, at the transmission
shaft datum. Port and starboard groups use rigid placements; starboard is a
180-degree rotation about X. M263 remains one physical casting and owns both
new rear saddles. Each side's cap container owns its cap and dowel, with the
bush and two fastener sets in the surrounding bearing-support container.

| Feature | Nominal reconstruction |
|---|---|
| Bush axial interval | Y246.472857 to311.938571 mm |
| Bush bore/body/flange radii | 76.35 /84.5 /88 mm |
| Bush end flanges | 3 mm each |
| Cap and rear-saddle interval | Y249.472857 to308.938571 mm |
| Cap outer radius | 109 mm, tapering to96 mm at each end |
| Cap split | X±0.15 mm |
| Stud axes | Y279.205714 mm, Z±110 mm |
| Stud interval | X−12.85 to30.0125 mm |
| Nut interval /cotter station | X12.5 to25.5 /X23 mm |
| Dowel origin | X81.5, Y279.205714, Z0 mm |
| Dowel diameter /length | 15.875 /12.7 mm, printed |
| Journal running clearance | 0.15 mm radial, assumed |

The bush axially overlaps the drum journal by 42.542857 mm and the case neck
by 18.568571 mm. Its flanges locate it axially in the two half saddles. The
rear bridge passes behind the high-speed drum at X−224 to−200 mm and joins
the existing M263 end-wall material. Smooth thread envelopes are used; there
are no invented helical thread forms or load claims.

## Validation and visual review

The [combined qualification](../experiments/drive_chains/transmission_brake_bearing_build/qualification.json)
passes for the saved native document. All **153 affected material pairs** have
zero intersections. **21 native/STEP comparisons** have zero raw and bounded
material differences. Thirty interfaces are freshly checked; 584 earlier
interface results are retained against unchanged geometry and a hash-bound
parent report. The builder's report is immutable; the combined qualification
records completed rendering and review.

The [independent checker](../experiments/drive_chains/transmission_brake_bearing_build/interface_checks.json)
passes **109 checks**. It verifies source dimensions and identities, definition
reuse, connected M263 material, preserved original case/drum stock, unchanged
splines and ring pockets, both journal clearances, flange capture, dowel
engagement and anti-rotation, threaded intervals, nut seats, both cotter legs
and formed-tail retention. A swept annular witness checks bush insertion over
the M277 neck with the cap and drum removed; an oversized-neck negative is
correctly rejected. This is a local installation check, not a complete assembly
procedure or moving-gear validation.

The first checker used a solid cylinder occupying the bush bore as its
collision witness. That volume correctly overlapped the journal and produced
two false failures. The corrected witness sweeps the actual annular material.
The failed checker/report/log are preserved in `rejected_trials`; no CAD
geometry was changed to repair the test.

Four [local parameter trials](../experiments/drive_chains/transmission_brake_bearing_build/sensitivity_checks.json)
pass: radial running gaps of0.10 and0.25 mm, bush body radius85.5 mm, and the
alternate39.6875 mm stud length. Each uses twelve actual local parts and
checks all66 pairs. These trials do not requalify the complete tank.

Seven [inspected views](../experiments/drive_chains/transmission_brake_bearing_build/visual_review.json)
include an overview, joint and fastener detail, two sections and SNL22 overlays.
The cap/bush now occupy the pictured bearing region. Casting contours, shoulder
positions and the pin glyph still differ; the drawing's drum silhouette remains
larger than the retained printed381 mm diameter. The prior32.113 mm bevel/output
registration discrepancy is unchanged. No image was stretched to hide these
residuals.

Three new [progression snapshots](../../VISUAL_PROGRESSION.md) preserve the
support overview, focused bearing section and fastener. Twenty standard native
files and all forty-six earlier snapshots remain byte-identical. Standard
milestone011 and its transparent-hull companion are unchanged.

## Reproduce and continue

```sh
python3 cad/003_FullTank/experiments/drive_chains/transmission_brake_bearing_probe.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/check_transmission_brake_bearing.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/check_brake_bearing_variants.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/render_transmission_brake_bearing.py --stage cad/003_FullTank
```

The builder accepts `--output`; the remaining scripts accept `--candidate`.
Rendering and independent checks write separate receipts without changing the
builder report. Visual inspection and the combined qualification follow them.

Next work remains: input pump/support installation, M263/M264 and planetary
case fasteners/gaskets, reversing controls, brakes, complete lubrication and
mounting, then standard integration. M249 quantity, MX25 count/nut identity,
MX14 length and source-datum disagreements remain explicit. This is a checked
geometric increment with documented approximations, not a completed transmission
or full tank.
