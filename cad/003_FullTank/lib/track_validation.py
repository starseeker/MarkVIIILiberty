"""Independent SNL composition checks and native track-interface qualification."""
from collections import Counter

from .evidence import database, write


def source_composition(data):
    """Compare authored templates with the frozen SNL BOM, not duplicated counts."""
    checks = []
    with database() as connection:
        def source(pid, stack=()):
            if pid in stack:
                raise ValueError("Cyclic source composition: " + pid)
            edges = list(connection.execute("SELECT child_part_id,quantity_per_parent FROM v_bom_edges "
                                            "WHERE parent_part_id=? AND source_id='SNL' AND relation='composed_of'", (pid,)))
            if not edges:
                return Counter({pid:1})
            result = Counter()
            for edge in edges:
                count = edge["quantity_per_parent"]
                if count is None or count < 1 or int(count) != count:
                    raise ValueError("Unresolved source assembly quantity: " + pid)
                result.update({key:int(count)*value for key,value in source(edge["child_part_id"],stack+(pid,)).items()})
            return result
        def authored(key):
            result = Counter()
            for child in data["assemblies"][key]["children"]:
                if child.get("assembly"):
                    result.update(authored(child["assembly"]))
                else:
                    ids = data["definitions"][child["definition"]]["survey_ids"]
                    if len(ids) != 1:
                        raise ValueError("Track composition needs a reviewed unique identity mapping")
                    result.update(ids)
            return result
        for key,spec in data.get("assemblies",{}).items():
            if not spec.get("survey_ids"):
                continue
            if len(spec["survey_ids"]) != 1:
                raise ValueError("Assembly source alias mapping requires explicit review")
            expected = source(spec["survey_ids"][0])
            actual = authored(key)
            omitted=Counter(spec.get('omitted_source_counts',{}))
            if omitted and (spec.get('composition_status')!='partial' or
                            any(not isinstance(v,int) or v<1 for v in omitted.values())):
                raise ValueError('Invalid explicit partial composition: '+key)
            if expected != actual+omitted:
                raise ValueError("Source composition mismatch for " + key + ": " + str(dict(actual)) + " != " + str(dict(expected)))
            checks.append({"template":key,"source_part_id":spec["survey_ids"][0],"leaf_counts":dict(expected),
                           "leaf_total":sum(expected.values()),"modeled_counts":dict(actual),
                           "omitted_counts":dict(omitted),"complete":not bool(omitted),"passed":True})
    return checks


def bend_trials(data, components):
    """Sample two installed units about their shared pin axis; no continuous-range claim."""
    import FreeCAD as App
    from .cad_build import frame
    first = [i for i in components if i["id"].startswith("PortTrack_Unit000_")]
    second = [i for i in components if i["id"].startswith("PortTrack_Unit001_")]
    if not first or not second:
        return []
    pitch = data["values"]["shoe_pitch"].value
    def flatten(items,identifier,offset):
        transform = App.Placement(App.Vector(offset,0,0),App.Rotation()).multiply(frame(identifier,data).inverse())
        result = []
        for item in items:
            shape = item["shape"].copy()
            shape.Placement = transform.multiply(shape.Placement)
            result.append(dict(item,shape=shape))
        return result
    first = flatten(first,"PortTrack_Unit000",0)
    second = flatten(second,"PortTrack_Unit001",pitch)
    pivot = App.Vector(pitch/2,0,data["values"]["track_pin_height"].value)
    results = []
    for angle in [-10,-5,0,10,20,30,35]:
        transform = App.Placement(pivot,App.Rotation(App.Vector(0,1,0),-angle)).multiply(App.Placement(-pivot,App.Rotation()))
        turned = []
        for item in second:
            shape = item["shape"].copy()
            shape.Placement = transform.multiply(shape.Placement)
            turned.append(dict(item,shape=shape))
        overlaps = []
        for a in first:
            for b in turned:
                if a["shape"].BoundBox.intersect(b["shape"].BoundBox):
                    volume = a["shape"].common(b["shape"]).Volume
                    if volume > 1e-3:
                        overlaps.append({"a":a["id"],"b":b["id"],"volume_mm3":volume})
        results.append({"angle_deg":angle,"noninterference_passed":not overlaps,"overlaps":overlaps,
                        "scope":"Sampled joint angle only; wheel contact and intermediate angles remain unqualified."})
    return results


def pitch_checks(data, items):
    import FreeCAD as App
    from .cad_build import frame
    present = {i["id"] for i in items}
    pitch = data["values"]["shoe_pitch"].value
    height = data["values"]["track_pin_height"].value
    checks = []
    for pattern in data.get("patterns",[]):
        if pattern.get('mode')!='closed_track' and pattern.get('assembly')!='track_unit':
            continue
        if not any(key.startswith(pattern["id"]+"_") for key in present):
            continue
        units = sorted([i for i in data["occurrences"] if i["parent"] == pattern["id"]],key=lambda i:i["id"])
        endpoints = [(frame(i["frame"],data).multVec(App.Vector(-pitch/2,0,height)),
                      frame(i["frame"],data).multVec(App.Vector(pitch/2,0,height))) for i in units]
        lengths = [(b-a).Length for a,b in endpoints]
        gaps = [(a[1]-b[0]).Length for a,b in zip(endpoints,endpoints[1:]+endpoints[:1])]
        closed = pattern.get("mode") == "closed_track"
        if not closed:
            gaps = gaps[:-1]
        max_pitch = max(abs(x-pitch) for x in lengths)
        max_gap = max(gaps,default=0)
        passed = max_pitch<1e-6 and max_gap<1e-6
        checks.append({"pattern":pattern["id"],"units":len(units),"closed":closed,
                       "max_joint_pitch_error_mm":max_pitch,"max_adjacent_pin_gap_mm":max_gap,
                       "last_to_first_pin_gap_mm":gaps[-1] if closed else None,"passed":passed})
        if not passed:
            raise ValueError("Track lost printed pitch or shared-pin closure")
    return checks


def validate(data, items, out, bends=False):
    import Part
    from .cad_build import frame
    components = [i for i in items if i["representation"] == "assembly" and i["id"].startswith(("PortTrack_","StarboardTrack_"))]
    result = {"source_compositions":source_composition(data), "component_occurrences":len(components),
              "complete_track":False,"full_loop_and_articulation_verified":False}
    if not components:
        return result
    # Prove the other track is a rigid transverse translation before reusing
    # its identical interference result. Native datum checks remain independent.
    by_id = {i["id"]:i for i in components}
    port = [i for i in components if i["id"].startswith("PortTrack_")]
    import FreeCAD as App
    expected_delta = App.Vector(0,-data["values"]["track_centers"].value,0)
    for item in port:
        other = by_id[item["id"].replace("PortTrack_","StarboardTrack_",1)]
        a,b = item["shape"].Placement,other["shape"].Placement
        if item["definition"] != other["definition"] or (b.Base-a.Base-expected_delta).Length>1e-6 or a.Rotation.inverted().multiply(b.Rotation).Angle>1e-7:
            raise ValueError("Track-copy placement differs; cannot reuse interference checks")
    if len(port)*2 != len(components):
        raise ValueError("Unexpected physical components outside the paired track patterns")
    port_box,starboard_box = App.BoundBox(),App.BoundBox()
    for item in components:
        (port_box if item["id"].startswith("PortTrack_") else starboard_box).add(item["shape"].BoundBox)
    if port_box.intersect(starboard_box):
        raise ValueError("Paired track bounding boxes overlap; cross-track fit must be checked")
    result["opposite_track_rigid_translation_verified"] = True
    result["cross_track_boxes_disjoint"] = True
    candidates = sorted(port, key=lambda i:i["shape"].BoundBox.XMin)
    overlaps, tested = [], 0
    for index,a in enumerate(candidates):
        box = a["shape"].BoundBox
        for b in candidates[index+1:]:
            other = b["shape"].BoundBox
            if other.XMin > box.XMax:
                break
            if not box.intersect(other):
                continue
            unit_a = a["id"].split("_",2)[:2]
            unit_b = b["id"].split("_",2)[:2]
            if unit_a == unit_b and unit_a != ["PortTrack","Unit000"]:
                continue  # identical rigid source template, checked in Unit000
            # Touching planes are legitimate interfaces, not volumetric overlaps.
            if min(box.YMax,other.YMax)-max(box.YMin,other.YMin) < 1e-6 or min(box.ZMax,other.ZMax)-max(box.ZMin,other.ZMin) < 1e-6:
                continue
            tested += 1
            volume = a["shape"].common(b["shape"]).Volume
            if volume > 1e-3:
                overlaps.append({"a":a["id"],"b":b["id"],"volume_mm3":volume})
    shoes = [i for i in components if i["definition"] == "track_shoe"]
    result.update(exact_collision_pairs_tested=tested,overlaps=overlaps,
                  static_track_noninterference_passed=not overlaps,
                  repeated_unit_internal_fit="Unit000 checked; identical rigid templates reused",
                  shoe_nurbs_faces=sorted({sum(isinstance(f.Surface,Part.BSplineSurface) for f in i["shape"].Faces) for i in shoes}))
    if not result["shoe_nurbs_faces"] or min(result["shoe_nurbs_faces"]) < 2:
        raise ValueError("Pressed shoe lost its native NURBS top/bottom surfaces")
    result["pitch_checks"] = pitch_checks(data,items)
    units = sum(x["units"] for x in result["pitch_checks"])
    expected_units = data["configuration"]["decisions"]["P_2a3e041c45389451"]["installed_count"]
    expected_loops = data["configuration"]["decisions"]["P_1cd56f1415062c80"]["installed_count"]
    leaves_per_unit = next(x["leaf_total"] for x in result["source_compositions"] if x["template"] == "track_unit")
    if units != expected_units or len(result["pitch_checks"]) != expected_loops or len(components) != units*leaves_per_unit:
        raise ValueError("Installed track count differs from the selected production source quantities")
    result["production_quantity_check"] = {"loops":expected_loops,"shoe_units":units,
                                          "physical_leaves":len(components),"passed":True}
    from .track_path import solve
    solution = solve(data)
    write(out/"reports/track_path.json",solution)
    result["closed_component_loops"] = all(x["closed"] and x["passed"] for x in result["pitch_checks"])
    result["actual_route_bend_range_deg"] = [solution["min_bend_deg"],solution["max_bend_deg"]]
    if bends:
        result["sampled_bend_trials"] = bend_trials(data,components)
    write(out/"reports/track_components.json",result)
    if overlaps:
        raise ValueError("Track component material overlaps; see reports/track_components.json")
    return result
