"""Strict native/STEP comparison of revised lower case in both frames."""
import argparse
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,default=HERE/'engine_lower_drive_installation');p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.candidate.resolve()
if not a.worker:
    with (out/'exchange_check.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(out),'--worker'],env=runtime.environment(out/'exchange_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App
    import Part
    from lib.cad_build import leaves
    from case_joint_mass import calculator
    r=read(out/'report.json');native=out/r['native_file'];assert sha(native)==r['native_sha256']
    doc=App.openDocument(str(native));case=next(i for i in leaves(doc.Root) if i['id']=='EngineCase_lower')
    mass=calculator(out/'exchange_runtime/mass');checks=[]
    for label,shape in [('Definition',case['target'].Shape),('Installation',case['shape'])]:
        path=out/('LowerCase'+label+'.step');loaded=Part.Shape();loaded.read(str(path))
        assert loaded.isValid() and len(loaded.Solids)==1,label
        one,two=shape.Solids[0],loaded.Solids[0]
        ma=mass(one,label+'_native');mb=mass(two,label+'_step')
        ta,tb=one.getTolerance(1),two.getTolerance(1);fuzzy=min(.0001,max(1e-7,ta+tb))
        missing,added=one.cut(two).Volume,two.cut(one).Volume
        fuzzy_missing,fuzzy_added=len(one.cut(two,fuzzy).Faces),len(two.cut(one,fuzzy).Faces)
        dv=abs(ma['volume_mm3']-mb['volume_mm3']);dc=(App.Vector(*ma['center_mm'])-App.Vector(*mb['center_mm'])).Length
        passed=abs(missing)<1e-5 and abs(added)<1e-5 and not fuzzy_missing and not fuzzy_added and ta<=1e-4 and tb<=max(1e-7,ta)+1e-10 and dv<=(one.Area+two.Area)/2*(ta+tb) and dc<max(1e-6,ta+tb)
        checks.append(dict(scope=label,passed=passed,missing_mm3=missing,added_mm3=added,
            fuzzy_missing_faces=fuzzy_missing,fuzzy_added_faces=fuzzy_added,mass_difference_mm3=dv,
            centroid_difference_mm=dc,native_max_tolerance_mm=ta,step_max_tolerance_mm=tb,step_sha256=sha(path)))
        write(out/'exchange_progress.json',dict(checks=checks));print(label,passed,flush=True)
    write(out/'exchange_checks.json',dict(passed=all(x['passed'] for x in checks),native_sha256=sha(native),checker_sha256=sha(Path(__file__)),checks=checks))
    assert all(x['passed'] for x in checks)
finally:
    runtime.close()
