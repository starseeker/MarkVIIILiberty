"""Strict per-definition and installed STEP comparison for the saved shared-pin family and retained low-speed receivers."""
import argparse
import math
from pathlib import Path
import sys
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H.parents[1]))
import FreeCAD as App
import Part,Import
from lib.evidence import read,write,sha
from lib.mass_properties import AdaptiveMass
from lib.kronrod_mass import KronrodMass
from lib.step_matching import StepSolidMatcher
from lib.camera_review import validate_native_bindings

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve()
r=read(out/'report.json');m=read(out/'isolated/manifest.json');native=out/r['native_file'];assert sha(native)==m['native_sha256'];assert not (out/'exchange_checks.json').exists()
assert read(out/'independent_checks.json')['passed']
validate_native_bindings(dict(native_file=str(native),render_occurrences=[v['name'] for v in m['occurrences']],landmarks=[]),m)
Part.setStaticValue('write.surfacecurve.mode',1);App.ParamGet('User parameter:BaseApp/Preferences/Mod/Import').SetBool('ExportKeepPlacement',True)
analytic=AdaptiveMass(out/'adaptive_mass_runtime');curved=KronrodMass(out/'kronrod_mass_runtime');definitions={};installed={}
for key,d in m['definitions'].items():
    assert sha(d['brep_path'])==d['brep_sha256'];s=Part.Shape();s.read(d['brep_path']);definitions[key]=s
for row in m['occurrences']:
    s=definitions[row['definition']].copy();s.Placement=App.Placement(App.Matrix(*row['frame']));installed[row['name']]=s
checks=[];files={}
for scope,shapes in [('Definitions',definitions),('Installed',installed)]:
    path=out/('ControlPinFamily'+scope+'.step');assert not path.exists();doc=App.newDocument('PinFamilyExchange'+scope)
    try:
        objects=[]
        for name,s in shapes.items():
            obj=doc.addObject('PartDesign::Feature',name);obj.Shape=s;objects.append(obj)
        doc.recompute();Import.export(objects,str(path))
    finally:App.closeDocument(doc.Name)
    text=path.read_text();assert 'PCURVE(' in text and text.count('NEXT_ASSEMBLY_USAGE_OCCURRENCE')==len(shapes)
    recovered=Part.Shape();recovered.read(str(path));assert recovered.isValid() and len(recovered.Solids)==len(shapes);matcher=StepSolidMatcher(recovered.Solids)
    for name,one in shapes.items():
        index,two=matcher.pop(one);ta,tb=one.getTolerance(1),two.getTolerance(1);fuzz=min(1e-4,max(1e-7,ta+tb))
        missing,added=one.cut(two),two.cut(one);fm,fa=len(one.cut(two,fuzz).Faces),len(two.cut(one,fuzz).Faces)
        mass=curved if ('HighSpeedBrakeLever' in name or 'HighBrakeMechanism_lever' in name) or any(isinstance(f.Surface,Part.SurfaceOfExtrusion) or 'BSpline' in type(f.Surface).__name__ for f in one.Faces) else analytic
        ma,mb=mass.measure(one),mass.measure(two);distance=math.dist(ma['centroid_mm'],mb['centroid_mm'])
        passed=one.isValid() and two.isValid() and len(one.Solids)==len(two.Solids)==1 and one.Solids[0].isClosed() and two.isClosed() and abs(missing.Volume)<1e-5 and abs(added.Volume)<1e-5 and not fm and not fa and ta<=1e-4 and tb<=max(ta,1e-7)+1e-10 and ma['converged'] and mb['converged'] and distance<1e-5
        checks.append(dict(scope=scope,name=name,passed=passed,step_solid_index=index,missing_mm3=missing.Volume,added_mm3=added.Volume,fuzzy_missing_faces=fm,fuzzy_added_faces=fa,native_tolerance_mm=ta,step_tolerance_mm=tb,native_mass=ma,step_mass=mb,centroid_error_mm=distance))
        write(out/'exchange_progress.json',checks);print(scope,name,passed,flush=True)
    assert not len(matcher);files[path.name]=sha(path)
write(out/'exchange_checks.json',dict(passed=all(v['passed'] for v in checks),checks=checks,native_sha256=sha(native),checker_sha256=sha(Path(__file__)),mass_provenance=dict(analytic=analytic.provenance,curved=curved.provenance),step_hashes=files,export_settings={'write.surfacecurve.mode':1,'Mod/Import/ExportKeepPlacement':True},historical_geometry_qualified=False,installation_qualified=False))
assert all(v['passed'] for v in checks)
