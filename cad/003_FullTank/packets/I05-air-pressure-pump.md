# I05 — air-pressure pump and transmission attachment

Status: **source preparation; no pump geometry built** (21 September 2026).
The next installation uses the accepted approximate MX5 transmission checkpoint.
This packet spans FuelPressure and its Drivetrain mounting interfaces. It is not
the transmission mechanical lubricator, the engine oil pump, or the B6205
input-pinion bearing-housing support.

## Identity and quantity

One engine-driven pump, survey assembly `P_dd55a02fabc8964b`, is enumerated by
SNL159:003–020. Its composition and shaft subassembly were checked visually
against original SNL pages159 and209. SNL Plate5 (printed279) and HB Plate115
(printed195) show the same four-cylinder form. HB Plate22 (printed29) repeats the
views; repetition is not independent dimensional confirmation.

| Item | Physical quantity | Source record |
|---|---:|---|
| SH901F air-hole cover | 1 | SNL159:005 |
| SH903A base | 1 | SNL159:006 |
| SH900A bearing/end cover | 2 | SNL159:007 |
| SH901C bushing | 2 | SNL159:008 |
| SH901B check nut | 4 | SNL159:009 |
| SH900C cylinder | 4 | SNL159:010 |
| SH901E displacement plug | 4 | SNL159:011 |
| SH901D piston | 4 | SNL159:012 |
| SH900B pulley | 1 | SNL159:013 |
| SH900D cam shaft | 1 | SNL209:022 |
| Plain US half-inch hex nut, shaft retention | 1 | SNL209:023 |
| SH901A spring | 4 | SNL159:015 |
| US 3/8 × 1-1/4in base bolt, plain nut and lock washer | 4 sets / 12 pieces | SNL159:016;30:004 |
| Woodruff No.5 key | 1 | SNL159:017;115:010 |
| Q52A square-head 1/8in pipe plug | 7 | SNL159:018 |
| US 5/16 × 3/4in hex cap screw | 8 | SNL159:019 |
| US 3/8 × 3/4in hex cap screw | 6 | SNL159:020 |

This expands to **63 physical pieces**, including the four base-attachment sets,
before the drive belt, transmission brackets and studs. This is a source count,
not geometric coverage. Port/plug allocation must be checked again when the air
lines are installed; a closed catalogue pump may differ from the connected
installation. Pump and shaft assembly records are containers. The
base-bolt survey identity describes a set; splitting it into three physical
pieces must retain that identity as the set's provenance and must not duplicate
it as a fourth solid. No invented survey identifiers are required.

The survey lists no configuration membership for the pump assembly. The decision
is to carry this documented equipment provisionally into the selected production
reconstruction, with 1925 handbook/1928 catalogue applicability retained. SNL's
%, X and & notes concern requisition/issue classification, not tank variants.
The handbook's 80-gallon tank description is not a reason to replace the
separately selected production fuel tanks.

## Form and useful dimensional controls

The inspected views show two cylinders on each sloping side of a hollow base,
a shaft along the two cylinder stations, and a grooved pulley at one shaft end.
Triangular three-screw bearing covers enclose separate bushes. Each cylinder has
a two-screw mounting flange. The section exposes the pistons, displacement plugs,
return springs and cam shaft. These components need separate native solids;
the section does not justify arbitrary solid cylinder placeholders.

The end view suggests bank axes roughly 45degrees from vertical. This is a visual
estimate. Overall length, width, pulley diameter, shaft journals, piston stroke,
spring dimensions, cam profiles and internal port routes are not dimensioned in
the inspected figures. Their reconstruction values and bounds must be authored
before building. Do not scale from a nominal pipe-thread size as if it were an
outside diameter.

SNL18:011 explicitly gives SH900G as a **link V belt, 54in long, 5/8in wide,
28degree angle** (1371.6mm,15.875mm,28degrees); the original page was inspected.
The length's pitch/inside/outside convention is unstated. Treat it as a closure
constraint with that uncertainty, not an exact pulley-center dimension. The
adjacent 60in belt belongs to the transmission mechanical lubricator. No.5 key
dimensions require a historical standard or a declared estimate; its number
alone is not a millimeter dimension.

## Installation and ownership

HB printed31 explicitly places the pump above the clutch, driven by the V pulley
on the engine-shaft brake; its own cam shaft operates the pistons directly.
HB Plate15 (printed23) shows the pump over the input-bearing housing with the
belt descending to the drive pulley. HB32 describes a frame above the cardan
shaft. These support the broad placement, not an exact mounting transform.

The catalogue separates the following installation items:

| Owning installation | Item | Evidence |
|---|---|---|
| Transmission assembly | One left MX101 and one right MX100 pump bracket | SNL251:018/019;36:012/013 |
| M264 input cover | Two MX98 stud assemblies | SNL77:003;240:019–023 |
| M250 input-bearing housing assembly | Two MX99 stud assemblies | SNL112:013;231:020–026 |
| Pump base to supports | Four 3/8 × 1-1/4in bolt/nut/washer sets already counted above | SNL159:016;30:004 |
| FuelPressure pump drive | One SH900G link V belt | SNL18:011 |

MX98 has a printed half-inch diameter and 2-7/8in length, with 1in US and 7/8in
SAE thread spans. Each owns a half-inch castle nut and a 3/32 × 1in split pin;
the latter explicitly names the air-pressure pump. MX99 has a special MX102
half-inch SAE jam nut (3/8in thick), a 3/8in SAE plain nut, a half-inch SAE plain
nut and **two** 3/8in lock washers per stud. This mixed hardware suggests a stepped
or adjustable arrangement; its exact construction remains unproved. Resolve the
bracket shape and stud axes from installed views before making receiver holes.

Own the pump body and its internals once under FuelPressure. Own transmission
brackets and their transmission attachment hardware once under Drivetrain, and
reference their mounting faces from the pump installation. The four base-bolt
sets must occur once across that interface. A combined experimental document may
contain both subsystem containers until standard-tank integration.

B6205, capA7679, two A7681 stud/nut/pin sets, stiffenerA7680, shimA7682 and eight
3/8 × 2-1/4in attachment sets form a separate input-bearing support family.
Their split-clamp relationship is supported by the catalogue; a particular tall
pedestal shape or mounting location has not yet been established.
Relevant records are SNL41:030–034,56:011,217:013,222:021,241:006–010 and25:017.

## Next construction cycle

1. Establish an explicit approximate pump scale using the illustrated shaft/nut
   and printed fastener controls. Retain pixel picks, original image hash and
   disagreement between views. Check the installed envelope and belt closure
   against the existing clutch-stop pulley before freezing the scale.
2. Build the hollow base, triangular covers, bushes, shaft, V pulley and four
   separate cylinder/piston/plug/spring groups. Record static cam phases and
   undocumented internal passage/valve assumptions. Add the source hardware.
3. Reconstruct MX100/MX101 and MX98/MX99 around named M250/M264 datums; preserve
   the existing grease feed and MX25 installation, including their open conflicts.
   Check access, pulley alignment, belt route and all nearby component clearances.
4. Reopen the saved native assembly, reconcile the source counts, verify closed
   solids and critical interfaces, then round-trip changed definitions through
   STEP. Perturb pump scale and support height coherently rather than introducing
   unrelated dimensional variation into each occurrence.
5. Compare the assembled and sectional native views with SNL5/HB115 and HB15.
   Save a progression image when actual geometry improves; source preparation
   alone does not warrant another isometric snapshot.

The [source dossier](../experiments/drive_chains/air_pressure_pump_sources.json)
preserves exact survey records, linked identities, selected assembly edges and
source hashes. No part of this packet yet counts as populated standard geometry.
