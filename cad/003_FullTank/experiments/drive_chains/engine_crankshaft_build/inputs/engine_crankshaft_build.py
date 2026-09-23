"""Install crankshaft, main bearings and double thrust in the saved case assembly."""
import argparse
from pathlib import Path
import subprocess,sys
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,default=HERE/'engine_crankshaft_build')
p.add_argument('--controls',type=Path,default=HERE/'engine_crankshaft_controls.json')
p.add_argument('--worker',action='store_true');a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--output',str(out),'--controls',str(a.controls.resolve()),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part
    from lib.cad_build import leaves,metadata,shape_signature
    from lib.worker import same_shape,placement_errors
    from engine_crankshaft_parts import parts
    V=App.Vector
    parent=HERE/'engine_case_build';pn=parent/'DrivetrainWithEngineCase.FCStd';pr=read(parent/'report.json')
    assert sha(pn)==pr['native_sha256']
    source=read(HERE/'engine_crankshaft_sources.json');c=read(a.controls)['controls'];cc=pr['controls']
    for rel,digest in source['source_assets'].items():assert sha(ROOT/rel)==digest,rel
    inputs={};(out/'inputs').mkdir(exist_ok=True)
    for path in [Path(__file__),HERE/'engine_crankshaft_parts.py',HERE/'engine_crankshaft_sources.json',a.controls.resolve(),
                 HERE/'transmission_stud_parts.py',HERE/'transmission_input_installation_parts.py',HERE/'engine_crossmember_parts.py']:
        (out/'inputs'/path.name).write_bytes(path.read_bytes());inputs[str(path.relative_to(ROOT))]=sha(path)
    doc=App.openDocument(str(pn));old={i['id']:i for i in leaves(doc.Root)}
    before={n:(shape_signature(i['shape']),App.Placement(i['shape'].Placement)) for n,i in old.items()}
    origin=doc.TankLibertyEngine.Placement.Base
    clutch=read(HERE/'clutch_drum_build/report.json');cd=clutch['datums'];fc=clutch['controls']
    fly=old['ClutchDrum_flywheel']['shape'].Placement
    assert (fly.Rotation.multVec(V(1,0,0))-V(1,0,0)).Length<1e-8
    taper=dict(rear=fly.multVec(V(cd['hub_rear'],0,0)).x-origin.x,front=fly.multVec(V(cd['taper_front'],0,0)).x-origin.x,
               rear_radius=fc['taper_rear_radius'],front_radius=fc['taper_front_radius'],keyway_depth=fc['keyway_depth'],keyway_width=fc['keyway_width'])
    originals={k:doc.getObject('Def_EngineCase_'+k).Shape.copy() for k in ['upper','lower']}
    print('Constructing source-informed crankshaft and bearing installation.',flush=True)
    shapes,occ,d=parts(c,cc,taper,originals,lambda label,s:print(label,s.isValid(),len(s.Solids),flush=True))
    d['origin']=list(origin);d['axial_registration']=pr['datums']['axial_registration']
    changed=['EngineCase_upper','EngineCase_lower']
    for key in ['upper','lower']:
        obj=doc.getObject('Def_EngineCase_'+key);obj.Tip.Shape=shapes[key]
        metadata(obj,GeometryInputs=dict(case=cc,crankshaft=c),ParameterUpdate='Regenerate engine_crankshaft_build.py from controls and committed engine case parent',
                 ReconstructionNotes='Original hollow casting plus source-length bearing seats, oil/dowel passages, estimated thrust housing and raised gear floor. Mount pattern and cast profiles remain provisional.')
    groups={}
    for name in ['EngineRotatingAssembly','EngineMainBearings','EngineThrustBearing']:
        group=doc.addObject('App::Part',name);doc.TankLibertyEngine.addObject(group);groups[name]=group
        metadata(group,QuantityRole='Nonphysical assembly container',Subsystem='Powerplant',Coverage='partial')
    metadata(groups['EngineThrustBearing'],OriginalMark='LQ273A',SourceRecord='SNL:17:026',ReconstructionNotes='One catalogue double-thrust bearing, decomposed into 3 races, 2 cages and 40 estimated balls. Internal dimensions/count unprinted.')
    metadata(doc.TankLibertyEngine,ReconstructionNotes='Hollow crankcase, crankshaft forging, main and thrust bearings. Cylinder assemblies, shaft plugs/gear/locking hardware, oil pipes and other engine systems remain pending.')
    ownership={
        'shaft':('LQ255A','SNL:212:018'),'long_lower':('LQ238A','SNL:17:019'),'short_lower':('LQ240A','SNL:17:020'),
        'long_upper':('LQ239A','SNL:17:021'),'short_upper':('LQ241A','SNL:17:022'),'dowel':('LQ194A','SNL:83:017'),
        'thrust_nut':('LQ275A','SNL:125:017'),'thrust_sleeve':('LQ274A','SNL:217:026'),
        'key':('SH136B','SNL:212:011'),'key_screw':('No10-24 x 3/4in','SNL:212:014'),
        'output_nut':('SH136A','SNL:125:016'),'output_cotter':('1/4 x 3in split pin','SNL:212:013')}
    definitions={};records={r['record_id']:r for r in source['records']}
    for key in sorted({o['key'] for o in occ}):
        body=doc.addObject('PartDesign::Body','Def_EngineCrank_'+key);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedMachining').Shape=shapes[key]
        mark,rid=ownership.get(key,('', 'SNL:17:026'));evidence=records[rid]
        metadata(body,DefinitionId='engine_crank_'+key,OriginalMark=mark,SurveyIds=evidence['part_ids'],SourceRecord=rid,
                 Representation='assembly',Coverage='partial',Subsystem='Powerplant',GeometryInputs=c,ParameterUpdate='Regenerate engine_crankshaft_build.py from controls',
                 ReconstructionNotes='Source-informed static reconstruction; unprinted profiles and dimensions are named estimates. Source/interpretation decisions are in engine_crankshaft_sources.json. Smooth thread envelopes. Thrust internals belong to one LQ273A assembly.')
        definitions[key]=body.Name
    for row in occ:
        obj=doc.addObject('App::Link',row['name']);groups[row['assembly']].addObject(obj);obj.setLink(doc.getObject(definitions[row['key']]))
        obj.LinkPlacement=App.Placement(V(*row['xyz']),App.Rotation(*row['rotation']))
        metadata(obj,OccurrenceId=row['name'],Subsystem='Powerplant',QuantityRole='One installed physical constituent')
    new=[o['name'] for o in occ];definition_order=list(definitions.values())+['Def_EngineCase_upper','Def_EngineCase_lower']
    doc.Definitions.Visibility=False;doc.recompute();App.ParamGet('User parameter:BaseApp/Preferences/Document').SetInt('CountBackupFiles',0)
    native=out/'DrivetrainWithEngineCrankshaft.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));items=leaves(doc.Root);byid={i['id']:i for i in items}
    assert len(items)==len(byid)==len(before)+len(new)
    for n,(sig,pl) in before.items():
        if n in changed:continue
        t,angle=placement_errors(pl,byid[n]['shape'].Placement)
        assert same_shape(sig,shape_signature(byid[n]['shape'])) and t<1e-6 and angle<1e-8,n
    for n in new+changed:assert byid[n]['shape'].isValid() and len(byid[n]['shape'].Solids)==1,n
    Part.setStaticValue('write.surfacecurve.mode',1)
    Part.makeCompound([doc.getObject(n).Shape for n in definition_order]).exportStep(str(out/'EngineCrankshaftDefinitions.step'))
    Part.makeCompound([byid[n]['shape'] for n in new+changed]).exportStep(str(out/'EngineCrankshaftInstallation.step'))
    write(out/'definition_order.json',definition_order)
    write(out/'report.json',dict(status='development_hypothesis_not_qualified',native_sha256=sha(native),parent_native_sha256=sha(pn),input_hashes=inputs,
        controls=c,case_controls=cc,datums=d,occurrences=occ,new_ids=new,changed_ids=changed,exchange_ids=new+changed,native_occurrences=len(items),
        new_definitions=len(definitions),unchanged_parent_occurrences=len(before)-len(changed),standard_native_hashes=pr['standard_native_hashes'],
        standard_assembly_modified=False,historically_qualified=False,complete_engine=False,complete_tank=False,
        pending='Shaft plugs/studs/gear/locking hardware; cylinders and rods; complete lubrication; engine mounting reconciliation; combined qualification and standard integration.',
        artifact_hashes={f.name:sha(f) for f in out.glob('*.step')},export_settings={'write.surfacecurve.mode':1},headless=not App.GuiUp,freecad=App.Version(),occ=Part.OCC_VERSION))
    print('Saved',len(items),'physical occurrences;',len(new),'new;',len(changed),'revised;',len(before)-len(changed),'preserved.',flush=True)
finally:
    runtime.close()
