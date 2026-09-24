"""Build a saved bottom-stop and anchor-retention prototype against actual neighbors."""
import argparse,itertools,shutil,sys
from pathlib import Path
from types import SimpleNamespace
H=Path(__file__).resolve().parent;STAGE=H.parents[1];ROOT=STAGE.parents[1];sys.path[:0]=[str(H),str(STAGE)]
from lib.evidence import read,write,sha
import FreeCAD as App
import Part
import numpy as np
from lib.camera_review import validate_native_bindings
from lib.visual_review import shaded
from lib.cad_build import COLORS,metadata
from transmission_high_brake_stop_parts import parts
V=App.Vector
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--controls',type=Path,default=H/'transmission_high_brake_support_study/stop_controls.json');a=p.parse_args()
out=a.output.resolve();assert not out.exists();out.mkdir(parents=True)
packet=H/'transmission_high_brake_support_study';parent=packet/'integrated01';r=read(parent/'report.json');m=read(parent/'isolated/manifest.json');native=parent/r['native_file']
assert sha(native)==r['native_sha256']==m['native_sha256'];rows={v['name']:v for v in m['occurrences']};cache={}
def definition(key):
 if key not in cache:
  d=m['definitions'][key];assert sha(d['brep_path'])==d['brep_sha256'];s=Part.Shape();s.read(d['brep_path']);cache[key]=s
 return cache[key].copy()
def world(name):
 row=rows[name];s=definition(row['definition']);s.Placement=App.Placement(App.Matrix(*row['frame']));return s
base=App.Placement(V(*r['interfaces']['PortHighSpeedBrake']['center_world_mm']),App.Rotation())
target_names=['PortHighSpeedBrake'+v for v in ['LongBand','ShortBand','AnchorEnd']]
selected=target_names+['PortHighSpeedBrakeAnchorBracket','StarboardHighSpeedBrakeAnchorBracket']
validate_native_bindings(dict(native_file=str(native),render_occurrences=selected,landmarks=[]),m)
targets=[]
for name in target_names:
 s=world(name);s.Placement=base.inverse().multiply(s.Placement);targets.append(s)
c=read(a.controls)['controls'];receiver=r['controls'];old_bracket=definition('Def_HighBrakeSupport_anchor_bracket')
shapes,details,envelopes=parts(c,receiver,old_bracket,targets)
for name,s in {**shapes,**envelopes}.items():s.exportBrep(str(out/(name+'.brep')))
specs={};installed={}
for hand in ['Port','Starboard']:
 base=App.Placement(V(*r['interfaces'][hand+'HighSpeedBrake']['center_world_mm']),App.Rotation())
 def add(suffix,role,local):
  name=hand+suffix;pose=base.multiply(local);s=shapes[role].copy();s.Placement=pose;specs[name]=dict(role=role,frame=list(pose.toMatrix().A),local_frame=list(local.toMatrix().A));installed[name]=s
 for suffix,role in [('AnchorBracket','anchor_bracket'),('BottomStop','bottom_stop'),('BottomLockPlate','bottom_lock_plate')]:add(suffix,role,App.Placement())
 turn=App.Rotation(V(0,0,1),180) if hand=='Port' else App.Rotation()
 pin_frame=App.Placement(V(*receiver['anchor_center']),turn);add('AnchorPin','anchor_pin',pin_frame)
 add('AnchorCotter','anchor_cotter',pin_frame.multiply(App.Placement(V(0,details['cotter_cross_y_mm'],0),App.Rotation())))
 for index,f in enumerate(details['mount_seat_frames'],1):
  local=App.Placement(App.Matrix(*f));local.Base+=local.Rotation.multVec(V(0,0,-c['bottom_stock']-c['lock_stock']));add('BottomMountScrew'+str(index),'mount_screw',local)
 for index,d in enumerate(details['stops'],1):
  add('StopScrew'+str(index),'stop_screw',App.Placement(App.Matrix(*d['screw_frame'])))
  add('StopNut'+str(index),'stop_nut',App.Placement(App.Matrix(*d['nut_frame'])))
doc=App.newDocument('HighBrakeBottomStopStudy');root=doc.addObject('App::Part','Root');defs=doc.addObject('App::Part','Definitions');made={}
marks={'anchor_bracket':'M362','anchor_pin':'M363','anchor_cotter':'','bottom_stop':'M366','bottom_lock_plate':'MX77','mount_screw':'MX76','stop_screw':'M400','stop_nut':''}
for role,s in shapes.items():
 body=doc.addObject('PartDesign::Body','Def_'+role);defs.addObject(body);body.newObject('PartDesign::Feature','ReconstructedBottomStop').Shape=s
 metadata(body,SourcePartMark=marks[role],Representation='unqualified_prototype',ReconstructionStatus='Bottom-stop and anchor-retention hypothesis; physical interfaces and source review remain separate.');made[role]=body
for name,v in specs.items():
 link=doc.addObject('App::Link',name);root.addObject(link);link.setLink(made[v['role']]);link.LinkPlacement=App.Placement(App.Matrix(*v['frame']))
defs.Visibility=False;doc.recompute();native_out=out/'HighBrakeBottomStopStudy.FCStd';doc.saveAs(str(native_out));App.closeDocument(doc.Name)
checks=[]
def ck(name,passed,**kw):checks.append(dict(name=name,passed=bool(passed),**kw))
missing=old_bracket.cut(shapes['anchor_bracket']);added=shapes['anchor_bracket'].cut(old_bracket);outside=added.cut(envelopes['bracket_addition'])
ck('Retained M362 material preserved',not missing.Solids and not missing.Faces,missing_mm3=missing.Volume)
ck('Bracket additions bounded to proposed shelf and ribs',not outside.Solids and not outside.Faces,outside_mm3=outside.Volume)
# Conservative boxes select comparisons, which still use the full saved solids.
bounds={}
for key in m['definitions']:
 s=definition(key);b=s.BoundBox;bounds[key]=np.array(list(itertools.product([b.XMin,b.XMax],[b.YMin,b.YMax],[b.ZMin,b.ZMax])))
 if key!='Def_HighBrakeSupport_anchor_bracket':cache.pop(key,None)
boxes={}
for name,row in rows.items():
 f=np.array(row['frame']).reshape(4,4);pts=bounds[row['definition']]@f[:3,:3].T+f[:3,3];boxes[name]=(pts.min(axis=0),pts.max(axis=0))
replaced={h+'HighSpeedBrakeAnchorBracket' for h in ['Port','Starboard']};pairs=[]
def compare(n,one,k,two):
 common=one.common(two);vol=sum(abs(s.Volume) for s in common.Solids);valid=common.isNull() or common.isValid()
 pairs.append(dict(first=n,second=k,common_mm3=vol,valid_common=valid,passed=valid and vol<1e-5))
for name,s in installed.items():
 b=s.BoundBox;lo=np.array([b.XMin,b.YMin,b.ZMin]);hi=np.array([b.XMax,b.YMax,b.ZMax])
 for other,(low,high) in boxes.items():
  if other in replaced or not (np.all(low<=hi+1e-7) and np.all(high>=lo-1e-7)):continue
  compare(name,s,other,world(other))
  if len(pairs)%20==0:write(out/'interference_progress.json',pairs)
for one,two in itertools.combinations(installed,2):
 if installed[one].BoundBox.intersect(installed[two].BoundBox):compare(one,installed[one],two,installed[two])
ck('Prototype clears all new and retained material',all(v['passed'] for v in pairs),pairs=len(pairs),failed=[v for v in pairs if not v['passed']])
write(out/'material_checks.json',dict(passed=all(v['passed'] for v in pairs),pairs=pairs))
COLORS.update(Bracket=(.64,.46,.29),Stop=(.48,.55,.60),Hardware=(.67,.69,.70),Retained=(.51,.61,.68))
items=[]
for name,s in installed.items():
 role=specs[name]['role'];system='Bracket' if role=='anchor_bracket' else 'Stop' if role in ['bottom_stop','bottom_lock_plate'] else 'Hardware'
 items.append(dict(id=name,shape=s,target=SimpleNamespace(Shape=s),definition=role,system=system,representation='assembly'))
context=[]
for name in [h+'HighSpeedBrake'+v for h in ['Port','Starboard'] for v in ['LongBand','ShortBand','AnchorEnd']]:
 s=world(name);context.append(dict(id=name,shape=s,target=SimpleNamespace(Shape=s),definition=name,system='Retained',representation='assembly'))
shaded(items,out/'bottom_stop_isometric.svg',(1,-1,.45),'High-speed anchor pins and bottom stops | reconstruction trial',context=context)
inputs=[Path(__file__),a.controls.resolve(),H/'transmission_high_brake_stop_parts.py',H/'transmission_input_installation_parts.py',H/'transmission_high_brake_support_parts.py',packet/'controls.json',packet/'source_registration.json']
for f in inputs:shutil.copy2(f,out/('input_'+f.name))
write(out/'report.json',dict(passed=all(v['passed'] for v in checks),checks=checks,controls=c,receiver_controls=receiver,details=details,specs=specs,
 parent_native_sha256=r['native_sha256'],native_file=native_out.name,prototype_native_sha256=sha(native_out),source_registration_sha256=sha(packet/'source_registration.json'),
 input_hashes={str(f.relative_to(ROOT)):sha(f) for f in inputs},runtime=dict(freecad=App.Version(),occ=Part.OCC_VERSION),geometry_integrated=False,packet_complete=False,installation_qualified=False,limits=details['limits']))
print('Bottom-stop prototype:',len(shapes),'definitions,',len(specs),'occurrences;',len(pairs),'pairs; checks passed',all(v['passed'] for v in checks),flush=True)
for v in checks:
 if not v['passed']:print(v,flush=True)
