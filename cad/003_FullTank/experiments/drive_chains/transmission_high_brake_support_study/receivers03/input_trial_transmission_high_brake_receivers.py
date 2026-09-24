"""Build and check a bounded receiving-web/anchor prototype before integration."""
import argparse, itertools, json, shutil, sys
from pathlib import Path
from types import SimpleNamespace
H=Path(__file__).resolve().parent; STAGE=H.parents[1]; ROOT=STAGE.parents[1]
sys.path[:0]=[str(H),str(STAGE)]
from lib.evidence import read,write,sha
import FreeCAD as App
import Part
import numpy as np
from lib.camera_review import validate_native_bindings
from lib.visual_review import shaded
from lib.cad_build import COLORS,metadata
from transmission_high_brake_support_parts import parts

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
p.add_argument('--controls',type=Path,default=H/'transmission_high_brake_support_study/controls.json');a=p.parse_args()
out=a.output.resolve();assert not out.exists();out.mkdir(parents=True)
parent=H/'transmission_high_brake_mechanism_study/trial01';r=read(parent/'report.json');m=read(parent/'isolated/manifest.json')
native=parent/r['native_file'];assert sha(native)==r['native_sha256']==m['native_sha256']
rows={o['name']:o for o in m['occurrences']};cache={};V=App.Vector
def definition(key):
 if key not in cache:
  d=m['definitions'][key];assert sha(d['brep_path'])==d['brep_sha256'];s=Part.Shape();s.read(d['brep_path']);cache[key]=s
 return cache[key].copy()
def world(name):
 row=rows[name];s=definition(row['definition']);s.Placement=App.Placement(App.Matrix(*row['frame']));return s
c=read(a.controls)['controls'];case_name='CenterTransmissionCore_bevel_case';case_key=rows[case_name]['definition'];old=definition(case_key)
selected=[case_name]+[hand+'HighSpeedBrakeAnchorEnd' for hand in ['Port','Starboard']]
validate_native_bindings(dict(native_file=str(native),render_occurrences=selected,landmarks=[]),m)
shapes,details,envelopes=parts(c,old)
for name,s in {**shapes,**envelopes}.items():s.exportBrep(str(out/(name+'.brep')))
frame=App.Placement(App.Matrix(*rows[case_name]['frame']));installed={'Case':shapes['case'].copy()};installed['Case'].Placement=frame
mounts={};specs={};colors={};newnames=[]
for hand,sign in [('Port',1),('Starboard',-1)]:
 pose=frame.multiply(App.Placement(V(0,sign*c['brake_station'],0),App.Rotation()))
 name=hand+'AnchorBracket';s=shapes['anchor_bracket'].copy();s.Placement=pose;installed[name]=s;specs[name]=('anchor_bracket',pose);newnames.append(name)
 name=hand+'AnchorLockPlate';s=shapes['anchor_lock_plate'].copy();s.Placement=pose;installed[name]=s;specs[name]=('anchor_lock_plate',pose);newnames.append(name)
 for i,f in enumerate(details['mounts']['bottom']['bolt_seat_frames'],1):
  local=App.Placement(App.Matrix(*f));local.Base+=local.Rotation.multVec(V(0,0,c['bracket_stock']+c['lock_plate_stock']))
  placement=pose.multiply(local);name=hand+'AnchorMountScrew'+str(i);s=shapes['mount_screw'].copy();s.Placement=placement
  installed[name]=s;specs[name]=('mount_screw',placement);newnames.append(name)
# The prototype keeps the real case datum and source identities, with all new
# shapes called out as unqualified. It is not substituted for the main assembly.
doc=App.newDocument('ReceivingWebStudy');root=doc.addObject('App::Part','Root');defs=doc.addObject('App::Part','Definitions')
made={}
for role,mark in [('case','M263'),('anchor_bracket','M362'),('mount_screw','MX60'),('anchor_lock_plate','MX61')]:
 body=doc.addObject('PartDesign::Body','Def_'+role);defs.addObject(body);body.newObject('PartDesign::Feature','ReceiverHypothesis').Shape=shapes[role]
 metadata(body,SourcePartMark=mark,Representation='unqualified_prototype',ReconstructionStatus='Receiving-web experiment; do not promote without full independent checks and source review.');made[role]=body
specs['Case']=('case',frame)
for name,(role,pose) in specs.items():
 link=doc.addObject('App::Link',name);root.addObject(link);link.setLink(made[role]);link.LinkPlacement=pose
defs.Visibility=False;doc.recompute();doc.saveAs(str(out/'ReceivingWebStudy.FCStd'));App.closeDocument(doc.Name)
checks=[]
def ck(name,passed,**more):
 checks.append(dict(name=name,passed=bool(passed),**more));write(out/'check_progress.json',dict(checks=checks))
missing=old.cut(shapes['case']);ck('Original case material retained',not missing.Faces and not missing.Solids)
added=shapes['case'].cut(old);outside=added.cut(envelopes['addition_envelope']);ck('Added material confined to declared receiving stock',not outside.Faces and not outside.Solids)
ck('Actual saved anchor bore frame retained',all(abs(v-c['anchor_center'][i])<1e-7 for i,v in enumerate(read(H/'transmission_high_brake_support_study/context01/report.json')['anchor_pin_center_brake_mm'])))
# Positive face contact, rather than zero distance alone, establishes each seat.
def faces(s,point,normal):
 return [f for f in s.Faces if isinstance(f.Surface,Part.Plane) and f.normalAt(0,0).cross(normal).Length<1e-7 and abs((f.CenterOfMass-point).dot(normal))<1e-6]
for hand,sign in [('Port',1),('Starboard',-1)]:
 d=details['mounts']['bottom'];n=V(*d['normal']);o=frame.multVec(V(*d['origin'])+V(0,sign*c['brake_station'],0)+n*d['seat_normal_mm'])
 one=faces(installed[hand+'AnchorBracket'],o,n);two=faces(installed['Case'],o,n)
 area=sum(f.common(g).Area for f in one for g in two);ck(hand+' bracket has positive case-seat contact',area>1000,area_mm2=area)
 # Fork cheeks leave the original M361 material intact and share its pin axis.
 anchor=world(hand+'HighSpeedBrakeAnchorEnd');intersection=installed[hand+'AnchorBracket'].common(anchor)
 ck(hand+' bracket clears retained M361 end',not intersection.Solids,common_volume_mm3=intersection.Volume)
 plate=installed[hand+'AnchorLockPlate'];bracket=installed[hand+'AnchorBracket']
 q=o+n*c['bracket_stock'];area=sum(f.common(g).Area for f in faces(plate,q,n) for g in faces(bracket,q,n))
 ck(hand+' common locking strip bears on bracket',area>1000,area_mm2=area)
 for i in [1,2]:
  screw=installed[hand+'AnchorMountScrew'+str(i)];pose=specs[hand+'AnchorMountScrew'+str(i)][1];q=pose.Base
  bearing=sum(f.common(g).Area for f in faces(plate,q,n) for g in faces(screw,q,n))
  ck(hand+' mounting screw '+str(i)+' head bears on locking strip',bearing>100,area_mm2=bearing)
  # A deliberately displaced plate must lose its coplanar bearing area.
  lifted=plate.copy();lifted.translate(n*.1)
  ck(hand+' displaced locking strip fails head support '+str(i),not faces(lifted,q,n))
  shank=Part.makeCylinder(c['mount_screw_diameter']/2,c['bracket_stock']+c['lock_plate_stock'],V(0,0,-c['bracket_stock']-c['lock_plate_stock']))
  shank.Placement=pose
  ck(hand+' through mounting passage '+str(i),not shank.common(Part.makeCompound([bracket,plate])).Solids)
COLORS.update(Receiver=(.66,.44,.27),Retained=(.50,.61,.68))
render_items=[]
for name,s in installed.items():
 role='Retained' if name=='Case' else 'Receiver';render_items.append(dict(id=name,shape=s,target=SimpleNamespace(Shape=s),definition=name,system=role,representation='assembly'))
context=[]
for name in ['TransmissionFrame_TopChannel','TransmissionFrame_BottomChannel']+[o['name'] for o in m['occurrences'] if o['name'].startswith('PortHighSpeedBrake') and o['name'].endswith(('Band','Lining','FrontEnd','AnchorEnd'))]:
 s=world(name);context.append(dict(id=name,shape=s,target=SimpleNamespace(Shape=s),definition=name,system='Retained',representation='assembly'))
shaded(render_items,out/'receiver_isometric.svg',(1,-1,.4),'Receiving webs and M362 anchor brackets | unqualified reconstruction trial',context=context)
# Read each definition once for conservative whole-assembly neighbor filtering.
bounds={}
for key,d in m['definitions'].items():
 s=definition(key);bb=s.BoundBox;bounds[key]=np.array(list(itertools.product([bb.XMin,bb.XMax],[bb.YMin,bb.YMax],[bb.ZMin,bb.ZMax])))
 if key not in {case_key,rows['PortHighSpeedBrakeAnchorEnd']['definition']}:cache.pop(key,None)
boxes={}
for name,row in rows.items():
 f=np.array(row['frame']).reshape(4,4);pts=bounds[row['definition']]@f[:3,:3].T+f[:3,3];boxes[name]=(pts.min(axis=0),pts.max(axis=0))
collisions=[];invalid=[];tested=0
for fresh,s in installed.items():
 b=s.BoundBox;lo=np.array([b.XMin,b.YMin,b.ZMin]);hi=np.array([b.XMax,b.YMax,b.ZMax])
 for name,(b0,b1) in boxes.items():
  if name==case_name or not (np.all(b0<=hi+1e-7) and np.all(b1>=lo-1e-7)):continue
  other=world(name);common=s.common(other);vol=sum(abs(v.Volume) for v in common.Solids);tested+=1
  if not common.isValid():invalid.append([fresh,name])
  if vol>1e-5:collisions.append(dict(first=fresh,second=name,volume_mm3=vol))
  if tested%20==0:write(out/'interference_progress.json',dict(tested=tested,collisions=collisions,invalid=invalid))
for one,two in itertools.combinations(installed,2):
 common=installed[one].common(installed[two]);vol=sum(abs(v.Volume) for v in common.Solids);tested+=1
 if not common.isValid():invalid.append([one,two])
 if vol>1e-5:collisions.append(dict(first=one,second=two,volume_mm3=vol))
ck('New receiver and bracket material clears retained assembly',not collisions and not invalid,pairs=tested,collisions=collisions,invalid=invalid)
assert sha(native)==r['native_sha256']
for f in [Path(__file__),a.controls,H/'transmission_high_brake_support_parts.py']:
 shutil.copy2(f,out/('input_'+f.name))
write(out/'report.json',dict(passed=all(v['passed'] for v in checks),checks=checks,controls=c,details=details,
 parent_native_sha256=r['native_sha256'],prototype_native_sha256=sha(out/'ReceivingWebStudy.FCStd'),
 source_registration_sha256=sha(H/'transmission_high_brake_support_study/source_registration.json'),
 input_hashes={str(f.relative_to(ROOT)):sha(f) for f in [Path(__file__),a.controls.resolve(),H/'transmission_high_brake_support_parts.py']},
 runtime=dict(freecad=App.Version(),occ=Part.OCC_VERSION),geometry_integrated=False,standard_assembly_modified=False,
 historical_geometry_qualified=False,installation_qualified=False,packet_complete=False,
 limits=details['limitations']+['Anchor pins/cotters and stops not present in this prototype.',
     'STEP, rebuild, receiving-void preservation and parameter variation are not yet qualified.']))
print('Receiver trial checks',len(checks),'pairs',tested,'passed',all(v['passed'] for v in checks),flush=True)
for v in checks:
 if not v['passed']:print(v,flush=True)
