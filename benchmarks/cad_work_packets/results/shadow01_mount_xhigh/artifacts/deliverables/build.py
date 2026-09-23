"""Repair the supplied native assembly, then verify native and STEP round trips.

Run from the workspace root:
    python3 freecad_python.py deliverables/build.py

Only occurrence LinkPlacement values that fail mount_spec.json are assigned.
No objects, definition geometry, assembly frames, or presentation settings are
created or changed in the native document. All generated files stay here.
"""

import copy
import hashlib
import itertools
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

import FreeCAD as App
import Part


OUT = Path(__file__).resolve().parent
ROOT = OUT.parent
INPUT = ROOT / "inputs"
# Numerical verification thresholds, NOT design or manufacturing tolerances.
POSITION_EPS = 1e-8  # mm, native placement/geometry comparisons
ROTATION_EPS = 1e-10  # dimensionless, rotated unit-vector comparisons
STEP_POSITION_EPS = 1e-7  # mm, STEP round trip
VOLUME_EPS = 1e-6  # mm^3, boolean/volume comparisons


def require(condition, description):
    if not condition:
        raise RuntimeError(description)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def placement(frame):
    return App.Placement(
        App.Vector(*frame["translation"]),
        App.Rotation(App.Vector(*frame["axis"]), frame["angle_degrees"]),
    )


def placement_error(actual, expected):
    translation = (actual.Base - expected.Base).Length
    rotation = max(
        (actual.Rotation.multVec(axis) - expected.Rotation.multVec(axis)).Length
        for axis in (App.Vector(1, 0, 0), App.Vector(0, 1, 0), App.Vector(0, 0, 1))
    )
    return translation, rotation


def same_placement(actual, expected):
    distance, rotation = placement_error(actual, expected)
    return distance <= POSITION_EPS and rotation <= ROTATION_EPS


def coordinates(vector):
    return [vector.x, vector.y, vector.z]


def placement_record(value):
    return {"translation": coordinates(value.Base), "quaternion_xyzw": list(value.Rotation.Q)}


def snapshot(doc):
    """Capture object identities, graph, link configuration, shapes and placements."""
    result = {}
    for obj in doc.Objects:
        info = {
            "type": obj.TypeId,
            "label": obj.Label,
            "properties": sorted(obj.PropertiesList),
            "parents_and_referrers": sorted(item.Name for item in obj.InList),
            "children_and_references": sorted(item.Name for item in obj.OutList),
        }
        for key in ("Group", "OriginFeatures"):
            if key in obj.PropertiesList:
                info[key] = [item.Name for item in getattr(obj, key)]
        if "Origin" in obj.PropertiesList:
            info["Origin"] = obj.Origin.Name
        if "Visibility" in obj.PropertiesList:
            info["Visibility"] = obj.Visibility
        if "Placement" in obj.PropertiesList:
            info["Placement"] = App.Placement(obj.Placement)
        if obj.TypeId == "App::Link":
            info["LinkedObject"] = obj.LinkedObject.Name
            info["LinkPlacement"] = App.Placement(obj.LinkPlacement)
            for key in ("LinkTransform", "ElementCount", "Scale", "LinkCopyOnChange", "LinkClaimChild"):
                info[key] = getattr(obj, key)
            info["ScaleVector"] = coordinates(obj.ScaleVector)
        for key in ("Shape", "SuppressedShape", "PreviewShape"):
            if key in obj.PropertiesList:
                shape = getattr(obj, key)
                info[key] = hashlib.sha256(shape.exportBrepToString().encode()).hexdigest()
        result[obj.Name] = info
    return result


def verify_preservation(before, after, changed):
    require(set(before) == set(after), "Object names changed")
    for name, original in before.items():
        current = after[name]
        require(set(original) == set(current), f"Snapshot keys changed for {name}")
        for key, value in original.items():
            if key in ("Placement", "LinkPlacement"):
                if name not in changed:
                    require(same_placement(value, current[key]), f"Valid placement changed: {name}.{key}")
            else:
                require(value == current[key], f"Invariant changed: {name}.{key}")


def brep_payloads(path):
    with zipfile.ZipFile(path) as archive:
        return {
            name: hashlib.sha256(archive.read(name)).hexdigest()
            for name in archive.namelist()
            if name.endswith(".brp")
        }


def preserve_untouched_native_data(source, saved, changed):
    """Keep source archive data, carrying over only FreeCAD's repaired placements.

    FreeCAD/OCC save rewrites topology bookkeeping flags and can normalize
    untouched datum quaternions in the last decimal place. Neither is needed
    for this repair. Preserve the original payloads and properties exactly,
    importing ONLY the two placement properties of each changed link from the
    document actually repaired and saved by FreeCAD. Reopen/check the result.
    """
    with zipfile.ZipFile(source) as original, zipfile.ZipFile(saved) as repaired:
        entries = [(item, original.read(item.filename)) for item in original.infolist()]
        source_xml = ET.fromstring(original.read("Document.xml"))
        saved_xml = ET.fromstring(repaired.read("Document.xml"))
    original_tree = copy.deepcopy(source_xml)
    original_objects = {obj.get("name"): obj for obj in source_xml.find("ObjectData")}
    repaired_objects = {obj.get("name"): obj for obj in saved_xml.find("ObjectData")}
    for name in changed:
        old_properties = original_objects[name].find("Properties")
        new_properties = repaired_objects[name].find("Properties")
        for key in ("Placement", "LinkPlacement"):
            old = old_properties.find(f"Property[@name='{key}']")
            new = new_properties.find(f"Property[@name='{key}']")
            require(old is not None and new is not None, f"Missing saved placement: {name}.{key}")
            index = list(old_properties).index(old)
            old_properties.remove(old)
            old_properties.insert(index, copy.deepcopy(new))

    def canonical(node):
        return node.tag, sorted(node.attrib.items()), (node.text or "").strip(), [canonical(child) for child in node]

    # Compare the entire native document data after masking only allowed edits.
    masked = copy.deepcopy(source_xml)
    masked_objects = {obj.get("name"): obj for obj in masked.find("ObjectData")}
    original_check = {obj.get("name"): obj for obj in original_tree.find("ObjectData")}
    for name in changed:
        for objects in (masked_objects, original_check):
            properties = objects[name].find("Properties")
            for key in ("Placement", "LinkPlacement"):
                properties.remove(properties.find(f"Property[@name='{key}']"))
    require(canonical(masked) == canonical(original_tree), "Unrelated native XML data changed")
    xml_bytes = ET.tostring(source_xml, encoding="utf-8", xml_declaration=True)
    temporary = OUT / ".preserved.FCStd"
    try:
        with zipfile.ZipFile(temporary, "w") as archive:
            for info, payload in entries:
                archive.writestr(info, xml_bytes if info.filename == "Document.xml" else payload)
        temporary.replace(saved)
    finally:
        if temporary.exists():
            temporary.unlink()
    with zipfile.ZipFile(source) as original, zipfile.ZipFile(saved) as repaired:
        require(original.namelist() == repaired.namelist(), "Native archive member list changed")
        for name in original.namelist():
            if name != "Document.xml":
                require(original.read(name) == repaired.read(name), f"Native payload changed: {name}")


def one_solid(shape, description):
    require(not shape.isNull() and shape.isValid(), f"Invalid shape: {description}")
    require(len(shape.Solids) == 1, f"Expected one solid: {description}")
    solid = shape.Solids[0]
    require(solid.isClosed() and solid.Volume > 0, f"Non-closed or empty solid: {description}")
    return solid


def compare_solids(actual, expected, description, position_eps=POSITION_EPS):
    a = one_solid(actual, description)
    b = one_solid(expected, description + " reference")
    require((a.CenterOfMass - b.CenterOfMass).Length <= position_eps, f"Center mismatch: {description}")
    for field in ("XMin", "YMin", "ZMin", "XMax", "YMax", "ZMax"):
        require(abs(getattr(a.BoundBox, field) - getattr(b.BoundBox, field)) <= position_eps,
                f"Bounds mismatch: {description}.{field}")
    require(abs(a.Volume - b.Volume) <= VOLUME_EPS, f"Volume mismatch: {description}")
    difference = abs(a.cut(b).Volume) + abs(b.cut(a).Volume)
    require(difference <= VOLUME_EPS, f"Geometry mismatch: {description} ({difference} mm^3)")
    return difference


def occurrences(doc, spec):
    require(doc.Rig.TypeId == "App::Part", "Unexpected Rig type")
    require([obj.Name for obj in doc.Rig.Group] == list(spec["side_frames"]), "Unexpected Rig hierarchy")
    require(same_placement(doc.Rig.Placement, placement(spec["rig_frame"])), "Rig frame violates spec; refusing occurrence-only repair")
    result = []
    for side_name, frame in spec["side_frames"].items():
        side = doc.getObject(side_name)
        require(side.TypeId == "App::Part", f"Unexpected {side_name} type")
        require(same_placement(side.Placement, placement(frame)), f"{side_name} frame violates spec; refusing occurrence-only repair")
        expected = [("Plate" + side_name, "Plate", App.Placement())]
        expected += [
            (f"Bolt{side_name}{index}", "Bolt", App.Placement(App.Vector(x, y, 0), App.Rotation()))
            for index, (x, y) in enumerate(spec["holes"])
        ]
        require([obj.Name for obj in side.Group] == [item[0] for item in expected], f"Unexpected {side_name} hierarchy")
        for name, definition, local in expected:
            obj = doc.getObject(name)
            require(obj.TypeId == "App::Link", f"Unexpected occurrence type: {name}")
            require(obj.LinkedObject == doc.getObject(definition), f"Unexpected shared definition: {name}")
            require(not obj.LinkTransform and obj.ElementCount == 0, f"Unexpected link behavior: {name}")
            require(obj.Scale == 1 and coordinates(obj.ScaleVector) == [1, 1, 1], f"Unexpected scale: {name}")
            require(same_placement(obj.LinkedObject.Placement, App.Placement()), "Nonidentity definition placement")
            result.append((side_name, obj, local))
    require(len(result) == 10, "Expected exactly ten installed occurrences")
    require({obj.Name for obj in doc.Objects if obj.TypeId == "App::Link"} == {obj.Name for _, obj, _ in result},
            "Unexpected additional links")
    return result


def installed_solids(doc, spec):
    result = []
    for side_name, obj, local in occurrences(doc, spec):
        require(same_placement(obj.LinkPlacement, local), f"Local placement still violates contract: {obj.Name}")
        parent = doc.Rig.Placement.multiply(doc.getObject(side_name).Placement)
        # App::Link.Shape already contains its local placement, but no parent
        # placement. Apply the Rig/side transform exactly once to a shape copy.
        shape = obj.Shape.copy()
        shape.Placement = parent.multiply(shape.Placement)
        solid = one_solid(shape, obj.Name)
        # Independent FreeCAD hierarchy traversal checks the installed transform.
        traversed = doc.Rig.getSubObject(f"{side_name}.{obj.Name}.")
        compare_solids(solid, traversed, f"FreeCAD hierarchy traversal: {obj.Name}")
        # Independent reference uses the specification frames and unchanged BREP.
        reference = obj.LinkedObject.Shape.copy()
        world = placement(spec["rig_frame"]).multiply(placement(spec["side_frames"][side_name])).multiply(local)
        reference.Placement = world.multiply(reference.Placement)
        compare_solids(solid, reference, f"Specification world placement: {obj.Name}")
        result.append((obj.Name, solid))
    rig_shape = Part.getShape(doc.Rig)
    require(rig_shape.isValid() and len(rig_shape.Solids) == 10, "Native Rig is not ten valid solids")
    require(abs(rig_shape.Volume - sum(s.Volume for _, s in result)) <= VOLUME_EPS, "Rig volume mismatch")
    return result


def inspect_definition_geometry(doc, spec):
    plate = one_solid(doc.Plate.Shape, "Plate definition")
    bolt = one_solid(doc.Bolt.Shape, "Bolt definition")
    cylinders = [face.Surface for face in plate.Faces if isinstance(face.Surface, Part.Cylinder)]
    require(len(cylinders) == len(spec["holes"]), "Plate hole count differs from contract")
    hole_radii = []
    for x, y in spec["holes"]:
        candidates = [c for c in cylinders if math.hypot(c.Center.x - x, c.Center.y - y) <= POSITION_EPS]
        require(len(candidates) == 1, "Hole XY cannot be matched to source geometry")
        cylinder = candidates[0]
        require(abs(abs(cylinder.Axis.z) - 1) <= ROTATION_EPS, "Hole is not parallel to local Z")
        hole_radii.append(cylinder.Radius)
    bolt_cylinders = [face.Surface for face in bolt.Faces if isinstance(face.Surface, Part.Cylinder)]
    require(len(bolt_cylinders) == 1, "Unexpected source bolt geometry")
    cylinder = bolt_cylinders[0]
    require(math.hypot(cylinder.Center.x, cylinder.Center.y) <= POSITION_EPS and abs(abs(cylinder.Axis.z) - 1) <= ROTATION_EPS,
            "Bolt cylinder is not centered on local Z")
    return plate, bolt, hole_radii, cylinder.Radius


def write_notes(spec, source_hashes, changes, total_objects, solids, plate, bolt, hole_radii, bolt_radius,
                clearances, max_overlap, max_step_difference, max_step_center_error):
    bounds = Part.makeCompound([shape for _, shape in solids]).BoundBox
    rows = []
    for item in changes:
        before = item["before"]
        rows.append(
            f"| {item['name']} | {', '.join(f'{v:.9f}' for v in before['translation'])} | "
            f"{', '.join(f'{v:.9f}' for v in before['quaternion_xyzw'])} | "
            f"{', '.join(f'{v:g}' for v in item['after']['translation'])} |"
        )
    world_rows = []
    for name, solid in solids:
        world_rows.append(f"| {name} | " + ", ".join(f"{v:.9f}" for v in coordinates(solid.CenterOfMass)) + f" | {solid.Volume:.9f} |")
    notes = f"""# Mount occurrence repair

This is the supplied synthetic cross-assembly diagnostic fixture, not a historical mount design. Units are {spec['units']}.

## Reproduce

From the workspace root run:

```sh
python3 freecad_python.py deliverables/build.py
```

The builder reads only the supplied inputs, checks their packet SHA-256 identities, opens the native file in FreeCAD, diagnoses every installed occurrence against the specification, and assigns only violating `LinkPlacement` values. Together with this builder, it produces all five declared deliverables and raises an exception if a check fails. It uses installed FreeCAD {'.'.join(App.Version()[:3])} and Open CASCADE {getattr(Part, 'OCC_VERSION', 'version unavailable')}; no additional software or external service is used. FreeCAD's supplied launcher keeps runtime settings under the workspace. Reproduction means the same assembly and diagnosis; STEP file metadata may vary between runs.

FreeCAD's initial native save changed only topology bookkeeping bits in the BREP payloads and normalized four untouched datum quaternion components in the last decimal place. The builder therefore preserves the original archive payloads and original document data, carrying over only FreeCAD's saved `Placement` and `LinkPlacement` properties for the two repaired links. It verifies that all other native XML data is identical and every non-XML archive payload is byte-identical, then reopens and checks that final native file. This preserves the original datums, geometry, and stored modeling tolerances without serialization drift.

## Diagnosis and exact repair

Only {', '.join('`' + item['name'] + '`' for item in changes)} violated the local placement contract. All other occurrences, the Rig frame, and both side frames passed before repair. The source has {total_objects} objects, including origin axes/planes/points; none was added, deleted, renamed, retyped, reparented, or edited geometrically.

For column-vector transforms, `W = R * S * L`, where `R` is the Rig placement, `S` is the side placement relative to Rig, and `L` is the occurrence placement relative to that side. Each defective stored `L_bad` equals `R * S * L_required` within the stated numerical check thresholds. FreeCAD therefore evaluates the defective installed placement as `R * S * R * S * L_required`. Applying `(R * S)^-1` to the defective stored value recovers the specified hole placement. This establishes a world-to-local frame assignment error from the CAD data; the upstream edit history itself was not supplied.

The repair assigns the exact hole XY, Z=0 and identity rotation from the specification. Plate links stay at identity. The two changed links continue to reference the original shared `Bolt` definition. Local rotations after repair are the identity quaternion `(0, 0, 0, 1)`.

| Occurrence | Before local translation, mm | Before quaternion x,y,z,w | After local translation, mm |
| --- | --- | --- | --- |
{chr(10).join(rows)}

Rig remains translated `(320, 50, -80)` and rotated 20 degrees about Y. Left remains translated `(0, 100, 0)` and rotated +90 degrees about Z relative to Rig; Right remains translated `(0, -100, 0)` and rotated -90 degrees about Z relative to Rig. All source origin/datum placements and all previously valid object placements are preserved.

## Checks actually run by the builder

- Verified both source hashes against `packet.json`; checked again after all CAD operations. Input files were never saved or edited.
- Inspected all {total_objects} native objects, identities/types, labels, property inventories, reference/parent graphs, ordered groups, origins, and placements. Verified unchanged link targets, scale, link behavior, visibility, and definition/auxiliary shape BREP hashes immediately after repair and after saving/reopening `fixed.FCStd`.
- Compared every native `.brp` payload against the source archive byte for byte by SHA-256, and all other non-XML payloads by direct byte comparison. All shared and suppressed shape payloads are unchanged. Compared the complete native XML data after excluding only the four repaired placement properties: all other data is identical. Rechecked every required local placement after the native round trip. A second diagnostic pass found no remaining violations.
- Confirmed two valid closed source solids. Matched all four actual plate cylindrical hole axes to the specification's XY coordinates. The measured plate is {plate.BoundBox.XLength:g} x {plate.BoundBox.YLength:g} x {plate.BoundBox.ZLength:g} mm, local Z={plate.BoundBox.ZMin:g} to {plate.BoundBox.ZMax:g}. Hole radii are {', '.join(f'{r:g}' for r in hole_radii)} mm. The source Bolt is a plain radius-{bolt_radius:g} mm cylinder, local Z={bolt.BoundBox.ZMin:g} to {bolt.BoundBox.ZMax:g}; its source identity is retained.
- Constructed ten world-space solids from the installed links by applying `Rig * side` once to each already locally placed link shape. Compared each with FreeCAD's accumulated hierarchy traversal and with an independently composed specification placement applied to the unchanged definition. Checked validity, solid count, center of mass, bounds, volume, and symmetric boolean difference. Native Rig extraction also contains exactly ten solids.
- Checked all 45 installed solid pairs for volumetric overlap: maximum common volume {max_overlap:.12g} mm^3. Measured each of the eight bolt-to-corresponding-plate minimum distances: range {min(clearances):.12g} to {max(clearances):.12g} mm. This agrees with the source geometry's nominal 0.5 mm radial gap.
- Exported one STEP compound containing exactly two installed plates and eight installed bolts; the uninstalled definitions are excluded, and the solids are not fused. Read `fixed.step` back using Open CASCADE and matched its ten valid closed solids one-to-one to installed native solids by center of mass, then checked bounds, volumes, and symmetric boolean differences. Maximum center error {max_step_center_error:.12g} mm; maximum symmetric-difference volume {max_step_difference:.12g} mm^3.

Total installed volume: {sum(s.Volume for _, s in solids):.12f} mm^3. World bounding box `(xmin, ymin, zmin; xmax, ymax, zmax)` in mm: `({bounds.XMin:.9f}, {bounds.YMin:.9f}, {bounds.ZMin:.9f}; {bounds.XMax:.9f}, {bounds.YMax:.9f}, {bounds.ZMax:.9f})`.

| Installed occurrence | World center of mass, mm | Volume, mm^3 |
| --- | --- | --- |
{chr(10).join(world_rows)}

Numerical check thresholds are {POSITION_EPS:g} mm for native positions/bounds, {ROTATION_EPS:g} for differences of rotated unit vectors, {STEP_POSITION_EPS:g} mm for STEP positions/bounds, and {VOLUME_EPS:g} mm^3 for volume/boolean differences. These are floating-point verification thresholds, not new or altered design tolerances. No design fit tolerance was stated in the supplied specification.

## Evidence and limits

The only design evidence supplied is `mount_spec.json` and `broken_mount.FCStd`, with the instructions and source identifiers in `packet.json`. Packet review flags are dimensions=true, sources=true, interfaces=false. No interface approval, manufacturing tolerance, fastening/thread/head detail, materials, load cases, or physical test evidence was supplied. No such details were inferred or added. No new geometry approximation was introduced: definition BREP payloads are preserved. STEP translation is subject to normal numerical representation effects quantified above. This work checks the static assembly only; no motion, structural validation, or GUI/standard-view visual acceptance was performed. Independent source, visual, and acceptance review remains outside this session.

## Source identities

{chr(10).join('- `' + name + '`: `' + digest + '`' for name, digest in source_hashes.items())}

Declared outputs: `build.py`, `notes.md`, `fixed.FCStd`, `fixed.step`, and `diagnosis.json`, all in `deliverables/`.
"""
    (OUT / "notes.md").write_text(notes)


def main():
    OUT.mkdir(exist_ok=True)
    packet = json.loads((INPUT / "packet.json").read_text())
    spec = json.loads((INPUT / "mount_spec.json").read_text())
    require(spec["units"] == "mm", "Unexpected units")
    source_hashes = {"packet.json": sha256(INPUT / "packet.json")}
    for item in packet["inputs"]:
        path = INPUT / item["destination"]
        require(path.resolve().parent == INPUT.resolve(), "Input path escapes inputs")
        digest = sha256(path)
        require(digest == item["sha256"], f"Source hash mismatch: {path.name}")
        source_hashes[path.name] = digest
    source = INPUT / "broken_mount.FCStd"
    original_breps = brep_payloads(source)
    doc = App.openDocument(str(source))
    try:
        before = snapshot(doc)
        plate, bolt, hole_radii, bolt_radius = inspect_definition_geometry(doc, spec)
        changes = []
        for side_name, obj, required in occurrences(doc, spec):
            if same_placement(obj.LinkPlacement, required):
                continue
            stored = App.Placement(obj.LinkPlacement)
            parent = doc.Rig.Placement.multiply(doc.getObject(side_name).Placement)
            require(same_placement(stored, parent.multiply(required)), f"Unexpected defect mechanism: {obj.Name}")
            require(same_placement(parent.inverse().multiply(stored), required), f"Frame inversion fails: {obj.Name}")
            changes.append({"name": obj.Name, "before": placement_record(stored), "after": placement_record(required)})
            obj.LinkPlacement = required
        doc.recompute()
        changed = [item["name"] for item in changes]
        verify_preservation(before, snapshot(doc), changed)
        installed_solids(doc, spec)
        fixed_path = OUT / "fixed.FCStd"
        # Avoid creating backup copies on repeated reproduction runs.
        if fixed_path.exists():
            fixed_path.unlink()
        doc.saveAs(str(fixed_path))
    finally:
        App.closeDocument(doc.Name)

    preserve_untouched_native_data(source, fixed_path, changed)
    require(brep_payloads(fixed_path) == original_breps, "Native BREP payloads changed on save")
    fixed = App.openDocument(str(fixed_path))
    try:
        verify_preservation(before, snapshot(fixed), changed)
        solids = installed_solids(fixed, spec)
        max_overlap = 0.0
        for (name_a, a), (name_b, b) in itertools.combinations(solids, 2):
            overlap = abs(a.common(b).Volume)
            require(overlap <= VOLUME_EPS, f"Installed solid overlap: {name_a}/{name_b}")
            max_overlap = max(max_overlap, overlap)
        by_name = dict(solids)
        clearances = []
        for side in spec["side_frames"]:
            for index in range(len(spec["holes"])):
                distance = by_name[f"Bolt{side}{index}"].distToShape(by_name[f"Plate{side}"])[0]
                require(abs(distance - (hole_radii[index] - bolt_radius)) <= POSITION_EPS, "Unexpected bolt/plate clearance")
                clearances.append(distance)

        compound = Part.makeCompound([solid for _, solid in solids])
        require(compound.isValid() and len(compound.Solids) == 10, "Invalid export compound")
        step_path = OUT / "fixed.step"
        compound.exportStep(str(step_path))
        imported = Part.Shape()
        imported.read(str(step_path))
        require(imported.isValid() and len(imported.Solids) == 10, "STEP must contain exactly ten valid solids")
        unmatched = list(imported.Solids)
        max_step_difference = 0.0
        max_step_center_error = 0.0
        for name, expected in solids:
            actual = min(unmatched, key=lambda shape: (shape.CenterOfMass - expected.CenterOfMass).Length)
            max_step_center_error = max(max_step_center_error, (actual.CenterOfMass - expected.CenterOfMass).Length)
            max_step_difference = max(max_step_difference, compare_solids(actual, expected, f"STEP round trip: {name}", STEP_POSITION_EPS))
            unmatched.remove(actual)
        require(not unmatched, "Unmatched STEP solids")
        for name, digest in source_hashes.items():
            require(sha256(INPUT / name) == digest, f"Input changed during build: {name}")
        cause = (
            "BoltLeft1 and BoltRight2 stored their intended WORLD placements in their side-local LinkPlacement fields. "
            "With W = Rig * Side * Local, each defective Local equals Rig * Side * the required hole placement, "
            "so FreeCAD applies the parent frames twice: Rig * Side * Rig * Side * required_local. "
            "CAD comparison and inverse-parent composition confirm this error. Reset only those links to their "
            "specified side-local translations (20, -10, 0) and (20, 10, 0), respectively, with identity rotation. "
            "Preserved Rig/side frames, all other placements, all object names/types/hierarchy, and shared definitions."
        )
        (OUT / "diagnosis.json").write_text(json.dumps({"changed_objects": changed, "cause": cause}, indent=2) + "\n")
        write_notes(spec, source_hashes, changes, len(before), solids, plate, bolt, hole_radii, bolt_radius,
                    clearances, max_overlap, max_step_difference, max_step_center_error)
        for output in packet["outputs"]:
            path = ROOT / output
            require(path.resolve().parent == OUT and path.is_file() and path.stat().st_size > 0, f"Missing output: {output}")
        print(json.dumps({
            "status": "PASS",
            "changed_objects": changed,
            "preserved_objects": len(before),
            "installed_step_solids": len(imported.Solids),
            "installed_volume_mm3": compound.Volume,
            "maximum_pair_overlap_mm3": max_overlap,
            "bolt_plate_distance_range_mm": [min(clearances), max(clearances)],
            "maximum_step_center_error_mm": max_step_center_error,
            "maximum_step_symmetric_difference_mm3": max_step_difference,
            "definition_brep_payloads_unchanged": True,
            "input_hashes_unchanged": True,
        }, indent=2))
    finally:
        App.closeDocument(fixed.Name)


if __name__ == "__main__":
    main()
