# I03 — central transmission cases and rotors

This packet adds component geometry to the isolated transmission/chain fixture.
The standard tank remains milestone 011 until integration and full-model checks.
The complete transmission still requires its gears, bearings, brakes, controls,
joint hardware and lubrication connections.

## Identity and ownership

| Mark | Component | Installed quantity | Survey identity |
|---|---|---:|---|
| M263 | Bevel-gear case | 1 | P_2f8188a10797254f |
| M264 | Bevel-gear case cover | 1 | P_5bd671035703ae57 |
| M255 | Transmission cross shaft | 1 | P_07bd3bc1da1a5605 |
| M278 | Planetary case, brake-drum half | 2 | P_59761ccda0d080c8 |
| M277 | Planetary case, plain half | 2 | P_6dee7b3b041a728b |
| M286 | Large planet-carrier disk | 2 | P_ec32be861df98224 |
| M269 | High-speed brake drum | 2 | P_947705f236231a46 |

`TransmissionCore` owns center, port and starboard groups through native
`App::Part` containers and shared `App::Link` definitions. M255 is a single
cross shaft between the two previously reconstructed M289 output shafts.
The carrier disks follow their output-shaft spline phases. The fixed bevel
case and cover keep the tank coordinate frame.

## Evidence and reconstruction

Original SNL 59, 60, 77, 80, 83, 215, 252 and 253 were inspected with Plates
22/23 and HB 124–127. Source hashes and exact survey rows are preserved in
`experiments/drive_chains/transmission_core_sources.json`.

HB126 explicitly gives M255 ten splines and M269 ten splines with a 15-inch
outside diameter. The model uses 381 mm for the latter. Other shaft diameters,
straight spline forms, wall thicknesses and cast profiles remain estimates.
The plate's approximately 408 mm drum extent under the existing local scale
conflicts with the printed diameter; it is not silently used as another size.

Plate22 is interpreted as a horizontal section: source horizontal follows the
transverse shaft, and source down is tank forward. Its unchanged local scale
comes from the printed four-inch M291 hub width. M278/M277 are hollow revolved
sections; M286 is a separate conical carrier, not part of the surrounding case.
The large case also provides the low-speed brake-drum surface.

M263 and M264 are interpreted as rear and front case halves from Plate23's
upper/lower joint, input-bearing boss and rear mounting webs. Their outline
uses explicit cubic B-spline poles, with axial extrusion, a scaled internal
cavity and analytic shaft/input openings. The rear webs meet the existing
channel faces. Exact cast blends, axial taper, bolt patterns and bearing seats
are not established. Versioned controls retain all profile points and poles;
changing them requires regeneration.

The central case is provisionally centered on the tank. The input-pinion center
in Plate22 lies about 44 source pixels, or 32 mm, away from the projection of
that assumed centerline. Local calibration, scan distortion and possible
asymmetric geometry have not been separated. Input-gear and shaft installation
must revisit this discrepancy. The Plate23 overlay uses a separately stated
inspection scale; it does not provide independent dimensional validation.

## Interface corrections and limits

The initial M278 flange trace crossed the M286 carrier edge. Its inferred bore
boundary was revised by ten source pixels (7.257 mm radially), exceeding the
earlier four-pixel output-feature allowance. This is a part-boundary
reinterpretation requiring review with the future M279 ring gear.

The carrier hub's inner face stops immediately outside the existing M290 ring.
Moving its outer face did not resolve the clash and was rejected. M289 and
M290 geometry remain unchanged. The separate M288 washer at the outer side of
the carrier remains unpopulated; its space is not counted as a finished part.

These corrections establish nominal component separation. They do not qualify
gear engagement, historical running clearance, loads, oil retention, complete
case fastening or the whole uncertainty envelope. The empty housing interiors
remain unfinished geometry coverage.

## Reproduction and review

```sh
python3 cad/003_FullTank/experiments/drive_chains/transmission_core_probe.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/render_transmission_core_review.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/check_transmission_core_sensitivity.py --stage cad/003_FullTank
```

The candidate bundle records reopened native solids and retained placements,
material intersections against the current physical tank context, axial joints,
frame contacts, STEP roundtrip and source overlays. Read its `report.json`,
`sensitivity.json` and `visual_review.json` for actual outcomes; running the
commands alone is not evidence that those outcomes passed.

Next populate the two M288 washers, M256 retaining rings and sun/ring/planet
gear assemblies, then the bevel gears, input bearings and reversing clutch.
Use HB126's stub-tooth counts and pitch specifications with an explicit tooth
form approximation; do not assume a modern full-depth involute silently.
Revisit the case boundaries as these interfaces become concrete. Frame mounting
hardware, brake bands/linkages and full oil feeds precede final integration.
