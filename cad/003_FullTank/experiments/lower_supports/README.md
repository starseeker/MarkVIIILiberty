# Lower roller support installation experiment

This experiment develops the missing lower support installation against the
qualified idler-mount delivery. It writes a separate native FreeCAD document;
it does not change the delivered tank, source survey, milestone snapshots or
authored model inputs. Results are experimental until reviewed and promoted.

Run from the repository root:

```sh
python3 cad/003_FullTank/experiments/lower_supports/probe.py
python3 cad/003_FullTank/experiments/lower_supports/verify_native.py
```

The default `build/` output contains the native installation, native contact
and interference report, and software-rendered front/rear/bank views.
The experimental document stores separate support bodies and linked bolts in
four installation groups, with baked copies of the roller banks and hull for
review. It is not the modular delivery assembly.

The [source comparison page](comparison.html) and [inspected source hashes](inspected_sources.json)
record the visual review. The probe requires the current authored fingerprint
to match the delivered native baseline and records both input library hashes.

## Verified experiment result, 20 September 2026

The second trial has 34 single-solid angles and 76 linked single-solid bolts,
with all fourteen angle identities/counts reconciled to frozen SNL rows. Native
checks found no material overlap above 0.00001 mm³ among 1,502 candidate pairs,
including every externally affected component in the twelve rotated front
roller units. All 348 pin/washer faces and 76 bolt-head faces have zero gap within
0.000001 mm and nonzero bearing area. All 34 angles also meet an existing hull
face. Native contact area is a geometric check, not a strength calculation.

`build/reopened_checks.json` confirms the saved FreeCAD file independently:
110 new single solids, all 424 bearing faces, both occurrences of each printed
inner-support length, and rejection of a 0.2 mm displaced pin and bolt head.
The verifier runs without a GUI because its work only needs saved native solids;
the initial GUI verification attempt terminated with signal 15 before opening
completed, without a diagnostic cause. The headless reopen succeeded.

The first trial is retained in `trials/01_uniform_fasteners.json`: equal bolt
spacing produced 30 actual clashes, and a reflection through `transformGeometry`
converted planar faces to spline surfaces, causing 348 false missing-seat
reports. The second trial builds each extrusion directly in its installed
direction, preserving analytic planes, and moves the inferred attachment holes
within their runs. It preserves the catalogue bolt count and printed shank
dimensions. No geometry tolerance was relaxed to pass the checks.

## Evidence and working choices

SNL4:019–030 / 5:001–002 independently determine fourteen support identities
and 34 installed angles: sixteen outer and eighteen inner. Their A/B identities
exchange between the outer side and the opposite inner side. SNL31:001 allocates
76 half-inch × 7/8-inch hex-head bolts among those angles. The original page was
inspected: unlike the following entries, this row does **not** specify a nut
and washer. This supports investigating a tapped attachment, but does not prove
the receiving part, hole depth or thread form.

The handbook (original MarkVIII073.jpg, p.144) requires removal of plates on
the support angle before withdrawing a lower roller pin. No separate catalogue
identity has yet been established for those plates. This experiment must not
be described as a resolved removable-retention design.

The run-to-station allocation follows the hypothesis in
[the research packet](../../packets/R02-rollers-research.md). Runs 1–3 are
straight and inclined through paired installed pin centers. The entire roller
unit rotates around its transverse axis, preserving internal relationships;
the experiment checks external intersections of every affected component,
including springs and split rings.

Runs 4 and 8 have varying pin heights. The trial uses 120 mm horizontal seat
regions connected by cubic curves. These are explicit inferred formed shapes,
not original manufacturing contours. The two rear outline roller stations
remain especially uncertain as members of run 8.

The inner No.5 split uses M2176 for Lower12 and M2175 for Lower13–15. Their
printed lengths remain **168.275 and 822.325 mm**, separated by an inferred
4 mm gap. This tests a complete four-roller allocation without stretching either
part or treating the short angle as an unattached spare. The allocation is not
a source fact.

The wall plane follows the current **10 mm skirt** stock instead of the 12 mm
general side-wall offset. This addresses the 2 mm gap found in the earlier
front-angle experiment. Cross-section sizes are transferred from the provisional
upper angle: 34 mm flange, 6.35 mm stock, toe at 12 mm and washer seat at 50 mm
above the pin. The trial omits the inside root radius. Stock on cubic regions is
measured vertically; no constant normal thickness or manufacturing feasibility
is claimed for those transitions.

Attachment positions, 22.225 mm head across flats and 8.73125 mm head height are
inferred. The 12.7 mm × 22.225 mm shank follows the catalogue. Plain bores model
thread envelopes. A 6.35 mm angle plus 10 mm shell consumes 16.35 mm of the
shank; the remaining 5.875 mm does not accommodate the existing 11.1 mm full nut
plus washer. Adding those parts solely because they occur on other bolts would
create an unsupported and geometrically impossible stack.

## Promotion requirements

- Inspect all three native renders and compare their topology with SNL Plate 2
  and HB88/89/91. Keep visual disagreement visible.
- Resolve or document every native interference, lost pin/washer bearing face
  and missing hull seat. Check bolt bearing faces and useful receiving material.
- Resolve the angle/retention-plate ownership sufficiently to avoid counting
  alternative interpretations as simultaneous parts.
- Move accepted choices into typed parameters, source locks, assembly patterns,
  installation datums and source-scoped validators. Reuse interchangeably shaped
  definitions; keep geometric variants of a shared mark explicit.
- Run the affected interface trials and complete delivery qualification before
  advancing the numbered whole-tank snapshot sequence.
