"""Install inferred M1592 collars and their documented rivets in the native fixture."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage',type=Path,required=True)
parser.add_argument('--output',type=Path,default=ROOT/'casing_wall_mount_build')
parser.add_argument('--worker',action='store_true')
args=parser.parse_args();stage=args.stage.resolve();out=args.output.resolve()
sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import read,write,sha,fingerprint,database
if not args.worker:
    out.mkdir(parents=True,exist_ok=True)
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--output',str(out),'--worker'],
                 env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui()
    import Part
    import numpy as np
    from types import SimpleNamespace
    from lib.cad_build import leaves,metadata
    from lib.worker import check_build
    from lib.model import load
    from lib.wheel_parts import button_rivet
    from lib.hull_validation import validate as validate_hull
    from lib.visual_review import shaded
    from casing_mount_parts import joint,cutter
    lock=fingerprint();build=check_build(stage/'build')
    paths=[Path(__file__),ROOT/'casing_mount_parts.py',ROOT/'casing_mount_controls.json',
           ROOT/'casing_parts.py',ROOT/'casing_controls.json',ROOT/'casing_source_rows.json',
           ROOT/'casing_joint_review.json',ROOT/'installed_pitch_route_report.json',
           ROOT/'casing_shell_passage_build/report.json',ROOT/'casing_shell_passage_build/CasingShellCandidate.FCStd']
    hashes={str(p.relative_to(ROOT)):sha(p) for p in paths}
    controls=read(paths[2]);a={k:v['value'] for k,v in controls['controls'].items()}
    casing={k:v['value'] for k,v in read(paths[4])['controls'].items()}
    sources=read(paths[5]);route=read(paths[7]);prior=read(paths[8])
    assert prior['passed'] and prior['rendering_complete'] and prior['native_sha256']==sha(paths[9])
    assert prior['authored_fingerprint']==lock and prior['tank_native_hashes']==build['native_hashes']
    tank=App.openDocument(build['build']['top_document']);tank.recompute();original=leaves(tank.Root)
    context=[i for i in original if i['id'] not in {'hull_engine_back','PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting'}]
    doc=App.openDocument(str(paths[9]));doc.recompute();before=leaves(doc.Root)
    wall=next(i for i in before if i['id']=='hull_engine_back')
    body=next(i for i in before if i['id']=='PortCasing_Body')
    angle,stations=joint(a,casing,route,prior,wall['shape'].BoundBox)
    case_tools=[cutter(s,a['case_rivet_diameter']+a['hole_diameter_clearance']) for s in stations['case']]
    wall_tools=[cutter(s,a['wall_rivet_diameter']+a['hole_diameter_clearance']) for s in stations['wall']]
    angle=angle.cut(Part.makeCompound(case_tools+wall_tools)).removeSplitter()
    updated_body=body['target'].Shape.cut(Part.makeCompound(case_tools)).removeSplitter()
    assert updated_body.cut(body['target'].Shape).Volume<1e-5
    body['target'].Tip.Shape=updated_body
    all_wall_tools=[];centers={}
    for hand in ['Port','Starboard']:
        cy=next(i for i in before if i['id']==hand+'Chain_RollerPinion')['shape'].Placement.Base.y
        centers[hand]=cy
        for shape in wall_tools:
            cut=shape.copy();cut.translate(App.Vector(0,cy,0));all_wall_tools.append(cut)
    updated_wall=wall['shape'].cut(Part.makeCompound(all_wall_tools)).removeSplitter()
    assert updated_wall.cut(wall['shape']).Volume<1e-5
    wall['target'].Tip.Shape=updated_wall
    defs={}
    obj=doc.addObject('PartDesign::Body','Def_CasingWallAngle');doc.Definitions.addObject(obj)
    feature=obj.newObject('PartDesign::Feature','FlangedCollarAndAttachmentHoles');feature.Shape=angle
    metadata(obj,DefinitionId='casing_wall_angle',Representation='assembly',Coverage='partial',
             SurveyIds=[sources['parts']['M1592']['part_id']],OriginalMark='M1592')
    defs['angle']=obj
    with database() as connection:
        for role,record in [('wall','SNL:170:002'),('case','SNL:167:009')]:
            ids=[r[0] for r in connection.execute('select distinct part_id from part_evidence where record_id=?',(record,))]
            assert len(ids)==1
            rivet=button_rivet(doc,'Def_Casing'+role.title()+'Rivet',a[role+'_rivet_diameter'],
                               a[role+'_rivet_stock_length'],stations[role][0]['grip'])
            doc.Definitions.addObject(rivet)
            metadata(rivet,DefinitionId='casing_'+role+'_rivet',Representation='assembly',Coverage='partial',
                     SurveyIds=ids,SourceRecord=record)
            defs[role]=rivet
    for hand,cy in centers.items():
        group=doc.addObject('App::Part',hand+'CasingWallJoint');doc.Root.addObject(group)
        def link(name,target,pose):
            obj=doc.addObject('App::Link',name);group.addObject(obj);obj.setLink(target);obj.LinkPlacement=pose
            metadata(obj,OccurrenceId=name,Subsystem='Drivetrain')
        link(hand+'CasingWall_Angle',defs['angle'],App.Placement(App.Vector(0,cy,0),App.Rotation()))
        for role in ['wall','case']:
            for n,s in enumerate(stations[role]):
                center=App.Vector(*s['center'])+App.Vector(0,cy,0)
                rotation=App.Rotation(App.Vector(0,1,0),App.Vector(*s['axis']))
                link(hand+'CasingWall_'+role.title()+'Rivet%02d'%n,defs[role],App.Placement(center,rotation))
    metadata(doc.Root,Scope='Chain/casing candidate with inferred M1592 collars and source-allocated wall/case rivets')
    doc.Definitions.Visibility=False;doc.recompute();native=out/'CasingWallMountCandidate.FCStd';doc.saveAs(str(native))
    App.closeDocument(doc.Name);doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root)
    assert len(items)==567
    for item in items:
        if not item['shape'].isValid() or len(item['shape'].Solids)!=1:raise ValueError('Invalid mount leaf '+item['id'])
    new=[i for i in items if i['id'].startswith(('PortCasingWall_','StarboardCasingWall_'))]
    assert len(new)==58
    changed=new+[i for i in items if i['id'] in {'hull_engine_back','PortCasing_Body','StarboardCasing_Body'}]
    physical=[i for i in context if i['representation']=='assembly']+items
    boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].BoundBox for i in physical]])
    checked=set();overlaps=[];neighbors=set()
    for first in changed:
        b=first['shape'].BoundBox;box=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
        near=np.where(np.all(boxes[:,:3]<=box[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=box[:3]-1e-7,axis=1))[0]
        for n in near:
            second=physical[n];pair=tuple(sorted([first['id'],second['id']]))
            if pair[0]==pair[1] or pair in checked:continue
            checked.add(pair);neighbors.add(second['id'])
            volume=first['shape'].common(second['shape']).Volume
            if volume>1e-5:overlaps.append(dict(a=first['id'],b=second['id'],volume_mm3=volume))
    byid={i['id']:i for i in items};bore_checks=[];seat_checks=[]
    for hand,cy in centers.items():
        angle=byid[hand+'CasingWall_Angle']['shape']
        for role in ['wall','case']:
            receiver=byid['hull_engine_back' if role=='wall' else hand+'Casing_Body']['shape']
            for n,s in enumerate(stations[role]):
                cut=cutter(s,a[role+'_rivet_diameter']+a['hole_diameter_clearance']);cut.translate(App.Vector(0,cy,0))
                residual=sum(shape.common(cut).Volume for shape in [angle,receiver])
                if residual>1e-5:raise ValueError('Rivet bore remains obstructed')
                rivet=byid[hand+'CasingWall_'+role.title()+'Rivet%02d'%n]['shape']
                distances=[rivet.distToShape(shape)[0] for shape in [angle,receiver]]
                if max(distances)>1e-6:raise ValueError('Rivet does not seat on both receivers')
                bore_checks.append(dict(side=hand,role=role,index=n,remaining_material_mm3=residual))
                seat_checks.append(dict(side=hand,role=role,index=n,receiver_distances_mm=distances))
    hull=validate_hull(load(),context+items,out)
    assert fingerprint()==lock;check_build(stage/'build')
    report=dict(complete=True,passed=not overlaps,fixture_occurrences=len(items),new_mount_occurrences=len(new),
                material_candidate_pairs=len(checked),overlaps=overlaps,bore_checks=bore_checks,seat_checks=seat_checks,
                stations=stations,input_sha256=hashes,native_sha256=sha(native),authored_fingerprint=lock,
                tank_native_hashes=build['native_hashes'],hull_report='reports/hull_plates.json',
                standard_assembly_modified=False,full_casing_bom_populated=False,historical_fit_qualified=False,
                source_fastener_schedule_reconciled=False,visual_review_status='pending',rendering_complete=False)
    write(out/'report.json',report)
    print('Casing wall joints:',len(new),'new parts,',len(checked),'candidate pairs,',len(overlaps),'overlaps',flush=True)
    detail=new+[i for i in items if i['id']=='hull_engine_back' or i['id'].startswith(('PortCasing_','StarboardCasing_'))]
    shaded(detail,out/'wall_joints_oblique.svg',(1,1,.65),'M1592 casing wall joints | separate source-allocated rivets; inferred angle form')
    cut=[];hand='Port';cy=centers[hand]
    slab=Part.makeBox(300,800,1200,App.Vector(wall['shape'].BoundBox.XMin-150,cy-400,500))
    for item in detail:
        if item['id'].startswith('Starboard'):continue
        shape=item['shape'].common(slab)
        if not shape.isNull():cut.append(dict(item,shape=shape,target=SimpleNamespace(Shape=shape),definition=item['id']+'_detail'))
    shaded(cut,out/'wall_joint_detail.svg',(-1,1,.65),'Casing wall attachment crop | 11 wall and 17 case rivets per side')
    assert all(sha(p)==hashes[str(p.relative_to(ROOT))] for p in paths)
    report['rendering_complete']=True;write(out/'report.json',report)
    sys.exit(0 if report['passed'] else 1)
finally:
    runtime.close()
