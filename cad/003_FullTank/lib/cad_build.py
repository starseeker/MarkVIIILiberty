"""Native reusable parts, linked subsystem documents and world-space traversal."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import time

import FreeCAD as App
import Part
import Sketcher
import _PartDesign
import AssemblyApp

from .evidence import STAGE, write, read, sha
from .model import datum_values, geometry_arguments

COLORS = {
    "HullStructure": (0.55, 0.60, 0.54), "RunningGear": (0.37, 0.40, 0.35),
    "Sponsons": (0.62, 0.66, 0.51), "Powerplant": (0.54, 0.64, 0.72),
    "Drivetrain": (0.55, 0.50, 0.62), "CoolingVentilation": (0.48, 0.68, 0.61),
    "FuelPressure": (0.74, 0.65, 0.40), "ElectricalInstruments": (0.70, 0.47, 0.39),
    "CrewControlsAndEquipment": (0.65, 0.52, 0.38), "ArmamentRepresentation": (0.42, 0.47, 0.41),
}


def metadata(obj, **values):
    for key, value in values.items():
        typ = "App::PropertyBool" if isinstance(value, bool) else "App::PropertyString"
        if key not in obj.PropertiesList:
            obj.addProperty(typ, key, "Reconstruction")
        setattr(obj, key, value if isinstance(value, (str, bool)) else json.dumps(value, ensure_ascii=False))


def frame(key, data, cache=None):
    cache = {} if cache is None else cache
    if key in cache:
        return cache[key]
    d = datum_values(key, data)
    local = App.Placement(App.Vector(*d["translation"]), App.Rotation(*d["rotation_deg"]))
    result = frame(d["parent"], data, cache).multiply(local) if d["parent"] else local
    cache[key] = result
    return result


def sketch_polygon(body, name, pts, placement):
    sketch = body.newObject("Sketcher::SketchObject", name)
    sketch.Placement = placement
    for a, b in zip(pts, pts[1:] + pts[:1]):
        index = sketch.addGeometry(Part.LineSegment(App.Vector(*a, 0), App.Vector(*b, 0)), False)
        sketch.addConstraint(Sketcher.Constraint("Block", index))
    return sketch


def pad(body, sketch, length):
    feature = body.newObject("PartDesign::Pad", "Extrusion")
    feature.Profile = sketch
    feature.Length = length
    body.Document.recompute()
    sketch.Visibility = False
    return feature


def part(doc, key, definition, arguments):
    builder = definition["builder"]
    if builder.startswith("track_"):
        from .track_parts import build as build_track
        obj = build_track(doc, "Def_"+key, builder, arguments)
    elif builder.startswith("upper_"):
        from .upper_parts import build as build_upper
        obj = build_upper(doc, "Def_"+key, builder, arguments)
    elif builder == "lower_support_component":
        from .lower_support_parts import build as build_support
        obj = build_support(doc, "Def_"+key, arguments)
    elif builder == "roller_component":
        from .roller_parts import build as build_roller
        obj = build_roller(doc, "Def_"+key, arguments)
    elif builder == "drive_mount_component":
        from .drive_mount_parts import build as build_drive_mount
        obj = build_drive_mount(doc, "Def_"+key, arguments)
    elif builder == "idler_component":
        from .idler_parts import build as build_idler
        obj = build_idler(doc, "Def_"+key, arguments)
    elif builder == "wheel_component":
        from .wheel_parts import build as build_wheel
        obj = build_wheel(doc, "Def_"+key, arguments)
    elif builder == "louver_component":
        from .louver_parts import build as build_louver
        obj = build_louver(doc, "Def_"+key, arguments)
    elif builder == "sponson_plate":
        from .sponson_parts import build as build_sponson
        obj = build_sponson(doc, "Def_"+key, arguments)
    elif builder == "hull_plate":
        from .hull_parts import build as build_hull
        obj = build_hull(doc, "Def_"+key, arguments)
    elif builder == "profile_wire":
        obj = doc.addObject("PartDesign::Feature", "Def_" + key)
        pts = [App.Vector(x, 0, z) for x, z in arguments["points"]]
        obj.Shape = Part.makePolygon(pts + pts[:1])
    else:
        obj = doc.addObject("PartDesign::Body", "Def_" + key)
        along_y = App.Rotation(App.Vector(1, 0, 0), -90)
        if builder == "profile_prism":
            w = arguments["width"]
            sketch = sketch_polygon(obj, "Profile", [(x, -z) for x, z in arguments["points"]],
                                    App.Placement(App.Vector(0, -w/2, 0), along_y))
            pad(obj, sketch, w)
        elif builder in {"cylinder", "annulus"}:
            diameter = arguments.get("diameter", arguments.get("outer_diameter"))
            length = arguments.get("length", arguments.get("width"))
            sketch = obj.newObject("Sketcher::SketchObject", "Section")
            sketch.Placement = App.Placement(App.Vector(0, -length/2, 0), along_y)
            radii = [diameter/2] + ([arguments["inner_diameter"]/2] if builder == "annulus" else [])
            for radius in radii:
                index = sketch.addGeometry(Part.Circle(App.Vector(), App.Vector(0, 0, 1), radius), False)
                sketch.addConstraint(Sketcher.Constraint("Coincident", index, 3, -1, 1))
                sketch.addConstraint(Sketcher.Constraint("Radius", index, radius))
            pad(obj, sketch, length)
        elif builder == "box":
            length, width, height = (arguments[k] for k in ["length", "width", "height"])
            sketch = sketch_polygon(obj, "Footprint", [(-length/2,-width/2),(length/2,-width/2),
                                     (length/2,width/2),(-length/2,width/2)], App.Placement())
            pad(obj, sketch, height)
        elif builder == "sponson_envelope":
            length, depth, height = (arguments[k] for k in ["length", "depth", "height"])
            sketch = sketch_polygon(obj, "Plan", [(-length/2,0),(-length*0.3,depth),
                                     (length*0.3,depth),(length/2,0)], App.Placement())
            pad(obj, sketch, height)
        else:
            raise ValueError("Unknown native builder: " + builder)
    obj.Label = definition["label"]
    metadata(obj, DefinitionId=key, SurveyIds=definition["survey_ids"], Representation=definition["representation"],
             Coverage=definition["coverage"], ReferenceOnly=definition["representation"] == "layout",
             EvidenceReferences=definition["evidence"], ReconstructionNotes=definition["notes"],
             Configuration="ROCK_ISLAND_FIRST_100", Subsystem=definition["subsystem"],
             GeometryInputs=arguments)
    obj.ViewObject.ShapeColor = COLORS[definition["subsystem"]]
    obj.ViewObject.LineColor = (0.12, 0.14, 0.12)
    obj.ViewObject.Transparency = 70 if key in {"central_hull", "track_frame"} else 0
    doc.recompute()
    if obj.Shape.isNull() or not obj.Shape.isValid():
        raise ValueError("Invalid definition geometry: " + key)
    if builder != "profile_wire" and (len(obj.Shape.Solids) != 1 or obj.Shape.Volume <= 0):
        raise ValueError("Expected one closed solid: " + key)
    return obj


def shape_signature(shape):
    box = shape.optimalBoundingBox(False)
    return {"solids": len(shape.Solids), "volume_mm3": shape.Volume,
            "bounds_mm": [getattr(box, k) for k in ["XMin","YMin","ZMin","XMax","YMax","ZMax"]]}


def build(data, out, selected=None):
    start = time.monotonic()
    for name in list(App.listDocuments()):
        App.closeDocument(name)
    native = out / "native"
    (native / "library").mkdir(parents=True, exist_ok=True)
    (native / "subsystems").mkdir(exist_ok=True)
    systems = [x["id"] for x in data["occurrences"] if x["parent"] == "Root"]
    if selected:
        if selected not in systems:
            raise ValueError("Unknown subsystem: " + selected)
        systems = [selected]
    definitions, grouped, stats = {}, defaultdict(dict), {}
    for key, spec in data["definitions"].items():
        if spec["subsystem"] in systems:
            grouped[spec["subsystem"]][key] = spec
    code_hash = {p.name: sha(p) for p in [Path(__file__), STAGE/"lib/model.py", STAGE/"lib/parameters.py",
                                        STAGE/"lib/track_parts.py", STAGE/"lib/upper_parts.py",
                                        STAGE/"lib/patterns.py", STAGE/"lib/track_path.py",
                                        STAGE/"lib/hull_geometry.py", STAGE/"lib/hull_parts.py",
                                        STAGE/"lib/sponson_geometry.py", STAGE/"lib/sponson_parts.py",
                                        STAGE/"lib/louver_geometry.py", STAGE/"lib/louver_parts.py",
                                        STAGE/"lib/roller_geometry.py", STAGE/"lib/roller_parts.py",
                                        STAGE/"lib/wheel_geometry.py", STAGE/"lib/wheel_parts.py",
                                        STAGE/"lib/idler_geometry.py", STAGE/"lib/idler_parts.py",
                                        STAGE/"lib/drive_mount_geometry.py", STAGE/"lib/drive_mount_parts.py",
                                        STAGE/"lib/lower_support_geometry.py", STAGE/"lib/lower_support_parts.py"]}
    for system in systems:
        specifications = grouped[system]
        if not specifications:
            continue
        inputs = {key: geometry_arguments(spec, data) for key, spec in specifications.items()}
        payload = {"specifications": specifications, "arguments": inputs, "code": code_hash,
                   "FreeCAD": App.Version(), "OpenCASCADE": Part.OCC_VERSION}
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        path = native / "library" / (system + ".FCStd")
        cache_path = out / "cache" / (system + ".json")
        cached = read(cache_path) if cache_path.is_file() else {}
        if path.is_file() and cached.get("input_hash") == digest and cached.get("file_hash") == sha(path):
            doc = App.openDocument(str(path))
            for key in specifications:
                obj = doc.getObject("Def_" + key)
                if obj is None or obj.Shape.isNull() or not obj.Shape.isValid():
                    raise ValueError("Invalid cached native definition: " + key)
                definitions[key] = obj
            reused = True
        else:
            doc = App.newDocument("Library_" + system)
            for key, spec in specifications.items():
                definitions[key] = part(doc, key, spec, inputs[key])
            doc.recompute()
            doc.saveAs(str(path))
            write(cache_path, {"input_hash": digest, "file_hash": sha(path)})
            reused = False
        stats[system] = {"definitions": len(specifications), "cache_reused": reused, "input_hash": digest}
    nodes = {x["id"]: x for x in data["occurrences"]}
    def system_of(item):
        if item["parent"] == "Root":
            return item["id"]
        return system_of(nodes[item["parent"]])
    assembled = {}
    for system in systems:
        doc = App.newDocument("Assembly_" + system)
        root = doc.addObject("App::Part", "Root")
        root.Label = system
        metadata(root, OccurrenceId=system, Subsystem=system)
        doc.saveAs(str(native / "subsystems" / (system + ".FCStd")))
        objects = {system: root}
        pending = [x for x in data["occurrences"] if x["id"] != system and system_of(x) == system]
        while pending:
            ready = [x for x in pending if x["parent"] in objects]
            if not ready:
                raise ValueError("Unresolvable assembly parents: " + system)
            for item in ready:
                parent = objects[item["parent"]]
                obj = doc.addObject("App::Link" if item["definition"] else "App::Part", item["id"])
                parent.addObject(obj)
                parent_frame = frame(nodes[item["parent"]]["frame"], data)
                local = parent_frame.inverse().multiply(frame(item["frame"], data))
                if item["definition"]:
                    obj.setLink(definitions[item["definition"]])
                    obj.LinkPlacement = local
                else:
                    obj.Placement = local
                metadata(obj, OccurrenceId=item["id"], DefinitionId=item["definition"] or "",
                         DatumId=item["frame"], EvidenceReferences=item["evidence"], Subsystem=system,
                         AssemblyTemplate=item.get("assembly_template",""), SurveyIds=item.get("survey_ids",[]))
                objects[item["id"]] = obj
                pending.remove(item)
        doc.recompute()
        doc.save()
        assembled[system] = root
    doc = App.newDocument("MarkVIII_Assembly")
    root = doc.addObject("Assembly::AssemblyObject", "Root")
    root.Label = "Mark VIII — production reconstruction in progress"
    metadata(root, Configuration=data["configuration"]["id"], ModelRevision=data["model"]["revision"],
             ReconstructionNotes=data["model"]["scope_note"], PhysicalRelease=False)
    name = "MarkVIII_" + selected + ".FCStd" if selected else "MarkVIII.FCStd"
    doc.saveAs(str(native / name))
    for system, target in assembled.items():
        link = doc.addObject("App::Link", system)
        root.addObject(link)
        link.setLink(target)
        link.LinkPlacement = frame(nodes[system]["frame"], data)
        metadata(link, OccurrenceId=system, Subsystem=system)
    doc.recompute()
    App.setActiveDocument(doc.Name)
    import FreeCADGui as Gui
    Gui.activeDocument().activeView().viewAxonometric()
    Gui.activeDocument().activeView().fitAll()
    doc.save()
    return doc, {"subsystems": stats, "seconds": time.monotonic() - start, "top_document": str(doc.FileName),
                 "selected_subsystem": selected, "definitions": len(definitions)}


def leaves(root):
    """Resolve nested external links; geometry is counted only at definition leaves."""
    result = []
    def visit(obj, parent, occurrence, system, stack):
        token = (obj.Document.Name, obj.Name)
        if token in stack:
            raise ValueError("Cyclic linked assembly: " + str(token))
        stack = stack | {token}
        is_link = obj.TypeId == "App::Link"
        if is_link:
            if obj.LinkedObject is None:
                raise ValueError("Missing native link: " + obj.Name)
            world = parent.multiply(obj.LinkPlacement)
            target = obj.LinkedObject
            ident = getattr(obj, "OccurrenceId", occurrence)
            subsystem = getattr(obj, "Subsystem", system)
            if getattr(target, "DefinitionId", ""):
                shape = target.Shape.copy()
                shape.Placement = world.multiply(shape.Placement)
                result.append({"id": ident, "definition": target.DefinitionId, "shape": shape,
                               "object": obj, "target": target, "system": subsystem,
                               "representation": target.Representation, "coverage": target.Coverage})
            else:
                visit(target, world, ident, subsystem, stack)
        else:
            world = parent.multiply(getattr(obj, "Placement", App.Placement()))
            for child in getattr(obj, "Group", []):
                visit(child, world, occurrence, system, stack)
    visit(root, App.Placement(), "", "", set())
    return result
