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

## Acceptance and exchange

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
