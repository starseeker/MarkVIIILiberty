"""Check the uncertain wire/hole sizes and an alternate seam against fixed neighbors."""
import argparse
import math
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,default=HERE/'clutch_retention_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();base=a.candidate.resolve();out=base/'variants';out.mkdir(exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(base),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part,numpy as np
    from lib.cad_build import leaves,metadata
    from lib.worker import check_build
    from clutch_retention_parts import build
    from case_joint_mass import calculator
    App.ParamGet('User parameter:BaseApp/Preferences/Document').SetInt('CountBackupFiles',0)
    r=read(base/'report.json');native=base/'TransmissionWithClutchRetention.FCStd';assert sha(native)==r['native_sha256']
    nominal=App.openDocument(str(native));items=leaves(nominal.Root);origin=nominal.TransmissionCore.Placement.Base
    untouched=[i for i in items if i['id'] not in r['affected_ids']]
    standard=check_build(STAGE/'build');td=App.openDocument(standard['build']['top_document'])
    context=untouched+[i for i in leaves(td.Root) if i['representation']=='assembly']
    blank=Part.Shape();blank.read(str(base/'inputs/plunger_blank.brep'));parent=read(HERE/'clutch_cone_build/report.json');results=[]
    mass=calculator(out/'mass')
    for variant in read(HERE/'clutch_retention_controls.json')['parameter_trials']:
        label=variant['name'];c=dict(r['controls'],**{k:v for k,v in variant.items() if k!='name'})
        plunger,wire,spine,occ,d=build(c,parent,blank)
        doc=App.newDocument('RetentionVariant');root=doc.addObject('App::Part','Root');root.Placement.Base=origin
        library=doc.addObject('App::Part','Definitions');defs={}
        for key,s in [('plunger',plunger),('wire',wire)]:
            obj=doc.addObject('PartDesign::Feature','Def_'+key);library.addObject(obj);obj.Shape=s
            metadata(obj,DefinitionId=key,Representation='assembly',Coverage='partial');defs[key]=obj
        occ+=[dict(name='ClutchRetention_Wire',key='wire',xyz=[0,0,0],angle=0)]
        for row in occ:
            obj=doc.addObject('App::Link',row['name']);root.addObject(obj);obj.setLink(defs[row['key']])
            obj.LinkPlacement=App.Placement(App.Vector(*row['xyz']),App.Rotation(App.Vector(1,0,0),row['angle']))
            metadata(obj,OccurrenceId=obj.Name,Subsystem='Drivetrain')
        library.Visibility=False;doc.recompute();path=out/(label+'.FCStd');doc.saveAs(str(path));App.closeDocument(doc.Name)
        doc=App.openDocument(str(path));items=leaves(doc.Root);byid={i['id']:i for i in items};w=byid['ClutchRetention_Wire']['shape'];checks=[]
        def ck(name,passed):checks.append(dict(name=name,passed=bool(passed)))
        ck('seven single valid saved solids',len(items)==7 and all(i['shape'].isValid() and len(i['shape'].Solids)==1 for i in items))
        ck('printed cut length retained',abs(spine.Length-762)<1e-5)
        # Default BRep volume quadrature drifted0.055mm3 on the larger spline sweep.
        # Explicit-accuracy integration resolves that numerical error; retain the criterion.
        actual_mass=mass(w,label);expected_volume=math.pi*(c['wire_diameter']/2)**2*762
        ck('changed wire size changes physical material',abs(actual_mass['volume_mm3']-expected_volume)<.05)
        ck('bore remains inside head thickness',d['head_wall_axial']>.5)
        for n in range(1,7):
            theta=math.radians(30+60*(n-1));s=byid[f'ClutchCone_Plunger{n}']['shape']
            point=origin+App.Vector(1019.3,114*math.cos(theta),114*math.sin(theta));tangent=App.Vector(0,-math.sin(theta),math.cos(theta))
            ck(f'head{n}/through passage',not s.section(Part.makeLine(point-tangent*8,point+tangent*8)).Vertexes)
            ck(f'head{n}/wire inside passage',w.isInside(point,1e-7,False) and not s.isInside(point,1e-7,False))
            ck(f'head{n}/changed bore removes material',not s.isInside(point+App.Vector(c['head_drill_radius']-.025,0,0),1e-7,False) and s.isInside(point+App.Vector(c['head_drill_radius']+.025,0,0),1e-7,False))
        physical=items+context;pairs=[];seen=set()
        boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].copy().cleaned().BoundBox for i in physical]])
        for i in items:
            s=i['shape'];b=s.copy().cleaned().BoundBox;bb=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
            near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
            for idx in near:
                other=physical[idx];pair=tuple(sorted([i['id'],other['id']]))
                if i['id']==other['id'] or pair in seen:continue
                seen.add(pair);pairs.append(dict(a=i['id'],b=other['id'],intersection_mm3=s.common(other['shape']).Volume))
        overlaps=[x for x in pairs if abs(x['intersection_mm3'])>1e-5]
        row=dict(name=label,passed=all(x['passed'] for x in checks) and not overlaps,native_sha256=sha(path),controls=c,datums=d,checks=checks,pairs=pairs,overlaps=overlaps,
            wire_mass=dict(default_volume_mm3=w.Volume,accurate=actual_mass,expected_volume_mm3=expected_volume))
        write(out/(label+'.json'),row);results.append(dict(name=label,passed=row['passed'],native_sha256=sha(path),report_sha256=sha(out/(label+'.json'))))
        print(label,row['passed'],len(pairs),'pairs',len(checks),'checks',flush=True);App.closeDocument(doc.Name)
    write(out/'report.json',dict(passed=all(x['passed'] for x in results),native_sha256=r['native_sha256'],scenarios=results,
        checker_sha256=sha(Path(__file__)),parts_sha256=sha(HERE/'clutch_retention_parts.py'),standard_native_hashes=standard['native_hashes']))
    assert all(x['passed'] for x in results)
finally:
    runtime.close()
