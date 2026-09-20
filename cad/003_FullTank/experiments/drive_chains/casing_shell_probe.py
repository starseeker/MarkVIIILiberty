"""Save, reopen and check both casing shells against chains and installed tank."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage', type=Path, required=True)
parser.add_argument('--output', type=Path, default=ROOT / 'casing_shell_build')
parser.add_argument('--worker', action='store_true')
parser.add_argument('--fit-casing-passages', action='store_true')
args = parser.parse_args()
stage, out = args.stage.resolve(), args.output.resolve()
sys.path.insert(0, str(stage))
from lib import runtime
from lib.evidence import fingerprint, read, write, sha

if not args.worker:
    out.mkdir(parents=True, exist_ok=True)
    with (out / 'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable, __file__, '--stage', str(stage), '--output', str(out), '--worker'] +
                 (['--fit-casing-passages'] if args.fit_casing_passages else []),
                 env=runtime.environment(out), stdout=log, stderr=subprocess.STDOUT).returncode)

try:
    App, Gui = runtime.start_gui()
    import numpy as np
    import Part
    from types import SimpleNamespace
    from lib.cad_build import leaves, metadata
    from lib.worker import check_build
    from lib.model import load
    from lib.pinion_geometry import values
    from lib.visual_review import shaded
    from casing_parts import shells
    from lib.hull_validation import validate as validate_hull

    lock = fingerprint()
    build = check_build(stage / 'build')
    paths = [Path(__file__), ROOT / 'casing_parts.py', ROOT / 'casing_controls.json',
             ROOT / 'casing_source_rows.json', ROOT / 'installed_pitch_route_report.json',
             ROOT / 'chain_candidate_controls.json', ROOT / 'casing_passage_build/report.json',
             ROOT / 'casing_passage_build/CasingPassageCandidate.FCStd']
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    controls, sources, route, chain_controls, prior = [read(p) for p in paths[2:7]]
    a = {key: record['value'] for key, record in controls['controls'].items()}
    assert prior['passed'] and prior['native_sha256'] == sha(paths[-1])
    assert prior['authored_fingerprint'] == lock and prior['tank_native_hashes'] == build['native_hashes']
    shapes, dimensions = shells(a, route, values(load())['hub_radius'],
                                chain_controls['controls']['small_hub_radius']['value'])
    tank = App.openDocument(build['build']['top_document'])
    tank.recompute()
    original = leaves(tank.Root)
    context = [i for i in original if i['id'] not in prior['replaced_existing_occurrences']]
    doc = App.openDocument(str(paths[-1]))
    doc.recompute()
    before = leaves(doc.Root)
    opening_changes = []
    if args.fit_casing_passages:
        wall = next(i for i in original if i['id'] == 'hull_engine_back')
        old = next(i for i in before if i['id'] == 'hull_engine_back')
        b = wall['shape'].BoundBox
        slab = Part.makeBox(b.XLength, 6000, 6000, App.Vector(b.XMin, -3000, -1000))
        section_bounds = shapes['body'].common(slab).BoundBox
        gap, radius = a['passage_straight_gap'], a['passage_corner_radius']
        z0, z1 = section_bounds.ZMin - gap, section_bounds.ZMax + gap
        width = section_bounds.YLength + 2 * gap
        x0, depth = b.XMin - 1, b.XLength + 2
        cutters = []
        for hand in ['Port', 'Starboard']:
            cy = next(i for i in before if i['id'] == hand + 'Chain_RollerPinion')['shape'].Placement.Base.y
            y0, y1 = cy - width / 2, cy + width / 2
            assert b.YMin < y0 < y1 < b.YMax and b.ZMin < z0 < z1 < b.ZMax
            pieces = [Part.makeBox(depth, width - 2 * radius, z1 - z0, App.Vector(x0, y0 + radius, z0)),
                      Part.makeBox(depth, width, z1 - z0 - 2 * radius, App.Vector(x0, y0, z0 + radius))]
            for y in [y0 + radius, y1 - radius]:
                for z in [z0 + radius, z1 - radius]:
                    pieces.append(Part.makeCylinder(radius, depth, App.Vector(x0, y, z), App.Vector(1, 0, 0)))
            cutters.append(pieces[0].multiFuse(pieces[1:]).removeSplitter())
            opening_changes.append(dict(side=hand, center_y_mm=cy, width_mm=width, bottom_z_mm=z0,
                                        top_z_mm=z1, height_mm=z1-z0, corner_radius_mm=radius))
        revised = wall['shape'].cut(Part.makeCompound(cutters)).removeSplitter()
        assert revised.isValid() and len(revised.Solids) == 1
        # Enlarging a previous passage cannot add material to the old passing
        # context. Verify this before reusing any prior contact evidence.
        assert revised.cut(old['shape']).Volume < 1e-5
        for attr in ['XMin', 'YMin', 'ZMin', 'XMax', 'YMax', 'ZMax']:
            assert abs(getattr(revised.BoundBox, attr) - getattr(b, attr)) < 1e-7
        old['target'].Tip.Shape = revised
        doc.recompute()
    definitions = {}
    for kind, mark in [('body', 'M1590'), ('cap', 'M1591')]:
        body = doc.addObject('PartDesign::Body', 'Def_Casing_' + kind)
        doc.Definitions.addObject(body)
        feature = body.newObject('PartDesign::Feature', 'InferredSheetShell')
        feature.Shape = shapes[kind]
        metadata(body, DefinitionId='chain_casing_' + kind, Representation='assembly', Coverage='partial',
                 SurveyIds=[sources['parts'][mark]['part_id']], OriginalMark=mark,
                 ReconstructionNotes='Analytic contour and cap seam inferred; see casing_controls.json')
        definitions[kind] = body
    for hand in ['Port', 'Starboard']:
        center_y = next(i for i in before if i['id'] == hand + 'Chain_RollerPinion')['shape'].Placement.Base.y
        group = doc.addObject('App::Part', hand + 'Casing')
        doc.Root.addObject(group)
        for kind in ['body', 'cap']:
            name = hand + 'Casing_' + kind.title()
            obj = doc.addObject('App::Link', name)
            group.addObject(obj)
            obj.setLink(definitions[kind])
            # Both shells are symmetric about local Y, so translations preserve
            # the proper mirrored installation without reflected native geometry.
            obj.LinkPlacement = App.Placement(App.Vector(0, center_y, 0), App.Rotation())
            metadata(obj, OccurrenceId=name, Subsystem='Drivetrain')
    metadata(doc.Root, Scope='Experimental chains, wall passages and casing shells; hardware still pending')
    doc.Definitions.Visibility = False
    doc.recompute()
    native = out / 'CasingShellCandidate.FCStd'
    doc.saveAs(str(native))
    App.closeDocument(doc.Name)
    doc = App.openDocument(str(native))
    doc.recompute()
    candidates = leaves(doc.Root)
    assert len(candidates) == 509
    for item in candidates:
        assert item['shape'].isValid() and len(item['shape'].Solids) == 1
    new = [i for i in candidates if i['definition'].startswith('chain_casing_')]
    physical = [i for i in context if i['representation'] == 'assembly'] + candidates
    boxes = np.array([[b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax]
                      for b in [i['shape'].BoundBox for i in physical]])
    ids = {i['id'] for i in new}
    overlaps, neighbors, counts = [], set(), dict(casing_internal=0, previous_candidate=0, existing_tank=0)
    candidate_ids = {i['id'] for i in candidates}
    for first in new:
        b = first['shape'].BoundBox
        box = np.array([b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax])
        near = np.where(np.all(boxes[:, :3] <= box[3:] + 1e-7, axis=1) &
                        np.all(boxes[:, 3:] >= box[:3] - 1e-7, axis=1))[0]
        for n in near:
            second = physical[n]
            if second['id'] in ids:
                if second['id'] <= first['id']:
                    continue
                counts['casing_internal'] += 1
            elif second['id'] in candidate_ids:
                counts['previous_candidate'] += 1
            else:
                counts['existing_tank'] += 1
                neighbors.add(second['id'])
            volume = first['shape'].common(second['shape']).Volume
            if volume > 1e-5:
                overlaps.append(dict(a=first['id'], b=second['id'], volume_mm3=volume))
    interfaces = []
    for hand in ['Port', 'Starboard']:
        parts = [i for i in new if i['id'].startswith(hand)]
        wall = next(i for i in candidates if i['id'] == 'hull_engine_back')
        gear = next(i for i in candidates if i['id'] == hand + 'Chain_RollerPinion')
        interfaces.append(dict(side=hand,
            wall_clearance_mm=min(i['shape'].distToShape(wall['shape'])[0] for i in parts),
            roller_pinion_clearance_mm=min(i['shape'].distToShape(gear['shape'])[0] for i in parts),
            cap_body_gap_mm=parts[0]['shape'].distToShape(parts[1]['shape'])[0]))
    hull_report = validate_hull(load(), context + candidates, out) if args.fit_casing_passages else None
    if args.fit_casing_passages:
        assert min(row['wall_clearance_mm'] for row in interfaces) >= a['passage_minimum_gap'] - 1e-6
    report = dict(complete=True, passed=not overlaps, new_casing_occurrences=len(new),
        fixture_occurrences=len(candidates), candidate_pairs=counts, overlaps=overlaps,
        dimensions=dimensions, interfaces=interfaces, wall_opening_changes=opening_changes,
        hull_report='reports/hull_plates.json' if hull_report else None,
        wall_change_only_removes_material=args.fit_casing_passages,
        native_sha256=sha(native), input_sha256=hashes,
        authored_fingerprint=lock, tank_native_hashes=build['native_hashes'],
        previous_candidate_report_sha256=sha(paths[-2]), standard_assembly_modified=False,
        full_casing_bom_populated=False, source_bom_reconciled=False, historical_fit_qualified=False,
        visual_review_status='pending', rendering_complete=False)
    # Persist measured fit before rendering; an interrupted preview must not
    # discard the native result or masquerade as a completed review.
    write(out / 'report.json', report)
    print('Casing shells:', counts, len(overlaps), 'overlaps', flush=True)
    neighbors = [i for i in context if i['id'] in neighbors]
    shaded(neighbors + candidates, out / 'casing_installed_oblique.svg', (1, 1, .65),
           'Chain casing body and cap candidates | inferred contours and seams; hardware pending')
    shaded(new, out / 'shells_oblique.svg', (1, 1, .65),
           'Paired M1590 bodies and M1591 caps | nominal standard positions')
    shaded([i for i in new if i['id'].startswith('Port')], out / 'shell_elevation.svg', (0, 1, 0),
           'Port casing elevation | inferred cap seam; source-sized overall width')
    # A section through the casing exposes the chain without changing its pose.
    section = []
    center_y = next(i for i in candidates if i['id'] == 'PortChain_RollerPinion')['shape'].Placement.Base.y
    half = Part.makeBox(5000, 5000, 5000, App.Vector(-1000, center_y, -1000))
    for item in new:
        if not item['id'].startswith('Port'):
            continue
        cut = item['shape'].cut(half)
        if not cut.isNull():
            section.append(dict(item, shape=cut, target=SimpleNamespace(Shape=cut), definition=item['id']+'_section'))
    chain = [i for i in candidates if i['id'].startswith('PortChain_')]
    shaded(section + chain, out / 'casing_half_section.svg', (1, 1, .65),
           'Port casing section | separate chain parts retained; static fit only')
    assert fingerprint() == lock
    check_build(stage / 'build')
    assert all(sha(p) == hashes[str(p.relative_to(ROOT))] for p in paths)
    report['rendering_complete'] = True
    write(out / 'report.json', report)
    sys.exit(0 if report['passed'] else 1)
finally:
    runtime.close()
