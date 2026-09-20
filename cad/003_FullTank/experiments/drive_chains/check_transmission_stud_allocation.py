"""Test the opposite inner stud corner allocation without changing saved CAD."""
import argparse
from collections import Counter
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage',type=Path,required=True)
parser.add_argument('--candidate',type=Path,default=ROOT/'transmission_stud_clearance_build')
parser.add_argument('--worker',action='store_true')
args=parser.parse_args();stage=args.stage.resolve();out=args.candidate.resolve()
sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import read,write,sha

if not args.worker:
    with (out/'allocation_run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--candidate',str(out),'--worker'],
                               env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)

try:
    App,Gui=runtime.start_gui()
    import numpy as np
    from lib.cad_build import leaves
    from transmission_stud_parts import hardware,receiving_castings
    r=read(out/'report.json');assert r['passed'] and r['rendering_complete']
    native=out/'TransmissionStudCandidate.FCStd';assert sha(native)==r['native_sha256']
    for name,digest in r['input_hashes'].items():assert sha(ROOT/name)==digest,name
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items}
    old=App.openDocument(str(ROOT/'transmission_lid_clearance_build/TransmissionLidCandidate.FCStd'));old.recompute()
    before={i['id']:i for i in leaves(old.Root)}
    c={k:v['value'] for k,v in read(ROOT/'transmission_stud_controls.json')['controls'].items()}
    support={k:v['value'] for k,v in read(ROOT/'transmission_support_controls.json')['controls'].items()}
    dims=read(ROOT/'transmission_support_clearance_build/report.json')['dimensions']
    shapes,stack,_=hardware(c,support)
    bracket,cap,locations,_=receiving_castings(before['PortFixedBearing_inner_bracket']['target'].Shape,
        before['PortFixedBearing_inner_cap']['target'].Shape,'inner',c,support,dims['inner'],stack,swap=True)
    assert bracket.isValid() and len(bracket.Solids)==1
    current=byid['PortFixedBearing_inner_cap']['target'].Shape
    cap_difference=cap.cut(current).Volume+current.cut(cap).Volume;assert cap_difference<1e-5
    altered={};allocation=[]
    for hand in ['Port','Starboard']:
        prefix=hand+'FixedBearing_inner_';item=byid[prefix+'bracket']
        frame=item['shape'].Placement.multiply(item['target'].Shape.Placement.inverse())
        shape=bracket.copy();shape.Placement=frame.multiply(shape.Placement);altered[prefix+'bracket']=shape
        for row in locations:
            name=prefix+'Stud'+str(row['index']).zfill(2)+'_Stud';shape=shapes[row['mark']].copy()
            shape.Placement=frame.multiply(App.Placement(App.Vector(row['tail_x_mm'],row['y_mm'],row['z_mm']),App.Rotation())).multiply(shape.Placement)
            altered[name]=shape;allocation.append(dict(hand=hand,occurrence=name,mark=row['mark'],z_mm=row['z_mm']))
    assert Counter(a['mark'] for a in allocation)=={'MX10':4,'MX36':4}
    for name,digest in r['tank_native_hashes'].items():assert sha(stage/'build'/name)==digest
    tank=App.openDocument(str(stage/'build/native/MarkVIII.FCStd'));tank.recompute()
    replaced={'hull_engine_back','PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting',
              'hull_port_inner_rear_end','hull_port_rear_wing','hull_starboard_inner_rear_end','hull_starboard_rear_wing'}
    context=[i for i in leaves(tank.Root) if i['id'] not in replaced and i['representation']=='assembly']
    physical={i['id']:altered.get(i['id'],i['shape']) for i in items+context};names=list(physical)
    boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [physical[n].copy().cleaned().BoundBox for n in names]])
    pairs=set();overlaps=[]
    for name,shape in altered.items():
        b=shape.copy().cleaned().BoundBox;bb=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
        near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
        for index in near:
            other=names[index];pair=tuple(sorted([name,other]))
            if name==other or pair in pairs:continue
            pairs.add(pair);volume=shape.common(physical[other]).Volume
            if volume>1e-5:overlaps.append(dict(a=name,b=other,volume_mm3=volume))
    result=dict(analysis_completed=True,native_sha256=sha(native),candidate_report_sha256=sha(out/'report.json'),
                script_sha256=sha(Path(__file__)),alternate_allocation=allocation,
                cap_material_difference_mm3=cap_difference,changed_brackets_and_studs=len(altered),
                material_candidate_pairs=len(pairs),overlaps=overlaps,alternative_nominal_clearance_pass=not overlaps,
                historical_allocation_qualified=False,thread_and_load_qualification=False,
                conclusion='A clearance result tests feasibility only. The inspected source schedule does not locate the two inner stud lengths by corner.')
    write(out/'allocation_checks.json',result)
    (out/'inputs/check_transmission_stud_allocation.py').write_bytes(Path(__file__).read_bytes())
    assert sha(native)==r['native_sha256']
    for name,digest in r['tank_native_hashes'].items():assert sha(stage/'build'/name)==digest
    print('Alternative allocation:',len(pairs),'material pairs,',len(overlaps),'overlaps.',flush=True)
finally:runtime.close()
