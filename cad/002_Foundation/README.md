# Mark VIII CAD foundation and pilot

This stage turns selected survey evidence into reproducible native FreeCAD parts
and a hierarchical assembly. The baseline is the **1919–1920 Rock Island first-100
production configuration**, with explicitly qualified transfers from the
preliminary handbook and later service illustrations.

The survey remains frozen and read-only. Scripts and `data/*.json` are the
authoritative model; generated files live under the ignored `build/` directory.
There are no required third-party FreeCAD workbenches.

## Build and inspect

From the repository root, run:

```sh
python3 cad/002_Foundation/manage.py check
python3 cad/002_Foundation/manage.py calibrate
python3 cad/002_Foundation/manage.py build
python3 cad/002_Foundation/manage.py validate
```

`build` also runs the environment checks and calibration. `validate` includes
STEP export, previews, relocation, reproducibility, parameter-change tests,
interference checks, and the original 27 survey checks on a disposable copy.
To regenerate exports without the full validation suite:

```sh
python3 cad/002_Foundation/manage.py export
```

Open **`build/native/MarkVIII_Pilot.FCStd`** in FreeCAD. Keep the entire `native/`
directory together when moving the assembly; it uses relative external links.
The generated `build/README.md` links previews and records evidence limitations.
`build/delivery_manifest.json` lists artifact checksums. Generated documents have
native view settings as well as geometry; previews do not require OpenGL.

All commands accept `--output DIRECTORY` and `--data DIRECTORY`. Paths are
resolved independently of the calling directory. Output must be separate from
research inputs. Rebuild after editing either data or Python code before running
validation/export; stale builds are rejected.

## Installed runtime

The launcher uses the tested FreeCAD **1.1.1** libraries in `/snap/freecad/current`
and their Qt runtime in `/snap/kf6-core24/current`. It starts a fresh Python process
with the necessary library paths and redirects application settings/caches under
the output directory. It does not change the ordinary desktop FreeCAD profile or
require the Snap launcher to work inside the agent sandbox.

Alternate installation roots can be supplied with `MARKVIII_FREECAD_ROOT` and
`MARKVIII_QT_ROOT`. A different FreeCAD version must be requalified before changing
the version gate in `workflow.py`. Every check records the exact FreeCAD, Open
CASCADE, and Python-package versions. The native capability probe covers a
constrained sketch, parametric pad, Boolean, NURBS solid and surface, nested links,
and FCStd/STEP round trips.

System Python needs PyMuPDF (`fitz`), Pillow, NumPy, and SciPy; these were available
on the assessed system. FreeCAD's packaged Python must be ABI-compatible with
the interpreter (tested with system Python 3.12). Qt may print an offscreen
OpenGL-widget warning: previews use geometry projection and software rendering.

## Model and evidence interfaces

| Authored data | Purpose |
|---|---|
| `parameters.json` | Millimeter values, original units, reconstruction bounds, evidence, applicability, and derivations |
| `calibrations.json` | Original/derived image paths, crop bounds, independent scale spans, held-out checks, wheel axes, traced profiles |
| `model.json` | Part definitions, survey IDs, native builders, occurrence hierarchy and placements |
| `issues.json` | Named limitations and prioritized research gaps |
| `sources.json` | Hash lock for the frozen survey and consumed sources; bounded supplementary-source inspection notes |

Parameter arithmetic permits numeric literals, parameter names, `+`, `-`, `*`,
`/`, and parentheses only. Derived parameters refer to preceding entries. Bounds
express reconstruction uncertainty or permitted study ranges; they are **not
manufacturing tolerances**. A `blocked` parameter stops the build. Missing sources,
changed locked hashes, unsupported references, invalid values, and missing part
definitions also stop it. Source-lock updates require reviewing the changed
evidence; do not regenerate hashes simply to suppress a failure.

Evidence references use `record:<survey record ID>`, `page:<source>:<printed page>`,
`calibration:<key>`, and `issue:<key>`. Survey `part_id` values are preserved; new
illustrative objects have no invented historical identifier. Occurrences have
stable IDs, parents, configuration, evidence, translation and rotation. Rotation
uses FreeCAD's yaw/pitch/roll convention in degrees; this pilot uses zero rotation.

Coordinates are millimeters, X forward, Y port, Z up. The origin is on the ground
under the rear drive axle at the tank centerline. The configuration is a static
level-ground reference, not a suspension or track-motion solution.

## What the pilot represents

- A recognizable **reference blockout**: hull, upper structures, deployed sponson
  envelopes, track outlines and drive/idler reference rims. These are not armor
  manufacturing parts and are excluded from physical STEP and part counts.
- **Six track shoe/link units**, three per side, using a shared pressed-shoe
  definition and left/right simplified link webs. Shoe width and pin pitch come
  from HB p. 137. Forming details and rail profiles are approximate; pin eyes,
  bushings, pins and rivets are deferred. There is no articulated-track claim.
- **Two five-piece rotating roller units**: two rollers, one tube, and two split
  rings each. Dimensions promoted from HB p. 141 are recorded explicitly.
  Roller waist, bore clearance and groove details remain approximations.
  Shafts, floating bushes, staples and suspension hardware are outside this
  rotating-unit scope. The stored survey assembly ID is retained.
- **One local support-joint coupon** anchored to M2078 (support angle No. 1): a
  straight L section, mating plate and two illustrative unthreaded fasteners.
  This is not the full curved support or a replacement-ready M2078 part.

There are **32 physical solid occurrences** and nine reusable part definitions.
Counts describe this pilot only, not the vehicle BOM. Shared geometry does not
establish historical left/right interchangeability.

The parts use native Sketcher/Part Design pads, revolutions and pockets. Polygon
profiles have explicit blocked geometry; edit those sketch constraints or change
the authoritative data and rebuild. The `Parameters` object retains source
values; shoe-width and plate-thickness pads also have live native expressions.
Other profile parameters require script regeneration. Record useful GUI edits in
the scripts/data before rebuilding, because regeneration replaces native files.

## Calibration and historical limitations

SNL Plates **1, 3, 4 and 10 are perspective photographs**. They are cropped for
visual checks and deliberately receive no global mm/pixel scale. Plate 4's title
does not make it an orthographic plan view.

Plate 2 is a flat-scanned longitudinal section. Its X and Z scales are fitted
independently to the provisional handbook envelope; wheel diameters are withheld
checks. Selected silhouette vertices and wheel centers are recorded in image
pixels. Plate 29 adds the roller section, using its plate-spacing dimension and
the handbook roller diameter on separate axes; roller width and tube length are
withheld checks. The report retains residual disagreements, including those
larger than point-picking uncertainty. Printed part dimensions take precedence
over scaling those particular section details; this does not resolve the wider
source/configuration conflict.

The metric SVG derivatives embed unchanged reference pixels and record separate
horizontal/vertical physical scaling. Overlays show controls and selected
profiles. Original scans, upstream restoration records and hashes remain intact.
No cleaned image is treated as proof of manufacturing precision.

The additional screw-thread report was visually checked at its title and preface;
no thread dimensions are imported because the pilot fasteners are unthreaded and
their historical type is unresolved. Only front leaves of the Lunkenheimer
catalogue were inspected; no exact valve match is claimed, and no valve is needed
for this milestone.

## Verification and next work

Validation checks solid validity, link identities, actual world-space geometry,
contact/overlap, native reopening after relocation, equivalent independent
rebuilds, propagation to all repeated shoes after changing pitch, a plate-thickness
change, and a live native expression update across external links. It exercises
missing-source, blocked-parameter and missing-linked-file diagnostics. STEP
checks use relative volume tolerance `1e-6` and bounding-coordinate tolerance
`1e-5 mm`; these numerical checks do not certify historical dimensions.

Visual review compares the pilot with the retained section and photographs.
Refer to `VISUAL_REVIEW.md` for findings, including differences deliberately left
as provisional. There are no motion joints, complete track loops, manufacturing
drawings, detailed weapons, proprietary machinery internals, or museum-measurement
claims in this milestone.

Next: refine hull plates and sponson interfaces; establish complete running-gear
stations and tracks; then develop engine/transmission installation envelopes and
supported ancillary detail. Keep production fuel tanks/Ball & Ball, Bijur units,
tank-versus-aircraft interfaces, SH642B and missing installation drawings at the
top of the research backlog. Resolve these before treating a whole-vehicle model
as dimensionally complete.
