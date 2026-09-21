"""Local rebuild sensitivity for inferred joint grip and receiver clearance."""
import argparse
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--candidate',type=Path,default=ROOT/'transmission_case_joint_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();stage=a.stage.resolve();out=a.candidate.resolve();sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import read,write,sha
if not a.worker:
    with (out/'sensitivity_run.log').open('w') as log:sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--candidate',str(out),'--worker'],env=runtime.environment(out/'sensitivity_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part
    from lib.cad_build import leaves
    from transmission_case_joint_parts import case_joint_parts
    report=read(out/'report.json');assert report['passed']
    parent=ROOT/'transmission_brake_bearing_build/TransmissionBrakeBearingCandidate.FCStd'
    assert sha(parent)==report['input_hashes']['transmission_brake_bearing_build/TransmissionBrakeBearingCandidate.FCStd']
    doc=App.openDocument(str(parent));doc.recompute();byid={i['id']:i for i in leaves(doc.Root)}
    base=read(ROOT/'transmission_case_joint_controls.json')['controls'];rows=[]
    for change in [dict(half_grip=14),dict(half_grip=18),dict(receiver_gap=.25)]:
        c=dict(base,**change);shapes,d=case_joint_parts(c,*[byid['CenterTransmissionCore_'+k]['target'].Shape for k in ['bevel_case','bevel_cover']])
        solids={k:shapes[k] for k in ['case','cover','gasket_upper','gasket_lower']}
        for n,(y,z) in enumerate(d['axes_yz_mm']):
            for key,x in [('bolt',0),('nut',c['half_grip']),('cotter',d['cotter_axis_x_mm'])]:
                s=(shapes['bolt'] if key=='bolt' else byid['PortBrakeBearing_nut0' if key=='nut' else 'InputInstallation_mount_cotter0']['target'].Shape).copy()
                s.translate(App.Vector(x,y,z));solids[key+str(n)]=s
        overlap=[];pairs=0;ids=list(solids)
        for n,one in enumerate(ids):
            s=solids[one]
            for two in ids[n+1:]:
                t=solids[two]
                if not s.BoundBox.intersect(t.BoundBox):continue
                pairs+=1;v=s.common(t).Volume
                if v>1e-5:overlap.append([one,two,v])
        valid=all(s.isValid() and len(s.Solids)==1 for s in solids.values())
        rows.append(dict(change=change,passed=valid and not overlap,solid_count=len(solids),material_pairs=pairs,overlaps=overlap,dimensions=d))
        print(change,rows[-1]['passed'],overlap,flush=True)
    passed=all(r['passed'] for r in rows)
    write(out/'sensitivity_checks.json',dict(passed=passed,trials=rows,checker_sha256=sha(Path(__file__)),generator_sha256=sha(ROOT/'transmission_case_joint_parts.py'),
        report_sha256=sha(out/'report.json'),parent_native_sha256=sha(parent),scope='Forty-six local solids per rebuild; surrounding gear train and complete tank not requalified by these trials.'))
    sys.exit(0 if passed else 1)
finally:runtime.close()
