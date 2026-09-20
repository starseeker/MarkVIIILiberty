# R02 — drive wheels, shafts and roller-pinion interface

Preparation begun 20 September 2026 while lower-support delivery checks run.
Drive-wheel geometry is now authored; native delivery qualification is pending.
The standard installed configuration remains the priority.

## Initial source inventory

SNL275:005–014 lists two driving-wheel assemblies. Each has two M1401 rims,
one M1403 boss, five M1405X diaphragms, one M1405Y diaphragm, two M1404 disks,
36 short 5/8-inch rivets, 24 long 5/8-inch rivets and 48 3/4-inch rim rivets.
That is 119 physical leaves per wheel before the shaft assembly. The boss,
diaphragms, disks and rivets share source identities with the idler assembly;
their source totals must be reconciled across both families, not duplicated as
new independent source parts. The current idler construction is partial.

SNL215:001–007 lists two shaft assemblies, each composed of two M1477 nuts,
one M1402 shaft, two M1409 bronze bushes, one 20297/D89 key and one Q52C plug.
The resulting wheel-plus-shaft source scope is 126 leaves per side. Bearings,
retainers and hull attachments must be identified separately; these seven
shaft leaves do not establish a complete mounting installation.

The inspected [HB Plate 86](../../../references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate86.png)
shows paired toothed rims, six perforated disk sectors, formed diaphragms,
separate boss and a shaft-end retaining arrangement. It supports reuse of the
catalogue's common internal parts. It does not supply a qualified tooth profile
or permit metric measurements directly from the oblique figure.

The HB133–134 transcription gives a 39.237-inch outside diameter, 35 teeth,
3.735-inch pitch and 2-inch tooth width; the shaft is 27.625 inches long by
4.434 inches diameter. The existing layout retains 39.237 inches and the
HB130 32.75-inch inside diameter. These tooth/pitch statements require original
scan review and reconciliation with the separately recorded 9:37 reduction and
the 11.154-inch road-track chord pitch. Do not silently choose a tooth count
or reinterpret pitch to force engagement. Original scans MarkVIII066 and 067
have now been inspected: both the HB130 table and HB133 narrative explicitly
print 35 road-wheel teeth. This is not an OCR correction opportunity. The
9:37 assertion has now also been confirmed in original HB119 (MarkVIII060).
Retain all three printed assertions as a genuine source conflict.

HB132 identifies the **23.031-inch diameter with the chain sprocket / roller
pinion assembly**, not the road-track driving wheel. Its narrative identifies
23 chain teeth and 2-inch roller pinions on separate transverse pins. Preserve
these component distinctions when resolving the consolidated specification rows.

Original HB133's legend identifies M1406 inner bearings, M1407 outer bearings,
M1411 shaft-nut locking plates and M1552 bearing plates. The SNL catalogue gives
two M1406, four M1407, four M1411 and four M1552 for the vehicle. M1407/M1552
are shared with the roller-pinion shafts; assigning all four to the driving
wheels would be wrong. SNL152:021 prints M402 in the plate application, so its
apparent M1402 relationship must remain an explicit interpretation. Original
HB134 confirms the shaft and common-bush dimensions and describes a two-part
chain case. These adjacent structures must retain their own source identities.
The [review manifest](assets/drive_source_review.json) records hashes of the seven
images inspected so far. They are preparation for the next geometry increment.

SNL Plate 27, also inspected, depicts the same driving-wheel arrangement as HB86.
The present partial idler disk has a 489.3749 mm outside radius, leaving only
8.935 mm below the printed driving-wheel tip radius. This is a reason to review
the **shared** disk/rim land geometry before drawing tooth roots. It is not a
measured tooth depth. Any refinement must preserve common source identities
and be qualified on both idler and drive installations.

The [isolated rim study](../experiments/drive_rims/README.md) now preserves native
35- and 37-tooth hypotheses. Both clear the existing port assembly at eight
sampled phases. Their trial lands overlap the existing common disks, and a
first smaller-disk trial also interferes with diaphragm ends and outer short
rivets. Those rejected interfaces remain separate from the tank. Common-part
refinement must preserve the catalogue identities and qualify both families.

A revised shared interface is geometrically feasible: 449 mm disk radius,
415.925 mm rim-land bore radius, 430 mm rim-rivet circle, 410 mm diaphragm flange
radius, 404 mm web-end radius and 25 mm short-rivet radial pitch. These inferred
values remain outside the accepted parameter registry. Each 121-part fixture
clears 358 material candidates; all four installed wheel candidates clear
1,626 pairs against the preserved standard model. A subsequent 3 mm crest
rounding removes material only, preserving that clearance and the disk seats.
The isolated native files and inspected images remain in the study directory.
Next review/adopt the shared parameter ownership, integrate source-common parts
and add the source-defined drive shafts and their support interfaces.

## Next implementation work

1. Inspect original HB130–134 pages, Plates 81–83/86 and SNL driving assembly
   plates; retain each source hash and unresolved disagreement.
2. Map the fixed drive-shaft and roller-pinion axes from the existing calibrated
   section. Retain independent source picks when testing static installed fit.
3. Reuse source-common wheel internals, with explicitly owned common dimensions;
   construct the two toothed rims as separate native BRep parts.
4. Reconstruct the seven-part shaft BOM and identify adjacent bearings/retainers
   before claiming a supported wheel installation.
5. Test native seats, material clearance and static tooth/track/pinion phase in
   an isolated experiment. Continuous motion remains outside this stage.
6. Integrate accepted geometry, validate source totals over both wheel families,
   qualify native/STEP/parameter propagation, and preserve the next significant
   standard isometric milestone.

## Authored integration — qualification pending

The nominal 35-tooth hypothesis is now an explicit partial M1401 definition.
It retains the printed outside/inside diameters and 2-inch tooth width; circular
reliefs, a 462.5 mm root radius, 25.7 mm relief radius, 450 mm lip bore and
3 mm crest rounding remain inferred. The 37-tooth source assertion stays in
both the issue registry and the native reconstruction properties.

The accepted working interface uses independently owned common disk radius
449 mm and rim-rivet circle radius 430 mm. The idler land bore is provisionally
415.925 mm; it does not track changes to idler outside diameter. Diaphragm web
and flange ends are 404/410 mm, with 25 mm short-rivet spacing. These are bounded
reconstruction assumptions, supported by the separate feasibility studies,
not measured manufacturing dimensions. Rim width is provisionally common to
both families so the same source disks and joint stock can be reused.

Each new hierarchy contains the complete 119-leaf wheel BOM and a partial
shaft assembly containing its two M1409 bushes. Two nuts, the shaft, key and
pipe plug are explicitly omitted from each seven-leaf shaft BOM. Separate
bearings and retention also remain open. Global wheel totals reconcile four
bosses, eight disks, twenty X and four Y diaphragms, and four M1401 rims;
shared bushes and rivets still have unpopulated uses elsewhere.

Nominal native checks require one common library target for every shared
identity, eight rim/disk bearing seats, sampled rivet-head seats on all four
wheels, native relief counts and cylindrical dimensions, and material checks
against the rest of the assembled physical geometry. Nearest drive-to-track
bushing distances are measured without asserting engagement. Trials change
idler diameter independently, enlarge the common disks by 0.5 mm on all eight
copies, and build the alternate 37-tooth branch without moving unrelated parts.
Results and source/model visual findings will follow the saved-native checks.

## Paired-rim phase correction

The first integrated native build passed 1,876 material candidates and eight
rim/disk seats, but inspection of the installed transforms found a half-pitch
stagger between the two 35-tooth rings. Reversing the inner rim about X changes
the +Z groove phase for an odd tooth count. Reversing about Z keeps both groove
sets aligned while placing the attachment land correctly. The native phase
checker rejects the old placement and a deliberate one-degree error; corrected
placements pass on both sides. See the [preserved regression](../experiments/drive_rims/phase_alignment/README.md).

HB Plate 125, subsequently inspected, gives the labeled wheel section and
supports the nested common disk/land topology. It is now source-locked and
included beside the native transverse section. A new complete build and all
parameter trials are required after the phase correction. Pre-correction
track-gap measurements are retained in the diagnostic history, not final results.

## Delivered qualification

Nominal wheel checks pass 1,876 material candidate pairs with zero overlaps,
24 sampled rivets with two bearing heads each, eight rim/disk seats and native
paired-rim alignment. The five remaining shaft-BOM leaves per drive side are
explicitly omitted. Shafts, keys, end nuts, oil plugs, bearings, locking plates,
roller pinions and chain still require integration.

Saved-native validity/placement, both STEP round trips, relocated dependencies,
independent rebuild/cache reuse and all thirteen parameter trials pass. The
new trials change the common disk radius and drive tooth count; the idler-OD
trial confirms that common disks and drive installations stay independent.
Thirty-three record/renderer tests pass. Native generation took
67.78 s; independent/cached rebuilds took
102.36 / 46.75 s.
The source lock verifies 740 files and the unchanged survey.

Preserved [isometric 009](../../intermediate_snapshot_iso_009.png) and a
[drive-wheel detail](../../intermediate_snapshot_detail_drive_009.png). Earlier
snapshots remain byte-identical. Eight final rasters were inspected, including
the shared idler sections and lower-support bank.

The next-stage [shaft/mount fixture](../experiments/drive_mounts/README.md) remains
separate from this delivery. Its isolated and installed contacts pass; the
source-correct receiver reconstruction and mounting builders still require
integration and full delivery qualification. The
standard tank, remaining exterior systems and identifiable interiors remain
in progress; historical-fit and complete-tank verification remain false.

