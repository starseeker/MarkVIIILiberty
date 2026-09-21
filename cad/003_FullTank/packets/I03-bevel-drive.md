# I03 — central bevel drive and thrust-bearing stack

This increment continues the [bevel sleeve supports](I03-bevel-sleeve-supports.md)
with M258A bevel wheels, M258B clutch rings, M257A shifter clutch, the integral
M247 pinion/shaft, M260 shims, 24 rivets and two decomposed thrust bearings.
Standard ahead engagement connects the right/starboard wheel, following HB119.
Input bearings, coupling, controls and the rest of the transmission remain open.

## Evidence and geometry

The [source register](../experiments/drive_chains/transmission_bevel_gear_sources.json)
retains catalogue records and inspected image hashes. HB126 specifies 14 and
46 stub teeth, 3–4 diametral pitch, and a four-tooth, ten-spline clutch. SNL99
allocates one wheel, one clutch ring and six rivets of each printed length per
bevel assembly. The 5/8 inch rivets have blank lengths 2-1/8 and 2-3/8 inches.
SNL217/252 supply two M260 laminated shims. HB M257/M258 are provisionally mapped
to SNL M257A/M258A; the suffix difference is retained in the metadata.

SNL16 gives the commercial thrust bearing's bore, outside diameter and height
as 4.1339, 6.1024 and 1.5748 inches. The modeled envelope is 105 × 155 × 40 mm;
rounding residuals are −0.00106, −0.00096 and +0.00008 mm. Each assembly contains
two races, a cage and sixteen balls. Internal ball count, groove form and cage
are inferred. Its catalogue identity belongs to the assembly container; the
38 internal solids do not add 38 catalogue bearings.

The straight bevel teeth have cubic spline spherical-involute flanks joined
between two radial stations by ruled surfaces. The pitch-cone apex is common
and centered on the cross shaft. The cone distance is 203.552472 mm; wheel and
pinion pitch radii are 194.733333 and 59.266667 mm. Face width 50 mm, pressure
angle 20 degrees, tooth thinning 0.2 mm and dedendum 1.25 times the 6.35 mm stub
addendum are assumptions. Root/tip chords, end caps and absent root fillets
limit fidelity. The local implementation has no external gear-workbench
runtime dependency. [KHK's geometry reference](https://khkgears.net/gear-knowledge/gear-technical-reference/calculation-gear-dimensions/)
and the [FreeCAD gear spherical-involute implementation](https://github.com/looooo/freecad.gears/blob/master/pygears/bevel_tooth.py)
were consulted as method references, not historical Mark VIII specifications.

The clutch has four sector lugs and ten rectangular internal splines, with a
fork groove. Its center is Y−16 mm in the standard assembly. The quarter-inch
M258B flange, alternating twelve-hole rivet pattern and joint allocation are
hypotheses: six short rivets join wheel/sleeve; six longer rivets also include
the clutch ring. The shorter heads have explicit access recesses. Nominal
rivet radial clearance is 0.15 mm. Spherical heads are constructed by revolving
circular arcs; upset volume equals the unused printed shank length. Factory
and formed head profiles are assumed equal.

## Axial reconciliation and rejected geometry

The printed thrust-bearing width moves the outer bush seat outward. M259's
flange remains Y66.766–82.731 mm; the bearing occupies Y82.731–122.731 mm,
followed by a 0.3 mm shim and the M262 flange. M259 and M261 now extend to
Y206.084 mm, 0.2 mm from the retained small-sun datum. The outer bush ends at
Y196.227 mm and M310 ends at Y198.727 mm, leaving 0.3 mm to the brake drum.
These lengths, running fits, shim thickness and cast seat profiles are inferred.
The earlier 31.387 mm sleeve-end gap is superseded by this populated stack.

The existing case cavity was originally cut before fusing its input boss.
That ordering left inboard boss stock inside the cavity and caused two
19,155.314 mm³ gear overlaps. Reapplying the original cavity removes that
stock while preserving the external casting outline. The revision also
extends the split bearing bosses and cross-shaft journals.

The first full trial exposed another defect: sphere/cylinder intersection
returned an empty rivet tail cap and a tiny spherical face at the opposite
pole. Native single-solid validity alone did not catch the missing head;
head seating and STEP reimport did. Revolved arcs replace that construction,
with explicit checks on both cap volumes and axial retention.

The bearing cage's original spherical-pocket parametrization also caused STEP
reimport to raise its maximum shape tolerance from about 0.000000116 to 0.00001 mm.
Aligning the pocket sphere axes with the bearing axis preserves the exact same
material in both Boolean directions and reimports at 0.0000001 mm. The geometry
is retained without relaxing the tolerance check.

The **32.113 mm difference between local bevel and inherited output source
registrations remains unresolved**. Both overlays retain the same scale;
mechanical fit to printed dimensions and adjoining parts is not proof that
all illustrated proportions have been recovered. Input-shaft axial steps,
spline count and thread envelope remain provisional. Its 69.65 mm journal
allows 0.1 mm radial clearance within the printed 2.75 inch Timken cone bore;
that separate bearing/housing/coupling stack still needs reconstruction. The
comparison explicitly shows its provisional end extending beyond the source.
The later [input-assembly review](I03-input-assembly.md) corrects that endpoint
interpretation: Plate22 shows the coupling as a detached detail and omits its
assembled extension. It cannot establish complete shaft length. Plate23 now
provides the conditional end-to-end comparison.
The wheel tooth-band/web contours and pinion cone width also differ; printed
tooth counts/pitch are retained while source-scale and inferred-profile
uncertainties remain open.

## Verification status

The [saved candidate](../experiments/drive_chains/transmission_bevel_gear_build/TransmissionBevelGearCandidate.FCStd)
reopens with 1,199 valid single-solid leaves: 70 new, 13 revised and 1,116 unchanged.
All 458 material pairs, 497 specified interfaces and 83 native/STEP material
comparisons pass. Both raw and bounded Boolean comparisons retain zero material
difference; stored tolerances are not inflated. Protected exterior case and
shaft material remain unchanged outside the named revision regions.

The [independent checker](../experiments/drive_chains/transmission_bevel_gear_build/interface_checks.json)
passes 109 checks of native tooth counts and cubic surfaces, 26 sampled mesh
positions, deliberately wrong tooth phase, four clutch dogs and ten splines,
ahead engagement, printed bearing envelopes, shared ball definitions,
continuous shaft passages, both rivet heads and axial capture, and deliberately
displaced STEP solids. Mesh sampling does not prove full motion or tooth contact
stress. Bearing internals, press fits, threads and sealing remain unqualified.

The [visual review](../experiments/drive_chains/transmission_bevel_gear_build/visual_review.json)
binds seven inspected rasters, including the
[source comparison](../experiments/drive_chains/transmission_bevel_gear_build/source_review/bevel_drive_comparison.png).
Standard tank 011, its opaque/transparent views and 37 earlier snapshots remain
unchanged. This checkpoint accepts nominal static geometry with documented
approximations; it does not complete the transmission or qualify its full
parameter envelope, service loads or complete assembly sequence.

## Reproduce and continue

```sh
python3 cad/003_FullTank/experiments/drive_chains/transmission_bevel_gear_probe.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/render_transmission_bevel_gear_review.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/check_transmission_bevel_gear.py --stage cad/003_FullTank
```

Use `--output` on the builder and `--candidate` on renderer/checker for trials.
Actual raster inspection is recorded separately from successful rendering.
Next complete the input bearing/housing/coupling stack, resolve M265/M266 brake
bearing attachment, and continue case fastening, controls, lubrication,
mounting and standard integration. Other full-tank packets remain active or
queued; this increment does not complete the tank.
