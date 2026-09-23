#!/usr/bin/env python3
"""Regenerate and verify both reviewed synthetic fixtures.

From the workspace root: python3 freecad_python.py deliverables/build.py
Only the supplied JSON is dimensional input. No third-party Python packages.
"""
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile

import FreeCAD as App
import FreeCADGui as Gui
import Part


OUT = Path(__file__).resolve().parent
ROOT = OUT.parent
SPEC_PATH = ROOT / "inputs" / "stack_spec.json"
PACKET_PATH = ROOT / "inputs" / "packet.json"
# Numerical verification thresholds only, NOT manufacturing tolerances.
LENGTH_EPS = 1e-7  # mm
VOLUME_EPS = 1e-6  # mm^3, absolute threshold for intersections
REL_EPS = 1e-9
OCCURRENCES = ("PinInstance", "TubeInstance", "BushLeft", "BushRight")
DEFINITION_FOR = dict(zip(OCCURRENCES, ("Pin", "Tube", "Bush", "Bush")))
FIELDS = {
    "Pin": ("pin_radius", "pin_bore_radius", "pin_length"),
    "Tube": ("tube_outer_radius", "tube_inner_radius", "tube_length"),
    "Bush": ("bush_outer_radius", "bush_inner_radius", "bush_length"),
}
COLORS = {"Pin": (0.72, 0.75, 0.80), "Tube": (0.37, 0.51, 0.64),
          "Bush": (0.77, 0.60, 0.29)}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def close(a, b, label, absolute=LENGTH_EPS, relative=REL_EPS):
    require(math.isclose(a, b, abs_tol=absolute, rel_tol=relative),
            f"{label}: {a!r} != {b!r}")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def vector_values(v):
    return [v.x, v.y, v.z]


def frame(spec_frame):
    return App.Placement(App.Vector(*spec_frame["translation"]),
                         App.Rotation(App.Vector(*spec_frame["axis"]),
                                      spec_frame["angle_degrees"]))


def check_placement(actual, expected, label):
    close((actual.Base - expected.Base).Length, 0, label + " translation")
    # Basis vectors avoid quaternion sign and axis-angle representation ambiguity.
    for v in (App.Vector(1, 0, 0), App.Vector(0, 1, 0), App.Vector(0, 0, 1)):
        close((actual.Rotation.multVec(v) - expected.Rotation.multVec(v)).Length,
              0, label + " rotation", absolute=1e-10)


def text_property(obj, name, value):
    obj.addProperty("App::PropertyString", name, "Fixture source")
    setattr(obj, name, value)
    obj.setEditorMode(name, 1)


def hollow_solid(outer, inner, length):
    base, axis = App.Vector(0, 0, 0), App.Vector(1, 0, 0)
    shell = Part.makeCylinder(outer, length, base, axis).cut(
        Part.makeCylinder(inner, length, base, axis))
    require(len(shell.Solids) == 1, "Annular cylinder did not yield one solid")
    return shell.Solids[0]


def initialize_gui():
    # Settings remain in runtime/ through the supplied launcher. The GUI is
    # initialized only to persist native view providers, colors and a camera.
    general = App.ParamGet("User parameter:BaseApp/Preferences/General")
    general.SetString("AutoloadModule", "PartWorkbench")
    document = App.ParamGet("User parameter:BaseApp/Preferences/Document")
    document.SetBool("RecoveryEnabled", False)
    document.SetBool("AutoSaveEnabled", False)
    document.SetBool("SaveThumbnail", False)
    document.SetInt("CountBackupFiles", 0)
    start = App.ParamGet("User parameter:BaseApp/Preferences/Mod/Start")
    start.SetBool("Migration2024Complete", True)
    start.SetBool("ShowOnStartup", False)
    output = App.ParamGet("User parameter:BaseApp/Preferences/OutputWindow")
    output.SetBool("RedirectPythonOutput", False)
    output.SetBool("RedirectPythonErrors", False)
    Gui.showMainWindow()
    Gui.getMainWindow().hide()


def set_static_view(doc, spec):
    # Standard FreeCAD axonometric orientation, set directly without animation
    # or a framebuffer operation (Qt's offscreen platform has no GL context).
    view = Gui.activeDocument().activeView()
    view.setCameraType("Orthographic")
    rotation = App.Rotation(0.4247082002778669, 0.17591989660616117,
                            0.33985114297998736, 0.8204732385702833)
    center = doc.Assembly.Placement.multiply(doc.Station.Placement).Base
    distance = 2 * spec["pin_length"]
    eye = center + rotation.multVec(App.Vector(0, 0, distance))
    axis = rotation.Axis
    view.setCamera(
        "#Inventor V2.1 ascii\nOrthographicCamera {\n"
        " viewportMapping ADJUST_CAMERA\n"
        f" position {eye.x:.12g} {eye.y:.12g} {eye.z:.12g}\n"
        f" orientation {axis.x:.12g} {axis.y:.12g} {axis.z:.12g} {rotation.Angle:.12g}\n"
        " nearDistance 0.1\n"
        f" farDistance {4 * spec['pin_length']:.12g}\n"
        f" focalDistance {distance:.12g}\n"
        " aspectRatio 1\n"
        f" height {1.35 * spec['pin_length']:.12g}\n}}\n")


def offsets(spec):
    return dict(zip(OCCURRENCES, (
        -spec["pin_length"] / 2,
        -spec["tube_length"] / 2,
        -spec["tube_length"] / 2,
        spec["tube_length"] / 2 - spec["bush_length"],
    )))


def check_input(spec):
    require(spec["units"] == "mm", "Only reviewed millimetre units are supported")
    require(0 < spec["pin_bore_radius"] < spec["pin_radius"]
            < spec["bush_inner_radius"] < spec["bush_outer_radius"]
            < spec["tube_inner_radius"] < spec["tube_outer_radius"],
            "Reviewed radial dimensions are inconsistent")
    require(0 < 2 * spec["bush_length"] < spec["tube_length"] <= spec["pin_length"],
            "Reviewed axial dimensions are inconsistent")


def build_document(scenario, spec, digest):
    doc = App.newDocument(scenario)
    doc.Label = scenario
    doc.Comment = spec["historical_status"] + "; source inputs/stack_spec.json"
    defs = doc.addObject("App::Part", "Definitions")
    text_property(defs, "Scenario", scenario)
    text_property(defs, "SourceFile", "inputs/stack_spec.json")
    text_property(defs, "SourceSHA256", digest)
    text_property(defs, "HistoricalStatus", spec["historical_status"])
    for name, keys in FIELDS.items():
        obj = doc.addObject("Part::Feature", name)
        defs.addObject(obj)
        for prop, key in zip(("OuterRadius", "InnerRadius", "Length"), keys):
            obj.addProperty("App::PropertyLength", prop, "Reviewed fixture dimensions",
                            "stack_spec.json: " + key + " (mm)")
            setattr(obj, prop, spec[key])
            # These describe the stored BRep. Rebuild from JSON to change it.
            obj.setEditorMode(prop, 1)
        text_property(obj, "DimensionKeys", ", ".join(keys))
        obj.Shape = hollow_solid(*(spec[k] for k in keys))
        obj.Placement = App.Placement()
        obj.ViewObject.ShapeColor = COLORS[name]
        obj.ViewObject.LineColor = (0.15, 0.15, 0.15)
        obj.ViewObject.DisplayMode = "Flat Lines"
        obj.ViewObject.Deviation = 0.05
        obj.ViewObject.AngularDeflection = 10
    assembly = doc.addObject("App::Part", "Assembly")
    assembly.Placement = frame(spec["assembly_frame"])
    station = doc.addObject("App::Part", "Station")
    assembly.addObject(station)
    station.Placement = frame(spec["station_frame"])
    for name, x in offsets(spec).items():
        link = doc.addObject("App::Link", name)
        station.addObject(link)
        link.setLink(doc.getObject(DEFINITION_FOR[name]))
        link.LinkPlacement = App.Placement(App.Vector(x, 0, 0), App.Rotation())
        link.Visibility = True
    doc.recompute()
    defs.Visibility = False
    for name in FIELDS:
        doc.getObject(name).Visibility = False
    assembly.Visibility = True
    station.Visibility = True
    set_static_view(doc, spec)
    return doc


def check_definition(obj, values):
    outer, inner, length = values
    shape = obj.Shape
    require(shape.ShapeType == "Solid" and len(shape.Solids) == 1
            and shape.isValid() and shape.isClosed(), obj.Name + " invalid solid")
    check_placement(obj.Placement, App.Placement(), obj.Name + " definition")
    close(shape.Volume, math.pi * (outer**2 - inner**2) * length,
          obj.Name + " analytic volume", absolute=VOLUME_EPS)
    require(len(shape.Faces) == 4, obj.Name + " unexpected face count")
    cylinders = [f.Surface for f in shape.Faces if isinstance(f.Surface, Part.Cylinder)]
    planes = [f.Surface for f in shape.Faces if isinstance(f.Surface, Part.Plane)]
    require(len(cylinders) == len(planes) == 2, obj.Name + " non-analytic faces")
    for actual, expected in zip(sorted(c.Radius for c in cylinders), (inner, outer)):
        close(actual, expected, obj.Name + " cylindrical radius")
    for c in cylinders:
        close(abs(c.Axis.x), 1, obj.Name + " cylinder axis")
        close(math.hypot(c.Center.y, c.Center.z), 0, obj.Name + " concentricity")
    for actual, expected in zip(sorted(p.Position.x for p in planes), (0, length)):
        close(actual, expected, obj.Name + " end-plane X")
    for p in planes:
        close(abs(p.Axis.x), 1, obj.Name + " end-plane normal")
    # Direct interior tests distinguish an annulus from a capped or solid cylinder.
    require(not shape.isInside(App.Vector(length / 2, 0, 0), LENGTH_EPS, True),
            obj.Name + " bore obstructed")
    require(shape.isInside(App.Vector(length / 2, (inner + outer) / 2, 0),
                           LENGTH_EPS, True), obj.Name + " wall missing")
    for prop, expected in zip(("OuterRadius", "InnerRadius", "Length"), values):
        close(getattr(obj, prop).Value, expected, obj.Name + "." + prop)
    return {"volume_mm3": shape.Volume, "analytic_cylinders": 2,
            "planar_annular_ends": 2, "through_bore_clear": True}


def check_document(doc, spec, digest):
    require(doc.Definitions.TypeId == doc.Assembly.TypeId == doc.Station.TypeId == "App::Part",
            "Incorrect container types")
    require({o.Name for o in doc.Definitions.Group} == set(FIELDS), "Definitions membership")
    require([o.Name for o in doc.Assembly.Group] == ["Station"], "Assembly membership")
    require([o.Name for o in doc.Station.Group] == list(OCCURRENCES), "Station membership")
    require({o.Name for o in doc.Objects if o.TypeId == "App::Link"} == set(OCCURRENCES),
            "Document must contain exactly four links")
    require(doc.Definitions.SourceSHA256 == digest, "Saved input source hash")
    require(doc.Definitions.HistoricalStatus == spec["historical_status"], "Historical status")
    check_placement(doc.Definitions.Placement, App.Placement(), "Definitions frame")
    check_placement(doc.Assembly.Placement, frame(spec["assembly_frame"]), "Assembly frame")
    check_placement(doc.Station.Placement, frame(spec["station_frame"]), "Station frame")
    report = {"definitions": {}, "occurrences": {}, "pairwise_common_volume_mm3": {}}
    for name, keys in FIELDS.items():
        report["definitions"][name] = check_definition(doc.getObject(name), [spec[k] for k in keys])
    world = {}
    total_frame = frame(spec["assembly_frame"]).multiply(frame(spec["station_frame"]))
    for name, x in offsets(spec).items():
        link = doc.getObject(name)
        definition = doc.getObject(DEFINITION_FOR[name])
        require(link.LinkedObject == definition, name + " shared-definition reference")
        close(link.Scale, 1, name + " scale")
        for component in vector_values(link.ScaleVector):
            close(component, 1, name + " scale vector")
        local = App.Placement(App.Vector(x, 0, 0), App.Rotation())
        check_placement(link.LinkPlacement, local, name + " local placement")
        expected = total_frame.multiply(local)
        actual = doc.Assembly.getSubObject("Station." + name + ".", 3)
        check_placement(actual, expected, name + " resolved hierarchy")
        # Resolve the actual installed hierarchy, including both parent frames.
        resolved = Part.getShape(doc.Assembly, "Station." + name + ".")
        require(len(resolved.Solids) == 1 and resolved.isValid(), name + " resolved solid")
        solid = resolved.Solids[0]
        expected_center = expected.multVec(App.Vector(definition.Length.Value / 2, 0, 0))
        close((solid.CenterOfMass - expected_center).Length, 0, name + " world centroid")
        close(solid.Volume, definition.Shape.Volume, name + " world volume", absolute=VOLUME_EPS)
        world[name] = solid
        report["occurrences"][name] = {
            "definition": definition.Name, "station_start_x_mm": x,
            "station_end_x_mm": x + definition.Length.Value,
            "world_start_mm": vector_values(expected.Base),
            "world_end_mm": vector_values(expected.multVec(App.Vector(definition.Length.Value, 0, 0))),
            "world_centroid_mm": vector_values(solid.CenterOfMass),
            "volume_mm3": solid.Volume,
        }
    for a, b in itertools.combinations(OCCURRENCES, 2):
        volume = world[a].common(world[b]).Volume
        require(volume <= VOLUME_EPS, f"Overlap between {a} and {b}: {volume}")
        report["pairwise_common_volume_mm3"][a + "/" + b] = volume
    distances = {"pin_to_bush": world["PinInstance"].distToShape(world["BushLeft"])[0],
                 "bush_to_tube": world["BushLeft"].distToShape(world["TubeInstance"])[0]}
    close(distances["pin_to_bush"], spec["bush_inner_radius"] - spec["pin_radius"], "Pin/bush gap")
    close(distances["bush_to_tube"], spec["tube_inner_radius"] - spec["bush_outer_radius"], "Bush/tube gap")
    report["measured_radial_clearance_mm"] = distances
    report["world_station_axis"] = vector_values(total_frame.Rotation.multVec(App.Vector(1, 0, 0)))
    return report, world


def check_saved_view(path):
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("GuiDocument.xml"))
    visibility = {}
    for name in ("Definitions", "Pin", "Tube", "Bush", "Assembly", "Station", *OCCURRENCES):
        node = root.find(f"./ViewProviderData/ViewProvider[@name='{name}']/Properties/Property[@name='Visibility']/Bool")
        require(node is not None, "Missing saved visibility: " + name)
        visibility[name] = node.get("value") == "true"
        require(visibility[name] == (name in ("Assembly", "Station", *OCCURRENCES)),
                "Incorrect saved visibility: " + name)
    camera = root.find("Camera").get("settings")
    require("OrthographicCamera" in camera, "Missing standard orthographic saved camera")
    return {"visibility": visibility, "camera": camera}


def check_step(path, world):
    imported = Part.read(str(path))
    require(imported.ShapeType == "Compound", "STEP is not a compound")
    require(imported.isValid() and len(imported.Solids) == 4, "STEP must contain four valid solids")
    remaining = list(imported.Solids)
    errors = {}
    for name, expected in world.items():
        actual = min(remaining, key=lambda s: (s.CenterOfMass - expected.CenterOfMass).Length)
        remaining.remove(actual)
        centroid_error = (actual.CenterOfMass - expected.CenterOfMass).Length
        close(centroid_error, 0, name + " STEP centroid")
        close(actual.Volume, expected.Volume, name + " STEP volume", absolute=VOLUME_EPS)
        # Symmetric differences detect translation, rotation, lost bores and extra material.
        mismatch = actual.cut(expected).Volume + expected.cut(actual).Volume
        require(mismatch <= VOLUME_EPS, name + " STEP geometry mismatch")
        require(sum(isinstance(f.Surface, Part.Cylinder) for f in actual.Faces) == 2,
                name + " STEP analytic cylinders lost")
        errors[name] = {"centroid_error_mm": centroid_error,
                        "symmetric_difference_mm3": mismatch}
    return {"valid": True, "shape_type": imported.ShapeType, "solid_count": 4,
            "total_volume_mm3": imported.Volume, "round_trip": errors}


def write_notes(specs, digest):
    rows = []
    for scenario, spec in specs.items():
        x = offsets(spec)
        rows.append(f"| {scenario} | {spec['pin_length']:.2f} | {spec['tube_length']:.2f} | "
                    f"{spec['bush_length']:.2f} | {x['PinInstance']:.3f} | "
                    f"{x['TubeInstance']:.3f} | {x['BushLeft']:.3f} | {x['BushRight']:.3f} |")
    text = """# Synthetic hollow pin / tube / two-bush fixture

Implemented both supplied scenarios without changing input dimensions, datums,
frames, identities or units. **Synthetic interface qualification fixture; not
accepted tank geometry.** The packet reviews internal consistency only.

## Reproduce

From this workspace root, run:

```sh
python3 freecad_python.py deliverables/build.py
```

The builder reads `inputs/packet.json` and `inputs/stack_spec.json`, verifies the
packet's source SHA-256, rebuilds both FCStd and STEP files, reopens and checks
the saved artifacts, and regenerates these notes and `checks.json`. It requires
the installed FreeCAD supplied by the launcher; no installation or external
service is used. It writes its outputs in `deliverables/`; the launcher keeps
FreeCAD settings and scratch data in this workspace's `runtime/`.

Source identity: `benchmarks/cad_work_packets/fixtures/stack_spec.json` as recorded
in the packet; the only available dimensional source is its supplied JSON copy.
Source SHA-256: `DIGEST`.

## Native model and export

Each native document contains `Definitions` (App::Part) with exactly three
analytic Part::Feature solids named `Pin`, `Tube`, `Bush`. Their placements are
identity; each annular cylinder starts at X=0 and extends along local +X.
Named read-only `OuterRadius`, `InnerRadius`, `Length` properties retain the
supplied values and identify their JSON keys. Use the builder to regenerate
geometry; changing a custom property alone is not a parametric rebuild.

`Assembly` is at the exact assembly_frame. Its child `Station` is at the exact
station_frame relative to Assembly. Station contains exactly four App::Link
occurrences: `PinInstance`, `TubeInstance`, `BushLeft`, `BushRight`. The bushes
reference the same Bush object. Link rotations and scales are identity. World
placement is Assembly × Station × link. No frame is flattened in the native file.
FreeCAD-generated Origin objects are container infrastructure, not added solids.

All following axial coordinates are in Station, in mm:

| Scenario | Pin length | Tube length | Each bush length | Pin start | Tube start | Left bush start | Right bush start |
|---|---:|---:|---:|---:|---:|---:|---:|
ROWS

Pin and tube are centered at Station X=0. The left bush starts at -tube_length/2;
the right bush ends at +tube_length/2. Pin protrusion at each end is 53.975 mm
(nominal) and 55.975 mm (variant). The space between bushes is 446.1 mm and
454.1 mm, respectively.

The STEP is one unfused compound containing exactly the four installed,
world-space solids, obtained from the native occurrence hierarchy. Source
definition solids are excluded. STEP preserves analytic surfaces and all four
through hollows, but not the native App::Link sharing and hierarchy; use FCStd
for occurrence identities and `checks.json` for their world-coordinate mapping.

Definitions and its three source features are hidden in the saved views;
Assembly, Station and the four occurrences are visible. The saved camera is
static world axonometric, orthographic, with room around the entire stack.
Colors distinguish pin, tube and bushes for review only; they specify no material.

## Fixture fits, missing evidence and approximations

Both scenarios have pin outer radius 28.5369 mm and bore radius 4.0 mm; bush
inner/outer radii 28.6369/34.775 mm; tube inner/outer radii 34.925/48.4124 mm.
The pin/bush clearance is 0.1000 mm radial (0.2000 mm diametral); bush/tube
clearance is 0.1500 mm radial (0.3000 mm diametral). These are nominal fixture
assumptions, not historical measurements, tolerance classes or a qualified fit.

No manufacturing tolerances, historical drawings, material properties, surface
finish, loads, lubrication, retention details or tank qualification evidence
were supplied. No such evidence is inferred. No chamfers, fillets, interference,
fasteners, deformation or thermal effects are added. The solids are ideal
coaxial circular cylinders with planar annular ends; booleans retain the hollows.
Analytic BRep geometry is not approximated with mesh facets. GUI tessellation
is display-only; STEP serialization and floating-point arithmetic have finite
numerical precision. Frame axes are normalized by FreeCAD's axis-angle API.

## Checks and limits

`checks.json` records successful checks for both scenarios after reopening their
FCStd files: container/link membership, shared Bush identity, named dimensions,
identity definition and link rotations, both reviewed parent frames, local and
world placements, valid closed solids, exact analytic surface types/radii/end
planes, analytic volumes, clear bores, and all six pairwise intersections.
The minimum radial separations are measured from the installed BReps. All six
pairwise common volumes are zero in each scenario.

Each STEP is reimported and checked for four valid solids, cylindrical surfaces,
world centroids, volumes and zero symmetric-difference volumes against the native
installed solids. The saved XML is checked for visibility and orthographic camera
state. Output SHA-256 values are recorded in `checks.json`.

Numerical assertions use 1e-7 mm absolute length/centroid tolerance, 1e-10 for
rotation basis vectors, 1e-9 relative scalar tolerance, and 1e-6 mm³ absolute
volume/intersection tolerance. These are computational check thresholds, not
new design or manufacturing tolerances.

The Qt offscreen platform has no working OpenGL framebuffer here. Native view
providers and camera were saved and inspected as data; no successful rendered
image or thumbnail is claimed. Visual acceptance, source review and independent
acceptance remain for the subsequent review specified by the work packet.
"""
    (OUT / "notes.md").write_text(text.replace("DIGEST", digest).replace("ROWS", "\n".join(rows)))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
    packet = json.loads(PACKET_PATH.read_text())
    require(packet["id"] == "stack", "Unexpected packet identity")
    digest = sha256(SPEC_PATH)
    source = next(i for i in packet["inputs"] if i["destination"] == "stack_spec.json")
    require(digest == source["sha256"], "Input specification hash differs from reviewed packet")
    specs = json.loads(SPEC_PATH.read_text())
    require(set(specs) == {"nominal", "variant"}, "Unexpected scenario identities")
    initialize_gui()
    report = {"status": "passed", "source_sha256": digest,
              "packet_sha256": sha256(PACKET_PATH), "freecad_version": App.Version(),
              "numerical_thresholds": {"length_mm": LENGTH_EPS, "relative": REL_EPS,
                                       "rotation_basis": 1e-10, "volume_mm3": VOLUME_EPS},
              "scenarios": {}}
    try:
        for scenario in ("nominal", "variant"):
            print("Building and checking", scenario, flush=True)
            spec = specs[scenario]
            check_input(spec)
            doc = build_document(scenario, spec, digest)
            _, world = check_document(doc, spec, digest)
            compound = Part.makeCompound([world[n] for n in OCCURRENCES])
            compound.exportStep(str(OUT / (scenario + ".step")))
            native_path = OUT / (scenario + ".FCStd")
            doc.recompute()
            doc.saveAs(str(native_path))
            App.closeDocument(doc.Name)
            doc = App.openDocument(str(native_path))
            scenario_report, world = check_document(doc, spec, digest)
            scenario_report["saved_view"] = check_saved_view(native_path)
            scenario_report["step"] = check_step(OUT / (scenario + ".step"), world)
            scenario_report["status"] = "passed"
            report["scenarios"][scenario] = scenario_report
            App.closeDocument(doc.Name)
        write_notes(specs, digest)
        require(sha256(SPEC_PATH) == digest, "Source input changed during build")
        report["output_sha256"] = {}
        for relative in packet["outputs"]:
            path = ROOT / relative
            require(path.is_file() and path.stat().st_size > 0, "Missing declared output: " + relative)
            report["output_sha256"][relative] = sha256(path)
        (OUT / "checks.json").write_text(json.dumps(report, indent=2) + "\n")
        print("PASS: both native documents and both four-solid STEP compounds verified.")
    finally:
        for name in list(App.listDocuments()):
            App.closeDocument(name)


if __name__ == "__main__":
    main()
