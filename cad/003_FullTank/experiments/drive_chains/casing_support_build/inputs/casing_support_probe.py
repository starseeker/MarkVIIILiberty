"""Fit casing support brackets to the existing inner and outer hull wing plates."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage',type=Path,required=True)
parser.add_argument('--output',type=Path,default=ROOT/'casing_support_build')
parser.add_argument('--worker',action='store_true')
args=parser.parse_args();stage=args.stage.resolve();out=args.output.resolve()
sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import read,write,sha,fingerprint,database,REPO
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
    from lib.hull_validation import validate as validate_hull
    from lib.wheel_parts import button_rivet
    from lib.visual_review import shaded
    from casing_mount_parts import cutter
    from casing_cap_parts import fasteners
    from casing_support_parts import support
    lock=fingerprint();build=check_build(stage/'build')
    names=['casing_support_probe.py','casing_support_parts.py','casing_support_controls.json','casing_support_sources.json',
           'casing_cap_parts.py','casing_cap_controls.json','casing_cap_fastener_sources.json','casing_mount_parts.py',
           'casing_parts.py','casing_controls.json','casing_source_rows.json','installed_pitch_route_report.json',
           'casing_shell_passage_build/report.json','casing_trim_build/report.json','casing_trim_build/CasingTrimCandidate.FCStd']
    paths=[ROOT/n for n in names];hashes={n:sha(p) for n,p in zip(names,paths)}
    for n,p in zip(names,paths):
        if '/' not in n:
            target=out/'inputs'/n;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())
    for source in ['casing_support_sources.json','casing_cap_fastener_sources.json']:
        for n,h in read(ROOT/source)['inspected_source_hashes'].items():assert sha(REPO/n)==h
    a={k:v['value'] for k,v in read(ROOT/'casing_support_controls.json')['controls'].items()}
    hardware={k:v['value'] for k,v in read(ROOT/'casing_cap_controls.json')['controls'].items()};hardware['bolt_length']=a['bolt_length']
    casing={k:v['value'] for k,v in read(ROOT/'casing_controls.json')['controls'].items()}
    sources=read(ROOT/'casing_source_rows.json');route=read(ROOT/'installed_pitch_route_report.json')
    shell=read(ROOT/'casing_shell_passage_build/report.json');prior=read(paths[-2])
    assert prior['passed'] and prior['rendering_complete'] and prior['native_sha256']==sha(paths[-1])
    assert prior['authored_fingerprint']==lock and prior['tank_native_hashes']==build['native_hashes']
    tank=App.openDocument(build['build']['top_document']);tank.recompute();original=leaves(tank.Root)
    original_byid={i['id']:i for i in original}
    doc=App.openDocument(str(paths[-1]));doc.recompute();before=leaves(doc.Root)
    definitions={};added_ids=[];joints=[];receiver_ids=[];removal=[]
    records=dict(bolt='SNL:31:007',nut='SNL:128:001',washer='SNL:270:003',rivet='SNL:167:010')
    with database() as c:
        ids={role:[r[0] for r in c.execute('select distinct part_id from part_evidence where record_id=?',(record,))]
             for role,record in records.items()}
    assert all(len(v)==1 for v in ids.values())
    def definition(key,shape,survey_ids,mark='',record=''):
        body=doc.addObject('PartDesign::Body','Def_CasingSupport'+key);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedSupportAndDrilling').Shape=shape
        metadata(body,DefinitionId='casing_support_'+key,Representation='assembly',Coverage='partial',
                 SurveyIds=survey_ids,OriginalMark=mark,SourceRecord=record)
        definitions[key]=body;return body
    for key,shape in fasteners(hardware).items():
        body=definition(key,shape,ids[key],record=records[key])
        metadata(body,JointAllocationBasis='Reconstruction assumption; standard type source does not identify this casing joint')
    rivet=button_rivet(doc,'Def_CasingSupportRivet',a['case_rivet_diameter'],a['case_rivet_length'],casing['sheet_stock']+a['bracket_stock'])
    doc.Definitions.addObject(rivet)
    metadata(rivet,DefinitionId='casing_support_rivet',Representation='assembly',Coverage='partial',SurveyIds=ids['rivet'],SourceRecord=records['rivet'])
    definitions['rivet']=rivet
    body_tools=[]
    for hand in ['Port','Starboard']:
        cy=next(i for i in before if i['id']==hand+'Chain_RollerPinion')['shape'].Placement.Base.y
        group=doc.addObject('App::Part',hand+'CasingSupports');doc.Root.addObject(group)
        def link(name,key,center=(0,0,0),axis=(0,1,0)):
            name=hand+'CasingSupport_'+name
            obj=doc.addObject('App::Link',name);group.addObject(obj);obj.setLink(definitions[key])
            obj.LinkPlacement=App.Placement(App.Vector(*center)+App.Vector(0,cy,0),App.Rotation(App.Vector(0,1,0),App.Vector(*axis)))
            metadata(obj,OccurrenceId=name,Subsystem='Drivetrain');added_ids.append(name)
        for sign,face,mark in [(-1,'Right','M1587'),(1,'Left','M1588')]:
            inner=(hand=='Port')==(sign<0)
            receiver='hull_'+hand.lower()+('_inner_rear_end' if inner else '_rear_wing')
            old=original_byid[receiver];b=old['shape'].BoundBox
            y=(b.YMin if sign>0 else b.YMax)-cy
            shape,stations,dimensions=support(a,casing,route,shell,sign,y,b.YLength)
            key=hand+face;definition(key,shape,[sources['parts'][mark]['part_id']],mark=mark)
            link(face+'Bracket',key)
            local_tools=[cutter(s,a['case_rivet_diameter']+a['hole_diameter_clearance']) for s in stations['case_rivets']]
            if hand=='Port':body_tools+=local_tools
            for n,s in enumerate(stations['case_rivets']):link(face+'Rivet%02d'%n,'rivet',s['center'],s['axis'])
            hull_tools=[]
            for n,s in enumerate(stations['hull_bolts']):
                name=face+'HullSet%02d'%n;center=App.Vector(*s['center']);axis=App.Vector(*s['axis'])
                head=center+axis*s['grip']/2
                washer=center-axis*(s['grip']/2+hardware['washer_stock'])
                nut=washer-axis*hardware['nut_stock']
                for suffix,key,pos in [('Bolt','bolt',head),('Washer','washer',washer),('Nut','nut',nut)]:
                    link(name+suffix,key,[pos.x,pos.y,pos.z],s['axis'])
                tool=cutter(s,hardware['bolt_diameter']+a['hole_diameter_clearance']);tool.translate(App.Vector(0,cy,0));hull_tools.append(tool)
            updated=old['shape'].cut(Part.makeCompound(hull_tools)).removeSplitter()
            added=updated.cut(old['shape']).Volume;removed=old['shape'].Volume-updated.Volume
            assert added<1e-5 and removed>0
            assert all(abs(getattr(updated.BoundBox,k)-getattr(b,k))<1e-7 for k in ['XMin','XMax','YMin','YMax','ZMin','ZMax'])
            removal.append(dict(receiver=receiver,added_material_mm3=added,removed_material_mm3=removed))
            body=definition(receiver,updated,old['target'].SurveyIds)
            body.DefinitionId=old['definition']
            obj=doc.addObject('App::Link','Updated_'+receiver);doc.Root.addObject(obj);obj.setLink(body)
            metadata(obj,OccurrenceId=receiver,Subsystem=old['system']);receiver_ids.append(receiver)
            joints.append(dict(hand=hand,cy=cy,face=face,mark=mark,receiver=receiver,stations=stations,dimensions=dimensions))
    body=next(i for i in before if i['id']=='PortCasing_Body')['target']
    updated=body.Shape.cut(Part.makeCompound(body_tools)).removeSplitter()
    assert updated.cut(body.Shape).Volume<1e-5
    removal.append(dict(receiver='shared_casing_body',added_material_mm3=updated.cut(body.Shape).Volume,removed_material_mm3=body.Shape.Volume-updated.Volume))
    body.Tip.Shape=updated
    doc.Definitions.Visibility=False;doc.recompute();native=out/'CasingSupportCandidate.FCStd';doc.saveAs(str(native))
    App.closeDocument(doc.Name);doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root)
    assert len(items)==809 and len(added_ids)==56
    for i in items:
        if not i['shape'].isValid() or len(i['shape'].Solids)!=1:raise ValueError('Invalid support leaf '+i['id'])
    replaced=set(receiver_ids)|{'hull_engine_back','PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting'}
    context=[i for i in original if i['id'] not in replaced];byid={i['id']:i for i in items}
    new=[byid[key] for key in added_ids]
    changed=new+[byid[key] for key in receiver_ids+['PortCasing_Body','StarboardCasing_Body']]
    physical=[i for i in context if i['representation']=='assembly']+items
    boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].BoundBox for i in physical]])
    pairs=set();overlaps=[]
    for first in changed:
        b=first['shape'].BoundBox;box=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
        near=np.where(np.all(boxes[:,:3]<=box[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=box[:3]-1e-7,axis=1))[0]
        for n in near:
            second=physical[n];pair=tuple(sorted([first['id'],second['id']]))
            if pair[0]==pair[1] or pair in pairs:continue
            pairs.add(pair);volume=first['shape'].common(second['shape']).Volume
            if volume>1e-5:overlaps.append(dict(a=first['id'],b=second['id'],volume_mm3=volume))
    bores=[];seats=[];retention=[];support_seats=[]
    for j in joints:
        prefix=j['hand']+'CasingSupport_'+j['face'];bracket=byid[prefix+'Bracket']['shape']
        case=byid[j['hand']+'Casing_Body']['shape'];hull=byid[j['receiver']]['shape']
        distances=[bracket.distToShape(s)[0] for s in [case,hull]]
        support_seats.append(dict(bracket=prefix,receiver_distances_mm=distances,passed=max(distances)<1e-6))
        for role in ['case_rivets','hull_bolts']:
            for n,s in enumerate(j['stations'][role]):
                receivers=[bracket,case if role=='case_rivets' else hull]
                diameter=a['case_rivet_diameter'] if role=='case_rivets' else hardware['bolt_diameter']
                tool=cutter(s,diameter+a['hole_diameter_clearance']);tool.translate(App.Vector(0,j['cy'],0))
                residual=sum(receiver.common(tool).Volume for receiver in receivers)
                bores.append(dict(bracket=prefix,role=role,index=n,remaining_material_mm3=residual,passed=residual<1e-5))
                if role=='case_rivets':
                    rivet=byid[prefix+'Rivet%02d'%n]['shape'];distances=[rivet.distToShape(receiver)[0] for receiver in receivers]
                else:
                    name=prefix+'HullSet%02d'%n
                    bolt,washer,nut=[byid[name+suffix]['shape'] for suffix in ['Bolt','Washer','Nut']]
                    distances=[bolt.distToShape(hull)[0],washer.distToShape(bracket)[0],nut.distToShape(washer)[0]]
                    protrusion=hardware['bolt_length']-s['grip']-hardware['washer_stock']-hardware['nut_stock']
                    radial=bolt.distToShape(nut)[0]
                    retention.append(dict(joint=name,protrusion_mm=protrusion,thread_envelope_radial_gap_mm=radial,
                        source_joint_allocation_confirmed=False,passed=protrusion>0 and abs(radial-hardware['thread_envelope_diameter_clearance']/2)<1e-6))
                seats.append(dict(bracket=prefix,role=role,index=n,receiver_distances_mm=distances,passed=max(distances)<1e-6))
    validate_hull(load(),context+items,out)
    assert fingerprint()==lock;check_build(stage/'build')
    passed=not overlaps and all(r['passed'] for r in bores+seats+retention+support_seats)
    report=dict(complete=True,passed=passed,fixture_occurrences=len(items),new_support_occurrences=len(new),
        new_hull_receivers=len(receiver_ids),brackets=4,case_rivets=28,inferred_hull_bolt_sets=8,
        material_candidate_pairs=len(pairs),overlaps=overlaps,bore_checks=bores,seat_checks=seats,
        support_seat_checks=support_seats,retention_checks=retention,receiver_material_removal=removal,
        joints=joints,hull_report='reports/hull_plates.json',input_sha256=hashes,native_sha256=sha(native),
        authored_fingerprint=lock,tank_native_hashes=build['native_hashes'],standard_assembly_modified=False,
        source_fastener_schedule_reconciled=False,support_bolt_joint_allocation_source_confirmed=False,
        full_casing_bom_populated=False,historical_fit_qualified=False,visual_review_status='pending',rendering_complete=False)
    write(out/'report.json',report)
    print('Casing supports:',len(new),'new leaves;',len(pairs),'material pairs;',len(overlaps),'overlaps; passed=',passed,flush=True)
    one=[i for i in items if i['id'].startswith(('PortCasing_','PortCasingWall_','PortCasingCap_','PortCasingTrim_','PortCasingSupport_'))]
    shaded(one,out/'casing_support_oblique.svg',(1,1,.65),'Casing supports | inferred bracket form and hull-bolt allocation')
    cy=joints[0]['cy'];x=joints[0]['dimensions']['center_x_mm'];z=joints[0]['dimensions']['web_base_z_mm']
    slab=Part.makeBox(240,800,300,App.Vector(x-120,cy-400,z-100));crop=[]
    detail=one+[byid[key] for key in receiver_ids if 'port' in key]
    for i in detail:
        s=i['shape'].common(slab)
        if not s.isNull():crop.append(dict(i,shape=s,target=SimpleNamespace(Shape=s),definition=i['id']+'_detail'))
    shaded(crop,out/'casing_support_detail.svg',(1,1,.6),'Native support crop | riveted casing legs and bolted hull legs; inferred installation')
    assert all(sha(p)==hashes[n] for n,p in zip(names,paths))
    report['rendering_complete']=True;write(out/'report.json',report)
    sys.exit(0 if passed else 1)
finally:
    runtime.close()
