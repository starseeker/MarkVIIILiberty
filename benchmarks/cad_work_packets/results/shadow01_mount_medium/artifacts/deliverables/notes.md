# Mount repair

Synthetic diagnostic fixture, not a historical mount design. Source inputs are `inputs/packet.json`, `inputs/mount_spec.json`, and `inputs/broken_mount.FCStd`. Both declared input SHA256 hashes were verified. Inputs and the FreeCAD launcher were not modified.

Reproduce from the workspace root:

```sh
python3 freecad_python.py deliverables/build.py
```

The builder opens the supplied native file and diagnoses each occurrence against the specification. It edits only violating link placements and fails if a defect does not match the diagnosed frame-composition error. No geometry is rebuilt and no document objects are added or removed.

`BoltLeft1` incorrectly held the expected world transform in its local placement: position approximately (329.396926, 170, -83.420201) mm with the composed left-side orientation. Its correct local placement is (20, -10, 0) mm with identity rotation. `BoltRight2` similarly held approximately (329.396926, -70, -83.420201) mm with the composed right-side orientation; its correct local placement is (20, 10, 0) mm with identity rotation. These decimal values are explanatory approximations; the builder uses the specification directly.

World placement is `T_Rig * T_side * T_occurrence`. Storing that full transform in an occurrence applies the parent frames twice. Rig, side frames, both plate placements, and the six other bolt placements were already valid and remain unchanged. Definition links and shapes are preserved.

Checks actually run using FreeCAD 1.1.1:

- Input hashes, all 48 object names/types/labels, parent references, group ordering, link targets and LinkTransform flags.
- Rig and side frames against the specification; all ten local occurrence placements; preservation of every other object's placement.
- Exact definition BREP strings before and after the in-memory repair. Save/reopen changes BREP serialization; reopened definition validity, face/edge/vertex counts, volumes and bidirectional Boolean differences were checked instead of claiming byte-identical serialization.
- Ten individually valid installed solids; comparison of explicitly composed world shapes against FreeCAD's native recursive Rig shape by bidirectional Boolean difference.
- All 45 solid pairs checked for intersection volume: maximum 0 mm³.
- STEP readback: ten valid solids, individually matched by world center of mass and volume, with bidirectional geometric differences checked.
- Native save/reopen: structure, placements, definition geometry and ten-solid Rig validity checked again.

The STEP is an unfused compound containing two plates and eight bolts in world coordinates. Shared definition solids are not separately exported. Total installed volume is approximately 58429.380460548 mm³. Machine-readable results are in `checks.json`; `build.log` records the run.

No manufacturing tolerances were supplied. Matrix comparisons use a numerical threshold of 1e-8; STEP/reopen geometry checks use 1e-6 mm for centers and 1e-6 mm³ for volumes. These are computational checks, not new design tolerances. No source shape, reviewed datum or stated dimension was changed. No meshing or geometric approximation was used in the repair or STEP export.

Missing evidence: interfaces are explicitly unreviewed in the packet. There is no evidence here for mechanical loading, fastener engagement, manufacturing suitability, or historical authenticity. This session performed static CAD diagnostics and geometry checks, not GUI standard-view visual review. Independent acceptance and source/visual review remain for the subsequent review stage stated in the request.
