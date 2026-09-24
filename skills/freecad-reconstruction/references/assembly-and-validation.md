# Assembly geometry and validation

These operational details were exercised with FreeCAD 1.1.1 / OCC 7.8.0 on
22 September 2026. Recheck API assumptions after a runtime upgrade.

## Definition and occurrence coordinates

Prefer a reusable definition at its documented local origin, with identity
placement, and place its `App::Link` occurrences relative to their owning
`App::Part`. For an ordinary nested rigid hierarchy:

```python
world = outer.Placement.multiply(inner.Placement).multiply(link.Placement)
```

The rightmost transform acts first. Do not assign this world placement back to
the child: the assembly would apply its ancestors again. Use three non-collinear
points or a full rigid matrix to verify orientation as well as translation.

The tested `App::Link` object does **not** expose `getGlobalPlacement()`, although
`App::Part` does. For a direct, unscaled link to an identity-frame shape definition,
the parent's global placement multiplied by the link's placement is its world
placement. The supplied helper walks ordinary geometric parents and explicitly
checks this narrower contract. Do not silently apply it to linked assemblies,
scaled links, or nonidentity definition frames. In the MarkVIII repository,
`cad/003_FullTank/lib/cad_build.py:leaves` handles the established delivery's
nested external links; inspect its conventions before extending that model.

`App::Part` creates Origin/axis/plane objects automatically. Count physical
definitions and installed links by role/type, not `len(doc.Objects)`. A library
definition and its installed occurrences must not both enter the physical BOM.

## BRep and surface construction

Keep cylinders, planes, cones and revolved analytic profiles analytic where that
matches the evidence. Booleans can return a compound containing one solid; check
`isValid()` and `len(shape.Solids)`. Inspect the actual topology before assuming
attributes specific to a solid, such as its `CenterOfMass`, are present on a
generic imported `Part.Shape`. Use the constituent solids for aggregate centroids.

On FreeCAD 1.1.1 / OCC 7.8.0, `removeSplitter()` can return invalid topology
without raising an exception. A grooved bearing passed validity after every
Boolean cut, then failed only after same-domain face unification. The operation
also mutated its input BRep. Running `shape.copy().removeSplitter()` preserved
the original and produced a valid result in the focused probe. Isolate optional
cleanup on a copy, and check the returned shape before replacing the original.
If cleanup fails, retain the checked original BRep and record that choice;
saved-native and exchange checks still apply. The project retains the
[focused probe and before/after BReps](../../../cad/003_FullTank/experiments/drive_chains/engine_crankshaft_build/diagnostics/groove_probe/).

Validity alone also does not prove that optional cleanup improved a shape. In
the lower-drive receiving case, the same `removeSplitter()` operation returned
a valid single solid but raised its maximum kernel tolerance from about
5.10e-6 to 1.015e-4 mm at intersecting cone/cylinder boundaries. The original
and cleaned shapes had zero material differences in both directions. Keeping
the valid shape before cleanup passed the original strict STEP criteria, with
about 1.28e-7 mm maximum STEP tolerance. Compare the tolerances as well as
validity before adopting an optional cleanup; retain the original when cleanup
degrades the representation. Do not reset tolerances to hide the change. The
[saved diagnostic and replay](../../../cad/003_FullTank/experiments/drive_chains/engine_lower_drive_installation/diagnostics/cleanup_tolerance/README.md)
records this FreeCAD 1.1.1 / OCC 7.8.0 case.

For a prismatic rounded opening, prefer one planar wire of tangent lines and
analytic circular arcs, extruded once. In the lower distribution housing study,
an equivalent tool assembled from boxes and cylinders left higher-tolerance
intersection edges after Boolean operations. Both housing halves reopened from
STEP with slightly increased kernel tolerances despite zero material differences.
The single-profile prism preserved material in both directions and passed the
original tolerance bounds. Diagnose and compare the actual shapes before adopting
this remedy; do not enlarge import tolerances to conceal an unexplained failure.
See the [lower distribution packet](../../../cad/003_FullTank/packets/P01-engine-lower-distribution.md).

For spherical pockets between two parallel trimming planes, the sphere's
parametrization can affect STEP transfer even though rotating a complete sphere
does not change its material. On the same runtime, pockets crossing the default
sphere poles produced valid native cages but invalid STEP solids. Aligning the
sphere axis with the trimming-plane normal made the boundaries latitude circles;
both tested sizes then reopened with zero material differences, in definition
and installed coordinates. Retain the intended spherical geometry and verify
the actual round trip. See the
[isolated pocket export probe](../../../cad/003_FullTank/experiments/drive_chains/engine_crankshaft_build/diagnostics/cage_step_probe/).

Choose that orientation from the actual retained patch. In a thicker cylindrical
water-pump cage, axial sphere poles remained inside the cage stock and produced
invalid STEP; tangential poles also failed. Radial poles lay outside both cage
cylinders, preserving material in both directions and passing the original strict
round-trip criteria. Thus the useful rule is to keep singularities outside the
trimmed patch when possible, then verify the saved result. See the
[three-orientation cage probe](../../../cad/003_FullTank/experiments/drive_chains/engine_water_pump_study/diagnostics/cage_step/README.md).

For small formed wire with planar circular bends, consider explicit cylinders
and torus segments before sweeping a circular section along a composite path.
On FreeCAD 1.1.1 / OCC 7.8.0, a swept split pin with a polygonal eye passed native
validity but failed STEP material/centroid comparisons; analytic bends and a
semicircular eye passed both definition and installed-orientation checks. This is
a tested local alternative, not a ban on sweeps. Check that fusions retain both
legs; a connected, valid result can still have lost material. The project retains
the [failure and focused probe](../../../cad/003_FullTank/experiments/drive_chains/clutch_support_build/diagnostics/README.md).

A native save can normalize quaternion components in their last decimal places
or change BRep bookkeeping without changing the geometry. Preserve the original
parent file and its hash, then assess the new document against the declared
geometric, metadata and frame criteria. Unless exact archive-byte preservation
is an actual requirement, avoid rewriting FCStd ZIP internals merely to make
serialized hashes match. Such a repair adds another implementation to qualify.

Capture object identifiers, metadata and other plain values before closing their
document. On FreeCAD 1.1.1/OCC 7.8.0, reading an `App::Part.Name` through a retained
Python object after `App.closeDocument()` raised `ReferenceError`, even though
the native file had saved successfully. The frame-joint builder now captures its
assembly-name list before closing; the fresh rebuild reproduces all persistent
properties. The [initial failure](../../../cad/003_FullTank/experiments/drive_chains/transmission_frame_joint_study/trial01/failure_status.json)
and adjacent failed builder retain the tested case. Reopen the saved document
and obtain fresh objects when later CAD access is required.

For formed round wire, a valid fused solid can conceal self-interference: fusion
removes the overlapping stock. Retain a nonphysical centerline and compare solid
volume with cross-sectional area times its length. Check nonadjacent centerline
separation and local bend radius as well as contact with neighboring parts.
On FreeCAD 1.1.1 / OCC 7.8.0, a doubled lock-wire tail passed validity and all
neighbor checks but lost 6.337590 mm³ through self-overlap. Revising its estimated
twist retained the full source stock length and passed all three checks. The
[saved positive and negative controls](../../../cad/003_FullTank/experiments/drive_chains/engine_oil_pump_relief_lock_study/diagnostics/wire_self_contact/README.md)
include a replay. Centerline sampling needs a spacing allowance; it is not an
exact global minimum-distance proof or a simulation of wire deformation.

For bearing contact, distinguish surface area from volumetric intersection.
On FreeCAD 1.1.1/OCC 7.8.0, two touching 10 mm boxes have zero distance but their
solid/solid `common()` is empty; intersecting their coincident faces gives the
expected 100 mm². For planar seats, select the actual coplanar bearing faces and
measure their intersection while checking solid overlap separately. The engine
rail probe measured 52,454.767 mm² per side this way; lifting the flange 0.01 mm
removed the contact and failed the unchanged area criterion. The
[reproducer and measurements](../../../cad/003_FullTank/experiments/drive_chains/engine_pump_receiver_study/registration/native_support_trial01/contact_probe.py)
record the tested case. Zero distance alone does not establish a bearing area.

Default mass/area integration can also disagree for identical, heavily trimmed
curved faces. On FreeCAD 1.1.1/OCC 7.8.0, a drilled brake band passed strict
native/STEP material comparisons but its default volumes differed by 915 mm³
and its centroids by 0.040 mm. Adaptive OCCT integration of the unchanged BReps
converged in both files; a separate Gauss-Kronrod calculation corroborated it.
Use a verified higher-accuracy measurement when diagnosing this symptom, while
retaining validity, material, tolerance and convergence checks. Do not enlarge
geometric tolerances or alter sound geometry just to match default mass values.
The project's [adapter and focused qualification](../../../cad/003_FullTank/experiments/drive_chains/transmission_brake_band_study/trial01/diagnostics/adaptive_mass/README.md)
record the tested case. Similarly, two fully seated cylindrical lining faces
gave slightly different integrated areas after re-trimming. Matching analytic
supports plus empty uncovered-face differences, with displaced negative controls,
proved coverage directly; an area estimate alone was insufficient.

Treat kernel bounding boxes as enclosures, not guaranteed exact size measurements.
On this runtime, a retained cross-drilled stud reports a 19.058984 mm bounding-box
width, while its axial cylinder faces have radius 9.525 mm and no material lies
outside the 19.05 mm nominal stock. Measure the defining surfaces and check the
whole material envelope before declaring a dimensional error. The
[saved checks and initial failure](../../../cad/003_FullTank/experiments/drive_chains/engine_pump_receiver_study/registration/native_frame_trial02/README.md)
record this case. Conservative bounds remain useful for interference filtering.

For freeform sections, establish a common coordinate system and corresponding
curve directions before lofting or fitting surfaces. Retain source picks and
control curves; check section residuals, seams, surface continuity where required,
shell closure and resulting solid validity. A smooth NURBS surface is not evidence
that the source shape was recovered. This project's current effort benchmarks
exercise analytic BRep construction, not general NURBS fitting.

When repairing a qualified shape, preserve the required region explicitly and
compare it in both material directions. Fusing a replacement onto an old body
can leave a larger stale rim intact. Distinguish missing material, extra material,
and neighbor interference; a volume-only check can miss an incorrect distribution.

A Boolean difference can be an empty compound with `isNull() == False`.
On FreeCAD 1.1.1 / OCC 7.8.0, this occurred in the water-pump case preservation
check; a further cut raised `ValueError: Null shape`. A simple contained-box
probe also returns a non-null compound with zero solids, faces and volume,
although its second cut succeeds. For differences between validated closed
solids, inspect the material/topology before chaining more Boolean operations
and handle an empty result explicitly. Do not silently classify unexpected
shells or invalid topology as a successful empty difference. See the
[mounting diagnostics](../../../cad/003_FullTank/experiments/drive_chains/engine_water_pump_mounting_study/diagnostics/mounting_revision/README.md).

## Acceptance and exchange

Match isolated probes to the delivery pipeline's STEP settings before changing
geometry in response to an exchange failure. In the local FreeCAD 1.1.1/OCC 7.8
drain-wire probe, an export without surface curves reopened as a valid solid but
gave an incorrect full-volume Boolean difference from its native source. Exporting
the **same BRep** with `Part.setStaticValue('write.surfacecurve.mode', 1)` retained
the STEP `PCURVE` records and passed both material directions with no difference
faces. The project builder already used that setting; the isolated probe omitted
it. This is a tested local export remedy, not a reason to discard geometry or
weaken acceptance limits. Preserve the settings and failing control in the
[focused replay](../../../cad/003_FullTank/experiments/drive_chains/engine_water_pump_connections_study/diagnostics/step_surface_curves/replay.py).

Use criteria that would reject a plausible wrong solution: independent material/
void witnesses, analytic dimensions, whole-region differences, required openings,
composed frames and neighbor clearances. Keep numerical tolerances separate from
design fit allowances and historical dimensional uncertainty.

Recompute, save, close and reopen native documents. For assembly exchange, export
the installed world-space shapes and reimport the STEP. Compare solid count,
volume, centroids and material in both directions. STEP geometry alone does not
prove native link hierarchy or dependency portability; inspect those separately.
Rebuild in a fresh workspace when qualifying a generator. Do not interpret custom
dimension properties as live parametric dependencies unless expressions/features
actually connect them to the geometry.

Read only the relevant API when an unfamiliar method matters. The official
[App::Part Python API](https://freecad.github.io/API/d5/df9/classApp_1_1PartPy.html)
documents the part placement interface; the
[TopoShape API](https://freecad.github.io/SourceDoc/d8/ded/classPart_1_1TopoShape.html)
describes kernel operations and exchange. Online generated docs can lag the
installed release; local probes above establish this skill's tested behavior.
