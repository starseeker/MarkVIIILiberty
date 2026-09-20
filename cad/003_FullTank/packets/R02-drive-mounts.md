# R02 — driving-wheel shafts and bearing attachments

Preparatory source review, 20 September 2026. The current wheel build is being
qualified separately. No shaft/support geometry is integrated by this packet.

## Source scope

Each SNL215:001–007 shaft assembly has seven leaves: one M1402 shaft, two M1477
nuts, two M1409 bushes, one 20297/D89 key and one Q52C pipe plug. The current
wheel increment includes the two bushes and explicitly omits the other five.
HB133 describes a central axial oil lead reaching approximately mid-length,
with a radial lead to the bushing. HB134 prints 27.625-inch shaft length and
4.434-inch diameter. Exact journal shoulders, keyway orientation and oil-bore
sizes are unprinted in the reviewed pages.

| Component | Source | Vehicle quantity | Drive-wheel interpretation |
|---|---|---:|---|
| M1406 inner bearing | SNL18:006 | 2 | One per drive wheel |
| M1407 outer bearing | SNL18:008 | 4 | Two drive plus two roller-pinion uses |
| M1552 bearing plate | SNL152:021 | 4 | Two drive plus two roller-pinion uses; printed `M402` is retained as an apparent M1402 reference |
| M1411 nut locking plate | SNL152:022 | 4 | Two per drive shaft supported by HB237; outer plate visible in HB86/119/125, inner placement remains inferred |
| 3/4 × 2 1/4 inch cap screw | SNL201:008 | 24 | Six per M1407, twelve in the drive subset |
| 1/2 × 3/4 inch cap screw | SNL200:009 | 4 | One per M1411 |
| 3/4 × 2 5/8 inch rivet | SNL189:009 | 12 | Six at each M1406/M1977 joint |
| 1/2 × 1 3/4 inch rivet | SNL170:004 | 52 across several joints | Four per explicitly named M1975/M1552 drive joint; further plate-only allocation remains to be resolved |

Original HB237 (scan MarkVIII119) prints two M1411 plates and two M1477 nuts
within the driving-wheel subset, alongside one inner and one outer bearing.
Its global column heading is inconsistent with this local assembly scope;
SNL whole-vehicle quantity four supports two plates per drive shaft.

Do not assign M1411 automatically to the roller-pinion shafts: SNL215:009–013
contains a shaft, key and two pipe plugs, with no shaft nuts. Its retention
topology is distinct. The bush scopes also differ: the M1544 shaft BOM does
not list its two M1409 bushes, although the standalone M1409 application does.
These distinctions require source-specific assembly reconciliation.

## Inspected topology

HB Plate 81's sectional plan shows the drive wheel rotating around the fixed
shaft, two hull-side bearing supports, and separate chain-sprocket/roller-pinion
geometry forward of it. Plates 82 and 83 show that installation and chain-case
clearance. Plate 119 identifies the removable outer M1407 bearing, shaft end,
M1477 nut and M1411 locking plate. Plate 85 is an installed rear-track photograph;
it supports surrounding plate/track topology but does not dimension the bearing.
The labeled HB125 section further identifies the stepped outer bearing, M1552
backing plate, key at the outer bearing, and M1410 oil plug. The key therefore
belongs to the outer support interface in the next fixture. The section also
supports the nested rim/disk and relieved diaphragm topology. No metric
calibration is inferred from these uncalibrated illustrations.

The present model uses an 88.9 mm reduced journal and 89.4 mm nut envelope for
M1477 on the idlers. Reuse of the same M1477 identity implies a corresponding
journal envelope on the drive shaft. This remains a working inferred interface;
threads and historical tolerances have not been established. The wheel has
490 mm boss length and two 203.2 mm bushes. Its fixed shaft centers and the
printed overall shaft length must remain independent controls.

## Receiving-plate discrepancy to resolve

The source explicitly attaches M1406 to **M1977**. The initial hull layout put
M1977 beside the fuel bay, ending at the provisional pixel-1630 seam, while the
drive axis is at pixel 1715. The current receiver at that axis is labeled M1978
(`inner_rear_end`). Thus a native bearing contact at that location alone would
not reconcile the source identity of the receiving plate. Reinspect rear hull
plate extents and seams before accepting the mounting installation. Preserve
this discrepancy rather than silently relabeling a plate or claiming full fit.

The M1552 rivet row also names four rivets solely against each bearing plate,
in addition to four at each named outer-hull joint. The remaining receiving
structure/fastener allocation must stay explicit until resolved.

## Next geometry study

Construct a separate shaft/bearing fixture with the two common bushes and nuts,
printed key and pipe plug, separate inner/outer bearings, locking plates and
owned bores. Measure native bush clearances, shoulder/nut seats, key interfaces,
oil passages and source-counted attachment joints. Then place it at the fixed
axes and inspect the actual receiving plates. Integrate only with documented
plate mapping and geometric interfaces; no motion or load qualification follows
from the static fixture.

The [source review manifest](../experiments/drive_mounts/source_review.json)
records inspected source hashes and the later HB125/HB237 findings.

## Native studies and corrected receiver interpretation

The [isolated and installed studies](../experiments/drive_mounts/README.md) now
provide a geometrically feasible mounting hypothesis. The isolated 149-part
fixture clears 441 material pairs after rejecting the first locking-plate
outline; inferred scallops now clear neighboring heads. All 39 isolated bearing
faces survive a fresh native reopen. The two receiver coupons are expressly
excluded from physical/source counts.

Direct inspection of the original SNL189 scan confirms that the adjacent rivet
rows distinguish M1977/M1406 (drive) from M1978/M1546 (roller pinion). SNL169:004
pairs M1977 and M1975 through M2031/M2032 angles; SNL178:002 pairs M1978 and
M1976 through M2004 angles. These allocations support correcting the initial
inner fore/aft geometry assignments. Exact outlines and the seam position remain
inferred; the part identities must remain attached to their source records.

The separate installed trial adds 56 shaft/mount parts around both existing
wheels and reconstructs twelve rear plates. Its level rear skirt-border
hypothesis provides a full bearing footprint without moving either drive axis.
All 430 material candidate pairs, 26 hull seats and 32 full 12 mm receiving
cylinders pass. The 424 lower-support seats, 34 hull contacts and 76 attachment
bores remain valid with the trial plates substituted into the full native tank.
The main authored inputs are frozen during the preceding wheel qualification;
this trial has not yet been integrated into the delivery.

Integration should preserve the seven-leaf shaft BOM and separately count the
23 bearing/attachment leaves per side. Reuse the existing M1477 nut, M1409 bushes
and Q52C plug. Add ten new definitions for the shaft, key, two bearing types,
backing/locking plates and four attachment-fastener types. Source totals for
shared M1407, M1552, key, bushes and cap screws must continue to show the remaining
roller-pinion uses; the additional plate-only M1552 rivets remain unresolved.
Keep the historical shaft/bearing, thread, retention and load gates open.

Adoption needs typed controls, derived mount datums, owned hull cuts, source
quantity reconciliation and integrated native interface checks. Parameter trials
should vary shaft length and bearing-wall spacing so shoulders, keys, nuts,
oil plugs and flange/fastener seats follow their owners. Scope the existing
idler-length trial's oil-plug matching to idler assemblies before drive oil
plugs are introduced. Qualify the full native/STEP delivery and inspect the
standard isometric before advancing the next numbered snapshot.
