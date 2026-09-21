from pathlib import Path
import sys,json
stage=Path('cad/003_FullTank').resolve();root=stage/'experiments/drive_chains';sys.path[:0]=[str(stage),str(root)]
from lib import runtime
if '--worker' not in sys.argv:
    import subprocess
    sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=runtime.environment(Path(__file__).parent)).returncode)
try:
    App,Gui=runtime.start_gui();import Part
    from lib.cad_build import leaves
    doc=App.openDocument(str(root/'transmission_case_joint_build/TransmissionCaseJointCandidate.FCStd'));byid={i['id']:i for i in leaves(doc.Root)}
    origin=App.Vector(*json.load(open(root/'transmission_case_joint_build/report.json'))['shaft_axis_world_mm'])
    def local(n):
        s=byid[n]['shape'].Solids[0].copy();s.translate(-origin);return s
    rows=[]
    for suffix in ['Upper','Lower']:
        g=local('CentralCaseJoint_gasket'+suffix)
        for label,delta in [('case',-.001),('cover',.001)]:
            s=local('CenterTransmissionCore_bevel_'+label);probe=g.copy();probe.translate(App.Vector(delta,0,0))
            overlap=probe.common(s);expected=g.Volume/.3*.001
            samples=[]
            for y,z in [(40,218),(119,150),(150,67)]:
                sign=1 if suffix=='Upper' else -1;point=App.Vector(-.1505 if label=='case' else .1505,y,sign*z)
                samples.append([list(point),s.isInside(point,1e-7,False)])
            rows.append(dict(suffix=suffix,case=label,overlap=overlap.Volume,expected=expected,fraction=overlap.Volume/expected,samples=samples))
    print(json.dumps(rows,indent=2),flush=True)
finally:runtime.close()
