"""Install the pump and source-counted supports in the transmission checkpoint."""
import argparse,json,subprocess,sys
from pathlib import Path
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];REPO=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,default=HERE/'air_pump_mount_build')
p.add_argument('--worker',action='store_true');p.add_argument('--skip-context',action='store_true')
a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
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
    from air_pressure_pump_parts import build as pump_parts
    from air_pump_mount_parts import build
    parent=HERE/'transmission_case_mount_trial_build';pump=HERE/'air_pressure_pump_build'
    parent_path=parent/'MX5CaseMountTrial.FCStd';pump_path=pump/'AirPressurePump.FCStd'
    q=read(parent/'qualification.json');pq=read(pump/'qualification.json')
    assert q['passed'] and sha(parent_path)==q['native_sha256']
    assert pq['passed'] and sha(pump_path)==pq['native_sha256']
    inputs=[Path(__file__),HERE/'air_pump_mount_parts.py',HERE/'air_pump_mount_controls.json',
        HERE/'air_pressure_pump_controls.json',HERE/'air_pressure_pump_parts.py',HERE/'air_pressure_pump_sources.json',HERE/'air_pump_mount_sources.json',
        HERE/'transmission_input_installation_parts.py',HERE/'transmission_stud_parts.py']
    hashes={str(path.relative_to(REPO)):sha(path) for path in inputs}
    for path in inputs:
        dst=out/'inputs'/path.name;dst.parent.mkdir(exist_ok=True);dst.write_bytes(path.read_bytes())
    c=read(HERE/'air_pump_mount_controls.json')['controls']
    pc=read(HERE/'air_pressure_pump_controls.json')['controls'];pc['foot_hole_y']=c['pump_foot_hole_y'];pc['foot_extension']=c['pump_foot_extension']
    dossier=read(HERE/'air_pressure_pump_sources.json');records={r['record_id']:r for r in dossier['records']}
    for path,h in read(HERE/'air_pump_mount_sources.json')['source_assets'].items():assert sha(REPO/path)==h,path
    doc=App.openDocument(str(parent_path));doc.recompute();before=leaves(doc.Root);old={i['id']:i for i in before}
    signatures={n:shape_signature(i['shape']) for n,i in old.items()};places={n:i['shape'].Placement for n,i in old.items()}
    origin=doc.TransmissionCore.Placement.Base
    cover_id='CenterTransmissionCore_bevel_cover';house_id='InputHousing_housing'
    parts,occ,revised,details=build(c,pc,old[cover_id]['target'].Shape,old[house_id]['target'].Shape)
    for key,name in [('cover',cover_id),('housing',house_id)]:
        old[name]['target'].Shape.exportBrep(str(out/'inputs'/('parent_'+key+'.brep')))
        old[name]['target'].Tip.Shape=revised[key]
        metadata(old[name]['target'],PumpMountRevision='Integral blind bosses for estimated pump support arrangement; original receivers preserved.')
    pd=App.openDocument(str(pump_path));pd.recompute();pump_items=leaves(pd.Root)
    changed_pump,_,_=pump_parts(pc)
    fuel=doc.addObject('App::Part','FuelPressureInstallation');doc.Root.addObject(fuel)
    fuel.Placement=doc.TransmissionCore.Placement
    pump_root=doc.addObject('App::Part','AirPressurePump');fuel.addObject(pump_root)
    pump_root.Placement=App.Placement(App.Vector(*details['pump_origin']),App.Rotation())
    metadata(pump_root,SurveyIds=['P_dd55a02fabc8964b'],Subsystem='FuelPressure',
        Scope='51 core pieces plus12 base fasteners in adjoining group. Drive and fluid circuit remain incomplete.')
    bodies={};pump_groups={}
    for item in pump_items:
        target=item['target'];key=target.DefinitionId
        if key not in bodies:
            body=doc.addObject('PartDesign::Body','Def_InstalledPump_'+key);doc.Definitions.addObject(body)
            body.newObject('PartDesign::Feature','ReconstructedPart').Shape=changed_pump['base'] if key=='air_pressure_pump_base' else target.Shape.copy()
            values={name:getattr(target,name) for name in target.PropertiesList if target.getGroupOfProperty(name)=='Reconstruction'}
            metadata(body,**values)
            if key=='air_pressure_pump_base':
                metadata(body,InstallationRevision='Foot holes moved toY+/-90.5; ledges extended4mm for head clearance. Rebuild air_pump_mount_build.py.')
            bodies[key]=body
        group_name=item['object'].getParentGeoFeatureGroup().Name
        if group_name not in pump_groups:
            pump_groups[group_name]=doc.addObject('App::Part','Installed_'+group_name);pump_root.addObject(pump_groups[group_name])
        link=doc.addObject('App::Link',item['id']);pump_groups[group_name].addObject(link);link.setLink(bodies[key])
        link.LinkPlacement=item['shape'].Placement
        metadata(link,OccurrenceId=item['id'],Subsystem='FuelPressure',SourceRecord=getattr(item['object'],'SourceRecord',''))
    App.closeDocument(pd.Name)
    identity=dict(bracket_left=('MX101','SNL:36:012'),bracket_right=('MX100','SNL:36:013'),
        mx98_stud=('MX98','SNL:240:021'),mx98_nut=('','SNL:240:022'),mx98_cotter=('','SNL:240:023'),
        mx99_stud=('MX99','SNL:231:022'),mx102_jam=('MX102','SNL:231:023'),
        half_nut=('','SNL:231:025'),small_nut=('','SNL:231:024'),washer=('','SNL:231:026'),
        base_bolt=('','SNL:30:004'),base_nut=('','SNL:30:004'),base_washer=('','SNL:30:004'))
    mount_bodies={}
    for key,s in parts.items():
        body=doc.addObject('PartDesign::Body','Def_PumpMount_'+key);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedPart').Shape=s
        mark,record=identity[key]
        metadata(body,DefinitionId='air_pump_mount_'+key,OriginalMark=mark,SurveyIds=records[record]['part_ids'],
            SourceRecord=record,Representation='assembly',Coverage='partial',
            ParameterUpdate='Rebuild air_pump_mount_build.py from air_pump_mount_controls.json',
            ReconstructionNotes='Printed identity and selected sizes; inferred geometry, position and historical fit.')
        mount_bodies[key]=body
    groups={}
    for row in occ:
        name=row['parent']
        if name not in groups:
            groups[name]=doc.addObject('App::Part','AirPump_'+name)
            (fuel if name=='BaseFasteners' else doc.TransmissionCore).addObject(groups[name])
        body=mount_bodies[row['key']]
        # The base set has its own definitions and source identity, even where
        # smooth inspection geometry matches a separately listed SAE component.
        link=doc.addObject('App::Link',row['name']);groups[name].addObject(link);link.setLink(body)
        link.LinkPlacement=App.Placement(App.Vector(*row['xyz']),App.Rotation())
        record='SNL:30:004' if name=='BaseFasteners' else identity[row['key']][1]
        values=dict(OccurrenceId=row['name'],Subsystem=row['subsystem'],SourceRecord=record,
            SurveyIds=records[record]['part_ids'],QuantityRole='One physical component')
        if name=='BaseFasteners':values.update(SourceSet='P_55c06904318526e8',SetPiece=row['name'].rsplit('_',1)[-1])
        metadata(link,**values)
    doc.Definitions.Visibility=False;doc.recompute();native=out/'TransmissionWithAirPump.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items}
    new=[i['id'] for i in pump_items]+[r['name'] for r in occ];changed=[cover_id,house_id]
    assert len(items)==len(byid)==1490 and len(new)==83
    for n,i in byid.items():
        assert i['shape'].isValid() and len(i['shape'].Solids)==1,n
        if n in old:
            t,r=placement_errors(i['shape'].Placement,places[n]);assert t<1e-6 and r<1e-8,n
            if n not in changed:assert same_shape(signatures[n],shape_signature(i['shape'])),n
    preserved_pump=0
    for row in pump_items:
        if row['id']=='AirPump_base':continue
        expected=row['shape'].copy();expected.translate(origin+App.Vector(*details['pump_origin']))
        assert same_shape(shape_signature(expected),shape_signature(byid[row['id']]['shape'])),row['id']
        preserved_pump+=1
    assert preserved_pump==50
    report=dict(status='pump_mount_candidate',native_sha256=sha(native),parent_native_sha256=sha(parent_path),pump_native_sha256=sha(pump_path),
        input_hashes=hashes,controls=c,pump_controls=pc,details=details,new_ids=new,changed_ids=changed,
        native_occurrences=len(items),new_physical_occurrences=83,new_support_and_fastener_occurrences=32,
        unchanged_parent_occurrences=1405,unchanged_pump_occurrences=preserved_pump,pump_base_revised=True,standard_assembly_modified=False,
        complete_installation=False,clutch_and_belt_verified=False,complete_tank=False,historical_fit_qualified=False)
    write(out/'report.json',report);print('Reopened1490 leaves;83 new,2 changed,1405 prior leaves unchanged.',flush=True)
    context=[]
    if not a.skip_context:
        b=check_build(STAGE/'build');td=App.openDocument(b['build']['top_document']);td.recompute()
        context=[i for i in leaves(td.Root) if i['representation']=='assembly']
        report['standard_native_hashes']=b['native_hashes']
    physical=items+context;boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].copy().cleaned().BoundBox for i in physical]])
    pairs=[];seen=set()
    for n in new+changed:
        s=byid[n]['shape'];b=s.copy().cleaned().BoundBox;bb=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
        near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
        for idx in near:
            other=physical[idx];pair=tuple(sorted([n,other['id']]))
            if n==other['id'] or pair in seen:continue
            seen.add(pair);v=s.common(other['shape']).Volume
            pairs.append(dict(a=n,b=other['id'],intersection_mm3=v))
        write(out/'material_progress.json',dict(last=n,pairs=len(pairs),overlaps=[r for r in pairs if r['intersection_mm3']>1e-5]))
    conflicts=[r for r in pairs if r['intersection_mm3']>1e-5]
    report.update(material_pairs=len(pairs),overlaps=conflicts,material_passed=not conflicts,standard_context_checked=not a.skip_context)
    write(out/'material_checks.json',dict(passed=not conflicts,pairs=pairs,native_sha256=sha(native),standard_context_checked=not a.skip_context))
    write(out/'report.json',report);print('Material pairs',len(pairs),'conflicts',json.dumps(conflicts),flush=True)
    selected=[byid[n] for n in new+changed]
    exchange=out/'AirPumpInstallation.step';Part.makeCompound([i['shape'] for i in selected]).exportStep(str(exchange))
    report['step_sha256']=sha(exchange);report['step_ids']=[i['id'] for i in selected]
    defs=list(parts)+['cover','housing','pump_base'];local=[doc.getObject('Def_PumpMount_'+key).Shape for key in parts]
    local += [byid[cover_id]['target'].Shape,byid[house_id]['target'].Shape,byid['AirPump_base']['target'].Shape]
    definitions=out/'AirPumpMountDefinitions.step';Part.makeCompound(local).exportStep(str(definitions))
    write(out/'definition_order.json',defs);report['definition_step_sha256']=sha(definitions)
    view=out/'previews';view.mkdir(exist_ok=True)
    COLORS.update(Pump=(.66,.54,.30),Bracket=(.43,.57,.47),Hardware=(.66,.67,.69))
    def draw(names,file,title,view_direction,clip=None):
        chosen=[]
        for n in names:
            i=byid[n];s=i['shape'] if clip is None else i['shape'].common(clip)
            if s.isNull() or not s.Solids:continue
            system='Pump' if n.startswith('AirPump_') else ('Bracket' if n.endswith('Bracket') else ('Hardware' if n.startswith('PumpMount_') else i['system']))
            chosen.append(dict(i,shape=s,target=SimpleNamespace(Shape=s),definition=n,system=system))
        shaded(chosen,view/(file+'.svg'),view_direction,title)
    context_ids=[i['id'] for i in items if i['id'].startswith(('InputHousing_','InputMount_','InputFeed_')) or i['id']==cover_id]
    draw(new+context_ids,'isometric','Air pump installation | inferred supports; clutch drive and belt pending',(1,1,.65))
    draw([n for n in new if n.startswith('PumpMount_')]+context_ids,'supports','Pump supports | source-counted brackets, stepped studs and attachment sets',(1,1,.65))
    section=Part.makeBox(600,2,700,origin+App.Vector(140,c['pump_foot_hole_y']-1,40))
    draw(new+context_ids,'side_section','Pump attachment section | rear blind stud and four base fasteners',(0,-1,0),section)
    draw(new+context_ids,'front','Pump installation | front view; drive plane remains conditional',(1,0,0))
    report['render_hashes']={f.name:sha(f) for f in view.glob('*.png')};write(out/'report.json',report)
    assert sha(parent_path)==q['native_sha256'] and sha(pump_path)==pq['native_sha256']
    for path,h in hashes.items():assert sha(REPO/path)==h,path
    print('Native, STEP and four installation views saved.',flush=True)
    assert not conflicts,'See material_checks.json'
finally:runtime.close()
