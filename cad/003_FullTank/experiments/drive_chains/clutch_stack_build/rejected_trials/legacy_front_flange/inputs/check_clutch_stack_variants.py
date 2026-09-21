"""Vary the fitted radial stack and rear bearing station while retaining HB transfers."""
import argparse,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];REPO=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,default=HERE/'clutch_stack_build')
p.add_argument('--worker',action='store_true');a=p.parse_args();base=a.candidate.resolve();out=base/'variants';out.mkdir(parents=True,exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(base),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part,numpy as np
    from lib.cad_build import leaves
    from lib.worker import check_build
    from clutch_stack_parts import build
    report=read(base/'report.json');native=base/'TransmissionWithClutchStack.FCStd';nh=sha(native);assert nh==report['native_sha256']
    for path,h in report['input_hashes'].items():assert sha(REPO/path)==h,path
    standard=check_build(STAGE/'build');td=App.openDocument(standard['build']['top_document']);td.recompute()
    context=[i for i in leaves(td.Root) if i['representation']=='assembly'];scenarios=[]
    parent_collar=Part.Shape();parent_collar.read(str(base/'inputs/parent_collar.brep'));assert sha(base/'inputs/parent_collar.brep')==report['parent_collar_sha256']
    for delta in [-1,1]:
        c=dict(report['controls'])
        for name in ['main_bore_radius','collar_body_radius','key_bed_radius','support_radius','support_flange_radius','snap_inner_radius','snap_outer_radius','thrust_outer_radius']:c[name]+=delta
        c['bearing_rear']+=delta*2;c['relief_rear']+=delta*2
        c['support_rear']+=delta*.5;c['key_rear']+=delta*.5
        parts,occ,collar=build(c,report['parent_controls'],parent_collar)
        doc=App.openDocument(str(native));doc.recompute();byid={i['id']:i for i in leaves(doc.Root)}
        for key,s in parts.items():doc.getObject('Def_ClutchStack_'+key).Tip.Shape=s
        byid['ClutchCollar_collar']['target'].Tip.Shape=collar
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
        seating=[('ClutchStack_bearing','ClutchCollar_collar',0),('ClutchStack_sleeve','ClutchCollar_collar',0),
            ('ClutchStack_bearing','ClutchStack_sleeve',0),('ClutchStack_bearing','ClutchStack_thrust',0),('ClutchStack_thrust','ClutchCollar_collar',0),('ClutchStack_thrust','ClutchStack_snap',1),
            ('ClutchStack_snap','ClutchCollar_collar',0),('ClutchStack_support','ClutchCollar_collar',.15),
            ('ClutchCollar_collar','FrontClutch_Coupling',0),('ClutchCollar_ring','ClutchCollar_collar',0)]
        seating += [(f'ClutchStack_Key{n}','ClutchCollar_collar',0) for n in range(1,5)]
        seating += [(f'ClutchStack_Key{n}','ClutchStack_support',.1) for n in range(1,5)]
        seating += [(f'ClutchCollar_Screw{n}','ClutchCollar_collar',0) for n in range(1,7)]
        for an,bn,want in seating:
            distance=byid[an]['shape'].distToShape(byid[bn]['shape'])[0]
            contacts.append(dict(a=an,b=bn,gap_mm=distance,expected_gap_mm=want,passed=abs(distance-want)<1e-5))
        overlaps=[r for r in pairs if abs(r['intersection_mm3'])>1e-5]
        wire_gap=byid['ClutchStack_support']['shape'].distToShape(byid['ClutchCollar_wire']['shape'])[0]
        row=dict(controls=c,material_pairs=len(pairs),overlaps=overlaps,contacts=contacts,wire_gap_mm=wire_gap,
            passed=not overlaps and all(x['passed'] for x in contacts) and wire_gap>.25)
        scenarios.append(row);write(out/('smaller.json' if delta<0 else 'larger.json'),dict(**row,pairs=pairs))
        write(out/'progress.json',dict(completed=len(scenarios),scenarios=scenarios));print('Scenario',delta,row['passed'],overlaps,flush=True)
        App.closeDocument(doc.Name)
    assert sha(native)==nh
    for path,h in report['input_hashes'].items():assert sha(REPO/path)==h,path
    result=dict(passed=all(x['passed'] for x in scenarios),scenarios=scenarios,native_sha256=nh,checker_sha256=sha(Path(__file__)),
        parts_sha256=sha(HERE/'clutch_stack_parts.py'),standard_native_hashes=standard['native_hashes'],
        scope='Two coherent radial-stack/rear-bearing-station samples retain printed HB key/sleeve transfers, with full transmission and standard physical context. Not exhaustive tolerance, torque, historical fit or assembly-deflection qualification.')
    write(out/'report.json',result);print('Both coupled stack trials',result['passed'],flush=True)
    sys.exit(0 if result['passed'] else 1)
finally:runtime.close()
