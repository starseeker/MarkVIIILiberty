"""CAD build/export/validation worker; launched in a fresh compatible runtime."""
from collections import Counter
import copy
from pathlib import Path
import resource
import shutil
import sys

from . import runtime
from .evidence import read, write, fingerprint, verify_sources, sha
from .model import load


def same_shape(a, b):
    if a["solids"] != b["solids"]:
        return False
    if abs(a["volume_mm3"]-b["volume_mm3"]) > max(1e-5, abs(a["volume_mm3"])*1e-6):
        return False
    return all(abs(x-y)<=1e-5 for x,y in zip(a["bounds_mm"],b["bounds_mm"]))


def check_build(out):
    report = read(out / "reports/build.json")
    if report["fingerprint"] != fingerprint():
        raise ValueError("Authored data or code changed; rebuild before exporting/validating")
    for relative, digest in report["native_hashes"].items():
        path = out / relative
        if not path.is_file() or sha(path) != digest:
            raise ValueError("Missing or changed native file: " + relative)
    return report


def reopen_saved(doc):
    """Qualify the delivered native file, with fresh external dependencies."""
    import FreeCAD as App
    filename = doc.FileName
    for name in list(App.listDocuments()):
        App.closeDocument(name)
    restored = App.openDocument(filename)
    restored.recompute()
    return restored


def placement_errors(installed, expected):
    import FreeCAD as App
    axes = (App.Vector(1,0,0), App.Vector(0,1,0), App.Vector(0,0,1))
    return ((installed.Base-expected.Base).Length,
            max((installed.Rotation.multVec(v)-expected.Rotation.multVec(v)).Length for v in axes))


def coverage(data, items):
    definitions = {i["definition"] for i in items}
    finished = {i["definition"] for i in items if i["coverage"].startswith("finished")}
    return {"configuration": data["configuration"]["id"], "native_occurrences": len(items),
            "solid_occurrences": sum(bool(i["shape"].Solids) for i in items),
            "definitions_represented": len(definitions), "finished_definitions": len(finished),
            "representation_counts": dict(Counter(i["representation"] for i in items)),
            "subsystem_occurrences": dict(Counter(i["system"] for i in items)),
            "survey_identities_with_layout": sorted({pid for k in definitions if data["definitions"][k]["representation"] == "layout" for pid in data["definitions"][k]["survey_ids"]}),
            "survey_identities_with_components": sorted({pid for k in definitions if data["definitions"][k]["representation"] == "assembly" for pid in data["definitions"][k]["survey_ids"]}),
            "component_occurrences": sum(i["representation"] == "assembly" for i in items),
            "required_vehicle_occurrence_count": None, "complete": False,
            "unmodeled_layout_families": data["model"]["missing_layout_families"],
            "limitation": "Native layout solids are not finished component coverage. Inventory reconciliation and component work remain open."}


def exports(data, items, out):
    import FreeCAD as App
    import Part
    import Import
    from .cad_build import shape_signature
    folder = out / "exports"
    folder.mkdir(parents=True, exist_ok=True)
    reports = []
    for representation, suffix in [("layout", "Layout"), ("assembly", "Components")]:
        solids = [i for i in items if i["shape"].Solids and i["representation"] == representation]
        path = folder / ("MarkVIII_" + suffix + ".step")
        if not solids:
            path.unlink(missing_ok=True)
            continue
        export_doc = App.newDocument("Exchange" + suffix)
        root = export_doc.addObject("App::Part", "MarkVIII_" + suffix)
        groups = {}
        for item in solids:
            system = item["system"]
            if system not in groups:
                groups[system] = export_doc.addObject("App::Part", system)
                root.addObject(groups[system])
            obj = export_doc.addObject("PartDesign::Feature", item["id"])
            obj.Label = item["target"].Label
            obj.Shape = item["shape"]
            groups[system].addObject(obj)
        export_doc.recompute()
        Import.export([root], str(path))
        restored = Part.Shape()
        restored.read(str(path))
        expected = Part.makeCompound([i["shape"] for i in solids])
        good = restored.isValid() and same_shape(shape_signature(expected), shape_signature(restored))
        if not good:
            raise ValueError(suffix + " STEP round trip changed geometry")
        reports.append({"path": str(path.relative_to(out)), "solid_occurrences": len(solids),
                        "representation": representation, "roundtrip_passed": good})
        App.closeDocument(export_doc.Name)
    result = {"files": reports, "roundtrip_passed": all(x["roundtrip_passed"] for x in reports),
              "scope": "Separate provisional layout and reconstructed physical component exports; full tank incomplete.",
              "relative_volume_tolerance": 1e-6, "bounds_tolerance_mm": 1e-5}
    write(out / "reports/export.json", result)
    return result


def layout_interference(data, items):
    """Surface layout conflicts for review without pretending envelopes are parts."""
    contexts = {"central_hull", "track_frame", "main_enclosure", "driver_enclosure", "lookout", "sponson"}
    candidates = [i for i in items if i["representation"] == "layout" and i["shape"].Solids and i["definition"] not in contexts]
    overlaps = []
    for index, a in enumerate(candidates):
        for b in candidates[index+1:]:
            if not a["shape"].BoundBox.intersect(b["shape"].BoundBox):
                continue
            volume = a["shape"].common(b["shape"]).Volume
            if volume > 1e-4:
                overlaps.append({"a": a["id"], "b": b["id"], "volume_mm3": volume,
                                 "status": "unresolved_layout_overlap",
                                 "interpretation": "May indicate conflicting placement or overlapping package reservations. Resolve from component geometry and sources; not accepted as physical interference."})
    return {"overlaps": overlaps,
            "excluded_context_envelopes": [i["id"] for i in items if i["definition"] in contexts],
            "physical_fit_verified": False}


def validate(data, doc, out, build_report):
    import FreeCAD as App
    from .cad_build import frame, leaves, shape_signature
    items = leaves(doc.Root)
    nodes = {x["id"]: x for x in data["occurrences"]}
    selected = build_report["build"]["selected_subsystem"]
    def subsystem(item):
        return item["id"] if item["parent"] == "Root" else subsystem(nodes[item["parent"]])
    expected = {x["id"] for x in nodes.values() if x["definition"] and (not selected or subsystem(x) == selected)}
    actual = [i["id"] for i in items]
    if len(actual) != len(set(actual)) or set(actual) != expected:
        raise ValueError("Native occurrence coverage differs from the authored hierarchy")
    print("Validating native definitions and installed rigid placements", file=sys.stderr, flush=True)
    baseline, checked_definitions = {}, set()
    definition_signatures = {}
    max_translation_error = max_rotation_error = 0.0
    for item in items:
        target = item["target"]
        token = (target.Document.Name, target.Name)
        if token not in checked_definitions:
            if not target.Shape.isValid():
                raise ValueError("Invalid native definition: " + item["definition"])
            checked_definitions.add(token)
            definition_signatures[item['definition']] = shape_signature(target.Shape)
        # leaves() preserves the definition geometry and applies a rigid
        # placement. Validate that transform directly: OCC's optimal bounds
        # can vary by tens of nanometers for equivalent rotated curved faces.
        calculated = frame(nodes[item["id"]]["frame"], data).multiply(target.Shape.Placement)
        installed = item["shape"].Placement
        translation_error, rotation_error = placement_errors(installed, calculated)
        max_translation_error = max(max_translation_error, translation_error)
        max_rotation_error = max(max_rotation_error, rotation_error)
        # Reopened near-zero rotations show up to 1.8e-7 mm / 1.2e-9
        # basis-vector differences in this assembly. Preserve a small explicit
        # numerical allowance and report the actual maxima, not just a pass.
        if translation_error > 1e-6 or rotation_error > 1e-8:
            raise ValueError("Nested transform does not match the named datum: " + item["id"])
        signature = shape_signature(item["shape"])
        baseline[item["id"]] = signature
    report = {"occurrence_coverage": True, "native_shape_validity": True, "named_datum_placements": True,
              "solid_occurrences": sum(bool(i["shape"].Solids) for i in items),
              "wire_occurrences": sum(not bool(i["shape"].Solids) for i in items),
              "hierarchy_depth": "top assembly / subsystem / nested source assemblies / native part definition links",
              "layout_interference": layout_interference(data, items),
              "valid_native_definitions": len(checked_definitions),
              "rigid_placements_checked": len(items),
              "placement_tolerance_mm": 1e-6, "rotation_basis_tolerance": 1e-8,
              "max_translation_error_mm": max_translation_error, "max_rotation_basis_error": max_rotation_error,
              "complete_tank_verified": False}
    print("Validating track composition, closure and material contacts", file=sys.stderr, flush=True)
    from .track_validation import validate as validate_tracks
    report["track_components"] = validate_tracks(data, items, out, bends=True)
    from .upper_validation import validate as validate_upper
    report["upper_plates"] = validate_upper(data, items, out)
    from .hull_validation import validate as validate_hull
    report["hull_plates"] = validate_hull(data, items, out)
    from .sponson_validation import validate as validate_sponsons
    report["sponson_plates"] = validate_sponsons(data, items, out)
    from .louver_validation import validate as validate_louvers
    report["louvers"] = validate_louvers(data, items, out)
    from .roller_validation import validate as validate_rollers
    report['rollers'] = validate_rollers(data, items, out)
    from .lower_support_validation import validate as validate_lower_supports
    report['lower_supports'] = validate_lower_supports(data,items,out)
    from .wheel_validation import validate as validate_wheels
    report['idler_wheels'] = validate_wheels(data,items,out)
    print("Exporting and reopening layout/component STEP files", file=sys.stderr, flush=True)
    report["step"] = exports(data, items, out)
    print("Validating relocated native dependencies", file=sys.stderr, flush=True)
    native = out / "native"
    relocated = out / "verification/relocated_native"
    if relocated.exists():
        shutil.rmtree(relocated)
    shutil.copytree(native, relocated)
    top_name = Path(doc.FileName).name
    for name in list(App.listDocuments()):
        App.closeDocument(name)
    copied = App.openDocument(str(relocated / top_name))
    copied.recompute()
    moved = leaves(copied.Root)
    if {i["id"] for i in moved} != set(baseline):
        raise ValueError("Relocated assembly lost occurrence coverage")
    for item in moved:
        if not same_shape(baseline[item["id"]], shape_signature(item["shape"])):
            raise ValueError("Relocation changed installed shape")
        if relocated.resolve() not in Path(item["target"].Document.FileName).resolve().parents:
            raise ValueError("Relocation silently resolved a source outside the copied native directory")
    report["relocated_native_links"] = True
    # Qualify the implementation with an independent rebuild and a meaningful
    # installation change before relying on thousands of repeated instances.
    from .cad_build import build
    from .parameters import resolve
    print("Validating independent rebuild and unchanged cache reuse", file=sys.stderr, flush=True)
    rebuild_folder = out/"verification/rebuild"
    if rebuild_folder.exists():
        shutil.rmtree(rebuild_folder)
    rebuilt, rebuild_stats = build(data, rebuild_folder, selected)
    if any(v["cache_reused"] for v in rebuild_stats["subsystems"].values()):
        raise ValueError("Independent rebuild unexpectedly reused a native definition cache")
    rebuilt = reopen_saved(rebuilt)
    regenerated = {i["id"]: shape_signature(i["shape"]) for i in leaves(rebuilt.Root)}
    if set(regenerated) != set(baseline) or not all(same_shape(baseline[k], regenerated[k]) for k in baseline):
        raise ValueError("Independent rebuild changed nominal installed geometry")
    report["equivalent_independent_rebuild"] = True
    cached, cache_stats = build(data, out/"verification/rebuild", selected)
    if not all(v["cache_reused"] for v in cache_stats["subsystems"].values()):
        raise ValueError("Unchanged native definition cache was not reused")
    cached = reopen_saved(cached)
    cached_signature = {i["id"]: shape_signature(i["shape"]) for i in leaves(cached.Root)}
    if not all(same_shape(baseline[k], cached_signature[k]) for k in baseline):
        raise ValueError("Cache reuse changed installed geometry")
    report["unchanged_definition_cache"] = True
    report["rebuild_seconds"] = rebuild_stats["seconds"]
    report["cached_build_seconds"] = cache_stats["seconds"]
    if any(i["representation"] == "assembly" and i["definition"].startswith("track_") for i in items):
        print("Validating closed-track pitch propagation", file=sys.stderr, flush=True)
        changed = copy.deepcopy(data)
        delta = 0.5
        changed["parameters"]["shoe_pitch"]["value"] += delta
        changed["values"] = resolve(changed["parameters"])
        variant, _ = build(changed, out/"verification/track_pitch_change", selected)
        variant = reopen_saved(variant)
        variant_items = leaves(variant.Root)
        altered = {i["id"]: shape_signature(i["shape"]) for i in variant_items}
        if set(altered) != set(baseline):
            raise ValueError("Pitch change altered native occurrence coverage")
        max_translation = max_rotation = 0.0
        for item in variant_items:
            expected = frame(nodes[item["id"]]["frame"], changed).multiply(item["target"].Shape.Placement)
            translation, rotation = placement_errors(item["shape"].Placement, expected)
            max_translation, max_rotation = max(max_translation,translation), max(max_rotation,rotation)
            if translation > 1e-6 or rotation > 1e-8:
                raise ValueError("Pitch change did not update the installed native placement: " + item["id"])
        for key,signature in baseline.items():
            definition = nodes[key]["definition"]
            if definition.startswith("track_") and "Track_Unit" in key:
                if definition in {"track_shoe","track_link_left","track_link_right"} and abs(signature["volume_mm3"]-altered[key]["volume_mm3"])<1:
                    raise ValueError("Track part did not rebuild for the pitch perturbation: " + key)
            elif definition.startswith(('roller_','wheel_','idler_')):
                if abs(signature['volume_mm3']-altered[key]['volume_mm3'])>1e-4:
                    raise ValueError('Track pitch changed a fixed-size running gear component: '+key)
                if 'Idler_Unit000_Supports_' in key and not same_shape(signature,altered[key]):
                    raise ValueError('Track pitch moved a fixed idler bracket or mounting part: '+key)
            elif definition.startswith('hull_'):
                # Shaft bores and upper roof reliefs follow the roller stations.
                pass
            elif definition.startswith('lower_support_'):
                # Reconstructed contours and hole datums follow installed pins;
                # printed stock lengths and counts are checked independently.
                pass
            elif not same_shape(signature,altered[key]):
                raise ValueError("Track pitch change modified unrelated geometry: " + key)
        from .track_validation import pitch_checks
        from .track_path import solve
        checks = pitch_checks(changed,variant_items)
        old_path,new_path = solve(data),solve(changed)
        if abs(old_path["source_curve_scale"]-new_path["source_curve_scale"])<1e-6:
            raise ValueError("Closed route did not respond to altered pitch")
        pitch_hull_checks = validate_hull(changed,variant_items,out/"verification/track_pitch_change")
        pitch_sponson_checks = validate_sponsons(changed,variant_items,out/"verification/track_pitch_change")
        pitch_louver_checks = validate_louvers(changed,variant_items,out/"verification/track_pitch_change")
        pitch_roller_checks = validate_rollers(changed,variant_items,out/'verification/track_pitch_change')
        pitch_support_checks = validate_lower_supports(changed,variant_items,out/'verification/track_pitch_change')
        pitch_wheel_checks = validate_wheels(changed,variant_items,out/'verification/track_pitch_change')
        report["track_pitch_change"] = {"delta_mm":delta,"parts_and_nested_occurrences_updated":True,
                                        "unrelated_geometry_unchanged":True,"closed_loop_checks":checks,
                                        "reopened_native_placements_checked":len(variant_items),
                                        "max_translation_error_mm":max_translation,
                                        "max_rotation_basis_error":max_rotation,
                                        "perturbed_fit_qualified":False,"hull_contacts":pitch_hull_checks,
                                        "sponson_contacts":pitch_sponson_checks,"louver_contacts":pitch_louver_checks,
                                        "dependent_roller_and_hull_opening_checks":pitch_roller_checks,
                                        "dependent_lower_support_checks":pitch_support_checks,
                                        "dependent_idler_checks":pitch_wheel_checks}
    if any(i["definition"].startswith("upper_") for i in items):
        print("Validating upper-enclosure width propagation", file=sys.stderr, flush=True)
        changed = copy.deepcopy(data)
        changed["parameters"]["main_turret_width"]["value"] += 10
        changed["values"] = resolve(changed["parameters"])
        variant, _ = build(changed, out/"verification/upper_width_change", "HullStructure")
        variant = reopen_saved(variant)
        altered_items = leaves(variant.Root)
        variant_checks = validate_upper(changed, altered_items, out/"verification/upper_width_change")
        hull_variant_checks = validate_hull(changed, altered_items, out/"verification/upper_width_change")
        altered = {i["id"]: shape_signature(i["shape"]) for i in altered_items}
        for side,delta in [("port",5),("starboard",-5)]:
            key = "upper_"+side+"_main_flap"
            wanted = copy.deepcopy(baseline[key])
            wanted["bounds_mm"][1] += delta
            wanted["bounds_mm"][4] += delta
            if not same_shape(wanted,altered[key]):
                raise ValueError("Main width did not move the closed flap correctly: " + key)
        unchanged = [k for k in altered if "lookout" in k or "driver" in k or k == "central_hull"]
        if not all(same_shape(baseline[k],altered[k]) for k in unchanged):
            raise ValueError("Main width changed the independent lookout/driver geometry")
        for side in ["port","starboard"]:
            key = "upper_"+side+"_main_roof"
            if altered[key]["volume_mm3"] <= baseline[key]["volume_mm3"]:
                raise ValueError("Main roof did not widen with the enclosure")
        report["upper_width_change"] = {"delta_mm":10,"opposed_flaps_shifted_mm":5,
            "roof_halves_widened":True,"independent_enclosures_unchanged":True,
            "reopened_plate_checks":variant_checks,"hull_interfaces":hull_variant_checks,"historical_fit_qualified":False}
    if any(i["definition"].startswith("hull_") for i in items):
        print("Validating lower-shell spacing propagation", file=sys.stderr, flush=True)
        changed = copy.deepcopy(data)
        changed["parameters"]["hull_frame_clear"]["value"] += 10
        # Artificial qualification input, not a revision to the printed dimension.
        changed["parameters"]["hull_frame_clear"]["bounds"][1] += 10
        changed["values"] = resolve(changed["parameters"])
        variant,_ = build(changed,out/"verification/hull_gap_change","HullStructure")
        variant = reopen_saved(variant)
        altered_items = leaves(variant.Root)
        checks = validate_hull(changed,altered_items,out/"verification/hull_gap_change")
        altered = {i["id"]:shape_signature(i["shape"]) for i in altered_items}
        for side,hand in [("port",1),("starboard",-1)]:
            for layer,sign in [("inner",-1),("outer",1)]:
                key = "hull_"+side+"_"+layer+"_skirt_front"
                wanted = copy.deepcopy(baseline[key]);delta=hand*sign*5
                wanted["bounds_mm"][1] += delta;wanted["bounds_mm"][4] += delta
                if not same_shape(wanted,altered[key]):
                    raise ValueError("Lower shell face did not follow spacing change: "+key)
        if not altered["hull_floor_4"]["volume_mm3"] > baseline["hull_floor_4"]["volume_mm3"]:
            raise ValueError("Broad floor did not widen with shell gap")
        if not altered["hull_floor_1"]["volume_mm3"] < baseline["hull_floor_1"]["volume_mm3"]:
            raise ValueError("Front floor did not narrow with shell gap")
        if not all(same_shape(baseline[k],altered[k]) for k in altered if k.startswith("upper_")):
            raise ValueError("Shell spacing changed independent upper enclosures")
        report["hull_spacing_change"] = {"delta_mm":10,"face_shifts_verified_mm":5,
            "broad_floor_widened":True,"front_floor_narrowed":True,"upper_enclosures_unchanged":True,
            "reopened_hull_checks":checks,"test_bound_override":True,"historical_fit_qualified":False}
    if any(i["definition"].startswith("sponson_") for i in items):
        print("Validating sponson roof-thickness propagation", file=sys.stderr, flush=True)
        changed=copy.deepcopy(data)
        changed["parameters"]["sponson_plate_roof"]["value"] += 1
        changed["values"]=resolve(changed["parameters"])
        variant,_=build(changed,out/"verification/sponson_roof_change","Sponsons")
        variant=reopen_saved(variant);altered_items=leaves(variant.Root)
        checks=validate_sponsons(changed,altered_items,out/"verification/sponson_roof_change")
        altered={i['id']:shape_signature(i['shape']) for i in altered_items}
        for side in ['port','starboard']:
            key='sponson_'+side+'_roof';old=baseline[key];new=altered[key]
            if abs(new['bounds_mm'][5]-old['bounds_mm'][5])>1e-6 or abs(new['bounds_mm'][2]-old['bounds_mm'][2]+1)>1e-6 or new['volume_mm3']<=old['volume_mm3']:
                raise ValueError('Sponson roof did not thicken inward with fixed crown')
            if altered['sponson_'+side+'_side']['volume_mm3']>=baseline['sponson_'+side+'_side']['volume_mm3']:
                raise ValueError('Sponson side did not shorten below thicker roof')
            for role in ['floor','sloping_bottom','sloping_side']:
                key='sponson_'+side+'_'+role
                if not same_shape(baseline[key],altered[key]):raise ValueError('Sponson roof change altered independent floors')
        report['sponson_roof_change']={'delta_mm':1,'fixed_crown':True,'roof_inward_thickening':True,
            'side_height_updated':True,'floors_unchanged':True,'reopened_plate_checks':checks,'historical_fit_qualified':False}
    if any(i['definition'].startswith('roller_') for i in items):
        print('Validating roller diameter and installed station propagation', file=sys.stderr, flush=True)
        changed=copy.deepcopy(data)
        changed['parameters']['roller_diameter']['value'] += 1
        changed['values']=resolve(changed['parameters'])
        variant,_=build(changed,out/'verification/roller_diameter_change',selected)
        variant=reopen_saved(variant)
        altered_items=leaves(variant.Root)
        checks=validate_rollers(changed,altered_items,out/'verification/roller_diameter_change')
        support_checks=validate_lower_supports(changed,altered_items,out/'verification/roller_diameter_change')
        altered={i['id']:shape_signature(i['shape']) for i in altered_items}
        for item in altered_items:
            key=item['id'];definition=item['definition']
            if definition in {'roller_lower','roller_upper'}:
                if altered[key]['volume_mm3']<=baseline[key]['volume_mm3']:
                    raise ValueError('Roller diameter failed to increase native wheel material')
            elif not definition.startswith(('roller_','hull_','lower_support_')) and not same_shape(baseline[key],altered[key]):
                raise ValueError('Roller diameter changed unrelated geometry: '+key)
        from .roller_geometry import stations
        shifts=[b['z']-a['z'] for a,b in zip(stations(data),stations(changed))]
        if any(abs(x)<.49 for x in shifts):raise ValueError('Roller diameter did not move every rail-facing station')
        report['roller_diameter_change']={'delta_mm':1,'wheel_material_increased':True,
            'source_x_retained':all(a['x']==b['x'] for a,b in zip(stations(data),stations(changed))),
            'station_z_shifts_mm':shifts,'reopened_contacts':checks,'lower_support_contacts':support_checks,'historical_fit_qualified':False}
    if any(i['definition']=='wheel_rim' for i in items):
        print('Validating idler diameter and station with fixed common wheel geometry',file=sys.stderr,flush=True)
        changed=copy.deepcopy(data)
        changed['parameters']['idler_diameter']['value']+=1
        changed['values']=resolve(changed['parameters'])
        variant,_=build(changed,out/'verification/idler_diameter_change',selected)
        variant=reopen_saved(variant);altered_items=leaves(variant.Root)
        checks=validate_wheels(changed,altered_items,out/'verification/idler_diameter_change')
        altered={i['id']:shape_signature(i['shape']) for i in altered_items}
        for item in altered_items:
            key=item['id'];definition=item['definition']
            if definition == 'wheel_rim':
                if altered[key]['volume_mm3']<=baseline[key]['volume_mm3']:
                    raise ValueError('Idler diameter did not increase rim material')
            elif 'Idler_' in key:
                if abs(altered[key]['volume_mm3']-baseline[key]['volume_mm3'])>1e-4:
                    raise ValueError('Idler diameter changed unrelated wheel/shaft stock')
                if '_Supports_' in key and not same_shape(baseline[key],altered[key]):
                    raise ValueError('Idler diameter moved fixed supports')
            elif not same_shape(baseline[key],altered[key]):
                raise ValueError('Idler diameter changed unrelated installed geometry: '+key)
        for item in altered_items:
            if item['definition'].startswith('wheel_') and item['definition']!='wheel_rim':
                if not same_shape(definition_signatures[item['definition']],shape_signature(item['target'].Shape)):
                    raise ValueError('Idler diameter resized a source-common wheel definition')
        from .wheel_geometry import station
        if abs(station(changed)['x']-station(data)['x'])<.1:
            raise ValueError('Idler adjustment did not follow altered diameter')
        report['idler_diameter_change']={'delta_mm':1,'idler_rim_updated':True,
            'common_disk_and_rivet_pattern_unchanged':True,'drive_installations_unchanged':True,
            'static_station_updated':True,'unrelated_geometry_unchanged':True,
            'reopened_contacts':checks,'historical_fit_qualified':False}
    if any(i['definition']=='drive_rim' for i in items):
        for parameter,delta,affected,trial in [
            ('wheel_disk_radius',.5,'wheel_disk','common_wheel_disk_change'),
            ('drive_teeth',2,'drive_rim','drive_tooth_count_change')]:
            print('Validating '+trial+' and source-common installed interfaces',file=sys.stderr,flush=True)
            changed=copy.deepcopy(data)
            changed['parameters'][parameter]['value']+=delta
            changed['values']=resolve(changed['parameters'])
            variant,_=build(changed,out/'verification'/trial,selected)
            variant=reopen_saved(variant);altered_items=leaves(variant.Root)
            checks=validate_wheels(changed,altered_items,out/'verification'/trial)
            affected_ids=[]
            for item in altered_items:
                key=item['id'];signature=shape_signature(item['shape'])
                if item['definition']==affected:
                    if abs(signature['volume_mm3']-baseline[key]['volume_mm3'])<1e-3:
                        raise ValueError('Wheel parameter failed to change native material: '+key)
                    if parameter=='wheel_disk_radius' and signature['volume_mm3']<=baseline[key]['volume_mm3']:
                        raise ValueError('Larger common disk radius did not increase material')
                    affected_ids.append(key)
                elif not same_shape(baseline[key],signature):
                    raise ValueError('Wheel parameter changed unrelated installed geometry: '+key)
            wanted=8 if parameter=='wheel_disk_radius' else 4
            if len(affected_ids)!=wanted:raise ValueError('Wheel propagation missed installed copies')
            report[trial]={'parameter':parameter,'delta':delta,'affected_occurrences':affected_ids,
                'unrelated_geometry_unchanged':True,'reopened_contacts':checks,'historical_fit_qualified':False}
    if any(i['definition']=='idler_shaft' for i in items):
        print('Validating idler shaft length, end plugs and locking screw propagation',file=sys.stderr,flush=True)
        changed=copy.deepcopy(data)
        changed['parameters']['idler_shaft_length']['value']+=2
        changed['values']=resolve(changed['parameters'])
        variant,_=build(changed,out/'verification/idler_shaft_length_change',selected)
        variant=reopen_saved(variant);altered_items=leaves(variant.Root)
        checks=validate_wheels(changed,altered_items,out/'verification/idler_shaft_length_change')
        altered={i['id']:shape_signature(i['shape']) for i in altered_items}
        for item in altered_items:
            key=item['id'];definition=item['definition']
            if definition in {'idler_shaft','idler_locking_screw'}:
                if altered[key]['volume_mm3']<=baseline[key]['volume_mm3']:
                    raise ValueError('Shaft extension did not lengthen shaft/locking screw')
            elif '_ShaftAssembly_OilPlug' in key:
                wanted=copy.deepcopy(baseline[key]);delta=-1 if key.endswith('A') else 1
                wanted['bounds_mm'][1]+=delta;wanted['bounds_mm'][4]+=delta
                if not same_shape(wanted,altered[key]):raise ValueError('Idler oil plug failed to follow shaft end')
            elif not same_shape(baseline[key],altered[key]):
                raise ValueError('Shaft length changed independent geometry: '+key)
        report['idler_shaft_length_change']={'delta_mm':2,'shaft_and_locking_screws_lengthened':True,
            'oil_plugs_follow_ends':True,'fixed_supports_and_other_components_unchanged':True,
            'reopened_contacts':checks,'historical_fit_qualified':False}
    if any(i['definition']=='roller_upper_support' for i in items):
        print('Validating upper roller support stock and bearing faces', file=sys.stderr, flush=True)
        changed=copy.deepcopy(data)
        changed['parameters']['roller_support_thickness']['value'] += .5
        changed['values']=resolve(changed['parameters'])
        variant,_=build(changed,out/'verification/roller_support_stock_change',selected)
        variant=reopen_saved(variant);altered_items=leaves(variant.Root)
        checks=validate_rollers(changed,altered_items,out/'verification/roller_support_stock_change')
        altered={i['id']:shape_signature(i['shape']) for i in altered_items}
        for item in altered_items:
            key=item['id']
            if item['definition']=='roller_upper_support':
                if altered[key]['volume_mm3']<=baseline[key]['volume_mm3']:
                    raise ValueError('Upper angle stock did not increase native material')
                if any(abs(a-b)>1e-6 for a,b in zip(altered[key]['bounds_mm'],baseline[key]['bounds_mm'])):
                    raise ValueError('Upper angle stock changed the fixed outside envelope')
            elif not same_shape(baseline[key],altered[key]):
                raise ValueError('Upper angle stock changed unrelated geometry: '+key)
        report['roller_support_stock_change']={'delta_mm':.5,'fixed_outside_envelope':True,
            'material_increased':True,'unrelated_geometry_unchanged':True,
            'reopened_contacts':checks,'historical_fit_qualified':False}
    if any(i['definition'].startswith('lower_support_') for i in items):
        print('Validating lower support stock, bolt seats and owned hull holes',file=sys.stderr,flush=True)
        changed=copy.deepcopy(data)
        changed['parameters']['lower_support_thickness']['value']+=.5
        changed['values']=resolve(changed['parameters'])
        variant,_=build(changed,out/'verification/lower_support_stock_change',selected)
        variant=reopen_saved(variant);altered_items=leaves(variant.Root)
        checks=validate_lower_supports(changed,altered_items,out/'verification/lower_support_stock_change')
        roller_checks=validate_rollers(changed,altered_items,out/'verification/lower_support_stock_change')
        altered={i['id']:shape_signature(i['shape']) for i in altered_items}
        for item in altered_items:
            key=item['id'];definition=item['definition']
            if definition.startswith('lower_support_') and definition!='lower_support_attachment_bolt':
                if altered[key]['volume_mm3']<=baseline[key]['volume_mm3']:
                    raise ValueError('Lower support stock did not increase native material')
                if any(abs(a-b)>1e-6 for a,b in zip(altered[key]['bounds_mm'],baseline[key]['bounds_mm'])):
                    raise ValueError('Lower support stock changed fixed outside envelope')
            elif definition=='lower_support_attachment_bolt':
                if abs(altered[key]['volume_mm3']-baseline[key]['volume_mm3'])>1e-4:
                    raise ValueError('Lower support stock changed printed bolt stock')
                if same_shape(altered[key],baseline[key]):
                    raise ValueError('Bolt failed to follow thicker lower support')
            elif not definition.startswith('hull_') and not same_shape(altered[key],baseline[key]):
                raise ValueError('Lower support stock changed independent geometry: '+key)
        report['lower_support_stock_change']={'delta_mm':.5,'fixed_outside_envelope':True,
            'material_increased':True,'bolt_seats_and_hull_holes_follow_stock':True,
            'printed_bolt_stock_unchanged':True,'independent_geometry_unchanged':True,
            'reopened_contacts':checks,'roller_checks':roller_checks,'historical_fit_qualified':False}
    if any(i['definition'].startswith('louver_') for i in items):
        print('Validating louver blade-thickness propagation', file=sys.stderr, flush=True)
        changed=copy.deepcopy(data)
        changed['parameters']['louver_blade_thickness']['value'] += .5
        changed['values']=resolve(changed['parameters'])
        variant,_=build(changed,out/'verification/louver_thickness_change','CoolingVentilation')
        variant=reopen_saved(variant);altered_items=leaves(variant.Root)
        checks=validate_louvers(changed,altered_items,out/'verification/louver_thickness_change')
        altered={i['id']:shape_signature(i['shape']) for i in altered_items}
        for item in altered_items:
            key=item['id']
            if item['definition'] in {'louver_inlet_blade','louver_outlet_blade'}:
                if altered[key]['volume_mm3']<=baseline[key]['volume_mm3']:
                    raise ValueError('Louver blade stock did not grow')
            elif not same_shape(baseline[key],altered[key]):
                raise ValueError('Louver blade thickness changed unrelated geometry: '+key)
        report['louver_thickness_change']={'delta_mm':.5,'blade_stock_increased':True,
            'fixed_inside_radius_and_outside_width':True,'unrelated_components_unchanged':True,
            'reopened_louver_checks':checks,'historical_fit_qualified':False}
    if not selected or selected == "FuelPressure":
        print("Validating fuel-spacing propagation", file=sys.stderr, flush=True)
        changed = copy.deepcopy(data)
        changed["parameters"]["layout_fuel_spacing"]["value"] += 10
        changed["values"] = resolve(changed["parameters"])
        variant, _ = build(changed, out/"verification/fuel_spacing_change", selected)
        variant = reopen_saved(variant)
        altered = {i["id"]: shape_signature(i["shape"]) for i in leaves(variant.Root)}
        for key, signature in baseline.items():
            wanted = copy.deepcopy(signature)
            delta = 10 if key == "fuel_tank_port" else -10 if key == "fuel_tank_starboard" else 0
            wanted["bounds_mm"][1] += delta
            wanted["bounds_mm"][4] += delta
            if not same_shape(wanted, altered[key]):
                raise ValueError("Fuel installation change failed to propagate correctly: " + key)
        report["fuel_spacing_change"] = {"delta_mm": 10, "port_and_starboard_updated": True,
                                          "center_and_unrelated_occurrences_unchanged": True}
    report["source_lock"] = verify_sources(data["model"]["source_locks"])
    report["implemented_checks_passed"] = True
    report["rebuild_and_perturbation_checks_use_reopened_native_files"] = True
    report["remaining_release_checks"] = ["Complete physical component coverage", "Physical interference and interface fits",
                                          "Track wheel engagement and support contacts", "Pose clearances", "Final configuration/loadout reconciliation",
                                          "Qualification of later detailed geometry and full-tank performance"]
    write(out / "reports/validation.json", report)
    return report


def delivery(data, out):
    report = read(out / "reports/coverage.json")
    native = read(out / "reports/build.json")["build"]["top_document"]
    lines = ["# Mark VIII — reconstruction in progress", "",
             "This is an intermediate native assembly, not the complete tank model.", "",
             f"Open native/{Path(native).name} and keep the complete native directory together.",
             "The top-level document links subsystem files, which link reusable native definitions.", "",
             "![Installed layout](previews/isometric.png)", "",
             "[Interactive source comparisons](comparisons/index.html) · [Inventory](inventory/index.html)", "",
             f"{report['definitions_represented']} represented definitions; {report['native_occurrences']} installed occurrences.",
             f"Finished component definitions: {report['finished_definitions']}. Full-tank coverage remains incomplete.", "",
             "Layout and physical component STEP exports are separate; component coverage/approximations remain explicit.",
             "See reports for the source lock, runtime, native/STEP checks and unresolved coverage.", ""]
    (out / "README.md").write_text("\n".join(lines))
    paths = []
    for directory in ["native", "exports", "previews", "comparisons", "reports", "inventory"]:
        if (out / directory).exists():
            paths.extend(p for p in (out / directory).rglob("*") if p.is_file())
    paths.append(out / "README.md")
    write(out / "delivery_manifest.json", {"configuration": data["configuration"]["id"], "complete_tank": False,
          "files": {str(p.relative_to(out)): {"sha256": sha(p), "bytes": p.stat().st_size} for p in sorted(paths)}})


def run(command, out, selected=None):
    data = load()
    source_report = verify_sources(data["model"]["source_locks"])
    App, Gui = runtime.start_gui()
    import Part
    from .cad_build import build, leaves, shape_signature
    from .visual_review import run as review
    environment = {"FreeCAD": App.Version(), "OpenCASCADE": Part.OCC_VERSION, "source_lock": source_report}
    if command == "check":
        write(out / "reports/environment.json", environment)
        return environment
    if command == "build":
        for relative in ["reports/build.json", "reports/validation.json", "reports/export.json", "delivery_manifest.json",
                         "exports/MarkVIII_Layout.step", "exports/MarkVIII_Components.step"]:
            (out / relative).unlink(missing_ok=True)
        doc, build_stats = build(data, out, selected)
        items = leaves(doc.Root)
        from .track_validation import validate as validate_tracks
        validate_tracks(data, items, out)
        from .upper_validation import validate as validate_upper
        validate_upper(data, items, out)
        from .hull_validation import validate as validate_hull
        validate_hull(data, items, out)
        from .sponson_validation import validate as validate_sponsons
        validate_sponsons(data, items, out)
        from .louver_validation import validate as validate_louvers
        validate_louvers(data, items, out)
        from .roller_validation import validate as validate_rollers
        validate_rollers(data, items, out)
        from .lower_support_validation import validate as validate_lower_supports
        validate_lower_supports(data,items,out)
        from .wheel_validation import validate as validate_wheels
        validate_wheels(data,items,out)
        report = {"fingerprint": fingerprint(), "build": build_stats, "environment": environment,
                  "native_hashes": {str(p.relative_to(out)): sha(p) for p in sorted((out/"native").rglob("*.FCStd"))},
                  "geometry": {i["id"]: shape_signature(i["shape"]) for i in items},
                  "peak_memory_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024}
        write(out / "reports/build.json", report)
        write(out / "reports/coverage.json", coverage(data, items))
        write(out / "reports/environment.json", environment)
        from .inventory import build as inventory_build
        inventory_build(out, data, items)
        review(data, items, out)
        result = build_stats
    else:
        report = check_build(out)
        doc = App.openDocument(report["build"]["top_document"])
        doc.recompute()
        items = leaves(doc.Root)
        if command == "validate":
            result = validate(data, doc, out, report)
        elif command == "export":
            result = exports(data, items, out)
        elif command == "review":
            result = review(data, items, out)
        else:
            raise ValueError("Unknown worker command: " + command)
    delivery(data, out)
    return result
