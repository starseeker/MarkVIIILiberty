"""Compare saved nominal/varied rear joints; source linings and inherited material stay fixed."""
import argparse,math,sys
from pathlib import Path
import FreeCAD as App
import Part
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H.parents[1]))
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--parameter',type=Path,required=True)
a=p.parse_args();paths=[a.candidate.resolve(),a.parameter.resolve()];reports=[];manifests=[]
for path in paths:
 r=read(path/'report.json');m=read(path/'isolated/manifest.json');q=read(path/'independent_checks.json')
 assert q['passed'] and sha(path/r['native_file'])==r['native_sha256']==m['native_sha256']==q['native_sha256']
 reports.append(r);manifests.append(m)
r,pr=reports;m,pm=manifests;checks=[]
def ck(name,passed,**detail):checks.append(dict(name=name,passed=bool(passed),**detail))
def shape(manifest,key):
 d=manifest['definitions'][key];assert sha(d['brep_path'])==d['brep_sha256'];s=Part.Shape();s.read(d['brep_path']);return s
changed=[k for k in m['definitions'] if m['definitions'][k]['brep_sha256']!=pm['definitions'][k]['brep_sha256']]
ck('Only intended control changes',pr['controls']==dict(r['controls'],anchor_outer_stock=r['controls']['anchor_outer_stock']+1) and r['band_controls']==pr['band_controls'])
ck('All 504 inherited BReps identical',all(k.startswith('Def_HighBrake_') for k in changed))
for role in ['long_band','short_band','long_lining','short_lining']:
 key='Def_HighBrake_'+role;one=shape(m,key);two=shape(pm,key);differences=[one.cut(two),two.cut(one)]
 ck(role+' material unchanged',all(d.isValid() and not d.Faces and abs(d.Volume)<1e-5 for d in differences))
for role,kind in [('anchor_end','outer_radius'),('anchor_rivet','shank_end'),('coupling_screw','shank_length')]:
 values=[]
 for manifest in manifests:
  s=shape(manifest,'Def_HighBrake_'+role);faces=[f for f in s.Faces if isinstance(f.Surface,Part.Cylinder)]
  if kind=='outer_radius':value=max(f.Surface.Radius for f in faces)
  else:
   f=next(f for f in faces if abs(f.Surface.Radius-(7.9375/2 if role=='anchor_rivet' else 9.525/2))<1e-7);b=f.optimalBoundingBox(False,False);value=b.ZMax if kind=='shank_end' else b.ZLength
  values.append(value)
 ck(role+' actual '+kind+' follows one millimeter increase',abs(values[1]-values[0]-1)<1e-5,values_mm=values)
rows,prows=[{v['name']:v for v in data['occurrences']} for data in manifests]
moved=[]
for name,row in rows.items():
 other=prows[name]
 if max(abs(x-y) for x,y in zip(row['frame'],other['frame']))>1e-7:moved.append(name)
ck('Only twelve coupling screws move',set(moved)=={hand+'HighSpeedBrakeCouplingScrew'+str(n) for hand in ['Port','Starboard'] for n in range(1,7)})
ck('Each moved head follows its radial stock by one millimeter',all(abs(math.dist([rows[n]['frame'][i] for i in [3,7,11]],[prows[n]['frame'][i] for i in [3,7,11]])-1)<1e-6 for n in moved))
ck('All occurrence identities and owners preserved',rows.keys()==prows.keys() and all(v['definition']==prows[n]['definition'] and v['owners']==prows[n]['owners'] for n,v in rows.items()))
result=dict(passed=all(v['passed'] for v in checks),native_sha256=r['native_sha256'],parameter_native_sha256=pr['native_sha256'],checker_sha256=sha(Path(__file__)),checks=checks,changed_brep_definitions=changed,moved_occurrences=moved,nominal_controls=r['controls'],varied_controls=pr['controls'],scope='Engineering sensitivity, not a historical confidence interval; both candidates must pass independent local checks.')
write(paths[0]/'variation_checks.json',result);print(result,flush=True);assert result['passed']
