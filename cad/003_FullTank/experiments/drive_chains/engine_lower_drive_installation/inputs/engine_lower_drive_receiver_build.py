"""Rebuild one lower casing from the committed 2170-occurrence driver study."""
import argparse
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent; STAGE=HERE.parents[1]; ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,default=HERE/'engine_lower_drive_installation')
p.add_argument('--controls',type=Path,default=HERE/'engine_lower_drive_receiver_controls.json')
p.add_argument('--worker',action='store_true');a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--output',str(out),'--controls',str(a.controls.resolve()),'--worker'],
            env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App
    import Part
    from lib.cad_build import leaves,metadata
    from engine_lower_drive_receivers import revise
    parent=HERE/'engine_lower_drive_study';pn=parent/'DrivetrainWithLowerDriveStudy.FCStd'
    pr=read(parent/'report.json');assert sha(pn)==pr['native_sha256']
    source=read(HERE/'engine_lower_drive_receiver_sources.json')
    for rel,digest in source['source_assets'].items():assert sha(ROOT/rel)==digest,rel
    c=read(a.controls)['controls'];(out/'inputs').mkdir(exist_ok=True);inputs={}
    for path in [Path(__file__),a.controls.resolve(),HERE/'engine_lower_drive_receivers.py',HERE/'engine_lower_drive_receiver_sources.json']:
        inputs[str(path)]=sha(path);(out/'inputs'/path.name).write_bytes(path.read_bytes())
    write(out/'inputs/parent_report.json',pr)
    doc=App.openDocument(str(pn));items={i['id']:i for i in leaves(doc.Root)};assert len(items)==2170
    target=items['EngineCase_lower']['target'];old=target.Shape.copy()
    revised,d=revise(old,c,pr['datums'],pr['main_apex'],pr['controls'],
        lambda n,s:print(n,s.isValid(),len(s.Solids),flush=True))
    feature=target.Tip if target.TypeId=='PartDesign::Body' else target
    feature.Shape=revised
    metadata(target,LowerDriveReceiverInputs=c,LowerDriveReceiverDatums=d,
        LowerDriveReceiverSource='LIB23/28/79/96/107; SNL14/17/19; HB99/100',
        LowerDriveReceiverStatus='Estimated receiver candidate; actual pump fit and standard integration remain unqualified',
        LowerDriveReceiverRegeneration='engine_lower_drive_receiver_build.py from committed lower-drive study')
    metadata(doc.EngineLowerDistributionDrive,ReconstructionNotes='Receiver development candidate. Complete pump assemblies and historical dimensional registration remain unqualified.')
    doc.recompute();doc.Definitions.Visibility=False
    App.ParamGet('User parameter:BaseApp/Preferences/Document').SetInt('CountBackupFiles',0)
    native=out/'DrivetrainWithLowerDriveReceivers.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));items={i['id']:i for i in leaves(doc.Root)};assert len(items)==2170
    new=items['EngineCase_lower']['target'].Shape
    assert new.isValid() and len(new.Solids)==1
    Part.setStaticValue('write.surfacecurve.mode',1)
    new.exportStep(str(out/'LowerCaseDefinition.step'))
    items['EngineCase_lower']['shape'].exportStep(str(out/'LowerCaseInstallation.step'))
    report=dict(status='receiver_development_candidate',native_file=native.name,native_sha256=sha(native),
        parent_native=str(pn.relative_to(ROOT)),parent_native_sha256=sha(pn),input_hashes=inputs,
        controls=pr['controls'],receiver_controls=c,datums=pr['datums'],receiver_datums=d,main_apex=pr['main_apex'],
        new_ids=[],unit_ids=pr['new_ids'],changed_ids=['EngineCase_lower'],native_occurrences=2170,
        unchanged_parent_occurrences=2169,engine_origin=pr['engine_origin'],
        standard_native_hashes=pr['standard_native_hashes'],standard_assembly_modified=False,
        historically_qualified=False,installation_qualified=False,complete_engine=False,complete_tank=False,
        artifact_hashes={f.name:sha(f) for f in out.glob('*.step')},freecad=App.Version(),occ=Part.OCC_VERSION)
    write(out/'report.json',report)
    print('Saved2170occurrences; one revised lower case,2169preserved. Receiver checks pending.',flush=True)
finally:
    runtime.close()
