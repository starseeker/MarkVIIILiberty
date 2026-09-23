"""Reproduce the housing tolerance comparison using only adjacent saved artifacts."""
import json
from pathlib import Path
import FreeCAD as App
import Part

HERE=Path(__file__).resolve().parent
def read(name):
    shape=Part.Shape();shape.read(str(HERE/name));return shape
rows=[]
for key in ['housing_flywheel','housing_distributor']:
    original=read('rejected_'+key+'_native.brep')
    old_step=read('rejected_'+key+'_step.brep')
    revised=read('arc_prism_'+key+'.brep')
    step=read('arc_prism_'+key+'.step')
    ta,tb=original.getTolerance(1),old_step.getTolerance(1)
    tc,td=revised.getTolerance(1),step.getTolerance(1)
    fuzzy=min(1e-4,max(1e-7,tc+td))
    result=dict(part=key,rejected_native_tolerance_mm=ta,rejected_step_tolerance_mm=tb,
        revised_native_tolerance_mm=tc,revised_step_tolerance_mm=td,
        native_missing_mm3=original.cut(revised).Volume,native_added_mm3=revised.cut(original).Volume,
        missing_step_faces=len(revised.cut(step,fuzzy).Faces),added_step_faces=len(step.cut(revised,fuzzy).Faces))
    assert tb>max(1e-7,ta)+1e-10
    assert td<=max(1e-7,tc)+1e-10
    assert max(abs(result[n]) for n in ['native_missing_mm3','native_added_mm3'])<1e-5
    assert not result['missing_step_faces'] and not result['added_step_faces']
    rows.append(result)
print(json.dumps(dict(passed=True,checks=rows),indent=2))
