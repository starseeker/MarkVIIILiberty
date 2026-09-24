import json
from pathlib import Path
import FreeCAD as App
import Part
p=Path('/home/cyapp/MarkVIIILiberty/.work/high-brake-joint/short_cut_probe')
a=Part.Shape();a.read(str(p/'rotated_compound.brep'));b=Part.Shape();b.read(str(p/'sector_direct.brep'))
checks=[]
for name,one,two in [('rotated_minus_direct',a,b),('direct_minus_rotated',b,a)]:
 d=one.cut(two);checks.append(dict(name=name,valid=d.isValid(),faces=len(d.Faces),volume_mm3=d.Volume,passed=d.isValid() and not d.Faces and abs(d.Volume)<1e-5))
r=dict(passed=all(v['passed'] for v in checks),checks=checks,scope='Two rotational parameterizations of the same six countersinks; comparison without fuzzy tolerance.')
(p/'comparison.json').write_text(json.dumps(r,indent=2)+'\n');print(r,flush=True);assert r['passed']
