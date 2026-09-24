"""Independent saved-solid checks for M363 retention and bottom-stop load paths."""
import argparse,math,sys
from pathlib import Path
H=Path(__file__).resolve().parent;STAGE=H.parents[1];ROOT=STAGE.parents[1];sys.path.insert(0,str(STAGE))
import FreeCAD as App
import Part
from lib.evidence import read,write,sha
from lib.camera_review import validate_native_bindings
V=App.Vector
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve();r=read(out/'report.json');native=out/r['native_file'];assert sha(native)==r['prototype_native_sha256']
parent=H/'transmission_high_brake_support_study/integrated01';pr=read(parent/'report.json');m=read(parent/'isolated/manifest.json');pnative=parent/pr['native_file'];assert sha(pnative)==r['parent_native_sha256']==m['native_sha256']
rows={v['name']:v for v in m['occurrences']};c=r['controls'];rc=r['receiver_controls'];d=r['details'];checks=[]
def ck(name,passed,**details):checks.append(dict(name=name,passed=bool(passed),**details))
def planes(s,point,normal):return [f for f in s.Faces if isinstance(f.Surface,Part.Plane) and f.normalAt(0,0).cross(normal).Length<1e-7 and abs((f.CenterOfMass-point).dot(normal))<1e-6]
def area(one,two,q,n):return sum(f.common(g).Area for f in planes(one,q,n) for g in planes(two,q,n))
def cylinders(s,radius):return [f for f in s.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-radius)<1e-6]
cache={}
def prior(name):
 row=rows[name];rec=m['definitions'][row['definition']]
 if row['definition'] not in cache:
  assert sha(rec['brep_path'])==rec['brep_sha256'];s=Part.Shape();s.read(rec['brep_path']);cache[row['definition']]=s
 s=cache[row['definition']].copy();s.Placement=App.Placement(App.Matrix(*row['frame']));return s
validate_native_bindings(dict(native_file=str(pnative),render_occurrences=[h+'HighSpeedBrakeAnchorEnd' for h in ['Port','Starboard']],landmarks=[]),m)
doc=App.openDocument(str(native));shapes={};definitions={};frames={}
try:
 ck('Saved prototype contains22 physical links and8 definitions',len(doc.Root.Group)==22 and len(doc.Definitions.Group)==8)
 for body in doc.Definitions.Group:
  s=body.Shape.copy();role=body.Name.removeprefix('Def_');definitions[role]=s
  ck(role+' is a closed identity solid with bounded tolerance',body.Placement.isIdentity() and s.Placement.isIdentity() and s.isValid() and len(s.Solids)==1 and s.Solids[0].isClosed() and s.getTolerance(1)<=1e-4,tolerance_mm=s.getTolerance(1))
 for link in doc.Root.Group:
  assert link.TypeId=='App::Link' and link.Scale==1 and tuple(link.ScaleVector)==(1.,1.,1.)
  pose=doc.Root.getGlobalPlacement().multiply(link.LinkPlacement);frames[link.Name]=pose;s=link.LinkedObject.Shape.copy();s.Placement=pose;shapes[link.Name]=s
  ck(link.Name+' native composed frame',max(abs(x-y) for x,y in zip(pose.toMatrix().A,r['specs'][link.Name]['frame']))<1e-7)
finally:App.closeDocument(doc.Name)
# The straight portion of the split pin crosses X=0 in the saved definition.
corners=[V(0,y,z) for y,z in [(-20,-20),(20,-20),(20,20),(-20,20)]]
section=definitions['anchor_cotter'].section(Part.Face(Part.makePolygon(corners+corners[:1])))
bb=section.optimalBoundingBox(False,False)
ck('Source3/16inch cotter envelope at pin centre',abs(bb.ZLength-4.7625)<1e-6,measured_mm=bb.ZLength)
# The two untrimmed analytic tail cylinders determine the developed leg length
# independently of the builder's stored total. Eye/leg overlap is excluded.
wire=(4.7625-c['cotter_center_spacing'])/2
faces=cylinders(definitions['anchor_cotter'],wire);tail_lengths=[]
for f in faces:
 axis=f.Surface.Axis
 if abs(abs(axis.x)-math.cos(math.radians(c['cotter_bend_angle'])))<1e-6:
  tail_lengths.append(f.Area/(2*math.pi*wire))
straight=c['pin_diameter']+c['cotter_head_gap']+c['cotter_exit_gap'];arc=c['cotter_bend_radius']*math.radians(c['cotter_bend_angle'])
ck('Two source2inch developed cotter legs under stated datum',len(tail_lengths)==2 and all(abs(straight+arc+length-50.8)<1e-5 for length in tail_lengths),derived_lengths_mm=[straight+arc+x for x in tail_lengths])
for hand in ['Port','Starboard']:
 base=App.Placement(V(*pr['interfaces'][hand+'HighSpeedBrake']['center_world_mm']),App.Rotation());bracket=shapes[hand+'AnchorBracket'];pin=shapes[hand+'AnchorPin'];cotter=shapes[hand+'AnchorCotter'];anchor=prior(hand+'HighSpeedBrakeAnchorEnd')
 f=frames[hand+'AnchorPin'];axis=f.Rotation.multVec(V(0,1,0));pivot=f.Base
 # MX60 mounting bores share the pin-bore radius but have inclined axes.
 # Select transverse receiver faces before checking their actual location.
 borefaces=[face for shape in [bracket,anchor] for face in cylinders(shape,rc['pin_bore_radius']) if face.Surface.Axis.cross(axis).Length<1e-7];shaft=cylinders(pin,c['pin_diameter']/2)
 ck(hand+' actual M361/M362/pin axes coincide',len(borefaces)>=3 and bool(shaft) and all(s.Surface.Axis.cross(axis).Length<1e-7 and (s.Surface.Center-pivot).cross(axis).Length<1e-6 for s in borefaces+shaft),bore_faces=len(borefaces))
 seat=f.multVec(V(0,-rc['fork_outer_width']/2,0));contact=area(pin,bracket,seat,axis)
 ck(hand+' pin head has positive bracket bearing',contact>100,area_mm2=contact)
 moved=pin.copy();moved.translate(axis*2)
 ck(hand+' head arrests inward passage',moved.common(bracket).Volume>1)
 moved=cotter.copy();moved.translate(-axis*5)
 ck(hand+' cotter arrests outward pin withdrawal',moved.common(bracket).Volume>1)
 ck(hand+' installed pin and cotter clear each other',not pin.common(cotter).Solids)
 cross=f.multVec(V(0,d['cotter_cross_y_mm'],0));drillaxis=f.Rotation.multVec(V(1,0,0));hole=Part.makeCylinder(4.7625/2+c['cotter_hole_gap'],c['pin_diameter']+2,cross-drillaxis*(c['pin_diameter']/2+1),drillaxis)
 stock=Part.makeCylinder(c['pin_diameter']/2,c['pin_under_head_length'],seat,axis);inside=cotter.common(stock);outside=inside.cut(hole)
 ck(hand+' cotter traverses the actual drilled shank',bool(inside.Solids) and not outside.Solids and not hole.common(pin).Solids)
 bottom=shapes[hand+'BottomStop'];lock=shapes[hand+'BottomLockPlate'];bf=base.multiply(App.Placement(App.Matrix(*d['bottom_frame'])));normal=bf.Rotation.multVec(V(0,0,1))
 contact=area(bottom,bracket,bf.Base,normal);ck(hand+' bottom stop has positive cast-shelf support',contact>300,area_mm2=contact)
 lifted=bottom.copy();lifted.translate(-normal*.1);ck(hand+' displaced stop loses shelf bearing',area(lifted,bracket,bf.Base,normal)<1e-5)
 contact=area(bottom,lock,bf.multVec(V(0,0,-c['bottom_stock'])),normal);ck(hand+' common locking plate bears on stop',contact>300,area_mm2=contact)
 for index,local in enumerate(d['mount_seat_frames'],1):
  seatframe=base.multiply(App.Placement(App.Matrix(*local)));bolt=shapes[hand+'BottomMountScrew'+str(index)];pose=frames[hand+'BottomMountScrew'+str(index)]
  contact=area(bolt,lock,pose.Base,normal);ck(hand+' MX76 head bearing'+str(index),contact>80,area_mm2=contact)
  depth=d['mount_receiving_depth_mm'];hole=Part.makeCylinder(c['mount_diameter']/2+c['mount_bore_gap']-.01,depth-.02,V(0,0,.01));hole.Placement=seatframe
  ck(hand+' MX76 blind receiver passage'+str(index),not hole.common(bracket).Solids)
  witness=Part.makeCylinder(c['mount_diameter']/2,.5,V(0,0,depth+.2));witness.Placement=seatframe
  ck(hand+' MX76 blind receiver retains back stock'+str(index),not witness.cut(bracket).Solids and not witness.cut(bracket).Faces)
 for index in [1,2]:
  nut=shapes[hand+'StopNut'+str(index)];screw=shapes[hand+'StopScrew'+str(index)];nf=frames[hand+'StopNut'+str(index)];q=nf.multVec(V(0,0,c['stop_nut_stock']));contact=area(nut,bottom,q,normal)
  ck(hand+' M400 jam nut bears on stop'+str(index),contact>50,area_mm2=contact)
  target=Part.makeCompound([prior(hand+'HighSpeedBrake'+x) for x in ['LongBand','ShortBand','AnchorEnd']]);gap=screw.distToShape(target)[0]
  ck(hand+' M400 tip has bounded adjustment gap'+str(index),.05<gap<.5,gap_mm=gap)
  shifted=screw.copy();shifted.translate(normal*.6)
  ck(hand+' overadvanced M400 reaches band'+str(index),shifted.common(target).Volume>1e-4)
write(out/'independent_checks.json',dict(passed=all(v['passed'] for v in checks),checks=checks,native_sha256=sha(native),parent_native_sha256=sha(pnative),checker_sha256=sha(Path(__file__)),scope='Saved pin axes/retention, source cotter envelope/developed legs, positive mounting contacts, blind passages/back stock and stop adjustment. Full service paths, exchange, integration and source interpretation remain separate.'))
print('Saved bottom-stop checks',len(checks),'passed',all(v['passed'] for v in checks),flush=True)
for v in checks:
 if not v['passed']:print(v,flush=True)
assert all(v['passed'] for v in checks)
