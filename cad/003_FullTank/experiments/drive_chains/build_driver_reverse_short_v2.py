"""Close the third full M789A between a source-reach reverse lever and retained M784."""
import argparse,copy,math,sys
from control_rebuild_io_v2 import *
from driver_reverse_lever_parts_v2 import lever
V=App.Vector;X=V(1,0,0);Y=V(0,1,0)
p=argparse.ArgumentParser();p.add_argument('--controls',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--stock-offset',type=float,default=0);a=p.parse_args()
c=copy.deepcopy(read(a.controls));c['blade_stock_mm']+=a.stock_offset
parent=Saved(ROOT/c['parent']);assert sha(parent.native)==c['parent_native_sha256']
source=ROOT/c['source_review'];assert sha(source)==c['source_review_sha256']
assert all(sha(ROOT/f)==h for f,h in read(source)['source_hashes'].items())
main=V(*parent.report['details']['main_world_mm']);pivot=main+Y*c['lane_mm']
swingname='StarboardReverseDriverSwingLink';swingframe=pose(parent.rows[swingname]['frame']);rear=swingframe.multVec(V(45,0,-218))
stock=parent.definition('Def_DriverFrontShortRod_M789A');length=stock.BoundBox.XLength
assert abs(length-269.875)<1e-8;span=length+50.8;delta=rear-pivot;assert abs(delta.y)<1e-8
distance=delta.Length;radius=c['bell_radius_mm'];advance=(radius**2-span**2+distance**2)/(2*distance);height=math.sqrt(radius**2-advance**2)
unit=delta/distance;normal=V(-unit.z,0,unit.x);solutions=[unit*advance+normal*height,unit*advance-normal*height]
bell_relative=min(solutions,key=lambda v:v.z);front=pivot+bell_relative
q,rot,ld=lever(c,bell_relative);shapes={'Def_DriverReverseLever_M177':q};props={};specs={}
props['Def_DriverReverseLever_M177']=dict(SourcePartMark='M177 / M777 unresolved',SourceRecords=['SNL:118:008','HB:150','HB:plate94','SNL:plate6'],Representation='reconstruction_trial',
    ReconstructionStatus='Reverse lever body only. Printed27.968in hand reach and6in bell arm retained under stated datum interpretations. Included angle closes full sharedM789A; upper hand pose, blade set and sections estimated. Trigger, pawl, quadrant and long reverse controls remain pending.',ParameterUpdate='Regenerate build_driver_reverse_short_v2.py from recorded controls; no live expressions.')
def put(name,key,frame,role):specs[name]=dict(definition=key,frame=list(frame.toMatrix().A),owner='DriverReverseShortConnection',role=role)
put('DriverReverseOperatingLever','Def_DriverReverseLever_M177',App.Placement(pivot,rot),'lever')
doc=App.openDocument(str(parent.native))
def reuse(key):
    if key not in shapes:
        shapes[key]=parent.definition(key);obj=doc.getObject(key);props[key]={k:getattr(obj,k) for k in obj.PropertiesList if obj.getGroupOfProperty(k)=='Reconstruction'}
try:
    key='Def_DriverFrontShortRod_M789A';reuse(key)
    props[key]['ReconstructionStatus']='Complete printed10-5/8in stock. Shared definition for two high-control rods and the third reverse application. Fork insertion and nominal thread envelopes remain estimated.'
    axis=front-rear;axis.normalize();start=rear+axis*25.4
    put('DriverReverseShortRod',key,App.Placement(start,App.Rotation(X,axis)),'rod')
    template=pose(parent.rows['PortTrackBrakeJointFork']['frame']);joints=[]
    for end,point,direction,receiver in [('Rear',rear,axis,swingname),('Forward',front,-axis,'DriverReverseOperatingLever')]:
        frame=App.Placement(point,App.Rotation(direction,Y,direction.cross(Y),'XYZ'));stem='DriverReverseShort'+end+'Joint'
        for role in ['Fork','Pin','Cotter','Nut']:
            row=parent.rows['PortTrackBrakeJoint'+role];reuse(row['definition']);put(stem+role,row['definition'],frame.multiply(template.inverse().multiply(pose(row['frame']))),role.lower())
        joints.append(dict(stem=stem,pin_world_mm=list(point),rod_axis_world=list(direction),receiver=receiver))
    for name in ['DriverMainShaft','DriverSwingShaft',swingname]:
        row=parent.rows[name];reuse(row['definition']);specs[name]=dict(definition=row['definition'],frame=row['frame'],owner='Receivers',role='receiver')
finally:App.closeDocument(doc.Name)
details=dict(controls=c,stock_offset_mm=a.stock_offset,pivot_world_mm=list(pivot),front_pin_world_mm=list(front),rear_pin_world_mm=list(rear),
    main_world_mm=list(main),lever=ld,closure_alternatives_relative_main=[list(v) for v in solutions],stock_length_mm=length,pin_span_mm=span,stock_start_world_mm=list(start),rod_axis_world=list(axis),joints=joints,
    metadata_revisions={'Def_DriverFrontShortRod_M789A':['ReconstructionStatus']},
    retained_development_native=str(parent.native.relative_to(ROOT)),retained_development_native_sha256=sha(parent.native),source_camera_refitted=False,
    mechanism_complete=False,scope='Complete reverse lever body and third full sharedM789A with two complete clevis joints. Quadrant/trigger and full rearward reverse linkage remain unfinished.')
inputs=[Path(__file__),a.controls,source,parent.folder/'report.json',parent.folder/'isolated/manifest.json',parent.folder/'qualification.json',*[ROOT/f for f in read(source)['source_hashes']]]
inputs+=sorted({Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).resolve().parent==H and str(m.__file__).endswith('.py')})
trial(a.output,parent,shapes,specs,props,details,inputs)
print('Saved reverse lever and complete third short rod; checks pending. Bell',list(bell_relative),flush=True)
