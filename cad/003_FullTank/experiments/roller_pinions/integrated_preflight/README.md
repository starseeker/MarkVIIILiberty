# Pinions in the complete standard assembly — integration preflight

These experiments belong to the isolated pinion integration, not the main
mounting-stage delivery. Source checkpoint `a9a6304` on the local branch
`experiment/roller-pinions` retains the first integrated candidate. Generated
work and logs now live in the repository workspace rather than `/tmp`.

## Fuel-compartment junction

`neighbor_diagnostic` measures all 196 new pinion parts against the modeled
physical assembly. Its four material overlaps are the inner bearing and one
inner rivet on each side against the former inferred M2021 backplate position.
Bearing overlap is 73,654.6935 mm³ per side; rivet overlap is 2,606.3245 mm³.
The plan and oblique renders were inspected. No other new pinion/physical-part
overlaps were found. The failed full build log remains in the durable work area;
the source checkpoint reproduces its inputs.

HB Plate27 was inspected alongside SNL2/7. It supports a continuous rear plate,
but does not dimension its longitudinal station. `fuel_backplate_candidate`
tests a separate inferred control changing the former source-pixel equivalent
1630 to 1642, approximately 72 mm aft. It rebuilds only M2021 and the owned
roof/floor edges; the side-panel seam, bearings and shafts remain fixed.
The 16 mm printed backplate thickness and source calibration are retained.

The saved, reopened candidate passes hull/track contact checks and all pinion
checks: 394 internal plus 116 external candidate pairs, zero overlaps,
102 bearing faces, 32 full receiving-hole walls, 40 radial clearances and four
shaft-plug envelopes. Backplate/bearing clearance is 26.0295 mm on each side.
Both candidate rasters were inspected. This is a documented geometric
approximation, not a historical fit or an accepted source measurement.
The complete integrated build and parameter trials remain pending.

## Alternative 37-tooth wheel

`alternative_teeth` rebuilds a 37-tooth native rim and checks all four installed
copies against the unchanged paired pinion fixture. Twelve rim/pinion overlaps
occur at the current 17.21° pinion phase and current axes. The tested combination
is rejected. The experiment does not disprove the historical 37-tooth evidence,
nor test every possible tooth profile, phase or station. Both printed tooth
counts remain in the source record.
