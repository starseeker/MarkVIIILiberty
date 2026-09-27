"""M641 mounts and complete M578 rear foot connections, including real floor holes."""
import argparse
import json
from pathlib import Path
from control_rebuild_io_v2 import App,Part,H,ROOT,Saved,pose,trial,read,sha
from control_rebuild_center_foot_parts_v2 import parts
V=App.Vector
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--controls',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args();c=read(a.controls);parent=Saved(ROOT/c['parent'])
assert sha(parent.native)==c['parent_native_sha256']
source=ROOT/c['source_review'];assert sha(source)==c['source_review_sha256']
assert all(sha(ROOT/f)==h for f,h in read(source)['source_hashes'].items())
shapes,details=parts(c);specs={};properties={};joints={};groups={}
identities={
 'Def_CenterFootBracket_Redo':('M641',['SNL:37:039']),
 'Def_ControlRocker_Redo':('M640',['SNL:116:020']),
 'Def_CenterFootRivet_Redo':('11/16 x 1-1/2 inch button-head rivet',['SNL:172:002']),
 'Def_CenterFootKeeper_Redo':('1/4 x 1-3/4 inch split pin',['SNL:37:040','SNL:141:015']),
 'Def_RearFootRod_Redo':('M578',['SNL:194:020'])}
for key,(mark,records) in identities.items():
    properties[key]=dict(SourcePartMark=mark,SourceRecords=records,DefinitionKey=key,
        Representation='reconstruction_trial',ReconstructionStatus='Estimated static geometry; see center_foot_source_review01.json.',
        ParameterUpdate='Regenerate with trial_control_rebuild_center_foot_v2.py and '+str(a.controls.relative_to(ROOT)))

def carry(name):
    r=parent.rows[name];key=r['definition']
    shapes[key]=parent.definition(key);properties[key]=parent.manifest['definitions'][key]['properties']
    specs[name]=dict(definition=key,frame=r['frame'],owner=r['owners'][-1],role='receiver')

def put(name,key,frame,owner,role,records=None):
    specs[name]=dict(definition=key,frame=list(frame.toMatrix().A),owner=owner,role=role)
    if records:specs[name]['source_records']=records

identity=App.Placement()
groups['CenterFootControls']=dict(owner='Root',frame=list(identity.toMatrix().A))
joint_template=pose(parent.rows['PortTrackBrakeJointFork']['frame'])
hardware={}
for role in ['Fork','Pin','Cotter','Nut']:
    old=parent.rows['PortTrackBrakeJoint'+role];key=old['definition']
    shapes[key]=parent.definition(key);properties[key]=parent.manifest['definitions'][key]['properties']
    hardware[role]=(key,joint_template.inverse().multiply(pose(old['frame'])))
assert properties[hardware['Pin'][0]]['SourcePartMark']=='M568C'
carry('hull_floor_6');floor_key=parent.rows['hull_floor_6']['definition']
floor_pose=pose(parent.rows['hull_floor_6']['frame']);drills=[];mounts=[]
interfaces=read(H/'transmission_controls_study/track_rods_integrated01/operating_interfaces.json')

for side,sign in [('Starboard',-1),('Port',1)]:
    owner=side+'CenterFootControl'
    frame=App.Placement(V(c['bracket_station_x'],sign*c['bracket_station_y'],c['floor_top']),
                        App.Rotation(V(0,0,1),180 if sign==1 else 0))
    groups[owner]=dict(owner='CenterFootControls',frame=list(frame.toMatrix().A))
    put(side+'CenterFootBracket','Def_CenterFootBracket_Redo',frame,owner,'bracket')
    rocker_frame=frame.multiply(App.Placement(V(0,0,c['pivot_height']),App.Rotation()))
    put(side+'CenterFootRocker','Def_ControlRocker_Redo',rocker_frame,owner,'rocker')
    # Keeper axis local Y -> bracket Z; its prongs spread along bracket X,
    # keeping the entire keeper clear of the rocker's axial bearing face.
    keeper_local=App.Placement(V(0,c['keeper_station_y'],c['pivot_height']),App.Rotation(V(1,1,1),120))
    put(side+'CenterFootKeeper','Def_CenterFootKeeper_Redo',frame.multiply(keeper_local),owner,'keeper')
    for i,(x,y) in enumerate(c['rivet_centers'],1):
        bottom=frame.multVec(V(x,y,-c['floor_stock']))
        put(side+'CenterFootRivet'+str(i),'Def_CenterFootRivet_Redo',App.Placement(bottom,App.Rotation()),owner,'rivet')
        drill=Part.makeCylinder(c['rivet']['hole_diameter']/2,c['floor_stock']+2,bottom-V(0,0,1))
        drill.Placement=floor_pose.inverse().multiply(drill.Placement);drills.append(drill)
        mounts.append(dict(side=side,index=i,center_world_mm=list(bottom),axis_world=[0,0,1]))
    receiver=side+'TrackHorizontalLever';carry(receiver)
    old=next(v for v in interfaces['interfaces'] if v['occurrence']==receiver and abs(v['local_center_mm'][1]-203.2)<1e-6)
    rear=V(*old['center_world_mm']);front=rocker_frame.multVec(V(0,0,-c['arm_radius']))
    assert abs(front.y-rear.y)<1e-6 and abs(front.z-rear.z)<1e-6
    start=rear.x+44.45-c['rod_insertion'];end=front.x-44.45+c['rod_insertion']
    rod=Part.makeCylinder(c['rod_diameter']/2,end-start,V(),V(1,0,0))
    key='Def_RearFootRod_Redo'
    if key in shapes:assert abs(shapes[key].Volume-rod.Volume)<1e-6
    shapes[key]=rod
    put(side+'RearFootRod',key,App.Placement(V(start,rear.y,rear.z),App.Rotation()),owner,'rod')
    for end_name,center,x,y,receiving in [
        ('Rear',rear,V(1,0,0),V(0,0,1),receiver),
        ('Center',front,V(-1,0,0),V(0,sign,0),side+'CenterFootRocker')]:
        stem=side+'Foot'+end_name+'Joint'
        jf=App.Placement(center,App.Rotation(x,y,x.cross(y),'XYZ'))
        groups[stem]=dict(owner=owner,frame=list(jf.toMatrix().A))
        for role,(key,local) in hardware.items():
            records=['SNL:194:021'] if role=='Nut' else json.loads(properties[key]['SourceRecords'])
            put(stem+role,key,jf.multiply(local),stem,role.lower(),records)
        joints[stem]=dict(frame=list(jf.toMatrix().A),receiver=receiving,center_world_mm=list(center),
                          pin_axis_world=list(y),rod_axis_world=list(x),rod=side+'RearFootRod')
    details[side]=dict(rear_pin_world_mm=list(rear),center_pin_world_mm=list(front),rod_length_mm=end-start,
                      support_frame=list(frame.toMatrix().A),rocker_frame=list(rocker_frame.toMatrix().A))

shapes[floor_key]=shapes[floor_key].cut(Part.makeCompound(drills))
specs['hull_floor_6']['role']='revised_floor'
details.update(controls=c,joints=joints,mounts=mounts,floor_definition=floor_key)
native=trial(a.output,parent,shapes,specs,properties,details,
    [Path(__file__),H/'control_rebuild_center_foot_parts_v2.py',H/'control_rebuild_io_v2.py',
     H/'rear_control_channel_mount_parts.py',H/'transmission_frame_joint_parts.py',
     H/'transmission_input_installation_parts.py',a.controls,source,
     parent.folder/'qualification.json',parent.folder/'report.json',parent.folder/'isolated/manifest.json',
     H/'transmission_controls_study/track_rods_integrated01/operating_interfaces.json'],
    changed_definitions=[floor_key],assembly_groups=groups)
print('Saved',len(specs),'physical prototype occurrences; center foot and M578 geometry unqualified.',native,flush=True)
