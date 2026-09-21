"""Local sensitivity of fork thickness and installed detent spring height."""
import argparse,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--candidate',type=Path,default=ROOT/'transmission_reversing_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();stage=a.stage.resolve();out=a.candidate.resolve();sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import read,write,sha
if not a.worker:
    with (out/'sensitivity_run.log').open('w') as log:sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--candidate',str(out),'--worker'],env=runtime.environment(out/'sensitivity_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part
    from lib.cad_build import leaves
    from transmission_reversing_parts import reversing_parts
    report=read(out/'report.json');assert report['passed']
    parent=ROOT/'transmission_case_joint_build/TransmissionCaseJointCandidate.FCStd'
    assert sha(parent)==report['input_hashes']['transmission_case_joint_build/TransmissionCaseJointCandidate.FCStd']
    doc=App.openDocument(str(parent));doc.recompute();byid={i['id']:i for i in leaves(doc.Root)}
    base=read(ROOT/'transmission_reversing_controls.json')['controls'];rows=[]
    for change in [dict(fork_width=4.8),dict(fork_width=5.7),dict(spring_seat_z=188,spring_installed_height=26)]:
        c=dict(base,**change)
        solids,d=reversing_parts(c,*[byid[n]['target'].Shape for n in ['CenterTransmissionCore_bevel_case','CenterBevelDrive_clutch','PortBevelDrive_clutch_ring']])
        solids['clutch'].translate(App.Vector(0,c['forward_y'],0))
        twin=solids['clutch_ring'].copy();twin.rotate(App.Vector(),App.Vector(1,0,0),180);solids['starboard_ring']=twin
        nut=byid['PortSmallPlanetSupports_nut0']['target'].Shape.copy();nut.rotate(App.Vector(),App.Vector(1,0,0),180)
        nut.translate(App.Vector(c['rod_axis_xz'][0],323.85+d['nut_seat_y_mm'],c['rod_axis_xz'][1]));solids['nut']=nut
        overlap=[];pairs=0;ids=list(solids)
        for n,one in enumerate(ids):
            s=solids[one]
            for two in ids[n+1:]:
                t=solids[two]
                if not s.BoundBox.intersect(t.BoundBox):continue
                pairs+=1;v=s.common(t).Volume
                if v>1e-5:overlap.append([one,two,v])
        gaps={k:solids['spring'].distToShape(solids[k])[0] for k in ['plunger','cap']}
        valid=all(s.isValid() and len(s.Solids)==1 for s in solids.values())
        rows.append(dict(change=change,passed=valid and not overlap and all(v<1e-5 for v in gaps.values()),solid_count=len(solids),material_pairs=pairs,overlaps=overlap,spring_seat_gaps_mm=gaps,dimensions=d))
        write(out/'sensitivity_progress.json',dict(trials=rows));print(change,rows[-1]['passed'],overlap,flush=True)
    passed=all(r['passed'] for r in rows)
    write(out/'sensitivity_checks.json',dict(passed=passed,trials=rows,checker_sha256=sha(Path(__file__)),generator_sha256=sha(ROOT/'transmission_reversing_parts.py'),
        report_sha256=sha(out/'report.json'),parent_native_sha256=sha(parent),scope='Eleven local solids per rebuild; surrounding train and full tank not requalified by these trials.'))
    sys.exit(0 if passed else 1)
finally:runtime.close()
