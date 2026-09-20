"""Build and inspect the selected register-plate and beading reconstruction."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage',type=Path,required=True)
parser.add_argument('--output',type=Path,default=ROOT/'casing_trim_build')
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
    from collections import Counter
    from types import SimpleNamespace
    from lib.cad_build import leaves,metadata
    from lib.worker import check_build
    from lib.wheel_parts import button_rivet
    from lib.visual_review import shaded
    from casing_trim_parts import trim,drill,countersunk_rivet
    lock=fingerprint();build=check_build(stage/'build')
    names=['casing_trim_probe.py','casing_trim_parts.py','casing_trim_controls.json','casing_trim_sources.json',
           'casing_mount_parts.py','casing_parts.py','casing_controls.json','casing_source_rows.json',
           'installed_pitch_route_report.json','casing_shell_passage_build/report.json',
           'casing_cap_packing_build/report.json','casing_cap_packing_build/CasingCapCandidate.FCStd']
    paths=[ROOT/n for n in names];hashes={n:sha(p) for n,p in zip(names,paths)}
    for n,p in zip(names,paths):
        if '/' not in n:
            target=out/'inputs'/n;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())
    for n,expected in read(ROOT/'casing_trim_sources.json')['inspected_source_hashes'].items():assert sha(REPO/n)==expected
    a={k:v['value'] for k,v in read(ROOT/'casing_trim_controls.json')['controls'].items()}
    casing={k:v['value'] for k,v in read(ROOT/'casing_controls.json')['controls'].items()}
    sources=read(ROOT/'casing_source_rows.json');route=read(ROOT/'installed_pitch_route_report.json')
    shell=read(ROOT/'casing_shell_passage_build/report.json');prior=read(paths[-2])
    assert prior['passed'] and prior['rendering_complete'] and prior['native_sha256']==sha(paths[-1])
    assert prior['authored_fingerprint']==lock and prior['tank_native_hashes']==build['native_hashes']
    tank=App.openDocument(build['build']['top_document']);tank.recompute()
    context=[i for i in leaves(tank.Root) if i['id'] not in {'hull_engine_back','PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting'}]
    doc=App.openDocument(str(paths[-1]));doc.recompute();before=leaves(doc.Root)
    parts,stations=trim(a,casing,route,shell);removal=[]
    for owner in ['Body','Cap']:
        item=next(i for i in before if i['id']=='PortCasing_'+owner)
        tools=[drill(s,a) for s in stations if s['owner']==owner]
        old=item['target'].Shape
        updated=old.cut(Part.makeCompound(tools)).removeSplitter()
        added=updated.cut(old).Volume;removed=old.Volume-updated.Volume
        assert added<1e-5 and removed>0
        removal.append(dict(definition=item['definition'],added_material_mm3=added,removed_material_mm3=removed))
        item['target'].Tip.Shape=updated
    definitions={}
    for name,part in parts.items():
        body=doc.addObject('PartDesign::Body','Def_Trim'+name);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','InferredTrimAndDrilling').Shape=part['shape']
        metadata(body,DefinitionId='casing_trim_'+name,Representation='assembly',Coverage='partial',
                 OriginalMark=part['mark'],SurveyIds=[sources['parts'][part['mark']]['part_id']])
        definitions[name]=body
    records=dict(register='SNL:167:010',beading='SNL:191:001')
    with database() as c:
        identities={role:[r[0] for r in c.execute('select distinct part_id from part_evidence where record_id=?',(record,))]
                    for role,record in records.items()}
    assert all(len(ids)==1 for ids in identities.values())
    for role in records:
        grip=next(s['grip'] for s in stations if s['role']==role)
        body=(button_rivet(doc,'Def_RegisterRivet',a['register_rivet_diameter'],a['register_rivet_length'],grip)
              if role=='register' else countersunk_rivet(doc,'Def_BeadingRivet',a,grip))
        doc.Definitions.addObject(body)
        metadata(body,DefinitionId='casing_trim_'+role+'_rivet',Representation='assembly',Coverage='partial',
                 SurveyIds=identities[role],SourceRecord=records[role])
        definitions[role]=body
    added_ids=[];centers={}
    for hand in ['Port','Starboard']:
        cy=next(i for i in before if i['id']==hand+'Chain_RollerPinion')['shape'].Placement.Base.y
        centers[hand]=cy;group=doc.addObject('App::Part',hand+'CasingTrim');doc.Root.addObject(group)
        def link(name,target,center,axis=(0,1,0)):
            name=hand+'CasingTrim_'+name
            obj=doc.addObject('App::Link',name);group.addObject(obj);obj.setLink(definitions[target])
            obj.LinkPlacement=App.Placement(App.Vector(*center)+App.Vector(0,cy,0),App.Rotation(App.Vector(0,1,0),App.Vector(*axis)))
            metadata(obj,OccurrenceId=name,Subsystem='Drivetrain');added_ids.append(name)
        for name in parts:link(name,name,[0,0,0])
        for s in stations:link(s['name'],s['role'],s['center'],s['axis'])
    metadata(doc.Root,Scope='Isolated chain/casing candidate with corrected packing, lap registers and beading')
    doc.Definitions.Visibility=False;doc.recompute();native=out/'CasingTrimCandidate.FCStd';doc.saveAs(str(native))
    App.closeDocument(doc.Name);doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root)
    assert len(items)==749 and len(added_ids)==88
    for i in items:
        if not i['shape'].isValid() or len(i['shape'].Solids)!=1:raise ValueError('Invalid trim leaf '+i['id'])
    byid={i['id']:i for i in items};new=[byid[key] for key in added_ids]
    changed=new+[i for i in items if i['id'] in {h+'Casing_'+o for h in centers for o in ['Body','Cap']}]
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
    bores=[];seats=[];laps=[];flush=[]
    for hand,cy in centers.items():
        def shape(name):return byid[hand+'CasingTrim_'+name]['shape']
        for s in stations:
            receivers=[shape(s['part']),byid[hand+'Casing_'+s['owner']]['shape']]
            tool=drill(s,a);tool.translate(App.Vector(0,cy,0))
            remaining=sum(receiver.common(tool).Volume for receiver in receivers)
            distances=[shape(s['name']).distToShape(receiver)[0] for receiver in receivers]
            bores.append(dict(side=hand,joint=s['name'],remaining_material_mm3=remaining,passed=remaining<1e-5))
            seats.append(dict(side=hand,joint=s['name'],receiver_distances_mm=distances,passed=max(distances)<1e-6))
            if s['role']=='beading':
                b=shape(s['name']).BoundBox;sign=s['axis'][1]
                face=b.YMax if sign>0 else b.YMin
                deviation=abs(face-(cy+sign*casing['outside_width']/2))
                flush.append(dict(side=hand,joint=s['name'],head_flush_deviation_mm=deviation,passed=deviation<1e-6))
        for name,part in parts.items():
            if part['role']!='register':continue
            distances=[shape(name).distToShape(byid[hand+'Casing_'+owner]['shape'])[0] for owner in ['Body','Cap']]
            laps.append(dict(side=hand,register=name,receiver_distances_mm=distances,passed=max(distances)<1e-6))
    counts={mark:count*2 for mark,count in Counter(p['mark'] for p in parts.values()).items()}
    assert counts=={'M1581':4,'M1594A':2,'M1594B':2,'M1585':8}
    assert fingerprint()==lock;check_build(stage/'build')
    passed=not overlaps and all(r['passed'] for r in bores+seats+laps+flush)
    report=dict(complete=True,passed=passed,fixture_occurrences=len(items),new_trim_occurrences=len(new),
        new_vehicle_mark_counts=counts,register_rivets=32,beading_rivets=40,material_candidate_pairs=len(pairs),
        overlaps=overlaps,bore_checks=bores,seat_checks=seats,register_lap_checks=laps,flush_checks=flush,
        receiver_material_removal=removal,stations=stations,input_sha256=hashes,native_sha256=sha(native),
        authored_fingerprint=lock,tank_native_hashes=build['native_hashes'],standard_assembly_modified=False,
        source_fastener_schedule_reconciled=False,full_casing_bom_populated=False,historical_fit_qualified=False,
        visual_review_status='pending',rendering_complete=False)
    write(out/'report.json',report)
    print('Casing trim:',len(new),'new leaves;',len(pairs),'material pairs;',len(overlaps),'overlaps; passed=',passed,flush=True)
    one=[i for i in items if i['id'].startswith(('PortCasing_','PortCasingWall_','PortCasingCap_','PortCasingTrim_'))]
    shaded(one,out/'casing_trim_oblique.svg',(1,1,.6),'Casing register plates and beading | selected source schedule; inferred profiles')
    cy=centers['Port'];sz=shell['dimensions']['cap_seam_z_mm']
    def cropped(slab,suffix):
        result=[]
        for i in one:
            s=i['shape'].common(slab)
            if not s.isNull():result.append(dict(i,shape=s,target=SimpleNamespace(Shape=s),definition=i['id']+suffix))
        return result
    inner=cropped(Part.makeBox(900,200,250,App.Vector(200,cy-200,sz-100)),'_inner')
    shaded(inner,out/'casing_trim_inside.svg',(0,1,.5),'Casing inner seam crop | beading and formed rivet tails')
    x=next(s['center'][0] for s in stations if s['name']=='BodyRightBeadingRivet02')
    section=cropped(Part.makeBox(2,240,150,App.Vector(x-1,cy-120,sz-75)),'_section')
    shaded(section,out/'beading_rivet_section.svg',(1,0,0),'Native section through beading rivets | flush countersinks and separate inner strips')
    assert all(sha(p)==hashes[n] for n,p in zip(names,paths))
    report['rendering_complete']=True;write(out/'report.json',report)
    sys.exit(0 if passed else 1)
finally:
    runtime.close()
