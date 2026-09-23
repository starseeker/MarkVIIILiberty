"""Populate the connected main-clutch bearing, sleeve, keys and cone support."""
import argparse,json,subprocess,sys
from pathlib import Path
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];REPO=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=HERE/'clutch_stack_build')
p.add_argument('--worker',action='store_true');a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--output',str(out),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part,numpy as np
    from lib.cad_build import leaves,metadata,shape_signature,COLORS
    from lib.worker import same_shape,placement_errors,check_build
    from lib.visual_review import shaded
    from clutch_stack_parts import build
    parent=HERE/'clutch_collar_build';native_parent=parent/'TransmissionWithClutchCollar.FCStd'
    pq=read(parent/'qualification.json');assert pq['passed'] and sha(native_parent)==pq['native_sha256']
    dossier=read(HERE/'clutch_stack_sources.json');records={r['record_id']:r for r in dossier['records']}
    for path,h in dossier['source_assets'].items():assert sha(REPO/path)==h,path
    inputs=[Path(__file__)]+[HERE/n for n in ['clutch_stack_parts.py','clutch_stack_controls.json','clutch_stack_sources.json',
        'clutch_collar_controls.json','transmission_input_parts.py','transmission_core_parts.py','transmission_stud_parts.py']]
    hashes={str(f.relative_to(REPO)):sha(f) for f in inputs};(out/'inputs').mkdir(exist_ok=True)
    for path in inputs:(out/'inputs'/path.name).write_bytes(path.read_bytes())
    c=read(HERE/'clutch_stack_controls.json')['controls'];pc=read(HERE/'clutch_collar_controls.json')['controls']
    doc=App.openDocument(str(native_parent));doc.recompute();old={i['id']:i for i in leaves(doc.Root)}
    signatures={n:shape_signature(i['shape']) for n,i in old.items()};places={n:i['shape'].Placement for n,i in old.items()}
    base=old['ClutchCollar_collar']['target'].Shape.copy();base.exportBrep(str(out/'inputs/parent_collar.brep'))
    parts,occ,collar=build(c,pc,base);changed=['ClutchCollar_collar']
    old['ClutchCollar_collar']['target'].Tip.Shape=collar
    metadata(old['ClutchCollar_collar']['target'],MainStackRevision='Larger main bore and body, four literal-dimension key beds, external snap-ring groove. Prior empty-bore approximation superseded in this candidate.')
    group=doc.addObject('App::Part','ClutchStack');doc.TransmissionCore.addObject(group)
    metadata(group,Scope='SH998D bearing,SH861B sleeve,SH869A cone support,four SH861D keys,SH998B thrust collar,SH861E external snap ring. Cones, thrust/ball mechanism, spring plungers and engine interface pending.')
    identity=dict(bearing=('SH998D','SNL:17:016'),sleeve=('SH861B','SNL:217:024'),support=('SH869A','SNL:67:018'),
        key=('SH861D','SNL:114:024'),thrust=('SH998B','SNL:67:020'),snap=('SH861E','SNL:165:001'))
    bodies={}
    for key,s in parts.items():
        body=doc.addObject('PartDesign::Body','Def_ClutchStack_'+key);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedPart').Shape=s;mark,rid=identity[key]
        metadata(body,DefinitionId='clutch_stack_'+key,OriginalMark=mark,SurveyIds=records[rid]['part_ids'],SourceRecord=rid,
            Representation='assembly',Coverage='partial',ParameterUpdate='Rebuild clutch_stack_build.py from clutch_stack_controls.json',
            ReconstructionNotes='Documented estimate; HB/SNL dimension transfers and exact drive, bearing and cone interfaces remain unqualified. See I03-clutch-stack packet.')
        bodies[key]=body
    for row in occ:
        key=row['key'];rid=identity[key][1];link=doc.addObject('App::Link',row['name']);group.addObject(link);link.setLink(bodies[key])
        link.LinkPlacement=App.Placement(App.Vector(*row['xyz']),App.Rotation(App.Vector(1,0,0),row['angle']))
        metadata(link,OccurrenceId=row['name'],SurveyIds=records[rid]['part_ids'],SourceRecord=rid,Subsystem='Drivetrain',QuantityRole='One physical component')
    doc.Definitions.Visibility=False;doc.recompute();native=out/'TransmissionWithClutchStack.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items};origin=doc.TransmissionCore.Placement.Base
    new=[r['name'] for r in occ];affected=new+changed
    assert len(items)==len(byid)==1549 and len(new)==9 and len(affected)==10
    for n,i in byid.items():
        assert i['shape'].isValid() and len(i['shape'].Solids)==1,n
        if n in old and n not in changed:
            t,r=placement_errors(i['shape'].Placement,places[n]);assert t<1e-6 and r<1e-8,n
            assert same_shape(signatures[n],shape_signature(i['shape'])),n
    report=dict(status='clutch_stack_candidate',native_sha256=sha(native),parent_native_sha256=sha(native_parent),input_hashes=hashes,
        controls=c,parent_controls=pc,native_occurrences=1549,new_physical_occurrences=9,new_ids=new,changed_ids=changed,
        affected_ids=affected,unchanged_parent_occurrences=1539,parent_collar_sha256=sha(out/'inputs/parent_collar.brep'),
        standard_assembly_modified=False,main_clutch_complete=False,historical_fit_qualified=False,complete_tank=False)
    write(out/'report.json',report);print('Saved and reopened1549 leaves,9new,1revised collar,1539unchanged.',flush=True)
    standard=check_build(STAGE/'build');td=App.openDocument(standard['build']['top_document']);td.recompute()
    context=[i for i in leaves(td.Root) if i['representation']=='assembly'];report['standard_native_hashes']=standard['native_hashes']
    physical=items+context;boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].copy().cleaned().BoundBox for i in physical]])
    pairs=[];seen=set()
    for n in affected:
        s=byid[n]['shape'];b=s.copy().cleaned().BoundBox;bb=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
        near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
        for idx in near:
            other=physical[idx];pair=tuple(sorted([n,other['id']]))
            if n==other['id'] or pair in seen:continue
            seen.add(pair);v=s.common(other['shape']).Volume;pairs.append(dict(a=n,b=other['id'],intersection_mm3=v))
        write(out/'material_progress.json',dict(last=n,pairs=len(pairs),overlaps=[r for r in pairs if r['intersection_mm3']>1e-5]))
    overlaps=[r for r in pairs if r['intersection_mm3']>1e-5]
    report.update(material_pairs=len(pairs),overlaps=overlaps,material_passed=not overlaps,standard_context_checked=True)
    write(out/'material_checks.json',dict(passed=not overlaps,pairs=pairs,native_sha256=sha(native),standard_context_checked=True))
    print('Material pairs',len(pairs),'overlaps',json.dumps(overlaps),flush=True)
    path=out/'ClutchStackInstallation.step';Part.makeCompound([byid[n]['shape'] for n in affected]).exportStep(str(path));report.update(step_sha256=sha(path),step_ids=affected)
    keys=['Def_ClutchStack_'+k for k in parts]+[byid['ClutchCollar_collar']['target'].Name]
    path=out/'ClutchStackDefinitions.step';Part.makeCompound([doc.getObject(k).Shape for k in keys]).exportStep(str(path));write(out/'definition_order.json',keys);report['definition_step_sha256']=sha(path)
    view=out/'previews';view.mkdir(exist_ok=True);COLORS.update(Clutch=(.67,.61,.46),Shaft=(.64,.66,.70),Spring=(.42,.46,.48),Fastener=(.66,.67,.69),Belt=(.24,.25,.23),Bronze=(.68,.52,.28))
    def draw(names,file,title,direction,clip=None):
        selected=[]
        for n in names:
            i=byid[n];s=i['shape'] if clip is None else i['shape'].common(clip)
            if s.isNull() or not s.Solids:continue
            color='Spring' if n=='FrontClutch_Spring' else ('Shaft' if n=='ClutchDrive_shaft' else ('Clutch' if n.startswith(('FrontClutch_','ClutchDrive_','ClutchCollar_','ClutchStack_')) else i['system']))
            if n=='ClutchDrive_belt':color='Belt'
            if n.startswith(('ClutchCollar_Screw','FrontClutch_Set','ClutchStack_Key')) or n in ['ClutchCollar_wire','ClutchCollar_ring','ClutchStack_sleeve','ClutchStack_snap']:color='Fastener'
            if n in ['ClutchCollar_bush','ClutchStack_bearing']:color='Bronze'
            selected.append(dict(i,shape=s,target=SimpleNamespace(Shape=s),definition=n,system=color))
        shaded(selected,view/(file+'.svg'),direction,title)
    front=[n for n in byid if n.startswith(('FrontClutch_','ClutchCollar_'))]
    drive=[n for n in byid if n.startswith(('ClutchDrive_','AirPump_','PumpMount_','InputHousing_')) or n=='CenterTransmissionCore_bevel_cover']
    draw(new+front+drive,'isometric','Main clutch core | bearing, sleeve, keyed support, thrust collar and external ring',(1,1,.65))
    mechanism=new+front+['ClutchDrive_shaft','ClutchDrive_box','ClutchDrive_drum']
    draw(mechanism,'mechanism','Main clutch core | cones, thrust mechanism and spring plungers still pending',(1,1,.6))
    clip=Part.makeBox(225,270,2,origin+App.Vector(800,-135,-1))
    draw(new+front+['ClutchDrive_shaft'],'section','Main clutch axial section | nested sleeve, relieved bearing and keyed support',(0,0,1),clip)
    draw(['ClutchStack_bearing','ClutchStack_sleeve','ClutchStack_thrust'],'internals','Enclosing collars hidden | separate bearing, sleeve and thrust collar',(1,1,.6))
    draw(['ClutchStack_sleeve'],'sleeve','Positive sleeve | provisional HB24-spline dimensional transfer',(1,1,.6))
    draw(['ClutchCollar_collar']+[n for n in new if 'Key' in n],'keys','Cone support hidden | four keys in actual receiving beds',(1,1,.6))
    clip=Part.makeBox(50,200,2,origin+App.Vector(975,-100,-1))
    draw(['ClutchCollar_collar','ClutchStack_bearing','ClutchStack_thrust','ClutchStack_snap'],'retention','Front retention section | thrust collar and separate external snap ring',(0,0,1),clip)
    report['render_hashes']={f.name:sha(f) for f in view.glob('*.png')};write(out/'report.json',report)
    assert sha(native_parent)==pq['native_sha256']
    for path,h in hashes.items():assert sha(REPO/path)==h,path
    print('Native,7definition STEP,10placed STEP and seven views saved.',flush=True)
    assert not overlaps,'See material_checks.json'
finally:runtime.close()
