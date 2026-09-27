# Complete handle-profile comparison

Four self-contained FreeCAD prototypes retain the accepted fulcrums, joints,
selector interfaces and every occurrence frame. Each has 150 contextual
occurrences and 42 definitions; only the two existing handle definitions change.
These are experiments, not additional installed tank parts.

| Interpretation | Plan grip residual, port/starboard | Side residual | Current hull result, each handle |
| --- | --- | --- | --- |
| Accepted overall radial extent, replay | 47.16 / 48.59 px | 49.41 px | Clear by 14.08 mm |
| 37 in second-pivot-to-grip reach | 43.36 / 44.75 px | 43.09 px | Clear by 10.13 mm |
| 37 in main-shaft radius, current return | 26.41 / 27.49 px | 25.74 px | 2,451.67 mm³ interference |
| 37 in main-shaft radius, source direction | 12.14 / 13.11 px | 0.48 px | 6,530.52 mm³ interference |

The last case's inclination uses the side grip pick as a **construction
constraint**. Its small residual is not independent validation. All original
registrations are unchanged. The exact source meaning of 37 inches stays open.

The baseline passes 243 saved-solid checks, including complete material identity
with the accepted handles. Each alternative passes 241 construction checks.
Every case preserves lower stock through canonical X375 in both material
directions, all 40 other definitions and all 150 frames. The actual saved cap
pole measures 939.8 mm under the explicitly named interpretation. Full grip and
blade material is constructed before checking the hull; nothing is trimmed to
avoid it.

Broad context checks inspect 19 candidate pairs for each shorter interpretation
and 21 for each functional-radius interpretation, with no mating exemptions.
Both functional-radius trials fail against the actual front plate; all other
tested pairs clear. These failures are retained. None of the alternatives has
been promoted, STEP-qualified or added to the standard tank.

Inspected comparisons:

- [Fixed side figure](comparison02/side_comparison.png)
- [Fixed plan figure](comparison02/plan_comparison.png)
- [Actual hull section and intersections](comparison02/hull_comparison.png)

The comparisons prompted a wider
[front-hull audit](../front_hull_audit01/README.md). It confirms that the current
front plate has the opposite rake from the whole-tank section. Therefore these
context failures establish incompatibility with the **current model**, not proof
that the source-inspired handles are historically wrong. Conversely, changing
the plate to the reviewed source line alone does not clear the current grips.
Review the bow wall, floor joins, upper enclosure datums and driver layout
together before continuing upper fittings.

## Diagnostics and recovery

The first checker incorrectly required one spherical face per grip cap. Each
cap actually has two trimmed faces on the same sphere. The unchanged baseline
already passed complete material identity. `profile_checks` retains that failed
receipt; `profile_checks02` checks shared centre/radius instead. The failed
checker and sphere-support probe are under `diagnostics/cap_face_count`.

The first source-comparison renderer applied Matplotlib's default colormap to a
monochrome source. `comparison01` is retained; `comparison02` explicitly loads RGB
and is authoritative. No source geometry or source bytes were changed.

Regenerate with `trial_driver_handle_profiles.py`,
`../handle_profile_controls01.json`, the selected `--hypothesis`, and a fresh
output folder. Extract with `pump_integration_worker.py`, then run
`check_driver_handle_profiles.py` and `check_control_rebuild_context.py` through
the qualified headless launcher with absolute paths. A nonzero context exit for
the functional cases is expected only when a completed receipt records the two
specific front-plate intersections. Do not treat an interrupted worker as that
geometric result.

The accepted development model remains `operating_integrated01`, with its
historical limits and the newly identified front-hull contradiction explicit.
The geometry progression remains 308 images; diagnostic comparisons are kept
separately from accepted visual improvements.
