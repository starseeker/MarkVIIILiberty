# I03 — clutch cone, lining and spring-plunger sets

Status: accepted approximate for continued clutch development, 22 September 2026.
Configuration: Rock Island first100, standard assembled geometry. Parent is the
qualified1,581-component clutch thrust checkpoint8e793e6. This packet adds71
physical occurrences and refines/reparents the existing SH869A support. It does
not add a second support or count the catalogue cone assembly heading as a solid.

The nine new definitions are SH876A cone, SH997C lining, Q52A plug, two rivet
families, SH861A plunger, SH861C spring cup, SH861F spring and SH849C rear ring.
Installed counts are1,1,1,6,43,6,6,6,1 respectively. The support belongs to the
native cone container; spring sets have their own installation container under
TransmissionCore. All installed repeated hardware uses shared definitions.

## Evidence and interpretation

Original full SNL21, HB71/72 and catalogue pages68,157,164,165,167,219 were inspected.
The source dossier binds these assets and12survey records; the survey is unchanged.

| Feature | Evidence | Decision and uncertainty |
|---|---|---|
| Cone and lining | HB115 diameters19.186/17.887in, face2.5in; HB117 developed radii36.924/34.424in, angle93deg31min36sec, section2.5x.25in | Conditional HB-to-SNL transfer. The pattern independently reproduces diameters within.015mm. Listed diameters are selected at finished friction face;2.5in is slant width. |
| Expanded length | HB11558.5in | Mean circumference from diameters is58.234in,6.753mm less. Retain discrepancy; do not distort the supported cone surface. |
| Cone attachment | SNL68six5/16x1-1/8 button rivets; SNL167 allocation toSH869A6 | Six inclined rivets with actual drilled joint. Catalogue total24includes unrelated plates/flanges. |
| Lining attachment | SNL68forty-three3/16x11/16 countersunk copper rivets |43 installed;22+21 staggered rows inferred. Nominal length is blank stock, not installed upset shank length. Head/seat forms estimated. |
| Spring set | SNL21callouts5,6,7,8; sixSH861A/C/F, oneSH849C | Long plunger spans stop ring to separate rear ring; spring runs from rear ring to cup, cup bears on support. Six inferred threaded tail envelopes attach the ring. |
| Plungers | HB1154-7/8in long,3/8diameter | Length selected overall including inferred head; sameSH861A mark. |
| Springs | HB1155/8diameter,32coils,5.85in length; SNL2194-5/8in free length | Source free lengths conflict and HB spring mark differs. Diameter selected asOD; wire1.6mm inferred. Installed length77.475mm comes from seats. Ground end geometry is an approximation. |
| Support | SNL21callout9, SH869A already modeled | Preserve keyed inner running region, except new oil port; reconstruct outer cup bores and inclined rivet seat. Profile stock/contour estimated, not calibrated. |
| Plug | SNL68Q52A square-head1/8in pipe plug | Nominal size does not set physical diameter. Location, tapered envelope and passage estimated; actual receiving hole provided. |

HB115 names conflicting lining materials in different passages. This geometry does
not claim to resolve that identification. Relative scan proportions guide topology
and arrangement, not metrology. Source and native sections use opposite horizontal
orientations and independent scales, explicitly labelled in the comparison.

## Parameters and interfaces

Authoritative inputs are `experiments/drive_chains/clutch_cone_controls.json`,
`clutch_cone_sources.json` and `clutch_cone_parts.py`; the native builder is
`clutch_cone_build.py`. Controls document printed transfers, estimates and useful
bounds. Updating these inputs requires regeneration; metadata is not a live
parametric dependency graph.

Coordinates remain millimeters in TransmissionCore, X forward. The parent keyed
bore, thrust race, ball/cage mechanism and stop ring retain their existing shapes.
Six plungers use the stop ring's114mm pitch radius and30degree phase. Plunger head
seats atX1017.30; tail begins897.475. Rear ring ends903.475; spring cup seats980.95.
Cup guide clearance.10mm and plunger clearance.15mm are physical allowances.
Rivet radial clearance.025mm, shallow flat seats.2mm and head-seat allowance.05mm
are finishing assumptions, separate from numerical Boolean tolerance.

The cone uses analytic conical faces, a tangent circular pressed bend and a
revolved dished web. The spring is a swept, retained interpolated centerline with
32turns and independent ground ends. Retained controls identify the sampled curve
and imposed pitch; it is an approximate wire path, not recovered spring design.

## Checks and current disposition

The initial connected trial revealed a short cup drilling and a cone inner-edge
lip overlap; both receiving features were corrected. A later independent material
witness exposed two faulty rivet cuts even though whole-part common-volume checks
returned zero. Cutter construction was revised to single revolved profiles and
explicit finishing allowances; acceptance additionally requires all43hole axes
to pass through without intersecting the cone, and the result to be a material
subset of its uncut blank. Failed candidates and diagnostics are retained.

Spring B-spline bounding boxes extend beyond their trim planes. Actual ground
planes, positive contact and zero material outside the two seats determine the
installed extent. The conservative bounds are retained as diagnostics, not
silently treated as actual material.

Independent saved-artifact checks, native/STEP exchange, source/visual review,
coupled parameter variation and fresh regeneration are required before acceptance.
The final revision passes 462 independent checks, 326 material pairs, ten
definition and 72 installed STEP comparisons, two coupled parameter trials and
a fresh rebuild. Seven native/source views were inspected by the primary Codex
agent. Qualification accepts this approximate geometry for further development;
it does not claim completion of the clutch or tank. Full clutch, loading, manufacturing fits and tank
integration remain unqualified. Next dependencies: flywheel/outer drum, crankshaft
engagement, SH861K plunger locking wire (SNL275:024, one30in length),
clutch-stop brake, then broader drivetrain/engine integration. The six spring sets
are not complete retention assemblies until that wire and its receiving head
holes are added.


## Accepted artifacts

- [Native assembly](../experiments/drive_chains/clutch_cone_build/TransmissionWithClutchCone.FCStd)
- [Qualification](../experiments/drive_chains/clutch_cone_build/qualification.json)
- [Source and native review](../experiments/drive_chains/clutch_cone_build/source_review/index.html)
- [Independent checks](../experiments/drive_chains/clutch_cone_build/independent_checks.json)
- [Retained failure diagnostics](../experiments/drive_chains/clutch_cone_build/diagnostics/receipt.json)

STEP matching now caches candidate centroids/volumes instead of reintegrating
the same spline solids for each pairing search. Explicit mass, material and
centroid acceptance criteria are unchanged.
