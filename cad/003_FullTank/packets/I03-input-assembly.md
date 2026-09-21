# I03 — transmission input bearings, housing and coupling

This increment extends the [bevel drive](I03-bevel-drive.md) with the opposed
Timken bearings, M250 housing, M246 coupling, M252 packing disk, M253 felt,
M251 gland, M249 distance piece, MX35/M254 shim packs, M248 washer, MX33 nut,
split pin and four MX22 bolts with eight separate nuts. The integral M247
pinion remains one existing part. Its shaft extension and the M264 input
receiver change to fit the populated assembly.

The input assembly is still partial: cover fasteners, pump attachments,
lubrication, support bracket and detailed retention remain open. It belongs
to the isolated transmission candidate, pending standard-tank integration.

## Source evidence and inventory

The [source register](../experiments/drive_chains/transmission_input_sources.json)
retains the SNL rows, handbook quantity conflict and inspected source hashes.
SNL68/78 specify a 69.85 mm cone bore, 54.229 mm cone width, 149.225 mm cup
outside diameter and 44.45 mm cup width. The current
[Timken 6454/6420 listing](https://cad.timken.com/item/tapered-roller-bearings-ts-tapered-single-/tapered-roller-bearings-ts-tapered-single-imperi-2/6454-6420/)
corroborates those four dimensions. Its assembled width of 53.975 mm is used
as a provisional transfer; agreement does not prove unchanged historical
internal construction. Timken's [bearing design reference](https://www.timken.com/resources/tapered-roller-bearing-catalog/)
supports the common-apex construction method, not our inferred race angles,
roller count or cage dimensions.

Each bearing has a cup and a cone subassembly; the cone has an inner race,
a perforated conical cage and sixteen linked tapered rollers. The canonical
commercial identities belong to the assembly containers and cup leaf.
Embedded SNL18/112 aliases are recorded explicitly. Thirty-eight internal
solids represent two commercial bearings, rather than thirty-eight catalogue
bearings. Both bearings reuse the same four definitions.

SNL27 expressly gives two 3/8 inch plain nuts for each MX22 bolt. These are
modeled separately; lock washers are not substituted. The SNL's thirteen
MX35 and sixteen M254 shims are marked “as required.” This reconstruction
selects those nominal counts with assumed 0.1 and 0.125 mm leaf thicknesses.
SNL215 supplies the 3/16 × 2-1/2 inch split pin; its legs remain unspread.
Threads are plain diameter envelopes and the nut/head sizes are inferred.

Two inventory conflicts remain explicit:

- SNL112 lists one M249 distance piece, while SNL134 and HB205 list two.
  One outer-cup spacer is provisionally installed from the assembly list and
  section interpretation. The second catalogue allocation is unresolved.
- Original SNL240 prints a one-inch nut for a half-inch MX25 stud, and its
  global quantity differs from the stated housing-joint allocation. These
  cover fasteners remain pending; the modeled receivers do not resolve that
  source conflict.

## Geometry and visual registration

The [controls](../experiments/drive_chains/transmission_input_controls.json)
separate printed dimensions, the modern width transfer and reconstruction
assumptions. X increases from the bevel centre toward the coupling. The
inboard cone seats at X203 mm; the small cone faces are X257.229 and
X297.229 mm. The outboard cone seats against the coupling at X351.458 mm.
The spacer and thirteen separate shims locate the cup backs. Sixteen M254
leaves occupy the cover/flange joint at X248–250 mm.

The packing cavity and gland are sized to let the source-sized cups pass
through the housing's open end. The packing disk has a narrow annular nose
against the outboard cup, and an inward flange clear of the rotating cone.
The felt contacts the coupling sleeve. The shaft thread starts at X466 mm
beneath the washer; the nut seats at X470 mm and the shaft/flange ends are
X490 mm. Coupling bolt pattern, casting sections, splines, fits, grease
passages and sealing details are not original manufacturing dimensions.

The [Plate23 calibration](../experiments/drive_chains/transmission_input_calibration.json)
uses the cup's 149.225 mm outside diameter over a visually picked 162 pixels.
The resulting 0.921142 mm/pixel scale has independent axial-width residuals
of +4.724 mm for the cone and +7.134 mm for the cup. Those discrepancies remain
visible; the source raster is not stretched to match the model. Plate22's
existing hub-based scale is retained for a separate comparison.
The cup-diameter pick midpoint is also seven pixels above the selected bevel
centre, a 6.448 mm apparent axis offset. The model retains a common mechanical
axis; that scan/illustration discrepancy is not silently absorbed into a
misaligned bearing placement. The printed-pitch pinion remains visibly smaller
than the illustrated profile in Plate23, as in the previous bevel review.

**Correction to the preceding review:** Plate22 shows the coupling detached
beside the principal section. That section's endpoint is therefore not the
complete assembled shaft endpoint. The earlier statement that the shaft
was necessarily too long is withdrawn. Plate23 is used for the complete
axial span, with its own scale uncertainty. The earlier 32.113 mm bevel/output
registration disagreement also remains unresolved.

## Verification and rejected trials

The initial bearing trial found a 148.096 mm³ cage/rib intersection. The
assumed large rib radius was reduced from 60 to 59 mm, and the cage pockets
were extended axially so the roller end faces have clearance. The first
complete assembly trial found a 3,859.497 mm³ washer/spline intersection.
Separating the thread-start datum from the nut seat corrects that defect.

The independent checker's first pass also exposed two measurement mistakes:
the cached display mesh gave a slightly undersized cup bounding box, and each
cage pocket had two conical wall patches. The corrected checks measure the
saved analytic cylinder radius and count unique inclined pocket axes. The
CAD geometry was unchanged by those checker corrections.

The saved candidate reopens with **1,287 valid single-solid leaves**: 88 new,
two revised and 1,197 retained unchanged. All 749 affected material pairs,
578 specified interfaces and 90 native/STEP material comparisons pass. Both
raw and bounded exchange comparisons have zero material difference; stored
tolerances are not inflated. Further qualification results and inspected
raster hashes are recorded in the build reports. Geometry checks include
native reopen, all affected material pairs
against the candidate and standard physical context, seats/clearances,
two-way STEP material comparisons, printed bearing envelopes, shared
definitions, common-apex race surfaces, cup insertion and shaft passage
gauges, and deliberate obstructed-entry/displaced-STEP negatives. This does
not qualify operating preload, contact stress, sealing, manufactured fits,
formed cotter retention or the complete transmission installation sequence.

The [independent checker](../experiments/drive_chains/transmission_input_build/interface_checks.json)
passes 181 checks. The [visual review](../experiments/drive_chains/transmission_input_build/visual_review.json)
records all six inspected images, including the
[Plate23 overlay](../experiments/drive_chains/transmission_input_build/source_review/input_plate23_overlay.png).
The [saved native candidate](../experiments/drive_chains/transmission_input_build/TransmissionInputCandidate.FCStd)
retains all accepted pinion spline surfaces and material outside the shaft
extension region. Twenty standard native files and forty previous snapshots
remain byte-identical; three new progression images preserve this increment.

## Reproduce and continue

```sh
python3 cad/003_FullTank/experiments/drive_chains/transmission_input_probe.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/render_transmission_input_review.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/check_transmission_input.py --stage cad/003_FullTank
```

Use `--output` on the builder and `--candidate` on renderer/checker for trials.
Next resolve the M249/MX25 allocations and finish the housing installation,
then the M265/M266 brake-bearing joint, case fastening, controls, lubrication,
mounting and standard-tank integration. The complete-tank objective remains
active; this increment is not a finished transmission or tank.
