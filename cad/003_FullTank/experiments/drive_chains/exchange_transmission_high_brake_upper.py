"""Strict STEP round trips for saved upper-stop definitions and installed poses."""
import argparse,math,sys
from pathlib import Path
H=Path(__file__).resolve().parent;STAGE=H.parents[1];sys.path.insert(0,str(STAGE))
from lib.evidence import read,write,sha
import FreeCAD as App
import Part
import Import
from lib.mass_properties import AdaptiveMass
from lib.step_matching import StepSolidMatcher
from lib.refined_kronrod_mass import RefinedKronrodMass
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve();r=read(out/'report.json');native=out/r['native_file']
assert r['passed'] and sha(native)==r['prototype_native_sha256'];assert not (out/'exchange_checks.json').exists()
q=read(out/'independent_checks.json');assert q['passed'] and q['native_sha256']==sha(native)
Part.setStaticValue('write.surfacecurve.mode',1);mass=AdaptiveMass(out/'adaptive_mass_runtime');refined=RefinedKronrodMass(out/'refined_mass_runtime')
doc=App.openDocument(str(native));definitions={};installed={}
try:
 for body in doc.Definitions.Group:
  assert body.Placement.isIdentity();s=body.Shape.copy();assert s.Placement.isIdentity();definitions[body.Name.removeprefix('Def_')]=s
 for link in doc.Root.Group:
  pose=doc.Root.getGlobalPlacement().multiply(link.LinkPlacement);assert max(abs(x-y) for x,y in zip(pose.toMatrix().A,r['specs'][link.Name]['frame']))<1e-7
  s=link.LinkedObject.Shape.copy();s.Placement=pose;installed[link.Name]=s
finally:App.closeDocument(doc.Name)
assert len(definitions)==8 and len(installed)==17
checks=[];files={}
for scope,shapes in [('Definitions',definitions),('Installed',installed)]:
 path=out/('HighBrakeUpperStop'+scope+'.step');assert not path.exists();doc=App.newDocument('UpperStopExchange'+scope)
 try:
  features=[]
  for name,s in shapes.items():
   f=doc.addObject('PartDesign::Feature',name);f.Shape=s;features.append(f)
  doc.recompute();Import.export(features,str(path))
 finally:App.closeDocument(doc.Name)
 txt=path.read_text();assert txt.count('NEXT_ASSEMBLY_USAGE_OCCURRENCE')==len(shapes) and 'PCURVE(' in txt
 step=Part.Shape();step.read(str(path));assert step.isValid() and len(step.Solids)==len(shapes);matcher=StepSolidMatcher(step.Solids)
 for name,one in shapes.items():
  i,two=matcher.pop(one);ta,tb=one.getTolerance(1),two.getTolerance(1);missing,added=one.cut(two),two.cut(one);fuzzy=min(1e-4,max(1e-7,ta+tb));fm,fa=len(one.cut(two,fuzzy).Faces),len(two.cut(one,fuzzy).Faces)
  baseline_a,baseline_b=mass.measure(one),mass.measure(two)
  if name in ['case','Case']:
   ma,mb=refined.measure(one),refined.measure(two);measurement='Explicit refined Kronrod for revised receiving case; baseline retained below.'
  else:ma,mb=baseline_a,baseline_b;measurement='Default adaptive mass'
  dc=math.dist(ma['centroid_mm'],mb['centroid_mm'])
  passed=one.isValid() and two.isValid() and len(one.Solids)==len(two.Solids)==1 and abs(missing.Volume)<1e-5 and abs(added.Volume)<1e-5 and not fm and not fa and ta<=1e-4 and tb<=max(ta,1e-7)+1e-10 and ma['converged'] and mb['converged'] and dc<1e-5
  checks.append(dict(scope=scope,name=name,passed=passed,imported_solid_index=i,native_tolerance_mm=ta,step_tolerance_mm=tb,missing_mm3=missing.Volume,added_mm3=added.Volume,fuzzy_missing_faces=fm,fuzzy_added_faces=fa,native_mass=ma,step_mass=mb,centroid_error_mm=dc,measurement=measurement,baseline_native=baseline_a,baseline_step=baseline_b))
  write(out/'exchange_progress.json',checks);print(scope,name,passed,flush=True)
 assert not len(matcher);files[path.name]=sha(path)
write(out/'exchange_checks.json',dict(passed=all(v['passed'] for v in checks),checks=checks,native_sha256=sha(native),checker_sha256=sha(Path(__file__)),independent_checks_sha256=sha(out/'independent_checks.json'),mass_provenance=mass.provenance,refined_mass_provenance=refined.provenance,step_hashes=files,export_settings={'write.surfacecurve.mode':1,'writer':'Import.export per named feature'},scope='Eight prototype definitions and17 installed shapes; full integration and historical qualification remain separate.',installation_qualified=False))
assert all(v['passed'] for v in checks)
