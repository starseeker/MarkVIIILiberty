"""Strict STEP round trips for the coupled receiver in both exported frames."""
import argparse
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,required=True)
p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.candidate.resolve()
if not a.worker:
    with (out/'exchange_check.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(out),'--worker'],
            env=runtime.environment(out/'exchange_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)

try:
    import FreeCAD as App
    import Part
    from case_joint_mass import calculator
    r=read(out/'report.json');native=out/r['native_file'];assert sha(native)==r['native_sha256']
    parent=r['parent_reports']['drive'];parent_path=ROOT/parent['path']
    assert sha(parent_path)==parent['sha256']
    origin=read(parent_path)['engine_origin'];assert origin==r['engine_origin']
    doc=App.openDocument(str(native));definition=doc.Def_EngineCase_lower.Shape.copy()
    App.closeDocument(doc.Name)
    assert definition.isValid() and len(definition.Solids)==1
    installed=definition.copy();installed.translate(App.Vector(*origin))
    mass=calculator(out/'exchange_runtime/mass');checks=[]
    for label,shape in [('Definition',definition),('Installation',installed)]:
        path=out/('PumpReceiver'+label+'.step');assert sha(path)==r['step_hashes'][path.name]
        loaded=Part.Shape();loaded.read(str(path))
        assert loaded.isValid() and len(loaded.Solids)==1,label
        one,two=shape.Solids[0],loaded.Solids[0]
        ma,mb=mass(one,label+'_native'),mass(two,label+'_step')
        ta,tb=one.getTolerance(1),two.getTolerance(1);fuzzy=min(1e-4,max(1e-7,ta+tb))
        missing,added=one.cut(two).Volume,two.cut(one).Volume
        fm,fa=len(one.cut(two,fuzzy).Faces),len(two.cut(one,fuzzy).Faces)
        dv=abs(ma['volume_mm3']-mb['volume_mm3'])
        dc=(App.Vector(*ma['center_mm'])-App.Vector(*mb['center_mm'])).Length
        passed=abs(missing)<1e-5 and abs(added)<1e-5 and not fm and not fa and ta<=1e-4 and \
            tb<=max(1e-7,ta)+1e-10 and dv<=(one.Area+two.Area)/2*(ta+tb) and dc<max(1e-6,ta+tb)
        checks.append(dict(scope=label,passed=passed,missing_mm3=missing,added_mm3=added,
            fuzzy_missing_faces=fm,fuzzy_added_faces=fa,mass_difference_mm3=dv,
            centroid_difference_mm=dc,native_max_tolerance_mm=ta,step_max_tolerance_mm=tb,
            step_sha256=sha(path)))
        write(out/'exchange_progress.json',dict(checks=checks));print(label,passed,flush=True)
    result=dict(passed=all(x['passed'] for x in checks),native_sha256=sha(native),
        checker_sha256=sha(Path(__file__)),checks=checks,engine_origin=origin,
        installation_qualified=False,scope='Receiver material exchange only; inherited installation frame')
    write(out/'exchange_checks.json',result)
    assert result['passed']
finally:
    runtime.close()
