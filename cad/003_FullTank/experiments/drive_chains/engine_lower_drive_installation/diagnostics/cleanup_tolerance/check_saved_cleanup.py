from pathlib import Path
import json,sys,os
import FreeCAD as App
import Part
h=Path(__file__).resolve().parents[3];sys.path[:0]=[str(h),str(h.parents[1])]
from case_joint_mass import calculator
folder=Path.cwd();artifacts=Path(__file__).resolve().parent
def read(name):
 s=Part.Shape();s.read(str(artifacts/name));return s
before,after,step=(read(n) for n in ['before_cleanup.brep','after_cleanup.brep','before_cleanup.step'])
equivalence=dict(before_valid=before.isValid(),after_valid=after.isValid(),missing_mm3=before.cut(after).Volume,added_mm3=after.cut(before).Volume,before_tolerance_mm=before.getTolerance(1),after_tolerance_mm=after.getTolerance(1))
assert equivalence['before_valid'] and equivalence['after_valid'] and abs(equivalence['missing_mm3'])<1e-5 and abs(equivalence['added_mm3'])<1e-5
os.environ.setdefault('MARKVIII_RESOLVED_FREECAD',str(Path('/snap/freecad/current').resolve()))
mass=calculator(folder/'mass');a=mass(before.Solids[0],'native');b=mass(step.Solids[0],'step')
ta,tb=before.getTolerance(1),step.getTolerance(1);fuzzy=min(.0001,max(1e-7,ta+tb))
missing,added=before.cut(step).Volume,step.cut(before).Volume;dv=abs(a['volume_mm3']-b['volume_mm3']);dc=(App.Vector(*a['center_mm'])-App.Vector(*b['center_mm'])).Length
passed=step.isValid() and len(step.Solids)==1 and abs(missing)<1e-5 and abs(added)<1e-5 and not before.cut(step,fuzzy).Faces and not step.cut(before,fuzzy).Faces and ta<=1e-4 and tb<=max(1e-7,ta)+1e-10 and dv<=(before.Area+step.Area)/2*(ta+tb) and dc<max(1e-6,ta+tb)
r=dict(material_equivalence=equivalence,step_passed=passed,step_tolerance_mm=tb,step_missing_mm3=missing,step_added_mm3=added,step_mass_difference_mm3=dv,step_centroid_difference_mm=dc)
(folder/'cleanup_comparison.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2),flush=True);assert passed
