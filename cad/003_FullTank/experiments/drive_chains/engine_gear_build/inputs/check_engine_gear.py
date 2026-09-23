"""Inspect saved gear geometry, joint interfaces and preservation independently."""
import argparse
from collections import Counter
import hashlib
import math
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent; STAGE = HERE.parents[1]; ROOT = STAGE.parents[1]
sys.path[:0] = [str(HERE), str(STAGE)]
from lib import runtime
from lib.evidence import read, write, sha
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, default=HERE/'engine_gear_build')
p.add_argument('--worker', action='store_true'); p.add_argument('--local-only', action='store_true')
a = p.parse_args(); out = a.candidate.resolve()
if not a.worker:
    cmd = [sys.executable, __file__, '--candidate', str(out), '--worker']
    if a.local_only: cmd.append('--local-only')
    with (out/'interface_check.log').open('w') as log:
        sys.exit(subprocess.run(cmd, env=runtime.environment(out/'check_runtime'), stdout=log, stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App
    import Part
    from lib.cad_build import leaves
    from lib.worker import placement_errors, check_build
    V = App.Vector; X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)
    native = out/'DrivetrainWithEngineGear.FCStd'; r = read(out/'report.json')
    assert sha(native) == r['native_sha256']
    doc = App.openDocument(str(native)); items = leaves(doc.Root); byid = {i['id']: i for i in items}
    origin = doc.TankLibertyEngine.Placement.Base
    c, pc, pd = r['controls'], r['parent_controls'], r['parent_datums']
    checks = []

    def ck(name, passed, detail=None):
        checks.append(dict(name=name, passed=bool(passed), detail=detail))
        if not passed: print('FAIL', name, detail, flush=True)

    def near(name, value, expected=0, tol=1e-5):
        ck(name, abs(value-expected) < tol, dict(actual=value, expected=expected, tolerance=tol))

    def local(n):
        s = byid[n]['shape'].copy(); s.translate(-origin); return s

    def runs(shape, x, radius, samples, material=True):
        flags = [shape.isInside(V(x, radius*math.cos(i*2*math.pi/samples), radius*math.sin(i*2*math.pi/samples)), 1e-7, False) == material for i in range(samples)]
        return sum(flags[i] and not flags[i-1] for i in range(samples))

    def cylinder(radius, start, end):
        delta = end-start; return Part.makeCylinder(radius, delta.Length, start, delta)

    def intersects(a, b):
        return all(getattr(a, k+'Min') <= getattr(b, k+'Max')+1e-7 and getattr(b, k+'Min') <= getattr(a, k+'Max')+1e-7 for k in ['X', 'Y', 'Z'])

    new = [n for n in byid if n.startswith('EngineGear_')]
    changed = ['EngineCrank_Forging', 'EngineCrank_ThrustNut']
    counts = Counter(byid[n]['definition'].removeprefix('engine_gear_') for n in new)
    ck('2153 unique physical occurrences', len(items) == len(byid) == 2153)
    ck('22 newly owned constituents', len(new) == 22 and set(new) == set(r['new_ids']))
    ck('selected component counts', counts == dict(gear=1, shim=1, bolt=6, nut=6, cotter=6, lock_screw=1, lock_wire=1), dict(counts))
    ck('two locally revised parent occurrences', set(r['changed_ids']) == set(changed))
    ck('hidden shared definition library', not doc.Definitions.Visibility)
    ck('affected shapes are valid single solids', all(byid[n]['shape'].isValid() and len(byid[n]['shape'].Solids) == 1 for n in new+changed))
    ck('gear and thrust lock owned by rotating assembly', all(doc.getObject(n) in doc.EngineRotatingAssembly.Group for n in ['EngineDrivingGear', 'EngineThrustNutLock']))
    for k, value in [('teeth', 33), ('mating_teeth', 22), ('bolt_count', 6), ('bolt_diameter', 7.9375), ('bolt_length', 22.225), ('cotter_diameter', 1.5875), ('cotter_length', 15.875)]:
        near('selected source control '+k, c[k], value)
    source = read(out/'inputs/engine_gear_sources.json')
    near('contrary handbook grip retained', source['conflicts']['HB199_printed_head_to_nut_mm'], 2.38125)
    ck('shim alternatives not installed together', counts['shim'] == 1 and doc.Def_EngineGear_shim.OriginalMark == 'LQ259A')
    gear, shim, shaft = local('EngineGear_DrivingBevel'), local('EngineGear_ThinShim'), local('EngineCrank_Forging')
    nut, screw, wire = local('EngineCrank_ThrustNut'), local('EngineGear_ThrustLockScrew'), local('EngineGear_ThrustLockWire')
    flange0, flange1 = pd['gear_flange_span']
    near('shim native thickness', shim.BoundBox.XLength, c['shim_stock'])
    near('shim touches flange', shim.distToShape(shaft)[0])
    near('gear touches shim', gear.distToShape(shim)[0])
    near('gear native back face', gear.BoundBox.XMin, flange1+c['shim_stock'])
    # Count crossings in native material, independent of generated tooth metadata.
    delta = math.atan2(33, 22)
    distance = math.hypot(33*c['module']/2, 22*c['module']/2)
    root = delta-math.atan(1.25*c['module']/distance)
    tip = delta+math.atan(c['module']/distance)
    apex = flange1+c['shim_stock']+distance*math.cos(root)+c['root_embed']
    station_radius = distance-c['face_width']/2
    station = apex-station_radius*math.cos(delta)
    measured = runs(gear, station, station_radius*math.sin(delta), 33*24)
    ck('33 saved bevel teeth', measured == 33, measured)
    surfaces = [f.Surface for f in gear.Faces if isinstance(f.Surface, Part.BSplineSurface)]
    cubic = sum(3 in [s.UDegree, s.VDegree] for s in surfaces)
    ck('saved cubic tooth flanks present', cubic >= 66, cubic)
    # Independently evaluate an ideal spherical involute at held-out parameters,
    # then measure to actual saved material surfaces at both radial stations.
    beta = math.asin(math.sin(delta)*math.cos(math.radians(c['pressure_angle_deg'])))
    def involute(theta):
        t = math.acos(min(1., math.cos(theta)/math.cos(beta)))
        return t/math.sin(beta)-math.atan(math.tan(t)/math.sin(beta)) if theta > beta else 0.
    half = math.pi/66-c['tooth_thinning']/(33*c['module'])
    residuals = []
    for radius in [distance-c['face_width']*.23, distance-c['face_width']*.77]:
        for sign in [-1, 1]:
            for j in range(11):
                theta = root+(tip-root)*(j+.37)/11
                angle = sign*(half+involute(delta)-involute(theta))-math.radians(90+pc['static_phase_deg']+12.5)
                point = V(apex-radius*math.cos(theta), radius*math.sin(theta)*math.cos(angle), radius*math.sin(theta)*math.sin(angle))
                residuals.append(gear.distToShape(Part.Vertex(point))[0])
    ck('held-out spherical involute residual below0.00002mm', max(residuals) < 2e-5, dict(max_mm=max(residuals), samples=len(residuals)))
    webfront = flange1+c['shim_stock']+c['web_stock']
    hubend = webfront+c['hub_length']
    ck('two estimated broad starting-claw lobes', runs(gear, hubend+c['claw_stock']/2, c['hub_radius']-2, 180) == 2)
    phase = math.radians(-90-pc['static_phase_deg']-12.5)
    ck('source indexed tooth follows reference crank phase', gear.isInside(V(station, station_radius*math.sin(delta)*math.cos(phase), station_radius*math.sin(delta)*math.sin(phase)), 1e-7, False))
    shim_void = cylinder(c['shim_bore_radius']-.1, V(flange1-.1,0,0), V(flange1+c['shim_stock']+.1,0,0))
    near('source86 broad central shim opening', abs(shim_void.common(shim).Volume))
    ck('twelve estimated internal spline slots', runs(gear, webfront+c['hub_length']/2, c['bore_radius']+c['spline_depth']/2, 288, False) == 12)
    through = cylinder(c['bore_radius']-.1, V(flange1-.1, 0, 0), V(hubend+c['claw_stock']+.1, 0, 0))
    near('gear central bore remains open', abs(through.common(gear).Volume))
    near('cotter source developed leg length', r['datums']['cotter']['total_leg_centerline_mm'], 15.875)
    grip = flange1-flange0+c['shim_stock']+c['web_stock']
    ck('selected grip conflict explicitly unresolved', abs(grip-2.38125) > 1 and 'grip' in ' '.join(source['decisions']))
    edit_zones = []
    for n in range(6):
        phi = n*math.pi/3; radial = V(0, math.sin(phi), math.cos(phi)); center = radial*c['bolt_circle']
        name = str(n+1)
        group = doc.getObject('EngineGearBoltSet'+name)
        t, angle = placement_errors(group.getGlobalPlacement(), App.Placement(origin+V(flange0, 0, 0)+center, App.Rotation(X, -n*60)))
        ck('boltset'+name+' full frame and three constituents', len(leaves(group)) == 3 and t < 1e-6 and angle < 1e-8)
        bolt = local('EngineGear_Bolt'+name); fastnut = local('EngineGear_Nut'+name); pin = local('EngineGear_Cotter'+name)
        near('bolt'+name+' source underhead length', bolt.BoundBox.XMax-flange0, 22.225)
        near('bolt'+name+' head seats flange', bolt.distToShape(shaft)[0])
        near('nut'+name+' seats gear web', fastnut.distToShape(gear)[0])
        near('nut'+name+' source bolt end exposure', bolt.BoundBox.XMax-fastnut.BoundBox.XMax, 22.225-grip-c['nut_stock'])
        # The pin must cross the drilled shank and open castellations.
        near('cotter'+name+' clears bolt', abs(pin.common(bolt).Volume))
        near('cotter'+name+' clears nut', abs(pin.common(fastnut).Volume))
        witness = cylinder(c['bolt_diameter']/2+.01, V(flange0+.1, center.y, center.z), V(flange1+c['shim_stock']+c['web_stock']-.1, center.y, center.z))
        near('bolt'+name+' receivers have radial clearance', abs(witness.common(shaft).Volume)+abs(witness.common(shim).Volume)+abs(witness.common(gear).Volume))
        edit_zones.append(cylinder(c['bolt_diameter']/2+c['receiver_gap']+.01, V(flange0-.2, center.y, center.z), V(flange1+.2, center.y, center.z)))
    # Wire material follows a connected route from cross-hole into a real slot.
    phi = math.radians(c['lock_angle_deg']); radial = V(0, math.cos(phi), math.sin(phi))
    base = V(c['lock_station'], 0, 0)
    for fraction in [0, .13, .39, .73, 1]:
        theta = phi+(2*math.pi-phi)*fraction
        point = base+V(0, c['wire_pitch_radius']*math.cos(theta), c['wire_pitch_radius']*math.sin(theta))
        ck('wire arc material '+str(fraction), wire.isInside(point, 1e-7, False))
    anchor = base+V(0, c['wire_anchor_radius']+.2, c['wire_end_bend_radius'])
    ck('wire anchor occupies existing nut slot', wire.isInside(anchor, 1e-7, False) and not nut.isInside(anchor, 1e-7, True))
    near('wire passes screw without interference', abs(wire.common(screw).Volume))
    ck('wire crosses head hole', wire.isInside(base+radial*c['wire_pitch_radius'], 1e-7, False))
    ck('lock receiver remains blind in shaft', shaft.isInside(base+radial*(c['lock_tip_radius']-c['lock_blind_gap']-.2), 1e-7, False))
    near('screw shank clears nut and shaft', abs(screw.common(nut).Volume)+abs(screw.common(shaft).Volume))
    lock_zone = cylinder(c['lock_screw_diameter']/2+c['receiver_gap']+.01,
                         base+radial*(c['lock_tip_radius']-.2), base+radial*(c['lock_seat_radius']+2))
    edit_zones.append(lock_zone)
    print('Checking parent material preservation.', flush=True)
    pn = HERE/'engine_shaft_fittings_build/DrivetrainWithEngineShaftFittings.FCStd'
    assert sha(pn) == r['parent_native_sha256']
    parent = App.openDocument(str(pn)); old = {i['id']: i for i in leaves(parent.Root)}
    def brep_hashes(path):
        with zipfile.ZipFile(path) as archive:
            tree = ET.fromstring(archive.read('Document.xml'))
            return {obj.get('name'): hashlib.sha256(archive.read(prop.get('file'))).hexdigest()
                for obj in tree.findall('./ObjectData/Object') for prop in obj.findall('./Properties/Property[@name="Shape"]/Part') if prop.get('file')}
    previous, current = brep_hashes(pn), brep_hashes(native)
    compared, failed, fallback = set(), [], []
    for n, item in old.items():
        if n in changed: continue
        t, angle = placement_errors(item['shape'].Placement, byid[n]['shape'].Placement)
        if t >= 1e-6 or angle >= 1e-8: failed.append(n+' frame')
        target, now = item['target'], byid[n]['target']
        if target.Name in compared: continue
        compared.add(target.Name)
        if previous.get(target.Name) and previous.get(target.Name) == current.get(now.Name): continue
        fallback.append(target.Name)
        missing, added = abs(target.Shape.cut(now.Shape).Volume), abs(now.Shape.cut(target.Shape).Volume)
        if max(missing, added) >= 1e-5: failed.append(dict(definition=target.Name, missing=missing, added=added))
    ck('2129 parent occurrences preserve material and frames', len(old)-2 == 2129 and not failed,
       dict(failures=failed, unique_definitions=len(compared), material_fallback=fallback))
    for name, after, zones in [('shaft', shaft, edit_zones), ('thrust_nut', nut, [lock_zone])]:
        original = parent.getObject('Def_EngineCrank_'+name).Shape
        allowed = Part.makeCompound(zones)
        near(name+' preserved outside local receivers', abs(original.cut(after).cut(allowed).Volume))
        near(name+' has no added material', abs(after.cut(original).Volume))
    write(out/'independent_checks.json', dict(passed=all(x['passed'] for x in checks), checks=checks,
        native_sha256=sha(native), checker_sha256=sha(Path(__file__)),
        scope='Static source-informed reconstruction; mating pinion backlash, historical claw/spline counts, actual shim stack and locking performance remain unqualified'))
    candidates = dict(byid)
    if not a.local_only:
        standard = check_build(STAGE/'build'); tank = App.openDocument(standard['build']['top_document'])
        for item in leaves(tank.Root):
            if item['representation'] != 'layout' and item['id'] not in byid: candidates['Standard_'+item['id']] = item
    boxes = {n: i['shape'].BoundBox for n, i in candidates.items()}
    pairs, seen = [], set()
    for n in sorted(new+changed):
        for other in sorted(candidates):
            pair = tuple(sorted([n, other]))
            if n == other or pair in seen or not intersects(boxes[n], boxes[other]): continue
            seen.add(pair)
            volume = abs(byid[n]['shape'].common(candidates[other]['shape']).Volume)
            pairs.append(dict(a=n, b=other, overlap_mm3=volume, passed=volume < 1e-5))
            if len(pairs) % 25 == 0:
                write(out/'material_progress.json', dict(checked=len(pairs), failed=[x for x in pairs if not x['passed']]))
                print('Material pairs', len(pairs), flush=True)
    failures = [x for x in pairs if not x['passed']]
    write(out/'material_checks.json', dict(passed=not failures, native_sha256=sha(native), pairs=pairs,
        overlaps=failures, standard_context_checked=not a.local_only))
    print(len(checks), 'independent;', len(pairs), 'material pairs;', len(failures), 'overlaps.', flush=True)
    assert all(x['passed'] for x in checks) and not failures
finally:
    runtime.close()
