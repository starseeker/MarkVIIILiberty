"""Exercise coupled cone/support station, bend and spring-seat variation."""
import argparse
import math
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,default=HERE/'clutch_cone_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();base=a.candidate.resolve();out=base/'variants';out.mkdir(exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(base),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part,numpy as np
    from lib.cad_build import leaves,metadata
    from lib.worker import check_build
    from clutch_cone_parts import build
    App.ParamGet('User parameter:BaseApp/Preferences/Document').SetInt('CountBackupFiles',0)
    report=read(base/'report.json');native=base/'TransmissionWithClutchCone.FCStd';assert sha(native)==report['native_sha256']
    nominal=App.openDocument(str(native));origin=nominal.TransmissionCore.Placement.Base
    untouched=[i for i in leaves(nominal.Root) if i['id'] not in report['affected_ids']]
    standard=check_build(STAGE/'build');td=App.openDocument(standard['build']['top_document'])
    context=untouched+[i for i in leaves(td.Root) if i['representation']=='assembly'];results=[]
    for label,sign in [('smaller',-1),('larger',1)]:
        c=dict(report['controls']);c['web_x_intercept']+=sign*2;c['bend_radius']+=sign*2;c['cup_front']+=sign
        parts,occ,support,spine,d,blanks=build(c,report['parent_controls'],report['thrust_controls'])
        parts['support']=support;occ+=[dict(name='ClutchStack_support',key='support',xyz=[0,0,0],rotation=[0,0,0,1])]
        doc=App.newDocument('ConeVariant');root=doc.addObject('App::Part','Root');root.Placement.Base=origin
        library=doc.addObject('App::Part','Definitions');defs={}
        for key,shape in parts.items():
            obj=doc.addObject('PartDesign::Feature','Def_'+key);library.addObject(obj);obj.Shape=shape
            metadata(obj,DefinitionId=key,Representation='assembly',Coverage='partial');defs[key]=obj
        for row in occ:
            obj=doc.addObject('App::Link',row['name']);root.addObject(obj);obj.setLink(defs[row['key']])
            obj.LinkPlacement=App.Placement(App.Vector(*row['xyz']),App.Rotation(*row['rotation']));metadata(obj,OccurrenceId=row['name'],Subsystem='Drivetrain')
        library.Visibility=False;doc.recompute();path=out/(label+'.FCStd');doc.saveAs(str(path));App.closeDocument(doc.Name)
        doc=App.openDocument(str(path));items=leaves(doc.Root);byid={i['id']:i for i in items}
        physical=items+context;assert len(items)==72 and all(i['shape'].isValid() and len(i['shape'].Solids)==1 for i in items)
        boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].copy().cleaned().BoundBox for i in physical]])
        pairs=[];seen=set()
        for i in items:
            s=i['shape'];b=s.copy().cleaned().BoundBox;bb=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
            near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
            for idx in near:
                other=physical[idx];pair=tuple(sorted([i['id'],other['id']]))
                if i['id']==other['id'] or pair in seen:continue
                seen.add(pair);pairs.append(dict(a=i['id'],b=other['id'],intersection_mm3=s.common(other['shape']).Volume))
            write(out/'progress.json',dict(scenario=label,last=i['id'],pairs=len(pairs)))
        overlaps=[x for x in pairs if abs(x['intersection_mm3'])>1e-5];checks=[]
        def ck(name,passed):checks.append(dict(name=name,passed=bool(passed)))
        ck('cone/support station responds',d['small_face'][0]!=report['datums']['small_face'][0])
        ck('spring responds to cup seat',abs(d['spring_length']-report['datums']['spring_length']-sign)<1e-6)
        # Verify actual plane seats and absence of all43 filled rivet bores.
        for n in range(1,7):
            spring=byid[f'ClutchCone_Spring{n}']['shape'];ring=byid['ClutchCone_ring']['shape'];cup=byid[f'ClutchCone_Cup{n}']['shape']
            ck(f'spring{n}/rear contact',spring.distToShape(ring)[0]<1e-6)
            ck(f'spring{n}/front contact',spring.distToShape(cup)[0]<1e-6)
            angle=math.radians(30+(n-1)*60);p=origin+App.Vector(d['cup_support_seat'],124.75*math.cos(angle),124.75*math.sin(angle))
            ck(f'cup{n}/support shoulder',Part.Vertex(p).distToShape(cup)[0]<1e-6 and Part.Vertex(p).distToShape(byid['ClutchStack_support']['shape'])[0]<1e-6)
        for j in d['rivet_joints']:
            if j['kind']!='lining':continue
            p=origin+App.Vector(*j['base']);N=App.Vector(*j['normal']);line=Part.makeLine(p-N*4,p+N*(j['surface']+2))
            section=byid['ClutchCone_cone']['shape'].section(line)
            ck(j['name']+'/through hole',not section.Vertexes)
        result=dict(passed=not overlaps and all(x['passed'] for x in checks),native_sha256=sha(path),controls=c,
                    material_pairs=len(pairs),pairs=pairs,overlaps=overlaps,checks=checks,datums=d)
        write(out/(label+'.json'),result);results.append({k:v for k,v in result.items() if k not in ['pairs','datums']})
        print(label,'passed',result['passed'],'pairs',len(pairs),'failed',[x for x in checks if not x['passed']],flush=True)
        App.closeDocument(doc.Name)
    write(out/'report.json',dict(passed=all(x['passed'] for x in results),native_sha256=sha(native),scenarios=results,
        checker_sha256=sha(Path(__file__)),parts_sha256=sha(HERE/'clutch_cone_parts.py'),standard_native_hashes=standard['native_hashes']))
    assert all(x['passed'] for x in results)
finally:
    runtime.close()
