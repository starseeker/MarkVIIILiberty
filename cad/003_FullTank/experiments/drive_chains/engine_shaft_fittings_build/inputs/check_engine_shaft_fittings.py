"""Inspect saved closure ownership, material interfaces and connected oil routes."""
import argparse
from collections import Counter
import hashlib
import math
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
STAGE = HERE.parents[1]
ROOT = STAGE.parents[1]
sys.path[:0] = [str(HERE), str(STAGE)]
from lib import runtime
from lib.evidence import read, write, sha

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, default=HERE/'engine_shaft_fittings_build')
p.add_argument('--worker', action='store_true')
p.add_argument('--local-only', action='store_true')
a = p.parse_args()
out = a.candidate.resolve()
if not a.worker:
    command = [sys.executable, __file__, '--candidate', str(out), '--worker']
    if a.local_only:
        command.append('--local-only')
    with (out/'interface_check.log').open('w') as log:
        sys.exit(subprocess.run(command, env=runtime.environment(out/'check_runtime'),
                               stdout=log, stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App
    import Part
    from lib.cad_build import leaves
    from lib.worker import placement_errors, check_build

    V = App.Vector
    X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)
    r = read(out/'report.json')
    native = out/'DrivetrainWithEngineShaftFittings.FCStd'
    assert sha(native) == r['native_sha256']
    doc = App.openDocument(str(native))
    items = leaves(doc.Root)
    byid = {i['id']: i for i in items}
    c, pc, cc, pd = r['controls'], r['parent_controls'], r['case_controls'], r['parent_datums']
    origin = doc.TankLibertyEngine.Placement.Base
    checks = []

    def ck(name, passed, detail=None):
        checks.append(dict(name=name, passed=bool(passed), detail=detail))
        if not passed:
            print('FAIL', name, detail, flush=True)

    def near(name, actual, expected=0, tol=1e-5):
        ck(name, abs(actual-expected) < tol, dict(actual=actual, expected=expected, tolerance=tol))

    def local(name):
        s = byid[name]['shape'].copy()
        s.translate(-origin)
        return s

    def cylinder(radius, start, end):
        delta = end-start
        return Part.makeCylinder(radius, delta.Length, start, delta)

    def intersects(a, b):
        return all(getattr(a, k+'Min') <= getattr(b, k+'Max')+1e-7 and
                   getattr(b, k+'Min') <= getattr(a, k+'Max')+1e-7 for k in ['X', 'Y', 'Z'])

    shaft = local('EngineCrank_Forging')
    new = [n for n in byid if n.startswith('ShaftClosure_')]
    expected_counts = dict(main_cap=11, pin_cap=12, gear_cap=1, nose_plug=1, oil_plug=6,
        main_gasket=11, pin_gasket=12, gear_gasket=1, small_gasket=24, main_stud=5,
        pin_stud=6, gear_stud=1, plain_nut=12, castle_nut=12, washer=12, cotter=12)
    counts = Counter(byid[n]['definition'].removeprefix('shaft_closure_') for n in new)
    ck('2131 unique physical occurrences', len(items) == len(byid) == 2131)
    ck('139 newly owned constituents', len(new) == 139 and set(new) == set(r['new_ids']))
    ck('source-selected component counts', counts == expected_counts, dict(counts))
    ck('one revised forging', r['changed_ids'] == ['EngineCrank_Forging'])
    ck('closures owned by rotating assembly', doc.EngineShaftClosures in doc.EngineRotatingAssembly.Group)
    ck('definitions hidden', not doc.Definitions.Visibility)
    ck('all affected shapes valid with one solid', all(byid[n]['shape'].isValid() and
       len(byid[n]['shape'].Solids) == 1 for n in new+['EngineCrank_Forging']))
    for key, expected in [('stud_diameter', 9.525), ('main_stud_length', 102.39375),
                          ('pin_stud_length', 115.09375), ('coarse_thread_length', 17.4625),
                          ('fine_thread_length', 12.7), ('cotter_diameter', 2.38125), ('cotter_length', 15.875)]:
        near('source '+key, c[key], expected)
    near('source cotter developed leg length', r['datums']['cotter']['total_leg_centerline_mm'], 15.875)
    # Recompute stations/recesses independently of the generator's pair datums.
    rows = [cc['nose_to_first_row']+i*165.1 for i in range(7)]
    play = pc['journal_endplay']/2
    web = pc['web_stock']
    stack = 2*(c['large_gasket_stock']+c['cap_stock']+c['small_gasket_stock']) + c['plain_nut_stock'] + c['washer_stock'] + c['castle_nut_stock'] + 2*c['stud_end_exposure']
    main_recess = (49+2*play+2*web+stack-102.39375)/2
    pairs = []
    for i in range(1, 6):
        pairs.append(('Main%d' % (i+1), 'main', rows[i]-24.5-play-web,
                      rows[i]+24.5+play+web, V(), 0, main_recess, main_recess))
    for i, offset in enumerate([0, -120, 120, 120, -120, 0]):
        phase = pc['static_phase_deg']+offset
        angle = math.radians(phase)
        center = V(0, 88.9*math.sin(angle), 88.9*math.cos(angle))
        left, right = rows[i]+24.5+play, rows[i+1]-24.5-play
        left_recess = right-left+stack-115.09375-c['pin_rear_recess']
        pairs.append(('Pin%d' % (6-i), 'pin', left, right, center, -phase, left_recess, c['pin_rear_recess']))
    pairs.append(('Gear', 'gear', rows[-1]-24.5-play-web, pd['gear_flange_span'][1],
                  V(), 0, main_recess, c['gear_recess']))
    zones = []
    for name, family, left, right, center, roll, lr, rr in pairs:
        prefix = 'ShaftClosure_'+name+'_'
        group = doc.getObject('EngineShaftClosure_'+name)
        members = leaves(group)
        ck(name+' eleven physical constituents', len(members) == 11)
        expected_frame = App.Placement(origin+center, App.Rotation(X, roll))
        t, angle = placement_errors(group.getGlobalPlacement(), expected_frame)
        ck(name+' composed group frame', t < 1e-6 and angle < 1e-8, [t, angle])
        stud = local(prefix+'Stud')
        # An X-axis roll changes no axial length or radial distance.
        bb = stud.optimalBoundingBox(False)
        expected_length = {'main': 102.39375, 'pin': 115.09375}.get(family, right-left-lr-rr+stack)
        near(name+' stud axial length', bb.XLength, expected_length)
        radius = 9.525/2
        near(name+' stud diameter Y', bb.YLength, 9.525)
        near(name+' stud diameter Z', bb.ZLength, 9.525)
        plain, castle = local(prefix+'PlainNut'), local(prefix+'CastleNut')
        pb, cb = plain.optimalBoundingBox(False), castle.optimalBoundingBox(False)
        ck(name+' nuts lie on their respective thread envelopes',
           pb.XMin >= bb.XMin-1e-6 and pb.XMax <= bb.XMin+17.4625+1e-6 and
           cb.XMin >= bb.XMax-12.7-1e-6 and cb.XMax <= bb.XMax+1e-6)
        for side, seat, edge, kind in [('Left', left+lr, left, 'main' if family == 'gear' else family),
                                       ('Right', right-rr, right, family)]:
            cap, gasket = local(prefix+side+'Cap'), local(prefix+side+'Gasket')
            seal = local(prefix+side+'Seal')
            near(name+side+' cap contacts gasket', cap.distToShape(gasket)[0])
            near(name+side+' gasket contacts seat', gasket.distToShape(shaft)[0])
            near(name+side+' small gasket contacts cap', seal.distToShape(cap)[0])
            near(name+side+' stud clearance through cap', cap.distToShape(stud)[0], c['stud_bore_gap'])
            start, end = (edge-1.1, seat+.1) if side == 'Left' else (seat-.1, edge+1.1)
            zones.append(cylinder(c[kind+'_cap_radius']+c['radial_fit_gap']+.1,
                                  V(start, center.y, center.z), V(end, center.y, center.z)))
        for lhs, rhs in [('LeftSeal', 'PlainNut'), ('RightSeal', 'Washer'), ('Washer', 'CastleNut')]:
            near(name+' seated '+lhs+'/'+rhs, local(prefix+lhs).distToShape(local(prefix+rhs))[0])
        cotter = local(prefix+'Cotter')
        ck(name+' cotter traverses stud', cotter.BoundBox.XMin > cb.XMin and cotter.BoundBox.XMax < cb.XMax,
           dict(cotter_x=[cotter.BoundBox.XMin, cotter.BoundBox.XMax], nut_x=[cb.XMin, cb.XMax]))
    print('Closure interfaces checked; checking oil routes.', flush=True)
    # Finite-radius continuous witnesses enter each rear main-journal oil hole,
    # pass around its axial stud, cross the rear web, pass around the pin stud,
    # and reach the radial big-end outlet. These are geometric clearance checks,
    # not a fluid-flow or pressure-sealing qualification.
    material = {'EngineCrank_Forging': shaft, **{n: local(n) for n in new}}
    for i, offset in enumerate([0, -120, 120, 120, -120, 0]):
        phase = math.radians(pc['static_phase_deg']+offset)
        u = V(0, math.sin(phase), math.cos(phase))
        tangent = V(0, math.cos(phase), -math.sin(phase))
        row = rows[i+1]
        wx = row-24.5-play-web/2
        px = (rows[i]+rows[i+1])/2
        rho = 8.
        points = [V(row, 0, -34.3375), V(row, 0, -rho)]
        delta = (phase-math.pi+math.pi) % (2*math.pi)-math.pi
        points += [V(row, rho*math.sin(math.pi+delta*j/12), rho*math.cos(math.pi+delta*j/12)) for j in range(1, 13)]
        points += [V(wx, 0, 0)+u*rho, V(wx, 0, 0)+u*(88.9-rho)]
        points += [V(wx, 0, 0)+u*88.9 + (-u*math.cos(math.pi*j/12)+tangent*math.sin(math.pi*j/12))*rho for j in range(1, 13)]
        points += [V(px, 0, 0)+u*(88.9+rho), V(px, 0, 0)+u*(88.9+pc['crankpin_diameter']/2+1)]
        segments = [cylinder(.65, p0, p1) for p0, p1 in zip(points, points[1:]) if (p1-p0).Length > 1e-7]
        segments += [Part.makeSphere(.65, point) for point in points[1:-1]]
        witness = Part.makeCompound(segments)
        collisions = {}
        for n, shape in material.items():
            if intersects(witness.BoundBox, shape.BoundBox):
                v = abs(witness.common(shape).Volume)
                if v >= 1e-5:
                    collisions[n] = v
        ck('continuous oil route to cylinder pair%d' % (6-i), not collisions, collisions)
        face = V(wx, 0, 0)+u*(88.9+pc['web_pin_radius']-c['small_plug_recess'])
        plug = material['ShaftClosure_OilPlug%d' % (6-i)]
        inside = face-u*(c['small_plug_length']/2)
        ck('oil access%d capped with material' % (6-i), plug.isInside(inside, 1e-7, False))
        near('oil access%d seated bottom' % (6-i), plug.distToShape(shaft)[0])
        middle = plug.common(cylinder(c['small_plug_radius']+1, inside-u*.1, inside+u*.1))
        ck('oil access%d clearance witness is one solid' % (6-i), middle.isValid() and len(middle.Solids) == 1)
        near('oil access%d radial receiver clearance' % (6-i), middle.distToShape(shaft)[0], c['radial_fit_gap'])
        zones.append(cylinder(pc['oil_drill_radius']+.1, V(wx, 0, 0), V(wx, 0, 0)+u*(88.9+pc['web_pin_radius']+1.1)))
        zones.append(cylinder(c['small_plug_radius']+c['radial_fit_gap']+.1,
            face-u*(c['small_plug_length']+.1), face+u*(c['small_plug_recess']+1.1)))
    near('nose plug seats radially', shaft.distToShape(material['ShaftClosure_NosePlug'])[0])
    nose_end = rows[0]+24.5+play+web
    ck('nose inner termination material', shaft.isInside(V(nose_end-c['nose_blind_stock']/2, 0, 0), 1e-7, False))
    ck('first throw has no fictitious axial bar', not shaft.isInside(V((rows[0]+rows[1])/2, 0, 0), 1e-7, False))
    normal = V(*pd['key_screw_normal'])
    receiver_bottom = V(*pd['key_center'])-normal*(pc['key_screw_length']+.1)
    ck('key screw receiver blind floor retained', shaft.isInside(receiver_bottom-normal*.2, 1e-7, False))
    # Preserve exact serialized BRep definitions wherever available; if save
    # normalization differs, compare actual material in both directions instead.
    print('Checking unchanged parent definitions and placements.', flush=True)
    pn = HERE/'engine_crankshaft_build/DrivetrainWithEngineCrankshaft.FCStd'
    assert sha(pn) == r['parent_native_sha256']
    parent = App.openDocument(str(pn))
    old = {i['id']: i for i in leaves(parent.Root)}

    def brep_hashes(path):
        with zipfile.ZipFile(path) as archive:
            tree = ET.fromstring(archive.read('Document.xml'))
            return {obj.get('name'): hashlib.sha256(archive.read(prop.get('file'))).hexdigest()
                    for obj in tree.findall('./ObjectData/Object')
                    for prop in obj.findall('./Properties/Property[@name="Shape"]/Part') if prop.get('file')}

    previous_hashes, current_hashes = brep_hashes(pn), brep_hashes(native)
    compared, failed, changed_serialization = set(), [], []
    for n, item in old.items():
        if n == 'EngineCrank_Forging':
            continue
        t, angle = placement_errors(item['shape'].Placement, byid[n]['shape'].Placement)
        if t >= 1e-6 or angle >= 1e-8:
            failed.append(n+' placement')
        target, current = item['target'], byid[n]['target']
        if target.Name in compared:
            continue
        compared.add(target.Name)
        if previous_hashes.get(target.Name) and previous_hashes.get(target.Name) == current_hashes.get(current.Name):
            continue
        changed_serialization.append(target.Name)
        missing = abs(target.Shape.cut(current.Shape).Volume)
        added = abs(current.Shape.cut(target.Shape).Volume)
        if missing >= 1e-5 or added >= 1e-5:
            failed.append(dict(definition=target.Name, missing_mm3=missing, added_mm3=added))
    ck('1991 parent occurrences preserve material and placement', len(old)-1 == 1991 and not failed,
       dict(failures=failed, unique_definitions=len(compared), material_fallback=changed_serialization))
    tip = pd['taper']['rear']-pc['output_thread_length']
    for start, end in [(tip-.1, c['nose_bore_transition_start']+c['nose_bore_transition_length']+.1),
                       (nose_end-c['nose_blind_stock']-.1, nose_end+.1)]:
        zones.append(cylinder(pc['main_hollow_radius']+.2, V(start, 0, 0), V(end, 0, 0)))
    allowed = Part.makeCompound(zones)
    original = parent.Def_EngineCrank_shaft.Shape
    near('shaft original material outside closure edits preserved', abs(original.cut(shaft).cut(allowed).Volume))
    near('shaft has no extra material outside closure edits', abs(shaft.cut(original).cut(allowed).Volume))
    write(out/'independent_checks.json', dict(passed=all(x['passed'] for x in checks), checks=checks,
        native_sha256=sha(native), checker_sha256=sha(Path(__file__)),
        scope='Static source-selected closure reconstruction; thread matching, pressure sealing and source profile fit remain unqualified'))
    candidates = dict(byid)
    if not a.local_only:
        standard = check_build(STAGE/'build')
        tank = App.openDocument(standard['build']['top_document'])
        for item in leaves(tank.Root):
            if item['representation'] != 'layout' and item['id'] not in byid:
                candidates['Standard_'+item['id']] = item
    boxes = {n: item['shape'].BoundBox for n, item in candidates.items()}
    pairs_checked, seen = [], set()
    for n in sorted(new+['EngineCrank_Forging']):
        for other in sorted(candidates):
            pair = tuple(sorted([n, other]))
            if n == other or pair in seen or not intersects(boxes[n], boxes[other]):
                continue
            seen.add(pair)
            volume = abs(byid[n]['shape'].common(candidates[other]['shape']).Volume)
            pairs_checked.append(dict(a=n, b=other, overlap_mm3=volume, passed=volume < 1e-5))
            if len(pairs_checked) % 25 == 0:
                write(out/'material_progress.json', dict(checked=len(pairs_checked), failed=[x for x in pairs_checked if not x['passed']]))
                print('Material pairs', len(pairs_checked), flush=True)
    failures = [x for x in pairs_checked if not x['passed']]
    write(out/'material_checks.json', dict(passed=not failures, native_sha256=sha(native),
        pairs=pairs_checked, overlaps=failures, standard_context_checked=not a.local_only))
    print(len(checks), 'independent;', len(pairs_checked), 'material pairs;', len(failures), 'overlaps.', flush=True)
    assert all(x['passed'] for x in checks) and not failures
finally:
    runtime.close()
