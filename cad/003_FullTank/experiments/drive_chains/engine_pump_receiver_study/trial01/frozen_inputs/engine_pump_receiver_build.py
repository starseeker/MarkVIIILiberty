"""Build a local receiving-case candidate without changing any parent assembly."""
import argparse
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--controls',type=Path,default=HERE/'engine_pump_receiver_study/controls.json')
p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
if not a.worker:
    with (out/'build.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--output',str(out),
            '--controls',str(a.controls.resolve()),'--worker'],
            env=runtime.environment(out/'runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)

try:
    import FreeCAD as App
    import Part
    from lib.cad_build import leaves,metadata
    from engine_pump_receivers import revise
    study=HERE/'engine_pump_layout_study'
    folders=dict(drive=study/'lower_drive_trial',oil=study/'oil_profile_joint_trial',
                 water=HERE/'engine_water_pump_connections_study')
    reports={k:read(v/'report.json') for k,v in folders.items()}
    paths={k:folders[k]/r.get('native_file','DrivetrainWithLowerDriveStudy.FCStd') for k,r in reports.items()}
    for key,path in paths.items():assert sha(path)==reports[key]['native_sha256'],key
    # Only the pre-receiver case is needed for construction; release its parent
    # document before the Boolean stages. Context is checked independently.
    source=App.openDocument(str(paths['drive']))
    source_case=next(i['target'] for i in leaves(source.Root) if i['id']=='EngineCase_lower')
    original=source_case.Shape.copy()
    App.closeDocument(source.Name);del source_case,source
    controls=read(a.controls);stages=[]
    def progress(name,shape):
        row=dict(stage=name,valid=shape.isValid(),solids=len(shape.Solids),
                 volume_mm3=shape.Volume,max_tolerance_mm=shape.getTolerance(1))
        stages.append(row);write(out/'build_progress.json',stages)
        print(name,row['valid'],row['solids'],flush=True)
        assert row['valid'] and row['solids']==1,name
    shape,datums=revise(original,controls,reports['oil'],reports['drive'],reports['water'],progress)
    doc=App.newDocument('CoupledPumpReceiver');root=doc.addObject('App::Part','Root')
    body=doc.addObject('PartDesign::Body','Def_EngineCase_lower')
    body.newObject('PartDesign::Feature','ReconstructedReceiver').Shape=shape
    metadata(body,GeometryInputs=controls,ReceiverDatums=datums,
        SourceEvidence='engine_pump_receiver_study/source_review.json; engine_pump_layout_study/source_constraints.json',
        RepresentationStatus='Development case only; local mechanical, manifold circuit and global installation checks incomplete')
    link=doc.addObject('App::Link','EngineCase_lower');root.addObject(link);link.setLink(body)
    metadata(link,OccurrenceId='EngineCase_lower',QuantityRole='One physical lower crankcase; local study')
    body.Visibility=False;doc.recompute()
    native=out/'PumpReceiver.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));shape=doc.Def_EngineCase_lower.Shape
    assert shape.isValid() and len(shape.Solids)==1
    Part.setStaticValue('write.surfacecurve.mode',1)
    shape.exportStep(str(out/'PumpReceiverDefinition.step'))
    installed=shape.copy();installed.translate(App.Vector(*reports['drive']['engine_origin']))
    installed.exportStep(str(out/'PumpReceiverInstallation.step'))
    inputs=[Path(__file__),HERE/'engine_pump_receivers.py',HERE/'engine_lower_drive_receivers.py',
            HERE/'engine_oil_pump_parts.py',HERE/'engine_water_pump_mounting.py',a.controls.resolve(),
            HERE/'engine_pump_receiver_study/source_review.json']
    report=dict(status='unqualified_coupled_receiver_trial',native_file=native.name,native_sha256=sha(native),
        controls=controls,datums=datums,stages=stages,input_hashes={str(f.relative_to(ROOT)):sha(f) for f in inputs},
        parent_natives={key:dict(path=str(path.relative_to(ROOT)),sha256=sha(path)) for key,path in paths.items()},
        parent_reports={key:dict(path=str((folder/'report.json').relative_to(ROOT)),sha256=sha(folder/'report.json')) for key,folder in folders.items()},
        engine_origin=reports['drive']['engine_origin'],physical_occurrences=1,
        local_mechanical_qualified=False,hydraulic_circuit_qualified=False,standard_assembly_modified=False,
        installation_qualified=False,complete_engine=False,complete_tank=False,
        step_hashes={f.name:sha(f) for f in out.glob('*.step')},freecad=App.Version(),occ=Part.OCC_VERSION)
    write(out/'report.json',report)
    print('Saved one local receiving case; combined installation not qualified',flush=True)
finally:
    runtime.close()
