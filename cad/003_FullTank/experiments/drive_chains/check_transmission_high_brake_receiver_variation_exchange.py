"""Qualify the receiver stock variation with the independently tested refined mass adapter."""
import argparse,math,sys
from pathlib import Path
H=Path(__file__).resolve().parent;STAGE=H.parents[1];ROOT=STAGE.parents[1];sys.path[:0]=[str(H),str(STAGE)]
from lib.evidence import read,write,sha
import FreeCAD as App
import Part
import Import
from lib.mass_properties import AdaptiveMass
from lib.step_matching import StepSolidMatcher

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True)
p.add_argument('--output',type=Path);p.add_argument('--refined-case-mass',action='store_true');a=p.parse_args()
out=a.candidate.resolve();r=read(out/'report.json');native=out/'ReceivingWebStudy.FCStd'
assert r['passed'] and sha(native)==r['prototype_native_sha256']
eout=a.output.resolve() if a.output else out
if eout!=out:assert not eout.exists();eout.mkdir(parents=True)
assert not (eout/'exchange_checks.json').exists()
mass=AdaptiveMass(eout/'adaptive_mass_runtime');Part.setStaticValue('write.surfacecurve.mode',1)
refined=None
if a.refined_case_mass:
 from lib.refined_kronrod_mass import RefinedKronrodMass
 failed=read(out/'exchange_checks.json');control_path=H/'transmission_high_brake_support_study/receivers04/diagnostics/refined_mass_controls/qualification.json';control=read(control_path)
 assert failed['native_sha256']==sha(native) and not failed['passed'] and control['passed']
 assert control['provenance']['adapter_sha256']==sha(STAGE/'lib/refined_kronrod_mass.py')
 refined=RefinedKronrodMass(eout/'refined_mass_runtime')
parent=H/'transmission_high_brake_mechanism_study/trial01';m=read(parent/'isolated/manifest.json')
source_row=next(v for v in m['occurrences'] if v['name']=='CenterTransmissionCore_bevel_case')
base=App.Placement(App.Matrix(*source_row['frame']));c=r['controls'];V=App.Vector
doc=App.openDocument(str(native));definitions={};installed={};native_checks=[]
try:
 assert doc.Root.Placement.isIdentity()
 for role in ['case','anchor_bracket','anchor_lock_plate','mount_screw']:
  body=doc.getObject('Def_'+role);s=body.Shape.copy();assert body.Placement.isIdentity() and s.Placement.isIdentity()
  reference=Part.Shape();reference.read(str(out/(role+'.brep')))
  missing,added=s.cut(reference),reference.cut(s)
  passed=s.isValid() and len(s.Solids)==1 and not missing.Faces and not added.Faces
  native_checks.append(dict(name=role,passed=passed));assert passed
  definitions[role]=s
 for link in doc.Root.Group:
  assert link.TypeId=='App::Link' and link.Scale==1 and tuple(link.ScaleVector)==(1.,1.,1.)
  pose=doc.Root.getGlobalPlacement().multiply(link.LinkPlacement)
  if link.Name=='Case':expected=base
  else:
   sign=1 if link.Name.startswith('Port') else -1
   expected=base.multiply(App.Placement(V(0,sign*c['brake_station'],0),App.Rotation()))
   if 'MountScrew' in link.Name:
    i=int(link.Name[-1])-1;local=App.Placement(App.Matrix(*r['details']['mounts']['bottom']['bolt_seat_frames'][i]))
    local.Base+=local.Rotation.multVec(V(0,0,c['bracket_stock']+c['lock_plate_stock']));expected=expected.multiply(local)
  error=max(abs(x-y) for x,y in zip(pose.toMatrix().A,expected.toMatrix().A))
  native_checks.append(dict(name=link.Name+' composed frame',passed=error<1e-7,max_error=error));assert error<1e-7
  s=link.LinkedObject.Shape.copy();s.Placement=pose;installed[link.Name]=s
finally:App.closeDocument(doc.Name)
assert len(definitions)==4 and len(installed)==9
checks=[];files={}
for scope,shapes in [('Definitions',definitions),('Installed',installed)]:
 path=eout/('ReceivingWeb'+scope+'.step');assert not path.exists()
 doc=App.newDocument('ReceiverExchange'+scope)
 try:
  features=[]
  for name,s in shapes.items():
   f=doc.addObject('PartDesign::Feature',name);f.Shape=s;features.append(f)
  doc.recompute();Import.export(features,str(path))
 finally:App.closeDocument(doc.Name)
 txt=path.read_text();assert txt.count('NEXT_ASSEMBLY_USAGE_OCCURRENCE')==len(shapes) and 'PCURVE(' in txt
 step=Part.Shape();step.read(str(path));assert step.isValid() and len(step.Solids)==len(shapes)
 matcher=StepSolidMatcher(step.Solids)
 for name,one in shapes.items():
  i,two=matcher.pop(one);ta,tb=one.getTolerance(1),two.getTolerance(1)
  missing,added=one.cut(two),two.cut(one);fuzzy=min(1e-4,max(1e-7,ta+tb))
  fm,fa=len(one.cut(two,fuzzy).Faces),len(two.cut(one,fuzzy).Faces)
  ma,mb=mass.measure(one),mass.measure(two);initial=None
  if name.lower()=='case' and refined is not None and not (ma['converged'] and mb['converged']):
   initial=dict(native=ma,step=mb);ma,mb=refined.measure(one),refined.measure(two)
  dc=math.dist(ma['centroid_mm'],mb['centroid_mm'])
  passed=one.isValid() and two.isValid() and len(one.Solids)==len(two.Solids)==1 and abs(missing.Volume)<1e-5 and abs(added.Volume)<1e-5 and not fm and not fa and ta<=1e-4 and tb<=max(ta,1e-7)+1e-10 and ma['converged'] and mb['converged'] and dc<1e-5
  row=dict(scope=scope,name=name,passed=passed,imported_solid_index=i,native_tolerance_mm=ta,step_tolerance_mm=tb,
   missing_mm3=missing.Volume,added_mm3=added.Volume,fuzzy_missing_faces=fm,fuzzy_added_faces=fa,
   native_mass=ma,step_mass=mb,initial_whole_mass=initial,centroid_error_mm=dc)
  checks.append(row);write(eout/'exchange_progress.json',checks);print(scope,name,passed,flush=True)
 assert not len(matcher);files[path.name]=sha(path)
write(eout/'exchange_checks.json',dict(passed=all(v['passed'] for v in checks),checks=checks,native_checks=native_checks,
 native_sha256=sha(native),checker_sha256=sha(Path(__file__)),mass_provenance=mass.provenance,step_hashes=files,
 refined_mass_provenance=refined.provenance if refined else None,refined_controls_sha256=sha(control_path) if refined else None,
 scope='Four saved prototype definitions and nine installed components; unchanged strict STEP criteria. Whole-parent preservation, variation, source review and integration remain separate.',
 export_settings={'write.surfacecurve.mode':1,'writer':'Import.export per named feature'},historical_geometry_qualified=False,installation_qualified=False))
assert all(v['passed'] for v in checks),'Retain failed exchange evidence and diagnose without loosening acceptance.'
