# I03 — clutch plunger locking wire and receiving heads

Status: accepted approximate for continued clutch development, 22 September 2026.
Configuration: Rock Island first 100, standard assembled geometry. Parent is the
qualified 1,652-component cone/spring checkpoint `0f57d0d`. This packet adds one
SH861K wire and drills the shared SH861A plunger definition. Six existing links
receive tangential bore clocking; the other 1,646 occurrences remain unchanged.
The resulting isolated transmission/pump candidate contains 1,653 physical
components. These counts are not additive to the standard tank inventory.

## Evidence and approximations

Original catalogue pages 157 and 275 and full SNL Plate 21 were inspected.
The source dossier freezes three survey records and four original image assets.

| Feature | Source | Reconstruction decision |
| --- | --- | --- |
| Wire identity and count | SNL275:024 SH861K, one piece for SH861A | One installed wire, owned by the existing spring-set container. |
| Cut length and material | Soft iron, W.&M. Ga. No16, length30in | Centerline length762mm. Diameter1.5mm is explicitly estimated; no verified gauge conversion is claimed. |
| Spool allocation | SNL275:023 includes one 30in length for clutch spring plunger | Corroboration of the same wire, not another installed component. |
| Plunger quantity | SNL157:018 SH861A, six; Plate21callout5 | Reuse one definition and six native links. No replacement or duplicate plungers. |
| Head passages | Necessary receiving interface; route not resolved by Plate21 | Tangential2.7mm bores through the middle of inherited4mm heads. Axial wall stock0.65mm. Size and clocking are estimates. |
| Wire route | No measurable source routing | Near-circular route through all six heads, paired1.5-turn twisted ends in the0degree gap; inferred bends and clearances. |

The native assembly retains the inherited conditional handbook dimensions and
spring-length conflict. Wire retention is represented geometrically, without
qualifying locking strength, forming strain, spring loading or historical fits.

## Frames and parameter behavior

Units are millimeters. The existing TransmissionCore origin and hierarchy remain
unchanged; local X points toward the engine. Plungers lie at radius114 and phase
30degrees. Their tails start at X897.475; head wire plane is X1019.3. The shared
plunger's bore center is local X121.825, parallel to local Z. Each occurrence
rotates about X so its bore is tangent to the pitch circle.

The wire has one interpolated B-spline centerline, split into eight sweep spans
to retain a valid continuous solid. Length is solved by adjusting the paired
tail's axial length, nominally17.538mm. The bridge advances10mm from the head
plane; the tail reaches approximately X1046.84 before its section radius. That
projection must be checked against the future flywheel and crankshaft geometry.
The current packet does not establish a fit to those missing parts.

Authoritative controls, source dossier and geometry scripts live under
`experiments/drive_chains/clutch_retention_*`. Parameter changes require
regeneration; native metadata does not constitute a live expression dependency.
The source-specified length stays fixed while wire diameter, hole size and seam
orientation can change within the documented trial range.

## Validation

The saved native passes 84 independent checks, including actual bore-axis lines,
small void witnesses, wire material through every head, three-point frame
witnesses, preserved shafts, unchanged parent occurrences, and an intentionally
misaligned wire that must strike each head. All 68 affected material pairs clear
the existing transmission/pump and standard tank physical context. Standard
layout envelopes are not treated as finished physical parts.

Two local definition and seven installed STEP solids pass explicit-accuracy
mass, centroid and two-way material comparisons. Two saved parameter trials use
1.4/1.6mm wire,2.5/2.9mm bore diameter and an alternate60degree seam. Each passes
22 independent checks and 68 material pairs. A fresh build and independent checker
repeat the nominal result from the unchanged qualified parent.

The larger trial initially missed the0.05mm3 wire-volume criterion because the
default spline-volume quadrature was about0.055mm3 high. Explicit-accuracy OCC
integration reduced the discrepancy from the theoretical circular-section sweep
volume to about0.0004mm3. The original criterion was retained; this was a numeric
measurement correction, not permission for extra material. Original failed
reports and the checker are retained under `diagnostics/` with the accurate
integration results.

Five native/source images were inspected by the primary Codex agent. Three new
progression snapshots preserve the installed view, six-head wire route and head
section. All 92 earlier images and all 20 standard native files are preserved.

## Artifacts and remaining work

- [Native assembly](../experiments/drive_chains/clutch_retention_build/TransmissionWithClutchRetention.FCStd)
- [Qualification](../experiments/drive_chains/clutch_retention_build/qualification.json)
- [Source and geometry review](../experiments/drive_chains/clutch_retention_build/source_review/index.html)
- [Independent checks](../experiments/drive_chains/clutch_retention_build/independent_checks.json)
- [Parameter trials](../experiments/drive_chains/clutch_retention_build/variants/report.json)

Next: SH866A outer clutch drum, six SH866B screws and SH866C48in wire, then the
SH868A flywheel/key/screws and crankshaft engagement, clutch-stop brake and further
engine/drivetrain work. The flywheel's catalogue callout conflict remains open.
Standard tank integration, remaining interiors, complete coverage reconciliation
and later selected poses are required before the full goal can be complete.

Rebuild from the repository root:

```sh
python3 cad/003_FullTank/experiments/drive_chains/clutch_retention_sources.py
python3 cad/003_FullTank/experiments/drive_chains/clutch_retention_build.py
python3 cad/003_FullTank/experiments/drive_chains/check_clutch_retention.py
python3 cad/003_FullTank/experiments/drive_chains/check_clutch_retention_variants.py
python3 cad/003_FullTank/experiments/drive_chains/render_clutch_retention_review.py
```

Qualification additionally requires a fresh build/check, recorded source and
visual inspection, and preserved progression images bound to the actual files.
