# I03 — clutch-stop anchor and operating linkage

Status: **verified development checkpoint; not historically qualified**, 23 September 2026.
This continues [the support checkpoint](I03-clutch-supports.md). The objective remains
the complete standard tank with identifiable interiors, before pose variants.

## Inventory and ownership

The candidate contains 1,821 physical occurrences, adding 35 components to
the 1,786-occurrence support assembly. Four receiving parts change: M4158 band,
M4159 lining, SH953A left supporting bracket and M4162 left clutch lever. The
remaining 1,782 inherited occurrences must retain their geometry and placement.
The inherited floor is replacement context and must not be duplicated at eventual
standard integration. These local counts are not additive to the tank inventory.

| Added components | Physical occurrences |
| --- | ---: |
| M4160 anchor and its six 1/4 × 1in button rivets | 7 |
| Two 1/2 × 2-7/8in bolts, two plain nuts and two lock washers | 6 |
| M4157 band pin and its 1/8 × 7/8in split pin | 2 |
| M4156 eyebolt, two SH955B nuts, two SH955A washers, two plain 1/2in nuts | 7 |
| M4151 rod and four SH955D nuts | 5 |
| M4152 rod pin and its 1/8 × 1in split pin | 2 |
| SH87A bell crank, SH955C spring and M4153 carrier | 3 |
| M4165 pin, 5/8in crown nut and 5/32 × 1in split pin | 3 |

The existing 19-piece band construction plus the anchor and six rivets accounts
for the 26 children in SNL8's band assembly. The native hierarchy nests those seven
additions in the existing band assembly; mounting bolts remain outside it.
Catalogue pin/rod/eyebolt assemblies
are not extra solids on top of their listed children. The single M4165 split pin
is the part corrected in the preceding packet; there is no extra M4150 shaft pin.

## Evidence and chosen mechanical arrangement

The [source dossier](../experiments/drive_chains/clutch_brake_linkage_sources.json)
retains the literal catalogue records and original-source hashes. HB118 explicitly
connects the brake band to a clutch-shaft bracket. HB150–151 connects the stop rod
to the left clutch lever and describes the bell crank, adjustable nuts, eyebolt
and opposing spring. The paragraph's antecedents are ambiguous; it does not fix
the carrier orientation or prove the chosen joint geometry.

This candidate uses a right-angle bell crank. The longitudinal stop rod enters one
arm; the spring-loaded eyebolt enters the other along the free band's tangent.
The crank plane tilts with that tangent, allowing a static connection to the
existing rolled eye. A fork at the other rod end pins to a real opening in M4162.
The carrier and anchor share the two catalogue anchor bolts on added SH953A lugs.
**That shared mounting, the selected left bracket and the crank orientation are
engineering hypotheses**, not details recovered from a dimensioned drawing.

The anchor has a curved shoe with six radial rivets and a tapered, offset web to
the mounting plate. The carrier routes outside the mounting lugs and below the
stop rod. The web toe finishes at the bracket's flat mating plane below the
plate's upper edge. The carrier return is centered 14mm beyond the anchor plate's
outer end; this clearance is an explicit estimate, not a source dimension.
New head recesses and shank passages are real cuts through the
band/lining/anchor stack. The free band's central throat continues along the
eyebolt shank, preserving its two pin-bearing ears. Rivet tails conserve the selected under-head blank
volume; head shapes and that length convention remain assumptions. The carrier
supports a shouldered M4165 pin with a separate slotted crown nut and split pin.
Nominal thread envelopes represent threaded joints; there are no modeled helices.

| Source constraint | Treatment |
| --- | --- |
| SNL31: two 1/2 × 2-7/8in anchor bolt sets | Preserve diameter, under-head length and quantities. Head, nut and lock-washer profiles are estimated. |
| SNL125: SH955B nuts 3/8in thick | Preserve 9.525mm thickness. Across-flats profile and fit are estimated. |
| SNL193: four SH955D 3/4in nuts, 1/2in thick | Preserve 19.05mm nominal thread and 12.7mm thickness. Two nuts lie on each side of the crank arm. |
| SNL267: SH955A ID1/2, OD1-3/8, stock1/8in | Preserve 12.7/34.925/3.175mm. Two washers seat the spring. |
| SNL134–135: named pin assemblies and split-pin sizes | Preserve all three split-pin diameters and leg-length budgets. Pin lengths, shoulder sizes and crown profile are estimates. |
| SNL219: SH955C spring, quantity one | Four turns, wire, diameter, free form and installed length are estimates. A continuous swept wire has ground end seats; no spring-rate or preload claim. |

HB188 uses different spring/bell-crank/nut identifiers and quantities. The SNL
configuration remains selected; the earlier packet retains those alternatives.
Plate95 and the inspected museum side-brake photo show a larger brake arrangement;
their profiles are not scaled into the small M858 stop band. The full SNL2 figure
and its clutch crop remain the qualitative arrangement reference. Engine is to
the left and transmission to the right in that drawing.

## Validation and remaining qualification

The [native assembly](../experiments/drive_chains/clutch_brake_linkage_build/TransmissionWithClutchBrake.FCStd)
has built, saved and reopened. All **112 independent checks**, **273 affected
material pairs including standard-tank context**, and **64 STEP comparisons** pass.
The exchange checks cover 25 definitions and 39 installed occurrences, including
the four receiving revisions. The existing 1,782 unaffected occurrences retain
their geometry and placements. Catalogue quantities and the native 26-child band
hierarchy are checked independently of the builder's total count.

A coupled trial moves the two mounts from X590/630 to X600/640mm, lengthens the
crank arm from 70 to 80mm, and changes the spring wire/mean radii from 1.6/11 to
1.5/10.5mm. It passes all 112 checks and 271 local material pairs.
That trial does not check standard-tank context or STEP exchange. A fresh nominal
reproduction and combined drivetrain qualification remain required.

The [checkpoint receipt](../experiments/drive_chains/clutch_brake_linkage_build/development_checkpoint.json)
records exact native and validation hashes. The
[retained failed trials](../experiments/drive_chains/clutch_brake_linkage_build/diagnostics/README.md)
show the interface problems corrected without relaxing acceptance tolerances.
Six final native views were inspected beside the retained full SNL2 context and
clutch crop. The large anchor/carrier profiles and linkage angles are inferred;
the source drawing does not establish their fit. This is a usable development
checkpoint, not historical or motion qualification.

Three progression images are preserved:
[installed isometric](../../intermediate_snapshot_iso_clutch_brake_001.png),
[mechanism detail](../../intermediate_snapshot_detail_clutch_brake_001.png), and
[end view](../../intermediate_snapshot_end_clutch_brake_001.png).
All 108 previous images and all 20 standard native documents are unchanged.
The progression now has 111 images; standard tank011 and its transparent-hull
companion remain the current integrated tank views. The
[source comparison](../experiments/drive_chains/clutch_brake_linkage_build/source_review/index.html)
contains all six local views.

Mounting, casting profiles, pin lengths, spring dimensions and all unprinted
coordinates remain approximations. The inherited axial-registration discrepancy
and the HB115 complete-clutch-length interpretation remain unresolved. A plausible
static fit does not establish historical accuracy or a working motion range.

Engine-frame reconstruction, engine receiving interfaces and the forward M581
control connection are next. Revisit the provisional bracket attachment with
those structures in place. Qualify the combined drivetrain before standard
integration, then regenerate opaque and transparent-hull views without overwriting
earlier images.
Remaining engine/cooling/air circuits, interiors, inventory reconciliation and
later selected poses remain full-tank requirements.

## Reproduction

Run from the repository root:

```sh
python3 cad/003_FullTank/experiments/drive_chains/clutch_brake_linkage_build.py
python3 cad/003_FullTank/experiments/drive_chains/check_clutch_brake_linkage.py
python3 cad/003_FullTank/experiments/drive_chains/check_clutch_brake_linkage_exchange.py
python3 cad/003_FullTank/experiments/drive_chains/render_clutch_brake_linkage.py
```

The builder accepts `--controls` and `--output`. Checkers and renderer accept
`--candidate`; `--local-only` restricts the geometry checker to the isolated
development assembly. Parameter changes require regeneration. Source-sized
hardware values must not be silently changed to fix an interface problem.
