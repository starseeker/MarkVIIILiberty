"""Exercise coupled drum stock/bend changes and uncertain starter tooth counts."""
import argparse
import math
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,default=HERE/'clutch_drum_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();base=a.candidate.resolve();out=base/'variants';out.mkdir(exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(base),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part,numpy as np
    from lib.cad_build import leaves,metadata
    from lib.worker import check_build
    from clutch_drum_parts import build
    from case_joint_mass import calculator
    App.ParamGet('User parameter:BaseApp/Preferences/Document').SetInt('CountBackupFiles',0)
    r=read(base/'report.json');native=base/'TransmissionWithClutchDrum.FCStd';assert sha(native)==r['native_sha256']
    nominal=App.openDocument(str(native));items=leaves(nominal.Root);origin=nominal.TransmissionCore.Placement.Base
    standard=check_build(STAGE/'build');td=App.openDocument(standard['build']['top_document'])
    context=[i for i in items if i['id'] not in r['affected_ids']]+[i for i in leaves(td.Root) if i['representation']=='assembly']
    cone=read(HERE/'clutch_cone_build/report.json');retention=read(HERE/'clutch_retention_build/report.json')
    mass=calculator(out/'mass');results=[]
    scenarios=[dict(name='thinner_drum_122_teeth',drum_stock=5.5,drum_inner_bend_radius=24.,starter_teeth=122),
        dict(name='thicker_drum_126_teeth',drum_stock=6.5,drum_inner_bend_radius=26.,starter_teeth=126)]
    for variant in scenarios:
        label=variant['name'];c=dict(r['controls'],**{k:v for k,v in variant.items() if k!='name'})
        print('Constructing',label,flush=True)
        parts,occ,retained,spines,d=build(c,cone,retention);parts['retention']=retained
        occ += [dict(name='ClutchRetention_Wire',key='retention',xyz=[0,0,0],rotation=[0,0,0,1])]
        doc=App.newDocument('DrumVariant');root=doc.addObject('App::Part','Root');root.Placement.Base=origin
        library=doc.addObject('App::Part','Definitions');defs={}
        for key,shape in parts.items():
            obj=doc.addObject('PartDesign::Feature','Def_'+key);library.addObject(obj);obj.Shape=shape
            metadata(obj,DefinitionId=key,Representation='assembly',Coverage='partial');defs[key]=obj
        for row in occ:
            obj=doc.addObject('App::Link',row['name']);root.addObject(obj);obj.setLink(defs[row['key']])
            obj.LinkPlacement=App.Placement(App.Vector(*row['xyz']),App.Rotation(*row['rotation']))
            metadata(obj,OccurrenceId=obj.Name,Subsystem='Powerplant' if row['key']=='flywheel' else 'Drivetrain')
        library.Visibility=False;doc.recompute();path=out/(label+'.FCStd');doc.saveAs(str(path));App.closeDocument(doc.Name)
        doc=App.openDocument(str(path));items=leaves(doc.Root);byid={i['id']:i for i in items};s={}
        for n,i in byid.items():
            shape=i['shape'].copy();shape.translate(-origin);s[n]=shape
        checks=[]
        def ck(name,passed,detail=None):checks.append(dict(name=name,passed=bool(passed),detail=detail))
        fly=s['ClutchDrum_flywheel'];drum=s['ClutchDrum_drum'];wire=s['ClutchDrum_wire']
        ck('ten saved valid solids',len(items)==10 and all(i['shape'].isValid() and len(i['shape'].Solids)==1 for i in items))
        ck('printed largest flywheel diameter retained',abs(fly.BoundBox.YLength-19.811*25.4)<2e-5)
        tips=[f for f in fly.Faces if type(f.Surface).__name__=='Cylinder' and abs(f.Surface.Radius-19.811*25.4/2)<1e-6]
        ck('physical tooth count follows changed parameter',len(tips)==c['starter_teeth'],len(tips))
        ck('held-out involute fit remains below .001mm',d['starter_tooth_profile']['max_flank_fit_error_mm']<.001)
        normal=App.Vector(.2598,math.sqrt(1-.2598**2),0)
        point=App.Vector((958.7506231548401+1020.0701884885083)/2,(19.186+17.887)*25.4/4,0)
        ck('changed normal stock is physical',Part.Vertex(point+normal*c['drum_stock']).distToShape(drum)[0]<1e-6
            and drum.isInside(point+normal*(c['drum_stock']-.05),1e-7,False)
            and not drum.isInside(point+normal*(c['drum_stock']+.05),1e-7,False))
        ck('flywheel face moved with drum flange',abs(d['flywheel_joint']-r['datums']['flywheel_joint'])>.5)
        ck('blind screw bottom retains more than 4mm stock',d['blind_back_wall']>4)
        for radius in [169,180,200]:
            point=App.Vector(d['flywheel_joint'],radius*math.cos(.3),radius*math.sin(.3))
            ck('full flange support '+str(radius),Part.Vertex(point).distToShape(fly)[0]<1e-6 and Part.Vertex(point).distToShape(drum)[0]<1e-6)
        for n in range(1,7):
            theta=math.radians(60*(n-1));radial=App.Vector(0,math.cos(theta),math.sin(theta));tangent=App.Vector(0,-math.sin(theta),math.cos(theta))
            point=radial*188+App.Vector(d['bolt_seat']-c['bolt_head_height']/2,0,0)
            screw=s[f'ClutchDrum_Screw{n}']
            ck(f'screw{n}/wire follows moved drilled head',wire.isInside(point,1e-7,False) and not screw.section(Part.makeLine(point-tangent*18,point+tangent*18)).Vertexes)
            tip=d['bolt_seat']+31.75+c['blind_tip_gap']
            for angle in range(0,360,45):
                q=radial*188+App.Vector(tip+.05,0,0)+radial*(7.9*math.cos(math.radians(angle)))+tangent*(7.9*math.sin(math.radians(angle)))
                ck(f'screw{n}/blind bottom {angle}',fly.isInside(q,1e-7,False))
        wire_metrics={}
        for key,name,length in [('drum','ClutchDrum_wire',1219.2),('retention','ClutchRetention_Wire',762.)]:
            m=mass(s[name],label+'_'+key);wire_metrics[key]=dict(mass=m,centerline_length=spines[key].Length)
            ck(key+'/printed cut length retained',abs(spines[key].Length-length)<1e-5)
            ck(key+'/round section volume',abs(m['volume_mm3']-math.pi*.75**2*length)<.05)
        physical=items+context;pairs=[];seen=set()
        boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].copy().cleaned().BoundBox for i in physical]])
        for i in items:
            shape=i['shape'];b=shape.copy().cleaned().BoundBox;bb=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
            near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
            for idx in near:
                other=physical[idx];pair=tuple(sorted([i['id'],other['id']]))
                if i['id']==other['id'] or pair in seen:continue
                seen.add(pair);pairs.append(dict(a=i['id'],b=other['id'],intersection_mm3=shape.common(other['shape']).Volume))
            write(out/'progress.json',dict(scenario=label,last=i['id'],pairs=len(pairs)))
        overlaps=[x for x in pairs if abs(x['intersection_mm3'])>1e-5]
        row=dict(name=label,passed=all(x['passed'] for x in checks) and not overlaps,native_sha256=sha(path),controls=c,datums=d,
            checks=checks,pairs=pairs,overlaps=overlaps,wire_metrics=wire_metrics)
        write(out/(label+'.json'),row);results.append(dict(name=label,passed=row['passed'],native_sha256=sha(path),report_sha256=sha(out/(label+'.json'))))
        print(label,row['passed'],len(pairs),'pairs',len(checks),'checks',flush=True);App.closeDocument(doc.Name)
    write(out/'report.json',dict(passed=all(x['passed'] for x in results),native_sha256=r['native_sha256'],scenarios=results,
        checker_sha256=sha(Path(__file__)),parts_sha256=sha(HERE/'clutch_drum_parts.py'),standard_native_hashes=standard['native_hashes']))
    assert all(x['passed'] for x in results)
finally:
    runtime.close()
