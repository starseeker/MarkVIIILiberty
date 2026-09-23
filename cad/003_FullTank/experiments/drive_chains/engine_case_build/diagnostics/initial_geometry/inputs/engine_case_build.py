"""Install hollow crankcase castings and revise provisional supports for casing fit."""
import argparse
from pathlib import Path
import subprocess
import sys
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=HERE/'engine_case_build');p.add_argument('--controls',type=Path,default=HERE/'engine_case_controls.json');p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--output',str(out),'--controls',str(a.controls.resolve()),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part
    from lib.cad_build import leaves,metadata,shape_signature
    from lib.worker import same_shape,placement_errors
    from engine_case_parts import parts
    from engine_suspension_parts import parts as suspension_parts
    from engine_crossmember_parts import box
    V=App.Vector
    parent=HERE/'engine_suspension_build';pn=parent/'DrivetrainWithEngineSuspension.FCStd';pr=read(parent/'report.json');assert sha(pn)==pr['native_sha256']
    source=read(HERE/'engine_case_sources.json');c=read(a.controls)['controls'];sc=dict(pr['controls']);cc=pr['crossmember_controls']
    for rel,digest in source['source_assets'].items():assert sha(ROOT/rel)==digest
    inputs={};(out/'inputs').mkdir(exist_ok=True)
    for path in [Path(__file__),HERE/'engine_case_parts.py',HERE/'engine_case_sources.json',HERE/'engine_suspension_parts.py',HERE/'engine_crossmember_parts.py',a.controls.resolve()]:
        (out/'inputs'/path.name).write_bytes(path.read_bytes());inputs[str(path.relative_to(ROOT))]=sha(path)
    print('Building two source-informed hollow castings.',flush=True)
    shapes,datums=parts(c,lambda label,s:print(label,s.isValid(),len(s.Solids),flush=True))
    doc=App.openDocument(str(pn));old={i['id']:i for i in leaves(doc.Root)}
    before={n:(shape_signature(i['shape']),i['shape'].Placement) for n,i in old.items()}
    origin=V(old['ClutchDrum_flywheel']['shape'].BoundBox.XMax+c['output_clearance_to_flywheel'],0,doc.TransmissionCore.Placement.Base.z)
    datums['origin']=list(origin);datums['axial_registration']='5mm nominal flywheel-to-nose clearance plus conditional HB44 nose length; not qualified engine/crankshaft alignment'
    # Record whether the former yoke actually conflicts, before any revision.
    world_lower=shapes['lower'].copy();world_lower.translate(origin)
    prior_overlap=world_lower.common(old['EngineSuspension_FrontBracket']['shape']).Volume
    datums['previous_front_yoke_overlap_mm3']=prior_overlap
    originals={}
    for name,station in [('EngineFrame_RearChannel',cc['rear_x']),('EngineFrame_FrontCleat',cc['front_x'])]:
        s=old[name]['shape'].copy();s.translate(-V(station,0,cc['floor_top']))
        if name=='EngineFrame_FrontCleat':s=s.common(box(-100,200,-100,100,-1,cc['channel_height']))
        originals[name]=s
    sc['front_hub_height']=c['suspension_front_hub_height'];sc['rail_front_x']=c['suspension_rail_front_x']
    support,occ,revisions,sdatums=suspension_parts(sc,cc,origin.z,originals)
    replacements={'EngineSuspension_LeftRail':support['left_rail'],'EngineSuspension_RightRail':support['right_rail'],
                  'EngineSuspension_FrontBracket':support['front_bracket']}
    for n,s in replacements.items():old[n]['target'].Tip.Shape=s
    # Cleat definition uses the original crossmember center, not the yoke datum.
    cleat=revisions['EngineFrame_FrontCleat'];n='EngineFrame_FrontCleat';target=old[n]['target']
    world=old[n]['shape'].Placement.multiply(target.Shape.Placement.inverse());cleat.translate(V(cc['front_x'],0,cc['floor_top']))
    cleat.Placement=world.inverse().multiply(cleat.Placement);target.Tip.Shape=cleat
    moved=[]
    for row in occ:
        if row['name'].startswith('EngineSuspension_FrontPivot'):
            old[row['name']]['object'].LinkPlacement=App.Placement(V(*row['xyz']),App.Rotation(*row['rotation']));moved.append(row['name'])
    changed=list(replacements)+['EngineFrame_FrontCleat']+moved
    for n in changed:metadata(old[n]['object'],ReconstructionNotes='Provisional engine casing integration: rail extension and lower yoke/hub. Source support hardware retained; historical mounting unqualified.')
    engine=doc.addObject('App::Part','TankLibertyEngine');doc.PowerplantDevelopment.addObject(engine);engine.Placement=App.Placement(origin,App.Rotation())
    metadata(engine,Subsystem='Powerplant',QuantityRole='Nonphysical assembly container',Coverage='partial',ReconstructionNotes='Two castings only; rotating internals, cylinder assemblies, inserts, fittings and hardware remain pending.')
    casegroup=doc.addObject('App::Part','EngineCrankcase');engine.addObject(casegroup)
    new=[];defs=[]
    for key,mark,rid in [('upper','LQ207A','SNL:59:001'),('lower','LQ180A','SNL:57:036')]:
        body=doc.addObject('PartDesign::Body','Def_EngineCase_'+key);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedCasting').Shape=shapes[key]
        evidence=next(row for row in source['records'] if row['record_id']==rid)
        metadata(body,DefinitionId='engine_case_'+key,OriginalMark=mark,SurveyIds=evidence['part_ids'],SourceRecord=rid,Representation='assembly',Coverage='partial',Subsystem='Powerplant',
                 GeometryInputs=c,ParameterUpdate='Regenerate engine_case_build.py from controls',
                 ReconstructionNotes='Hollow case, integral webs and functional openings; profiles, stock and interfaces estimated. Aviation dimensions conditional. Mounting count/bearing insert conflicts unresolved. No helical threads or hardware included in casting.')
        obj=doc.addObject('App::Link','EngineCase_'+key);casegroup.addObject(obj);obj.setLink(body)
        metadata(obj,OccurrenceId=obj.Name,Subsystem='Powerplant',QuantityRole='One physical casting')
        new.append(obj.Name);defs.append(body.Name)
    defs += [old[n]['target'].Name for n in list(replacements)+['EngineFrame_FrontCleat']]
    doc.Definitions.Visibility=False;doc.recompute();App.ParamGet('User parameter:BaseApp/Preferences/Document').SetInt('CountBackupFiles',0)
    native=out/'DrivetrainWithEngineCase.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));byid={i['id']:i for i in leaves(doc.Root)};assert len(byid)==1911
    for n,(sig,pl) in before.items():
        if n in changed:continue
        t,angle=placement_errors(pl,byid[n]['shape'].Placement);assert same_shape(sig,shape_signature(byid[n]['shape'])) and t<1e-6 and angle<1e-8,n
    for n in new+changed:assert byid[n]['shape'].isValid() and len(byid[n]['shape'].Solids)==1,n
    # Retain p-curves on elliptical rims; learned from the suspension exchange.
    Part.setStaticValue('write.surfacecurve.mode',1)
    Part.makeCompound([doc.getObject(n).Shape for n in defs]).exportStep(str(out/'EngineCaseDefinitions.step'))
    Part.makeCompound([byid[n]['shape'] for n in new+changed]).exportStep(str(out/'EngineCaseInstallation.step'))
    write(out/'definition_order.json',defs)
    write(out/'report.json',dict(status='development_hypothesis_not_qualified',native_sha256=sha(native),parent_native_sha256=sha(pn),input_hashes=inputs,
        controls=c,suspension_controls=sc,crossmember_controls=cc,datums=datums,suspension_datums=sdatums,new_ids=new,changed_ids=changed,exchange_ids=new+changed,
        native_occurrences=len(byid),new_definitions=2,unchanged_parent_occurrences=len(old)-len(changed),standard_native_hashes=pr['standard_native_hashes'],standard_assembly_modified=False,
        historical_case_profiles_proven=False,engine_mounting_complete=False,complete_engine=False,complete_tank=False,
        artifact_hashes={f.name:sha(f) for f in out.glob('*.step')},export_settings={'write.surfacecurve.mode':1},headless=not App.GuiUp,freecad=App.Version(),occ=Part.OCC_VERSION))
    print('Saved1911 physical occurrences;2 castings;7 support revisions;',len(old)-len(changed),'preserved. Previous yoke overlap',prior_overlap,flush=True)
finally:
    runtime.close()
