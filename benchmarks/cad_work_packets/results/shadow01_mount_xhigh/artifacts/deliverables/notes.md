# Mount occurrence repair

This is the supplied synthetic cross-assembly diagnostic fixture, not a historical mount design. Units are mm.

## Reproduce

From the workspace root run:

```sh
python3 freecad_python.py deliverables/build.py
```

The builder reads only the supplied inputs, checks their packet SHA-256 identities, opens the native file in FreeCAD, diagnoses every installed occurrence against the specification, and assigns only violating `LinkPlacement` values. Together with this builder, it produces all five declared deliverables and raises an exception if a check fails. It uses installed FreeCAD 1.1.1 and Open CASCADE 7.8.0; no additional software or external service is used. FreeCAD's supplied launcher keeps runtime settings under the workspace. Reproduction means the same assembly and diagnosis; STEP file metadata may vary between runs.

FreeCAD's initial native save changed only topology bookkeeping bits in the BREP payloads and normalized four untouched datum quaternion components in the last decimal place. The builder therefore preserves the original archive payloads and original document data, carrying over only FreeCAD's saved `Placement` and `LinkPlacement` properties for the two repaired links. It verifies that all other native XML data is identical and every non-XML archive payload is byte-identical, then reopens and checks that final native file. This preserves the original datums, geometry, and stored modeling tolerances without serialization drift.

## Diagnosis and exact repair

Only `BoltLeft1`, `BoltRight2` violated the local placement contract. All other occurrences, the Rig frame, and both side frames passed before repair. The source has 48 objects, including origin axes/planes/points; none was added, deleted, renamed, retyped, reparented, or edited geometrically.

For column-vector transforms, `W = R * S * L`, where `R` is the Rig placement, `S` is the side placement relative to Rig, and `L` is the occurrence placement relative to that side. Each defective stored `L_bad` equals `R * S * L_required` within the stated numerical check thresholds. FreeCAD therefore evaluates the defective installed placement as `R * S * R * S * L_required`. Applying `(R * S)^-1` to the defective stored value recovers the specified hole placement. This establishes a world-to-local frame assignment error from the CAD data; the upstream edit history itself was not supplied.

The repair assigns the exact hole XY, Z=0 and identity rotation from the specification. Plate links stay at identity. The two changed links continue to reference the original shared `Bolt` definition. Local rotations after repair are the identity quaternion `(0, 0, 0, 1)`.

| Occurrence | Before local translation, mm | Before quaternion x,y,z,w | After local translation, mm |
| --- | --- | --- | --- |
| BoltLeft1 | 329.396926208, 170.000000000, -83.420201433 | 0.122787804, 0.122787804, 0.696364240, 0.696364240 | 20, -10, 0 |
| BoltRight2 | 329.396926208, -70.000000000, -83.420201433 | 0.122787804, -0.122787804, 0.696364240, -0.696364240 | 20, 10, 0 |

Rig remains translated `(320, 50, -80)` and rotated 20 degrees about Y. Left remains translated `(0, 100, 0)` and rotated +90 degrees about Z relative to Rig; Right remains translated `(0, -100, 0)` and rotated -90 degrees about Z relative to Rig. All source origin/datum placements and all previously valid object placements are preserved.

## Checks actually run by the builder

- Verified both source hashes against `packet.json`; checked again after all CAD operations. Input files were never saved or edited.
- Inspected all 48 native objects, identities/types, labels, property inventories, reference/parent graphs, ordered groups, origins, and placements. Verified unchanged link targets, scale, link behavior, visibility, and definition/auxiliary shape BREP hashes immediately after repair and after saving/reopening `fixed.FCStd`.
- Compared every native `.brp` payload against the source archive byte for byte by SHA-256, and all other non-XML payloads by direct byte comparison. All shared and suppressed shape payloads are unchanged. Compared the complete native XML data after excluding only the four repaired placement properties: all other data is identical. Rechecked every required local placement after the native round trip. A second diagnostic pass found no remaining violations.
- Confirmed two valid closed source solids. Matched all four actual plate cylindrical hole axes to the specification's XY coordinates. The measured plate is 60 x 40 x 12 mm, local Z=0 to 12. Hole radii are 3.5, 3.5, 3.5, 3.5 mm. The source Bolt is a plain radius-3 mm cylinder, local Z=-4 to 16; its source identity is retained.
- Constructed ten world-space solids from the installed links by applying `Rig * side` once to each already locally placed link shape. Compared each with FreeCAD's accumulated hierarchy traversal and with an independently composed specification placement applied to the unchanged definition. Checked validity, solid count, center of mass, bounds, volume, and symmetric boolean difference. Native Rig extraction also contains exactly ten solids.
- Checked all 45 installed solid pairs for volumetric overlap: maximum common volume 0 mm^3. Measured each of the eight bolt-to-corresponding-plate minimum distances: range 0.5 to 0.5 mm. This agrees with the source geometry's nominal 0.5 mm radial gap.
- Exported one STEP compound containing exactly two installed plates and eight installed bolts; the uninstalled definitions are excluded, and the solids are not fused. Read `fixed.step` back using Open CASCADE and matched its ten valid closed solids one-to-one to installed native solids by center of mass, then checked bounds, volumes, and symmetric boolean differences. Maximum center error 9.29720394087e-12 mm; maximum symmetric-difference volume 0 mm^3.

Total installed volume: 58429.380460547691 mm^3. World bounding box `(xmin, ymin, zmin; xmax, ymax, zmax)` in mm: `(301.206147584, -80.000000000, -88.205032346; 342.898094136, 180.000000000, -60.518656204)`.

| Installed occurrence | World center of mass, mm | Volume, mm^3 |
| --- | --- | --- |
| PlateLeft | 322.052120860, 150.000000000, -74.361844275 | 26952.743519689 |
| BoltLeft0 | 331.449047068, 130.000000000, -77.782045709 | 565.486677646 |
| BoltLeft1 | 331.449047068, 170.000000000, -77.782045709 | 565.486677646 |
| BoltLeft2 | 312.655194652, 170.000000000, -70.941642842 | 565.486677646 |
| BoltLeft3 | 312.655194652, 130.000000000, -70.941642842 | 565.486677646 |
| PlateRight | 322.052120860, -50.000000000, -74.361844275 | 26952.743519689 |
| BoltRight0 | 312.655194652, -30.000000000, -70.941642842 | 565.486677646 |
| BoltRight1 | 312.655194652, -70.000000000, -70.941642842 | 565.486677646 |
| BoltRight2 | 331.449047068, -70.000000000, -77.782045709 | 565.486677646 |
| BoltRight3 | 331.449047068, -30.000000000, -77.782045709 | 565.486677646 |

Numerical check thresholds are 1e-08 mm for native positions/bounds, 1e-10 for differences of rotated unit vectors, 1e-07 mm for STEP positions/bounds, and 1e-06 mm^3 for volume/boolean differences. These are floating-point verification thresholds, not new or altered design tolerances. No design fit tolerance was stated in the supplied specification.

## Evidence and limits

The only design evidence supplied is `mount_spec.json` and `broken_mount.FCStd`, with the instructions and source identifiers in `packet.json`. Packet review flags are dimensions=true, sources=true, interfaces=false. No interface approval, manufacturing tolerance, fastening/thread/head detail, materials, load cases, or physical test evidence was supplied. No such details were inferred or added. No new geometry approximation was introduced: definition BREP payloads are preserved. STEP translation is subject to normal numerical representation effects quantified above. This work checks the static assembly only; no motion, structural validation, or GUI/standard-view visual acceptance was performed. Independent source, visual, and acceptance review remains outside this session.

## Source identities

- `packet.json`: `da0f780b6ca2317381c5f8ea61b4dbc30c98b9650e783e0020d6c512d0abcd53`
- `mount_spec.json`: `7cc784e0419ba14ca74c548f0b9afeba3fb7623f3bb5cd34c706cbe6040f7445`
- `broken_mount.FCStd`: `c2d52ac7a2ddcc317ea3c6313b070a7870304179570420794499dbb179b461df`

Declared outputs: `build.py`, `notes.md`, `fixed.FCStd`, `fixed.step`, and `diagnosis.json`, all in `deliverables/`.
