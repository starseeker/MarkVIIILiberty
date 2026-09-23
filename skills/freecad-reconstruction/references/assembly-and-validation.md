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
