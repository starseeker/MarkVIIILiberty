"""Strict native/STEP comparison of every saved oil-pump part and occurrence."""
import argparse,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.candidate.resolve()
if not a.worker:
    with (out/'exchange_check.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(out),'--worker'],env=runtime.environment(out/'exchange_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part
    from case_joint_mass import calculator
    r=read(out/'report.json');native=out/r['native_file'];assert sha(native)==r['native_sha256'];doc=App.openDocument(str(native));installed=[]
    for row in r['occurrences']:
        link=doc.getObject(row['name']);s=link.LinkedObject.Shape.copy();s.Placement=doc.getObject(row['assembly']).getGlobalPlacement().multiply(link.LinkPlacement).multiply(s.Placement);installed.append((row['name'],s))
    mass=calculator(out/'exchange_runtime/mass');checks=[]
    for scope,filename,expected in [('Definitions','OilPumpDefinitions.step',[(key,doc.getObject('Def_'+key).Shape) for key in r['definition_order']]),('Assembly','OilPumpAssembly.step',installed)]:
        loaded=Part.Shape();loaded.read(str(out/filename));valid=loaded.isValid() and len(loaded.Solids)==len(expected)
        if not valid:
            write(out/'exchange_failure.json',dict(scope=scope,expected=len(expected),actual=len(loaded.Solids),invalid=[i for i,s in enumerate(loaded.Solids) if not s.isValid()]));raise ValueError(scope+' invalid STEP topology or count')
        remaining=list(loaded.Solids)
        for key,s in expected:
            one=s.Solids[0];center=one.CenterOfMass
            idx=min(range(len(remaining)),key=lambda i:(remaining[i].CenterOfMass-center).Length+abs(one.Volume-remaining[i].Volume)/max(one.Area,1));two=remaining.pop(idx)
            ma=mass(one,scope+'_'+key+'_native');mb=mass(two,scope+'_'+key+'_step');ta=one.getTolerance(1);tb=two.getTolerance(1);fuzzy=min(.0001,max(1e-7,ta+tb))
            missing=one.cut(two);extra=two.cut(one);dv=abs(ma['volume_mm3']-mb['volume_mm3']);dc=(App.Vector(*ma['center_mm'])-App.Vector(*mb['center_mm'])).Length
            passed=abs(missing.Volume)<1e-5 and abs(extra.Volume)<1e-5 and not one.cut(two,fuzzy).Faces and not two.cut(one,fuzzy).Faces and ta<=1e-4 and tb<=max(1e-7,ta)+1e-10 and dv<=(one.Area+two.Area)/2*(ta+tb) and dc<max(1e-6,ta+tb)
            checks.append(dict(scope=scope,part=key,passed=passed,missing_mm3=missing.Volume,added_mm3=extra.Volume,mass_difference_mm3=dv,centroid_difference_mm=dc,native_max_tolerance_mm=ta,step_max_tolerance_mm=tb));write(out/'exchange_progress.json',checks);print(scope,key,passed,flush=True)
    result=dict(passed=all(x['passed'] for x in checks),native_sha256=sha(native),checker_sha256=sha(Path(__file__)),checks=checks,step_hashes={n:sha(out/n) for n in ['OilPumpDefinitions.step','OilPumpAssembly.step']});write(out/'exchange_checks.json',result);assert result['passed']
finally:
    runtime.close()
