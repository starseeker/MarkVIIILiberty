# Installed rear-control support family

[PowertrainWithRearControlSupports.FCStd](PowertrainWithRearControlSupports.FCStd)
is the current full development native: **3,246 physical occurrences, 564 shared
definitions and 353 assembly groups**. It adds 20 parts in six groups under
`RearControlChannel`: two M4135 guides, two M4136 supports, eight mounting rivets,
two M4129 cleats and two bolt/lock-washer/nut sets. Existing nut and washer
definitions are reused. The receiving channel and floor are revised in place;
their occurrence frames and all earlier holes are retained.

This is a reviewed static reconstruction approximation. The
[prototype dossier](../support_family01/README.md) distinguishes source hardware
and quantities from estimated cleat shape, mounting topology and bracket
stations. M4129 is modeled with a forward floor foot and an upper transverse
pad sharing M4136's rivets. Catalogue/figure evidence does not establish that
hidden stack. M4136's original shape is retained and raised by the 9.525 mm
cleat stock; its rivets are reformed for the longer grip. No physical rod or
spring is added by this checkpoint.

Nominal and thicker-stock prototypes each pass 67 native/interface checks,
41 local material pairs, 20 context pairs, 32 strict STEP comparisons and
27 provisional short-rod/spring corridor comparisons. The integrated native
passes 45 checks covering local-link relocation, all inherited occurrence
frames/owners, persistent metadata and strict transfer of ten definitions and
22 installed shapes. All 556 unchanged inherited definitions are preserved:
533 have exact BRep bytes and 23 pass strict material comparison. Sixteen of
those comparisons reuse verified results for identical ordered BRep hashes
and unchanged checker code. Full integrated STEP export was not repeated;
the transferred prototype STEP evidence covers the changed/new shapes.

Fresh integration reproduces all 1,724 stored BReps, 155,376 persistent object
properties, 3,246 occurrence records and 353 assembly records. The prototype
also reproduces independently. These checks establish reproducibility and
bounded static fit, not historical accuracy or complete service installation.

The fixed SNL6 side registration is unchanged. New geometry is compared through
it without adding estimated cleat/anchor positions to the fitting landmarks.
The spring-height/inclination disagreement and the earlier 21.867-pixel
high-speed control-bore discrepancy remain open; HB104 is not calibrated.
The inspected [isometric](support_family_isometric.png),
[attachment detail](support_family_detail.png) and [source view](source_detail.png)
are copied into the visual progression, now 238 images with all 235 earlier
images preserved. The floor is translucent context. Standard `tank011` remains
unchanged; this selected subsystem view is not a new whole-tank standard render.

Recovery reuses the saved evidence:

```sh
python3 cad/003_FullTank/experiments/drive_chains/verify_rear_support_checkpoint.py
python3 tools/cad_pipeline/decisions.py cad/003_FullTank/decision_ledger.json
```

Next, develop the actual SH946D/M569C and SH946E/M569A short connections, M567
washers and M564 spring ends. Complete M575 and the long M573/M578 rear rods,
then center/front controls and remaining interiors. The measured operating-eye
coordinates remain in `fulcrum_integrated01/operating_interfaces.json`; their
four short-route **labels** are superseded by `spring_sources01/sources.json`.
The integration checks preserve those physical eye frames, but a future probe
must bind them explicitly to this new native. Full standard geometry remains
the active goal, with poses deferred.
