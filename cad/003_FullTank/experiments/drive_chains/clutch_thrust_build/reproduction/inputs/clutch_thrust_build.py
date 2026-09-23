"""Build a source-linked, headless native clutch thrust mechanism in its parent."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent
STAGE=HERE.parents[1]
ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,default=HERE/'clutch_thrust_build')
p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--output',str(out),'--worker'],
            env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)

try:
    import FreeCAD as App, Part, numpy as np
    from lib.cad_build import leaves,metadata,shape_signature,COLORS
    from lib.worker import same_shape,placement_errors,check_build
    from lib.visual_review import shaded
    from clutch_thrust_parts import build
    assert not App.GuiUp
    App.ParamGet('User parameter:BaseApp/Preferences/Document').SetInt('CountBackupFiles',0)
    parent=HERE/'clutch_stack_build';pn=parent/'TransmissionWithClutchStack.FCStd'
    pq=read(parent/'qualification.json');assert pq['passed'] and pq['native_sha256']==sha(pn)
    dossier=read(HERE/'clutch_thrust_sources.json')
    for rel,h in dossier['source_assets'].items():assert sha(ROOT/rel)==h,rel
    inputs=[HERE/n for n in ['clutch_thrust_build.py','clutch_thrust_parts.py','clutch_thrust_controls.json','clutch_thrust_sources.json']]
    hashes={str(f.relative_to(ROOT)):sha(f) for f in inputs}
    (out/'inputs').mkdir(exist_ok=True)
    for f in inputs:(out/'inputs'/f.name).write_bytes(f.read_bytes())
    pc=read(parent/'report.json')['controls'];c=read(HERE/'clutch_thrust_controls.json')['controls']
    doc=App.openDocument(str(pn));doc.recompute();old={i['id']:i for i in leaves(doc.Root)}
    before={n:(shape_signature(i['shape']),i['shape'].Placement) for n,i in old.items()}
    parent_thrust=old['ClutchStack_thrust']['target'].Shape.copy()
    parent_thrust.exportBrep(str(out/'inputs/parent_thrust.brep'))
    parts,occ,thrust,datums=build(c,pc,parent_thrust)
    old['ClutchStack_thrust']['target'].Tip.Shape=thrust
    metadata(old['ClutchStack_thrust']['target'],ThrustRaceRevision='Estimated forward annular pocket and concave axial groove for thirty 1/4-inch balls. Original bearing seat and bore retained.')
    group=doc.addObject('App::Part','ClutchThrust');doc.TransmissionCore.addObject(group)
    metadata(group,Scope='32 new physical components; SH998B race refinement; spring and cone interfaces remain partial.')
    bearing=doc.addObject('App::Part','ClutchBallRetainer');group.addObject(bearing)
    metadata(bearing,SourceRecord='SNL:164:002',QuantityRole='Nonphysical assembly container')
    rows={r['record_id']:r for r in dossier['records']}
    identities={'cage':('SH998C','SNL:164:004'),'ball':('1/4-inch steel ball','SNL:164:005'),'stop':('SH998A','SNL:165:003')}
    bodies={}
    for key,shape in parts.items():
        body=doc.addObject('PartDesign::Body','Def_ClutchThrust_'+key);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedPart').Shape=shape
        mark,rid=identities[key]
        metadata(body,DefinitionId='clutch_thrust_'+key,OriginalMark=mark,SurveyIds=rows[rid]['part_ids'],SourceRecord=rid,
            Representation='assembly',Coverage='partial',ParameterUpdate='Regenerate clutch_thrust_build.py from controls',
            ReconstructionNotes='Printed ball count/diameter; estimated race, cage, ring and interfaces. See I03-clutch-thrust.')
        bodies[key]=body
    for row in occ:
        key=row['key'];rid=identities[key][1];link=doc.addObject('App::Link',row['name'])
        (group if key=='stop' else bearing).addObject(link);link.setLink(bodies[key])
        link.LinkPlacement=App.Placement(App.Vector(*row['xyz']),App.Rotation())
        metadata(link,OccurrenceId=row['name'],SurveyIds=rows[rid]['part_ids'],SourceRecord=rid,Subsystem='Drivetrain',QuantityRole='One physical component')
    doc.Definitions.Visibility=False;doc.recompute()
    native=out/'TransmissionWithClutchThrust.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items}
    new=[r['name'] for r in occ];affected=['ClutchStack_thrust']+new
    assert len(items)==len(byid)==1581 and len(new)==32
    for n,i in byid.items():
        assert i['shape'].isValid() and len(i['shape'].Solids)==1,n
        if n in before and n!='ClutchStack_thrust':
            assert same_shape(before[n][0],shape_signature(i['shape'])),n
            t,r=placement_errors(i['shape'].Placement,before[n][1]);assert t<1e-6 and r<1e-8,n
    report=dict(native_sha256=sha(native),parent_native_sha256=sha(pn),parent_qualification_sha256=sha(parent/'qualification.json'),
        input_hashes=hashes,parent_thrust_sha256=sha(out/'inputs/parent_thrust.brep'),controls=c,parent_controls=pc,datums=datums,
        native_occurrences=1581,new_ids=new,affected_ids=affected,changed_ids=['ClutchStack_thrust'],unchanged_parent_occurrences=1548,
        standard_assembly_modified=False,complete_clutch=False,complete_tank=False,headless=True,freecad=App.Version(),occ=Part.OCC_VERSION)
    write(out/'report.json',report);print('Saved/reopened 1581 physical leaves; 32 new, 1 revised, 1548 preserved.',flush=True)
    standard=check_build(STAGE/'build');td=App.openDocument(standard['build']['top_document']);td.recompute()
    context=[i for i in leaves(td.Root) if i['representation']=='assembly'];report['standard_native_hashes']=standard['native_hashes']
    physical=items+context
    boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].copy().cleaned().BoundBox for i in physical]])
    pairs=[];seen=set()
    for name in affected:
        shape=byid[name]['shape'];b=shape.copy().cleaned().BoundBox;bb=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
        near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
        for idx in near:
            other=physical[idx];pair=tuple(sorted([name,other['id']]))
            if name==other['id'] or pair in seen:continue
            seen.add(pair);v=shape.common(other['shape']).Volume;pairs.append(dict(a=name,b=other['id'],intersection_mm3=v))
        write(out/'material_progress.json',dict(last=name,pairs=len(pairs),overlaps=[x for x in pairs if abs(x['intersection_mm3'])>1e-5]))
    overlaps=[x for x in pairs if abs(x['intersection_mm3'])>1e-5]
    write(out/'material_checks.json',dict(passed=not overlaps,native_sha256=sha(native),pairs=pairs,standard_context_checked=True))
    report.update(material_pairs=len(pairs),material_passed=not overlaps,overlaps=overlaps,standard_context_checked=True)
    path=out/'ClutchThrustInstallation.step';Part.makeCompound([byid[n]['shape'] for n in affected]).exportStep(str(path));report['step_sha256']=sha(path)
    keys=['Def_ClutchThrust_'+k for k in parts]+[byid['ClutchStack_thrust']['target'].Name]
    path=out/'ClutchThrustDefinitions.step';Part.makeCompound([doc.getObject(k).Shape for k in keys]).exportStep(str(path))
    report['definition_step_sha256']=sha(path);write(out/'definition_order.json',keys)
    view=out/'previews';view.mkdir(exist_ok=True);origin=doc.TransmissionCore.Placement.Base
    COLORS.update(Clutch=(.67,.61,.46),BearingBall=(.72,.75,.79),Cage=(.68,.52,.28),Stop=(.54,.58,.64))
    def draw(names,file,title,direction,clip=None):
        selected=[]
        for n in names:
            i=byid[n];s=i['shape'] if clip is None else i['shape'].common(clip)
            if s.isNull() or not s.Solids:continue
            color='BearingBall' if n.startswith('ClutchThrust_Ball') else ('Cage' if n=='ClutchThrust_Cage' else ('Stop' if n=='ClutchThrust_Stop' else 'Clutch'))
            selected.append(dict(i,shape=s,target=SimpleNamespace(Shape=s),definition=n,system=color))
        shaded(selected,view/(file+'.svg'),direction,title)
    front=[n for n in byid if n.startswith(('FrontClutch_','ClutchCollar_','ClutchStack_','ClutchDrive_'))]
    draw(front+new,'isometric','Clutch thrust assembly | retainer, 30 quarter-inch balls and spring-stop ring',(1,1,.6))
    draw(affected,'mechanism','Thrust mechanism | estimated race profiles, cage and stop ring',(1,1,.6))
    draw(['ClutchStack_thrust','ClutchThrust_Cage']+[n for n in new if 'Ball' in n],'race_open','Spring-stop ring hidden | shared ball definition and perforated cage',(1,1,.6))
    draw(['ClutchThrust_Cage'],'cage','SH998C reconstruction | 30 actual ball pockets',(1,1,.6))
    clip=Part.makeBox(42,260,1,origin+App.Vector(985,-130,-.5))
    draw(affected+['ClutchCollar_collar','ClutchStack_bearing','ClutchStack_snap'],'section','Axial race section | collar, two races, ball, cage and spring-stop ring',(0,0,1),clip)
    report['render_hashes']={f.name:sha(f) for f in view.glob('*.png')};write(out/'report.json',report)
    assert sha(pn)==pq['native_sha256']
    for rel,h in hashes.items():assert sha(ROOT/rel)==h,rel
    print('Material pairs:',len(pairs),'overlaps:',overlaps,flush=True)
    assert not overlaps
finally:
    runtime.close()
