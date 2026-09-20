# Roller-pinion preparation

The [research packet](../../packets/R02-roller-pinions.md) defines the next
source-counted pinion study. The first incomplete native rotor experiment is
described below, followed by a 73-leaf rotating fixture; no main-model
integration has been performed.

`source_rows.json` preserves twenty-three frozen survey records and their
part identities. `source_review.json` records inspected illustrations and the
original HB132 scan with hashes. `printed_controls.json` transcribes dimensions
without making the ambiguous boss diameter an accepted pitch-circle control.

The source-defined rotating assembly contains 73 leaves; its shaft assembly
contains four. Two separately supported common bushes and nineteen named
mounting leaves produce a provisional 98-leaf scope per side. Shared-part
quantities, the additional M1552 rivet allocation, the M1541A/B nomenclature,
35/37 driving-wheel conflict and installed plug treatment remain explicit.

`station_screen.py` produces an unaccepted planar arithmetic diagram. A manual
SNL Plate 2 pick at pixel [1614,422] puts the pinion 635.863 mm from the unchanged
drive axis under the existing provisional calibration. Interpreting 13.687
inches as the outer boss circle, with an illustrative 27.5 mm boss radius,
puts the roller-center circle within 1.338 mm of the drive groove-center circle
along the center line. Treating 13.687 inches as a roller-center diameter changes
that arithmetic to −26.162 mm. Neither number is a measured material gap.

The [diagram](station_screen/station_screen.png) visibly overlaps a roller with
a current tooth flank at its deliberately simple center-line phase. That phase
is not an accepted installation. The screen omits crest fillets and all axial
geometry; source-pick uncertainty alone is larger than the 1.338 mm comparison.
Use native phase/interface studies before accepting any geometric interpretation.
The report binds the drawing to the source, script and unchanged authored inputs.

## First native rotor fixture

`rotor_probe.py` creates one connected casting and eighteen individual rollers
in `rotor_build/PartialPinionRotor.FCStd`. Its nineteen installed solids and two
definitions survive a fresh reopen, have no detected material overlaps in the
candidate pairs, and retain 0.2 mm inferred roller end gaps. The eighteen pins,
split pins and lubrication plugs—54 source-BOM leaves—are still missing.
Shaft, bushes, supports and chain are also outside this fixture's scope.

The [oblique](rotor_build/oblique.png) and [axial](rotor_build/axial.png) views
were inspected against the broad HB Plate 81/82 arrangement. This is a first
topology hypothesis: four lobed boss webs, a central 23-tooth gear, axial hub
and two nine-roller banks. The bank positions, web thicknesses, hole patterns,
boss circle interpretation and tooth reliefs are inferred. Sharp gear crests
and schematic cast sections need refinement. Neither gearing nor installed
fit is qualified. The report retains native, script, image and authored-input
hashes; exact executed scripts accompany the outputs.

## Source-counted rotating fixture

`pin_probe.py` extends that study to `pin_build/PinionWithPins.FCStd`: five
definitions, eighteen nested pin assemblies and all 73 rotating-BOM leaves.
The 118 candidate material pairs have no detected overlaps. A separate fresh
reopen reconstructs 72 placements and checks eighteen pin-head seats, eighteen
0.1 mm roller/pin radial clearances, and eighteen open oil galleries. Moving a
pin 0.2 mm axially deliberately fails its head-seat check.

The [oblique](pin_build/oblique.png) and [axial](pin_build/axial.png) images were
inspected. Individual pin heads, oil plugs and cotter loops are visible. The
cotters retain the printed supplied stem length and combined nominal diameter,
but use round straight legs as an unsplayed fixture approximation. Their formed
installed shape and retention remain unqualified. The initial cotter-eye
placement intersected the pins by 0.106 mm³ each; that rejected result is retained
in `pin_build/rejected_initial_cotter_head/`. The corrected fixture provides an
explicit inferred 0.5 mm eye clearance without lengthening the supplied stem.

Source-count completeness applies only to the rotating assembly. This is still
an experimental reconstruction: casting sections, hole and head shapes, thread
envelopes, shaft, bushes, supports, hull receivers and gearing need further work.

## Shaft, mounting and receiver fixture

`interface_probe.py` measured 14,514.987 mm³ of interference between the first
casting and the unchanged M1407 barrel. An inferred 2.35 mm deep end counterbore
with 80.2 mm radius clears that barrel by 0.2 mm. This preserves the printed
casting length. The common bushes have 0.2014 mm radial clearance to the inferred
casting bore; a historical press fit or running fit is not established.

`mounted_probe.py` produces [MountedPinionStudy.FCStd](mounted_build/MountedPinionStudy.FCStd)
with 98 physical occurrences: 73 rotating leaves, the four-leaf shaft assembly,
two bushes and nineteen mounting leaves. Four separately labeled receiving
panels are inspection context outside that subtotal. Its 216 candidate material
pairs have no detected overlaps. Three bearing/backing-to-panel faces and both
shaft shoulders seat, with 0.04445 mm radial shaft/bush gaps.

The fixed shaft retains its printed length and central diameter. Reduced end
journals follow the existing common M1407 bearing; the first constant-diameter
shaft failed that interface and is retained in
`mounted_build/rejected_full_diameter_journals/`. The inner Q52E plug is cut
flush and the outer head retained, following HB132. Oil drilling, nominal
pipe-thread envelopes, M1546 casting and exact shaft turning remain inferred.
The keyway opens through the shaft end instead of leaving an accidental
0.0625 mm lip beside the shared key.

The original inferred wing/end seam left one bearing hole on each side and two
outside backing holes partly unsupported. The experimental seam moves from
source pixel 1630 to 1642, independently of the fuel-compartment backplate.
Each adjacent panel pair retains exactly the same combined solid before drilling;
all sixteen proposed fastener bores now lie fully within their assigned receiver.
The outside hull contour, old driving-shaft holes and source identities are
preserved. This seam is a documented inference, not a new source measurement.

The [mounting](mounted_build/oblique.png) and [receiver](mounted_build/receivers.png)
views were inspected. The standalone mounting arrangement is coherent, but the
complete tank installation, gear engagement, formed cotters, lubrication details,
threads and further shared-part quantity reconciliation remain open.

## Static gearing studies

`phase_probe.py` screened eighty angles at the source-picked axes. None cleared:
the best 0.5° sample had 174.859 mm³ overlap. `refine_phase.py` narrowed this to
3.127 mm³ at a 0.025° interval. These rejected placements remain recorded.
`solve_static_phase.py` continues the bounded placement study; a successful
single static sample must still be checked against both complete wheels and
does not establish continuous gearing or resolve the source 35/37-tooth conflict.

The first interface/phase rendering adapter duplicated placements when it mixed
pre-assignment shapes with recomputed bodies. `render_studies.py` corrected the
rasters from the unchanged saved native solids. Rejected images and reports are
retained under each study's `rejected_render_adapter/`; native numerical checks
were unaffected. The corrected views were inspected before use.


The resulting [static fit](static_fit/StaticPinionFit.FCStd) has a 0.29997 mm
minimum roller/ring gap at a 17.21° angle and an explicit 1.8033 mm station shift
toward the driving-wheel axis. The source pick and calibration remain unchanged.
Its visual inspection is recorded separately in `static_fit/visual_review.json`
to preserve the input-report hash already consumed by the next study.

`installation_probe.py` checks both complete 149-part drive units against both
98-part pinion units: 494 physical occurrences, 72 cross-family material
candidates, no overlap, and matching minimum gaps at all four roller/ring banks.
The [oblique](installation_build/oblique.png), [axial](installation_build/axial.png)
and [section-plan direction](installation_build/section_plan.png) views were
inspected against the broad HB81 arrangement. This is still an isolated static
study; full-tank neighbors and receiver bores at the corrected axis await
integration. `reopen_mounted.py` separately passes the saved 98-leaf fixture,
sixteen source definitions, sixteen full-depth bores, five seats and a deliberate
shaft displacement that loses its inner shoulder seat.
