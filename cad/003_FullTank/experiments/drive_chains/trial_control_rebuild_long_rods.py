"""Complete M573/M579 routing from actual rear/center receivers to M640 rockers."""
import argparse,math,json,sys
from pathlib import Path
from control_rebuild_io_v2 import *
from control_rebuild_center_foot_parts_v3 import parts as foot_parts
V=App.Vector;X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)
p=argparse.ArgumentParser();p.add_argument('--controls',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
c=read(a.controls);parent=Saved(ROOT/c['parent']);assert sha(parent.native)==c['parent_native_sha256']
source=ROOT/c['source_review'];assert sha(source)==c['source_review_sha256'];assert all(sha(ROOT/f)==v for f,v in read(source)['source_hashes'].items())
shapes={};specs={};properties={};details={};groups={};curves={};joints={}
def carry(n):
    row=parent.rows[n];key=row['definition'];shapes.setdefault(key,parent.definition(key));properties[key]=parent.manifest['definitions'][key]['properties'];specs[n]=dict(definition=key,frame=row['frame'],owner=row['owners'][-1],role='receiver')
def put(n,key,frame,owner,role,records=None):
    specs[n]=dict(definition=key,frame=list(frame.toMatrix().A),owner=owner,role=role)
    if records:specs[n]['source_records']=records
for n,row in parent.rows.items():
    if row['definition']=='Def_ControlRocker_Redo':carry(n)
oldc=read(H/'transmission_controls_study/redo01/center_foot_controls05.json');oldc['inner_arm_radius']=c['inner_arm_radius']
shapes['Def_ControlRocker_Redo']=foot_parts(oldc)[0]['Def_ControlRocker_Redo']
changed=['Def_ControlRocker_Redo'] if c['inner_arm_radius']!=76.2 else []
template=pose(parent.rows['PortTrackBrakeJointFork']['frame']);hardware={}
for role in ['Fork','Pin','Cotter','Nut']:
    row=parent.rows['PortTrackBrakeJoint'+role];key=row['definition'];shapes.setdefault(key,parent.definition(key));properties[key]=parent.manifest['definitions'][key]['properties'];hardware[role]=(key,template.inverse().multiply(pose(row['frame'])))
identity=list(App.Placement().toMatrix().A);groups['LongLowAndFootControls']=dict(owner='Root',frame=identity)
for side,sign in [('Starboard',-1),('Port',1)]:
    for kind,mark,records in [('Low','M573',['SNL:195:015']),('Foot','M579',['SNL:194:016'])]:
        owner=side+'Long'+kind+'Control';groups[owner]=dict(owner='LongLowAndFootControls',frame=identity)
        rear_name=side+('LowHorizontalLever' if kind=='Low' else 'CenterFootRocker');carry(rear_name)
        if kind=='Low':
            receiver=parent.world(rear_name)
            fs=[f for f in receiver.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-6.5)<1e-6 and f.Surface.Axis.cross(Z).Length<1e-7]
            assert len(fs)==2,(rear_name,len(fs))
            # The larger-X eye is already occupied by the accepted short low rod.
            f=min(fs,key=lambda v:v.Surface.Center.x);center=f.Surface.Center;bb=f.BoundBox;rear=V(center.x,center.y,(bb.ZMin+bb.ZMax)/2)
        else:rear=pose(parent.rows[rear_name]['frame']).multVec(V(0,0,c['inner_arm_radius']))
        front_name=side+kind+'IntermediateRocker';front_frame=pose(parent.rows[front_name]['frame']);front=front_frame.multVec(V(0,0,101.6))
        start=rear+X*25.4;finish=front-X*25.4
        if kind=='Low':
            points=[start,V(2770,rear.y,rear.z),V(3090,sign*180,655),V(5740,sign*180,655),V(5840,sign*180,front.z),finish]
            bends=[1,3]
        else:
            points=[start,V(3440,rear.y,rear.z),V(4490,sign*70,rear.z),V(5740,sign*70,rear.z),V(5840,sign*70,front.z),finish]
            bends=[1,3]
        edges=[];bend_records=[]
        for i,(u,v) in enumerate(zip(points,points[1:])):
            if i in bends:
                curve=Part.BezierCurve();handle=(v.x-u.x)*c['bend_handle_fraction'];ps=[u,u+X*handle,v-X*handle,v];curve.setPoles(ps);edges.append(curve.toShape());bend_records.append([list(p) for p in ps])
            else:edges.append(Part.makeLine(u,v))
        wire=Part.Wire(edges);profile=Part.Wire([Part.makeCircle(9.525,start,X)]);rod=wire.makePipeShell([profile],True,False);rod.translate(-start);rod=Part.makeCompound([rod])
        key='Def_'+side+kind+'LongRod_Redo';shapes[key]=rod;properties[key]=dict(SourcePartMark=mark,SourceRecords=records,Representation='reconstruction_trial',ReconstructionStatus='Complete installed routing estimate; continuous stock and all receivers must be independently checked.',ParameterUpdate='Regenerate trial_control_rebuild_long_rods.py')
        name=side+('RearLowRod' if kind=='Low' else 'CenterFootRod');put(name,key,App.Placement(start,App.Rotation()),owner,'rod');curves[name]=wire
        for end,point,x,y,receiver_name in [('Rear',rear,X,Z,rear_name),('Intermediate',front,-X,Y,front_name)]:
            stem=side+kind+'Long'+end+'Joint';frame=App.Placement(point,App.Rotation(x,y,x.cross(y),'XYZ'));groups[stem]=dict(owner=owner,frame=list(frame.toMatrix().A))
            for role,(key,local) in hardware.items():put(stem+role,key,frame.multiply(local),stem,role.lower(),['SNL:195:016'] if kind=='Low' and role=='Nut' else ['SNL:194:017'] if role=='Nut' else None)
            joints[stem]=dict(receiver=receiver_name,center_world_mm=list(point),pin_axis_world=list(y),rod_axis_world=list(x),rod=name,frame=list(frame.toMatrix().A))
        details[name]=dict(rear_pin_world_mm=list(rear),intermediate_pin_world_mm=list(front),path_points_world_mm=[list(p) for p in points],bezier_poles_world_mm=bend_records,centerline_length_mm=wire.Length)
# Reconcile all ten inner-eye interfaces and the provisional driver datum while
# retaining source-sized M574 length and every established outer/rear receiver.
interfaces={}
for n,row in parent.rows.items():
    if row['definition']!='Def_ControlRocker_Redo':continue
    f=pose(row['frame']);interfaces[n]=dict(front_pin_world_mm=list(f.multVec(V(0,0,c['inner_arm_radius']))),rear_pin_world_mm=list(f.multVec(V(0,0,101.6))),axis_world=list(f.Rotation.multVec(Y)))
low=V(*interfaces['PortLowIntermediateRocker']['front_pin_world_mm']);span=1257.3+2*(44.45-19.05)
driver=V(low.x+math.sqrt(span**2-(890-low.z)**2),180,890)
details.update(controls=c,joints=joints,receiving_interfaces=interfaces,provisional_driver_low_port_pin_mm=list(driver),M574_pin_distance_mm=span,notes='M640 inner-eye radius and driver reference remain estimates. Printed M574 length retained; opposite-side driver pin mirrors Y.')
inputs=[Path(__file__),a.controls,source,H/'control_rebuild_io_v2.py',H/'control_rebuild_center_foot_parts_v3.py',H/'transmission_controls_study/redo01/center_foot_controls05.json',parent.folder/'report.json',parent.folder/'isolated/manifest.json']
inputs+=sorted({Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).resolve().parent==H and str(m.__file__).endswith('.py')})
trial(a.output,parent,shapes,specs,properties,details,inputs,curves=curves,changed_definitions=changed,assembly_groups=groups)
print('Saved complete low/center-foot rod trial; unqualified.',flush=True)
