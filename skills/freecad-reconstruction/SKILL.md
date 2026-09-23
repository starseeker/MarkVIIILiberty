---
name: freecad-reconstruction
description: Build and verify scripted FreeCAD BRep parts and linked assemblies, including evidence-led historical reconstruction, native/STEP exchange, and headless runtime troubleshooting.
---

# FreeCAD reconstruction

Use the project's existing builders, datums, source records and validators when
available. Keep historical interpretation separate from CAD execution: a valid,
well-fitting solid can still represent the wrong part.

## Choose the relevant guidance

- For scripted construction, transforms, saved files or interchange, read
  [assembly and validation](references/assembly-and-validation.md).
- On this Linux workstation, or when FreeCAD imports/GUI startup fail, read
  [local runtime](references/local-runtime.md). Prefer headless construction and
  an existing software renderer when an interactive view is unnecessary.
- When deriving geometry from drawings, catalogues or conflicting dimensions,
  read [source reconstruction](references/source-reconstruction.md).

For a bounded implementation, establish units, definition coordinates, parent
frames and interfaces before writing geometry. Preserve shared part definitions
and separate installed occurrences. Produce a reproducible builder plus the
native documents; say which dimensions update live and which need regeneration.

Use analytic surfaces for analytic features. Use B-spline/NURBS sections or patches
when the supported form needs them, retaining the curves, fitting assumptions and
residual checks. Do not infer additional dimensional certainty from surface smoothness.

Validate the actual saved artifacts independently of the builder's self-checks.
Check material and voids, parent-relative placement, neighboring interfaces, and
native/STEP reopening. Include a relevant parameter variation for reusable parts.
Read the source and inspect a suitable view/section before accepting reconstruction
geometry; distinguish an approximate feature from a source-supported one.

## Reusable helpers

`scripts/freecad_headless.py` launches a script with the installed snap runtime
and task-local settings. It also has `--probe`. It does not start a GUI or change
sandbox permissions. Use an already-qualified project launcher when appropriate.

`scripts/assembly_geometry.py` resolves rigid `App::Part` ancestry and direct
`App::Link` occurrences of identity-frame shape definitions. It rejects unsupported
scales and definition frames instead of guessing. For links to assemblies, scaled
links or external dependency trees, use or qualify the project's full traversal.

Run `scripts/self_test.py` through the headless launcher after changing these
helpers or upgrading the runtime. It tests transformed assembly geometry,
interchange/reopening and rejection of unsupported link forms. The helpers do
not implement or certify general freeform surface fitting.

## Improve from evidence

Add a narrowly scoped lesson when a real failure reveals a reusable cause. Record
the tested runtime and a reproducer for API or GUI behavior. Keep task-specific
piece marks and dimensions in their work packet, rather than turning them into
skill-wide rules. Freeze skill copies supplied to comparison trials; evolve the
next trial or packet revision separately.
