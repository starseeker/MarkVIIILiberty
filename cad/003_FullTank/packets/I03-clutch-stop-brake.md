# I03 — clutch-stop brake and receiving throwout interfaces

Status: **development candidate, incomplete and not qualified**, 23 September 2026.
The subsequent [throwout packet](I03-clutch-throwout.md) develops the receiving
bearings, fork levers and main shaft while retaining the source-envelope questions.
The full-tank goal remains active. This packet retains the Rock Island first-100
target and the priority for standard assembled geometry before poses.

The [current native](../experiments/drive_chains/clutch_stop_band_build/TransmissionWithClutchStopBand.FCStd)
contains 1,681 physical occurrences. It adds the band, lining and seventeen rivets
to the qualified 1,662-component drum/flywheel checkpoint. The stop-drum diameter
correction changes 85 existing occurrences through the belt and pump supports;
1,577 other parent occurrences retain their geometry and placements. This local
candidate count is not additive to the standard tank inventory.

## Complete packet scope

The brake must ultimately contain M4158 band, M4159 lining, M4160 anchor plate,
three short button rivets, six long button rivets, fourteen copper lining rivets,
two anchor bolt/nut/lockwasher sets, M4157 band pin and split pin, M4156 eyebolt and
its nuts/washers, M4151 rod and four SH955D nuts, M4152 rod pin and split pin,
SH87A bell crank and SH955C spring. The M4153 carrier and the supporting clutch
throwout shaft, levers, bearings and brackets are receiving dependencies, with
their own installation hardware. They must be modeled and reconciled before
claiming a complete installed brake.

The current nineteen additions are **partial progress toward that scope**. M4160
and its six rivets are still pending; they have not been excluded. SNL8's band
assembly row is a nonphysical container with 26 physical children, not a 27th
component. SNL119's stock lining and named M4159 record identify one installed
lining. Existing M858 and the eight M855 bolt sets must not be duplicated.

## Evidence and current geometry

The [source dossier](../experiments/drive_chains/clutch_stop_brake_sources.json)
retains the exact survey records, original hashes and unresolved identities.
Full source pages were inspected. A public [original SNL Plate2](https://archive.org/download/SNL_G13_TANK_MKVIII/p277_foldout.jpg)
was retrieved at 11,072×5,456 pixels and verified against the archive's SHA1 and
byte count. It is retained alongside the packet; the older source is unchanged.

| Feature | Evidence | Current interpretation |
| --- | --- | --- |
| Stop drum diameter | HB115, 9.25in | 234.95mm supersedes the former 9in estimate. The inferred uniform wall and pulley groove grow with the exterior. |
| Pump drive | Existing 54in belt convention | Belt closure lowers the pump and attached supports 5.170902mm. Existing shaft and later clutch refinements are preserved. |
| Lining M4159 | SNL119, 2in wide, 3/16in thick, one 27¾in cut length | 50.8×4.7625mm stock; 704.85mm applies to the circular neutral-radius arc. Stretch and compression are not established. |
| Band M4158 | SNL8/119 identity and count | Estimated 3.175mm steel, 0.5mm released clearance; axial center X556.625 lies at the midpoint of the existing drum land. |
| Copper lining rivets | SNL8:026, fourteen 3/16×½in | Two rows of seven, head profiles and recesses inferred. Separate solids and real receiving passages. |
| Short button rivets | SNL8:024, three ¼×¾in | Provisionally retain an integral returned pin eye. This assignment and the eye form are estimates. |
| Anchor rivets | SNL8:025 and167:002, six ¼×1in for M4160 | Reserved for the forthcoming anchor; not yet added. |
| Band opening and pin eye | Unresolved drawing detail | Bottom opening, rolled ears, center relief and pin bore are provisional. Revisit their orientation with the operating linkage. |

The returned strip has a circular roll, an estimated smooth transition and a
contacting doubled lap. Offset spline section curves and a lining neutral curve
are retained as BRep inputs. The spline fit is checked at held-out sample points;
that numerical residual does not establish historical profile accuracy.

Rivet lengths describe selected blanks, not installed straight shanks. Button
lengths are taken under the factory head; countersunk lengths include the head.
Installed upset tails conserve those selected blank volumes. These conventions,
head shapes, shallow seats and forming assumptions remain unverified historically.
No strength, load or manufacturing certification is implied.

Definitions are hidden PartDesign bodies, repeated rivets are App::Links, and
`ClutchStopBandAssembly` belongs to Drivetrain/TransmissionCore. Units are
millimeters; local X points toward the engine. Controls require regeneration,
rather than live native expression updates.

## Source questions before the mounting geometry

The [envelope review](../experiments/drive_chains/clutch_envelope_review.json)
records two issues exposed by the clearer whole-vehicle drawing.

The survey retains HB115's **19.875in complete clutch-unit length** as an
uninterpreted dimension. From M858's rear face to the current flywheel front,
the model spans 586.575mm, versus 504.825mm printed. Starting at the front edge
of M855 instead gives 493.575mm. The printed endpoints and applicability to the
selected SNL clutch are unresolved; selecting convenient endpoints or shrinking
source-sized parts to force agreement would hide that question.

Mapping the new original pixels through the retained, conditional SNL2
calibration places the throwout shaft about 238mm below the drawn clutch axis.
The earlier 165mm visual estimate is unsupported. Its mapped X station also
differs from the current collar-flange gap. These are recorded discrepancies,
not adopted bracket coordinates. Resolve the axial budget and SKF1207 bearing
receivers before fixing the shaft brackets and M4160 attachment.

HB150–151 refers to Plate95 for Cardan-brake adjustment, but that figure does
not clearly resolve the small M858 brake. It has not been treated as a confirmed
profile drawing. HB188's spring, bell-crank and nut identifiers also differ from
the SNL inventory; the source alternatives remain explicit.

## Checks and review

The candidate saved and reopened with nineteen new valid single-solid pieces.
All **119 independent geometry checks** and **472 affected interference pairs**
pass. Checks inspect actual lining width, stock and arc length, drum radius,
lining clearance, rolled-ear bores, central relief, receiving voids and rivet
material volumes. Four definition and nineteen installed STEP comparisons pass.
Two coupled stock/gap/eye-size trials each pass the same119 independent checks
and111 local material pairs. They do not establish the complete brake, its
eventual installation or full standard-tank clearance across those variations.

Five native views and the full original/cropped source context were inspected.
Three new progression images preserve the installed isometric, isolated band
and returned-eye section; all 99 preceding images remain unchanged. Source
and native views have independent scales. The unresolved band details cannot
be visually certified from that drawing.

The first build saved the geometry but failed during export by accessing body
handles after closing the document. The builder now captures definition names
before closing; the first output and log are retained in the durable work area.
The first STEP check ended with SIGTERM after 22 passing comparisons and no final
receipt; the unchanged checker was rerun after confirmed termination and all
23 comparisons passed. The cause of that termination is not established.

Reproduce from the repository root:

```sh
python3 cad/003_FullTank/experiments/drive_chains/clutch_stop_band_build.py
python3 cad/003_FullTank/experiments/drive_chains/check_clutch_stop_band.py
python3 cad/003_FullTank/experiments/drive_chains/check_clutch_stop_band_exchange.py
python3 cad/003_FullTank/experiments/drive_chains/check_clutch_stop_band_variants.py
python3 cad/003_FullTank/experiments/drive_chains/render_clutch_stop_band.py
```

This packet is **not accepted for standard-tank integration**. The qualified
drum/flywheel checkpoint remains the accepted baseline. Complete brake/throwout
geometry, axial-source review, broader receiving-drive qualification and a fresh
reproduction remain ahead. Engine/crankshaft, air circuits, remaining interiors,
full coverage reconciliation, standard integration and later selected poses
remain required by the complete-tank workflow.
