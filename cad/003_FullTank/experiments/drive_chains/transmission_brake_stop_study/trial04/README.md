# Brake-stop and lower-bearing mounting revision

Trial04 is an **experimental, unaccepted** extension of the qualified front-brake
parent. It contains3,001 installed components,503 definitions and295 assembly
groups. Standard tank011 is unchanged. The trial adds44 components and revises
32 inherited occurrences; two bearing casting definitions change.

The earlier lower cap-stud positions and upper/lower stud allocation were
explicit estimates. Independent shaft-to-nut picks in HB134/135 support a lower
station near137mm below the shaft. This trial uses the source-lengthMX36 studs
below andMX10 above, with the lower cap face derived from complete nominal
coarse-thread enclosure. The allocation remains inferred.

Trial03's bulky lower casting passed local fit checks but was visually weak.
Trial04 uses separate rounded stud bosses, paired connecting webs and a narrow
rear web. The shaft socket, upper oil interfaces and protected frame regions
remain preserved. Neither trial establishes an authentic foundry profile.

The four reviewed views are [isometric](isometric.png),
[mounting detail](support_detail.png), [HB134 overlay](lowspeed_source_overlay.png)
and [HB135 overlay](track_source_overlay.png). The fixed drawing registration
is unchanged. The mounting nut is2.82mm forward and14.43mm low in HB134,
10.65mm aft and24.32mm low in HB135. Relative shaft-to-nut picks also retain a
6.76–12.05mm fore/aft discrepancy. These are estimated drawing residuals, not
manufacturing tolerances. The overlays show stop geometry, not full casting
contours. The M341/M342 versusMX95/MX96 mapping and common-crossbar arrangement
remain conditional.

Completed saved-artifact checks:

-13 new/changed definitions are valid closed solids;79 count/frame checks pass.
-592 development-context pairs have no detected material interference.
-55 mounting checks pass, including protected casting material, socket support,
  full nominal coarse-thread enclosure, nut contact and displaced negatives.
-71 joint/ownership checks pass, including complete curved foot support, rivet
  head/tail retention, drilled-band material confinement and inherited frames.
-The76 affected components have no nearby pair against5,316 retained standard
  tank occurrences after the documented obsolete stand-ins are excluded.

The rivet-volume check explicitly uses the inherited **provisional under-head
stock-length convention**. It proves internal material consistency under that
assumption; it does not resolve the historical countersunk-length datum.

The initial combined STEP export passes86 of89 comparisons. Only the track lug
and its two installed instances fail a small tolerance-growth check, despite
matching material and converged centroids. The unchanged lug passes isolated
export. Diagnostics under`diagnostics/lug_step` and`diagnostics/step_assembly`
investigate the combined representation without changing geometry or relaxing
acceptance limits. Complete exchange qualification remains open until a final
passing receipt exists. Preservation, rebuild and parameter checks are ongoing.

Four new progression copies bring the archive to196 images. The prior192 images
and31 native baselines are hash-preserved in[progression_receipt.json](progression_receipt.json).
Historical geometry, strength, complete installation/removal paths and final
vehicle coverage remain unqualified. The front-brake parent remains authoritative.
