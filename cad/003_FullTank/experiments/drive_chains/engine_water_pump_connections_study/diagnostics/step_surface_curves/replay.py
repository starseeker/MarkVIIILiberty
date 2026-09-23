"""Compare identical native geometry with and without STEP surface curves."""
from pathlib import Path
import hashlib,json
import FreeCAD as App
import Part
fixture=Path(__file__).resolve().parent/'wire.brep';results=[]
for mode in [0,1]:
 native=Part.Shape();native.read(str(fixture));Part.setStaticValue('write.surfacecurve.mode',mode)
 path=Path.cwd()/('surface_curves_'+str(mode)+'.step');native.exportStep(str(path));step=Part.Shape();step.read(str(path))
 missing,added=native.cut(step),step.cut(native)
 row=dict(mode=mode,native_valid=native.isValid(),step_valid=step.isValid(),native_max_tolerance_mm=native.getTolerance(1),step_max_tolerance_mm=step.getTolerance(1),
  missing_mm3=missing.Volume,added_mm3=added.Volume,missing_faces=len(missing.Faces),added_faces=len(added.Faces),missing_valid=missing.isValid(),added_valid=added.isValid(),
  pcurve_records=path.read_text().count('PCURVE('),step_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
 row['material_comparison_passed']=not missing.Faces and not added.Faces and abs(row['missing_mm3'])<1e-5 and abs(row['added_mm3'])<1e-5
 print(row,flush=True);results.append(row)
 data=dict(native_sha256=hashlib.sha256(fixture.read_bytes()).hexdigest(),freecad=App.Version(),occ=Part.OCC_VERSION,results=results)
 (Path.cwd()/'export_mode_checks.json').write_text(json.dumps(data,indent=2)+'\n')
assert results[0]['native_valid'] and results[0]['step_valid'] and not results[0]['material_comparison_passed']
assert results[0]['pcurve_records']==0 and results[1]['pcurve_records']>0 and results[1]['material_comparison_passed']
