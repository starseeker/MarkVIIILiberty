"""Check a locally narrowed casing against the unchanged output rotors and chain."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage', type=Path, required=True)
parser.add_argument('--output', type=Path, default=ROOT / 'casing_front_build')
parser.add_argument('--worker', action='store_true')
args = parser.parse_args()
stage, out = args.stage.resolve(), args.output.resolve()
sys.path.insert(0, str(stage))
from lib import runtime
from lib.evidence import read, write, sha, fingerprint

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
    from types import SimpleNamespace
    from lib.cad_build import leaves, metadata
    from lib.worker import check_build
    from lib.visual_review import shaded
    from casing_front_parts import narrowed_front

    lock = fingerprint()
    build = check_build(stage / 'build')
    names = ['casing_front_probe.py', 'casing_front_parts.py', 'casing_front_controls.json',
             'casing_parts.py', 'casing_controls.json', 'installed_pitch_route_report.json',
             'casing_shell_passage_build/report.json', 'transmission_output_build/report.json',
             'transmission_output_build/TransmissionOutputCandidate.FCStd']
    hashes = {name: sha(ROOT / name) for name in names}
    for name in names:
        if '/' not in name:
            target = out / 'inputs' / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / name).read_bytes())
    a = {k: v['value'] for k, v in read(ROOT / names[4])['controls'].items()}
    detail = {k: v['value'] for k, v in read(ROOT / names[2])['controls'].items()}
    route = read(ROOT / names[5])
    shell = read(ROOT / names[6])['dimensions']
    prior = read(ROOT / names[-2])
    assert prior['rendering_complete'] and prior['native_sha256'] == hashes[names[-1]]
    assert prior['authored_fingerprint'] == lock and prior['tank_native_hashes'] == build['native_hashes']
    assert not prior['passed'] and len(prior['overlaps']) == 2
    assert {r['b'] for r in prior['overlaps']} == {'PortCasing_Body', 'StarboardCasing_Body'}
    assert all(r['passed'] for r in prior['spline_interfaces'] + prior['hub_seating'])
    doc = App.openDocument(str(ROOT / names[-1]))
    doc.recompute()
    before = leaves(doc.Root)
    body = next(i['target'] for i in before if i['id'] == 'PortCasing_Body')
    assert body == next(i['target'] for i in before if i['id'] == 'StarboardCasing_Body')
    old = body.Shape.copy()
    updated, detail_report = narrowed_front(old, a, detail, route, shell)
    body.Tip.Shape = updated
    metadata(body, ReconstructionNotes='Locally narrowed transmission end; casing_front_controls.json retains inferred profile and maximum width interpretation')
    metadata(doc.Root, Scope='Isolated chain/casing and output rotors with inferred front taper; bearings and axial retention incomplete')
    doc.Definitions.Visibility = False
    doc.recompute()
    native = out / 'CasingFrontCandidate.FCStd'
    doc.saveAs(str(native))
    App.closeDocument(doc.Name)
    doc = App.openDocument(str(native))
    doc.recompute()
    items = leaves(doc.Root)
    assert len(items) == 813 and {i['id'] for i in items} == {i['id'] for i in before}
    for item in items:
        if not item['shape'].isValid() or len(item['shape'].Solids) != 1:
            raise ValueError('Invalid narrowed-case leaf ' + item['id'])
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
    changed = [i for i in items if i['id'].endswith('Casing_Body') or 'TransmissionOutput_' in i['id']]
    pairs, overlaps = set(), []
    for first in changed:
        b = first['shape'].BoundBox
        box = np.array([b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax])
        near = np.where(np.all(boxes[:, :3] <= box[3:] + 1e-7, axis=1)
                        & np.all(boxes[:, 3:] >= box[:3] - 1e-7, axis=1))[0]
        for index in near:
            second = physical[index]
            pair = tuple(sorted([first['id'], second['id']]))
            if pair[0] == pair[1] or pair in pairs:
                continue
            pairs.add(pair)
            volume = first['shape'].common(second['shape']).Volume
            if volume > 1e-5:
                overlaps.append(dict(a=first['id'], b=second['id'], volume_mm3=volume))
    clearances = []
    for hand in ['Port', 'Starboard']:
        casing = byid[hand + 'Casing_Body']['shape']
        drum = byid[hand + 'TransmissionOutput_drum']['shape']
        gap = casing.distToShape(drum)[0]
        chain = [i for i in items if i['id'].startswith(hand + 'Chain_')]
        distances = [(casing.distToShape(i['shape'])[0], i['id']) for i in chain]
        closest, occurrence = min(distances)
        clearances.append(dict(hand=hand, drum_gap_mm=gap, closest_chain_gap_mm=closest,
                               closest_chain_occurrence=occurrence,
                               passed=gap >= detail['minimum_rotor_gap'] - 1e-6 and closest > 0))
    passed = (not overlaps and detail_report['rear_region_symmetric_difference_mm3'] < 1e-5
              and all(r['passed'] for r in clearances + detail_report['sheet_thickness_checks']))
    report = dict(complete=True, passed=passed, fixture_occurrences=len(items),
                  material_candidate_pairs=len(pairs), overlaps=overlaps, detail=detail_report,
                  clearances=clearances, retained_spline_interfaces=prior['spline_interfaces'],
                  retained_hub_seating=prior['hub_seating'], input_sha256=hashes,
                  native_sha256=sha(native), authored_fingerprint=lock, tank_native_hashes=build['native_hashes'],
                  standard_assembly_modified=False, historical_fit_qualified=False,
                  axial_retention_qualified=False, bearing_support_qualified=False,
                  source_inventory_reconciled=False, rendering_complete=False, visual_review_status='pending')
    write(out / 'report.json', report)
    print('Narrowed casing:', len(pairs), 'material pairs;', len(overlaps), 'overlaps; passed=', passed, flush=True)
    port = [i for i in items if i['id'].startswith(('PortCasing', 'PortTransmissionOutput'))
            or i['id'] == 'PortChain_TransmissionPinion']
    shaded(port, out / 'casing_output_oblique.svg', (1, -1, .6),
           'Locally narrowed chain casing and output rotor | inferred small-end profile')
    small = route['candidate_transmission_axis_xz_mm']
    slab = Part.makeBox(800, 900, 2, App.Vector(detail['taper_start_x'] - 40, 420, small[1] - 1))
    section = []
    for item in port:
        cut = item['shape'].common(slab)
        if not cut.isNull() and cut.Faces:
            section.append(dict(item, shape=cut, target=SimpleNamespace(Shape=cut), definition=item['id'] + '_section'))
    shaded(section, out / 'casing_output_plan_section.svg', (0, 0, 1),
           'Native shaft-height section | casing taper clears the retained brake drum', up_direction=(1, 0, 0))
    assert fingerprint() == lock
    check_build(stage / 'build')
    assert all(sha(ROOT / name) == hashes[name] for name in names)
    report['rendering_complete'] = True
    write(out / 'report.json', report)
    sys.exit(0 if passed else 1)
finally:
    runtime.close()
