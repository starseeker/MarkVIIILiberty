"""Independent saved-material, upper mounting stack and clip-retention checks."""
import argparse,math,sys
from pathlib import Path
H=Path(__file__).resolve().parent;STAGE=H.parents[1];sys.path.insert(0,str(STAGE))
import FreeCAD as App
import Part
from lib.evidence import read,write,sha
from lib.camera_review import validate_native_bindings
V=App.Vector
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve();r=read(out/'report.json');native=out/r['native_file'];assert sha(native)==r['prototype_native_sha256']
parent=H/'transmission_high_brake_support_study/integrated_bottom01';pr=read(parent/'report.json');m=read(parent/'isolated/manifest.json');pnative=parent/pr['native_file'];assert sha(pnative)==r['parent_native_sha256']==m['native_sha256']
rows={v['name']:v for v in m['occurrences']};c=r['controls'];rc=r['receiver_controls'];d=r['details'];checks=[]
def ck(name,passed,**details):checks.append(dict(name=name,passed=bool(passed),**details))
def planes(s,q,n):return [f for f in s.Faces if isinstance(f.Surface,Part.Plane) and f.normalAt(0,0).cross(n).Length<1e-7 and abs((f.CenterOfMass-q).dot(n))<1e-6]
def area(one,two,q,n):return sum(f.common(g).Area for f in planes(one,q,n) for g in planes(two,q,n))
def cylinders(s,radius):return [f for f in s.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-radius)<1e-6]
cache={}
def definition(key):
 if key not in cache:
  rec=m['definitions'][key];assert sha(rec['brep_path'])==rec['brep_sha256'];s=Part.Shape();s.read(rec['brep_path']);cache[key]=s
 return cache[key].copy()
def prior(name):
 row=rows[name];s=definition(row['definition']);s.Placement=App.Placement(App.Matrix(*row['frame']));return s
validate_native_bindings(dict(native_file=str(pnative),render_occurrences=[h+'HighSpeedBrake'+v for h in ['Port','Starboard'] for v in ['LongBand','ShortBand','AnchorEnd','LongFrontEnd','ShortFrontEnd']],landmarks=[]),m)
doc=App.openDocument(str(native));shapes={};definitions={};frames={}
try:
 ck('Saved prototype contains17 physical links and8 definitions',len(doc.Root.Group)==17 and len(doc.Definitions.Group)==8)
 for body in doc.Definitions.Group:
  s=body.Shape.copy();role=body.Name.removeprefix('Def_');definitions[role]=s
  ck(role+' closed identity solid with bounded tolerance',body.Placement.isIdentity() and s.Placement.isIdentity() and s.isValid() and len(s.Solids)==1 and s.Solids[0].isClosed() and s.getTolerance(1)<=1e-4,tolerance_mm=s.getTolerance(1))
 for link in doc.Root.Group:
  assert link.TypeId=='App::Link' and link.Scale==1 and tuple(link.ScaleVector)==(1.,1.,1.)
  pose=doc.Root.getGlobalPlacement().multiply(link.LinkPlacement);frames[link.Name]=pose;s=link.LinkedObject.Shape.copy();s.Placement=pose;shapes[link.Name]=s
  ck(link.Name+' native composed frame',max(abs(x-y) for x,y in zip(pose.toMatrix().A,r['specs'][link.Name]['frame']))<1e-7)
finally:App.closeDocument(doc.Name)
for role,key in r['shared_definitions'].items():
 one=definitions[role];two=definition(key);a,b=one.cut(two),two.cut(one)
 ck(role+' reuses complete prior definition',not a.Faces and not b.Faces,missing_mm3=a.Volume,added_mm3=b.Volume)
# All contact areas below come from the saved analytic faces, not distance alone.
angle=math.radians(rc['top_slope_deg']);normal=V(math.sin(angle),0,math.cos(angle));tangent=V(-math.cos(angle),0,math.sin(angle));case=shapes['Case'];casepose=frames['Case'];casecenter=casepose.Base
for hand in ['Port','Starboard']:
 base=V(*pr['interfaces'][hand+'HighSpeedBrake']['center_world_mm']);seat=base+V(*rc['top_origin']);back=shapes[hand+'BackStop'];top=shapes[hand+'TopStop'];plate=shapes[hand+'UpperLockPlate']
 for label,one,two,q in [('M398 supported by case',back,case,seat),('M399 supported by M398',top,back,seat+normal*c['back_stock']),('MX61 bears on M399',plate,top,seat+normal*(c['back_stock']+c['top_stock']))]:
  contact=area(one,two,q,normal);ck(hand+' '+label,contact>300,area_mm2=contact)
 moved=back.copy();moved.translate(normal*.1);ck(hand+' raised back stop loses case bearing',area(moved,case,seat,normal)<1e-5)
 centers=[]
 for index in [1,2]:
  bolt=shapes[hand+'UpperMountScrew'+str(index)];bf=frames[hand+'UpperMountScrew'+str(index)];q=bf.Base;axis=bf.Rotation.multVec(V(0,0,1));centers.append(q)
  contact=area(bolt,plate,q,normal);ck(hand+' MX60 head bearing'+str(index),contact>150,area_mm2=contact)
  for label,s in [('case',case),('M398',back),('M399',top),('MX61',plate)]:
   bores=[f for f in cylinders(s,rc['mount_bore_radius']) if f.Surface.Axis.cross(axis).Length<1e-7 and (f.Surface.Center-q).cross(axis).Length<1e-6]
   ck(hand+' '+label+' actual MX60 axis'+str(index),bool(bores),coaxial_faces=len(bores))
  tip=min((v.Point-seat).dot(normal) for v in bolt.Vertexes);engagement=-tip;ck(hand+' MX60 positive actual engagement'+str(index),10<engagement<rc['case_foot_stock'],engagement_mm=engagement)
  casepoint=q-normal*((q-seat).dot(normal));depth=rc['mount_screw_length']-rc['bracket_stock']-rc['lock_plate_stock']+rc['blind_gap']
  passage=Part.makeCylinder(rc['mount_bore_radius']-.01,depth-.02,casepoint-normal*(depth-.01),normal)
  ck(hand+' clear blind passage'+str(index),not passage.common(case).Solids)
  witness=Part.makeCylinder(rc['mount_screw_diameter']/2,.5,casepoint-normal*(depth+.7),normal);difference=witness.cut(case)
  ck(hand+' solid stock beyond blind hole'+str(index),not difference.Solids and not difference.Faces)
 ck(hand+' shared MX61 actual60mm hole pitch',abs((centers[1]-centers[0]).Length-60)<1e-6,measured_mm=(centers[1]-centers[0]).Length)
 clip=shapes[hand+'Clip'];cf=frames[hand+'Clip'];q=cf.Base;cn=cf.Rotation.multVec(V(0,0,1));ct=cf.Rotation.multVec(V(1,0,0));screw=shapes[hand+'StopScrew'];nut=shapes[hand+'StopNut'];sf=frames[hand+'StopScrew'];nf=frames[hand+'StopNut']
 contact=area(clip,top,q-cn*c['top_stock']/2,cn);ck(hand+' clip floor bears on tongue',contact>200,area_mm2=contact)
 contact=area(nut,clip,nf.Base,cn);ck(hand+' M400 jam nut bears on clip roof',contact>50,area_mm2=contact)
 for label,s,radius in [('clip',clip,pr['controls']['stop_screw_diameter']/2+c['clip_bore_gap']),('tongue',top,c['tongue_bore_radius']),('nut',nut,pr['controls']['stop_screw_diameter']/2+pr['controls']['stop_bore_gap'])]:
  faces=[f for f in cylinders(s,radius) if f.Surface.Axis.cross(cn).Length<1e-7 and (f.Surface.Center-q).cross(cn).Length<1e-6];ck(hand+' M400 coaxial '+label,bool(faces),coaxial_faces=len(faces))
 # A nominal shaft tube must traverse the entire nut's geometric thread envelope.
 nutstock=pr['controls']['stop_nut_stock'];shaftwitness=Part.makeCylinder(pr['controls']['stop_screw_diameter']/2-.01,nutstock-.02,nf.Base+cn*.01,cn);missing=shaftwitness.cut(screw)
 ck(hand+' M400 shaft spans full nut stock',not missing.Solids and not missing.Faces)
 moved=clip.copy();moved.translate(ct*10);ck(hand+' M400 arrests clip sliding',moved.common(screw).Volume>1e-3)
 moved=top.copy();moved.translate(ct*10);ck(hand+' pierced tongue retains M400 axis',moved.common(screw).Volume>1e-3)
 target=Part.makeCompound([prior(hand+'HighSpeedBrake'+x) for x in ['LongBand','ShortBand','AnchorEnd','LongFrontEnd','ShortFrontEnd']]);gap=screw.distToShape(target)[0]
 ck(hand+' M400 bounded gap to complete band',.05<gap<.5,gap_mm=gap)
 moved=screw.copy();moved.translate(-cn*.6);ck(hand+' overadvanced M400 reaches band',moved.common(target).Volume>1e-4)
 gap=back.distToShape(target)[0];ck(hand+' M398 toe has bounded band gap',.05<gap<.5,gap_mm=gap)
 direction=V(*d['back']['toe_direction']);moved=back.copy();moved.translate(direction*.6);ck(hand+' overadvanced M398 reaches band',moved.common(target).Volume>1e-4)
write(out/'independent_checks.json',dict(passed=all(v['passed'] for v in checks),checks=checks,native_sha256=sha(native),parent_native_sha256=sha(pnative),checker_sha256=sha(Path(__file__)),scope='Saved hardware reuse, upper receiving stack/bearing, blind stock, coaxial bores, M365 floor and nut seats, clip/tongue retention and complete-band adjustment. Full service and historical certainty remain separate.'))
print('Saved upper-stop checks',len(checks),'passed',all(v['passed'] for v in checks),flush=True)
for v in checks:
 if not v['passed']:print(v,flush=True)
assert all(v['passed'] for v in checks)
