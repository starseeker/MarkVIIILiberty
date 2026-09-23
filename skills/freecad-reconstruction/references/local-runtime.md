# Local FreeCAD runtime

Verified on 22 September 2026: Python 3.12.3, FreeCAD 1.1.1, OCC 7.8.0,
`/snap/freecad/2741`, and Qt runtime `/snap/kf6-core24/64`.
Use `/snap/freecad/current` and `/snap/kf6-core24/current` to resolve the installed
paths, and record the versions actually loaded. These are local facts, not
assumptions to impose on another system.

## Headless first for geometry

Constructing BRep shapes, creating/linking objects, saving FCStd and exporting
STEP do not require `FreeCADGui.showMainWindow()`. Ordinary part/feature/link
`Visibility` properties are available headlessly in the tested release, although
`ViewObject` is absent; save/reopen and verify the required display state rather
than opening a GUI just to hide a definition library. For this skill's launcher:

```bash
python3 skills/freecad-reconstruction/scripts/freecad_headless.py --probe
python3 skills/freecad-reconstruction/scripts/freecad_headless.py --workdir .work/my_packet my_builder.py
```

The script path resolves relative to the invoking directory; relative files
opened by the builder resolve inside `--workdir`. Settings, cache and temporary
files stay under that work directory. This helper configures library paths; it
does not grant filesystem or network permissions. The controller's packet
launcher already supplies the runtime, so do not nest launchers unnecessarily.

In the tank pipeline, reuse `cad/003_FullTank/lib/runtime.py` when its GUI workflow
is required. Its output-directory argument must be absolute: relative Qt/XDG
paths have caused process aborts. Preserve task-local settings rather than sharing
the desktop profile or changing HOME/CODEX_HOME.

## GUI and rendering pitfalls

The offscreen Qt platform reports unsupported OpenGL widgets on this machine.
The tool-enabled trials observed stalls around GUI/view initialization and
`fitAll`, and a crash during GUI interpreter teardown. These are environment
observations, not proof that a generated shape is wrong or that every GUI call
will fail. Use bounded probes; do not repeatedly start the GUI to solve a kernel
geometry problem.

If saved display styling is required, isolate that stage and use the project's
qualified GUI startup/cleanup functions. Close documents and process deferred Qt
deletion before teardown. Diagnose a stall from its logs; do not remove source
or model constraints to get past it. A thumbnail without a valid OpenGL context
is not visual evidence. Avoid adopting forced process exit as a general remedy;
it can conceal unfinished saves or cleanup.

For review images here, `cad/003_FullTank/lib/visual_review.py:shaded` rasterizes
native shape tessellation in software and verifies placements. It can produce
isometric and section views without GUI rendering. Keep review cuts and display
transparency separate from the saved physical model.

Sandbox errors have a different cause from CAD errors. A Codex PATH-alias warning
means an optional runtime write failed; verify the actual process exit and tool
operation. A successful `--version` is not proof that a model run can initialize.
Use the controller's restrictive-profile preflight before candidate execution.
