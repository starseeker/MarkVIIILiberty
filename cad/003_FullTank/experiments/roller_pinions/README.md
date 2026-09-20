# Roller-pinion preparation

The [research packet](../../packets/R02-roller-pinions.md) defines the next
source-counted pinion study. The first incomplete native rotor experiment is
described below; no main-model integration has been performed.

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
