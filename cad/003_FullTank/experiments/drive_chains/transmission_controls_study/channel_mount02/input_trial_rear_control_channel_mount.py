"""Build four complete M4130 attachments and drilled receivers in an isolated assembly."""
import argparse
from pathlib import Path
import shutil
import sys
H=Path(__file__).resolve().parent;STAGE=H.parents[1];ROOT=H.parents[3]
sys.path[:0]=[str(H),str(STAGE)]
import FreeCAD as App
import Part
from lib.evidence import read,write,sha
from lib.cad_build import metadata
from lib.camera_review import validate_native_bindings
from rear_control_channel_mount_parts import parts
V=App.Vector

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--controls',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
out=a.output.resolve();assert not out.exists();out.mkdir(parents=True)
packet=H/'transmission_controls_study';parent=packet/'us_nuts01';m=read(parent/'isolated/manifest.json');pr=read(parent/'report.json');native=parent/pr['native_file'];assert sha(native)==m['native_sha256']
configuration=read(a.controls);c=configuration['controls'];assert configuration['source_review_sha256']==sha(packet/'channel_mount_source_review01.json')
for path,digest in read(packet/'channel_sources01/sources.json')['source_hashes'].items():assert sha(ROOT/path)==digest
rows={v['name']:v for v in m['occurrences']};floor_row=rows['hull_floor_7']
validate_native_bindings(dict(native_file=str(native),render_occurrences=['hull_floor_7','PortHighSpeedBrakeControlNut'],landmarks=[]),m)
def load(key):
    d=m['definitions'][key];assert sha(d['brep_path'])==d['brep_sha256'];s=Part.Shape();s.read(d['brep_path']);return s
floor_pose=App.Placement(App.Matrix(*floor_row['frame']))
shapes,details,tools=parts(c,load(floor_row['definition']),floor_pose,load(c['shared_nut_definition']))
doc=App.newDocument('RearControlChannelMount');root=doc.addObject('App::Part','Root');library=doc.addObject('App::Part','Definitions')
marks=dict(channel='M4128',cleat='M4130',bolt='3/4 x 2 inch U.S. Standard bolt',lock='3/4 inch lock washer',nut='3/4 inch plain U.S. Standard nut',rivet='1/2 x 2 inch button-head rivet',floor='Existing hull floor7 with four added mounting holes')
records=dict(channel=['SNL:63:010'],cleat=['SNL:65:023','SNL:63:006'],bolt=['SNL:33:007'],lock=['SNL:33:007'],nut=['SNL:33:007'],rivet=['SNL:170:006'],floor=['SNL:33:007'])
source_rows=read(packet/'channel_sources01/sources.json')['source_records'];made={}
for role,s in shapes.items():
    body=doc.addObject('PartDesign::Body','Def_ChannelMount_'+role);library.addObject(body);body.newObject('PartDesign::Feature','ReconstructedChannelMount').Shape=s
    ids=sorted({pid for row in source_rows if row['record_id'] in records[role] for pid in row['part_ids']}) if role in ['channel','cleat','bolt','rivet'] else []
    metadata(body,SourcePartMark=marks[role],SourceRecords=records[role],SurveyIds=ids,Representation='unqualified_mount_prototype',ParameterUpdate='Regenerate from channel_mount_controls01.json',ReconstructionStatus='Explicit cleat/stock/head and mounting-station approximation; two M4129 and remaining controls still pending.')
    made[role]=body;s.exportBrep(str(out/(role+'.brep')))
group=doc.addObject('App::Part','RearControlChannel');root.addObject(group);group.Placement=App.Placement(V(*c['channel']['placement']),App.Rotation())
specs={}
def occurrence(name,role,owner,local):
    link=doc.addObject('App::Link',name);owner.addObject(link);link.setLink(made[role]);link.LinkPlacement=local
    metadata(link,SourceRecords=records[role],Coverage='reconstruction_trial')
    world=owner.getGlobalPlacement().multiply(local)
    specs[name]=dict(role=role,owner=owner.Name,frame=list(world.toMatrix().A),local_frame=list(local.toMatrix().A))
occurrence('RearControlChannelStock','channel',group,App.Placement())
occurrence('hull_floor_7','floor',root,floor_pose)
rotation=App.Rotation(V(1,0,0),180);axial=App.Rotation(V(0,1,0),90)
for i,station in enumerate(c['cleat']['stations_y'],1):
    name='RearChannelLeftCleat'+str(i);g=doc.addObject('App::Part',name+'Mount');group.addObject(g);g.Placement=App.Placement(V(-c['channel']['width']/2,station,0),App.Rotation())
    occurrence(name,'cleat',g,App.Placement());cl=c['cleat'];x,y=cl['bolt_x'],cl['bolt_y']
    occurrence(name+'Bolt','bolt',g,App.Placement(V(x,y,cl['stock']),rotation))
    occurrence(name+'LockWasher','lock',g,App.Placement(V(x,y,-c['floor_thickness']),rotation))
    occurrence(name+'Nut','nut',g,App.Placement(V(x,y,-c['floor_thickness']-c['lock']['thickness']),rotation))
    for j,ry in enumerate(cl['rivet_y'],1):
        occurrence(name+'Rivet'+str(j),'rivet',g,App.Placement(V(-cl['stock'],ry,cl['rivet_z']),axial))
library.Visibility=False;doc.recompute();saved=out/'RearControlChannelMount.FCStd';doc.saveAs(str(saved));App.closeDocument(doc.Name)
for key,s in tools.items():s.exportBrep(str(out/(key+'.brep')))
inputs=[Path(__file__),H/'rear_control_channel_mount_parts.py',H/'rear_control_channel_stock.py',H/'transmission_frame_joint_parts.py',H/'transmission_brake_stop_parts.py',a.controls.resolve(),packet/'channel_mount_source_review01.json',packet/'channel_sources01/sources.json']
for f in inputs:shutil.copy2(f,out/('input_'+f.name))
write(out/'report.json',dict(native_file=saved.name,native_sha256=sha(saved),parent_native=str(native.relative_to(ROOT)),parent_native_sha256=sha(native),parent_manifest_sha256=sha(parent/'isolated/manifest.json'),controls=c,details=details,specs=specs,record_ids=records,input_hashes={str(f.relative_to(ROOT)):sha(f) for f in inputs},source_floor_definition=floor_row['definition'],source_floor_sha256=m['definitions'][floor_row['definition']]['brep_sha256'],shared_nut_definition=c['shared_nut_definition'],shared_nut_sha256=m['definitions'][c['shared_nut_definition']]['brep_sha256'],new_physical_occurrences=29,prototype_physical_occurrences=30,prototype_definition_count=7,geometry_integrated=False,channel_complete=False,historical_geometry_qualified=False,installation_qualified=False))
print('Saved29 new mounting occurrences plus drilled floor receiver;7 prototype definitions.',flush=True)
