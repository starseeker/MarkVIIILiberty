"""Independent source-size, relocation, hierarchy, seating and material checks."""
import argparse,itertools,json,shutil,sys,tempfile
from pathlib import Path
H=Path(__file__).resolve().parent;STAGE=H.parents[1];ROOT=STAGE.parents[1];sys.path.insert(0,str(STAGE))
import FreeCAD as App
import Part
import numpy as np
from lib.evidence import read,write,sha
from lib.camera_review import validate_native_bindings
V=App.Vector
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve()
r=read(out/'report.json');m=read(out/'isolated/manifest.json');source=ROOT/r['source_native'];old=read(source.parent/'isolated/manifest.json');native=out/r['native_file']
assert sha(native)==r['native_sha256']==m['native_sha256'] and sha(source)==r['source_native_sha256']==old['native_sha256']
rows,prior=[{v['name']:v for v in data['occurrences']} for data in [m,old]];checks=[]
def ck(name,passed,**kw):checks.append(dict(name=name,passed=bool(passed),**kw))
ck('3173 occurrences,546 definitions,338 groups; one new definition only',len(rows)==3173 and len(m['definitions'])==546 and len(m['assemblies'])==338 and set(rows)==set(prior) and set(m['definitions'])==set(old['definitions'])|{'Def_USStdControlNut'})
ck('Only two nut targets change; every inherited frame and owner remains',all(v['definition']==r['changed_occurrence_definitions'].get(n,prior[n]['definition']) and v['owners']==prior[n]['owners'] and max(abs(x-y) for x,y in zip(v['frame'],prior[n]['frame']))<1e-7 for n,v in rows.items()))
ck('Inherited assembly frames and child ownership retained',all(max(abs(x-y) for x,y in zip(g['world'],m['assemblies'][n]['world']))<1e-7 and max(abs(x-y) for x,y in zip(g['local'],m['assemblies'][n]['local']))<1e-7 and set(m['assemblies'][n]['children'])==set(g['children'])|set(r['added_children'].get(n,[])) for n,g in old['assemblies'].items()))
cache={}
def definition(key):
    if key not in cache:
        d=m['definitions'][key];assert sha(d['brep_path'])==d['brep_sha256'];s=Part.Shape();s.read(d['brep_path']);cache[key]=s
    return cache[key].copy()
def world(name):
    v=rows[name];s=definition(v['definition']);s.Placement=App.Placement(App.Matrix(*v['frame']));return s
with tempfile.TemporaryDirectory(prefix='relocated_us_nuts_',dir=out) as temporary:
    relocated=Path(temporary)/native.name;shutil.copy2(native,relocated);assert sha(relocated)==sha(native)
    validate_native_bindings(dict(native_file=str(relocated),render_occurrences=list(rows),landmarks=[]),m)
    doc=App.openDocument(str(relocated))
    try:
        ck('All physical links reopen with local targets',all(doc.getObject(v['object']).LinkedObject.Document==doc for v in rows.values()))
        body=doc.getObject('Def_USStdControlNut');nut=body.Shape.copy()
        ck('Two source-identified U.S. Standard nut occurrences',sum(v['definition']==body.Name for v in rows.values())==2 and json.loads(body.SourceRecords)==['SNL:195:008'] and json.loads(body.SurveyIds)==['P_357771abe885bcb1'])
        ck('Saved new definition is closed and unscaled',body.Placement.isIdentity() and nut.Placement.isIdentity() and nut.isValid() and len(nut.Solids)==1 and nut.Solids[0].isClosed() and nut.getTolerance(1)<=1e-4)
    finally:App.closeDocument(doc.Name)
vertical=[f for f in nut.Faces if isinstance(f.Surface,Part.Plane) and abs(f.normalAt(0,0).z)<1e-7]
distances=[abs(f.CenterOfMass.dot(f.normalAt(0,0))) for f in vertical]
ck('Classic U.S.31.75mm across six flats',len(vertical)==6 and all(abs(2*d-31.75)<1e-6 for d in distances),half_widths_mm=distances)
horizontal=[f.CenterOfMass.z for f in nut.Faces if isinstance(f.Surface,Part.Plane) and abs(abs(f.normalAt(0,0).z)-1)<1e-7]
ck('Classic U.S.19.05mm nut thickness',len(horizontal)==2 and abs(min(horizontal))<1e-6 and abs(max(horizontal)-19.05)<1e-6,planes_mm=horizontal)
void=Part.makeCylinder(19.05/2,19.05,V());ck('Nominal3/4inch rod passage traverses full nut',not void.common(nut).Faces)
def planes(s,q,n):return [f for f in s.Faces if isinstance(f.Surface,Part.Plane) and f.normalAt(0,0).cross(n).Length<1e-7 and abs((f.CenterOfMass-q).dot(n))<1e-6]
def bearing(a,b,q,n):return sum(f.common(g).Area for f in planes(a,q,n) for g in planes(b,q,n))
for hand in ['Port','Starboard']:
    name=hand+'HighSpeedBrakeControlNut';one=world(name);fork=world(hand+'HighSpeedBrakeControlFork');pose=App.Placement(App.Matrix(*rows[name]['frame']));axis=pose.Rotation.multVec(V(0,0,1))
    area=bearing(one,fork,pose.Base,axis);ck(hand+' full socket-end nut seating',area>200,area_mm2=area)
    lifted=one.copy();lifted.translate(axis*.1);ck(hand+' lifted nut loses bearing',bearing(lifted,fork,pose.Base,axis)<1e-5)
    witness=Part.makeCylinder(19.05/2,19.05,pose.Base,axis);ck(hand+' installed nominal thread passage clear',not witness.common(one).Faces)
bounds={};boxes={}
for key in m['definitions']:
    s=definition(key);b=s.BoundBox;bounds[key]=np.array(list(itertools.product([b.XMin,b.XMax],[b.YMin,b.YMax],[b.ZMin,b.ZMax])));cache.pop(key,None)
for name,v in rows.items():
    f=np.array(v['frame']).reshape(4,4);points=bounds[v['definition']]@f[:3,:3].T+f[:3,3];boxes[name]=(points.min(axis=0),points.max(axis=0))
pairs=[]
for name in r['affected_occurrences']:
    one=world(name);low,high=boxes[name]
    for other,(lo,hi) in boxes.items():
        if other==name or not (np.all(lo<=high+1e-7) and np.all(hi>=low-1e-7)):continue
        common=one.common(world(other));vol=sum(abs(s.Volume) for s in common.Solids);valid=common.isNull() or common.isValid();pairs.append(dict(first=name,second=other,volume_mm3=vol,passed=valid and vol<1e-5))
ck('New nuts clear every retained powertrain occurrence',all(v['passed'] for v in pairs),pairs=len(pairs),failed=[v for v in pairs if not v['passed']])
write(out/'independent_checks.json',dict(passed=all(v['passed'] for v in checks),checks=checks,pairs=pairs,native_sha256=sha(native),source_native_sha256=sha(source),checker_sha256=sha(Path(__file__)),scope='Relocated all-link verification, exact two-target change, source-sized hex stock, nominal bore, actual fork seating and complete local material context. Finish applicability remains inferred.'))
print(len(checks),'U.S. nut checks;',len(pairs),'pairs;',all(v['passed'] for v in checks),flush=True)
for v in checks:
    if not v['passed']:print(v,flush=True)
assert all(v['passed'] for v in checks)
