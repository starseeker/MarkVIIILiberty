# I03 — vertical reversing shaft, levers and bearings

Status: qualified partial reconstruction with documented approximations.
This is an isolated transmission increment. Standard tank011 and the complete
interior reconstruction remain incomplete. Standard geometry precedes poses.

## Identity, quantity and ownership

SNL215:029–034 owns one M305 shaft, one M303 upper lever, one M304 lower lever
and two No. C Woodruff keys. SNL18:010 and254:015 list two M306 bearings.
SNL28:006–010 and254:016 own two MX11 bolt/nut/pin sets; SNL241:001–005 separately
owns two MX12 stud/nut/pin sets for M306-to-M263. Both attachment types are
represented. This adds **19 physical occurrences**, using seven new definitions
and two existing definitions: the half-inch castle nut and repaired small cotter.
The latter has two intact analytic legs; older swept cotters are not reused.

`TransmissionCore/ReversingControl/VerticalReversingControl` owns the shaft
assembly and upper/lower bearing groups. Each bearing group owns its bearing,
MX11 assembly and MX12 assembly. Assembly identities live on containers; only
leaves contribute physical counts. The unmarked shaft identity at SNL254:014
is retained as a conditional reference on the shaft-assembly container. Its
mapping to the SNL215 assembly is an interpretation, supported by the absence
of separately listed levers/keys in the complete-transmission list. The frozen
survey is not merged and no extra physical shaft is invented.

The source JSON retains 22 records and original source hashes. SNL18,28,115,118,
215,241,254 scans and HB121/123/SNL23 illustrations informed the reconstruction.
No verified dimensional mapping for the old lettered No. C key was found;
modern numbered Woodruff standards are not treated as evidence for its size.

## Geometry and parameter basis

Coordinates use the existing transmission frame, X forward, Y port, Z up.
All control lengths/coordinates below and in the controls JSON are millimeters;
`lower_lever_angle` is in degrees. Counts and source quantities are separate.
The inherited SNL23 registration is unchanged: 0.921141975mm/pixel, shaft-origin
pixel[579,493]. Source images are not warped to match the model.

| Feature | Current value | Evidence or assumption |
|---|---:|---|
| MX12 nominal diameter / length | 12.7 / 98.425 | Printed half inch × 3-7/8in, SNL241:003 |
| MX12 US / SAE thread spans | 20.6375 /22.225 | Printed 13/16in and 7/8in; nominal envelopes |
| Small cotter diameter / leg length | 2.38125 /25.4 | Printed 3/32×1in; shared repaired definition |
| Shaft axis X,Y | −295,−179 | Straightened SNL23 silhouette; Y follows provisional rod endpoint |
| Shaft body / journal diameters | 40 /38.1 | Conditional picture width and estimated turned shoulders |
| Shaft end Z | −229.85,206.85 | Inferred blind bearing fit |
| Upper / lower bearing open face Z | 182 /−205 | Approximate source stations |
| Bearing height / bore depth | 32 /25 | Inferred opposed blind journals |
| Journal radial / axial clearance | 0.15 /0.15 | Reconstruction fit, not historical tolerance |
| Lever hub OD / height | 52 /30 | Estimated; shoulders and bearings capture both hubs |
| No. C key radius / width | 12.7 /6.35 | Unverified size mapping; pocket clearance 0.05 |
| Upper finger radius / rod socket radius | 6.35 /6.5 | Inferred integral rounded finger and cross-socket |
| Lower arm length / direction | 112 /−90° | Provisional reverse-linkage interface |
| MX11 underhead length | 110 | Inferred; not a printed dimension |
| Bearing fastener Y offsets | ±36 | One bolt and one stud per bearing, inferred allocation |
| Case mounting seat X | −253 | Added local lands; inherited case contour remains unresolved |
| Bearing nut spotface radius | 18 | Estimated receiver clearing the formed cotter and nut |

The upper lever uses a smooth B-spline arm and a single revolved neck/ball
profile. Its rounded finger enters the revised M302 cross-socket. Only the
provisional end-hole region of M302 changes; rod journal, fork clamping and
detent geometry remain. M263 gains two local mounting lands and attachment
bores/spotfaces. Saved-shape differences measure approximately 338,546mm³ added
and 2,805mm³ removed, confined to those mounting regions. Printed MX12 length
is preserved instead of stretching the stud to span the inherited case contour.

The blind opposed journals, turned shoulders and integral finger are explicit
construction hypotheses. The shaft/lever fit is geometrically captured in this
standard arrangement; friction, torque, wear, lubrication and movement are not
qualified. Lower lever orientation remains open until the long reverse linkage
is installed. This packet adds no unlisted retention clip or linkage pin.

## Verification and reproduction

Run from the repository. The last three commands are independent after a
passing builder:

```
python3 cad/003_FullTank/experiments/drive_chains/transmission_vertical_probe.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/check_transmission_vertical.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/check_vertical_variants.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/render_transmission_vertical.py --stage cad/003_FullTank
```

The reopened native assembly contains 1,391 valid single-solid leaves: 19 new,
2 revised and1,370 unchanged. All 148 affected material pairs are clear, including
the applicable standard tank context. Sixty-three interface distances are
freshly checked and641 retained from unchanged parent geometry. All 21 physical
STEP exports/reimports pass material, tolerance and adaptive mass checks.

All 116 independent checks pass. They inspect source identities and ownership,
shared definitions, blind bearing stock and continuous journal walls, shaft end
capture, keyed lever antirotation, bolt seating, stud engagement, both cotter
legs, nut withdrawal obstruction and the rod/finger connection. Deliberately
translated shafts/rod/nuts and rotated levers supply negative controls. Saved
case and rod revisions must remain inside independently constructed local masks.

Three parameter trials pass: key widths 5 and 8mm, and shaft X−300 with nut seat
X−310 to preserve the bearing-to-nut offset. Each rebuild checks 21 local solids
against the retained transmission. The moved shaft changes lever reach, bearing
foot and inferred bolt length while retaining printed MX12 length. These trials
do not qualify full tank variation, STEP export, loads or motion.

Rejected trials retain the initial nut/cotter contacts, undersized spotface,
incorrect expected reused-nut gap and upper-lever STEP discrepancy. Revolving
one analytic finger profile resolved the export discrepancy without changing
the nominal form or relaxing native tolerances. A misleading intermediate case
subtraction was replaced by checks of reopened, refined saved geometry. See
`transmission_vertical_build/rejected_trials/README.md` and the exact receipts.

## Visual comparison and remaining work

The fixed-scale SNL23 comparison follows the shaft's overall height and position.
The reconstructed shaft is straight; the drawing leans, leaving opposing offsets
near its ends. Bearing depth, feet, lower arm projection and transverse placement
remain estimates. The inherited case rear wall remains ahead of and flatter than
the drawing, and the added lands do not resolve that larger contour question.
The upper arm is projected through the case in the edge overlay, so its exposed
outline there is not an assertion that it would be visible through solid armor.

Seven final renders were visually inspected. Three progression snapshots preserve
the rear installed view, mechanism and bearing section. Twenty standard native
files and 55 previous snapshots are byte unchanged. The combined accepted status
is bound in `transmission_vertical_build/qualification.json`; the generation
report remains an immutable receipt with rendering incomplete at generation.
Next: the four MX5 case mounting studs and their 5-1/2 versus 5-5/8in source conflict,
input pump/support installation, brake mechanisms, lubrication, long controls,
frame/hull integration and the other tank interiors. No complete transmission,
complete tank or historical dimensional fit is claimed.
