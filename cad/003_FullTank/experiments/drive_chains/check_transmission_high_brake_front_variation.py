"""Measure saved forward-fitting stock sensitivity with fixed source fasteners."""
import argparse,sys
from pathlib import Path
import FreeCAD as App
import Part
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H.parents[1]))
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--parameter',type=Path,required=True);a=p.parse_args()
paths=[a.candidate.resolve(),a.parameter.resolve()];reports=[];manifests=[]
for path in paths:
 r=read(path/'report.json');m=read(path/'isolated/manifest.json')
 assert sha(path/r['native_file'])==r['native_sha256']==m['native_sha256']
 for file in ['independent_checks.json','material_checks.json']:
  q=read(path/file);assert q['passed'] and q['native_sha256']==r['native_sha256']
 reports.append(r);manifests.append(m)
r,pr=reports;m,pm=manifests;checks=[]
def ck(name,passed,**detail):checks.append(dict(name=name,passed=bool(passed),**detail))
def shape(manifest,key):
 d=manifest['definitions'][key];assert sha(d['brep_path'])==d['brep_sha256'];s=Part.Shape();s.read(d['brep_path']);return s
changed=[k for k in m['definitions'] if m['definitions'][k]['brep_sha256']!=pm['definitions'][k]['brep_sha256']]
ck('Only estimated fitting stock increases one millimeter',pr['controls']==dict(r['controls'],foot_stock=r['controls']['foot_stock']+1) and r['band_controls']==pr['band_controls'])
affected={'Def_HighBrakeFront_'+v for v in ['long_end','short_end','steel_rivet','lining_front_1']}
for key in sorted(set(m['definitions'])-affected):
 if key not in changed:continue
 one,two=shape(m,key),shape(pm,key);delta=[one.cut(two),two.cut(one)]
 ck(key+' normalization preserves material',all(v.isValid() and not v.Faces and abs(v.Volume)<1e-5 for v in delta))
ck('All definition metadata unchanged',m['definitions'].keys()==pm['definitions'].keys() and all(d['properties']==pm['definitions'][k]['properties'] for k,d in m['definitions'].items()))
for role in ['long_end','short_end','steel_rivet','lining_front_1']:
 values=[]
 for manifest in manifests:
  s=shape(manifest,'Def_HighBrakeFront_'+role);fs=[f for f in s.Faces if isinstance(f.Surface,Part.Cylinder)]
  if role.endswith('_end'):value=max(f.Surface.Radius for f in fs)
  else:
   radius=7.9375/2 if role=='steel_rivet' else 6.35/2;f=next(f for f in fs if abs(f.Surface.Radius-radius)<1e-7);value=f.optimalBoundingBox(False,False).ZMax
  values.append(value)
 ck(role+' actual outer radius or shank seat follows stock',abs(values[1]-values[0]-1)<1e-5,values_mm=values)
rows,prows=[{v['name']:v for v in data['occurrences']} for data in manifests]
ck('Every occurrence identity owner and frame unchanged',rows.keys()==prows.keys() and all(v['definition']==prows[n]['definition'] and v['owners']==prows[n]['owners'] and max(abs(x-y) for x,y in zip(v['frame'],prows[n]['frame']))<1e-7 for n,v in rows.items()))
result=dict(passed=all(v['passed'] for v in checks),native_sha256=r['native_sha256'],parameter_native_sha256=pr['native_sha256'],checker_sha256=sha(Path(__file__)),checks=checks,changed_brep_definitions=changed,scope='One millimeter estimated forward fitting-stock sensitivity. Source lining and rivet stock are fixed; both candidates pass independent stock, seat, support and interference checks.')
write(paths[0]/'variation_checks.json',result);assert result['passed'],[v for v in checks if not v['passed']]
