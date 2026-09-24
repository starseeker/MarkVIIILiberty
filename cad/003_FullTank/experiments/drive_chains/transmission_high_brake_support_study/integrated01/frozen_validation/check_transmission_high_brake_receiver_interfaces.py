"""Independent saved receiver seat, blind-stock and inherited bore witnesses."""
import argparse,sys
from pathlib import Path
H=Path(__file__).resolve().parent;STAGE=H.parents[1];ROOT=STAGE.parents[1];sys.path.insert(0,str(STAGE))
from lib.evidence import read,write,sha
import FreeCAD as App
import Part
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve()
r=read(out/'report.json');native=out/'ReceivingWebStudy.FCStd';assert sha(native)==r['prototype_native_sha256']
doc=App.openDocument(str(native))
try:
 case=doc.Def_case.Shape.copy();worldcase=case.copy();worldcase.Placement=doc.Root.getGlobalPlacement().multiply(doc.Case.LinkPlacement);frame=worldcase.Placement
finally:App.closeDocument(doc.Name)
c=r['controls'];m=read(H/'transmission_high_brake_mechanism_study/trial01/isolated/manifest.json');rows={o['name']:o for o in m['occurrences']};V=App.Vector;checks=[]
def ck(name,passed,**detail):checks.append(dict(name=name,passed=bool(passed),**detail))
def planes(s,q,n):return [f for f in s.Faces if isinstance(f.Surface,Part.Plane) and f.normalAt(0,0).cross(n).Length<1e-7 and abs((f.CenterOfMass-q).dot(n))<1e-6]
for role in ['top','bottom']:
 row=rows['TransmissionFrame_'+role.title()+'Channel'];d=m['definitions'][row['definition']];assert sha(d['brep_path'])==d['brep_sha256']
 channel=Part.Shape();channel.read(d['brep_path']);channel.Placement=App.Placement(App.Matrix(*row['frame']))
 q=frame.multVec(V(c['frame_front_x'],0,0));n=V(1,0,0)
 fs,gs=planes(worldcase,q,n),planes(channel,q,n)
 zlo,zhi=sorted([c[role+'_frame_web_z'],c[role+'_frame_web_z']+(1 if role=='top' else -1)*c['channel_height']])
 for hand,sign in [('Port',1),('Starboard',-1)]:
  ylo,yhi=sorted([sign*(c['brake_station']-c['bracket_width']/2),sign*(c['bearing_station']+c['web_stock']/2)])
  corners=[frame.multVec(V(c['frame_front_x'],y,z)) for y,z in [(ylo,zlo),(yhi,zlo),(yhi,zhi),(ylo,zhi)]]
  patch=Part.Face(Part.makePolygon(corners+corners[:1]))
  area=sum(f.common(g).common(patch).Area for f in fs for g in gs)
  ck(hand+role+' new outer tie bears on existing channel',area>1000,area_mm2=area)
  shift=channel.copy();shift.translate(V(-.1,0,0));ck(hand+role+' displaced channel loses contact plane',not planes(shift,q,n))
  for index,values in enumerate(r['details']['mounts'][role]['bolt_seat_frames'],1):
   pose=App.Placement(App.Matrix(*values));pose.Base+=V(0,sign*c['brake_station'],0)
   depth=c['mount_screw_length']-c['bracket_stock']-c['lock_plate_stock']+c['blind_gap']
   void=Part.makeCylinder(c['mount_screw_diameter']/2,depth,V(0,0,-depth));void.Placement=pose
   ck(hand+role+' blind mounting passage '+str(index),not case.common(void).Solids)
   witness=Part.makeCylinder(3,.5,V(0,0,-depth-1));witness.Placement=pose
   ck(hand+role+' material beyond blind drill '+str(index),not witness.cut(case).Faces and not witness.cut(case).Solids)
# M265/M266 bearing cap studs: preserve their complete existing nominal
# receiving envelopes, including clearance around the retained hardware.
b=read(H/'transmission_brake_bearing_controls.json')['controls'];y=b['dowel_y']
for hand in [1,-1]:
 for sign in [-1,1]:
  start=b['stud_start']-b['blind_gap'];end=b['nut_seat']+1
  tool=Part.makeCylinder(b['stud_diameter']/2+b['hole_gap'],end-start,V(start,hand*y,sign*b['stud_axis_z']),V(1,0,0))
  ck('Retained brake-bearing stud receiver '+str((hand,sign)),not case.common(tool).Solids)
result=dict(passed=all(v['passed'] for v in checks),checks=checks,native_sha256=sha(native),checker_sha256=sha(Path(__file__)),
 scope='Saved case: four new outer frame contacts, eight blind passages and back-stock witnesses, four inherited bearing-cap stud receiving envelopes. No structural or full service-path qualification.',
 historical_geometry_qualified=False,installation_qualified=False)
write(out/'receiver_interface_checks.json',result)
print('Saved receiver interface checks',len(checks),'passed',result['passed'],flush=True)
for v in checks:
 if not v['passed']:print(v,flush=True)
assert result['passed']
