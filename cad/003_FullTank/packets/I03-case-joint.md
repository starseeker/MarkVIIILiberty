# I03 — central bevel-case joint

Status: qualified partial reconstruction; standard tank011 remains unchanged.
This increment follows the qualified brake-bearing candidate. It develops the
M263/M264 joint while the reversing controls and other transmission equipment
remain unfinished.

## Source and interpretation

SNL27 lists fourteen MX8 bolt assemblies, each containing a bolt, half-inch SAE
castle nut and 3/32 × 1 inch split pin. SNL252 independently gives fourteen
assemblies and two M326 gaskets; SNL98 also gives two gaskets. The original page
photographs were inspected alongside the part-marked HB121 section and SNL23.
Exact records, survey identities and source hashes are in
`experiments/drive_chains/transmission_case_joint_sources.json`.

The inherited split at X ±0.15 mm divides the central casting into M263 behind
and M264 ahead. The transverse shaft and bearing openings separate its mating
land into two regions. The reconstruction allocates one M326 gasket and seven
bolts to each region. This interpretation follows the listed count and the
section's split location; it does not prove the complete original bolt pattern.
HB121 uses MX6/MX7/MX72/MX73 callouts at the illustrated joint, so equivalence to
the later SNL MX8 arrangement remains unresolved.

## Geometry and ownership

`TransmissionCore/CentralCaseJoint` owns two gasket occurrences and fourteen
bolt assembly containers. Each assembly owns three physical leaves. Both gaskets
reuse one definition; all bolts share one definition. Nuts and intact formed
cotters reuse the qualified brake-bearing/input-installation definitions.
M263 and M264 own their added lands and bored/spotfaced receivers.

Controls are authored in `transmission_case_joint_controls.json`. Bolt axes,
flange radius, 32 mm grip, 48 mm under-head length, head dimensions and thread
envelope are estimates. The half-inch shank follows the printed nut size; the
cotter dimensions and fourteen-set count are printed. Gasket thickness follows
the inherited 0.3 mm split, not a historical stock specification. The seal is
derived from the rear mating face and its support by the cover is checked
separately. The gasket's cylindrical edges have an inferred 0.05 mm radial gap
around the inherited bush/flange/retainer seats and 0.05 mm clearance at their
axial shoulders. No compression, load, torque or oil-tightness claim is made.

An initial attempt to intersect nearly coincident extruded mating faces returned
empty Boolean results despite both containing an interior test point. That
construction was rejected in the local study. The adopted construction uses the
rear mating face directly; independent support checks and exchange checks are
required before accepting it. No shape tolerances were enlarged to force a pass.

The first assembled trial exposed eight small gasket/seat intersections and six
cotter-eye/casting intersections. Cylindrical gasket-edge relief corrects the
flat-extrusion intrusion at the shaft; 15 mm spotface radii clear the cotter eyes.
The failed trial's report and exact inputs are retained under
`transmission_case_joint_build/rejected_trials/initial_fit`.

An additional absolute mass check exposed default integration differences between
FreeCAD and STEP (about 0.0101 mm³ per bolt). The adaptive OCC calculation in
`case_joint_mass.cpp` requests relative integration accuracy of 1e-12. Its native
bolt volume agrees with an independent integral for intersecting cylinders to
about 1.5e-8 mm³. Native/STEP adaptive masses are compared against a diagnostic
volume envelope equal to mean surface area times the sum of the existing shape
tolerances. This accounts for surface representation precision; it is not a new
sewing or Boolean tolerance. The fixed raw/bounded material-difference checks
remain mandatory. Default-mass failures and the adaptive diagnostic are retained
under `rejected_trials/default_mass`; stored BRep tolerances are unchanged.

Independent checks subsequently found contact at the gasket's axial steps.
Adding the shoulder clearance resolves that separate interface. Parameter trials
also exposed inconsistent results from a compound of overlapping bore/spotface
cutters. Each connected cutter is now fused into one solid before subtraction;
the stepped radial gasket cutter is also one union. Disjoint joint cutters may
still be grouped in a compound. The rejected checks and exact inputs are retained
under `rejected_trials/shoulder_and_tools`.

The thin-sheet Boolean support probe returned zero cover overlap even where
independent point classification found material. Support validation therefore
uses a documented 2 mm grid through the actual gasket, tested just inside both
casting faces, with a deliberately displaced cover as a negative control.
This is sampled backing evidence; it cannot establish exact contact area or a
fluid-tight seal.

## Reproduction and acceptance

From the repository, run these with `--stage cad/003_FullTank`:

```
python3 cad/003_FullTank/experiments/drive_chains/transmission_case_joint_probe.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/check_transmission_case_joint.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/check_case_joint_variants.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/render_transmission_case_joint.py --stage cad/003_FullTank
```

The builder must reopen the native hierarchy, preserve all unaffected shapes and
placements, check affected material pairs and repeat the new/revised geometry
through STEP. The independent checker examines quantities, shared definitions,
shank passage, supported bearing lands, nut retention, gasket support and bounded
casting changes. Local parameter trials vary inferred grip and hole clearance.
The render uses actual saved native geometry and the existing SNL23 calibration,
with no scan warping. The final candidate contains **1,365 valid solids**:
44 new occurrences, two revised castings and 1,319 unchanged occurrences.
All 335 affected material pairs and 46 native/STEP comparisons pass. Fifty-nine
interfaces are freshly checked and 602 retained against unchanged geometry.
All raw and bounded STEP material differences are zero; the largest adaptive
mass difference is 0.005255 mm³, within the existing surface-tolerance envelope.

The independent checker passes 200 checks, including 2,072 support samples per
gasket half against each casting. Three local parameter trials pass with 46
solids and 117 material pairs each: half-grip 14 and 18 mm, and receiver radial
gap 0.25 mm. These trials do not qualify the whole tank's parameter envelope.
Six final renders were inspected. The upper fastening station is lower than the
SNL illustration, and the rear case contour is flatter; these remain recorded
approximations. The complete transverse bolt pattern remains inferred.

`transmission_case_joint_build/qualification.json` binds the immutable generation,
independent-check, parameter, render, visual and artifact receipts. Twenty
standard native files and forty-nine previous progression images remain byte
unchanged. Three new snapshots preserve the case overview, cover-hidden view
and joint section. This is an isolated transmission increment, not tank012.

## Remaining work

Four MX5 mounting studs, M301/M302 reversing fork and shaft, M303–M309 controls,
input pump and support, lubrication, brakes and frame/hull integration remain
open. The standard tank still contains provisional interior envelopes. This
packet cannot establish complete-transmission or complete-tank coverage.
