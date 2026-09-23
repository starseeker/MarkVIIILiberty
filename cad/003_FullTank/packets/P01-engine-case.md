# P01 / I01 — Liberty engine crankcase castings

Status: **verified development checkpoint; historical geometry remains provisional**, 23 September 2026.
The complete-tank target remains all identifiable installed components, including
interiors, before pose development. This packet extends the
[engine suspension](I01-engine-suspension.md) with the upper and lower crankcase
castings and tests the earlier support estimates against their material.

## Scope and evidence

The [source dossier](../experiments/drive_chains/engine_case_sources.json) retains
71 literal catalogue records, 20 hashed source assets and relevant handbook/manual
prose. SNL57–59 originals were inspected along with SNL14/15, HB43–45 and Liberty
figures14–17,93,96,105. The two castings are LQ207A / D12035 upper and
LQ180A / D12036 lower. Catalogue case assemblies also include separately owned
bearings, bolts, studs, pipes, plugs and fittings. Those quantities must not be
absorbed into the two casting occurrences.

The saved candidate has **1,911 physical occurrences**: 1,909 inherited and two
castings, under PowerplantDevelopment / TankLibertyEngine / EngineCrankcase.
Seven support occurrences change: both rail definitions, the front yoke and cleat,
and placements of the three front-pivot fastener pieces. All other1,902 inherited
occurrences retain their shapes and placements. Candidate totals include contexts
and cannot be added to the standard tank inventory.

The case construction follows the source's two hollow castings, lapped horizontal
joint, integral main-bearing saddles, eight upper cross webs (two nose, five
windowed intermediates, one distribution-end web), twelve cylinder openings,
separate dry distribution-gear chamber and lower oil trough/wells. The lower
bearings are carried in the casting, rather than in invented detachable caps.
Cubic lower-section control poles and degree are retained in the build datums.
Their smooth surfaces are controlled approximations, not measured source fits.

HB45's engine prose gives5in bore,7in stroke,2.625in crankshaft diameter and seven
main bearings; its footnote warns that much engine material is aviation-derived.
LIB specifies a45-degree V. HB44 supplies6.5in pitch and a6-21/32in output-nose
extension beyond the adjacent mounting row. These are **conditional transfers**.
The11-37/64in dimension at the opposite end includes external equipment; it is
not treated as the length of the casting's gear chamber.

Two conflicts remain explicit:

- SNL58 lists six long and one short **lower** main-bearing halves, while SNL59
  lists one long and six short **upper** halves. The physical sources and Liberty
  description favor matching halves with one long nose bearing. Inserts remain
  pending identity reconciliation; no silent correction is made to the survey.
- The tank catalogue allocates six3/8 ×2in mounting sets per rail, versus seven
  aviation positions. Seven casting stiffener stations are represented, but the
  unassigned engine mounting holes and hardware have not been invented.

LIB figure96 is captioned “Oil Pump removed” on printed129; it shows the large
opening beneath the lower case. It is not a photograph of the exposed upper
casting. The130mm pump receiver diameter here is an estimate informed by that
view, not a printed dimension.

## Geometry and revised interfaces

The output end faces tank−X toward the existing flywheel; the distribution end
faces+X. The joint/shaft plane retains Z849.233510mm. Axial placement begins5mm
beyond the existing flywheel's forward bound, X2901.805551mm. That clearance and
the mapping of the nose-end datum remain provisional pending crankshaft/thrust
reconstruction and source registration.

| Controlled approximation | Selected geometry |
| --- | --- |
| Case stock | 8mm shell,9.525mm joint flanges,12.7mm webs. |
| Upper body | 348mm nominal width,240mm center roof height, planar V-bank seats with estimated spigot clearance. |
| Lower body | Controlled cubic side/bottom sections,165mm pan depth,190mm central trough;215mm forward well and220mm gear-end well depths. |
| Mount flange | 478mm overall at the principal engine rows; seven rib pairs per side. |
| Main receivers | Source2.625in shaft plus estimated3.175mm insert stock; one extended nose seat and six shorter seats. |
| Gear compartment | Estimated125mm beyond the last row, separating floor at46mm, four roof apertures and oil-trap passage. |
| Remaining features | Stud receivers, nut-access windows, oil galleries, filler connections and pump openings are approximate interfaces awaiting their mating parts. |

Installing the corrected lower casting produces **90,652.20mm³ of overlap**
with the previous estimated front yoke. The candidate reduces the central hub
height62→30mm, lowers its longitudinal pivot16mm, and drops each connecting arm
25mm below the former straight contour at Y±120mm while retaining the rail seats
and source-sized mounting hardware. The front
cleat receives the corresponding upright/hole revision. Both rails extend60mm to
X4120 so the transferred mounting rows lie within their length. These are explicit
revisions to uncertain support geometry, not new historical dimensions.

## Verification and review

The first candidate is retained as a rejected trial. Independent checks found
23,545.41mm³ of residual interference after lowering only the hub, a curved trough
wall narrowing to1.979mm despite its8mm control, and a breather passage cutting
into the last main-bearing web. The revised candidate drops the yoke arms,
insets the inner trough control poles in both Y and Z, and confines the breather
and inclined-shaft apertures to the gear-chamber roof. The dry floor retains its
separate vertical-shaft and oil-trap passages. No numerical tolerance was relaxed.
Two checker issues were also corrected: trimmed casting bounds are measured with
`optimalBoundingBox`, and the front pivot head seats on the cleat.

The saved native model passes **191 independent checks and71 affected material
pairs including standard-tank context**, with no overlaps. The curved section's
minimum separation is8.0mm; lower-casting/front-yoke clearance is4.392248mm.
Checks cover actual material and voids, twelve analytic spigot receivers,
bearing/stud passages, joint seating, revised fastener receivers, ownership and
preservation of all1,902 unaffected inherited occurrences. **15 STEP comparisons**
pass: six definitions and nine installed shapes, comparing material in both
directions, mass and centroid without increasing tolerances.

A coupled trial changes case wall8→9mm, deck height240→246mm, pan depth165→168mm,
trough depth190→193mm, gear well220→225mm and main-seat width38.1→40mm. It passes
**191 independent checks and71 material pairs including standard context**.
Printed constraints and support hardware remain fixed. Variant STEP and fresh
nominal reproduction have not been checked; combined qualification remains open.

Eight native views, the source crop and the fixed SNL2 overlay were inspected in
the [review bundle](../experiments/drive_chains/engine_case_build/source_review/index.html),
alongside Liberty figures14–16 and tank plates14/15. The views expose the hollow
castings, integral webs and bearing seats, cylinder openings and sump/support
relationship. Profiles are approximations and the projection is not fitted to
the drawing; engine/flywheel registration remains unresolved.

The [checkpoint receipt](../experiments/drive_chains/engine_case_build/development_checkpoint.json)
ties the native file, checks, source review and parameter trial to their hashes.
New [installed isometric](../../intermediate_snapshot_iso_engine_case_001.png),
[upper casting](../../intermediate_snapshot_detail_engine_case_upper_001.png) and
[lower casting](../../intermediate_snapshot_detail_engine_case_lower_001.png)
snapshots bring the progression to120. All117 prior images and20 standard native
files are preserved. The two additions are partial physical castings, not complete
catalogue case assemblies or a completed engine.

OCC7.8 fails same-domain face unification on the otherwise valid upper casting.
The builder records that event and retains the original valid single-solid BRep;
it does not heal it or inflate tolerances. STEP export explicitly retains surface
trimming curves, following the suspension's independently diagnosed exchange issue.

```sh
python3 cad/003_FullTank/experiments/drive_chains/engine_case_build.py
python3 cad/003_FullTank/experiments/drive_chains/check_engine_case.py
python3 cad/003_FullTank/experiments/drive_chains/check_engine_case_exchange.py
python3 cad/003_FullTank/experiments/drive_chains/render_engine_case.py
```

The builder accepts `--output` and `--controls`; checkers and renderer accept
`--candidate`. Geometry requires regeneration. Standard tank011, its transparent
view and the qualified drivetrain baseline await combined qualification/integration.
The source identity conflicts, case-joint and cylinder hardware, bearing inserts,
crankshaft/thrust interfaces, complete engine internals and mounting joints remain
open work. These two castings do not constitute a complete engine.
