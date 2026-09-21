"""Install the front coupling and external spring in the checked drive model."""
import argparse,json,subprocess,sys
from pathlib import Path
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];REPO=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=HERE/'front_clutch_build')
p.add_argument('--worker',action='store_true');a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--output',str(out),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part,numpy as np
    from lib.cad_build import leaves,metadata,shape_signature,COLORS
    from lib.worker import same_shape,placement_errors,check_build
    from lib.visual_review import shaded
    from front_clutch_parts import build
    parent=HERE/'clutch_drive_build';native_parent=parent/'TransmissionWithClutchDrive.FCStd'
    pq=read(parent/'qualification.json');assert pq['passed'] and sha(native_parent)==pq['native_sha256']
    dossier=read(HERE/'front_clutch_sources.json');records={r['record_id']:r for r in dossier['records']}
    for path,h in dossier['source_assets'].items():assert sha(REPO/path)==h,path
    inputs=[Path(__file__)]+[HERE/n for n in ['front_clutch_parts.py','front_clutch_controls.json','front_clutch_sources.json',
        'clutch_drive_controls.json','air_pressure_pump_parts.py','transmission_input_parts.py','transmission_core_parts.py','transmission_stud_parts.py']]
    hashes={str(f.relative_to(REPO)):sha(f) for f in inputs};(out/'inputs').mkdir(exist_ok=True)
    for path in inputs:(out/'inputs'/path.name).write_bytes(path.read_bytes())
    c=read(HERE/'front_clutch_controls.json')['controls'];dc=read(HERE/'clutch_drive_controls.json')['controls']
    doc=App.openDocument(str(native_parent));doc.recompute();old={i['id']:i for i in leaves(doc.Root)}
    signatures={n:shape_signature(i['shape']) for n,i in old.items()};places={n:i['shape'].Placement for n,i in old.items()}
    parts,occ,revised,d,spine=build(c,dc,old['ClutchDrive_shaft']['target'].Shape,old['ClutchDrive_box']['target'].Shape)
    changed=['ClutchDrive_shaft','ClutchDrive_box'];revision={}
    for key,name in [('shaft','ClutchDrive_shaft'),('box','ClutchDrive_box')]:
        target=old[name]['target'];target.Shape.exportBrep(str(out/'inputs'/('parent_'+key+'.brep')))
        target.Tip.Shape=revised[key];revision[key]=target.Name
        metadata(target,FrontClutchRevision='Source-shaped8mm shaft shoulder fillets and matching M855 passage relief; old native preserved.',
            ParameterUpdate='Rebuild front_clutch_build.py from front_clutch_controls.json and checked parent')
    group=doc.addObject('App::Part','FrontClutch');doc.TransmissionCore.addObject(group)
    metadata(group,Scope='SH945A front coupling, SH849A split collar, SH849B spring and two fastening sets. Main collar/cones/bearings remain pending.')
    identity=dict(coupling=('SH945A','SNL:73:016'),half_flange=('SH849A','SNL:94:013'),spring=('SH849B','SNL:219:024'),
        bolt=('','SNL:33:004'),nut=('','SNL:33:004'),washer=('','SNL:33:004'))
    bodies={}
    for key,s in parts.items():
        body=doc.addObject('PartDesign::Body','Def_FrontClutch_'+key);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedPart').Shape=s;mark,rid=identity[key]
        metadata(body,DefinitionId='front_clutch_'+key,OriginalMark=mark,SurveyIds=records[rid]['part_ids'],SourceRecord=rid,
            Representation='assembly',Coverage='partial',ParameterUpdate='Rebuild front_clutch_build.py from front_clutch_controls.json',
            ReconstructionNotes='Documented geometric approximation; see front_clutch_sources.json for identity, dimensional and quantity interpretations.')
        if key=='coupling':metadata(body,DimensionTransfer='HB SH864B dimensions transferred provisionally to SNL SH945A; applicability unproven.')
        if key=='spring':metadata(body,SpringInterpretation='5free+2seating turns;5-3/8in interpreted as inside diameter; wire/pitch/installed-length conventions inferred.')
        bodies[key]=body
    for row in occ:
        key=row['key'];rid=identity[key][1];link=doc.addObject('App::Link',row['name']);group.addObject(link);link.setLink(bodies[key])
        link.LinkPlacement=App.Placement(App.Vector(*row['xyz']),App.Rotation(App.Vector(1,0,0),row['angle']))
        metadata(link,OccurrenceId=row['name'],SurveyIds=records[rid]['part_ids'],SourceRecord=rid,Subsystem='Drivetrain',QuantityRole='One physical component')
        if key in ['bolt','nut','washer']:metadata(link,SourceSet=records[rid]['part_ids'][0],SetPiece=key)
    doc.Definitions.Visibility=False;doc.recompute();native=out/'TransmissionWithFrontClutch.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items};origin=doc.TransmissionCore.Placement.Base
    new=[r['name'] for r in occ];affected=new+changed
    assert len(items)==len(byid)==1530 and len(new)==10 and len(affected)==12
    for n,i in byid.items():
        assert i['shape'].isValid() and len(i['shape'].Solids)==1,n
        if n in old:
            t,r=placement_errors(i['shape'].Placement,places[n]);assert t<1e-6 and r<1e-8,n
            if n not in changed:assert same_shape(signatures[n],shape_signature(i['shape'])),n
    spine.exportBrep(str(out/'spring_spine.brep'))
    report=dict(status='front_clutch_candidate',native_sha256=sha(native),parent_native_sha256=sha(native_parent),input_hashes=hashes,
        controls=c,drive_controls=dc,details=d,native_occurrences=1530,new_physical_occurrences=10,new_ids=new,changed_ids=changed,
        affected_ids=affected,unchanged_parent_occurrences=1518,spring_spine_sha256=sha(out/'spring_spine.brep'),
        standard_assembly_modified=False,main_clutch_complete=False,historical_fit_qualified=False,complete_tank=False)
    write(out/'report.json',report);print('Saved and reopened1530 leaves,10new,2revised,1518unchanged.',flush=True)
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
    exchange=out/'FrontClutchInstallation.step';Part.makeCompound([byid[n]['shape'] for n in affected]).exportStep(str(exchange))
    report['step_sha256']=sha(exchange);report['step_ids']=affected
    keys=['Def_FrontClutch_'+k for k in parts]+list(revision.values());path=out/'FrontClutchDefinitions.step'
    Part.makeCompound([doc.getObject(k).Shape for k in keys]).exportStep(str(path));write(out/'definition_order.json',keys)
    report['definition_step_sha256']=sha(path)
    view=out/'previews';view.mkdir(exist_ok=True);COLORS.update(Clutch=(.67,.61,.46),Shaft=(.64,.66,.70),Spring=(.42,.46,.48),Fastener=(.66,.67,.69))
    def draw(names,file,title,direction,clip=None):
        selected=[]
        for n in names:
            i=byid[n];s=i['shape'] if clip is None else i['shape'].common(clip)
            if s.isNull() or not s.Solids:continue
            color='Spring' if n=='FrontClutch_Spring' else ('Shaft' if n=='ClutchDrive_shaft' else ('Fastener' if n.startswith('FrontClutch_Set') else ('Clutch' if n.startswith(('FrontClutch_','ClutchDrive_')) else i['system'])))
            selected.append(dict(i,shape=s,target=SimpleNamespace(Shape=s),definition=n,system=color))
        shaded(selected,view/(file+'.svg'),direction,title)
    drive=[n for n in byid if n.startswith(('ClutchDrive_','AirPump_','PumpMount_','InputHousing_')) or n=='CenterTransmissionCore_bevel_cover']
    draw(new+drive,'isometric','Front clutch coupling and spring | main clutch still under reconstruction',(1,1,.65))
    draw(new+['ClutchDrive_shaft','ClutchDrive_box','ClutchDrive_drum'],'mechanism','Front clutch | seven-turn spring, split flange and two fastening sets',(1,1,.6))
    clip=Part.makeBox(600,2,260,origin+App.Vector(450,-1,-130))
    draw(new+['ClutchDrive_shaft','ClutchDrive_box','ClutchDrive_drum'],'section','Front clutch centre section | diameter conventions and hidden profiles inferred',(0,-1,0),clip)
    clip=Part.makeBox(2,210,210,origin+App.Vector(c['clamp_bolt_x']-1,-105,-105))
    draw(new+['ClutchDrive_shaft'],'clamp_section','Spring flange transverse section | two off-axis bolts and nominal shaft contact',(1,0,0),clip)
    draw([n for n in new if n!='FrontClutch_Spring']+['ClutchDrive_shaft'],'spring_hidden','Front clutch with spring hidden | female spline and blended shaft shoulders',(1,1,.6))
    report['render_hashes']={f.name:sha(f) for f in view.glob('*.png')};write(out/'report.json',report)
    assert sha(native_parent)==pq['native_sha256']
    for path,h in hashes.items():assert sha(REPO/path)==h,path
    print('Native,8definitionSTEP,12placedSTEP and five views saved.',flush=True)
    assert not overlaps,'See material_checks.json'
finally:runtime.close()
