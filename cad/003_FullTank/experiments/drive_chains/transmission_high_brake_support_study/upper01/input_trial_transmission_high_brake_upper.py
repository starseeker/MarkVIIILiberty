"""Saved upper brake-stop prototype against retained band and full powertrain context."""
import argparse,itertools,shutil,sys,traceback
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
from transmission_high_brake_upper_parts import parts
V=App.Vector
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--controls',type=Path,default=H/'transmission_high_brake_support_study/upper_controls.json');a=p.parse_args()
out=a.output.resolve();assert not out.exists();out.mkdir(parents=True)
packet=H/'transmission_high_brake_support_study';parent=packet/'integrated_bottom01';r=read(parent/'report.json');m=read(parent/'isolated/manifest.json');native=parent/r['native_file']
assert sha(native)==r['native_sha256']==m['native_sha256'];rows={v['name']:v for v in m['occurrences']};cache={}
inputs=[Path(__file__),a.controls.resolve(),H/'transmission_high_brake_upper_parts.py',H/'transmission_high_brake_stop_parts.py',H/'transmission_high_brake_support_parts.py',packet/'controls.json',packet/'source_registration.json']
for f in inputs:shutil.copy2(f,out/('input_'+f.name))
write(out/'inputs.json',dict(parent_native_sha256=sha(native),input_hashes={str(f.relative_to(ROOT)):sha(f) for f in inputs}))
def definition(key):
 if key not in cache:
  d=m['definitions'][key];assert sha(d['brep_path'])==d['brep_sha256'];s=Part.Shape();s.read(d['brep_path']);cache[key]=s
 return cache[key].copy()
def world(name):
 row=rows[name];s=definition(row['definition']);s.Placement=App.Placement(App.Matrix(*row['frame']));return s
casekey='Def_TransmissionCore_bevel_case';casename='CenterTransmissionCore_bevel_case'
oldparent=H/'transmission_high_brake_mechanism_study/trial01';om=read(oldparent/'isolated/manifest.json');od=om['definitions'][casekey];assert sha(od['brep_path'])==od['brep_sha256'];originalcase=Part.Shape();originalcase.read(od['brep_path'])
sharedkeys=dict(lock_plate='Def_HighBrakeSupport_anchor_lock_plate',mount_screw='Def_HighBrakeSupport_mount_screw',stop_screw='Def_HighBrakeStops_stop_screw',stop_nut='Def_HighBrakeStops_stop_nut')
base=App.Placement(V(*r['interfaces']['PortHighSpeedBrake']['center_world_mm']),App.Rotation());target_names=['PortHighSpeedBrake'+v for v in ['LongBand','ShortBand','AnchorEnd']]
selected=target_names+[casename]+[v['name'] for v in m['occurrences'] if v['definition'] in sharedkeys.values()]
validate_native_bindings(dict(native_file=str(native),render_occurrences=selected,landmarks=[]),m)
targets=[]
for name in target_names:
 s=world(name);s.Placement=base.inverse().multiply(s.Placement);targets.append(s)
c=read(a.controls)['controls'];receiver=r['receiver_controls'];shared={k:definition(v) for k,v in sharedkeys.items()};shared['stop_screw_radius']=r['controls']['stop_screw_diameter']/2
try:shapes,details,envelopes=parts(c,receiver,originalcase,shared,targets)
except Exception:
 write(out/'construction_failure.json',dict(traceback=traceback.format_exc(),passed=False));raise
for name,s in {**shapes,**envelopes}.items():s.exportBrep(str(out/(name+'.brep')))
specs={};installed={}
casepose=App.Placement(App.Matrix(*rows[casename]['frame']));s=shapes['case'].copy();s.Placement=casepose;installed['Case']=s;specs['Case']=dict(role='case',frame=list(casepose.toMatrix().A))
for hand in ['Port','Starboard']:
 base=App.Placement(V(*r['interfaces'][hand+'HighSpeedBrake']['center_world_mm']),App.Rotation())
 def add(suffix,role,local):
  name=hand+suffix;pose=base.multiply(local);s=shapes[role].copy();s.Placement=pose;specs[name]=dict(role=role,frame=list(pose.toMatrix().A),local_frame=list(local.toMatrix().A));installed[name]=s
 for suffix,role in [('TopStop','top_stop'),('BackStop','back_stop')]:add(suffix,role,App.Placement())
 for suffix,role,field in [('Clip','clip','clip_frame'),('UpperLockPlate','lock_plate','lock_frame'),('StopScrew','stop_screw','stop_screw_frame'),('StopNut','stop_nut','stop_nut_frame')]:add(suffix,role,App.Placement(App.Matrix(*details[field])))
 for index,f in enumerate(details['mount_seat_frames'],1):
  local=App.Placement(App.Matrix(*f));local.Base+=local.Rotation.multVec(V(0,0,details['upper_clamped_stock_mm']));add('UpperMountScrew'+str(index),'mount_screw',local)
doc=App.newDocument('HighBrakeUpperStopStudy');root=doc.addObject('App::Part','Root');defs=doc.addObject('App::Part','Definitions');made={}
marks={'case':'','top_stop':'M399','back_stop':'M398','clip':'M365','lock_plate':'MX61','mount_screw':'MX60','stop_screw':'M400','stop_nut':''}
for role,s in shapes.items():
 body=doc.addObject('PartDesign::Body','Def_'+role);defs.addObject(body);body.newObject('PartDesign::Feature','ReconstructedUpperStop').Shape=s
 metadata(body,SourcePartMark=marks[role],Representation='unqualified_prototype',ReconstructionStatus='Upper-stop reconstruction hypothesis; shared hardware preserved; independent interfaces and source review remain separate.');made[role]=body
for name,v in specs.items():
 link=doc.addObject('App::Link',name);root.addObject(link);link.setLink(made[v['role']]);link.LinkPlacement=App.Placement(App.Matrix(*v['frame']))
defs.Visibility=False;doc.recompute();native_out=out/'HighBrakeUpperStopStudy.FCStd';doc.saveAs(str(native_out));App.closeDocument(doc.Name)
checks=[]
def ck(name,passed,**kw):checks.append(dict(name=name,passed=bool(passed),**kw))
oldcase=definition(casekey)
for label,delta in [('removed',oldcase.cut(shapes['case'])),('added',shapes['case'].cut(oldcase))]:
 outside=delta.cut(envelopes['upper_hole_revision']);ck('Case '+label+' material bounded to upper hole revision',not outside.Solids and not outside.Faces,outside_mm3=outside.Volume,delta_mm3=delta.Volume)
# Select neighbors by conservative boxes; compare complete saved material.
bounds={}
for key in m['definitions']:
 s=definition(key);b=s.BoundBox;bounds[key]=np.array(list(itertools.product([b.XMin,b.XMax],[b.YMin,b.YMax],[b.ZMin,b.ZMax])))
 if key!=casekey:cache.pop(key,None)
boxes={}
for name,row in rows.items():
 f=np.array(row['frame']).reshape(4,4);pts=bounds[row['definition']]@f[:3,:3].T+f[:3,3];boxes[name]=(pts.min(axis=0),pts.max(axis=0))
pairs=[]
def compare(n,one,k,two):
 common=one.common(two);vol=sum(abs(s.Volume) for s in common.Solids);valid=common.isNull() or common.isValid();pairs.append(dict(first=n,second=k,common_mm3=vol,valid_common=valid,passed=valid and vol<1e-5))
for name,s in installed.items():
 b=s.BoundBox;lo=np.array([b.XMin,b.YMin,b.ZMin]);hi=np.array([b.XMax,b.YMax,b.ZMax])
 for other,(low,high) in boxes.items():
  if other==casename or not (np.all(low<=hi+1e-7) and np.all(high>=lo-1e-7)):continue
  compare(name,s,other,world(other))
  if len(pairs)%20==0:write(out/'interference_progress.json',pairs)
for one,two in itertools.combinations(installed,2):
 if installed[one].BoundBox.intersect(installed[two].BoundBox):compare(one,installed[one],two,installed[two])
ck('Prototype clears all new and retained material',all(v['passed'] for v in pairs),pairs=len(pairs),failed=[v for v in pairs if not v['passed']]);write(out/'material_checks.json',dict(passed=all(v['passed'] for v in pairs),pairs=pairs))
write(out/'report.json',dict(passed=all(v['passed'] for v in checks),checks=checks,controls=c,receiver_controls=receiver,details=details,specs=specs,shared_definitions=sharedkeys,
 parent_native_sha256=r['native_sha256'],original_case_parent_sha256=om['native_sha256'],native_file=native_out.name,prototype_native_sha256=sha(native_out),source_registration_sha256=sha(packet/'source_registration.json'),
 input_hashes={str(f.relative_to(ROOT)):sha(f) for f in inputs},runtime=dict(freecad=App.Version(),occ=Part.OCC_VERSION),geometry_integrated=False,packet_complete=False,installation_qualified=False,limits=details['limits']))
COLORS.update(Top=(.65,.50,.29),Back=(.45,.60,.55),Hardware=(.67,.69,.70),Retained=(.51,.61,.68))
items=[]
for name,s in installed.items():
 if name=='Case':continue
 role=specs[name]['role'];system='Top' if role=='top_stop' else 'Back' if role=='back_stop' else 'Hardware'
 items.append(dict(id=name,shape=s,target=SimpleNamespace(Shape=shapes[role]),definition=role,system=system,representation='assembly'))
context=[]
for name in [h+'HighSpeedBrake'+v for h in ['Port','Starboard'] for v in ['LongBand','ShortBand','AnchorEnd']]:
 s=world(name);context.append(dict(id=name,shape=s,target=SimpleNamespace(Shape=s),definition=name,system='Retained',representation='assembly'))
shaded(items,out/'upper_stop_isometric.svg',(1,-1,.45),'High-speed top and back stops with M365 clips | reconstruction trial',context=context)
print('Upper-stop prototype:',len(shapes),'definitions,',len(specs),'occurrences;',len(pairs),'pairs; checks passed',all(v['passed'] for v in checks),flush=True)
for v in checks:
 if not v['passed']:print(v,flush=True)
