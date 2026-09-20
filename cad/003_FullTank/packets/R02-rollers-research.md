# R02 — roller and support preparation

Source inspection, 20 September 2026. No physical roller or support geometry is
added by this preparation record. Wheel/roller shapes were layout-only at that
point; see [R02 implementation](R02.md) for the subsequent populated stacks. Populate
standard supports before returning to posing. R01/R03 track counts and pitch
remain fixed; an inferred support must not silently stretch a track link.

## Assembly count and scope

HB141 explicitly gives 28 spring-equipped and 30 plain LOWER assemblies, with
alternating types. HB142 separately describes two upper assemblies, one per side.
A symmetric working arrangement would therefore have 14 spring and 15 plain
lower stations plus one upper station on each hand. Longitudinal stations still
require identification against the side drawing and the actual solved track.

SNL197:002 is the spring-equipped parent quantity 28. It contains the ordinary
roller assembly plus M1336 spring and two M1334 plates. SNL197:007 quantity 58
already INCLUDES those 28 base assemblies. Note (gp) and survey issue SURVEY_09
explicitly prevent summing 58 + 28. The base contains two M1332 rollers, two
M1335 rings and one M1333 tube. Pins, bushes and U-bolts are separately installed.

The SNL shared quantities also read 58 tubes/pins, 116 rollers/bushes/rings/staples.
They match the 58 lower stations. The handbook's separate M1341 upper roller
identity exists in the survey only through HB140/237, not an SNL part row. HB237
lists the top assembly's shared pieces separately, with two M1341 rollers per
station. Transferring two handbook upper assemblies thus adds shared components
beyond those SNL totals. Retain that configuration/quantity-scope difference;
do not remove two lower stations merely to force all totals to 58. SNL146:028
SH294A top-roller cover is specifically a first-100 item under note (gb).

## Printed controls and geometric conflicts

HB141 prints:

| Feature | Source value | mm |
|---|---|---:|
| Lower shell internal spacing | 22.25 in | 565.15 |
| Roller outside diameter | 8.75 in | 222.25 |
| Lower roller width | 4.875 in | 123.825 |
| Pin length | 25.75 in | 654.05 |
| Pin diameter | 2.247 in | 57.0738 |
| Tube length | 21.5 in | 546.1 |
| Tube outside / inside diameter | 3.812 / 2.75 in | 96.8248 / 69.85 |
| Spring stated diameter | 1 in | 25.4 |
| Spring loaded length at 2,500 lb | 6.652 in, three coils | 168.9608 |
| Spring stated outside diameter | 3.937 in | 99.9998 |
| Ring thickness / width / stated diameter | .187 / .375 / 3.531 in | 4.7498 / 9.525 / 89.6874 |

Original HB141 was directly inspected on the right half of `MarkVIII071.jpg`.
It confirms these spring/tube figures. If the 1-inch spring diameter denotes
wire, an OD of 3.937 inches gives an ID of 49.1998 mm, which cannot surround the
96.8248 mm tube shown in HB89/138. Treating 3.937 inches as the inside diameter
would instead allow 1.5875 mm radial clearance and give OD 150.7998 mm. That is
a potentially useful documented reconstruction, **not** a source correction.
The next geometry pass must choose and record this interpretation explicitly,
retain the literal printed OD, and check the resulting spring/plate/roller fit.
No force, stress or working suspension performance is established by that choice.

SNL165:018 describes M1335 stock as 3/16 × 3/8 × 12.56 inches. Its rounded shape,
section orientation, gap and groove are not established by the stock length.
HB141's stated 3.531-inch ring diameter also lacks an inside/mean/outside reference.
Recover an explicit installed ring/groove interpretation before using it as a
retainer. Do not scale the sleeve to conceal the disagreement.

SH642B is a revolver-port Belleville spring (SNL138:028), not the roller spring
M1336. Its dimensional issue belongs with the port-cover hardware. The earlier
R02 queue acceptance mention must not make roller reconstruction depend on it.

## Visual topology and native modeling direction

Inspected HB88/89 and repeated HB136/137/138 sections. These show:

- Lower M1332 rollers have two broad running rims with a recessed waist; they
  are not simple flat disks. Two rollers ride the paired rail channels per shaft.
- Upper M1341 rollers have a different one-sided flange/hub form; preserve that
  distinct definition and mirrored installation.
- The hollow tube bridges two end bushes around an oil-drilled fixed pin.
- Spring-equipped units have two formed/dished plates and a helical spring
  around the tube. Plain units retain the same paired lower rollers without
  those spring/plate parts.
- End U-bolts secure shaped pin ends to separate angle supports; the hull plates
  are penetrated at the shaft line. Model openings and owned supports together.

Use revolved, source-proportioned profiles for roller/tube/bush/plate geometry,
with printed dimensions as controls and unprinted curves separately approximate.
Model one complete plain and one spring stack, plus the distinct upper stack,
before repetition. Include pin bores, bushing clearance, retainer grooves and
U-bolt/nut/washer clearances. SNL4:021–030 / 5:001–002 identify the support runs: M2078, M2079, M2080,
M2081B/A, M2082B/A, M2083B/A, M2084B/A and M2085. Their printed quantities
are 4, 4, 4, 2/2, 1/1, 2/2, 2/2 and 4 respectively. These are extended support
angle pieces, not one bracket per shaft; do not repeat each whole source mark
at every roller station. Note (gk) resolves No. 5's inner counterpart: M2175 and M2176 roller-inner-skirt
angles replace the outer M2082A/B run. The field convention consequently numbers
eight outer and nine inner pieces. Retain the shared angle identities when
adding their roller-support role; do not create duplicate physical angles.

Derive stations against the native link rail surfaces and leave source station
picks independently visible. Establish both a contact/gap report and candidate
material intersections against skirts, side plates, tracks and neighboring
rollers. Opening and support geometry must follow the same station datums.
Drive/idler shafts, bearings, wheel contours and tension adjusters remain the
other R02 families; the existing drive-pitch conflict still applies.

SNL Plate 29 (`assets/p301-geometry.png`) was also inspected. It provides a
22.25-inch transverse shell-gap dimension and a drawn inch scale. Its spring
appears appreciably larger than the tube, supporting further investigation of
the inside/outer-diameter interpretation above. It does not print a corrected
spring diameter. A future local YZ calibration should use the printed transverse
gap, hold out the roller diameter to expose unequal scan scale, and retain pick
uncertainty. The existing longitudinal XZ calibration must not be applied to this
transverse section. The circular/formed shoulder profiles are visible enough to
replace the current roller envelopes with actual revolved sections.

## Initial longitudinal station picks

Re-inspected the locked SNL2 foldout at its native 1900 × 750 pixels. Twenty-nine
lower shaft centers are visible on one hand. Initial manual picks below are
research estimates with ±6 pixel uncertainty; recheck before geometry promotion.
The last two positions depict complete roller outlines, whereas most earlier
positions show the shaft/staple detail in the section. SNL197 identifies the
second-last outline as the spring-equipped assembly (Plate 2 callout 15), and
the last as the plain assembly (callout 14). This supports an alternating
plain/spring sequence beginning and ending plain, rather than adding those two
outlines to a previously counted 29-station set.

Front-to-rear pixel (x,z):

```
(202,444), (259,477), (319,505), (382,521), (445,534),
(509,540), (559,545), (611,548), (664,552), (705,555),
(744,557), (783,559), (832,559), (872,561), (911,562),
(951,563), (1002,564), (1042,564), (1080,564), (1120,564),
(1171,565), (1210,565), (1250,565), (1290,565), (1345,565),
(1402,566), (1458,565), (1550,561), (1647,549)
```

The existing track route's closure/clearance correction means a source pick is
not automatically a valid roller-to-rail contact datum. Preserve these picks
independently and report any offset needed for contact with the actual native
rails. Do not refit the source calibration to conceal that difference. Support
ownership for the final rear stations and the separate upper station still needs
specific geometry/evidence reconciliation.

## Supplemental image inspections

These inspections use existing files without modifying the frozen sources.
Their hashes below must join the authored model lock when the geometry consumes
them; a documentation inspection does not refresh an existing build's lock.

| Source | SHA-256 |
|---|---|
| `references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate88.png` | `b1b074e28cb25fef4deb17b246c67db55f58e6825093e8aa8d9af59e3c954a36` |
| `references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate89.png` | `d45cb3614a938f2607b738054675e1af49e0da558a3b1eabeb7a3bbf3f62c555` |
| `references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate136.png` | `908a100e22116d7f0583966d6d8f671e7fe4989a94953d0a655ccf3a6fd1286a` |
| `references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate137.png` | `111153f7632057b1a2c12b22438b9b184124aac1c1cc649deae980cde52b0691` |
| `references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate138.png` | `dd6e1758ce04ff051b5574528060298a3de1289fb12cf05b96e729dbb6a9000c` |
| `references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/original_scans/MarkVIII071.jpg` | `f62e0fc8194dbae7785eb6659bab6cdd07f42fe3aa6c9624bee27e772681e1d8` |
| `references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p301-geometry.png` | `cdf7beba996664041ebe32209f0d8ef1b0aff10446e05b4de8c9446af78a5944` |

## Upper station review during implementation

HB144 says the inner ends of the upper rollers are reached through the engine
room. Reinspection of SNL2 identifies a likely shaft feature at pixel
(1025,248), at the rear roof-contour bend just inside that compartment. This
replaces the initial unsupported forward trial pick (400,255). Retain ±12 pixel
uncertainty; exact supports/cover geometry remains unresolved. Source X is
4158.626 mm. Against the current reconstructed track, installed Z is
2025.153 mm versus the source pick 2057.111 mm (−31.957 mm). No source calibration
was changed. The rear position cleared the existing physical installation in
the preliminary probe; authoritative validation is recorded in the implementation
packet and generated reports.

## Support-run follow-up for the next geometry stage

Rechecked the original frozen SNL rows while the roller delivery was qualifying.
M2176 (SNL4:019) is 6⅝ inches / 168.275 mm long, quantity two. M2175
(SNL4:020) is 32⅜ inches / 822.325 mm long, quantity two. These printed lengths
are independent controls for the inner-skirt pieces shared with the support
family; they must not be stretched merely to span inferred shaft stations.

SNL4:021 through SNL5:002 total 30 support-angle occurrences. Adding the four
M2175/M2176 inner pieces gives 34: sixteen outer and eighteen inner runs. This
fits the eight-outer/nine-inner convention and note (gk). It is not 34 pieces
per side or per roller. No. 4/6/7 A/B identities are reused diagonally between
outer and opposite inner positions, as their source descriptions state.

The SNL2 callouts 6–13 identify the eight lower runs. A provisional station
grouping for investigation is Lower00–01, 02–03, 04–05, 06–11, 12–15, 16–17,
18–22 and 23–28. This is a visual research hypothesis, not an authored assembly
or an accepted bracket-to-shaft mapping. Check the inner No. 5 split, rear
outline stations, detachable pin retention, angled versus level seats and the
printed M2175/M2176 lengths before generating solids.

SNL146:028 SH294A is specifically the top-roller cover, quantity (2), first-100
note (gb). SNL147:001 M2065 is a different detachable plate **above roller
pinions**, quantity two; do not use it as a lower-roller clamp cover. HB143–144
separately describes removing upper support angles and lower plates on the
support angles before withdrawing roller pins. That establishes removable
retention topology but does not identify a separate source mark for every
lower retaining plate. Further evidence is needed before assigning those
plates to the long-angle or fastener inventory.

## Upper support topology resolved for the next subset

HB141 explicitly describes suspension of the pin by the U bolt beneath the
angle toe. Reinspection of HB88/89 and SNL29 distinguishes the flange above the
shaft from the separate lower skirt reinforcement visible well below it. The
former model's bottom pin flats were reversed. See
[upper support implementation](R02-upper-supports.md) for corrected upper-facing
flats and the inferred angle/clamp dimensions.

HB:nomenclature:221:019 supplies the previously unpopulated top support identity
M2092, four per vehicle (`P_19d6f046e2cd29dd`). The original right-hand page of
`MarkVIII111.jpg` confirms M-2092 / 4 / Roller support angle top. This is separate
from both the 34 lower runs and SH294A covers. Its longitudinal length, stock and
attachment-hole pattern remain unprinted in the located evidence.

## Lower-support preparation during idler-mount qualification

Read-only source and station review, 20 September 2026. No support geometry or
station inputs were changed during this research.

SNL31:001 identifies a further complete, independently checkable allocation:
**76 half-inch × 7/8-inch hex-head bolts**, survey identity
`P_be4b63e1b295445c`. Multiplying each application count by the support quantities
on SNL4–5 reconciles exactly:

| Support | Installed angles | Bolts per angle | Installed bolts |
|---|---:|---:|---:|
| M2078 / M2079 / M2080 | 4 each | 1 | 12 |
| M2081A/B | 2 each | 4 | 16 |
| M2082A/B | 1 each | 4 | 8 |
| M2083A/B | 2 each | 3 | 12 |
| M2084A/B | 2 each | 3 | 12 |
| M2085 | 4 | 2 | 8 |
| M2175 | 2 | 3 | 6 |
| M2176 | 2 | 1 | 2 |

These short bolts are distinct from the 116 U-bolts already holding the 58
lower pins. The 22.225 mm stock length constrains their eventual joint stack;
identify the detachable plate/angle connection and nut/washer allocation before
placing generic wall bolts. This allocation alone does not identify every
mating component.

The earlier proposed eight-run grouping was tested numerically against the
current **installed** pin centers. It remains a hypothesis:

| Run | Lower station indices | First-to-last pin span, mm | Maximum departure from a straight line through end pins, mm |
|---|---|---:|---:|
| 1 | 00–01 | 358.444 | 0 |
| 2 | 02–03 | 402.491 | 0 |
| 3 | 04–05 | 387.713 | 0 |
| 4 | 06–11 | 1350.876 | 24.275 |
| 5 | 12–15 | 717.212 | 0 |
| 6 | 16–17 | 241.080 | 0 |
| 7 | 18–22 | 1024.589 | 0 |
| 8 | 23–28 | 2155.211 | 57.436 |

The pin span is not the support's stock length. In particular, runs 4 and 8
cannot acquire full planar toe/pin seats simply by extruding a straight angle
between the current end stations. Revisit source grouping, local bending and
the track-driven station offsets before constructing them. A curved/formed
support would be a new explicit approximation, not evidence of historical form.
The front runs also require inclined pin flats and clamp frames; the present
shared pin and clamp geometry is oriented with an upward flat. A native rigid
rotation about the transverse shaft can preserve the round bearing interface,
but its oil port, U-bolt, washer and nut locations must move together and be
checked against the hull and rails.

SNL2 rear callouts 15 and 14 were checked against catalogue records: SNL197:002
is the spring/flange roller assembly, and SNL197:007 is the underlying plain
roller assembly. They are not extra drivetrain bearings or extra rollers to
add on top of the 58 lower assemblies. The last two currently selected stations
match that spring/plain order; exact rear support attachment remains unresolved.
Keep the printed M2175/M2176 lengths fixed while investigating the inner No. 5
split and do not expand the eight-run hypothesis into claimed source geometry.

### Isolated first-three-run native probe

A temporary `/tmp/lower-support-runs-probe/LowerSupportResearch.FCStd` tested
simple L envelopes on the port bank only, outside the authored/delivered model.
The trial spans the first two pins of each of runs 1–3 and uses arbitrary
60 mm end extensions. It rotates each affected pin/oil-plug assembly and both
clamp groups together about the transverse shaft axis by 33.604821°, 19.373391°
and 5.801247° respectively. The rotating sleeves and wheels stay unchanged.

All twelve toe/pin faces have effectively zero native gap and approximately
328.818344 mm² contact area. The six angle envelopes have no detected material
overlap against the supplied native running-gear/hull geometry. This check does
**not** requalify every rotated clamp against all other parts, or qualify the
opposite bank. Their nearest inner/outer skirt faces are **2 mm away**, exposing
the difference between the current 12 mm side-wall offset and 10 mm skirt stock.
The next authored support geometry must resolve its actual attachment plane and
owned holes; a 2 mm gap is not an attachment. The prototype has no detachable
retaining plates, attachment bolts, source-qualified end lengths or cast/formed
corner detail. It is a useful interface probe, not an additional completed part
count or a preserved tank milestone.

For implementation, consider putting the support inclination on the existing
roller-unit datum instead of giving only its pin and clamps extra transforms.
The roller validator already normalizes repeated stacks by their unit frames.
A whole-unit inclination keeps that contract simple and rotates round bearing
parts about their own common axis. It still needs native checking: a helical
spring and split retaining rings are not fully axisymmetric, so their phase and
external clearances must not be assumed unchanged. The temporary probe above
rotated only pin/plug and clamp groups; it did not test this alternative.

## Complete lower-support installation experiment

The [reproducible experiment](../experiments/lower_supports/README.md) now builds
all 34 angles and 76 attachment bolts in a separate FreeCAD document. Direct
inspection of original SNL4, SNL5 and SNL31 confirms the quantities and short
bolt notation. SNL31:001 does not specify nuts/washers, unlike the immediately
following entries. A tapped joint is therefore a useful but unproven hypothesis.
The 22.225 mm shank leaves only 5.875 mm beyond a 6.35 mm angle and 10 mm skirt,
which cannot receive the modeled 11.1 mm nut plus washer.

The revised inner No.5 allocation puts the 168.275 mm M2176 over Lower12 and
the 822.325 mm M2175 over Lower13–15, with a 4 mm inferred gap. Both exact native
lengths survive a fresh reopen. This is stronger geometrical evidence than
treating the short piece as an unexplained auxiliary, but does not establish
the historical arrangement. The three long-part bolts and one short-part bolt
retain the independently recorded SNL applications.

The first six complete roller units per hand rotate about their own transverse
axes; 246 affected physical components are included in the external interference
check. The angle wall moves to the actual 10 mm skirt outer plane, resolving
the earlier 2 mm gap. The trial's 348 pin/washer bearing faces, 76 bolt-head
faces and 34 hull contacts all have nonzero area. No material overlap above
0.00001 mm³ remains in 1,502 tested candidates. The native reopen checks all
424 pin/washer/bolt seats and rejects 0.2 mm separated test contacts.

Source topology still limits promotion: the drawn No.8 run most clearly
corresponds to the four small pin features preceding the two large rear roller
outlines. Extending it over both rear rollers is an explicit hypothesis. The
unhanded M2085 mark has four occurrences; a curved reconstruction with asymmetric
hole spacing cannot automatically claim one interchangeable historical shape
on both inner/outer faces. Keep any construction variants tied to the same
source identity while flagging interchangeability as unverified, or revisit
rear support ownership when stronger evidence is found. The cubic transitions
in runs 4/8 are fitted to installed stations, not traced manufacturing contours.

HB144's removable plates on the support angles are still unlocated in the
identity inventory. No additional invented plate counts were added. The next
implementation can promote supported partial angle/bolt geometry while keeping
that missing retention family explicit; this research does not require user
approval to continue. Main native delivery and snapshots remain at stage 007.
