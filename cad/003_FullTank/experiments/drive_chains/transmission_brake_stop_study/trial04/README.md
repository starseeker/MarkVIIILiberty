# Brake-stop and lower-bearing mounting revision

Trial04 is an **experimental, unaccepted** extension of the qualified front-brake
parent. It contains 3,001 installed components, 503 definitions and 295 assembly
groups. Standard tank011 is unchanged. The trial adds 44 components and revises
32 inherited occurrences; two bearing casting definitions change.

The earlier lower cap-stud positions and upper/lower stud allocation were
explicit estimates. Independent shaft-to-nut picks in HB134/135 support a lower
station near 137 mm below the shaft. This trial uses the source-length MX36 studs
below and MX10 above, with the lower cap face derived from complete nominal
coarse-thread enclosure. The allocation remains inferred.

Trial03's bulky lower casting passed local fit checks but was visually weak.
Trial04 uses separate rounded stud bosses, paired connecting webs and a narrow
rear web. The shaft socket, upper oil interfaces and protected frame regions
remain preserved. Neither trial establishes an authentic foundry profile.

The four reviewed views are [isometric](isometric.png),
[mounting detail](support_detail.png), [HB134 overlay](lowspeed_source_overlay.png)
and [HB135 overlay](track_source_overlay.png). The fixed drawing registration
is unchanged. The mounting nut is 2.82 mm forward and 14.43 mm low in HB134,
10.65 mm aft and 24.32 mm low in HB135. Relative shaft-to-nut picks also retain a
6.76–12.05 mm fore/aft discrepancy. These are estimated drawing residuals, not
manufacturing tolerances. The overlays show stop geometry, not full casting
contours. The M341/M342 versus MX95/MX96 mapping and common-crossbar arrangement
remain conditional.

Completed saved-artifact checks:

- 13 new/changed definitions are valid closed solids;79 count/frame checks pass.
- 592 development-context pairs have no detected material interference.
- 55 mounting checks pass, including protected casting material, socket support,
  full nominal coarse-thread enclosure, nut contact and displaced negatives.
- 71 joint/ownership checks pass, including complete curved foot support, rivet
  head/tail retention, drilled-band material confinement and inherited frames.
- The 76 affected components have no nearby pair against 5,316 retained standard
  tank occurrences after the documented obsolete stand-ins are excluded.

The rivet-volume check explicitly uses the inherited **provisional under-head
stock-length convention**. It proves internal material consistency under that
assumption; it does not resolve the historical countersunk-length datum.

The final component STEP export passes **89 of 89 comparisons**. The initial
flat compound passed 86: the track lug and its two installed instances failed
a small tolerance-growth check despite matching material and converged
centroids. Isolated export of the unchanged lug passed. The
[diagnostic](diagnostics/README.md) retains those controls and the successful
`Import.export()` component representation. No geometry or acceptance threshold
was changed. Definition and installed exports contain 13 and 76 component uses.

All **490 unchanged inherited definitions** are preserved: 464 exact BReps and
26 passing strict material comparisons. A fresh rebuild reproduces all 1,537
archive BReps and 139,961 persistent object properties. A bracket-stock change
from 6.35 to 7 mm combined with a lower-stud station change from -137 to -142 mm
passes all 55 mounting, 71 joint/ownership and 592 development-pair checks.
Its 490 unchanged inherited definitions exactly match the nominal candidate.
The variant is a generator check, not a historical alternative or qualified
variant STEP export.

Four new progression copies bring the archive to 196 images. The prior 192 images
and 31 native baselines are hash-preserved in [progression_receipt.json](progression_receipt.json).
Historical geometry, strength, complete installation/removal paths and final
vehicle coverage remain unqualified. The front-brake parent remains authoritative.
