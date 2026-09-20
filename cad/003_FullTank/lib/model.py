"""Load, check and resolve the authored model independently of the CAD runtime."""
from .evidence import STAGE, database, read, check_refs
from .parameters import resolve, scalar


def load():
    data = {name: read(STAGE / "data" / (name + ".json")) for name in
            ["model", "configuration", "parameters", "calibrations", "issues",
             "definitions", "datums", "occurrences", "visual_reviews", "roller_stations", "lower_support_runs"]}
    if data["model"]["configuration"] != data["configuration"]["id"]:
        raise ValueError("Model/configuration mismatch")
    data["values"] = resolve(data["parameters"])
    for name in ["assemblies", "patterns"]:
        path = STAGE/"data"/(name+".json")
        data[name] = read(path) if path.exists() else ({} if name == "assemblies" else [])
    from .patterns import expand
    expand(data)
    with database() as connection:
        def references(refs):
            check_refs(refs, connection, data["issues"], data["calibrations"])
        for key, item in data["parameters"].items():
            if not item.get("interpretation") or not item.get("basis") or not item.get("applicability"):
                raise ValueError("Incomplete parameter provenance: " + key)
            references(item["evidence"])
        for key, item in data["definitions"].items():
            if item["coverage"] not in {"layout_only", "partial", "finished_approximate", "finished_supported"}:
                raise ValueError("Unknown definition coverage: " + key)
            if item["representation"] not in {"layout", "assembly", "inspection"}:
                raise ValueError("Unknown representation: " + key)
            if item["representation"] == "layout" and item["coverage"].startswith("finished"):
                raise ValueError("Layout envelope cannot be a finished component: " + key)
            references(item["evidence"])
            for pid in item["survey_ids"]:
                if not connection.execute("SELECT 1 FROM parts WHERE part_id=?", (pid,)).fetchone():
                    raise ValueError("Unknown definition survey identity: " + pid)
                if data["configuration"]["decisions"].get(pid, {}).get("disposition") == "excluded":
                    raise ValueError("Definition selects an excluded configuration item: " + pid)
            geometry_arguments(item, data)
        for key, frame in data["datums"].items():
            references(frame["evidence"])
            datum_values(key, data)
        ids = {item["id"] for item in data["occurrences"]}
        if len(ids) != len(data["occurrences"]) or "Root" in ids:
            raise ValueError("Duplicate/reserved occurrence ID")
        nodes = {item["id"]: item for item in data["occurrences"]}
        def ancestry(key, seen):
            if key == "Root":
                return
            if key in seen or key not in nodes:
                raise ValueError("Missing/cyclic occurrence parent: " + key)
            parent = nodes[key]["parent"]
            if parent in nodes and nodes[parent]["definition"]:
                raise ValueError("Physical leaf cannot own child occurrences: " + parent)
            ancestry(parent, seen | {key})
        for item in data["occurrences"]:
            ancestry(item["id"], set())
            references(item["evidence"])
            if item["frame"] not in data["datums"]:
                raise ValueError("Unknown occurrence frame: " + item["id"])
            if item["definition"] and item["definition"] not in data["definitions"]:
                raise ValueError("Unknown occurrence definition: " + item["id"])
    from .track_validation import source_composition
    source_composition(data)
    return data


def point(data, calibration, pixel):
    entry = data["calibrations"][calibration]
    if entry["mode"] != "conditional_metric":
        raise ValueError("Cannot derive metric geometry from a visual-only reference")
    coords = []
    for i, axis in enumerate(["x", "z"]):
        spec = entry["axes"][axis]
        span = abs(spec["pixels"][1] - spec["pixels"][0])
        if span == 0:
            raise ValueError("Coincident calibration controls")
        scale = spec["sign"] * scalar(spec["span_parameter"], data["values"]) / span
        coords.append((pixel[i] - entry["datum_pixel"][i]) * scale)
    return coords


def datum_values(key, data, seen=None):
    seen = set() if seen is None else seen
    if key in seen or key not in data["datums"]:
        raise ValueError("Missing/cyclic datum: " + key)
    d = data["datums"][key]
    if d["parent"]:
        datum_values(d["parent"], data, seen | {key})
    if "louver_bank" in d:
        from .louver_geometry import datum
        return datum(d, data)
    if "lower_support_run" in d:
        from .lower_support_geometry import datum
        return datum(d,data)
    if "roller_station" in d:
        from .roller_geometry import datum
        return datum(d, data)
    if "idler_station" in d:
        from .wheel_geometry import datum
        return datum(d,data)
    if "drive_mount_child" in d:
        from .drive_mount_geometry import child_datum
        return child_datum(d,data)
    if "idler_child" in d:
        from .idler_geometry import child_datum
        return child_datum(d,data)
    if "wheel_child" in d:
        from .wheel_geometry import child_datum
        return child_datum(d,data)
    if "track_unit_index" in d:
        from .track_path import solve
        solution = solve(data)
        index = d["track_unit_index"]
        x,z = solution["origins"][index]
        return {"translation":[x,0,z],"rotation_deg":[0,-solution["angles_deg"][index],0],"parent":d["parent"]}
    if "source_point" in d:
        s = d["source_point"]
        x, z = point(data, s["calibration"], s["pixel"])
        tr = [x, scalar(s["y"], data["values"]), z]
    else:
        tr = [scalar(x, data["values"]) for x in d["translation"]]
    rot = [scalar(x, data["values"], (0, 1)) for x in d["rotation_deg"]]
    if len(tr) != 3 or len(rot) != 3:
        raise ValueError("A datum requires three translation and rotation coordinates")
    return {"translation": tr, "rotation_deg": rot, "parent": d["parent"]}


def geometry_arguments(definition, data):
    builder, source = definition["builder"], definition["arguments"]
    values = data["values"]
    if builder == "lower_support_component":
        from .lower_support_geometry import arguments
        return arguments(definition,data)
    if builder == "roller_component":
        from .roller_geometry import arguments
        return arguments(definition,data)
    elif builder == "drive_mount_component":
        from .drive_mount_geometry import arguments
        return arguments(definition,data)
    elif builder == "idler_component":
        from .idler_geometry import arguments
        return arguments(definition,data)
    elif builder == "wheel_component":
        from .wheel_geometry import arguments
        return arguments(definition,data)
    elif builder == "louver_component":
        from .louver_geometry import arguments
        return arguments(definition,data)
    elif builder == "sponson_plate":
        from .sponson_geometry import arguments
        return arguments(definition,data)
    elif builder == "hull_plate":
        from .hull_geometry import arguments
        return arguments(definition,data)
    elif builder in {"profile_prism", "profile_wire"}:
        entry = data["calibrations"][source["calibration"]]
        result = {"points": [point(data, source["calibration"], p) for p in entry["profiles"][source["profile"]]]}
        if builder == "profile_prism":
            result["width"] = scalar(source["width"], values)
    else:
        result = {key: scalar(value, values, (0,0) if key in {"hand"} else (1,0))
                  for key, value in source.items()}
    for key, value in result.items():
        if key in {"width", "length", "height", "depth", "diameter", "outer_diameter", "inner_diameter"} and value <= 0:
            raise ValueError("Nonpositive geometry dimension: " + key)
    if builder == "annulus" and result["inner_diameter"] >= result["outer_diameter"]:
        raise ValueError("Annulus has impossible diameters")
    return result
