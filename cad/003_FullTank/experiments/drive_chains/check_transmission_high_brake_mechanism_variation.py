"""Check coupled installed spring-height sensitivity without altering printed stock."""
import argparse,sys
from pathlib import Path
import FreeCAD as App
import Part
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H.parents[1]))
from lib.evidence import read,write,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--parameter',type=Path,required=True);a=p.parse_args()
dirs=[a.candidate.resolve(),a.parameter.resolve()];reports=[read(d/'report.json') for d in dirs];manifests=[read(d/'isolated/manifest.json') for d in dirs];checks=[]
def ck(name,passed,**details):checks.append(dict(name=name,passed=bool(passed),**details))
for d,r,m in zip(dirs,reports,manifests):
 q=read(d/'independent_checks.json');assert q['passed'] and sha(d/r['native_file'])==r['native_sha256']==m['native_sha256']==q['native_sha256']
c,v=[r['controls'] for r in reports];delta=v['spring_installed_height']-c['spring_installed_height'];ck('Only estimated installed spring height changed by 1 mm',abs(delta-1)<1e-10 and {k for k in c if c[k]!=v[k]}=={'spring_installed_height'})
ck('Printed joining-rivet stock and both washer bores fixed',all(c[k]==v[k] for k in ['rivet_diameter','rivet_stock_length','washer_a_bore_diameter','washer_b_bore_diameter']))
rows=[{v['name']:v for v in m['occurrences']} for m in manifests];ck('Physical quantities and definition identities retained',rows[0].keys()==rows[1].keys() and manifests[0]['definitions'].keys()==manifests[1]['definitions'].keys())
moving={h+'HighSpeedBrakeUpperSpringWasher' for h in ['Port','Starboard']}
for name,one in rows[0].items():
 two=rows[1][name];assert one['definition']==two['definition'] and one['owners']==two['owners']
 if name not in moving:assert max(abs(x-y) for x,y in zip(one['frame'],two['frame']))<1e-7,name
ck('All other occurrence frames fixed',True)
for name in moving:
 one,two=[App.Placement(App.Matrix(*table[name]['frame'])) for table in rows];axis=one.Rotation.multVec(App.Vector(0,0,1));ck(name+' follows spring end along the screw',((two.Base-one.Base)-axis*delta).Length<1e-7 and one.Rotation.isSame(two.Rotation,1e-9))
changed=[]
for key in reports[0]['new_definitions']:
 parts=[]
 for m in manifests:
  rec=m['definitions'][key];assert sha(rec['brep_path'])==rec['brep_sha256'];s=Part.Shape();s.read(rec['brep_path']);parts.append(s)
 one,two=parts;different=bool(one.cut(two).Faces or two.cut(one).Faces)
 if different:changed.append(key)
ck('Only spring and paired lever seat material changes',set(changed)=={'Def_HighBrakeMechanism_'+role for role in ['spring','lever_left','lever_right']},changed=changed)
result=dict(passed=all(c['passed'] for c in checks),checks=checks,native_sha256=reports[0]['native_sha256'],parameter_native_sha256=reports[1]['native_sha256'],checker_sha256=sha(Path(__file__)),scope='One estimated installed-height variation; both saved candidates independently pass static mechanism checks. Does not qualify operating motion or a general parameter range.')
write(dirs[0]/'variation_checks.json',result);print('Variation checks',len(checks),result['passed'],flush=True);assert result['passed']
