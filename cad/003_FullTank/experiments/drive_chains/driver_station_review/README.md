# Driver station landmark review — 27 September 2026

The earlier assertion that the driver main shaft was **below the depicted source
joint** did not identify that joint positively. The reviewed whole figures instead
support testing two exposed ends on the side plate as the main and swing shafts.
This is a conditional reconstruction hypothesis, not a newly established dimension.

- [Annotated source identities and candidate shaft pair](visibility01/landmark_review.png).
- [Handbook figure 2 detail](visibility01/hb2_driver_detail.png).
- [Four complete saved handle comparisons at the tentative station](profile_probe01/source_comparison.png).
- [Source records and full-stock closure calculation](visibility01/report.json).

## What changed in the source interpretation

SNL35:032 identifies Plate 2 callout 56 as the left 6-pdr tool box. Its **leader
ends at the horizontal box region behind the seat**. The printed number itself
lies inside the large sloping outline below; this does not identify that whole
outline as the tool box. The previous source_visibility01 packet correctly named
the catalogue item, but any broader box-boundary inference is withdrawn here.

The shaded HB2 section shows the control blades disappearing behind a near side
plate. Thus a blade/edge intersection is not automatically a visible shaft center.
Two exposed round/hexagonal ends inside the plate offer a coherent alternative.
HB2 and SNL2 may share a drawing lineage, so this is better visibility evidence,
not independent dimensional corroboration. HB6 remains an uncalibrated perspective
photograph. No camera was fitted or changed.

Using the unchanged SNL2 calibration and tentative picks (477,428) and (545,425):

- The main pick gives X7461.419 / Z990.022 mm, **165.893 mm aft and 15.022 mm
  above** the Z975 trial.
- Retaining the existing 406.530 mm shaft separation and 20 mm height difference
  predicts the second feature within **0.664 pixels**. Only the first feature
  controls this placement; the second is a consistency check of the paired-feature
  hypothesis. Feature identity and source accuracy remain unproven.
- Five-pixel picking allowances correspond to roughly 30 mm per coordinate here.
  They do not bound drawing, projection or identity error.

The frozen older reports are preserved. This review supersedes only their claim
of a positively identifiable shaft-height discrepancy. It does not accept either
the old or new absolute station, and it leaves the separate SNL6/HB113 grip
discrepancy intact.

## Geometry feasibility and the next coupled revision

Four self-contained native probes each contain **150 occurrences**: 72 driver
mechanism parts, 38 fixed seat parts and 40 fixed bow plates. Each native was
reopened and its saved solids checked. Pair checks include the moving mechanism
against itself, the seat and bow, with no mating exemptions.

| Complete handle interpretation | Checked pairs | Intersections | Bow clearance |
|---|---:|---:|---:|
| Existing overall extent | 200 | 0 | 145.84 mm |
| Second-pivot reach | 200 | 0 | 129.51 mm |
| Main-shaft radius, current return | 202 | 0 | 55.87 mm |
| Main-shaft radius, source direction | 202 | 0 | 37.24 mm |

The previously colliding functional-radius profiles are therefore feasible
against these particular bow/seat solids at the tentative station. Their local
source comparison residuals remain unchanged. The source-direction case retains
12.14/13.11 px plan residuals and 0.48 px side residual; its side direction was
constructed from that drawing, so the small side residual is not validation.
The inspected SNL2 overlay still shows differences in blade/heel silhouette and
seat curves. No profile has been selected as historically proven.

These are **clearance probes, not complete installations**. They omit long front
rods, support plates/stays/angles, their floor attachments and the remaining tank.
The omitted support material must be rebuilt and checked, not exempted later.
No STEP acceptance or mechanical connection is claimed for these probes. Four
alternative natives do not add 600 installed parts to the tank inventory.

The source-sized M574 rods expose the coupling that a driver-only move misses.
Their 1257.3 mm cores and two retained 25.4 mm pin-to-core offsets require
1308.1 mm between pins. The tentative driver station is only 1142.667 mm from
the current intermediate receivers. **The complete rods are 165.433 mm too long
for those fixed endpoints.** The legacy report field `core_shortfall_if_fixed_mm`
means the endpoint span is short by this amount; it is not missing rod material.
Holding receiver Y/Z fixed requires both receiver X coordinates to move aft by
165.521 mm. This is a closure calculation, not permission to translate isolated
eyes or shorten the rods.

Next reconstruct the **coupled intermediate/driver layout** with complete rods,
actual floor mounts and connected seat supports. Start from the retained native
mechanisms, propagate the receiver change through all affected rear/front rod
routes and supports, and preserve every printed length. Use the functional-source
profile as a candidate, retaining the other profiles as alternatives. Check the
full saved context before choosing a reconstruction approximation for integration.
Then complete the remaining seat adjustment/locking fittings, including SH291C.

Accepted development remains operating_integrated01 (3,582 occurrences / 635
definitions / 442 groups), standard tank011 and image progression 308. The
connected seat support trial remains the last locally qualified support model.

## Recovery

Run `verify_driver_station_review.py` with system Python. To reproduce source
work, run `review_driver_station_landmarks.py --output NEW_PATH`. For geometry,
run `probe_driver_station_profiles.py --output ABSOLUTE_NEW_PATH` through the
existing headless launcher with a fresh runtime directory. The geometry worker
uses the frozen visibility01 review. Saved comparison PNGs are diagnostic source
views, not an accepted tank isometric milestone.
