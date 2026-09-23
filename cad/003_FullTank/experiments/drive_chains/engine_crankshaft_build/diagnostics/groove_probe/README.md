# Same-domain unification diagnostic

FreeCAD1.1.1 / OCC7.8.0,23September2026. The retained probe constructs the four
main-bearing shell definitions, checking each Boolean step. All raw shells are
valid single solids. Calling removeSplitter on the long upper shell returns one
invalid solid without raising an exception; the other three remain valid.
Before/after BReps and the step log are retained. The production generator keeps
the checked raw shell when optional refinement fails. Saved-native and STEP
verification remain required; this diagnostic alone does not qualify delivery.

Run through the repository FreeCAD headless launcher. The probe uses the current
crankshaft controls and primitive helpers, and writes into the ignored groove_probe
workspace. Its machining sequence is retained in this file, including the failing
unconditional refinement. These observed kernel results are runtime-specific.
