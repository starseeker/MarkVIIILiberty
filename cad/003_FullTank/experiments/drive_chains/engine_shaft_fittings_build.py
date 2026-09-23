"""Install source-owned shaft closures in the saved crankshaft development assembly."""
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
p.add_argument('--output', type=Path, default=HERE/'engine_shaft_fittings_build')
p.add_argument('--controls', type=Path, default=HERE/'engine_shaft_fittings_controls.json')
p.add_argument('--worker', action='store_true')
a = p.parse_args()
out = a.output.resolve()
out.mkdir(parents=True, exist_ok=True)
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
    from engine_shaft_fittings_parts import parts

    parent = HERE/'engine_crankshaft_build'
    pn = parent/'DrivetrainWithEngineCrankshaft.FCStd'
    pr = read(parent/'report.json')
    assert sha(pn) == pr['native_sha256']
    source = read(HERE/'engine_shaft_fittings_sources.json')
    c = read(a.controls)['controls']
    for rel, digest in source['source_assets'].items():
        assert sha(ROOT/rel) == digest, rel
    inputs = {}
    (out/'inputs').mkdir(exist_ok=True)
    for path in [Path(__file__), a.controls.resolve(), HERE/'engine_shaft_fittings_parts.py',
                 HERE/'engine_shaft_fittings_sources.json', HERE/'engine_crankshaft_parts.py',
                 HERE/'engine_crossmember_parts.py', HERE/'transmission_stud_parts.py',
                 HERE/'transmission_input_installation_parts.py']:
        (out/'inputs'/path.name).write_bytes(path.read_bytes())
        inputs[str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)] = sha(path)
    doc = App.openDocument(str(pn))
    old = {i['id']: i for i in leaves(doc.Root)}
    assert len(old) == 1992
    before = {n: (shape_signature(i['shape']), App.Placement(i['shape'].Placement)) for n, i in old.items()}
    print('Constructing shaft closures and retaining sets.', flush=True)
    shapes, occ, assembly_rows, d, zones = parts(c, pr, doc.Def_EngineCrank_shaft.Tip.Shape,
        lambda name, s: print(name, s.isValid(), len(s.Solids), flush=True))
    d['origin'] = list(doc.TankLibertyEngine.Placement.Base)
    shaft = doc.Def_EngineCrank_shaft
    shaft.Tip.Shape = shapes['shaft']
    metadata(shaft, GeometryInputs=dict(crankshaft=pr['controls'], closures=c),
             ParameterUpdate='Regenerate engine_shaft_fittings_build.py from controls and frozen crankshaft parent',
             ReconstructionNotes='Inherited shaft with source-owned plug receivers, inferred blind nose termination, reduced nose cavity and capped oil-drill entries. Profiles and recesses are estimates; source conflicts retained in fittings dossier.')
    group = doc.addObject('App::Part', 'EngineShaftClosures')
    doc.EngineRotatingAssembly.addObject(group)
    metadata(group, QuantityRole='Nonphysical assembly container', Subsystem='Powerplant', Coverage='partial')
    groups = {group.Name: group}
    for row in assembly_rows:
        obj = doc.addObject('App::Part', row['name'])
        group.addObject(obj)
        obj.Placement = App.Placement(App.Vector(*row['xyz']), App.Rotation(*row['rotation']))
        metadata(obj, QuantityRole='Nonphysical assembly container', Subsystem='Powerplant', Coverage='partial',
                 ReconstructionNotes='Two closures with gaskets plus seven constituents of one retaining stud set; detailed source composition selected despite nut-count conflict.')
        groups[obj.Name] = obj
    ownership = {
        'main_cap': ('LQ265A', 'SNL:156:003'), 'pin_cap': ('LQ266A', 'SNL:156:001'),
        'gear_cap': ('LQ263A', 'SNL:156:002'), 'nose_plug': ('LQ256A', 'SNL:156:004'),
        'oil_plug': ('LQ257A', 'SNL:212:023'), 'gear_gasket': ('LQ264A', 'SNL:97:031'),
        'main_gasket': ('Unmarked 1-3/8in gasket', 'SNL:212:026'),
        'pin_gasket': ('Unmarked 1-1/4in gasket', 'SNL:212:025'),
        'small_gasket': ('Unmarked 3/8in gasket', 'SNL:239:024'),
        'main_stud': ('LQ271A', 'SNL:239:023'), 'pin_stud': ('LQ270A', 'SNL:240:003'),
        'gear_stud': ('LQ269A', 'SNL:231:037'), 'plain_nut': ('LQ272A', 'SNL:129:018'),
        'castle_nut': ('LQ198A', 'SNL:129:016'), 'washer': ('LQ166A', 'SNL:273:017'),
        'cotter': ('Unmarked 3/32 x 5/8in split pin', 'SNL:232:004')}
    records = {r['record_id']: r for r in source['records']}
    definitions = {}
    for key in sorted({o['key'] for o in occ}):
        body = doc.addObject('PartDesign::Body', 'Def_ShaftClosure_'+key)
        doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature', 'ReconstructedMachining').Shape = shapes[key]
        mark, rid = ownership[key]
        metadata(body, DefinitionId='shaft_closure_'+key, OriginalMark=mark,
                 SurveyIds=records[rid]['part_ids'], SourceRecord=rid, Representation='assembly',
                 Coverage='partial', Subsystem='Powerplant', GeometryInputs=c,
                 ParameterUpdate='Regenerate engine_shaft_fittings_build.py from controls',
                 ReconstructionNotes='Static estimated profiles and smooth thread envelopes. Source identities, catalogue conflicts and inferred fits recorded in engine_shaft_fittings_sources.json. Not pressure-seal or thread compatibility qualification.')
        definitions[key] = body.Name
    for row in occ:
        obj = doc.addObject('App::Link', row['name'])
        groups[row['assembly']].addObject(obj)
        obj.setLink(doc.getObject(definitions[row['key']]))
        obj.LinkPlacement = App.Placement(App.Vector(*row['xyz']), App.Rotation(*row['rotation']))
        metadata(obj, OccurrenceId=row['name'], Subsystem='Powerplant', QuantityRole='One installed physical constituent')
    metadata(doc.TankLibertyEngine, ReconstructionNotes='Hollow crankcase, crankshaft, bearings and shaft closures. Driving gear, shims, thrust-nut lock, cylinders, rods, valve gear and engine services remain pending.')
    doc.Definitions.Visibility = False
    doc.recompute()
    App.ParamGet('User parameter:BaseApp/Preferences/Document').SetInt('CountBackupFiles', 0)
    native = out/'DrivetrainWithEngineShaftFittings.FCStd'
    doc.saveAs(str(native))
    App.closeDocument(doc.Name)
    doc = App.openDocument(str(native))
    items = leaves(doc.Root)
    byid = {i['id']: i for i in items}
    new = [o['name'] for o in occ]
    changed = ['EngineCrank_Forging']
    assert len(items) == len(byid) == 2131 and len(new) == 139
    for n, (sig, pl) in before.items():
        if n in changed:
            continue
        t, angle = placement_errors(pl, byid[n]['shape'].Placement)
        assert same_shape(sig, shape_signature(byid[n]['shape'])) and t < 1e-6 and angle < 1e-8, n
    for n in new+changed:
        assert byid[n]['shape'].isValid() and len(byid[n]['shape'].Solids) == 1, n
    print('Native saved and reopened; exporting STEP.', flush=True)
    definition_order = list(definitions.values())+['Def_EngineCrank_shaft']
    Part.setStaticValue('write.surfacecurve.mode', 1)
    Part.makeCompound([doc.getObject(n).Shape for n in definition_order]).exportStep(str(out/'EngineShaftFittingsDefinitions.step'))
    Part.makeCompound([byid[n]['shape'] for n in new+changed]).exportStep(str(out/'EngineShaftFittingsInstallation.step'))
    write(out/'definition_order.json', definition_order)
    write(out/'report.json', dict(status='development_hypothesis_not_qualified', native_sha256=sha(native),
        parent_native_sha256=sha(pn), input_hashes=inputs, controls=c, parent_controls=pr['controls'],
        case_controls=pr['case_controls'], parent_datums=pr['datums'], datums=d, occurrences=occ,
        assemblies=assembly_rows, new_ids=new, changed_ids=changed, exchange_ids=new+changed,
        native_occurrences=len(items), new_definitions=len(definitions), unchanged_parent_occurrences=1991,
        standard_native_hashes=pr['standard_native_hashes'], standard_assembly_modified=False,
        historically_qualified=False, complete_engine=False, complete_tank=False,
        pending='Independent native/interface/oil-route/STEP/visual checks; gear/shims/thrust lock; cylinders and rods; remaining engine systems; combined qualification and standard integration.',
        artifact_hashes={f.name: sha(f) for f in out.glob('*.step')},
        export_settings={'write.surfacecurve.mode': 1}, headless=not App.GuiUp, freecad=App.Version(), occ=Part.OCC_VERSION))
    print('Saved 2131 physical occurrences;139 new;1 revised;1991 preserved.', flush=True)
finally:
    runtime.close()
