# Synthetic hollow stack

This implements `inputs/packet.json` and `inputs/stack_spec.json` for nominal and variant. Source specification SHA-256: `6c69a8ffe08e70065ba89f8c97e999937c907911f9bc78dfeda719ffe97fdc78`. The packet's source identity is `benchmarks/cad_work_packets/fixtures/stack_spec.json`; the supplied local copy is the evidence used. No source files, reviewed frames, or dimensions were modified.

These are synthetic interface qualification fixtures, reviewed for internal consistency only. They are **not accepted tank geometry**. Clearances are fixture assumptions, not historical measurements. No manufacturing tolerances, material specifications, loading, lubrication requirements, historical drawings, or physical fit measurements were supplied. Consequently no tolerance-stack or service qualification is claimed.

## Construction and installation

Each FCStd has an identity `Definitions` App::Part holding three analytic hollow solids, `Pin`, `Tube`, and `Bush`, each starting at local X=0 and having identity placement. Cylindrical subtraction preserves the pin's 4 mm bore and both other hollows. Named length/radius properties record the JSON dimensions. They are read-only annotations of generated geometry; regenerate with the builder after a specification change rather than editing these annotations.

`Assembly` is placed at the supplied assembly frame. Its child `Station` uses the supplied relative station frame. Station contains exactly four App::Link objects: `PinInstance`, `TubeInstance`, `BushLeft`, and `BushRight`. Both bush occurrences reference the same Bush definition. All link rotations are identity. World installation uses `assembly_frame * station_frame * link_placement`; STEP contains a compound of those four separate world-space solids, without fusing them or exporting library definitions.

| Station X extent (mm) | Nominal | Variant |
|---|---:|---:|
| Pin | -327.025 to 327.025 | -337.025 to 337.025 |
| Tube | -273.05 to 273.05 | -281.05 to 281.05 |
| Left bush | -273.05 to -223.05 | -281.05 to -227.05 |
| Right bush | 223.05 to 273.05 | 227.05 to 281.05 |
| Pin projection at each tube end | 53.975 | 55.975 |
| Gap between bushes | 446.10 | 454.10 |

Both cases have 0.100 mm radial / 0.200 mm diametral pin-to-bush clearance and 0.150 mm radial / 0.300 mm diametral bush-to-tube clearance. These are positive clearances, not interference fits. Dimensions and rotations are used without rounding or adjustment. Axis-angle normalization is performed by FreeCAD's Rotation API.

Definitions are hidden in saved views; installed links remain visible. The saved camera is axonometric with explicit framing centered on Station (camera height 1.3 times the pin length). Opaque colors distinguish pin, tube, and bushes. Internal surfaces are naturally occluded in a solid standard view; no section cuts, transparency, or altered geometry are introduced. No raster image or visual acceptance is claimed: the installed offscreen Qt platform reports that OpenGL widgets are unsupported. The offscreen `fitAll` operation stalled, so camera framing is set directly. The GUI also crashed on interpreter teardown during a preliminary probe, so the builder explicitly exits only after saves and checks finish (with failure exit on exceptions).

## Reproduction and checks

From the workspace root run:

```sh
python3 freecad_python.py deliverables/build.py
```

This regenerates both FCStd and STEP files and `checks.json`. `build.log` records the execution used for this delivery. Only installed FreeCAD and Python's standard library are used.

Builder checks cover the supplied source hash; radial and axial ordering; valid one-solid analytic hollow definitions; exact definition placements; hierarchy and shared link targets; identity link rotations and specified translations; nested world frames and solid centroids; analytic volumes; all six pairwise overlap volumes; measured clearance distances; four valid solids after STEP reimport; STEP per-solid volume, centroid, and common-volume agreement; and native document reopen with repeated model checks and hidden Definitions.

Numerical check thresholds are 1e-7 mm for lengths and 1e-5 mm³ for volumes, relaxed to 1e-6 mm and 1e-4 mm³ for STEP round trips. These are computational comparison thresholds, **not supplied or inferred manufacturing tolerances**. Analytic BRep geometry is used throughout; display tessellation and STEP serialization are the only representation approximations. Independent acceptance and source/visual review remain external to this session.

Both scenarios passed all builder checks, including a second regeneration run. Saved GUI XML was also inspected: Definitions visibility is false and all four occurrence visibilities are true. Native thumbnail capture reported no active OpenGL context; thumbnails must not be treated as visual evidence. See `checks.json` for numeric results.
