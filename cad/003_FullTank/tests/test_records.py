"""Evidence/units invariants that prevent plausible-looking invalid CAD inputs."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.parameters import resolve, scalar
from lib.model import load, datum_values, point


def parameter(unit, value=None, expression=None):
    result = {"unit": unit, "bounds": [-10000,10000]}
    result["expression" if expression is not None else "value"] = expression if expression is not None else value
    return result


class RecordChecks(unittest.TestCase):
    def test_pinion_source_counts_and_shared_vehicle_quantities(self):
        from types import SimpleNamespace
        from lib.pinion_validation import composition
        data=load();selected=[];targets={}
        for occurrence in data['occurrences']:
            definition=occurrence['definition']
            if not definition:continue
            targets.setdefault(definition,SimpleNamespace(Name=definition,Document=SimpleNamespace(FileName='one_library')))
            selected.append(dict(occurrence,target=targets[definition]))
        report=composition(data,selected)
        self.assertEqual([r['physical_occurrences'] for r in report['assemblies']],[98,98])
        self.assertEqual({r['definition']:r['physical_occurrences'] for r in report['shared_vehicle_counts']},
                         {'wheel_bush':12,'drive_outer_bearing':4,'drive_backing_plate':4,
                          'drive_bearing_screw':24,'pinion_inner_rivet':12})
        selected.remove(next(i for i in selected if i['id']=='PortPinion_Rotor_PinAssemblyA0_Cotter'))
        with self.assertRaisesRegex(ValueError,'Pinion source composition mismatch'):
            composition(data,selected)

    def test_pinion_identity_rejects_a_same_size_drive_shaft_substitution(self):
        from lib.pinion_validation import composition
        data=load()
        data['definitions']['pinion_shaft']['survey_ids']=data['definitions']['drive_shaft']['survey_ids']
        with self.assertRaisesRegex(ValueError,'Pinion source identity mismatch: pinion_shaft'):
            composition(data,[])

    def test_drive_wheel_counts_and_complete_source_shaft(self):
        from lib.wheel_validation import composition
        data=load();selected=[i for i in data['occurrences'] if i['definition'] and
                              i['id'].startswith(('PortIdler_','StarboardIdler_','PortDrive_','StarboardDrive_'))]
        report=composition(data,selected)
        self.assertEqual(sum(r['modeled_leaves'] for r in report['installed']),604)
        self.assertEqual(len(report['whole_vehicle_wheel_totals']),5)
        shaft=next(r for r in report['assemblies'] if r['template']=='drive_shaft')
        self.assertTrue(shaft['complete']);self.assertEqual(shaft['leaf_total'],7)
        data['assemblies']['drive_shaft']['children'].remove(next(c for c in data['assemblies']['drive_shaft']['children'] if c['id']=='NutInner'))
        with self.assertRaisesRegex(ValueError,'Source composition mismatch for drive_shaft'):
            composition(data,selected)

    def test_drive_receiver_identity_cannot_be_replaced_by_adjacent_plate(self):
        from lib.drive_mount_validation import composition
        data=load();selected=[i for i in data['occurrences'] if i['definition']]
        composition(data,selected)
        data['definitions']['hull_port_inner_fuel_side']['survey_ids']=data['definitions']['hull_port_inner_rear_end']['survey_ids']
        with self.assertRaisesRegex(ValueError,'receiver identity conflicts with source'):
            composition(data,selected)

    def test_drive_shaft_length_updates_end_fittings_with_fixed_hull_faces(self):
        from lib.drive_mount_geometry import values
        data=load();before=values(data)
        outer=datum_values('PortDrive_Unit000_ShaftAssembly_NutOuter',data)
        inner=datum_values('PortDrive_Unit000_ShaftAssembly_NutInner',data)
        data['parameters']['drive_mount_shaft_length']['value']+=2
        data['values']=resolve(data['parameters']);after=values(data)
        self.assertEqual(after['outside'],before['outside'])
        self.assertEqual(after['shoulder'],before['shoulder'])
        self.assertAlmostEqual(after['key_end']-before['key_end'],1)
        self.assertAlmostEqual(after['flange_stock']-before['flange_stock'],1)
        self.assertAlmostEqual(datum_values('PortDrive_Unit000_ShaftAssembly_NutOuter',data)['translation'][1]-outer['translation'][1],1)
        self.assertAlmostEqual(datum_values('PortDrive_Unit000_ShaftAssembly_NutInner',data)['translation'][1]-inner['translation'][1],-1)

    def test_common_rivet_pattern_and_drive_axis_independent_of_idler_tip(self):
        from lib.wheel_geometry import values,rivets
        data=load();pattern=rivets(values(data));axis=datum_values('port_drive',data)
        radius=data['values']['wheel_disk_radius'].value
        data['parameters']['idler_diameter']['value']+=1;data['values']=resolve(data['parameters'])
        self.assertEqual(pattern,rivets(values(data)))
        self.assertEqual(axis,datum_values('port_drive',data))
        self.assertEqual(radius,data['values']['wheel_disk_radius'].value)

    def test_drive_source_mapping_rejects_an_idler_rim_substitution(self):
        from lib.track_validation import source_composition
        data=load()
        rim=next(c for c in data['assemblies']['drive_wheel']['children'] if c.get('definition')=='drive_rim')
        rim['definition']='wheel_rim'
        with self.assertRaisesRegex(ValueError,'Source composition mismatch for drive_wheel'):
            source_composition(data)

    def test_lower_support_bolt_totals_cannot_hide_a_wrong_run_allocation(self):
        from lib.lower_support_validation import composition
        data=load()
        selected=copy.deepcopy([i for i in data['occurrences']
                                if (i['definition'] or '').startswith('lower_support_')])
        # Retain every source identity and the total of 76 bolts, but move one
        # bolt from the first angle to the second. SNL31 allocates one to each.
        bolt=next(i for i in selected if i['id']=='PortLowerSupports_Outer_Run01_Bolt00')
        bolt['id']='PortLowerSupports_Outer_Run02_Bolt01'
        with self.assertRaisesRegex(ValueError,'Lower support bolt allocation'):
            composition(data,selected)

    def test_lower_support_counts_reject_missing_shared_mark_variant(self):
        from lib.lower_support_validation import composition
        data=load();selected=[i for i in data['occurrences'] if (i['definition'] or '').startswith('lower_support_')]
        counts=composition(data,selected)
        self.assertEqual(sum(r['actual'] for r in counts),110)
        self.assertEqual(next(r['actual'] for r in counts if r['mark']=='M2085'),4)
        selected.remove(next(i for i in selected if i['id']=='PortLowerSupports_Inner_Run08_Angle'))
        with self.assertRaisesRegex(ValueError,'source quantity changed: M2085'):composition(data,selected)

    def test_lower_support_lengths_and_source_points_survive_pitch_change(self):
        from lib.lower_support_geometry import run,hull_holes
        from lib.roller_geometry import stations
        data=load();before=stations(data);holes=hull_holes(data)
        old=datum_values('PortRollers_Unit000',data)
        data['parameters']['shoe_pitch']['value']+=.5;data['values']=resolve(data['parameters'])
        for key,length in [('05short',168.275),('05long',822.325)]:
            r=run(data,key);self.assertAlmostEqual(r['ends'][1]-r['ends'][0],length)
        self.assertNotEqual(holes,hull_holes(data))
        self.assertNotEqual(old['rotation_deg'],datum_values('PortRollers_Unit000',data)['rotation_deg'])
        self.assertEqual([(s['source_x'],s['source_z']) for s in before],[(s['source_x'],s['source_z']) for s in stations(data)])

    def test_lower_stock_moves_owned_bolt_seat_without_changing_upper_stock(self):
        data=load();key='PortLowerSupports_Outer_Run01_Bolt00'
        old=datum_values(key,data)['translation'];upper=data['values']['roller_support_thickness'].value
        data['parameters']['lower_support_thickness']['value']+=.5;data['values']=resolve(data['parameters'])
        new=datum_values(key,data)['translation']
        self.assertAlmostEqual(new[1]-old[1],.5);self.assertAlmostEqual(new[2]-old[2],-.25)
        self.assertEqual(data['values']['roller_support_thickness'].value,upper)

    def test_idler_adjustment_keeps_brackets_fixed_and_follows_source_axis(self):
        import math
        from lib.idler_geometry import axis
        from lib.wheel_geometry import station
        data=load();original=station(data);source=axis(data)
        bracket=datum_values('PortIdler_Unit000_Supports',data)
        data['parameters']['idler_diameter']['value']+=1
        data['values']=resolve(data['parameters']);changed=station(data)
        self.assertEqual(source,axis(data))
        self.assertEqual(bracket,datum_values('PortIdler_Unit000_Supports',data))
        self.assertGreater(abs(changed['travel']-original['travel']),.1)
        self.assertAlmostEqual(changed['x_offset']*math.sin(source[2])-changed['z_offset']*math.cos(source[2]),0)

    def test_idler_shaft_source_counts_reject_undeclared_missing_parts(self):
        from lib.track_validation import source_composition
        data=load()
        report=next(r for r in source_composition(data) if r['template']=='idler_shaft')
        self.assertTrue(report['complete'])
        self.assertEqual(sum(report['modeled_counts'].values()),9)
        shaft=data['assemblies']['idler_shaft']
        shaft['children'].remove(next(c for c in shaft['children'] if c.get('definition')=='idler_shaft'))
        with self.assertRaisesRegex(ValueError,'Source composition mismatch'):
            source_composition(data)
        shaft.update(composition_status='partial',omitted_source_counts={'P_b6e2672cc73e5dd6':1})
        report=next(r for r in source_composition(data) if r['template']=='idler_shaft')
        self.assertFalse(report['complete'])
        self.assertEqual(sum(report['modeled_counts'].values()),8)

    def test_idler_keeps_x_y_identity_and_rejects_missing_rivet(self):
        from lib.wheel_validation import composition
        data=load();selected=[i for i in data['occurrences'] if i['definition'] and i['id'].startswith(('PortIdler_','StarboardIdler_'))]
        report=composition(data,selected)
        self.assertEqual(sum(r['modeled_leaves'] for r in report['installed']),306)
        wheel=next(r for r in report['assemblies'] if r['template']=='idler_wheel')
        self.assertTrue(wheel['complete'])
        self.assertEqual(wheel['leaf_total'],119)
        selected.remove(next(i for i in selected if i['definition']=='wheel_rivet_rim'))
        with self.assertRaisesRegex(ValueError,'Idler constituent count mismatch'):
            composition(data,selected)

    def test_front_roller_adjustment_preserves_source_and_invalidates_station_cache(self):
        from lib.roller_geometry import stations
        data=load();before=stations(data)
        self.assertAlmostEqual(before[0]['x']-before[0]['source_x'],-45)
        data['parameters']['idler_front_roller_offset']['value']=-44
        data['values']=resolve(data['parameters']);after=stations(data)
        self.assertAlmostEqual(after[0]['x']-before[0]['x'],1)
        self.assertEqual(after[0]['source_x'],before[0]['source_x'])
        self.assertEqual(after[1:],before[1:])

    def test_units_and_out_of_order_dependencies(self):
        data = {"twice": parameter("mm", expression="length*2"), "length": parameter("in", 3)}
        values = resolve(data)
        self.assertAlmostEqual(values["twice"].value, 152.4)

    def test_adding_angle_to_length_is_rejected(self):
        data = {"l": parameter("mm", 5), "a": parameter("deg", 45), "bad": parameter("mm", expression="l+a")}
        with self.assertRaisesRegex(ValueError, "Dimension mismatch"):
            resolve(data)

    def test_count_and_unit_errors_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "nonnegative integer"):
            resolve({"count": parameter("count", 3.2)})
        with self.assertRaisesRegex(ValueError, "units"):
            resolve({"length": parameter("parsecs", 3)})
        with self.assertRaisesRegex(ValueError, "numeric"):
            resolve({"length": parameter("mm", True)})

    def test_parameter_cycles_and_executable_expressions_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "cycle"):
            resolve({"a": parameter("mm", expression="b"), "b": parameter("mm", expression="a")})
        with self.assertRaises(ValueError):
            resolve({"a": parameter("mm", expression="__import__('os').getcwd()")})

    def test_geometry_field_requires_correct_dimensions(self):
        values = resolve({"length": parameter("mm", 25)})
        with self.assertRaisesRegex(ValueError, "units"):
            scalar("length", values, (0,1))

    def test_actual_authored_records_and_scoped_count(self):
        data = load()
        self.assertEqual(data["values"]["track_units_per_side"].value, 78)
        self.assertEqual(data["configuration"]["decisions"]["P_619a5da15fa3acce"]["installed_count"], 3)
        self.assertFalse(data["model"]["physical_release"])

    def test_louver_source_count_rejects_handbook_outlet_count_in_snl_configuration(self):
        from lib.louver_validation import composition
        data=load()
        ids={i['id'] for i in data['occurrences'] if (i['definition'] or '').startswith('louver_')}
        report=composition(data,ids)
        self.assertEqual(sum(x['actual'] for x in report),82)
        extra=copy.deepcopy(next(i for i in data['occurrences'] if i['id']=='louver_outlet_blade_027'))
        extra['id']='louver_outlet_blade_extra'
        data['occurrences'].append(extra);ids.add(extra['id'])
        with self.assertRaisesRegex(ValueError,'quantity mismatch: M994'):
            composition(data,ids)

    def test_roller_counts_keep_upper_shared_parts_separate_from_snl_lower_totals(self):
        from lib.roller_validation import composition
        data=load()
        ids={i['id'] for i in data['occurrences'] if i['definition'] and i['id'].startswith(('PortRollers_','StarboardRollers_'))}
        report=composition(data,ids)
        self.assertEqual(sum(r['actual'] for r in report),1228)
        tube=[r for r in report if r['role']=='tube']
        self.assertEqual(sorted(r['actual'] for r in tube),[2,58])
        ids.remove('PortRollers_Unit029_Rotating_Tube')
        with self.assertRaisesRegex(ValueError,'Upper roller quantity mismatch: tube'):
            composition(data,ids)

    def test_upper_supports_retain_handbook_whole_vehicle_quantity(self):
        from lib.roller_validation import composition
        data=load()
        ids={i['id'] for i in data['occurrences'] if i['definition'] and i['id'].startswith(('PortRollers_','StarboardRollers_'))}
        report=composition(data,ids)
        supports=next(r for r in report if r['role']=='upper_support')
        self.assertEqual((supports['record'],supports['expected'],supports['actual']),
                         ('HB:nomenclature:221:019',4,4))
        ids.remove('PortRollers_Unit029_SupportA')
        with self.assertRaisesRegex(ValueError,'Upper support quantity/scope mismatch'):
            composition(data,ids)

    def test_roller_station_and_hull_openings_follow_track_pitch_without_refitting_source(self):
        from lib.roller_geometry import stations
        from lib.hull_geometry import arguments
        data=load();before=stations(data)
        data['parameters']['shoe_pitch']['value']+=.5
        data['values']=resolve(data['parameters']);after=stations(data)
        self.assertEqual([s['x'] for s in before],[s['x'] for s in after])
        self.assertEqual([s['source_z'] for s in before],[s['source_z'] for s in after])
        self.assertGreater(max(abs(a['z']-b['z']) for a,b in zip(before,after)),.1)
        openings=arguments(data['definitions']['hull_port_outer_skirt_front'],data)['roller_clearance']['stations']
        self.assertEqual([s['z'] for s in openings],[s['z'] for s in after])

    def test_upper_roller_is_accessible_from_the_engine_compartment_as_hb144_requires(self):
        from lib.roller_geometry import stations
        data=load();upper=next(s for s in stations(data) if s['kind']=='upper')
        rear=data['values']['hull_engine_back_x'].value
        front=rear+data['values']['hull_engine_length'].value
        self.assertGreater(upper['x'],rear)
        self.assertLess(upper['x'],front)
        self.assertIn('page:HB:144',upper['evidence'])

    def test_upper_source_quantities_detect_a_missing_plate(self):
        from lib.upper_validation import composition
        data = load()
        ids = {i["id"] for i in data["occurrences"] if (i["definition"] or "").startswith("upper_")}
        result = composition(data,ids)
        self.assertEqual(len(result),21)
        self.assertEqual(sum(x["actual"] for x in result),26)
        ids.remove("upper_lookout_rear")
        with self.assertRaisesRegex(ValueError,"quantity mismatch: M2347"):
            composition(data,ids)

    def test_hull_source_quantities_detect_a_missing_numbered_floor(self):
        from lib.hull_validation import composition
        data=load()
        ids={i["id"] for i in data["occurrences"] if (i["definition"] or "").startswith("hull_")}
        report=composition(data,ids)
        self.assertEqual(len(report),63)
        self.assertEqual(sum(x["actual"] for x in report),77)
        ids.remove("hull_floor_6")
        with self.assertRaisesRegex(ValueError,"quantity mismatch: M1936"):
            composition(data,ids)

    def test_photograph_cannot_be_used_as_metric_geometry(self):
        with self.assertRaisesRegex(ValueError, "visual-only"):
            point(load(), "snl_1", [100,100])

    def test_sponson_source_quantities_detect_missing_handed_roof(self):
        from lib.sponson_validation import composition
        data=load()
        ids={i['id'] for i in data['occurrences'] if (i['definition'] or '').startswith('sponson_')}
        report=composition(data,ids)
        self.assertEqual(len(report),38)
        self.assertEqual(sum(x['actual'] for x in report),39)
        ids.remove('sponson_starboard_roof')
        with self.assertRaisesRegex(ValueError,'quantity mismatch: M2756A'):
            composition(data,ids)

    def test_nested_datums_reject_cycles(self):
        data = load()
        data["datums"]["world"]["parent"] = "port_track"
        with self.assertRaisesRegex(ValueError, "cyclic"):
            datum_values("port_track", data)

    def test_track_template_matches_independent_source_composition(self):
        from lib.track_validation import source_composition
        data = load()
        checks = source_composition(data)
        shoe = next(x for x in checks if x["template"] == "track_unit")
        self.assertEqual(shoe["leaf_total"],19)
        data["assemblies"]["track_channel_A"]["children"].pop(0)
        with self.assertRaisesRegex(ValueError,"composition mismatch"):
            source_composition(data)

    def test_track_pattern_retains_parameter_dependencies(self):
        data = load()
        datum = "PortTrack_Unit002_Links_ChannelB_PinAssembly"
        before = datum_values(datum,data)["translation"][0]
        before_unit = datum_values("PortTrack_Unit002",data)["translation"]
        data["parameters"]["shoe_pitch"]["value"] += 0.5
        data["values"] = resolve(data["parameters"])
        self.assertAlmostEqual(datum_values(datum,data)["translation"][0]-before,0.25)
        self.assertNotEqual(datum_values("PortTrack_Unit002",data)["translation"],before_unit)

    def test_upper_track_clearance_parameter_invalidates_route_cache(self):
        import math
        from lib.track_path import solve
        data=load()
        raised=solve(data)
        data["parameters"]["track_upper_clearance_lift"]["value"]=0
        data["values"]=resolve(data["parameters"])
        original=solve(data)
        self.assertGreater(max(a[1]-b[1] for a,b in zip(raised["pins"],original["pins"])),50)
        for route in [raised,original]:
            self.assertEqual(len(route["pins"]),78)
            for a,b in zip(route["pins"],route["pins"][1:]+route["pins"][:1]):
                self.assertAlmostEqual(math.dist(a,b),283.3116,places=6)

    def test_closed_track_uses_printed_count_and_chord_pitch(self):
        import math
        from lib.track_path import solve
        solution = solve(load())
        pins = solution["pins"]
        self.assertEqual(len(pins),78)
        for a,b in zip(pins,pins[1:]+pins[:1]):
            self.assertAlmostEqual(math.dist(a,b),283.3116,places=6)
        self.assertLess(solution["max_bend_deg"],35)
        self.assertGreater(solution["min_bend_deg"],-5)
        self.assertFalse(solution["wheel_contact_qualified"])


if __name__ == "__main__":
    unittest.main()
