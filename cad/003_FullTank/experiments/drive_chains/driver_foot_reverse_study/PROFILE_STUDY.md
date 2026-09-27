# M769 bowed-link study — not ready for assembly integration

The saved [profile03 prototype](profile03/ControlRebuildTrial.FCStd) contains two
instances of one M769 hypothesis and six exact retained receivers. It is a useful
CAD construction study; the front eyes, rear socket and connecting-link topology
remain unproven. The authoritative development remains
`coupled_driver_integration/integrated01`; standard tank011 is unchanged.

The profile uses two retained interpolating B-spline boundaries, a complete web,
two through bores and a blind nominal rod socket. All four installed construction
curves remain outside the physical hierarchy. Native properties identify the
approximations and the correct regeneration worker. Parameters require rebuilding.

Both the 8 mm web and 9 mm variation pass 49 saved-material/property checks,
including three deliberately damaged controls. Six nearby-pair comparisons in
an 8,989-occurrence retained context find no intersections. Each case passes
three strict native/STEP comparisons. A fresh nominal run reproduces all 26
archive BReps and 966 persistent properties without exceptions. These checks
qualify the recorded solids, not their historical interpretation or connections.

Four [inspected views](profile03/visual01/visual_review.json) show the isolated
parts, retained controls, and unchanged HB113/SNL6 projections. The plan placement
does not agree with all apparent inner-link lines. The direct socket and two-eye
head are hypotheses; overlapping source outlines must not be treated as a proven
part boundary. No camera refit was made. Experimental snapshots are retained
separately from the accepted progression count of 314.

The [connection diagnosis](rod_closure03/report.json) selects the actual free
66.675 mm intermediate eye; the 101.6 mm eye already carries M579. Current socket
axes miss the free eyes by 54.210 mm, equivalent to a 2.3006° reorientation. Keeping
the shared M576 stock at 1298.281517 mm, and assuming 19.05 mm insertion at both
ends, would require a single fork with 90.264 mm pin-to-face reach. This is a
constraint to reconcile with SH946F and the rear-link interpretation, not a
dimension established by the catalogue. No rods, receivers or stock were changed.

The [new source review](source_topology_review.json) includes original HB149:
the pedal is described as a 35¼-inch overall malleable-iron bell crank with an
8-by-5-inch pad and I-section. Later M764A applicability remains provisional.
The full joint graph must preserve the neutral-selective braking described on
HB148, the eight M771 members and the catalogue pin inventory.

Continue by tracing the M771/M765/M770/M795 connections and resolving the rear
M769 attachment. Compare each graph against the source leaders, existing selector
eyes and rod closure. Then build the connected pedal/bridle mechanism, complete
stock and hardware; qualify it before replacing any accepted geometry. Do not
promote this isolated profile study as a finished brake mechanism.

Reproduce with the existing headless launcher and absolute script/output paths:

```text
build_driver_foot_link_profile_v3.py --controls .../foot_link_profile_controls01.json --output NEW
pump_integration_worker.py extract --input NEW/ControlRebuildTrial.FCStd --output NEW/isolated/manifest.json
check_driver_foot_link_profile.py --candidate NEW
check_driver_seat_context.py --candidate NEW
render_driver_foot_link_profile.py --candidate NEW
exchange_driver_foot_link_profile_v3.py --candidate NEW
```

Use `--stock-offset 1` for the tested variation. Use
`check_control_rebuild_reproduction.py` to compare a fresh nominal build, and
`verify_driver_foot_profile_study.py` for the frozen receipt.

Retained diagnostics: profile01/variation01 had misleading fixed stock wording;
profile02/variation02 corrected it but retained the old regeneration-worker name.
V3 corrects that metadata without changing geometry. The first exchange checker
incorrectly expected an assembly relation for a single root part. Subsequent
Gauss and Gauss–Kronrod passes failed the original mass convergence/error limits;
the qualified V6 knot/continuity-split integrator passes on the **same** native
and STEP material without changing tolerances. All failures remain saved.
`rod_closure02` picked the occupied outer eye and is explicitly superseded by
`rod_closure03`. `topology01` holds early manual crops; `topology02` provides a
reproducible source-view packet.
