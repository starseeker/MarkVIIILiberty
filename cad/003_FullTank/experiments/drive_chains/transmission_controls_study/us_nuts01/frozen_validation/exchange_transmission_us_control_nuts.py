"""Strict STEP round trips for saved rear-control joint definitions and installed poses."""
import argparse,math,sys
from pathlib import Path
H=Path(__file__).resolve().parent;STAGE=H.parents[1];sys.path.insert(0,str(STAGE))
from lib.evidence import read,write,sha
import FreeCAD as App
import Part
import Import
from lib.mass_properties import AdaptiveMass
from lib.step_matching import StepSolidMatcher
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve();r=read(out/'report.json');native=out/r['native_file']
assert sha(native)==r['native_sha256'];assert not (out/'exchange_checks.json').exists()
q=read(out/'independent_checks.json');assert q['passed'] and q['native_sha256']==sha(native)
Part.setStaticValue('write.surfacecurve.mode',1);mass=AdaptiveMass(out/'adaptive_mass_runtime')
doc=App.openDocument(str(native));definitions={};installed={}
try:
 definitions['us_standard_nut']=doc.getObject('Def_USStdControlNut').Shape.copy()
 m=read(out/'isolated/manifest.json');rows={v['name']:v for v in m['occurrences']}
 for name in r['affected_occurrences']:
  row=rows[name];link=doc.getObject(name);pose=doc.getObject(row['owners'][-1]).getGlobalPlacement().multiply(link.LinkPlacement)
  assert max(abs(x-y) for x,y in zip(pose.toMatrix().A,row['frame']))<1e-7
  s=link.LinkedObject.Shape.copy();s.Placement=pose;installed[name]=s
finally:App.closeDocument(doc.Name)
assert len(definitions)==1 and len(installed)==2
checks=[];files={}
for scope,shapes in [('Definitions',definitions),('Installed',installed)]:
 path=out/('HighSpeedControlJoint'+scope+'.step');assert not path.exists();doc=App.newDocument('ControlJointExchange'+scope)
 try:
  features=[]
  for name,s in shapes.items():
   f=doc.addObject('PartDesign::Feature',name);f.Shape=s;features.append(f)
  doc.recompute();Import.export(features,str(path))
 finally:App.closeDocument(doc.Name)
 txt=path.read_text();assert txt.count('NEXT_ASSEMBLY_USAGE_OCCURRENCE')==(0 if len(shapes)==1 else len(shapes)) and 'PCURVE(' in txt
 step=Part.Shape();step.read(str(path));assert step.isValid() and len(step.Solids)==len(shapes);matcher=StepSolidMatcher(step.Solids)
 for name,one in shapes.items():
  i,two=matcher.pop(one);ta,tb=one.getTolerance(1),two.getTolerance(1);missing,added=one.cut(two),two.cut(one);fuzzy=min(1e-4,max(1e-7,ta+tb));fm,fa=len(one.cut(two,fuzzy).Faces),len(two.cut(one,fuzzy).Faces)
  baseline_a,baseline_b=mass.measure(one),mass.measure(two)
  ma,mb=baseline_a,baseline_b;measurement='Default adaptive mass'
  dc=math.dist(ma['centroid_mm'],mb['centroid_mm'])
  passed=one.isValid() and two.isValid() and len(one.Solids)==len(two.Solids)==1 and abs(missing.Volume)<1e-5 and abs(added.Volume)<1e-5 and not fm and not fa and ta<=1e-4 and tb<=max(ta,1e-7)+1e-10 and ma['converged'] and mb['converged'] and dc<1e-5
  checks.append(dict(scope=scope,name=name,passed=passed,imported_solid_index=i,native_tolerance_mm=ta,step_tolerance_mm=tb,missing_mm3=missing.Volume,added_mm3=added.Volume,fuzzy_missing_faces=fm,fuzzy_added_faces=fa,native_mass=ma,step_mass=mb,centroid_error_mm=dc,measurement=measurement,baseline_native=baseline_a,baseline_step=baseline_b))
  write(out/'exchange_progress.json',checks);print(scope,name,passed,flush=True)
 assert not len(matcher);files[path.name]=sha(path)
write(out/'exchange_checks.json',dict(passed=all(v['passed'] for v in checks),checks=checks,native_sha256=sha(native),checker_sha256=sha(Path(__file__)),independent_checks_sha256=sha(out/'independent_checks.json'),mass_provenance=mass.provenance,step_hashes=files,export_settings={'write.surfacecurve.mode':1,'writer':'Import.export per named feature'},scope='One U.S. nut definition and two installed shapes; full integration and historical qualification remain separate.',installation_qualified=False))
assert all(v['passed'] for v in checks)
