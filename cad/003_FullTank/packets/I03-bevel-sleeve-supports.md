# I03 — bevel-wheel sleeve supports and shaft assembly passages

This increment installs twelve separate parts: two M259 flanged sleeves, two
M261 inner bushes, two M262 outer bushes, two M310 oil retainers, two headless
set screws and two M300 cover dowels. Five new definitions and the existing
M300 definition supply the two handed AppLink groups. The native fixture also
receives seven revised shaft, case, cover, small-sun and small-sun-bush occurrences.
It continues [small-sun retention](I03-sun-retention.md); it does not complete
the bevel drive, transmission or standard tank.

## Sources and assumptions

Original SNL44/217 establish the sleeve and bush identities and quantities.
SNL99 allocates a set screw to each bevel-wheel assembly; SNL204 identifies
M261 as its receiver and prints 5/16 by 1/2 inch. SNL77 assigns two bronze M300
5/8 by 1/2 inch dowels to the M264 cover. SNL164 identifies M310. Nested assembly
rows are not counted as additional physical parts. The source record extracts
and inspected original-image hashes are retained in
[the source register](../experiments/drive_chains/transmission_bevel_sleeve_sources.json).

The sleeve has separate inner and outer running interfaces. The nominal gaps
are 0.15 mm at the shaft/inner bush and bush/sleeve, 0.10 mm at the outer bush,
and 0.20 mm at the oil retainer. The set screw crosses sleeve and inner bush;
the reused dowel crosses the outer bush and cover. Split casting bosses carry
the bushes, and counterbores receive the nominal oil washers. Thread form,
press fits, oil-sealing behavior and service loads are not qualified. Six
provisional flange holes follow the source's six-rivet joint count; their
circle, angular phase and exact gear-joint assignment remain assumed.

The first static trial used an inner-bush bore radius of 28.95 mm on the
28.8 mm shaft root. It had no assembled-state overlaps, but shifting the bush
60 mm intersected the rectangular spline crests by 39,566.872 or 20,404.538 mm³.
The [rejected trial](../experiments/drive_chains/transmission_bevel_sleeve_build/rejected_root_journal/local_passage_report.json)
and its generator/controls are preserved. Static clearance alone was
insufficient to establish a plausible assembly path.

The revised bevel and M268 small-sun journals have 35.5 mm radius. Their bushes
have 35.65 mm bore radius and 40.5 mm outside radius, with corresponding
40.65 mm sleeve/sun bores. They can pass the smaller outboard spline corners.
The M267 external splines, teeth, retaining groove and shoulder are preserved.
A larger ten-spline central shaft section, root/tip radii 35.5/41.5 mm, reserves
passage for a future M257 clutch. These diameters and the stepped-shaft
interpretation are reconstruction hypotheses. A nonphysical female bore gauge
checks passage; it neither represents a completed clutch nor adds a BOM item.

## Source registration remains unresolved

The [three-panel comparison](../experiments/drive_chains/transmission_bevel_sleeve_build/source_review/bevel_support_comparison.png)
shows the original, actual native section registered to the bevel center, and
the same section using the inherited output registration. Both use the same
0.725714 mm/pixel scale. The local relation `Y=(1534-source_x)*scale` aligns the
already centered case to the illustrated input axis. It differs from the
output datum by **32.113 mm**; the global calibration is retained.

The port sleeve occupies Y66.766–174.897 mm. Its outer bush seats on the existing
case inner wall at Y113 mm, a 0.211 mm adjustment from the selected source
boundary, and ends at Y169.817 mm. The oil retainer ends at Y172.317 mm. The
M267 sleeve still begins at Y206.284 mm, leaving a 31.387 mm gap from M259.
That gap is not a validated thrust stack. Reconciliation must consider the
bevel gear/clutch/shim geometry and both axial datums together.

The overlay visibly retains differences in shaft, sleeve and case contours.
The enlarged journals follow assembly requirements rather than precise source
diameters. Missing bevel gears, clutch rings, central clutch, shims and rivets
remain explicit. No adjustment of the source raster conceals the discrepancy.

## Verification and deliverables

The saved and reopened [candidate](../experiments/drive_chains/transmission_bevel_sleeve_build/TransmissionBevelSleeveCandidate.FCStd)
contains **1,129 valid single-solid occurrences**: twelve new, seven revised
and 1,110 previous occurrences unchanged. All 117 affected material pairs are
clear and all 326 specified interfaces pass. Direct material comparisons
protect the case outside the local bosses, shaft outside the revised bands,
sun outside its bore and reused dowel definition. All nineteen new/revised
solids pass native/STEP material comparison, both raw and with bounded Boolean
tolerance; saved shape tolerances are not inflated.

Independent checks cover 24 native radii, 24 actual bush positions, four
continuous annular bush sweeps and a continuous clutch-bore gauge along the
shaft. Five deliberately undersized bores produce interference. Twelve local
capture checks cover the set screws, dowels and existing small-sun retention.
Two definition reuse checks, four source-station checks, three actual shaft
sections and four deliberately displaced STEP comparisons also pass. These
83 checks establish nominal local interfaces and shaft-only passages; a
complete assembly sequence and operating transmission remain unqualified.

The [build report](../experiments/drive_chains/transmission_bevel_sleeve_build/report.json),
[independent checks](../experiments/drive_chains/transmission_bevel_sleeve_build/interface_checks.json)
and [visual review](../experiments/drive_chains/transmission_bevel_sleeve_build/visual_review.json)
bind the delivered files. Six rendered images are inspected. Standard tank
011, its opaque and 18% transparent views, and all previous snapshots remain
preserved. New cutaway snapshots record this isolated interior increment.

## Reproduce and continue

```sh
python3 cad/003_FullTank/experiments/drive_chains/transmission_bevel_sleeve_probe.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/render_transmission_bevel_sleeve_review.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/check_transmission_bevel_sleeve.py --stage cad/003_FullTank
```

Use `--output` on the builder and `--candidate` on the renderer/checker for
isolated trials. Visual review remains a separate inspection of actual rasters.

Next reconstruct M258A bevel wheels, M258B clutch rings, M260 shims, their rivets
and M257/M247 input components, while resolving the axial registration. The
M265/M266 brake-bearing cap/bush attachment remains open: the handbook's
high/low-speed shading does not securely identify its joint. Case fastening,
brakes/controls, lubrication, mounting and standard integration follow. All
other unfinished full-tank workflow packets remain active or queued.
