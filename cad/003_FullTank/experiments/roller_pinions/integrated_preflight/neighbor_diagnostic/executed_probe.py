"""Inspect all new pinion/vehicle contacts in the failed integrated native build."""
from pathlib import Path
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parent;STAGE=ROOT/'cad/003_FullTank'
OUT=ROOT/'runs/neighbor_diagnostic'
sys.path.insert(0,str(STAGE))
from lib import runtime
from lib.evidence import fingerprint,sha,write
if '--worker' not in sys.argv:
    OUT.mkdir(parents=True,exist_ok=True)
    with (OUT/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=runtime.environment(OUT),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui()
    import numpy as np
    from lib.model import load
    from lib.cad_build import leaves
    from lib.visual_review import shaded
    lock=fingerprint();data=load();native=STAGE/'build/native/MarkVIII.FCStd'
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root)
    selected=[i for i in items if i['id'].startswith(('PortPinion_','StarboardPinion_'))]
    physical=[i for i in items if i['representation']=='assembly']
    boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].BoundBox for i in physical]])
    ids={i['id'] for i in selected};pairs=[];overlaps=[]
    for first in selected:
        b=first['shape'].BoundBox;bb=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
        near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
        for n in near:
            second=physical[n]
            if second['id'] in ids and second['id']<=first['id']:continue
            volume=first['shape'].common(second['shape']).Volume
            row=dict(a=first['id'],b=second['id'],overlap_mm3=volume)
            pairs.append(row)
            if volume>1e-5:
                overlaps.append(row);print(row,flush=True)
    keep={'hull_fuel_back','hull_floor_fuel','hull_roof_fuel','hull_port_inner_rear_end','hull_port_inner_fuel_side'}
    view=[i for i in items if i['id'] in keep or i['id'].startswith('PortPinion_')]
    print('Context:',[i['id'] for i in view if not i['id'].startswith('PortPinion_')],flush=True)
    for name,direction in [('oblique',(1,1,.65)),('plan',(0,0,1)),('axial',(0,1,0))]:
        shaded(view,OUT/(name+'.svg'),direction,'Integrated pinion / fuel compartment | interference diagnostic')
    write(OUT/'report.json',dict(passed=not overlaps,authored_fingerprint=lock,
        native_sha256={str(p.relative_to(STAGE)):sha(p) for p in (STAGE/'build/native').rglob('*.FCStd')},
        candidates=len(pairs),overlaps=overlaps,visual_review_status='pending',
        renders={n:sha(OUT/(n+'.png')) for n in ['oblique','plan','axial']}))
    shutil.copy2(__file__,OUT/'executed_probe.py')
    assert fingerprint()==lock
finally:
    runtime.close()
