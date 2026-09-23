"""Build a source-owned water pump in the current receiving-case assembly."""
import argparse
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,default=HERE/'engine_water_pump_passage_study')
p.add_argument('--controls',type=Path,default=HERE/'engine_water_pump_controls.json')
p.add_argument('--worker',action='store_true');a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--output',str(out),'--controls',str(a.controls.resolve()),'--worker'],
            env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App
    import Part
    from lib.cad_build import leaves,metadata,shape_signature
    from lib.worker import same_shape,placement_errors
    from engine_water_pump_parts import parts
    from engine_water_pump_mounting import revise_case
    parent=HERE/'engine_lower_drive_installation';pr=read(parent/'report.json');pn=parent/pr['native_file']
    assert sha(pn)==pr['native_sha256']=='ceac2e5305ed3e9b9411ced38931cd97ca317eb0e520b4243d000b3c6cd8f207'
    c=read(a.controls)['controls'];source=read(HERE/'engine_water_pump_sources.json')
    for name,digest in source['source_assets'].items():assert sha(ROOT/name)==digest,name
    (out/'inputs').mkdir(exist_ok=True);inputs={}
    for path in [Path(__file__),a.controls.resolve(),HERE/'engine_water_pump_parts.py',HERE/'engine_water_pump_sources.json',
                 HERE/'engine_water_pump_mounting.py',HERE/'transmission_bevel_tooth.py',HERE/'engine_crankshaft_parts.py',HERE/'engine_crossmember_parts.py',
                 HERE/'transmission_stud_parts.py',HERE/'transmission_input_installation_parts.py',HERE/'transmission_core_parts.py']:
        inputs[str(path)]=sha(path);(out/'inputs'/path.name).write_bytes(path.read_bytes())
    write(out/'inputs/parent_report.json',pr)
    doc=App.openDocument(str(pn));old={r['id']:r for r in leaves(doc.Root)};assert len(old)==2170
    before={n:(shape_signature(i['shape']),App.Placement(i['shape'].Placement)) for n,i in old.items()}
    shapes,occ,groups,d=parts(c,pr['controls'],pr['receiver_controls']['pump_mount_x']+c['shim_stock']-pr['main_apex'],
                            lambda n,s:print(n,s.isValid(),len(s.Solids),flush=True))
    pump=doc.addObject('App::Part','EngineWaterPump');doc.TankLibertyEngine.addObject(pump)
    pump.Placement.Base=App.Vector(pr['main_apex'],0,-pr['controls']['pump_axis_drop'])
    case=old['EngineCase_lower'];target=case['target']
    case_frame=case['shape'].Placement
    relative=case_frame.inverse().multiply(pump.getGlobalPlacement())
    revised,mounting_datums=revise_case(target.Shape,c,relative,d['mounting'])
    target.Tip.Shape=revised
    metadata(target,GeometryInputs=dict(receiver_parent_native_sha256=sha(pn),water_pump_mounting=c),
        ParameterUpdate='Regenerate engine_water_pump_build.py from the frozen lower-drive receiver parent; no live expression geometry',
        WaterPumpMountingInputs=c,WaterPumpMountingDatums=mounting_datums,
        WaterPumpMountingSource='SNL239:015-020; SNL17; LIB79',
        WaterPumpMountingStatus='Estimated mounting pads and blind source-length stud holes; checks required')
    metadata(pump,QuantityRole='One catalogue pump assembly; nonphysical container',SourceRecord='SNL:160:016',
        Subsystem='Powerplant',Coverage='partial',ReconstructionNotes='Development pump with complete four-stud mounting hardware; source profiles and installation checks pending. Packing quantity and cover elbow identity conflicts retained.')
    assembly={pump.Name:pump}
    for name in groups:
        obj=doc.addObject('App::Part',name);pump.addObject(obj);assembly[name]=obj
        metadata(obj,QuantityRole='Nonphysical subassembly container',Subsystem='Powerplant',Coverage='partial')
    metadata(assembly['EngineWaterPumpBearing'],SourceRecord='SNL:160:018',OriginalMark='H.B.303 / 8056',
        ReconstructionNotes='Printed external dimensions; estimated commercial bearing internals.')
    ownership=dict(shaft=('LQ138A','SNL:216:004'),key=('LQ105A','SNL:114:022'),impeller_nut=('LQ147A','SNL:130:020'),
        impeller_cotter=('Bronze3/32x5/8 split pin','SNL:216:006'),retainer=('LQ140A','SNL:164:025'),
        packing=('LQ141A','SNL:160:023'),gland=('LQ142A','SNL:100:026'),spring=('LQ143A','SNL:221:007'),
        body=('LQ144A','SNL:21:004'),impeller=('LQ146A','SNL:113:026'),cover=('LQ150A','SNL:77:009'),
        cover_gasket=('LQ149A','SNL:99:002'),joint_gasket=('LQ154A','SNL:99:003'),shim=('LQ151A','SNL:161:001'),
        plug=('LQ145A','SNL:161:005'),plug_gasket=('158 5/8 gasket','SNL:161:004'),
        cover_stud=('LQ88A / printed LA88A','SNL:21:005'),cover_washer=('LQ113A','SNL:21:006'),
        cover_nut=('LQ89A','SNL:129:013'),cover_cotter=('1/16x1/2 split pin','SNL:140:008'),
        mount_stud=('LQ197A / 140','SNL:239:017'),mount_nut=('LQ198A / 103','SNL:239:018'),
        mount_cotter=('3/32x5/8 split pin','SNL:239:019'),mount_washer=('LQ166A / 113','SNL:239:020'))
    for key in ['bearing_inner','bearing_outer','bearing_cage','bearing_ball']:ownership[key]=('Estimated HB303 internal','SNL:160:018')
    definitions={};records={r['record_id']:r for r in source['records']}
    for key,s in shapes.items():
        mark,rid=ownership[key];body=doc.addObject('PartDesign::Body','Def_EngineWaterPump_'+key);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedWaterPump').Shape=s
        metadata(body,DefinitionId='engine_water_pump_'+key,OriginalMark=mark,SourceRecord=rid,
            SurveyIds=records.get(rid,{}).get('part_ids',[]),Representation='assembly',Coverage='partial',Subsystem='Powerplant',
            GeometryInputs=c,ParameterUpdate='Regenerate engine_water_pump_build.py; no live expression geometry',
            ReconstructionNotes='Source-led development: unprinted dimensions and cast profiles estimated; packing and cover identity conflicts documented; threads smooth envelopes.')
        definitions[key]=body.Name
    for row in occ:
        obj=doc.addObject('App::Link',row['name']);assembly[row['assembly']].addObject(obj)
        obj.setLink(doc.getObject(definitions[row['key']]));obj.LinkPlacement=App.Placement(App.Vector(*row['xyz']),App.Rotation(*row['rotation']))
        metadata(obj,OccurrenceId=row['name'],Subsystem='Powerplant',QuantityRole='One physical constituent of development water pump')
    doc.recompute();doc.Definitions.Visibility=False
    App.ParamGet('User parameter:BaseApp/Preferences/Document').SetInt('CountBackupFiles',0)
    native=out/'DrivetrainWithWaterPump.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));byid={i['id']:i for i in leaves(doc.Root)}
    assert len(byid)==2170+len(occ)
    for name,(signature,pl) in before.items():
        if name=='EngineCase_lower':continue
        dt,angle=placement_errors(pl,byid[name]['shape'].Placement)
        assert same_shape(signature,shape_signature(byid[name]['shape'])) and dt<1e-6 and angle<1e-8,name
    for row in occ:assert byid[row['name']]['shape'].isValid() and len(byid[row['name']]['shape'].Solids)==1,row['name']
    Part.setStaticValue('write.surfacecurve.mode',1)
    Part.makeCompound([doc.getObject(name).Shape for name in definitions.values()]).exportStep(str(out/'WaterPumpDefinitions.step'))
    Part.makeCompound([byid[row['name']]['shape'] for row in occ]).exportStep(str(out/'WaterPumpInstallation.step'))
    byid['EngineCase_lower']['target'].Shape.exportStep(str(out/'LowerCaseDefinition.step'))
    byid['EngineCase_lower']['shape'].exportStep(str(out/'LowerCaseInstallation.step'))
    write(out/'definition_order.json',list(definitions.values()))
    write(out/'report.json',dict(status='unqualified_water_pump_development',native_file=native.name,native_sha256=sha(native),
        parent_native=str(pn.relative_to(ROOT)),parent_native_sha256=sha(pn),input_hashes=inputs,controls=c,
        lower_controls=pr['controls'],datums=d,occurrences=occ,definitions=definitions,new_ids=[row['name'] for row in occ],
        changed_ids=['EngineCase_lower'],native_occurrences=len(byid),new_definitions=len(shapes),unchanged_parent_occurrences=2169,
        mounting_datums=mounting_datums,
        engine_origin=pr['engine_origin'],main_apex=pr['main_apex'],pump_axis_z=-pr['controls']['pump_axis_drop'],
        standard_native_hashes=pr['standard_native_hashes'],standard_assembly_modified=False,complete_engine=False,complete_tank=False,
        pending=['Independent geometry, source views, gear mesh and STEP checks','Qualify estimated case mounting pads, hardware stack and source clocking; drain lock wire remains absent',
                 'Resolve packing quantity and cover elbow identity','Oil pump and remaining engine systems','Standard tank integration'],
        artifact_hashes={f.name:sha(f) for f in out.glob('*.step')},freecad=App.Version(),occ=Part.OCC_VERSION))
    print('Saved',len(byid),'physical occurrences;',len(occ),'new pump constituents;',len(shapes),'definitions',flush=True)
finally:
    runtime.close()
