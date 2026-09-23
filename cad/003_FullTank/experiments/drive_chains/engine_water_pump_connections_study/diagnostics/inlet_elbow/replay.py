"""Replay same-geometry inlet elbow construction and definition STEP behavior."""
from pathlib import Path
import json,sys,hashlib
import FreeCAD as App
import Part
base=Path(__file__).resolve().parent;paths=[Path(p) for p in sys.argv[1:]] or [base/'swept_cover.brep',base/'torus_cover.brep'];results=[];shapes=[]
assert len(paths)==2
Part.setStaticValue('write.surfacecurve.mode',1)
for label,filename in zip(['swept','torus'],paths):
 s=Part.Shape();s.read(str(filename));shapes.append(s);file=Path.cwd()/(label+'.step');s.exportStep(str(file));step=Part.Shape();step.read(str(file));minus,plus=s.cut(step),step.cut(s)
 result=dict(label=label,native_sha256=hashlib.sha256(filename.read_bytes()).hexdigest(),native_valid=s.isValid(),step_valid=step.isValid(),native_tolerance=s.getTolerance(1),step_tolerance=step.getTolerance(1),missing_mm3=minus.Volume,added_mm3=plus.Volume,missing_faces=len(minus.Faces),added_faces=len(plus.Faces),passed=not minus.Faces and not plus.Faces and abs(minus.Volume)<1e-5 and abs(plus.Volume)<1e-5)
 print(result,flush=True);results.append(result)
minus,plus=shapes[0].cut(shapes[1]),shapes[1].cut(shapes[0]);same=not minus.Faces and not plus.Faces
r=dict(passed=not results[0]['passed'] and results[1]['passed'] and same,results=results,native_material_identical=same,native_missing_mm3=minus.Volume,native_added_mm3=plus.Volume,freecad=App.Version(),occ=Part.OCC_VERSION)
Path('replay_checks.json').write_text(json.dumps(r,indent=2)+'\n');assert r['passed']
