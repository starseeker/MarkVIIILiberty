"""Source-bound SH944/M581 trial; nothing accepted by construction."""
import argparse,sys,math
from pathlib import Path
from control_rebuild_io_v2 import *
from control_rebuild_clutch_swing_parts_v2 import parts
V=App.Vector;X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)
p=argparse.ArgumentParser();p.add_argument('--controls',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();c=read(a.controls)
parent=Saved(ROOT/c['parent']);assert sha(parent.native)==c['parent_native_sha256'];source=ROOT/c['source_review'];assert sha(source)==c['source_review_sha256'];assert all(sha(ROOT/f)==v for f,v in read(source)['source_hashes'].items())
# Complete center-rod stock constrains the previously estimated swing-bracket X.
center_receiver='PortClutchIntermediateRocker'
center_front=pose(parent.rows[center_receiver]['frame']).multVec(V(0,0,101.6))
def center_wire(station):
 rear=V(station,c['center_y']+c['link_y_offsets'][1],c['journal_z']-c['long_arm'])
 distance=c['center_rod_straight_pin_distance'];points=[rear+X*25.4,rear+X*distance,center_front-X*distance,center_front-X*25.4]
 curve=Part.BezierCurve();u,v=points[1:3];handle=(v.x-u.x)/3;curve.setPoles([u,u+X*handle,v-X*handle,v])
 return Part.Wire([Part.makeLine(points[0],points[1]),curve.toShape(),Part.makeLine(points[2],points[3])]),rear,points
lo,hi=3400.,3800.
assert center_wire(lo)[0].Length>c['center_rod_length_mm']>center_wire(hi)[0].Length
for _ in range(45):
 mid=(lo+hi)/2
 if center_wire(mid)[0].Length>c['center_rod_length_mm']:lo=mid
 else:hi=mid
c['station_x']=(lo+hi)/2
shapes=parts(c);specs={};properties={};groups={};details={};curves={};changed=[]
records={'Bracket':('SH944A',['SNL:37:008']),'Shaft':('SH944D',['SNL:211:032']),'Key':('Woodruff No.15',['SNL:115:013']),'Short':('SH944B',['SNL:119:026']),'Long':('SH944C',['SNL:119:025']),'MountBolt':('1/2 x 1-3/4 inch',['SNL:31:009']),'ClampBolt':('1/2 x 2-1/2 inch',['SNL:31:011'])}
for kind,(mark,rs) in records.items():properties['Def_ClutchSwing'+kind+'_Redo']=dict(SourcePartMark=mark,SourceRecords=rs,Representation='reconstruction_trial',ReconstructionStatus='Estimated SH944 topology and dimensions; source bolt lengths retained. See clutch_swing_source_review04.json.',ParameterUpdate='Regenerate trial_control_rebuild_clutch_swing_v5.py from saved controls.')
def carry(n):
 row=parent.rows[n];key=row['definition'];shapes.setdefault(key,parent.definition(key));properties[key]=parent.manifest['definitions'][key]['properties'];specs[n]=dict(definition=key,frame=row['frame'],owner=row['owners'][-1],role='receiver')
def put(n,key,f,owner,role,rs=None):
 specs[n]=dict(definition=key,frame=list(f.toMatrix().A),owner=owner,role=role)
 if rs:specs[n]['source_records']=rs

def reuse(key):shapes[key]=parent.definition(key);properties[key]=parent.manifest['definitions'][key]['properties']
identity=list(App.Placement().toMatrix().A);groups['ClutchSwingControls']=dict(owner='Root',frame=identity)
base=V(c['station_x'],c['center_y'],c['base_z']);pivot=V(base.x,base.y,c['journal_z']);f=App.Placement(base,App.Rotation());owner='ClutchSwingControls'
put('ClutchSwingBracket','Def_ClutchSwingBracket_Redo',f,owner,'bracket')
put('ClutchSwingShaft','Def_ClutchSwingShaft_Redo',App.Placement(pivot,App.Rotation()),owner,'shaft')
for key in ['Def_EngineSuspension_half_nut','Def_EngineSuspension_half_lock']:reuse(key)
beam_name='hull_floor_6';carry(beam_name);beam=parent.world(beam_name);mounts=[]
# Four source bolts pass through actual floor6; only their receiving holes change.
for i,(x,y) in enumerate(( (x,y) for x in [-20,20] for y in [-65,65]),1):
 top=base+V(x,y,c['base_stock']);seat_z=base.z-6;station=V(top.x,top.y,seat_z)
 beam=beam.cut(Part.makeCylinder(6.5,c['base_stock']+8,top+Z,-Z))
 for role,key,point in [('Bolt','Def_ClutchSwingMountBolt_Redo',top),('Lock','Def_EngineSuspension_half_lock',station),('Nut','Def_EngineSuspension_half_nut',station-Z*3.175)]:
  put('ClutchSwingMount'+str(i)+role,key,App.Placement(point,App.Rotation(Z,-Z)),owner,role.lower(),['SNL:31:009'])
 mounts.append(dict(index=i,head_seat_world_mm=list(top),lock_seat_world_mm=list(station),nut_seat_world_mm=list(station-Z*3.175),source_length_mm=44.45))
beam.Placement=pose(parent.rows[beam_name]['frame']).inverse().multiply(beam.Placement);shapes[parent.rows[beam_name]['definition']]=Part.makeCompound([beam]);changed.append(parent.rows[beam_name]['definition'])
for i,(kind,dy) in enumerate(zip(['Short','Long'],c['link_y_offsets']),1):
 frame=App.Placement(pivot+Y*dy,App.Rotation());put('ClutchSwing'+kind+'Link','Def_ClutchSwing'+kind+'_Redo',frame,owner,'link')
 put('ClutchSwingKey'+str(i),'Def_ClutchSwingKey_Redo',frame,owner,'key')
 for role,key,z in [('Bolt','Def_ClutchSwingClampBolt_Redo',20),('Lock','Def_EngineSuspension_half_lock',-20),('Nut','Def_EngineSuspension_half_nut',-23.175)]:
  put('ClutchSwing'+kind+'Clamp'+role,key,App.Placement(frame.multVec(V(30,0,z)),App.Rotation(Z,-Z)),owner,role.lower(),['SNL:31:011'])
# End families are kept distinct. SH953E/F from the existing auxiliary joint;
# M569C/M568C from the accepted control fork family. Both use source 3/4in nuts.
carry('ClutchSupport_AuxLever1');rearframe=pose(parent.rows['ClutchSupport_AuxLever1']['frame']);rear=rearframe.multVec(V(0,0,-65));front=pivot+V(0,c['link_y_offsets'][0],-c['short_arm'])
angle=math.radians(c['rear_fork_down_pitch_deg']);rearaxis=V(math.cos(angle),0,-math.sin(angle))
for end,point,axis,template_name,roles in [('Rear',rear,rearaxis,'ClutchSupport_AuxFork',{'Fork':'ClutchSupport_AuxFork','Pin':'ClutchSupport_AuxForkPin','Cotter':'ClutchSupport_AuxForkCotter'}),('Forward',front,-X,'PortTrackBrakeJointFork',{r:'PortTrackBrakeJoint'+r for r in ['Fork','Pin','Cotter']})]:
 stem='ClutchRearRod'+end+'Joint';frame=App.Placement(point,App.Rotation(axis,Y,axis.cross(Y),'XYZ'));groups[stem]=dict(owner=owner,frame=list(frame.toMatrix().A));template=pose(parent.rows[template_name]['frame'])
 for role,n in roles.items():
  row=parent.rows[n];reuse(row['definition']);put(stem+role,row['definition'],frame.multiply(template.inverse().multiply(pose(row['frame']))),stem,role.lower())
 row=parent.rows['PortTrackBrakeJointNut'];reuse(row['definition']);nf=pose(parent.rows['PortTrackBrakeJointFork']['frame']).inverse().multiply(pose(row['frame']))
 if end=='Rear':nf.Base+=X*(55-44.45)
 put(stem+'Nut',row['definition'],frame.multiply(nf),stem,'nut',['SNL:193:008'])
 details[end]=dict(pin_world_mm=list(point),fork_axis_world=list(axis),fork_face_mm=55 if end=='Rear' else 44.45,receiver='ClutchSupport_AuxLever1' if end=='Rear' else 'ClutchSwingShortLink')
start=rear+rearaxis*(55-19.05);end=front-X*25.4
points=[start,rear+rearaxis*c['rear_straight_pin_distance'],V(c['outboard_transition_end_x'],front.y,710),V(2830,front.y,710),V(3120,front.y,front.z),end];edges=[]
for i,(u,v) in enumerate(zip(points,points[1:])):
 if i in [1,3]:
  curve=Part.BezierCurve();handle=(v.x-u.x)/3;curve.setPoles([u,u+(rearaxis if i==1 else X)*handle,v-X*handle,v]);edges.append(curve.toShape())
 else:edges.append(Part.makeLine(u,v))
wire=Part.Wire(edges);rod=wire.makePipeShell([Part.Wire([Part.makeCircle(9.525,start,rearaxis)])],True,False);rod.translate(-start);rod=Part.makeCompound([rod]);key='Def_ClutchRearRod_Redo';shapes[key]=rod
properties[key]=dict(SourcePartMark='M581',SourceRecords=['SNL:193:007'],Representation='reconstruction_trial',ReconstructionStatus='Estimated complete installed route between SH953E and M569C joints; 19.05mm solid stock and engagement.',ParameterUpdate='Regenerate trial_control_rebuild_clutch_swing_v5.py')
put('ClutchRearRod',key,App.Placement(start,App.Rotation()),owner,'rod');curves['ClutchRearRod']=wire
# SH229A center rod: one complete source-length part, two proper M569C joints.
carry(center_receiver)
wire,center_rear,center_points=center_wire(c['station_x']);start=center_points[0]
rod=wire.makePipeShell([Part.Wire([Part.makeCircle(9.525,start,X)])],True,False);rod.translate(-start);rod=Part.makeCompound([rod]);key='Def_ClutchCenterRod_Redo';shapes[key]=rod
properties[key]=dict(SourcePartMark='SH229A',SourceRecords=['SNL:192:020'],Representation='reconstruction_trial',ReconstructionStatus='Printed93in interpreted as stock centerline length. Complete estimated installed form, source M569C forks both ends.',ParameterUpdate='Regenerate trial_control_rebuild_clutch_swing_v5.py')
groups['ClutchCenterControl']=dict(owner=owner,frame=identity);put('ClutchCenterRod',key,App.Placement(start,App.Rotation()),'ClutchCenterControl','rod');curves['ClutchCenterRod']=wire
joints={};template=pose(parent.rows['PortTrackBrakeJointFork']['frame'])
for end,point,axis,receiver in [('Rear',center_rear,X,'ClutchSwingLongLink'),('Intermediate',center_front,-X,center_receiver)]:
 stem='ClutchCenterRod'+end+'Joint';frame=App.Placement(point,App.Rotation(axis,Y,axis.cross(Y),'XYZ'));groups[stem]=dict(owner='ClutchCenterControl',frame=list(frame.toMatrix().A))
 for role in ['Fork','Pin','Cotter','Nut']:
  row=parent.rows['PortTrackBrakeJoint'+role];reuse(row['definition']);put(stem+role,row['definition'],frame.multiply(template.inverse().multiply(pose(row['frame']))),stem,role.lower(),['SNL:192:021'] if role=='Nut' else ['SNL:86:022'] if role=='Fork' else None)
 joints[end]=dict(receiver=receiver,center_world_mm=list(point),rod_axis_world=list(axis),pin_axis_world=list(Y))
details['center_rod']=dict(source_mark='SH229A',printed_length_inches=93,stock_centerline_length_mm=wire.Length,joints=joints,path_points_world_mm=[list(p) for p in center_points],derived_swing_station_x_mm=c['station_x'])
inputs=[Path(__file__),a.controls,source,parent.folder/'report.json',parent.folder/'isolated/manifest.json']
inputs+=sorted({Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).resolve().parent==H and str(m.__file__).endswith('.py')})
details.update(controls=c,mounts=mounts,pivot_world_mm=list(pivot),forward_link_receiver_world_mm=list(pivot+V(0,c['link_y_offsets'][1],-c['long_arm'])),rod_path_points_world_mm=[list(p) for p in points],rod_length_mm=wire.Length)
trial(a.output,parent,shapes,specs,properties,details,inputs,curves=curves,changed_definitions=changed,assembly_groups=groups)
print('Saved SH944/M581 trial; independent validation required.',flush=True)
