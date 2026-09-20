"""Recheck frame/bracket interference using bounds without display triangulation."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage',type=Path,required=True)
parser.add_argument('--worker',action='store_true')
args=parser.parse_args();stage=args.stage.resolve();out=ROOT/'transmission_frame_clearance_build'
sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import read,write,sha

if not args.worker:
    with (out/'bounds_run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--worker'],
                               env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)

try:
    App,Gui=runtime.start_gui()
    import numpy as np
    from lib.cad_build import leaves
    r=read(out/'report.json');native=out/'TransmissionFrameCandidate.FCStd'
    assert sha(native)==r['native_sha256']
    for name,digest in r['tank_native_hashes'].items():assert sha(stage/'build'/name)==digest
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root)
    tank=App.openDocument(str(stage/'build/native/MarkVIII.FCStd'));tank.recompute()
    replaced={'hull_engine_back','PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting',
              'hull_port_inner_rear_end','hull_port_rear_wing','hull_starboard_inner_rear_end','hull_starboard_rear_wing'}
    context=[i for i in leaves(tank.Root) if i['id'] not in replaced and i['representation']=='assembly']
    physical=items+context;byid={i['id']:i for i in physical};assert len(physical)==len(byid)
    selected=[i for i in items if i['id'].startswith('TransmissionFrame_')
              or ('FixedBearing_' in i['id'] and i['id'].endswith('_bracket'))]
    assert len(selected)==19
    def bounds(shape,clean):
        b=(shape.copy().cleaned() if clean else shape).BoundBox
        return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
    pairs={}
    for clean in [False,True]:
        boxes=np.array([bounds(i['shape'],clean) for i in physical]);found=set()
        for item in selected:
            bb=np.array(bounds(item['shape'],clean))
            near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
            for index in near:
                pair=tuple(sorted([item['id'],physical[index]['id']]))
                if pair[0]!=pair[1]:found.add(pair)
        pairs[clean]=found
    union=pairs[True]|pairs[False];overlaps=[]
    print('Checking',len(union),'frame/bracket material pairs with cleaned bounds.',flush=True)
    for index,(a,b) in enumerate(sorted(union)):
        volume=byid[a]['shape'].common(byid[b]['shape']).Volume
        if volume>1e-5:overlaps.append(dict(a=a,b=b,volume_mm3=volume))
        if index%25==0:print('Checked',index+1,'of',len(union),flush=True)
    result=dict(passed=not overlaps,native_sha256=sha(native),nominal_report_sha256=sha(out/'report.json'),
                selected_occurrences=len(selected),cached_candidate_pairs=len(pairs[False]),
                cleaned_candidate_pairs=len(pairs[True]),tested_union_pairs=len(union),
                added_pairs=sorted(pairs[True]-pairs[False]),overlaps=overlaps,
                scope='Nominal frame/bracket material only; does not qualify historical form, attachment or uncertain ranges',
                script_sha256=sha(Path(__file__)),tank_native_hashes=r['tank_native_hashes'])
    write(out/'bounds_checks.json',result)
    (out/'inputs/check_transmission_frame_bounds.py').write_bytes(Path(__file__).read_bytes())
    assert sha(native)==r['native_sha256']
    for name,digest in r['tank_native_hashes'].items():assert sha(stage/'build'/name)==digest
    print('PASS' if result['passed'] else 'FAIL',flush=True)
    sys.exit(0 if result['passed'] else 1)
finally:runtime.close()
