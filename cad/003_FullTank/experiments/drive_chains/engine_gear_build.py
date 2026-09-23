"""Install the source-owned driving gear and thrust lock in the saved engine."""
import argparse
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
STAGE = HERE.parents[1]
ROOT = STAGE.parents[1]
sys.path[:0] = [str(HERE), str(STAGE)]
from lib import runtime
from lib.evidence import read, write, sha

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--output', type=Path, default=HERE/'engine_gear_build')
p.add_argument('--controls', type=Path, default=HERE/'engine_gear_controls.json')
p.add_argument('--worker', action='store_true')
a = p.parse_args()
out = a.output.resolve(); out.mkdir(parents=True, exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable, __file__, '--output', str(out), '--controls',
            str(a.controls.resolve()), '--worker'], env=runtime.environment(out),
            stdout=log, stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App
    import Part
    from lib.cad_build import leaves, metadata, shape_signature
    from lib.worker import same_shape, placement_errors
    from engine_gear_parts import parts

    parent = HERE/'engine_shaft_fittings_build'
    pn = parent/'DrivetrainWithEngineShaftFittings.FCStd'
    pr = read(parent/'report.json')
    assert sha(pn) == pr['native_sha256']
    source = read(HERE/'engine_gear_sources.json')
    c = read(a.controls)['controls']
    for rel, digest in source['source_assets'].items():
        assert sha(ROOT/rel) == digest, rel
    inputs = {}; (out/'inputs').mkdir(exist_ok=True)
    for path in [Path(__file__), a.controls.resolve(), HERE/'engine_gear_parts.py', HERE/'engine_gear_sources.json',
                 HERE/'transmission_bevel_tooth.py', HERE/'engine_crankshaft_parts.py',
                 HERE/'engine_crossmember_parts.py', HERE/'transmission_stud_parts.py',
                 HERE/'transmission_input_installation_parts.py', HERE/'transmission_core_parts.py']:
        (out/'inputs'/path.name).write_bytes(path.read_bytes())
        inputs[str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)] = sha(path)
    write(out/'inputs/parent_report.json', pr)
    doc = App.openDocument(str(pn))
    old = {i['id']: i for i in leaves(doc.Root)}
    assert len(old) == 2131
    before = {n: (shape_signature(i['shape']), App.Placement(i['shape'].Placement)) for n, i in old.items()}
    print('Constructing driving bevel, hardware and thrust lock.', flush=True)
    shapes, occ, rows, d, zones = parts(c, pr, doc.Def_EngineCrank_shaft.Tip.Shape,
        doc.Def_EngineCrank_thrust_nut.Tip.Shape,
        lambda n, s: print(n, s.isValid(), len(s.Solids), flush=True))
    d['origin'] = list(doc.TankLibertyEngine.Placement.Base)
    for key, name in [('shaft', 'Def_EngineCrank_shaft'), ('thrust_nut', 'Def_EngineCrank_thrust_nut')]:
        body = doc.getObject(name); body.Tip.Shape = shapes[key]
        metadata(body, GearInstallationInputs=c,
            ParameterUpdate='Regenerate engine_gear_build.py from controls and frozen shaft-fittings parent',
            GearInstallationNotes='Local driving-gear bolt bores and/or radial thrust-lock receiver only; unaffected parent geometry retained.')
    groups = {}
    for name in ['EngineDrivingGear', 'EngineThrustNutLock']:
        obj = doc.addObject('App::Part', name); doc.EngineRotatingAssembly.addObject(obj)
        metadata(obj, QuantityRole='Nonphysical assembly container', Subsystem='Powerplant', Coverage='partial')
        groups[name] = obj
    for row in rows:
        obj = doc.addObject('App::Part', row['name']); groups[row['parent']].addObject(obj)
        obj.Placement = App.Placement(App.Vector(*row['xyz']), App.Rotation(*row['rotation']))
        metadata(obj, QuantityRole='Nonphysical bolt-set container', Subsystem='Powerplant', Coverage='partial')
        groups[obj.Name] = obj
    ownership = dict(gear=('LQ258A', 'SNL:99:013'), shim=('LQ259A', 'SNL:217:004'),
        bolt=('LQ262A', 'SNL:23:016'), nut=('LQ51A', 'SNL:23:017'), cotter=('Unmarked1/16x5/8in split pin', 'SNL:23:018'),
        lock_screw=('LQ276A', 'SNL:202:017'), lock_wire=('LQ277A', 'SNL:212:010'))
    records = {r['record_id']: r for r in source['records']}
    definitions = {}
    for key in sorted(ownership):
        body = doc.addObject('PartDesign::Body', 'Def_EngineGear_'+key); doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature', 'ReconstructedMachining').Shape = shapes[key]
        mark, rid = ownership[key]
        metadata(body, DefinitionId='engine_gear_'+key, OriginalMark=mark, SurveyIds=records[rid]['part_ids'],
            SourceRecord=rid, Representation='assembly', Coverage='partial', Subsystem='Powerplant', GeometryInputs=c,
            ParameterUpdate='Regenerate engine_gear_build.py from controls',
            ReconstructionNotes='Conditional Liberty bevel dimensions; estimated profiles, claw/spline counts, wire route and smooth thread envelopes. Conflicting HB bolt grip retained; see engine_gear_sources.json. Mating gears and final shim stack pending.')
        definitions[key] = body.Name
    for row in occ:
        obj = doc.addObject('App::Link', row['name']); groups[row['assembly']].addObject(obj)
        obj.setLink(doc.getObject(definitions[row['key']]))
        obj.LinkPlacement = App.Placement(App.Vector(*row['xyz']), App.Rotation(*row['rotation']))
        metadata(obj, OccurrenceId=row['name'], Subsystem='Powerplant', QuantityRole='One installed physical constituent')
    metadata(doc.TankLibertyEngine, ReconstructionNotes='Crankcase, crankshaft, bearings, shaft closures, main bevel and thrust lock populated as development geometry. Mating distribution gears, cylinders, rods, valve gear and services remain pending.')
    doc.Definitions.Visibility = False; doc.recompute()
    App.ParamGet('User parameter:BaseApp/Preferences/Document').SetInt('CountBackupFiles', 0)
    native = out/'DrivetrainWithEngineGear.FCStd'; doc.saveAs(str(native)); App.closeDocument(doc.Name)
    doc = App.openDocument(str(native)); items = leaves(doc.Root); byid = {i['id']: i for i in items}
    new = [o['name'] for o in occ]; changed = ['EngineCrank_Forging', 'EngineCrank_ThrustNut']
    assert len(items) == len(byid) == 2153 and len(new) == 22
    for n, (sig, pl) in before.items():
        if n in changed:
            continue
        t, angle = placement_errors(pl, byid[n]['shape'].Placement)
        assert same_shape(sig, shape_signature(byid[n]['shape'])) and t < 1e-6 and angle < 1e-8, n
    for n in new+changed:
        assert byid[n]['shape'].isValid() and len(byid[n]['shape'].Solids) == 1, n
    print('Native saved/reopened with 2153 physical occurrences; exporting STEP.', flush=True)
    order = list(definitions.values())+['Def_EngineCrank_shaft', 'Def_EngineCrank_thrust_nut']
    Part.setStaticValue('write.surfacecurve.mode', 1)
    Part.makeCompound([doc.getObject(n).Shape for n in order]).exportStep(str(out/'EngineGearDefinitions.step'))
    Part.makeCompound([byid[n]['shape'] for n in new+changed]).exportStep(str(out/'EngineGearInstallation.step'))
    write(out/'definition_order.json', order)
    write(out/'report.json', dict(status='development_hypothesis_not_qualified', native_sha256=sha(native),
        parent_native_sha256=sha(pn), input_hashes=inputs, controls=c, parent_controls=pr['parent_controls'],
        case_controls=pr['case_controls'], parent_datums=pr['parent_datums'], datums=d,
        occurrences=occ, assemblies=rows, new_ids=new, changed_ids=changed, exchange_ids=new+changed,
        native_occurrences=len(items), new_definitions=len(definitions), unchanged_parent_occurrences=2129,
        standard_native_hashes=pr['standard_native_hashes'], standard_assembly_modified=False,
        historically_qualified=False, complete_engine=False, complete_tank=False,
        pending='Independent native, spline, interface, STEP and visual checks; mating distribution gears and final shim stack; remaining engine systems; combined qualification and standard integration.',
        artifact_hashes={f.name: sha(f) for f in out.glob('*.step')}, export_settings={'write.surfacecurve.mode': 1},
        headless=not App.GuiUp, freecad=App.Version(), occ=Part.OCC_VERSION))
    print('Complete:22 new,2 locally revised,2129 preserved occurrences.', flush=True)
finally:
    runtime.close()
