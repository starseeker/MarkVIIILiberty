# P01 — lower engine distribution drive

Status: **component development study; installation unqualified**, 23 September
2026. This extends the main-driving-gear work. The complete powerplant and tank
remain unfinished; standard geometry continues to precede pose variants.

The [native study](../experiments/drive_chains/engine_lower_drive_study/DrivetrainWithLowerDriveStudy.FCStd)
contains 2,170 physical occurrences: 17 new constituents and 2,153 unchanged
parent occurrences. This count includes drivetrain context and is not additive
to the standard tank BOM. The original casing is retained so its conflicts with
the new unit remain visible.

A subsequent [receiving-case candidate](P01-engine-lower-drive-receivers.md) resolves the three casing contacts and verifies local withdrawal and saved-driver mesh. The original component study below is preserved as its dated checkpoint.

## Ownership and evidence

The [source dossier](../experiments/drive_chains/engine_lower_drive_sources.json)
selects 29 catalogue records and preserves 21 source-asset hashes. The
[controls](../experiments/drive_chains/engine_lower_drive_controls.json) distinguish
61 source-supported, numerical and estimated choices.

| Constituent | Installed count | Source |
| --- | ---: | --- |
| LQ156A / C8077 integral bevel driver | 1 | SNL83:033; SNL113:006 |
| LQ159A / B8062 bronze bush half | 2 | SNL44:027; SNL113:007; LIB88 |
| LQ160A / B8065 flywheel-end housing half | 1 | SNL113:011 |
| LQ162A / B8064 distributor-end housing half | 1 | SNL113:016 |
| LQ163A locating dowel, 3/16 × 3/8 inch | 1 | SNL113:017 |
| LQ164A drilled bolt, 1/4 × 15/16 inch | 2 | SNL25:020; SNL113:013 |
| LQ89A special nut | 2 | SNL25:021 |
| LQ113A special washer | 4 | SNL25:023 |
| Split pin, 1/16 × 1/2 inch | 2 | SNL25:022 |
| LQ165A retaining screw, 3/8 × 3-1/4 inch | 1 | SNL89:024; SNL206:010 |

Catalogue assembly rows are containers, not additional physical material. In
particular, each clamp set contains two washers. Illustration identity **116**
belongs to the complete bolt set in SNL25:018; manufacturer number **712** belongs
to its constituent bolt in SNL25:020. The earlier preliminary notes treated these
as contradictory bolt marks. Their different quantity/identity scopes explain
the distinction without changing either literal record.

SNL plate 19 and HB99 retain the caption “Fan bevel gear drive.” Matching marks,
SNL113 ownership and HB100/101 place this unit in the engine water-pump drive.
It must not be substituted for the separate radiator-fan bevel gearbox.

LIB27/28 describes the lower vertical shaft as one piece with a 22-tooth upper
bevel, a 21-tooth lower bevel and a hollow, internally splined oil-pump coupling.
It runs in a split bronze bearing inside aluminium housing halves. The 21-tooth
lower gear drives a 21-tooth water-pump gear; the pumps run at 1.5 engine speed.
These aircraft-engine descriptions retain conditional applicability to the tank
engine. Figures 88 and 96 guide bearing oil passages and service access.

## Geometry and unresolved installation

The study uses the saved main-bevel apex and module 3.5 mm. Its upper gear has a
10 mm face and its lower gear a 7 mm face; HB101 identifies the wider gear with
the cupped housing end, but does not print these dimensions. The 16 mm shaft
radius, 8 mm bore radius, six internal spline slots, housing profiles, oil-port
dimensions and fastener details are estimates. Threads use nominal smooth
envelopes. The upper housing end has an estimated conical cup, radius 34 mm
and depth 6 mm, following HB101. Housing outer radius 43 mm exceeds the upper
gear radius so that a cylindrical supporting lug can pass the gear during
withdrawal. The earlier 37 mm housing failed that service-envelope constraint.

HB100 prints 0.005–0.008 inch endplay and 0.0015–0.0025 inch diametrical bearing
clearance. The selected midpoints are 0.1651 mm and 0.0508 mm respectively. The
diametrical clearance is halved for the radial running gap.

The provisional 184 mm separation between crankshaft and water-pump axes gives
an approximately 84 mm journal between the integral gears, comparable to the
driver diameter in the isolated plate 19 view. This is a qualitative proportion
estimate, not calibrated measurement. The inherited casing has a water-pump
aperture at 154 mm below the crankshaft. Reconcile this mismatch using the
longitudinal engine views and the future water-pump assembly before accepting
either position. The assumed main-gear module also remains open to source-led
revision; fitting a component does not establish historical dimensions.

The 82.55 mm housing screw is studied from the rear into a blind housing seat
outside the rotating shaft. Its supporting casting boss and case receiver are
not yet represented. HB100 requires removal of this screw followed by withdrawal
of the housing and driver through the bottom oil-pump opening. Figure 96 shows
an offset opening: check an actual removal path, rather than assuming that the
opening must be coaxial or that the spindle fitting through it is sufficient.

## Initial mating-gear experiment

The real saved 33-tooth main bevel was paired with a 22-tooth test pinion. A
half-tooth phase places a gap toward the crankshaft. Nine samples over one main
tooth pitch, with the pinion rotating at the opposing 3:2 ratio, have zero
material overlap and approximately 0.08043 mm minimum separation. The deliberately
incorrect phase produces substantial overlap, so the check distinguishes the
two arrangements.

Native contact bracketing gives approximately 0.20014 mm circumferential backlash
at the outer pitch circle, 0.18572 mm at mid-face and 0.17131 mm at the inner
pitch circle. These fall within the LIB117 cold range of 0.127–0.254 mm. The source
does not specify a measurement station. This test uses the initial 64-station
tooth interpolation; the component study uses 128 stations and still needs its
own full mesh/free-play confirmation before installation acceptance. This is
geometric evidence, not manufacturing or load qualification.

The test pinion intersects the inherited lower casing by approximately 840.97
mm³, near its rear wall. A casing revision must preserve supporting material and
provide the source-described housing lug. Merely cutting away the interference
does not complete that task.

## Acceptance still required

- Resolve the casing contacts exposed by the independent saved-native checks;
  continue preserving all unaffected parent material and frames.
- Refine the upper-edge oil-entry notches and smoother housing waist identified
  during comparison with LIB88 and SNL plate 19. The unequal-end treatment from
  HB101 is now represented; its exact dimensions remain estimates.
- Run a coupled parameter variation and fresh reproduction of the final accepted
  generator. Current component native/STEP comparisons pass.
- Reconcile gear scale, lower shaft length and water-pump axis; construct the
  receiving case lug, screw support and accessible bottom opening.
- Verify the completed unit's mesh, backlash, installed interfaces and service
  withdrawal, then include standard tank context checks.
- Continue the upper distribution drives, rods, pistons, cylinders, valve gear
  and services; reconcile inventory and mountings before standard integration.


## Saved component-study evidence

The corrected native passes **37 independent component checks**, including both
saved tooth counts, bearing endplay and diametrical clearance, oil groove,
unequal housing ends, printed hardware dimensions, five constituents per clamp
set and full material/frame preservation of all 2,153 parent occurrences. The
integral driver fits within a cylinder 0.25 mm smaller in radius than the housing,
providing a necessary condition for passage through its future receiving lug.
This does not qualify the complete removal route.

All new components clear one another. Among 68 affected material pairs,
3 contacts with the original lower casing remain unresolved and are explicitly
reported as installation failures. Standard tank context was not checked for
this unqualified study. **27 native/STEP comparisons pass** across ten definitions
and seventeen installed occurrences. No parameter trial or fresh independent
reproduction is claimed.

Six corrected native views were inspected against the source context. The upper
cup, split bearing and oil routes, windowed holders, integral gears and nested
clamp hardware are visible; unprinted shapes remain approximations. Source88
upper-edge oil-entry notches and the smoother waisted housing profile require
further refinement; component coverage is still partial. The first
flat-ended study's 0.01813 mm³ cotter contact was corrected by widening the
estimated hardware recess. Its failure receipt, original controls and views are
preserved in the study's diagnostics. A second, cupped but undersized-housing
native remains in the durable local work directory as a rejected intermediate.

The first housing STEP round trip preserved material and centroids but increased
the kernel's maximum edge tolerance slightly. Constructing the same rounded
window from one tangent line/arc profile, extruded once, replaced the previous
union of boxes and cylinders. Focused comparisons show zero added or missing
native material, and both housing STEP tolerances then satisfy the original
bounds. No physical fit or validation tolerance was changed. The diagnostic
includes the rejected and corrected housing BReps and the focused reproducer.

See the [source comparison gallery](../experiments/drive_chains/engine_lower_drive_study/source_review/index.html),
[independent checks](../experiments/drive_chains/engine_lower_drive_study/independent_checks.json)
and [STEP checks](../experiments/drive_chains/engine_lower_drive_study/exchange_checks.json).
