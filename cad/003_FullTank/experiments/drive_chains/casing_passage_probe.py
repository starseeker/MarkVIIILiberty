"""Test source-motivated casing passages in an isolated M2003 wall copy."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage', type=Path, required=True)
parser.add_argument('--output', type=Path, default=ROOT / 'casing_passage_build')
parser.add_argument('--worker', action='store_true')
args = parser.parse_args()
stage, out = args.stage.resolve(), args.output.resolve()
sys.path.insert(0, str(stage))
from lib import runtime
from lib.evidence import fingerprint, read, write, sha

if not args.worker:
    out.mkdir(parents=True, exist_ok=True)
    with (out / 'run.log').open('w') as log:
        sys.exit(subprocess.run(
            [sys.executable, __file__, '--stage', str(stage), '--output', str(out), '--worker'],
            env=runtime.environment(out), stdout=log, stderr=subprocess.STDOUT).returncode)

try:
    App, Gui = runtime.start_gui()
    import Part
    import numpy as np
    from lib.cad_build import leaves, metadata
    from lib.worker import check_build
    from lib.visual_review import shaded
    from lib.model import load
    from lib.hull_validation import validate as validate_hull

    lock = fingerprint()
    build = check_build(stage / 'build')
    inputs = [ROOT / 'casing_passage_controls.json', ROOT / 'installed_pitch_route_report.json',
              ROOT / 'installed_chain_build/report.json', ROOT / 'installed_chain_build/InstalledChainsCandidate.FCStd',
              Path(__file__)]
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in inputs}
    controls = read(inputs[0])
    route = read(inputs[1])
    prior = read(inputs[2])
    assert prior['complete'] and not prior['passed']
    assert prior['native_sha256'] == sha(inputs[3])
    assert prior['authored_fingerprint'] == lock and prior['tank_native_hashes'] == build['native_hashes']
    assert len(prior['overlaps']) == 18 and {v['b'] for v in prior['overlaps']} == {'hull_engine_back'}

    tank = App.openDocument(build['build']['top_document'])
    tank.recompute()
    original = leaves(tank.Root)
    wall = next(i for i in original if i['id'] == 'hull_engine_back')
    b = wall['shape'].BoundBox
    centers = route['vertices_world_xz_mm']
    crossings = []
    for x in [b.XMin, b.XMax]:
        hits = []
        for p, q in zip(centers, centers[1:] + centers[:1]):
            if min(p[0], q[0]) < x < max(p[0], q[0]):
                t = (x - p[0]) / (q[0] - p[0])
                hits.append(p[1] + t * (q[1] - p[1]))
        assert len(hits) == 2
        crossings.append(dict(wall_face_x_mm=x, chain_center_z_mm=sorted(hits)))
    a = controls['assumptions_mm']
    margin = sum(a[k] for k in ['chain_radial_envelope', 'chain_to_casing_radial_gap',
                               'casing_wall_stock', 'casing_to_aperture_gap'])
    z0 = min(z for row in crossings for z in row['chain_center_z_mm']) - margin
    z1 = max(z for row in crossings for z in row['chain_center_z_mm']) + margin
    width = controls['source_evidence']['casing_width_mm'] + 2 * a['casing_to_aperture_gap']
    radius = a['aperture_corner_radius']
    x0, depth = b.XMin - 1, b.XLength + 2
    doc = App.openDocument(str(inputs[3]))
    doc.recompute()
    existing = leaves(doc.Root)
    cutters, openings = [], []
    for hand in ['Port', 'Starboard']:
        gear = next(i for i in existing if i['id'] == hand + 'Chain_RollerPinion')
        cy = gear['shape'].Placement.Base.y
        y0, y1 = cy - width / 2, cy + width / 2
        assert b.YMin < y0 < y1 < b.YMax and b.ZMin < z0 < z1 < b.ZMax
        pieces = [Part.makeBox(depth, width - 2 * radius, z1 - z0, App.Vector(x0, y0 + radius, z0)),
                  Part.makeBox(depth, width, z1 - z0 - 2 * radius, App.Vector(x0, y0, z0 + radius))]
        for y in [y0 + radius, y1 - radius]:
            for z in [z0 + radius, z1 - radius]:
                pieces.append(Part.makeCylinder(radius, depth, App.Vector(x0, y, z), App.Vector(1, 0, 0)))
        cut = pieces[0].multiFuse(pieces[1:]).removeSplitter()
        assert cut.isValid() and len(cut.Solids) == 1
        cutters.append(cut)
        openings.append(dict(side=hand, center_y_mm=cy, width_mm=width, bottom_z_mm=z0,
                             top_z_mm=z1, height_mm=z1-z0, corner_radius_mm=radius))
    revised = wall['shape'].cut(Part.makeCompound(cutters)).removeSplitter()
    assert revised.isValid() and len(revised.Solids) == 1 and revised.Volume < wall['shape'].Volume
    for attr in ['XMin', 'YMin', 'ZMin', 'XMax', 'YMax', 'ZMax']:
        assert abs(getattr(revised.BoundBox, attr) - getattr(b, attr)) < 1e-7
    body = doc.addObject('PartDesign::Body', 'Def_hull_engine_back')
    doc.Definitions.addObject(body)
    feature = body.newObject('PartDesign::Feature', 'CasingPassageHypothesis')
    feature.Shape = revised
    metadata(body, DefinitionId='hull_engine_back', Representation='assembly', Coverage='partial',
             SurveyIds=wall['target'].SurveyIds)
    obj = doc.addObject('App::Link', 'EngineBackPassageCandidate')
    doc.Root.addObject(obj)
    obj.setLink(body)
    metadata(obj, OccurrenceId='hull_engine_back', Subsystem=wall['system'])
    metadata(doc.Root, Scope='Two chain candidates, replacement castings and inferred M2003 casing passages; diagnostic only')
    doc.Definitions.Visibility = False
    doc.recompute()
    native = out / 'CasingPassageCandidate.FCStd'
    doc.saveAs(str(native))
    App.closeDocument(doc.Name)
    doc = App.openDocument(str(native))
    doc.recompute()
    new = leaves(doc.Root)
    assert len(new) == 505
    for item in new:
        assert item['shape'].isValid() and len(item['shape'].Solids) == 1
    replaced = set(prior['replaced_existing_occurrences']) | {'hull_engine_back'}
    context = [i for i in original if i['id'] not in replaced]
    physical = [i for i in context if i['representation'] == 'assembly'] + new
    boxes = np.array([[s.XMin, s.YMin, s.ZMin, s.XMax, s.YMax, s.ZMax]
                      for s in [i['shape'].BoundBox for i in physical]])
    ids = {i['id'] for i in new}
    internal = external = 0
    overlaps, neighbors = [], set()
    for first in new:
        bb = first['shape'].BoundBox
        bounds = np.array([bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax])
        near = np.where(np.all(boxes[:, :3] <= bounds[3:] + 1e-7, axis=1) &
                        np.all(boxes[:, 3:] >= bounds[:3] - 1e-7, axis=1))[0]
        for n in near:
            second = physical[n]
            if second['id'] in ids:
                if second['id'] <= first['id']:
                    continue
                internal += 1
            else:
                external += 1
                neighbors.add(second['id'])
            volume = first['shape'].common(second['shape']).Volume
            if volume > 1e-5:
                overlaps.append(dict(a=first['id'], b=second['id'], volume_mm3=volume))
    plate = next(i for i in new if i['id'] == 'hull_engine_back')
    old_ids = {pair['a'] for pair in prior['overlaps']}
    resolved_gaps = [dict(occurrence=i['id'], gap_mm=i['shape'].distToShape(plate['shape'])[0])
                     for i in new if i['id'] in old_ids]
    assert len(resolved_gaps) == 18 and all(i['gap_mm'] > 0 for i in resolved_gaps)
    hull_report = validate_hull(load(), context + new, out)
    views = [i for i in context if i['id'] in neighbors and not i['definition'].startswith('hull_')] + new
    shaded(views, out / 'passages_oblique.svg', (1, 1, .65),
           'Inferred chain-casing passages in M2003 | static candidate, casing not populated')
    shaded([plate], out / 'plate_elevation.svg', (1, 0, 0),
           'M2003 candidate | two inferred casing passages; documented station and stock retained')
    shaded(context + new, out / 'installed_isometric.svg', (1, 1, .65),
           'Standard tank with experimental chain and passage geometry | not promoted')
    assert fingerprint() == lock
    check_build(stage / 'build')
    assert all(sha(p) == hashes[str(p.relative_to(ROOT))] for p in inputs)
    write(out / 'report.json', dict(complete=True, passed=not overlaps, native_sha256=sha(native),
          authored_fingerprint=lock, tank_native_hashes=build['native_hashes'], input_sha256=hashes,
          new_native_occurrences=len(new), replaced_existing_occurrences=sorted(replaced),
          route_wall_crossings=crossings, inferred_openings=openings,
          wall_original_volume_mm3=wall['shape'].Volume, wall_candidate_volume_mm3=plate['shape'].Volume,
          outer_wall_bounds_unchanged=True, internal_candidate_pairs=internal,
          external_candidate_pairs=external, overlaps=overlaps, formerly_overlapping_part_clearances=resolved_gaps,
          hull_report='reports/hull_plates.json', hull_plate_occurrences=hull_report['plate_occurrences'],
          standard_assembly_modified=False, source_bom_reconciled=False,
          chain_casing_and_mounts_populated=False, historical_fit_qualified=False, visual_review_status='pending'))
    print('Casing passage candidate:', internal, 'internal,', external, 'external,', len(overlaps), 'overlaps', flush=True)
    sys.exit(0 if not overlaps else 1)
finally:
    runtime.close()
