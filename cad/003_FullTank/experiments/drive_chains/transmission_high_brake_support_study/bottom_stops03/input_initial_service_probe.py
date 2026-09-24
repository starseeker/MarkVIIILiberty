"""Bounded straight pin withdrawal and drift-access envelopes; not full brake removal."""
import argparse,sys
from pathlib import Path
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H.parents[1]))
from lib.evidence import read,write,sha
import FreeCAD as A
import Part
V=A.Vector
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve();r=read(out/'report.json');parent=H/'transmission_high_brake_support_study/integrated01';m=read(parent/'isolated/manifest.json');pr=read(parent/'report.json')
assert sha(out/r['native_file'])==r['prototype_native_sha256'];assert sha(parent/pr['native_file'])==r['parent_native_sha256']==m['native_sha256'];cache={};neighbors={}
for row in m['occurrences']:
 if row['name'].endswith('HighSpeedBrakeAnchorBracket'):continue
 # Epicyclic/frame/brake material only. Handbook first removes the gear unit
 # from the tank, so unrelated tank and engine objects are outside this probe.
 if not any(x in row['name'] for x in ['Transmission','HighSpeedBrake','LowSpeedBrake','SmallPlanet','Reversing']):continue
 key=row['definition'];d=m['definitions'][key]
 if key not in cache:
  assert sha(d['brep_path'])==d['brep_sha256'];s=Part.Shape();s.read(d['brep_path']);cache[key]=s
 s=cache[key].copy();s.Placement=A.Placement(A.Matrix(*row['frame']));neighbors[row['name']]=s
# Read the actual saved prototype's revised receiving forks and pin frames.
doc=A.openDocument(str(out/r['native_file']));frames={}
try:
 for hand in ['Port','Starboard']:
  link=doc.getObject(hand+'AnchorBracket');s=link.LinkedObject.Shape.copy();s.Placement=doc.Root.getGlobalPlacement().multiply(link.LinkPlacement);neighbors[hand+'RevisedBracket']=s
  frames[hand]=doc.Root.getGlobalPlacement().multiply(doc.getObject(hand+'AnchorPin').LinkPlacement)
finally:A.closeDocument(doc.Name)
c=r['controls'];d=r['details'];seat=d['pin_head_seat_y_mm'];tip=d['pin_tip_y_mm'];distance=80.;tools={}
for hand,pose in frames.items():
 shaft=Part.makeCylinder(c['pin_diameter']/2,tip-seat+distance,V(0,seat-distance,0),V(0,1,0))
 head=Part.makeCylinder(c['pin_head_radius'],distance+c['pin_head_stock'],V(0,seat-distance-c['pin_head_stock'],0),V(0,1,0))
 for role,s in [('withdrawal',shaft.fuse(head)),('drift_access',Part.makeCylinder(5,100,V(0,tip,0),V(0,1,0)))]:
  s.Placement=pose;tools[hand+'_'+role]=s;s.exportBrep(str(out/(hand+'_'+role+'_envelope.brep')))
records=[]
for name,s in tools.items():
 for label,other in neighbors.items():
  if not s.BoundBox.intersect(other.BoundBox):continue
  common=s.common(other);volume=sum(abs(x.Volume) for x in common.Solids);valid=common.isNull() or common.isValid();records.append(dict(envelope=name,neighbor=label,common_mm3=volume,passed=valid and volume<1e-5))
write(out/'pin_service_probe.json',dict(passed=all(x['passed'] for x in records),pairs=records,neighbor_count=len(neighbors),native_sha256=r['prototype_native_sha256'],parent_native_sha256=r['parent_native_sha256'],probe_sha256=sha(Path(__file__)),withdrawal_mm=distance,drift_radius_mm=5,drift_access_length_mm=100,scope='Conservative straight pin withdrawal and a100mm drift approach after cotter/bottom-stop removal, against selected retained epicyclic/frame/brake material. Gear extraction from tank, cotter unbending/tool handling and complete service sequence are not qualified.',installation_qualified=False))
print('Pin service envelope pairs',len(records),'passed',all(x['passed'] for x in records),flush=True)
for v in records:
 if not v['passed']:print(v,flush=True)
