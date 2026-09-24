# Segmented transmission brake bands — 24 September 2026

`PowertrainWithBrakeBands.FCStd` adds **eight steel half-bands, 24 lining
segments and 216 copper rivets** to the qualified brake-suspension development
assembly. It contains **2,759 physical occurrences, 471 shared definitions and
268 assembly containers**. Two existing drum definitions acquire revised outer
friction lands; all inherited occurrence frames and ownership remain fixed.

The installation remains incomplete: band end ears, anchors, links, adjustment
mechanisms and support fastening are still required. Standard tank011 is
unchanged. These are physical CAD solids in the development assembly, not a
completed brake installation or a qualified historical production drawing.

## Source configuration

The selected arrangement follows the earlier handbook. HB207 lists four M344
low-speed half-bands, twelve M346 lining segments, four M349 track half-bands
and twelve M351 lining segments. HB97/98 dimension each lining segment and show
nine countersunk holes. Three segments fit each half-band; their hole pattern
requires 216 installed rivets across the four brakes.

The later SNL1928 arrangement lists four long MX108/MX107 lining strips for each
brake type, with different copper-rivet quantities. Each later stock length equals
three handbook segments plus 6.35 mm. These are retained as alternatives in
`../sources.json`; the model does not install both configurations. Applicability
of the selected handbook arrangement to every first-100 production tank is not
independently established.

| Printed control | Low-speed, HB97 | Track, HB98 |
|---|---:|---:|
| Inner friction radius, interpreted from arrow | 298.45 mm | 304.8 mm |
| Lining width | 95.25 mm | 69.85 mm |
| Segment length when flat | 301.625 mm | 306.3875 mm |
| Longitudinal hole pitch | 88.9 mm | 90.4875 mm |
| Lining stock | 7.9375 mm | 7.9375 mm |
| Hole diameter | 7.14375 mm | 7.14375 mm |

HB98/SNL119 explicitly support the 5/16 inch lining stock; it is applied to both
types. Both figures show 11/16 inch end margins and 5/8 inch edge margins. A
ninth hole occupies the center of the first column. The 1/8 inch section callout
is interpreted as the remaining straight stock at the outer face. HB97 gives
a 70-degree countersink; applying that angle to the track lining is an assumption.

Flat stock length is retained at the lining's middle radius. Estimated controls
include 6.35 mm steel stock, 3.175 mm axial overhang, 1 mm segment seams, 1.5 mm
terminal margins and the split clock/gap. These controls need regeneration;
they are not live expressions in the saved FreeCAD feature tree.

Copper rivets borrow the later SNL quarter-inch by 1⅛ inch stock as an explicit
estimate for this earlier configuration. Countersunk heads sit 0.5 mm below the
friction surface. Estimated spherical-cap upset tails conserve the unformed
shank stock volume and seat on shallow outer spotfaces. Head and tail forms,
clearances and spotfaces are reconstruction choices.

## Receiving drum correction

The printed lining radii expose a conflict with earlier source-scaled drums:
the low-speed friction radius was 288.834286 mm and the track radius was
303.348571 mm. The revised lands use the printed 298.45 and 304.8 mm values.
The larger low-speed correction exceeds the earlier scaling allowance and is
recorded as a source-driven revision, not hidden as a fit clearance.

Only outer stock is added. Every old material region and internal void, both
0.5 mm end strips, the shaft axes, body placements and existing end interfaces
are retained. New friction lands extend 2 mm beyond each lining edge. Their
connecting conical shoulders are estimated; these profiles have no recovered
manufacturing dimension. The standard geometric state has lining/drum contact;
release and actuation poses remain deferred.

## Validation records

`independent_checks.json` contains **154 passing native/context checks**. They
cover the saved identities and hierarchy, all prior frames, printed radii,
widths, arc lengths, hole stations, countersinks, stock, old receiver material
and voids, full backing/friction contact and seated rivet heads/tails. Filled
bores, displaced lining faces and lifted rivet heads are rejected controls.

All **1,090 nearby development material pairs pass**. Filtering all 5,316
retained standard-context occurrences finds no possible pair with the affected
parts. This scope does not establish complete-tank interference qualification.

The original `exchange_checks.json` deliberately retains its default-centroid
failures. Its **259 comparisons** pass material differences in both directions,
validity and kernel tolerances. The acceptance record for mass and the combined
exchange result is **`exchange_adaptive_checks.json`**. It binds those completed
material checks to unchanged native and STEP hashes, then remeasures every
definition/occurrence at two adaptive integration precisions. All **259 combined
comparisons pass**. Net integrated volume differences remain recorded diagnostics;
the original missing-material, added-material, centroid and tolerance criteria
govern acceptance. The additional rejected net-volume diagnostic and centered
replay are retained under `diagnostics/adaptive_mass/world_coordinates/`.

Two measurement diagnostics are preserved under `diagnostics/`:

- Cylindrical contact faces with complete coincident coverage acquired slightly
  different area estimates after re-trimming. Matching analytic supports and
  empty uncovered-face differences establish contact directly, with a 0.01 mm
  displacement rejected. The original failed report remains available.
- Default FreeCAD mass properties drifted on perforated curved bands. Adaptive
  OCCT Gauss integration converged for unchanged BReps; a Gauss-Kronrod probe
  independently corroborated the low-speed band. The adapter also passes a
  translated/rotated analytic sleeve, four brake round trips and four displaced
  centroid controls. No geometric tolerance or physical shape was changed.

All **464 unchanged inherited definitions** pass preservation: 446 exact BRep
matches and 18 strict material comparisons. A fresh nominal rebuild reproduces
all **1,439 BReps, 9,891 object types and 129,129 persistent properties**, including
assembly UUIDs, hierarchy and frames.

A variation adds 1 mm steel stock and 0.5 mm to each segment seam. It passes the
same 154 native checks and 1,090 development pairs. All 466 inherited definitions,
including the two revised receivers, retain their nominal BRep hashes. No
separate variation STEP qualification is claimed. Full variation/reproduction
natives remain under `.work/transmission-brake-bands/`; retained reports and
variation shapes accompany this checkpoint.

## Visual review and reproduction

The isometric, separate low-speed band detail and both handbook lining
comparisons were inspected directly. Source comparisons derive the curved
outline and flattened bore centers from saved native surfaces. They show
dimensional correspondence without claiming pixel registration. Missing ears
and linkage remain visible.

Four progression snapshots bring the collection to **174**, preserving all 170
earlier images and 28 recorded native baselines by hash. The full standard tank
remains unchanged.

Use the FreeCAD headless launcher with absolute paths and a fresh output folder:

1. `build_transmission_brake_bands.py --source <brake-suspension-trial02> --output <fresh>`
2. `pump_integration_worker.py extract --input <fresh>/PowertrainWithBrakeBands.FCStd --output <fresh>/isolated/manifest.json`
3. `check_transmission_brake_bands.py --candidate <fresh> --standard-manifest <standard-context-manifest>`
4. `exchange_transmission_brake_bands.py --candidate <fresh>` — the known default
   centroid failure is retained; verify its terminal result and completed report.
5. `check_transmission_brake_adaptive_exchange.py --candidate <fresh>` — requires
   the completed preceding report and installed matching OCCT headers plus `g++`.
6. Run `check_transmission_brake_band_preservation.py --candidate <fresh>` with
   ordinary Python, then `render_transmission_brake_bands.py` headlessly.
7. Rebuild/extract into a second directory and use
   `check_powertrain_frame_reproduction.py` to compare persistent saved contents.

The frozen builders, source packet, validation code and hashes accompany the
model. The mass adapter compiles locally; no compiled executable is a model
dependency. It records its source, header, runtime library and binary hashes.

Next: reconstruct band end ears and anchors, M337 suspension links, the M339
pin arrangement and adjustment mechanism, followed by support fastening and
remaining frame/hull mounting work. HB207/SNL251 give two M339 pins whereas SNL137
gives four; shared long pivots versus separate short pins remains unresolved.
The broader engine, interior inventory and final standard assembly remain open.
