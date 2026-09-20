"""Fit both source-identified transmission output rotors against chain/casing geometry."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage', type=Path, required=True)
parser.add_argument('--output', type=Path, default=ROOT / 'transmission_output_build')
parser.add_argument('--worker', action='store_true')
args = parser.parse_args()
stage, out = args.stage.resolve(), args.output.resolve()
sys.path.insert(0, str(stage))
from lib import runtime
from lib.evidence import read, write, sha, fingerprint, REPO

if not args.worker:
    out.mkdir(parents=True, exist_ok=True)
    with (out / 'run.log').open('w') as log:
        sys.exit(subprocess.run([
            sys.executable, __file__, '--stage', str(stage), '--output', str(out), '--worker'
        ], env=runtime.environment(out), stdout=log, stderr=subprocess.STDOUT).returncode)

try:
    App, Gui = runtime.start_gui()
    import Part
    import numpy as np
    import base64
    from types import SimpleNamespace
    from lib.cad_build import leaves, metadata
    from lib.worker import check_build
    from lib.visual_review import shaded
    from transmission_output_parts import parts, cylinder

    lock = fingerprint()
    build = check_build(stage / 'build')
    names = ['transmission_output_probe.py', 'transmission_output_parts.py',
             'transmission_output_sources.json', 'transmission_output_controls.json',
             'transmission_output_calibration.json', 'chain_candidate_controls.json',
             'chain_detail_build/report.json', 'chain_detail_build/ChainDetailCandidate.FCStd']
    hashes = {name: sha(ROOT / name) for name in names}
    for name in names:
        if '/' not in name:
            target = out / 'inputs' / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / name).read_bytes())
    sources = read(ROOT / names[2])
    for name, expected in sources['inspected_source_hashes'].items():
        assert sha(REPO / name) == expected
    a = {k: v['value'] for k, v in read(ROOT / names[5])['controls'].items()}
    controls = {k: v['value'] for k, v in read(ROOT / names[3])['controls'].items()}
    calibration = read(ROOT / names[4])
    prior = read(ROOT / names[-2])
    assert prior['passed'] and prior['rendering_complete'] and prior['native_sha256'] == hashes[names[-1]]
    assert prior['authored_fingerprint'] == lock and prior['tank_native_hashes'] == build['native_hashes']
    shapes, dimensions = parts(a, controls, calibration)
    doc = App.openDocument(str(ROOT / names[-1]))
    doc.recompute()
    before = leaves(doc.Root)
    definitions = {}
    for key, mark, record in [('shaft', 'M289', 'SNL:215:028'), ('drum', 'M292', 'SNL:83:036')]:
        row = next(r for r in sources['rows'] if r['record_id'] == record)
        assert len(row['part_ids']) == 1
        body = doc.addObject('PartDesign::Body', 'Def_Output_' + key)
        doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature', 'ReconstructedRotor').Shape = shapes[key]
        metadata(body, DefinitionId='transmission_output_' + key, OriginalMark=mark,
                 SurveyIds=row['part_ids'], SourceRecord=record, Representation='assembly', Coverage='partial',
                 ReconstructionNotes='Conditional drawing scale and inferred profiles; see transmission_output_controls.json')
        definitions[key] = body
    new_ids = []
    for hand in ['Port', 'Starboard']:
        group = doc.addObject('App::Part', hand + 'TransmissionOutput')
        doc.Root.addObject(group)
        gear = next(i for i in before if i['id'] == hand + 'Chain_TransmissionPinion')
        pose = gear['shape'].Placement.multiply(gear['target'].Shape.Placement.inverse())
        for key in definitions:
            name = hand + 'TransmissionOutput_' + key
            obj = doc.addObject('App::Link', name)
            group.addObject(obj)
            obj.setLink(definitions[key])
            obj.LinkPlacement = pose
            metadata(obj, OccurrenceId=name, Subsystem='Drivetrain')
            new_ids.append(name)
    metadata(doc.Root, Scope='Isolated chain/casing plus partial M289 shafts and M292 drums; supports and axial retention incomplete')
    doc.Definitions.Visibility = False
    doc.recompute()
    native = out / 'TransmissionOutputCandidate.FCStd'
    doc.saveAs(str(native))
    App.closeDocument(doc.Name)
    doc = App.openDocument(str(native))
    doc.recompute()
    items = leaves(doc.Root)
    assert len(items) == 813
    for item in items:
        if not item['shape'].isValid() or len(item['shape'].Solids) != 1:
            raise ValueError('Invalid output installation leaf ' + item['id'])
    tank = App.openDocument(build['build']['top_document'])
    tank.recompute()
    replaced = {'hull_engine_back', 'PortPinion_Rotor_Casting', 'StarboardPinion_Rotor_Casting',
                'hull_port_inner_rear_end', 'hull_port_rear_wing',
                'hull_starboard_inner_rear_end', 'hull_starboard_rear_wing'}
    context = [i for i in leaves(tank.Root) if i['id'] not in replaced]
    byid = {i['id']: i for i in items}
    physical = items + [i for i in context if i['representation'] == 'assembly']
    boxes = np.array([[b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax]
                      for b in [i['shape'].BoundBox for i in physical]])
    pairs, overlaps = set(), []
    for name in new_ids:
        first = byid[name]
        b = first['shape'].BoundBox
        box = np.array([b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax])
        near = np.where(np.all(boxes[:, :3] <= box[3:] + 1e-7, axis=1)
                        & np.all(boxes[:, 3:] >= box[:3] - 1e-7, axis=1))[0]
        for index in near:
            second = physical[index]
            pair = tuple(sorted([name, second['id']]))
            if pair[0] == pair[1] or pair in pairs:
                continue
            pairs.add(pair)
            volume = first['shape'].common(second['shape']).Volume
            if volume > 1e-5:
                overlaps.append(dict(a=name, b=second['id'], volume_mm3=volume))
    interfaces = []
    for hand in ['Port', 'Starboard']:
        shaft = byid[hand + 'TransmissionOutput_shaft']
        pose = shaft['shape'].Placement.multiply(shaft['target'].Shape.Placement.inverse())
        twist = shaft['target'].Shape.copy()
        twist.rotate(App.Vector(), App.Vector(0, 1, 0), controls['spline_rotation_witness'])
        twist.Placement = pose.multiply(twist.Placement)
        bare = cylinder(dimensions['shaft_root_radius_mm'], *dimensions['shaft_ends_local_y_mm'])
        bare.Placement = pose.multiply(bare.Placement)
        for role, name in [('sprocket', hand + 'Chain_TransmissionPinion'),
                           ('brake_drum', hand + 'TransmissionOutput_drum')]:
            receiver = byid[name]['shape']
            fit = shaft['shape'].common(receiver).Volume
            gap = shaft['shape'].distToShape(receiver)[0]
            capture = twist.common(receiver).Volume
            negative = bare.common(receiver).Volume
            interfaces.append(dict(hand=hand, receiver=role, overlap_mm3=fit,
                                   minimum_gap_mm=gap, twist_capture_mm3=capture,
                                   unsplined_negative_control_mm3=negative,
                                   passed=fit < 1e-5 and gap > 0 and capture > 1e-3 and negative < 1e-5))
    seating = []
    for hand in ['Port', 'Starboard']:
        distance = byid[hand + 'TransmissionOutput_drum']['shape'].distToShape(
            byid[hand + 'Chain_TransmissionPinion']['shape'])[0]
        seating.append(dict(hand=hand, drum_sprocket_hub_distance_mm=distance, passed=distance < 1e-6))
    passed = not overlaps and all(r['passed'] for r in interfaces + seating)
    report = dict(complete=True, passed=passed, fixture_occurrences=len(items), added_occurrences=4,
                  material_candidate_pairs=len(pairs), overlaps=overlaps, dimensions=dimensions,
                  spline_interfaces=interfaces, hub_seating=seating,
                  input_sha256=hashes, native_sha256=sha(native), authored_fingerprint=lock,
                  tank_native_hashes=build['native_hashes'], historical_fit_qualified=False,
                  source_inventory_reconciled=False, axial_retention_qualified=False,
                  bearing_support_qualified=False, standard_assembly_modified=False,
                  rendering_complete=False, visual_review_status='pending')
    write(out / 'report.json', report)
    print('Output rotors:', len(pairs), 'material pairs;', len(overlaps), 'overlaps; passed=', passed, flush=True)
    port_ids = {'PortTransmissionOutput_shaft', 'PortTransmissionOutput_drum', 'PortChain_TransmissionPinion'}
    shaded([i for i in items if i['id'] in port_ids], out / 'output_rotor_oblique.svg',
           (1, 1, .65), 'M289 output shaft and M292 track-brake drum | conditional reconstruction')
    adjacent = [i for i in items if i['id'].startswith(('PortCasing', 'PortTransmissionOutput'))
                or i['id'] == 'PortChain_TransmissionPinion']
    shaded(adjacent, out / 'output_casing_fit.svg', (1, -1, .6),
           'Transmission output and chain casing | diagnostic fit; see overlap report')
    section = []
    slab = Part.makeBox(.6, 700, 700, App.Vector(-.3, -430, -350))
    for key in shapes:
        cut = shapes[key].common(slab)
        section.append(dict(id=key, definition=key + '_section', shape=cut,
                            target=SimpleNamespace(Shape=cut), system='Drivetrain', representation='assembly'))
    shaded(section, out / 'output_rotor_section.svg', (1, 0, 0),
           'Output rotor meridian | separate shaft and inferred drum casting section')
    # Overlay exact kernel section edges on the unchanged illustration.
    scale = calibration['mm_per_pixel']
    width, height = calibration['image_size_px']
    background = base64.b64encode((REPO / calibration['image']).read_bytes()).decode()
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           f'<image width="{width}" height="{height}" href="data:image/png;base64,{background}" opacity="0.75"/>']
    # Use a thin slice boundary so the full shaft and drum contour are always covered.
    for key, color in [('shaft', '#0062d6'), ('drum', '#d74200')]:
        for edge in shapes[key].common(slab).Edges:
            vertices = edge.discretize(Deflection=.2)
            points = ' '.join(f'{calibration["sprocket_center_x_px"]-v.y/scale:.3f},{calibration["shaft_axis_y_px"]-v.z/scale:.3f}' for v in vertices)
            svg.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2"/>')
    svg.append('<rect x="20" y="1040" width="1280" height="72" fill="white" opacity="0.92"/>')
    svg.append('<text x="35" y="1065" font-family="sans-serif" font-size="20">Native section overlay: blue M289 shaft; orange M292 drum. Four-inch hub scale.</text>')
    svg.append('<text x="35" y="1095" font-family="sans-serif" font-size="18">Profiles and diameters inferred; scan residuals retained. No historical-fit acceptance.</text></svg>')
    (out / 'source_section_overlay.svg').write_text('\n'.join(svg))
    import fitz
    preview = fitz.open(stream=(out / 'source_section_overlay.svg').read_bytes(), filetype='svg')
    preview[0].get_pixmap().save(str(out / 'source_section_overlay.png'))
    preview.close()
    assert fingerprint() == lock
    check_build(stage / 'build')
    assert all(sha(ROOT / name) == hashes[name] for name in names)
    report['rendering_complete'] = True
    write(out / 'report.json', report)
    sys.exit(0 if passed else 1)
finally:
    runtime.close()
