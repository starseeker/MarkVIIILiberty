"""Qualify the final support combination independently of its three builders."""
import argparse,itertools,math,shutil,sys,tempfile
from pathlib import Path
H=Path(__file__).resolve().parent;STAGE=H.parents[1];ROOT=STAGE.parents[1];sys.path.insert(0,str(STAGE))
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['evidence','native','material','exchange']);p.add_argument('--contract',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
contract=read(a.contract);candidate=ROOT/contract['candidate'];r=read(candidate/'report.json');m=read(candidate/'isolated/manifest.json');native=candidate/r['native_file'];assert sha(native)==r['native_sha256']==contract['native_sha256']==m['native_sha256']
assert all(sha(ROOT/f)==v for f,v in contract['input_hashes'].items())
checks=[]
def ck(name,passed,**kw):checks.append(dict(name=name,passed=bool(passed),**kw))
def receipt(name,**kw):
 record=dict(passed=all(v['passed'] for v in checks),checks=checks,native_sha256=sha(native),contract_sha256=sha(a.contract),checker_sha256=sha(Path(__file__)),historical_geometry_qualified=False,installation_qualified=False,**kw);write(out/name,record);assert record['passed'];print(a.mode,len(checks),'checks passed',flush=True)
rows={v['name']:v for v in m['occurrences']};affected=contract['affected_occurrences'];definition_names=contract['affected_definitions']
if a.mode=='evidence':
 prior=read(ROOT/contract['baseline_manifest']);before={v['name']:v for v in prior['occurrences']};ck('Exact packet occurrence and definition scope',set(rows)-set(before)==set(affected)-{'CenterTransmissionCore_bevel_case'} and set(m['definitions'])-set(prior['definitions'])==set(definition_names)-{'Def_TransmissionCore_bevel_case'} and len(affected)==45 and len(definition_names)==14)
 ck('Final counts and unchanged baseline occurrence frames',len(rows)==3165 and len(m['definitions'])==542 and len(m['assemblies'])==336 and all(rows[n]['definition']==v['definition'] and rows[n]['owners']==v['owners'] and max(abs(x-y) for x,y in zip(rows[n]['frame'],v['frame']))<1e-7 for n,v in before.items()))
 for item in contract['successful_receipts']:
  data=read(ROOT/item['path']);ck(item['path'],data[item.get('flag','passed')] is True and all(data.get(k)==v for k,v in item.get('bindings',{}).items()))
 # Each inherited definition must be covered by every intervening preservation
 # receipt, except the one case explicitly revised in this packet.
 for name in set(prior['definitions'])-{'Def_TransmissionCore_bevel_case'}:
  chain=[]
  for folder in contract['increments']:
   data=read(ROOT/folder/'definition_preservation_checks.json');found=[v for v in data['checks'] if v['definition']==name];chain.append(len(found)==1 and found[0]['passed'])
  ck(name+' has complete inherited preservation chain',all(chain))
 ck('Unchanged source registration',sha(ROOT/contract['source_registration'])==contract['source_registration_sha256'])
 receipt('evidence_checks.json',scope='Hash-bound source/receipt chain and exact packet delta from the qualified operating-mechanism parent. Reuses completed scoped geometry checks; does not replace final combined native/material/STEP checks.')
 sys.exit(0)
import FreeCAD as App
import Part
import numpy as np
from lib.camera_review import validate_native_bindings
cache={}
def definition(key):
 if key not in cache:
  d=m['definitions'][key];assert sha(d['brep_path'])==d['brep_sha256'];s=Part.Shape();s.read(d['brep_path']);assert s.Placement.isIdentity();cache[key]=s
 return cache[key].copy()
def world(name):
 row=rows[name];s=definition(row['definition']);s.Placement=App.Placement(App.Matrix(*row['frame']));return s
if a.mode=='native':
 with tempfile.TemporaryDirectory(prefix='relocated_support_',dir=out) as temporary:
  relocated=Path(temporary)/native.name;shutil.copy2(native,relocated);assert sha(relocated)==sha(native)
  validate_native_bindings(dict(native_file=str(relocated),render_occurrences=list(rows),landmarks=[]),m)
  doc=App.openDocument(str(relocated))
  try:
   ck('All3165 saved physical links remain local and unscaled after relocation',all(doc.getObject(row['object']).LinkedObject.Document==doc and doc.getObject(row['object']).Scale==1 and tuple(doc.getObject(row['object']).ScaleVector)==(1.,1.,1.) for row in rows.values()))
   for key in definition_names:
    body=doc.getObject(key);s=body.Shape.copy();reference=definition(key);ta=s.getTolerance(1);missing,added=s.cut(reference),reference.cut(s)
    ck(key+' relocated closed material',body.Placement.isIdentity() and s.Placement.isIdentity() and s.isValid() and len(s.Solids)==1 and s.Solids[0].isClosed() and ta<=1e-4 and not missing.Faces and not added.Faces,tolerance_mm=ta)
  finally:App.closeDocument(doc.Name)
 receipt('native_checks.json',scope='Relocated native file, every installed link/definition binding and frame, and closed material for all14 affected definitions. Temporary copied native was removed after successful close.')
elif a.mode=='material':
 validate_native_bindings(dict(native_file=str(native),render_occurrences=affected,landmarks=[]),m)
 boxes={};bounds={}
 for key in m['definitions']:
  s=definition(key);b=s.BoundBox;bounds[key]=np.array(list(itertools.product([b.XMin,b.XMax],[b.YMin,b.YMax],[b.ZMin,b.ZMax])))
  if key not in definition_names:cache.pop(key,None)
 for name,row in rows.items():
  f=np.array(row['frame']).reshape(4,4);pts=bounds[row['definition']]@f[:3,:3].T+f[:3,3];boxes[name]=(pts.min(axis=0),pts.max(axis=0))
 seen=set();pairs=[]
 for name in affected:
  one=world(name);low,high=boxes[name]
  for other,(lo,hi) in boxes.items():
   pair=tuple(sorted([name,other]))
   if other==name or pair in seen or not (np.all(lo<=high+1e-7) and np.all(hi>=low-1e-7)):continue
   seen.add(pair);common=one.common(world(other));valid=common.isNull() or common.isValid();volume=sum(abs(s.Volume) for s in common.Solids);pairs.append(dict(first=name,second=other,valid_common=valid,common_mm3=volume,passed=valid and volume<1e-5))
  write(out/'material_progress.json',pairs)
 ck('All combined support and retained powertrain material pairs',all(v['passed'] for v in pairs),pairs=len(pairs),failed=[v for v in pairs if not v['passed']])
 receipt('material_checks.json',pairs=pairs,affected_count=45,scope='All45 final affected occurrences against all current powertrain material, with conservative box filtering and unique full-solid pairs; includes contacts between separate construction increments.')
elif a.mode=='exchange':
 import Import
 from lib.mass_properties import AdaptiveMass
 from lib.refined_kronrod_mass import RefinedKronrodMass
 from lib.step_matching import StepSolidMatcher
 validate_native_bindings(dict(native_file=str(native),render_occurrences=affected,landmarks=[]),m)
 mass=AdaptiveMass(out/'adaptive_mass_runtime');refined=RefinedKronrodMass(out/'refined_mass_runtime');Part.setStaticValue('write.surfacecurve.mode',1);files={}
 for scope,shapes in [('Definitions',{k:definition(k) for k in definition_names}),('Installed',{n:world(n) for n in affected})]:
  path=out/('HighBrakeSupports'+scope+'.step');assert not path.exists();doc=App.newDocument('SupportExchange'+scope)
  try:
   features=[]
   for name,s in shapes.items():
    f=doc.addObject('PartDesign::Feature',name);f.Shape=s;features.append(f)
   doc.recompute();Import.export(features,str(path))
  finally:App.closeDocument(doc.Name)
  text=path.read_text();assert text.count('NEXT_ASSEMBLY_USAGE_OCCURRENCE')==len(shapes) and 'PCURVE(' in text
  step=Part.Shape();step.read(str(path));assert step.isValid() and len(step.Solids)==len(shapes);matcher=StepSolidMatcher(step.Solids)
  for name,one in shapes.items():
   i,two=matcher.pop(one);ta,tb=one.getTolerance(1),two.getTolerance(1);missing,added=one.cut(two),two.cut(one);fuzzy=min(1e-4,max(1e-7,ta+tb));fm,fa=len(one.cut(two,fuzzy).Faces),len(two.cut(one,fuzzy).Faces)
   baseline_a,baseline_b=mass.measure(one),mass.measure(two);ma,mb=(refined.measure(one),refined.measure(two)) if name in ['Def_TransmissionCore_bevel_case','CenterTransmissionCore_bevel_case'] else (baseline_a,baseline_b);dc=math.dist(ma['centroid_mm'],mb['centroid_mm'])
   passed=one.isValid() and two.isValid() and len(one.Solids)==len(two.Solids)==1 and abs(missing.Volume)<1e-5 and abs(added.Volume)<1e-5 and not fm and not fa and ta<=1e-4 and tb<=max(ta,1e-7)+1e-10 and ma['converged'] and mb['converged'] and dc<1e-5
   ck(scope+'/'+name,passed,imported_solid_index=i,native_tolerance_mm=ta,step_tolerance_mm=tb,missing_mm3=missing.Volume,added_mm3=added.Volume,fuzzy_missing_faces=fm,fuzzy_added_faces=fa,native_mass=ma,step_mass=mb,baseline_native_mass=baseline_a,baseline_step_mass=baseline_b,centroid_error_mm=dc)
   write(out/'exchange_progress.json',checks);print(scope,name,passed,flush=True)
  assert not len(matcher);files[path.name]=sha(path)
 receipt('exchange_checks.json',step_hashes=files,mass_provenance=mass.provenance,refined_mass_provenance=refined.provenance,export_settings={'write.surfacecurve.mode':1,'writer':'Import.export per named feature'},scope='Combined final14 support definitions and45 installed occurrences; strict material/tolerance/converged-mass comparisons. Entire powertrain STEP and standard assembly are separate scopes.')
