"""Compare saved support definitions and installed STEP solids in both material directions."""
import argparse
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,default=HERE/'clutch_support_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.candidate.resolve()
if not a.worker:
    with (out/'exchange_check.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(out),'--worker'],env=runtime.environment(out/'exchange_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part
    from lib.cad_build import leaves
    from case_joint_mass import calculator
    native=out/'TransmissionWithClutchSupports.FCStd';nh=sha(native);r=read(out/'report.json');assert r['native_sha256']==nh
    doc=App.openDocument(str(native));byid={i['id']:i for i in leaves(doc.Root)}
    mass=calculator(out/'exchange_runtime/mass');exchange=[]
    for label,expected in [('Definitions',[(k,doc.getObject(k).Shape) for k in read(out/'definition_order.json')]),
                           ('Installation',[(n,byid[n]['shape']) for n in r['exchange_ids']])]:
        path=out/('ClutchSupport'+label+'.step');loaded=Part.Shape();loaded.read(str(path))
        assert loaded.isValid() and len(loaded.Solids)==len(expected)
        remaining=[(s,s.CenterOfMass,s.Volume) for s in loaded.Solids]
        for key,shape in expected:
            one=shape.Solids[0];center=one.CenterOfMass;vol=one.Volume;area=one.Area
            idx=min(range(len(remaining)),key=lambda j:(center-remaining[j][1]).Length+abs(vol-remaining[j][2])/max(area,1));two=remaining.pop(idx)[0]
            ma=mass(one,label+'_'+key+'_native');mb=mass(two,label+'_'+key+'_step')
            ta=one.getTolerance(1);tb=two.getTolerance(1);fuzzy=min(.0001,max(1e-7,ta+tb))
            missing=one.cut(two).Volume;added=two.cut(one).Volume;dv=abs(ma['volume_mm3']-mb['volume_mm3']);dc=(App.Vector(*ma['center_mm'])-App.Vector(*mb['center_mm'])).Length
            passed=abs(missing)<1e-5 and abs(added)<1e-5 and not one.cut(two,fuzzy).Faces and not two.cut(one,fuzzy).Faces and ta<=1e-4 and tb<=max(1e-7,ta)+1e-10 and dv<=(one.Area+two.Area)/2*(ta+tb) and dc<max(1e-6,ta+tb)
            exchange.append(dict(scope=label,part=key,passed=passed,missing_mm3=missing,added_mm3=added,mass_difference_mm3=dv,centroid_difference_mm=dc))
            print(label,key,passed,flush=True)
            write(out/'exchange_progress.json',dict(checks=exchange))
    write(out/'exchange_checks.json',dict(passed=all(x['passed'] for x in exchange),native_sha256=nh,checker_sha256=sha(Path(__file__)),
        artifact_hashes={n:sha(out/n) for n in ['ClutchSupportDefinitions.step','ClutchSupportInstallation.step']},checks=exchange))
    assert all(x['passed'] for x in exchange)
finally:
    runtime.close()
