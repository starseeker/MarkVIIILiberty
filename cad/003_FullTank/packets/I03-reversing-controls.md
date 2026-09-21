# I03 — reversing fork, rod and detent

Status: qualified partial reconstruction; all local qualification checks pass.
Standard tank011 remains unchanged. This packet continues the complete-tank
workflow; the vertical control shaft and its linkage follow this increment.

## Source and quantity scope

SNL95 and HB207 identify one M301 fork. SNL215:023–027 owns one M302 rod, one
M314 castle nut and one 3/16 × 2 inch split pin in the rod assembly. SNL254 owns
one M307 plunger, M308 spring and M309 cap. The listed spring OD is 11/16 inch
(17.4625 mm), with 1.5 inch (38.1 mm) free length. The catalogue's global spring
quantity two and global M314 nut quantity nine are not transmission allocations.
One of each is installed here. The assembly identity belongs to its container;
the component identities belong only to the physical leaves.

The original SNL95,215,254 photographs and HB121/123 drawings were inspected.
The inherited SNL23 registration remains fixed: 0.921141975 mm/pixel and cross
shaft origin [579,493]. The approximate rod-axis pick [776,320] places it at
local X−181.465,Z159.358 mm. This is a conditional picture measurement, not a
manufacturing dimension. HB119/120 selects the right/starboard bevel wheel for
ahead motion. The clutch center therefore remains Y−16 mm.

## Geometry and ownership

`TransmissionCore/ReversingControl` owns the fork and three detent parts, plus
`ReversingRodAssembly` with rod, nut and pin. Six new definitions provide seven
occurrences: M314 reuses the existing small-planet nut definition. The repaired
analytic cotter generator supplies two complete legs and a joined eye; the older
swept cotter definition is not reused. Other older pin definitions are outside
this packet's qualification.

The fork uses circular contact surfaces and cubic B-spline arm profiles. Its
hub is clamped between the rod shoulder and M314 nut. The shaft includes three
detent pockets and a provisional outer linkage hole. M263 gains an integral
journal boss, vertical detent tower, bored passages, hub-access relief and cap
spotface. M307 seats in the selected rod pocket. The hollow M309 cap retains a
separate helical spring with ground ends. Installed height 28 mm, wire 1.6 mm,
pitch 4.4 mm and six nominal active intervals are estimates. Quarter-turn end
allowances are trimmed at the seat planes. Free length is recorded separately;
neither spring rate nor preload is qualified.

The initial fit exposed an inherited clutch construction defect: its four lugs
had been fused after the fork groove was cut, blocking that groove. This packet
cuts the continuous groove last, leaving the shaft splines, disk and forward
station unchanged outside that band. The mating ring dogs also reached into the
fork path. Both hands share the revised ring definition, with their inferred
15 mm lugs shortened to 12.5 mm. Ahead engagement retains 10.85 mm of axial flank
overlap; torque capacity and shifted poses are unqualified. The fork's thick
arm starts outside the 98 mm rotating lug envelope with 1 mm radial clearance.

Additional failed trials found fork-hub/cotter contact with the case and a cap
head partly buried in the casting. Bounded local relief and a flat spotface
resolve these interfaces without moving the source-picked rod axis. Initial fit
reports and renders are retained under the candidate's `rejected_trials`.

## Qualification and reproduction

Run from the repository, in this order; the last three commands may run
independently after a passing build:

```
python3 cad/003_FullTank/experiments/drive_chains/transmission_reversing_probe.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/check_transmission_reversing.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/check_reversing_variants.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/render_transmission_reversing.py --stage cad/003_FullTank
```

The saved candidate contains 1,372 valid single-solid leaves: seven new, four
revised and 1,361 unchanged. The revised occurrences are M263, the sliding
clutch and the two shared-definition clutch rings. All 168 affected material
pairs have zero overlap. Eleven native/STEP comparisons have zero raw and
bounded added/missing material. Fifty interfaces are freshly checked; 621 are
retained against unchanged parent geometry. The three local parameter trials
vary fork width to 4.8 and5.7 mm and spring height to 26 mm with a raised lower
seat. They test 11 local solids, not the complete tank's parameter space.

Independent checks use a full annular fork-passage witness, retained material
outside bounded revisions, rod bearing support, both cotter legs, nut capture
and spring seats. Negative controls use the obstructed parent clutch/ring and
an axially displaced fork. Rendering reads the saved native document and uses
the fixed source registration without warping. Visual comparison led to a wider
upper arm using three additional conditional source picks. The lower opening,
hub contour and transverse depths remain estimates.

All 63 independent checks pass. The first spring checks incorrectly treated a
conservative B-spline control-hull bound as its material envelope and counted
unconnected section edges as wires. Exact tangent-cylinder subtraction also
returned inconsistent results, including negative volume. The final checks
measure the two saved ground faces, sort meridian edges into 13 closed wires,
sample exact boundary curves and test containment with an explicitly documented
0.0001 mm radial allowance. The sampled OD differs from nominal by about
0.000022 mm. No native BRep tolerance was changed. Failed checks and their exact
scripts are retained. A separate very fine tessellation diagnostic was stopped
after the direct boundary checks resolved the question; it is not qualification
evidence.

Six final native renders were visually inspected. Three new progression images
preserve the open isometric, mechanism and detent section. Twenty standard CAD
files and 52 previous snapshots remain byte unchanged. Use
`transmission_reversing_build/qualification.json` for the combined status; the
generation report remains an immutable receipt with rendering incomplete at
the time it was written. This remains an isolated component increment, not
standard tank012.

## Remaining work

M303/M304 levers, M305 shaft, two M306 bearings, two No.C Woodruff keys, two MX11
bolt sets and two MX12 stud sets remain. They must not be collapsed into a
single attachment type. The outer M302 linkage hole remains provisional until
that assembly is developed. Then continue case mounting, pump/support
installation, brakes, lubrication and frame/hull integration. The all-identifiable
interior goal and standard tank geometry remain incomplete.
