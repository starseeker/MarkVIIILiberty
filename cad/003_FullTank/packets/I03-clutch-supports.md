# I03 — clutch supports and auxiliary controls

The subsequent [brake-linkage checkpoint](I03-clutch-brake-linkage.md) adds the
remaining stop-brake inventory and revises the left bracket's receiving lugs.
The results below describe this preserved support checkpoint.

Status: **development hypothesis; incomplete and not qualified**, 23 September 2026.
This continues [the throwout packet](I03-clutch-throwout.md). Standard geometry
and all identifiable interiors remain the priority; the full-tank goal is active.

## Geometry and ownership

The candidate adds 27 mechanism pieces: M4148 and SH953A brackets, their eight
cap screws, the M4162 cup-point setscrew, SH953C auxiliary shaft, two SH953B
levers, two shared M4172 keys, two taper pins, SH953D rod, two nuts, two SH953E
forks, two SH953F pins and their two split pins. Each SH953F catalogue assembly
contains its split pin; those children are not extra catalogue assemblies.
The two auxiliary keys reuse the existing M4172 definition, bringing the main
and auxiliary installed total to five. SH953C is counted once despite its
appearance both in the throwout list and the left-bracket assembly.

The isolated assembly also carries a **replacement development copy of M1937
floor plate 7**, with eight clearance holes. It must replace that floor at eventual
integration, never become a second installed plate. All standard tank files remain
unchanged. The local assembly count is not additive to the tank inventory.

M4150 receives an estimated cup-screw seating flat and loses an unsupported hole.
M4164's operating arm now points rearward and downward; its shaft hub and keyed
receiver are retained. The other 1,756 inherited occurrences retain their geometry
and placements under independent preservation checks.
Builders retain the native hierarchy, shared definitions and installed
placements. JSON changes require regeneration; metadata is not a live expression
network.

## Source correction and mounting hypothesis

SNL134 lists the 5/32 × 1in split pin inside the M4165 bell-crank pin assembly.
SNL141 accounts for three such pins: two for another named pin and one for M4165.
Neither assigns it to M4150. The separate mention in SNL250 is provisionally
reconciled as a repeated nested component. The prior main-shaft assignment and
its receiving hole are withdrawn; the pin remains required in the pending brake
bell-crank joint. This avoids changing the shaft diameter to accommodate an
incorrectly assigned fastener.

SNL200 specifies four 1/2 × 1-3/4in cap screws for M4148; SNL201 specifies four
5/8 × 1-7/8in screws for SH953A. The selected development mounting has their heads
**beneath the floor**, with their shanks passing through real floor openings into
blind bores in the cast bracket bosses. This is an engineering hypothesis, not an
established historical detail. There are no assumed threads in the 6mm floor.
Boss heights, stock, hole patterns, screw head dimensions and thread clearance
are reconstruction estimates. Thread forms are nominal envelopes.

SNL175/184 explicitly join rear engine channel M180 to M1937 and front channel
M181 to M1936. This provides a future frame attachment chain, but does not prove
that the clutch brackets mount on those channels. HB159 and the inspected museum
photographs leave the relevant bracket joint obscured. Attachment to the engine
frame remains an alternative. The current floor holes and bracket feet are subject
to revision when the frame and engine are reconstructed.

## Auxiliary arrangement and source comparison

In full SNL Plate 2, the engine is to the left and the transmission to the right.
The controls are represented toward the transmission: the auxiliary shaft lies
260mm rearward and 25mm above the main shaft; M4164's eye is 100mm rearward and
40mm lower. The auxiliary lever eyes lie 65mm below their shaft, giving a horizontal
160mm eye-to-eye rod in this static installation. These are **estimated dimensions**,
not a traced or dimensioned reproduction of the drawing. Main-shaft height still
inherits the conditional source measurement from the preceding packet; its axial
registration and the complete clutch length remain unresolved.

The early trial placed the controls on the engine side and its inward lever
intersected the flywheel, outer drum and cone. A second, unvalidated trial moved
the auxiliary journal outward. Full-source review then corrected the longitudinal
direction and the inherited operating-arm orientation, eliminating the reason
for that outward jog. Both trials are retained locally. A passing clearance result
alone would not have exposed the source-direction error.

SNL37/142 specifies No6 × 3in taper pins, while HB188 lists 2-3/4in. The SNL length
is selected. The 0.341in large end and 1:48 diameter taper are a conditional transfer
from the modern [Lawson product specification](https://www.lawsonproducts.com/products/ansi-b18-8-2-taper-pin-steel-6-x-3-11541).
End finish is simplified. SH953F's printed 1-7/8in length is interpreted under the
head; that convention and its 16mm shank diameter remain assumptions. Each fork
joint includes the source 1/8 × 7/8in split pin, formed with a retained leg-length
budget. SH953D has the two source 3/4in nuts; fork shape, socket depth, nut profiles
and rod length are estimated.

The first split-pin construction passed native solid validity but failed STEP
material and centroid comparisons. The retained analytic cylinder/torus helper
passes the focused definition and two-orientation exchange probe. No acceptance
tolerance was relaxed. The full-candidate exchange and interface checks now pass;
this is a verified development parent, with historical qualification still pending.

## Saved checkpoint and validation

The [native assembly](../experiments/drive_chains/clutch_support_build/TransmissionWithClutchSupports.FCStd)
contains **1,786 physical occurrences**: 27 new mechanism components, one replacement
floor context, two revised parent parts and 1,756 unchanged inherited occurrences.
The floor is included in this local count and must not be counted twice at integration.
Fourteen new definitions include that floor; two auxiliary keys reuse a parent definition.

| Check | Result and scope |
| --- | --- |
| Independent saved-native checks | 117 pass: source sizes, real bores and stock, seats, ownership, inherited preservation and placement. |
| Affected material pairs | 88 pass, including existing standard-tank context; no unintended overlaps. |
| Native/STEP comparison | All 16 definition and 30 installed comparisons pass. |
| Coupled parameter trial | 117 checks and 78 local material pairs pass with changed auxiliary-axis offset/height, lever eye height, boss height and web stock. Full standard context and STEP were not checked for the trial. |
| Visual review | Five native views inspected against full SNL2 and the retained clutch crop. This is qualitative review, not a calibrated historical fit. |
| Preservation | All 20 standard native files and 105 earlier progression images retain their hashes. |

The [checkpoint receipt](../experiments/drive_chains/clutch_support_build/development_checkpoint.json)
links the exact native hash and validation receipts. The
[source comparison](../experiments/drive_chains/clutch_support_build/source_review/index.html)
includes isometric, support, auxiliary, underside and side views. Current spacing,
bracket feet and linkage angles remain estimates; the source drawing appears more
compact. No complete nominal fresh reproduction or historical mounting qualification
is claimed. The focused split-pin diagnostic was independently rerun from its
retained script and frozen helper imports.

Three new progression images bring the total to 108:
[installed isometric](../../intermediate_snapshot_iso_clutch_supports_001.png),
[support detail](../../intermediate_snapshot_detail_clutch_supports_001.png) and
[auxiliary controls](../../intermediate_snapshot_detail_clutch_auxiliary_001.png).
Standard tank011 and its transparent-hull companion remain unchanged.

## Required continuation

Populate the complete clutch-stop brake: M4160 anchor and six rivets, anchor
bolts, M4157 band pin, M4156 eyebolt, M4151 rod, SH87A bell crank, SH955C spring,
M4153 carrier, M4165 pin/crown nut/split pin, and their remaining hardware. The
anchor must join the existing band to a physical supporting bracket. Forward
M581 controls remain to connect the auxiliary shaft to the driver's mechanism.

Reconstruct the engine supports/frame and engine interfaces, revisit the mounting
hypothesis, overall clutch envelope and source registration, and qualify the
combined drivetrain before standard integration. Remaining tank interiors,
inventory coverage and later selected poses remain full-goal requirements.
The accepted qualified construction baseline remains the drum/flywheel checkpoint;
this candidate does not establish complete clutch, brake or tank geometry.

## Reproduction

Run from the repository root:

```sh
python3 cad/003_FullTank/experiments/drive_chains/clutch_support_build.py
python3 cad/003_FullTank/experiments/drive_chains/check_clutch_support.py
python3 cad/003_FullTank/experiments/drive_chains/check_clutch_support_exchange.py
python3 cad/003_FullTank/experiments/drive_chains/render_clutch_support.py
```

The builder accepts `--controls` and `--output`; the checkers/render accept
`--candidate`. Use a separate output for parameter trials. The independent checker
inspects source-sized hardware, physical bores/stock, mounting seats, native
ownership, preservation of inherited geometry and affected interference pairs.
STEP checks compare definitions and installed solids in both material directions.
Floor display crops in review images do not modify the saved physical floor.
Input snapshots include unchanged checker/renderer copies and supplemental
transitive imports; their manifests explicitly distinguish copies retained after
execution from the builder's original input record. Parameter-trial controls and
receipts are retained in `clutch_support_build/variants/alternate_support_layout`.
