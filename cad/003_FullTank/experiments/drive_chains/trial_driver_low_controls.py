"""Corrected driver eye identities, real low-speed links and complete M574 rods."""
import argparse,math,copy,sys
from pathlib import Path
from control_rebuild_io_v2 import *
from driver_control_mount_parts import plate
from driver_control_linkage_parts_v3 import swing_link,clutch_lever
from driver_low_control_parts import parts as low_parts
V=App.Vector;X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)
p=argparse.ArgumentParser();p.add_argument('--controls',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();c=read(a.controls)
parent=Saved(ROOT/c['parent']);assert sha(parent.native)==c['parent_native_sha256'];assert read(parent.folder/'qualification.json')['local_static_checks_passed']
source=ROOT/c['source_review'];assert sha(source)==c['source_review_sha256'];assert all(sha(ROOT/f)==h for f,h in read(source)['source_hashes'].items())
prior=read(ROOT/c['foundation_prototype']/'report.json');fd=copy.deepcopy(parent.report['details']['foundation']);fc=fd['controls'];probe=read(ROOT/fc['floor_probe']);registration=read(ROOT/fc['registration'])
normal=V(*fd['floor_normal']);slope=-normal.x/normal.z;fp=V(*probe['floors']['hull_floor_1']['planes'][2]['point'])
def floor_z(x):return fp.z+slope*(x-fp.x)
low=V(*read(ROOT/fc['receiver_report'])['details']['receiving_interfaces']['PortLowIntermediateRocker']['front_pin_world_mm'])
future_z=c['swing_shaft_z']+c['future_low_relative'][2];span=49.5*25.4+2*25.4;future_x=low.x+math.sqrt(span**2-(future_z-low.z)**2)
rear=V(future_x-c['future_low_relative'][0],0,c['swing_shaft_z']);main=V(rear.x+registration['shaft_separation_mm'],0,c['main_shaft_z']);origin=V(rear.x,0,floor_z(rear.x))
oldrear=V(*fd['shafts']['Swing']['center_world_mm']);dx=rear.x-oldrear.x;shaft_delta=V(dx,0,rear.z-oldrear.z);foot_delta=V(dx,0,slope*dx)
shapes={};properties={};specs={};changed=[];groups={};identity=list(App.Placement().toMatrix().A)
def reuse(key):
    if key not in shapes:shapes[key]=parent.definition(key);properties[key]=parent.manifest['definitions'][key]['properties']
def carry(name,role='receiver'):
    row=parent.rows[name];reuse(row['definition']);specs[name]=dict(definition=row['definition'],frame=row['frame'],owner=row['owners'][-1],role=role)
def put(name,key,frame,owner,role,rs=None):
    specs[name]=dict(definition=key,frame=list(frame.toMatrix().A),owner=owner,role=role)
    if rs:specs[name]['source_records']=rs
for name in prior['new_occurrences']:
    carry(name,prior['specs'][name]['role']);specs[name].update({k:v for k,v in prior['specs'][name].items() if k=='source_records'})
    frame=pose(specs[name]['frame'])
    if name.startswith(('DriverMain','DriverSwing')):frame.Base+=shaft_delta
    elif not name.startswith('hull_floor'):frame.Base+=foot_delta
    specs[name]['frame']=list(frame.toMatrix().A)
for side,sign in [('Port',1),('Starboard',-1)]:
    key='Def_Driver'+side+'SupportPlate_MountStudy';shapes[key]=plate(fc,sign,registration['shaft_separation_mm'],rear.z-origin.z,main.z-origin.z,normal,slope);changed.append(key)
for name,data in probe['floors'].items():
    assert sha(ROOT/data['brep'])==data['sha256'];q=Part.Shape();q.read(str(ROOT/data['brep']));key=specs[name]['definition'];shapes[key]=q;changed.append(key)
for m in fd['mounts']:
    for k in ['floor_contact_world_mm','head_seat_world_mm','lock_seat_world_mm','nut_seat_world_mm']:m[k]=list(V(*m[k])+foot_delta)
    base=V(*m['floor_contact_world_mm']);m['floor']='hull_floor_2' if base.x<7262.528034682733 else 'hull_floor_1';key=specs[m['floor']]['definition'];shapes[key]=shapes[key].cut(Part.makeCylinder(6.5,8,base+normal,-normal)).removeSplitter()
for key in changed:
    properties[key]=dict(properties[key],ReconstructionStatus='Revised height/profile or original-floor bore pattern for complete driver swing-link depth. Mounting stock retained; exact seat plate form and low-link datum remain approximate.',ParameterUpdate='Regenerate trial_driver_low_controls.py from the saved linkage controls.')
for kind,center in [('Main',main),('Swing',rear)]:fd['shafts'][kind]['center_world_mm']=list(center)
fd['plate_origin_world_mm']=list(origin);fd['future_low_pin_world_mm']=[future_x,180.,future_z]
fc.update(main_shaft_z=c['main_shaft_z'],future_low_pin_z=future_z,future_low_pin_relative_to_swing=c['future_low_relative'])
key='Def_DriverSwingLink_M784';shapes[key]=swing_link(c);changed.append(key)
properties[key]=dict(SourcePartMark='M784',SourceRecords=['SNL:119:029','HB:113','SNL:plate6'],Representation='reconstruction_trial',ReconstructionStatus='Estimated three-eye swing-link profile. Printed four occurrences; dimensions and oil bore inferred from assembled source views.',ParameterUpdate='Regenerate trial_driver_low_controls.py')
swings={}
for branch,y in c['swing_lanes'].items():
    center=rear+Y*y;name=branch+'DriverSwingLink';put(name,key,App.Placement(center,App.Rotation()),'DriverRearSwing','swing_link')
    swings[branch]=dict(occurrence=name,pivot_world_mm=list(center),front_pin_world_mm=list(center+V(*c['swing_front_eye'])),rear_pin_world_mm=list(center+V(*c['swing_rear_eye'])))
groups['DriverFrontClutch']=dict(owner='DriverControlFoundation',frame=identity)
key='Def_DriverClutchLever_M772';shapes[key],bell=clutch_lever(c);changed.append(key)
properties[key]=dict(SourcePartMark='M772',SourceRecords=['SNL:116:015','HB:149'],Representation='reconstruction_trial',ReconstructionStatus='Source723.9mm radial hand reach and127mm bell radius; projected arm angle, outward tilt and static inclination estimated against corrected M784 eyes and actual nose.',ParameterUpdate='Regenerate trial_driver_low_controls.py')
clutchpivot=main+Y*c['swing_lanes']['PortClutch'];swingfront=V(*swings['PortClutch']['front_pin_world_mm']);pinspan=c['clutch_short_rod_length']+2*c['fork_pin_to_stock_offset']
def lever_pose(theta):return App.Placement(clutchpivot,App.Rotation(Y,90-theta))
def residual(theta):return (lever_pose(theta).multVec(bell)-swingfront).Length-pinspan
lo,hi=25.,70.;assert residual(lo)<0<residual(hi)
for _ in range(45):
    mid=(lo+hi)/2
    if residual(mid)<0:lo=mid
    else:hi=mid
theta=(lo+hi)/2;leverframe=lever_pose(theta);mainpin=leverframe.multVec(bell)
put('DriverClutchOperatingLever',key,leverframe,'DriverFrontClutch','lever')
template=pose(parent.rows['PortTrackBrakeJointFork']['frame']);joints={};rods={}
carry('PortClutchIntermediateRocker');intermediate=pose(parent.rows['PortClutchIntermediateRocker']['frame']).multVec(V(0,0,66.675));swingrear=V(*swings['PortClutch']['rear_pin_world_mm'])
for kind,mark,startpin,endpin,receivers in [('Short','M789B',swingfront,mainpin,('PortClutchDriverSwingLink','DriverClutchOperatingLever')),('Front','M576',intermediate,swingrear,('PortClutchIntermediateRocker','PortClutchDriverSwingLink'))]:
    direction=endpin-startpin;distance=direction.Length;direction.normalize();start=startpin+direction*c['fork_pin_to_stock_offset'];length=distance-2*c['fork_pin_to_stock_offset'];key='Def_DriverClutch'+kind+'Rod_'+mark
    shapes[key]=Part.makeCylinder(c['rod_radius'],length,V(),X);properties[key]=dict(SourcePartMark=mark,SourceRecords=['SNL:193:003' if kind=='Short' else 'SNL:193:037'],Representation='reconstruction_trial',ReconstructionStatus='Complete source320.675mm M789B stock.' if kind=='Short' else 'Unprinted complete M576 stock inferred from actual clutch receiver span; common family length must be reconciled for all five applications.',ParameterUpdate='Regenerate trial_driver_low_controls.py')
    if kind=='Front':changed.append(key)
    else:shapes[key]=parent.definition(key);properties[key]=parent.manifest['definitions'][key]['properties']
    put('DriverClutch'+kind+'Rod',key,App.Placement(start,App.Rotation(X,direction)),'DriverFrontClutch','rod')
    endpoints=[]
    for end,point,axis,receiver in [('Rear',startpin,direction,receivers[0]),('Forward',endpin,-direction,receivers[1])]:
        stem='DriverClutch'+kind+end+'Joint';frame=App.Placement(point,App.Rotation(axis,Y,axis.cross(Y),'XYZ'));groups[stem]=dict(owner='DriverFrontClutch',frame=list(frame.toMatrix().A))
        for role in ['Fork','Pin','Cotter','Nut']:
            row=parent.rows['PortTrackBrakeJoint'+role];reuse(row['definition']);put(stem+role,row['definition'],frame.multiply(template.inverse().multiply(pose(row['frame']))),stem,role.lower(),['SNL:129:002'] if role=='Nut' else ['SNL:86:022'] if role=='Fork' else None)
        endpoints.append(dict(stem=stem,pin_world_mm=list(point),rod_axis_world=list(axis),receiver=receiver))
    rods[kind]=dict(mark=mark,stock_length_mm=length,pin_span_mm=distance,stock_start_world_mm=list(start),axis_world=list(direction),endpoints=endpoints)
# Complete low-speed receiving links and their two source-length front rods.
low_shapes,ld=low_parts(c,registration['shaft_separation_mm']);low_groups={};low_records={}
marks={'Def_DriverLowSuspension_M760':('M760','SNL:119:033'),'Def_DriverLowConnecting_M762':('M762','SNL:119:035'),'Def_DriverLowBrake_M763':('M763','SNL:119:030'),'Def_DriverLowSuspensionPin_M761':('M761','SNL:137:016'),'Def_DriverLowLinkWasher_SH220A':('SH220A','SNL:272:001'),'Def_DriverLowSuspensionKeeper':('3/16x1-1/4 split pin','SNL:137:017')}
for key,q in low_shapes.items():
    shapes[key]=q;mark,locator=marks[key];properties[key]=dict(SourcePartMark=mark,SourceRecords=[locator,'HB:113','SNL:plate6'],Representation='reconstruction_trial',ReconstructionStatus='Source-counted low-speed linkage; profile, pin dimensions and axial stack are explicit estimates. M762 front selector coupling remains unfinished.',ParameterUpdate='Regenerate trial_driver_low_controls.py with low_controls01.json')
groups['DriverLowControls']=dict(owner='DriverControlFoundation',frame=identity)
keeper_rotation=App.Rotation(-Y,X,Z,'XYZ')
for side,sign in [('Port',1),('Starboard',-1)]:
    base=rear+Y*(sign*180);stem=side+'DriverLow';group=stem+'Branch';groups[group]=dict(owner='DriverLowControls',frame=identity)
    knee=base+V(*ld['knee']);receiver=base+V(*ld['rod']);selector=base+V(*ld['connecting_front'])
    for suffix,key in [('Suspension','Def_DriverLowSuspension_M760'),('Connecting','Def_DriverLowConnecting_M762'),('Brake','Def_DriverLowBrake_M763')]:put(stem+suffix,key,App.Placement(base,App.Rotation()),group,'low_link')
    put(stem+'Pin','Def_DriverLowSuspensionPin_M761',App.Placement(knee,App.Rotation()),group,'pin')
    put(stem+'Washer','Def_DriverLowLinkWasher_SH220A',App.Placement(knee+Y*c['washer_seat_y'],App.Rotation()),group,'washer')
    put(stem+'Keeper','Def_DriverLowSuspensionKeeper',App.Placement(knee+Y*c['pin_keeper_y'],keeper_rotation),group,'keeper')
    receiving=side+'LowIntermediateRocker';carry(receiving);intermediate_pin=pose(parent.rows[receiving]['frame']).multVec(V(0,0,66.675))
    direction=receiver-intermediate_pin;distance=direction.Length;direction.normalize();length=49.5*25.4;assert abs(distance-length-50.8)<1e-7
    key='Def_DriverLowFrontRod_M574'
    if key not in shapes:
        shapes[key]=Part.makeCylinder(9.525,length,V(),X);properties[key]=dict(SourcePartMark='M574',SourceRecords=['SNL:194:037'],Representation='reconstruction_trial',ReconstructionStatus='Complete source49-1/2in stock between actual M763 and retained intermediate receivers; source length datum interpreted as rod stock.',ParameterUpdate='Regenerate trial_driver_low_controls.py')
    start=intermediate_pin+direction*25.4;put(stem+'Rod',key,App.Placement(start,App.Rotation(X,direction)),group,'rod')
    ends=[]
    for end,point,axis,receiving_part in [('Rear',intermediate_pin,direction,receiving),('Forward',receiver,-direction,stem+'Brake')]:
        joint=stem+end+'Joint';frame=App.Placement(point,App.Rotation(axis,Y,axis.cross(Y),'XYZ'));groups[joint]=dict(owner=group,frame=list(frame.toMatrix().A))
        for role in ['Fork','Pin','Cotter','Nut']:
            row=parent.rows['PortTrackBrakeJoint'+role];reuse(row['definition']);put(joint+role,row['definition'],frame.multiply(template.inverse().multiply(pose(row['frame']))),joint,role.lower())
        ends.append(dict(stem=joint,pin_world_mm=list(point),rod_axis_world=list(axis),receiver=receiving_part))
    low_records[side]=dict(base_world_mm=list(base),knee_world_mm=list(knee),rod_pin_world_mm=list(receiver),open_selector_connection_world_mm=list(selector),stock_start_world_mm=list(start),axis_world=list(direction),stock_length_mm=length,pin_span_mm=distance,endpoints=ends)
# Existing joint groups keep their original datums; updated link placements are
# resolved against those parent frames during full integration. Physical world
# frames, including all complete pins and retained intermediate eyes, are explicit.
groups={n:v for n,v in groups.items() if n not in parent.manifest['assemblies']}
inputs=[Path(__file__),a.controls,source,ROOT/c['foundation_prototype']/'report.json',ROOT/fc['floor_probe'],ROOT/fc['registration'],ROOT/fc['receiver_report'],parent.folder/'report.json',parent.folder/'isolated/manifest.json']
inputs += [ROOT/v['brep'] for v in probe['floors'].values()]
inputs += sorted({Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).resolve().parent==H and str(m.__file__).endswith('.py')})
details=dict(controls=c,foundation=fd,low_speed=low_records,low_parts=ld,swings=swings,clutch_hand_angle_degrees=theta,clutch_pivot_world_mm=list(clutchpivot),clutch_bell_pin_world_mm=list(mainpin),rods=rods,scope='Real M760/M762/M763 low-speed links, complete M761/SH220A retention and two source-length M574 rods. Corrected shared M784 eyes and declared driver/clutch revisions; M762 front selector coupling remains unfinished.')
trial(a.output,parent,shapes,specs,properties,details,inputs,changed_definitions=changed,assembly_groups=groups)
print('Saved corrected driver controls with actual low-speed receivers and complete source-stock rods.',flush=True)
