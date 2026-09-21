"""Two coherent dimension trials; no vehicle poses or historical tolerance claim."""
import argparse,copy,math,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,default=HERE/'air_pressure_pump_build/variants')
p.add_argument('--worker',action='store_true');a=p.parse_args();out=a.output.resolve();out.mkdir(exist_ok=True,parents=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--worker','--output',str(out)],
            env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui()
    from air_pressure_pump_parts import build,moved
    base=read(HERE/'air_pressure_pump_controls.json')['controls'];trials=[]
    for name,length,seat,ecc in [('short_low',126,54,2.5),('long_high',154,60,4.5)]:
        c=copy.deepcopy(base);delta=(length-c['body_length'])/2
        c.update(body_length=length,bank_seat=seat,cam_eccentricity=ecc)
        c['foot_hole_x']+=delta;c['oil_plug_x']=[v+(delta if v>0 else -delta) for v in c['oil_plug_x']]
        for k in ['pulley_rim_start','pulley_rim_end','pulley_hub_start','pulley_hub_end','shaft_thread_end','key_station_x']:c[k]+=delta
        parts,occ,detail=build(c)
        shapes={r['name']:moved(parts[r['key']],r['xyz'],App.Rotation(*r['rotation'])) for r in occ}
        boxes={n:s.copy().cleaned().BoundBox for n,s in shapes.items()};overlaps=[];pairs=0
        for index,(n,s) in enumerate(shapes.items()):
            for m,t in list(shapes.items())[index+1:]:
                if not boxes[n].intersect(boxes[m]):continue
                pairs+=1;v=s.common(t).Volume
                if v>1e-5:overlaps.append(dict(a=n,b=m,volume_mm3=v))
        gaps=[]
        for bank in detail['banks']:
            n=bank['name']
            for one,two in [(n+'_spring',n+'_piston'),(n+'_spring',n+'_cylinder'),(n+'_piston','shaft'),(n+'_cylinder','base')]:
                gap=shapes[one].distToShape(shapes[two])[0]
                gaps.append(dict(a=one,b=two,gap_mm=gap,passed=gap<1e-5))
        for label,sign in [('Rear',-1),('Front',1)]:
            shifted=shapes['shaft'].copy();shifted.translate(App.Vector(sign*(c['shaft_axial_gap']+.05),0,0))
            stopped=shifted.common(shapes[label+'Bush']).Volume>.01
            gaps.append(dict(a='shaft',b=label+'Bush',axial_stop_detected=stopped,passed=stopped))
        trials.append(dict(name=name,controls=c,physical_occurrences=len(occ),material_pairs=pairs,
            overlaps=overlaps,interfaces=gaps,passed=not overlaps and all(g['passed'] for g in gaps)))
        write(out/'progress.json',dict(completed=len(trials),trials=trials))
        print(name,'pairs',pairs,'overlaps',overlaps,'bad gaps',[x for x in gaps if not x['passed']],flush=True)
    write(out/'report.json',dict(passed=all(t['passed'] for t in trials),trials=trials,
        controls_sha256=sha(HERE/'air_pressure_pump_controls.json'),generator_sha256=sha(HERE/'air_pressure_pump_parts.py'),
        checker_sha256=sha(Path(__file__)),scope='Two coupled dimension samples: body length126/154mm,bank seat54/60mm,cam eccentricity2.5/4.5mm. End hardware,oil plugs,feet,pulley and key move with the case ends. Local topology/material/contact only; no vehicle context,STEP,continuous motion or full uncertainty-domain proof.'))
    sys.exit(0 if all(t['passed'] for t in trials) else 1)
finally:runtime.close()
