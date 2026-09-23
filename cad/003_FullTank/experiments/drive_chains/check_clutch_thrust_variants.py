"""Exercise uncertain thrust race radius and axial position in the installed context."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,default=HERE/'clutch_thrust_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();base=a.candidate.resolve();out=base/'variants';out.mkdir(exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(base),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part,numpy as np
    from lib.cad_build import leaves
    from lib.worker import check_build
    from clutch_thrust_parts import build
    r=read(base/'report.json');native=base/'TransmissionWithClutchThrust.FCStd';nh=sha(native);assert nh==r['native_sha256']
    for rel,h in r['input_hashes'].items():assert sha(ROOT/rel)==h,rel
    parent=Part.Shape();parent.read(str(base/'inputs/parent_thrust.brep'));assert sha(base/'inputs/parent_thrust.brep')==r['parent_thrust_sha256']
    standard=check_build(STAGE/'build');td=App.openDocument(standard['build']['top_document']);td.recompute()
    context=[i for i in leaves(td.Root) if i['representation']=='assembly'];scenarios=[]
    for delta in [-1,1]:
        c=dict(r['controls']);c['ball_pitch_radius']+=.5*delta;c['race_floor_depth']+=.2*delta
        parts,occ,thrust,datums=build(c,r['parent_controls'],parent)
        doc=App.openDocument(str(native));doc.recompute();byid={i['id']:i for i in leaves(doc.Root)}
        for key,shape in parts.items():doc.getObject('Def_ClutchThrust_'+key).Tip.Shape=shape
        byid['ClutchStack_thrust']['target'].Tip.Shape=thrust
        for row in occ:byid[row['name']]['object'].LinkPlacement=App.Placement(App.Vector(*row['xyz']),App.Rotation())
        doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items};physical=items+context
        boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].copy().cleaned().BoundBox for i in physical]])
        pairs=[];seen=set()
        for n in r['affected_ids']:
            shape=byid[n]['shape'];assert shape.isValid() and len(shape.Solids)==1
            b=shape.copy().cleaned().BoundBox;bb=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
            near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
            for idx in near:
                other=physical[idx];pair=tuple(sorted([n,other['id']]))
                if n==other['id'] or pair in seen:continue
                seen.add(pair);pairs.append(dict(a=n,b=other['id'],intersection_mm3=shape.common(other['shape']).Volume))
        contacts=[]
        for n in range(1,31):
            ball=byid[f'ClutchThrust_Ball{n:02}']['shape']
            for name,want in [('ClutchStack_thrust',0),('ClutchThrust_Stop',0),('ClutchThrust_Cage',.125)]:
                shape=byid[name]['shape'];value=ball.distToShape(shape)[0]
                if name=='ClutchThrust_Cage':
                    contacts.append(dict(ball=n,other=name,actual=value,expected=want,passed=abs(value-want)<1e-6))
                else:
                    sign=-1 if name=='ClutchStack_thrust' else 1
                    point=ball.Solids[0].CenterOfMass+App.Vector(sign*3.175,0,0);vertex=Part.Vertex(point)
                    db,dr=vertex.distToShape(ball)[0],vertex.distToShape(shape)[0]
                    behind=shape.isInside(point+App.Vector(sign*.01,0,0),1e-7,False)
                    contacts.append(dict(ball=n,other=name,whole_shape_distance_diagnostic=value,
                        point_on_ball=db,point_on_race=dr,material_beyond=behind,passed=db<1e-6 and dr<1e-6 and behind))
        overlaps=[x for x in pairs if abs(x['intersection_mm3'])>1e-5]
        row=dict(controls=c,datums=datums,material_pairs=len(pairs),overlaps=overlaps,contacts=contacts,
                 passed=not overlaps and all(x['passed'] for x in contacts))
        name='smaller' if delta<0 else 'larger';write(out/(name+'.json'),dict(row,pairs=pairs));scenarios.append(row)
        write(out/'progress.json',dict(completed=len(scenarios),scenarios=scenarios));print(name,row['passed'],overlaps,flush=True)
        App.closeDocument(doc.Name)
    assert sha(native)==nh
    for rel,h in r['input_hashes'].items():assert sha(ROOT/rel)==h,rel
    write(out/'report.json',dict(passed=all(x['passed'] for x in scenarios),scenarios=scenarios,native_sha256=nh,
        checker_sha256=sha(Path(__file__)),parts_sha256=sha(HERE/'clutch_thrust_parts.py'),standard_native_hashes=standard['native_hashes'],
        scope='Two coupled pitch-radius (+/-0.5 mm) and race-depth (+/-0.2 mm) variations. Printed ball size/count unchanged. All affected parts checked in full native and standard physical context. Not a manufacturing tolerance or load qualification.'))
    sys.exit(0 if all(x['passed'] for x in scenarios) else 1)
finally:
    runtime.close()
