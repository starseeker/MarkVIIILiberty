"""Install the catalogue sliding collar and correct its front coupling interface."""
import argparse,json,subprocess,sys
from pathlib import Path
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];REPO=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=HERE/'clutch_collar_build')
p.add_argument('--worker',action='store_true');a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--output',str(out),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part,numpy as np
    from lib.cad_build import leaves,metadata,shape_signature,COLORS
    from lib.worker import same_shape,placement_errors,check_build
    from lib.visual_review import shaded
    from clutch_collar_parts import build
    parent=HERE/'front_clutch_build';native_parent=parent/'TransmissionWithFrontClutch.FCStd'
    pq=read(parent/'qualification.json');assert pq['passed'] and sha(native_parent)==pq['native_sha256']
    dossier=read(HERE/'clutch_collar_sources.json');records={r['record_id']:r for r in dossier['records']}
    for path,h in dossier['source_assets'].items():assert sha(REPO/path)==h,path
    inputs=[Path(__file__)]+[HERE/n for n in ['clutch_collar_parts.py','clutch_collar_controls.json','clutch_collar_sources.json',
        'clutch_drive_controls.json','clutch_drive_parts.py','air_pressure_pump_parts.py','transmission_input_parts.py','transmission_core_parts.py','transmission_stud_parts.py']]
    hashes={str(f.relative_to(REPO)):sha(f) for f in inputs};(out/'inputs').mkdir(exist_ok=True)
    for path in inputs:(out/'inputs'/path.name).write_bytes(path.read_bytes())
    c=read(HERE/'clutch_collar_controls.json')['controls'];dc=read(HERE/'clutch_drive_controls.json')['controls']
    doc=App.openDocument(str(native_parent));doc.recompute();old={i['id']:i for i in leaves(doc.Root)}
    signatures={n:shape_signature(i['shape']) for n,i in old.items()};places={n:i['shape'].Placement for n,i in old.items()}
    parts,occ,coupling,spine,d=build(c,dc)
    changed=sorted(n for n in old if n.startswith('FrontClutch_'));shift=App.Vector(c['external_shift'],0,0)
    for name in ['FrontClutch_UpperFlange','FrontClutch_Spring']:
        target=old[name]['target'];shape=target.Shape.copy();shape.translate(shift);target.Tip.Shape=shape
    old['FrontClutch_Coupling']['target'].Tip.Shape=coupling
    metadata(old['FrontClutch_Coupling']['target'],CollarRevision='SNL21 second flange and end-bearing pocket; prior single-flange topology superseded in this candidate.')
    for n in changed:
        if n.startswith('FrontClutch_Set'):
            obj=old[n]['object'];place=obj.LinkPlacement;place.Base+=shift;obj.LinkPlacement=place
    group=doc.addObject('App::Part','ClutchCollar');doc.TransmissionCore.addObject(group)
    metadata(group,Scope='SH999A collar,SH997A/B end-bearing ring/bush,six cap screws,SH999C locking wire. Main internal stack remains pending.')
    identity=dict(collar=('SH999A','SNL:67:019'),ring=('SH997A','SNL:164:030'),bush=('SH997B','SNL:43:014'),
        screw=('','SNL:200:002'),wire=('SH999C','SNL:276:003'))
    bodies={}
    for key,s in parts.items():
        body=doc.addObject('PartDesign::Body','Def_ClutchCollar_'+key);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedPart').Shape=s;mark,rid=identity[key]
        metadata(body,DefinitionId='clutch_collar_'+key,OriginalMark=mark,SurveyIds=records[rid]['part_ids'],SourceRecord=rid,
            Representation='assembly',Coverage='partial',ParameterUpdate='Rebuild clutch_collar_build.py from clutch_collar_controls.json',
            ReconstructionNotes='Documented geometric approximation; exact internal profile, thread and crankshaft interfaces remain unqualified. See the packet.')
        if key=='wire':metadata(body,PrintedSpecification='W.&M.gauge16,soft steel,26in;1.5mm geometric diameter and formed route inferred.')
        bodies[key]=body
    for row in occ:
        key=row['key'];rid=identity[key][1];link=doc.addObject('App::Link',row['name']);group.addObject(link);link.setLink(bodies[key])
        link.LinkPlacement=App.Placement(App.Vector(*row['xyz']),App.Rotation(App.Vector(1,0,0),row['angle']))
        metadata(link,OccurrenceId=row['name'],SurveyIds=records[rid]['part_ids'],SourceRecord=rid,Subsystem='Drivetrain',QuantityRole='One physical component')
    doc.Definitions.Visibility=False;doc.recompute();native=out/'TransmissionWithClutchCollar.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items};origin=doc.TransmissionCore.Placement.Base
    new=[r['name'] for r in occ];affected=new+changed
    assert len(items)==len(byid)==1540 and len(new)==10 and len(affected)==20
    for n,i in byid.items():
        assert i['shape'].isValid() and len(i['shape'].Solids)==1,n
        if n in old and n not in changed:
            t,r=placement_errors(i['shape'].Placement,places[n]);assert t<1e-6 and r<1e-8,n
            assert same_shape(signatures[n],shape_signature(i['shape'])),n
    spine.exportBrep(str(out/'locking_wire_spine.brep'))
    external=Part.Shape();external.read(str(parent/'spring_spine.brep'));external.translate(shift);external.exportBrep(str(out/'external_spring_spine.brep'))
    report=dict(status='clutch_collar_candidate',native_sha256=sha(native),parent_native_sha256=sha(native_parent),input_hashes=hashes,
        controls=c,drive_controls=dc,details=d,native_occurrences=1540,new_physical_occurrences=10,new_ids=new,changed_ids=changed,
        affected_ids=affected,unchanged_parent_occurrences=1520,locking_wire_spine_sha256=sha(out/'locking_wire_spine.brep'),
        external_spring_spine_sha256=sha(out/'external_spring_spine.brep'),
        standard_assembly_modified=False,main_clutch_complete=False,historical_fit_qualified=False,complete_tank=False)
    write(out/'report.json',report);print('Saved and reopened1540 leaves,10new,10affected parent leaves,1520unchanged.',flush=True)
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
    path=out/'ClutchCollarInstallation.step';Part.makeCompound([byid[n]['shape'] for n in affected]).exportStep(str(path));report.update(step_sha256=sha(path),step_ids=affected)
    keys=['Def_ClutchCollar_'+k for k in parts]+[byid[n]['target'].Name for n in ['FrontClutch_Coupling','FrontClutch_UpperFlange','FrontClutch_Spring']]
    path=out/'ClutchCollarDefinitions.step';Part.makeCompound([doc.getObject(k).Shape for k in keys]).exportStep(str(path));write(out/'definition_order.json',keys);report['definition_step_sha256']=sha(path)
    view=out/'previews';view.mkdir(exist_ok=True);COLORS.update(Clutch=(.67,.61,.46),Shaft=(.64,.66,.70),Spring=(.42,.46,.48),Fastener=(.66,.67,.69),Belt=(.24,.25,.23),Bronze=(.68,.52,.28))
    def draw(names,file,title,direction,clip=None):
        selected=[]
        for n in names:
            i=byid[n];s=i['shape'] if clip is None else i['shape'].common(clip)
            if s.isNull() or not s.Solids:continue
            color='Spring' if n=='FrontClutch_Spring' else ('Shaft' if n=='ClutchDrive_shaft' else ('Clutch' if n.startswith(('FrontClutch_','ClutchDrive_','ClutchCollar_')) else i['system']))
            if n=='ClutchDrive_belt':color='Belt'
            if n.startswith(('ClutchCollar_Screw','FrontClutch_Set')) or n in ['ClutchCollar_wire','ClutchCollar_ring']:color='Fastener'
            if n=='ClutchCollar_bush':color='Bronze'
            selected.append(dict(i,shape=s,target=SimpleNamespace(Shape=s),definition=n,system=color))
        shaded(selected,view/(file+'.svg'),direction,title)
    drive=[n for n in byid if n.startswith(('ClutchDrive_','AirPump_','PumpMount_','InputHousing_')) or n=='CenterTransmissionCore_bevel_cover']
    draw(new+changed+drive,'isometric','Clutch sliding collar and end bearing | catalogue coupling topology',(1,1,.65))
    mechanism=new+changed+['ClutchDrive_shaft','ClutchDrive_box','ClutchDrive_drum']
    draw(mechanism,'mechanism','Clutch collar | main internal bearing, sleeve and cone stack still pending',(1,1,.6))
    clip=Part.makeBox(600,2,270,origin+App.Vector(450,-1,-135))
    draw(mechanism,'section','Clutch axial section | two coupling flanges and captured end-bearing ring',(0,-1,0),clip)
    clip=Part.makeBox(180,270,2,origin+App.Vector(760,-135,-1))
    draw(new+['FrontClutch_Coupling','ClutchDrive_shaft'],'joint_section','Collar joint section | blind screws and separate end-bearing ring and bush',(0,0,1),clip)
    draw([n for n in new if n.startswith('ClutchCollar_Screw') or n=='ClutchCollar_wire'],'locking_wire','Collar screw locking wire | six drilled heads and inferred paired twist',(1,1,.7))
    draw([n for n in new if n!='ClutchCollar_collar']+['FrontClutch_Coupling'],'collar_hidden','Collar hidden | end-bearing stack and six actual fastening screws',(1,1,.6))
    report['render_hashes']={f.name:sha(f) for f in view.glob('*.png')};write(out/'report.json',report)
    assert sha(native_parent)==pq['native_sha256']
    for path,h in hashes.items():assert sha(REPO/path)==h,path
    print('Native,8definition STEP,20placed STEP and six views saved.',flush=True)
    assert not overlaps,'See material_checks.json'
finally:runtime.close()
