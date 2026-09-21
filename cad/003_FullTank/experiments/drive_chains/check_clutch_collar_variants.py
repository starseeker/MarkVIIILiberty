"""Vary coupled collar length/lip stock while retaining printed screws and wire."""
import argparse,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];REPO=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,default=HERE/'clutch_collar_build')
p.add_argument('--worker',action='store_true');a=p.parse_args();base=a.candidate.resolve();out=base/'variants';out.mkdir(parents=True,exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(base),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part,numpy as np
    from lib.cad_build import leaves
    from lib.worker import check_build
    from clutch_collar_parts import build
    report=read(base/'report.json');native=base/'TransmissionWithClutchCollar.FCStd';nh=sha(native);assert nh==report['native_sha256']
    for path,h in report['input_hashes'].items():assert sha(REPO/path)==h,path
    standard=check_build(STAGE/'build');td=App.openDocument(standard['build']['top_document']);td.recompute()
    context=[i for i in leaves(td.Root) if i['representation']=='assembly'];scenarios=[]
    for delta in [-1,1]:
        c=dict(report['controls'])
        for name in ['joint_face','ring_shoulder','collar_front','collar_front_flange_start','collar_bore_step']:c[name]+=delta*4
        c['collar_lip_stock']+=delta*.5;c['collar_body_radius']+=delta*1.5
        parts,occ,coupling,spine,details=build(c,report['drive_controls'])
        doc=App.openDocument(str(native));doc.recompute();byid={i['id']:i for i in leaves(doc.Root)}
        for key,s in parts.items():doc.getObject('Def_ClutchCollar_'+key).Tip.Shape=s
        byid['FrontClutch_Coupling']['target'].Tip.Shape=coupling
        for row in occ:
            byid[row['name']]['object'].LinkPlacement=App.Placement(App.Vector(*row['xyz']),App.Rotation(App.Vector(1,0,0),row['angle']))
        doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items};physical=items+context
        boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].copy().cleaned().BoundBox for i in physical]])
        pairs=[];seen=set()
        for n in report['affected_ids']:
            s=byid[n]['shape'];assert s.isValid() and len(s.Solids)==1,n
            b=s.copy().cleaned().BoundBox;bb=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
            near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
            for idx in near:
                other=physical[idx];pair=tuple(sorted([n,other['id']]))
                if n==other['id'] or pair in seen:continue
                seen.add(pair);v=s.common(other['shape']).Volume;pairs.append(dict(a=n,b=other['id'],intersection_mm3=v))
        contacts=[]
        seating=[('FrontClutch_Spring','FrontClutch_UpperFlange'),('FrontClutch_Spring','FrontClutch_LowerFlange'),
            ('FrontClutch_Spring','FrontClutch_Coupling'),('FrontClutch_UpperFlange','ClutchDrive_shaft'),('FrontClutch_LowerFlange','ClutchDrive_shaft'),
            ('ClutchCollar_collar','FrontClutch_Coupling'),('ClutchCollar_ring','FrontClutch_Coupling'),
            ('ClutchCollar_ring','ClutchCollar_collar'),('ClutchCollar_bush','ClutchCollar_ring'),('ClutchCollar_bush','FrontClutch_Coupling')]
        seating += [(f'ClutchCollar_Screw{n}','ClutchCollar_collar') for n in range(1,7)]
        for an,bn in seating:
            distance=byid[an]['shape'].distToShape(byid[bn]['shape'])[0];contacts.append(dict(a=an,b=bn,gap_mm=distance,passed=distance<1e-5))
        overlaps=[r for r in pairs if r['intersection_mm3']>1e-5]
        row=dict(controls=c,thread_engagement=details['thread_engagement'],blind_back_wall=details['blind_back_wall'],
            wire_length=spine.Length,material_pairs=len(pairs),overlaps=overlaps,contacts=contacts,
            passed=not overlaps and all(x['passed'] for x in contacts) and abs(spine.Length-660.4)<1e-5)
        scenarios.append(row);write(out/('shorter.json' if delta<0 else 'longer.json'),dict(**row,pairs=pairs))
        write(out/'progress.json',dict(completed=len(scenarios),scenarios=scenarios));print('Scenario',delta,row['passed'],overlaps,flush=True)
        App.closeDocument(doc.Name)
    assert sha(native)==nh
    for path,h in report['input_hashes'].items():assert sha(REPO/path)==h,path
    result=dict(passed=all(x['passed'] for x in scenarios),scenarios=scenarios,native_sha256=nh,checker_sha256=sha(Path(__file__)),
        parts_sha256=sha(HERE/'clutch_collar_parts.py'),standard_native_hashes=standard['native_hashes'],
        scope='Two coherent axial-interface/lip-stock/body-radius samples, retaining printed screw and wire lengths, with full transmission and standard physical context. Not exhaustive uncertainty, historical fit or load qualification.')
    write(out/'report.json',result);print('Both coupled collar trials',result['passed'],flush=True)
    sys.exit(0 if result['passed'] else 1)
finally:runtime.close()
