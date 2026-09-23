# I03 — main clutch release bearings, forks and shaft

The subsequent [support and auxiliary-control checkpoint](I03-clutch-supports.md)
is the current development parent. Its source review withdraws this packet's
M4150 main-shaft split-pin assignment and removes that unsupported receiving hole:
the 5/32 × 1in split pin belongs to M4165's pending bell-crank pin assembly.
The results below describe the preserved earlier checkpoint.

Status: **development candidate; incomplete and not qualified**, 23 September 2026.
This continues [the clutch-stop brake packet](I03-clutch-stop-brake.md). The full
tank remains in progress, with standard geometry taking priority over poses.

The [native assembly](../experiments/drive_chains/clutch_throwout_build/TransmissionWithClutchThrowout.FCStd)
has **1,758 physical occurrences**: 77 additions and 1,681 preserved parent
occurrences. The additions represent two SKF1207 bearing units, two SH943A pins
and their nuts/lockwashers, four SH943C guards, two SH943B retainers, M4162 and
M4163 fork levers, two M4175 locking screws and nuts, M4150 main shaft, M4164
operating lever, and three M4172 keys.

The two catalogue bearings are nonphysical native containers with 27 physical
children each: two races, one cage and 24 balls. Those internal counts are
**estimates**, not independently enumerated SNL parts. The 77 new solid
occurrences therefore represent 25 catalogue-level installed items. They are
not additive to the standard tank's inventory, which has not been integrated.

## Evidence and chosen geometry

The [source dossier](../experiments/drive_chains/clutch_throwout_sources.json)
retains original-source hashes, survey records, and the measured parent axial
budget. Full SNL2, SNL250, SNL134 and SNL202 were inspected. SNL Plates22/23
depict transmission geometry and do not establish the main-clutch fork profiles;
their catalogue cross-reference was not used to transfer those shapes.

| Interface | Evidence | Interpretation and limitation |
| --- | --- | --- |
| Two SKF1207 envelopes | SNL250:027, OD2.8346in, bore1.378in, width.6693in | Rounded metric72×35×17mm, within0.0012mm of the printed conversions. |
| Bearing architecture | Modern [SKF1207 ETN9](https://www.emarketplace.in.skf.com/self-aligning-ball-bearing/1207-etn9) | Two open ball rows and cylindrical bore are a conditional transfer. Modern documentation does not establish historical ball count, cage material or internal dimensions. |
| Coupling receiver | Saved SH945A surfaces X744.95 and821.95 | 77mm gap accepts72mm rollers at X783.45, leaving2.5mm static clearance each side. No release-stroke or contact-state claim. |
| Transverse bearing centers | Mechanical reconstruction | Y±105mm clears the coupling body with the pins/nuts while placing the outer races within the flange radius. Not a printed transverse dimension. |
| Shaft height | Conditional SNL2 calibration and original pixel picks | Axis237.9056473mm below the clutch axis. Pick, registration and applicability uncertainty remain. |
| Shaft longitudinal station | Current bearing receiver | X783.45, directly below the rollers. It differs73.5803mm from the source-mapped shaft station; it is not a resolved historical datum. |
| Forks, main shaft and keys | SNL identities and counts; mechanical receivers | Profiles, stock, fits, shaft length/diameter, key sizes and operating-arm angle are estimates. Three keys installed; two of the source total five remain allocated to the auxiliary shaft. |
| Pins and locking hardware | SNL134 and202 | Source5/8in pin nuts and7/16in screw nuts constrain thread envelopes. Pin steps, nut heights, guard profiles and screw heads are estimated. No helical threads. |

Both guard washers on each bearing clamp only the inner race. The larger guard
diameter is relieved from the rolling outer race. Pins occupy real fork bores;
their locking screws seat against flats, with nuts supported by flat bosses.
Separate keys occupy cut passages in the shaft and three lever hubs. These are
solid interface features, not overlapping visual representations.

The commercial bearing reconstruction uses a spherical outer race, two toroidal
inner race grooves and an estimated one-piece cage with radial cylindrical
windows. The source-sized external envelope remains independent of these
internal assumptions. The controls and generators retain all dimensions; changing
the JSON requires regeneration, rather than updating native expressions live.

## Axial length remains unresolved

HB115 specifies19.875in for the complete clutch unit, but gives no established
endpoints for the selected SNL arrangement. Existing measured candidate spans
are retained in the [envelope review](../experiments/drive_chains/clutch_envelope_review.json)
and the source dossier. Source-sized inherited parts have not been compressed to
force the number. The bearing receiver is sufficient for a development assembly;
the overall length and source-registration discrepancy must be revisited with the
engine/crankshaft and bracket interfaces before historical fit is accepted.

## Remaining installation work

M4148 and SH953A supporting brackets, their eight source-listed cap screws,
SH953C auxiliary shaft, two SH953B levers, two auxiliary keys, taper pins, fork
ends, rod and pin assemblies remain required. Main-shaft split-pin retention
and the M4162 source5/8×7/8in cup setscrew remain pending, with receiving bores
present. Do not count SH953C or the two nested keys again through the left-bracket
assembly reference.

The brake still needs M4160 anchor and six rivets, anchor bolts, band pin,
eyebolt, carrier, bell crank, rod, spring and associated hardware. Supporting
feet must be reconciled with actual floor/frame geometry and source mounting
evidence. A clearance pass does not establish a load-bearing mounting interface.

The qualified drum/flywheel checkpoint remains the accepted baseline. The current
development assembly is not qualified, complete, or accepted for standard-tank
integration. Engine, cooling, air circuits, other interiors, complete coverage,
integration and later poses remain full-workflow obligations.

## Reproduction and checks

All **90 independent checks, 332 affected material pairs and 93 STEP comparisons
pass**. A coupled trial changes the inferred bearing ball count/radius/row
spacing and lowers the shaft to250mm below the clutch axis; it passes90 checks
and368 local material pairs. It keeps the printed bearing envelope fixed. That
trial does not include standard-tank clearance or STEP qualification, and a
fresh nominal reproduction remains pending.

Five saved-native views and the source context were inspected. Three new
progression images bring the total to105; all102 earlier image hashes are
unchanged. Standard tank011 and its transparent-hull view remain unchanged.

The [bracket context measurement](../experiments/drive_chains/clutch_throwout_build/bracket_context.json)
places the shaft axis at world[2608.680363,0,611.327863]mm,78.277863mm above
floor plate7's upper face at533.05mm. The other nearby standard objects are
engine/transmission/clutch layout envelopes, not physical mounting receivers.
Detailed supporting frame geometry and bracket attachment remain to be established.

Run from the repository root:

```sh
python3 cad/003_FullTank/experiments/drive_chains/clutch_throwout_build.py
python3 cad/003_FullTank/experiments/drive_chains/check_clutch_throwout.py
python3 cad/003_FullTank/experiments/drive_chains/check_clutch_throwout_exchange.py
python3 cad/003_FullTank/experiments/drive_chains/render_clutch_throwout.py
```

Reproduce the retained sensitivity trial using
`--controls cad/003_FullTank/experiments/drive_chains/clutch_throwout_build/variants/alternate_internals_lower_shaft/controls.json`
and a fresh `--output` directory on the builder; pass that directory as
`--candidate` with `--local-only` to the independent checker.

Saved receipts describe the actual completed checks and their limits. Independent
checks inspect the saved bearing envelope, spherical-race volume, real bores,
washer contact/relief, pin and key receiving material, installed hierarchy and
preservation of the parent. Material comparisons include nearby standard-tank
physical components. STEP checks compare definition and world-installed solids
in both material directions, with independent mass integration.

The first candidate exposed unreliable bounding/mass and STEP checks around
transversely parameterized spherical trims and spherical cage windows. Its
native file, logs and inputs are retained in the durable work area. Aligning the
spherical surface axis with the bearing axis preserves the intended race form
and matches its analytic volume. Radial cage windows replace the inferred
spherical windows. Neither correction changes the source bearing envelope or
relaxes the acceptance tolerances. Targeted diagnostic receipts are retained.
