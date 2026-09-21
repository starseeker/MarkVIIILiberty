"""Add the clutch-stop drive and a closed belt; update the coupled pump mounts."""
import argparse,json,subprocess,sys
from pathlib import Path
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];REPO=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,default=HERE/'clutch_drive_build');p.add_argument('--worker',action='store_true')
p.add_argument('--skip-context',action='store_true');a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        cmd=[sys.executable,__file__,'--output',str(out),'--worker']
        if a.skip_context:cmd.append('--skip-context')
        sys.exit(subprocess.run(cmd,env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part,numpy as np
    from lib.cad_build import leaves,metadata,shape_signature,COLORS
    from lib.worker import same_shape,placement_errors,check_build
    from lib.visual_review import shaded
    from clutch_drive_parts import build
    from air_pump_mount_parts import build as mounts
    parent=HERE/'air_pump_mount_build';parent_path=parent/'TransmissionWithAirPump.FCStd'
    pq=read(parent/'qualification.json');pr=read(parent/'report.json')
    assert pq['passed'] and sha(parent_path)==pr['native_sha256']
    sources=read(HERE/'clutch_drive_sources.json');records={r['record_id']:r for r in sources['records']}
    for path,h in sources['source_assets'].items():assert sha(REPO/path)==h,path
    inputs=[Path(__file__)]+[HERE/n for n in ['clutch_drive_parts.py','clutch_drive_controls.json','clutch_drive_sources.json',
        'air_pump_mount_parts.py','air_pump_mount_controls.json','air_pressure_pump_parts.py','air_pressure_pump_controls.json',
        'transmission_input_parts.py','transmission_input_controls.json','transmission_stud_parts.py','transmission_core_parts.py',
        'transmission_input_installation_parts.py']]
    hashes={str(path.relative_to(REPO)):sha(path) for path in inputs}
    (out/'inputs').mkdir(exist_ok=True)
    for path in inputs:(out/'inputs'/path.name).write_bytes(path.read_bytes())
    c=read(HERE/'clutch_drive_controls.json')['controls'];pc=pr['pump_controls']
    inp=read(HERE/'transmission_input_controls.json')
    parts,occ,flange,d=build(c,pc,inp['stack'],inp['bearing'])
    print('Constructed8 definitions and30 drive pieces.',flush=True)
    mc=read(HERE/'air_pump_mount_controls.json')['controls']
    mc['belt_drive_pitch_radius']=d['belt']['drive_pitch_radius'];mc['belt_pump_pitch_radius']=d['belt']['pump_pitch_radius']
    cv=Part.Shape();cv.read(str(parent/'inputs/parent_cover.brep'))
    hs=Part.Shape();hs.read(str(parent/'inputs/parent_housing.brep'))
    mp,mo,mr,md=mounts(mc,pc,cv,hs)
    assert abs(md['pump_origin'][2]-d['belt']['center_distance'])<1e-8
    assert abs(md['belt']['plane_x']-c['groove_plane'])<1e-8
    doc=App.openDocument(str(parent_path));doc.recompute();old={i['id']:i for i in leaves(doc.Root)}
    signatures={n:shape_signature(i['shape']) for n,i in old.items()};placements={n:i['shape'].Placement for n,i in old.items()}
    for key,s in mp.items():doc.getObject('Def_PumpMount_'+key).Tip.Shape=s
    for row in mo:doc.getObject(row['name']).LinkPlacement=App.Placement(App.Vector(*row['xyz']),App.Rotation())
    # Receiving castings do not depend on the small height update. Check rather
    # than silently revising them a second time.
    for key,name in [('cover','CenterTransmissionCore_bevel_cover'),('housing','InputHousing_housing')]:
        assert same_shape(shape_signature(mr[key]),shape_signature(old[name]['target'].Shape)),name
    doc.AirPressurePump.Placement=App.Placement(App.Vector(*md['pump_origin']),App.Rotation())
    old['InputHousing_coupling']['target'].Tip.Shape=flange
    metadata(old['InputHousing_coupling']['target'],ClutchDriveRevision='Eight holes from SNL31:013/HB118 replace six inferred holes; original shaft fit retained.',
        ParameterUpdate='Rebuild clutch_drive_build.py from clutch_drive_controls.json and frozen transmission input controls')
    for key in mp:metadata(doc.getObject('Def_PumpMount_'+key),ParameterUpdate='Rebuild clutch_drive_build.py: support height follows selected closed belt.')
    assembly=doc.addObject('App::Part','ClutchStopDrive');doc.TransmissionCore.addObject(assembly)
    metadata(assembly,Scope='M855/M856/M858, SNL cardan shaft and eight fastening sets. Main compound clutch and brake band remain unfinished.')
    belt_group=doc.addObject('App::Part','AirPumpBeltDrive');doc.FuelPressureInstallation.addObject(belt_group)
    identity=dict(drum=('M858','SNL:83:035'),box=('M855','SNL:34:012'),half_cover=('M856','SNL:74:027'),
        shaft=('SH1000A','SNL:211:031'),bolt=('','SNL:31:013'),nut=('','SNL:31:013'),washer=('','SNL:31:013'),belt=('SH900G','SNL:18:011'))
    bodies={}
    for key,s in parts.items():
        body=doc.addObject('PartDesign::Body','Def_ClutchDrive_'+key);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedPart').Shape=s
        mark,rid=identity[key]
        metadata(body,DefinitionId='clutch_drive_'+key,OriginalMark=mark,SurveyIds=records[rid]['part_ids'],SourceRecord=rid,
            Representation='assembly',Coverage='partial',ParameterUpdate='Rebuild clutch_drive_build.py from clutch_drive_controls.json',
            ReconstructionNotes='Source-counted static reconstruction; hidden contours and fit approximate. See clutch_drive_sources.json.')
        if key=='shaft':metadata(body,TransferredDimensions='HB SH864A differs from selected SNL SH1000A; applicability of HB dimensions unproven.')
        if key=='belt':metadata(body,InventoryGap='One linked-belt assembly representation; individual link count/construction unknown; scores are visual assumptions.')
        bodies[key]=body
    for row in occ:
        key=row['key'];link=doc.addObject('App::Link',row['name'])
        (belt_group if key=='belt' else assembly).addObject(link);link.setLink(bodies[key])
        link.LinkPlacement=App.Placement(App.Vector(*row['xyz']),App.Rotation(App.Vector(1,0,0),row['angle']))
        rid=identity[key][1]
        metadata(link,OccurrenceId=row['name'],SurveyIds=records[rid]['part_ids'],SourceRecord=rid,
            Subsystem='FuelPressure' if key=='belt' else 'Drivetrain',QuantityRole='One physical component/assembly representation')
        if key in ['bolt','nut','washer']:metadata(link,SourceSet=records[rid]['part_ids'][0],SetPiece=key)
    doc.Definitions.Visibility=False;doc.recompute();native=out/'TransmissionWithClutchDrive.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items};origin=doc.TransmissionCore.Placement.Base
    new=[r['name'] for r in occ];changed=['InputHousing_coupling']+pr['new_ids'];affected=new+changed
    assert len(items)==len(byid)==1520 and len(new)==30 and len(affected)==114
    for n,i in byid.items():
        assert i['shape'].isValid() and len(i['shape'].Solids)==1,n
        if n in old and n not in changed:
            assert same_shape(signatures[n],shape_signature(i['shape'])),n
            t,r=placement_errors(i['shape'].Placement,placements[n]);assert t<1e-6 and r<1e-8,n
    # Every core pump part remains geometrically unchanged and moves coherently.
    dz=md['pump_origin'][2]-pr['details']['pump_origin'][2]
    for n in pr['new_ids']:
        if not n.startswith('AirPump_'):continue
        expected=old[n]['shape'].copy();expected.translate(App.Vector(0,0,dz))
        assert same_shape(shape_signature(expected),shape_signature(byid[n]['shape'])),n
    report=dict(status='clutch_drive_candidate',native_sha256=sha(native),parent_native_sha256=sha(parent_path),input_hashes=hashes,
        controls=c,pump_controls=pc,mount_controls=mc,details=d,mount_details=md,pump_height_change_mm=dz,
        native_occurrences=1520,new_physical_occurrences=30,new_ids=new,changed_ids=changed,affected_ids=affected,
        unchanged_parent_occurrences=1406,standard_assembly_modified=False,complete_clutch=False,complete_installation=False,
        complete_tank=False,historical_fit_qualified=False,individual_belt_link_inventory_known=False)
    write(out/'report.json',report);print('Saved and reopened1520 leaves. Pump height shift',dz,flush=True)
    context=[]
    if not a.skip_context:
        b=check_build(STAGE/'build');td=App.openDocument(b['build']['top_document']);td.recompute()
        context=[i for i in leaves(td.Root) if i['representation']=='assembly'];report['standard_native_hashes']=b['native_hashes']
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
    conflicts=[r for r in pairs if r['intersection_mm3']>1e-5]
    report.update(material_pairs=len(pairs),overlaps=conflicts,material_passed=not conflicts,standard_context_checked=not a.skip_context)
    write(out/'material_checks.json',dict(passed=not conflicts,pairs=pairs,native_sha256=sha(native),standard_context_checked=not a.skip_context))
    write(out/'report.json',report);print('Material pairs',len(pairs),'conflicts',json.dumps(conflicts),flush=True)
    path=out/'ClutchDriveInstallation.step';Part.makeCompound([byid[n]['shape'] for n in affected]).exportStep(str(path))
    report['step_sha256']=sha(path);report['step_ids']=affected
    keys=['Def_ClutchDrive_'+k for k in parts]+['Def_PumpMount_'+k for k in mp]+[byid['InputHousing_coupling']['target'].Name]
    defs=out/'ClutchDriveDefinitions.step';Part.makeCompound([doc.getObject(k).Shape for k in keys]).exportStep(str(defs))
    write(out/'definition_order.json',keys);report['definition_step_sha256']=sha(defs)
    view=out/'previews';view.mkdir(exist_ok=True)
    COLORS.update(Clutch=(.67,.61,.46),Shaft=(.64,.66,.70),Belt=(.24,.22,.20),Pump=(.66,.54,.30),Bracket=(.43,.57,.47))
    def draw(names,file,title,direction,clip=None):
        chosen=[]
        for n in names:
            i=byid[n];s=i['shape'] if clip is None else i['shape'].common(clip)
            if s.isNull() or not s.Solids:continue
            color='Belt' if n=='ClutchDrive_belt' else ('Shaft' if n=='ClutchDrive_shaft' else ('Clutch' if n.startswith('ClutchDrive_') else ('Pump' if n.startswith('AirPump_') else ('Bracket' if n.startswith('PumpMount_') else i['system']))))
            chosen.append(dict(i,shape=s,target=SimpleNamespace(Shape=s),definition=n,system=color))
        shaded(chosen,view/(file+'.svg'),direction,title)
    context_ids=[n for n in byid if n.startswith(('InputHousing_','InputMount_','InputFeed_')) or n=='CenterTransmissionCore_bevel_cover']
    names=list(dict.fromkeys(affected+context_ids))
    draw(names,'isometric','Clutch-stop drive | captured shaft, eight fastening sets and linked-belt representation',(1,1,.65))
    draw(names,'opposite','Clutch-stop and pump drive | opposite isometric; mounting profiles inferred',(1,-1,.65))
    draw(names,'front','Closed pump drive | 54in assumed pitch length; pulley diameters estimated',(1,0,0))
    clip=Part.makeBox(900,2,1000,origin+App.Vector(100,-1,-200))
    draw([n for n in new if n!='ClutchDrive_belt']+['InputHousing_coupling'],'section',
        'Clutch-drive centre section | head/socket and hidden casting contours inferred',(0,-1,0),clip)
    draw([n for n in new if n not in ['ClutchDrive_drum','ClutchDrive_box','ClutchDrive_belt']]+['InputHousing_coupling'],
        'open','Clutch drive with enclosing drum and box hidden | estimated captured-head construction',(1,1,.65))
    report['render_hashes']={f.name:sha(f) for f in view.glob('*.png')};write(out/'report.json',report)
    assert sha(parent_path)==report['parent_native_sha256']
    for path,h in hashes.items():assert sha(REPO/path)==h,path
    print('Native,114-solid installation STEP,22 definitions and five views saved.',flush=True)
    assert not conflicts,'See material_checks.json'
finally:runtime.close()
