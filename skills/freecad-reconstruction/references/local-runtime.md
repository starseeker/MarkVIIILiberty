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

Collect the complete selected geometry before rendering views or publishing a
final receipt. A pump-review renderer accidentally nested its three-view pass
inside a 242-occurrence loading loop, issuing 726 renders and repeatedly replacing
incomplete intermediate images. Moving that pass after collection produced three
byte-identical final PNGs on this runtime. A separate output directory preserved
the terminal baseline during verification. The [retained implementation and
comparison](../../../cad/003_FullTank/experiments/drive_chains/engine_pump_receiver_study/assembly_trial02/diagnostics/render_loop/README.md)
document this control-flow failure; image existence alone did not prove completion.

When sharing tessellation by definition, supply the same canonical definition
shape for every occurrence and apply its installed placement separately. A
bottom-stop preview supplied world-posed targets under a shared definition key;
the renderer reused the first mesh and drew repeated parts at that first pose.
Native and STEP geometry were correct. Using identity-frame targets restored both
sides without changing geometry or the camera. Inspect repeated occurrences,
not just one exemplar; a transform calculation alone does not prove that its
cached input belongs to the right frame. The
[retained preview diagnostic](../../../cad/003_FullTank/experiments/drive_chains/transmission_high_brake_support_study/bottom_stops03/diagnostics/render_cache.json)
records this caller-contract failure and the corrected saved-native views.

Sandbox errors have a different cause from CAD errors. A Codex PATH-alias warning
means an optional runtime write failed; verify the actual process exit and tool
operation. A successful `--version` is not proof that a model run can initialize.
Use the controller's restrictive-profile preflight before candidate execution.

## Long native and STEP checks

Keep output and progress under a durable work directory and retain the tool's
job handle. A quiet log or a process absent from another sandbox's PID namespace
does not establish completion; obtain the terminal result before restarting a
job. Distinguish an interrupted check from a geometric failure.

One lower-drive exchange worker on this runtime used about 10.2 GiB RSS.
Copying the required saved shapes and composed occurrence poses, then closing
the large parent document before comparison, preserved all 27 strict results;
closing the document did not immediately imply lower RSS. Serialize similarly
large checks when memory is constrained. The
[retained diagnostic](../../../cad/003_FullTank/experiments/drive_chains/engine_pump_layout_study/lower_drive_trial/checker_memory_revision.json)
records unchanged acceptance predicates and identical completed legacy results.
The preceding process terminations did not establish their cause; do not label
them out-of-memory failures without supporting evidence.
