# I03 — large planetary gears and retention

This extends the isolated transmission fixture with the large epicyclic train
on each side. The standard tank remains milestone 011 until the transmission,
frame and chain candidates pass integration. Small planetary gears, pin supports,
bevel gears, input bearings, clutch, brakes and control connections remain open.

## Identity and ownership

| Mark | Component | Installed quantity | Survey identity |
|---|---|---:|---|
| M287 | Large sun pinion | 2 | P_5aa2cc682109c570 |
| M280 | Large planet pinion | 6 | P_ae2f5af8c4df4fd4 |
| M279 | Large internal spur ring | 2 | P_72f5578f29060f57 |
| M315 | Gear-case gasket | 4 | P_0fce7125f6c176ec |
| M256 | Cross-shaft retaining ring | 2 | P_7675081175233978 |
| M288 | Planet-disk washer | 2 | P_c8ab527b09d4e561 |

Each `PortPlanetTrain` / `StarboardPlanetTrain` is owned by the corresponding
`TransmissionCore` group. Native links share six component definitions. The
sun pinion is splined to the single M255 cross shaft; each group has three
planets. Ring/case mounting and rotating-member relationships are separate
interfaces within the assembly. Pin carriers are not yet a completed joint.

## Evidence and tooth construction

Original SNL 144, 165, 251, 253 and 274, Plate22, and HB126–127 were inspected.
`transmission_planet_sources.json` preserves source rows and scan hashes. HB126
prints 18, 27 and 72 teeth for the sun, planets and internal ring, all 4–5 DP.
The pitch-circle relation is `72 = 18 + 2 × 27`. Holding the large ring gives
the handbook's 5:1 low ratio. Three planets per side follow HB122 and SNL144;
equal 120-degree spacing and their clocking remain reconstruction decisions.

The two-pitch tooth-depth interpretation follows the general Fellows stub
system described by [Janninck's gear-design article](https://ik.imagekit.io/agmamedia/gt/issues/1188x/janninck.pdf)
and the [Martin Gear Manual](https://www.autotoolworld.com/assets/martin_tools/Martin_Tools_Sprocket_Gear_martin-gear-manual.pdf).
These are tooth-system references, not evidence of the tank's cutter or pressure
angle. A 20-degree pressure angle is assumed; the technical reference also lists
a 14.5-degree variant. Pitch radii are 57.15, 85.725 and 228.6 mm. Addendum is
5.08 mm and dedendum 6.35 mm, leaving 1.27 mm radial tip clearance.

Each involute flank is interpolated through 16 analytic samples with a cubic
B-spline. Independent dense samples measure the numerical fit residual. The
curves are axially extruded into closed native solids. Below-base-circle root
continuations are radial; generated cutter fillets and exact undercut are absent.
Shaft splines use the inherited rectangular envelopes, not involute tooth curves.
External teeth are thinned by 0.2 mm at their pitch circles; internal tooth voids
are enlarged by the same amount, for nominal 0.4 mm combined pair backlash.
These clearances are assumptions, not historical manufacturing tolerances.

## Axial stack and revised receivers

The 52.251 mm gear face follows a 72-pixel Plate22 pick at the inherited local
scale. Its outer face sits 1.5 mm inside the carrier rim. The sun hub extends
toward a separate M256 C-ring, seated in a new groove at each M255 shaft end.
The ring has 0.15 mm axial clearance in its groove and a 0.15 mm gap to the sun
hub. The central shaft geometry is protected outside the new end grooves.

M288 occupies the actual carrier-to-bush interval: 4.057 mm thick with 0.1 mm
clearance at both faces. That interval uses the flange face of M296, not the
earlier plain journal station. Washer diameters and all clip dimensions remain
estimates. Spring behavior, installation deformation and running loads are not
modeled.

HB120 says that the same bolt passes through the spur ring and both case halves.
SNL253 lists four M315 gaskets. The model uses an inferred 12 mm ring flange,
two 0.2 mm gaskets per side and receiving rabbets in the case halves. Bolt holes,
bolts and flange stiffness remain pending. M278's exterior brake surface is
retained.

Printed tooth dimensions force a correction to M277's earlier bore estimate.
The ring root reaches radius 234.95 mm, beyond the old 230.051 mm case bore.
The revised local bore is 243.114 mm, outside the ring's 242.964 mm body radius.
A 14 mm wall and 8 mm transition enlarge the local outer shoulder to radius
257.114 mm, 13.274 mm beyond the earlier trace. This is a documented contour
reinterpretation requiring further source review, not a precision fit to the
scan. Five earlier occurrences change: both pairs of case halves and one shaft.

## Validation and visual review

The native candidate, report, STEP, interface trials and inspected images live
in `experiments/drive_chains/transmission_planet_build/`. Reproduce with:

```sh
python3 cad/003_FullTank/experiments/drive_chains/transmission_planet_probe.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/check_transmission_planets.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/render_transmission_planet_review.py --stage cad/003_FullTank
```

The probe reopens the native file, checks inventory and link placements, tests
new/changed solids against the retained fixture and current physical tank, and
exports/reimports the changed set. Tooth counts are checked from native analytic
tip-cylinder patches. Saved native geometry supplies mesh gaps, washer/retainer
stops, gasket contacts and protected-shaft comparisons.

The independent checker shifts the clips, sun hubs, washers and ring flanges
into their receiving stops, deliberately misclocks each planet, and checks nearby
compatible gear phases. Gear-only phase trials are diagnostic checks; they do
not change the saved standard configuration or qualify full mechanical motion.

The saved candidate contains **957 valid single-solid occurrences**: 18 new,
five changed and 934 retained unchanged. All 110 material candidate pairs are
clear. Twenty-four specified interface checks pass, as do native tooth counts
on ten gears and six planet-center/mesh-gap checks. Nominal tooth gaps are about
0.188 mm; the model includes backlash and is not a loaded-contact state. The
23 new/changed solids retain their volumes and centers through STEP roundtrip.
The central protected shaft region has zero material difference.

All 28 local trials have their expected outcomes: fourteen axial-stop failures,
six misclocked-planet failures and eight compatible gear-phase trials. This is
not a full parameter or motion qualification. Maximum sampled involute fit
residual is below 0.000084 mm; that numerical approximation error says nothing
about confidence in the assumed tooth system.

Seven rasters were actually inspected and bound to the saved native/report
hashes in `visual_review.json`. The retained
[cutaway](../../intermediate_snapshot_iso_transmission_cutaway_001.png) and
[gear detail](../../intermediate_snapshot_detail_transmission_gears_001.png)
are isolated transmission checkpoints, not standard milestone 012.

The direct Plate22 comparison overlays the actual horizontal native section at
the shaft axis. Its source scale is unchanged. Three planets at 120 degrees
cannot all lie in that plane; the drawing may show a composite section. This
limits visual comparison of pin placement but does not justify moving individual
gears to force a two-dimensional match. Native front/oblique views expose the
sun and planets without the carrier hiding them; these are inspection views.

The close comparison reveals a substantial sun-outline discrepancy: the
printed-dimension model is smaller than the illustrated central dark profile.
Ring/planet proportions also differ. Actual axial gear faces map to source
pixels 902.067/974.067 versus the selected 895/967 width picks. The 7.067-pixel
(5.129 mm) station residual exceeds the earlier four-pixel pick allowance.
The model retains the printed tooth dimensions and carrier-relative placement;
source component boundaries, local calibration and illustration conventions
need further reconciliation. These differences are not a historical-fit pass.

## Outstanding reconstruction

The subsequent [pin-support checkpoint](I03-large-planet-supports.md) now provides
the following pin/bush/ring occurrences and physical receivers. Their nominal
fit checks pass, but the source carrier rim and ring-bolt position need further
reconstruction. The notes below record this gear checkpoint's research handoff.

M284 pins, M282/M283 bushings and M285 pin rings need geometry and physical
receivers in the existing carriers. SNL251 names M272 for the large bronze
bush, whereas the SNL43 catalogue and HB122 name M282. This identity conflict
must remain explicit until reconciled; it cannot be silently merged into a new
part occurrence.

Further inspected originals SNL43 and SNL137 and their rows are retained in
`transmission_planet_pin_research.json`. SNL137 specifies each large-pin assembly
as an M284 pin, M313 nut, 3/16 × 2½-inch split pin and ½-inch expansion plug.
Those assemblies are the next geometry increment; their survey assembly record
must not add a duplicate physical pin.

Gear tooth pressure angle, backlash, root form, bore and spline geometry remain
approximate. Case fastening, casting blends, gasket holes, full uncertainty
propagation and historical running fits are unfinished. The previously recorded
central-input offset and high-speed drum diameter conflict are unaffected.
