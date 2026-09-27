"""Propagate a conditional driver station through complete rods and real mounts.

Preserve M574 cores and the rigid SH229A93in center rod. Unprinted rear routes
are regenerated, and obsolete mounting holes are restored from original stock.
Nothing is accepted by this construction worker.
"""
import argparse
import copy
import math
from pathlib import Path
from control_rebuild_io_v2 import *
from driver_folded_floor_support import support as floor_support
from driver_seat_support_parts import supports as seat_supports

V=App.Vector;X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--main-x-offset',type=float,default=0.)
a=p.parse_args()
U=H/'driver_seat_support_study/trial01';A=C/'driver_redo01/operating_integrated01';R=C/'redo01'
parent=Saved(U);accepted=Saved(A)
source=H/'driver_station_review/visibility01/report.json';review=read(source)
# The proposal lacks an extracted manifest; use its independently reopened
# clearance report and the qualified canonical profile from the earlier study.
profile=Saved(C/'driver_redo01/handle_profiles01/functional_source')
probe=read(H/'driver_station_review/profile_probe01/functional_source/clearance_report.json')
assert probe['local_clearance_passed'] and not probe['installation_qualified']
seed=read(H/'driver_station_review/profile_probe01/functional_source/report.json')
main=V(*review['shaft_pair']['main_construction_world_mm'])+X*a.main_x_offset
old_main=V(*accepted.report['details']['foundation']['shafts']['Main']['center_world_mm'])
driver_delta=main-old_main
swing=V(*accepted.report['details']['foundation']['shafts']['Swing']['center_world_mm'])+driver_delta
low=accepted.report['details']['low_speed']['Port']['endpoints']
new_driver_pin=V(*low[1]['pin_world_mm'])+driver_delta;old_low=V(*low[0]['pin_world_mm'])
span=1257.3+50.8
intermediate_dx=new_driver_pin.x-math.sqrt(span**2-(new_driver_pin.y-old_low.y)**2-(new_driver_pin.z-old_low.z)**2)-old_low.x
intermediate_delta=X*intermediate_dx
shapes={k:parent.definition(k) for k in parent.manifest['definitions']}
props={k:dict(r['properties']) for k,r in parent.manifest['definitions'].items()}
specs={n:dict(definition=r['definition'],frame=r['frame'],owner='RetainedSeatBow',role='receiver') for n,r in parent.rows.items()}
changed=set();curves={};rod_records={};mount_records=[];floor_changes=[];rigid_groups={}


def carry(src,name,delta=None,owner=None):
    row=src.rows[name];key=row['definition']
    if key not in shapes:shapes[key]=src.definition(key);props[key]=dict(src.manifest['definitions'][key]['properties'])
    frame=pose(row['frame'])
    if delta is not None:frame.Base+=delta
    specs[name]=dict(definition=key,frame=list(frame.toMatrix().A),
        owner=owner or row['owners'][-1],role='coupled_station')
    return frame


def put(name,frame,owner=None):
    specs[name]['frame']=list(frame.toMatrix().A)
    specs[name]['role']='coupled_station'
    if owner:specs[name]['owner']=owner


def revise(key,shape,note):
    assert shape.Placement.isIdentity() and shape.isValid() and len(shape.Solids)==1 and shape.Solids[0].isClosed(),key
    shapes[key]=shape;changed.add(key)
    props[key]=dict(props[key],ReconstructionStatus=note,
        ParameterUpdate='Regenerate build_coupled_driver_station.py with recorded main-x-offset; no live expressions.')


def local_shape(q,frame):
    q=q.copy();q.Placement=frame.inverse().multiply(q.Placement)
    return Part.makeCompound([q])


unit=seed['details']['unit_occurrences']
for name in unit:carry(accepted,name,driver_delta,'DriverMechanism')
rigid_groups['DriverMechanism']=dict(source=str(A.relative_to(ROOT)),names=unit,delta_mm=list(driver_delta))
for side in ['Port','Starboard']:
    name=side+'DriverOperatingHandle';key=specs[name]['definition']
    revise(key,profile.definition(profile.rows[name]['definition']),
        'Complete main-shaft-radius/source-direction37in interpretation reused at conditional station; length datum and historical configuration remain hypotheses.')

# Translate complete intermediate gang and clutch swing. The entire center rod,
# its joints and both receivers translate together, preserving source stock.
intermediate_names=[n for n,r in accepted.rows.items() if 'IntermediateControls' in r['owners']]
clutch_names=[n for n,r in accepted.rows.items() if 'ClutchSwingControls' in r['owners'] and
              n!='ClutchRearRod' and not n.startswith('ClutchRearRodRearJoint')]
for group,names in [('IntermediateControls',intermediate_names),('ClutchSwingAndCenterRod',clutch_names)]:
    for name in names:carry(accepted,name,intermediate_delta,group)
    rigid_groups[group]=dict(source=str(A.relative_to(ROOT)),names=names,delta_mm=list(intermediate_delta))
assert len(intermediate_names)==22 and len(clutch_names)==37
center_path=R/'clutch_swing08/ClutchCenterRod_centerline.brep'
wire=Part.Shape();wire.read(str(center_path));wire.translate(intermediate_delta)
curves['ClutchCenterRod']=wire
assert abs(wire.Length-2362.2)<1e-6

# All five existing front rods close between translated actual receiver frames.
fronts={'DriverClutchFrontRod':accepted.report['details']['rods']['Front']}
for side in ['Port','Starboard']:
    fronts[side+'DriverLowRod']=accepted.report['details']['low_speed'][side]
    fronts[side+'DriverHighFrontRod']=accepted.report['details']['high_controls'][side]['rods']['Front']
common_lengths=[]
for name,record in fronts.items():
    carry(accepted,name)
    ends=record['endpoints'];rear=V(*ends[0]['pin_world_mm'])+intermediate_delta
    front=V(*ends[1]['pin_world_mm'])+driver_delta;axis=front-rear;distance=axis.Length;axis.normalize()
    length=distance-50.8;key=specs[name]['definition']
    if name.endswith('DriverLowRod'):
        assert abs(length-1257.3)<1e-7
        shapes[key]=accepted.definition(key)
    else:
        common_lengths.append(length)
        revise(key,Part.makeCylinder(9.525,length,V(),X),'Shared unprinted M576 stock regenerated between actual coupled receivers; full joint engagement retained.')
    put(name,App.Placement(rear+axis*25.4,App.Rotation(X,axis)),'DriverFrontRods')
    for end,point,along in zip(ends,[rear,front],[axis,-axis]):
        old_axis=V(*end['rod_axis_world'])
        old=App.Placement(V(*end['pin_world_mm']),App.Rotation(old_axis,Y,old_axis.cross(Y),'XYZ'))
        new=App.Placement(point,App.Rotation(along,Y,along.cross(Y),'XYZ'))
        for role in ['Fork','Pin','Cotter','Nut']:
            n=end['stem']+role;f=carry(accepted,n)
            put(n,new.multiply(old.inverse().multiply(f)),'DriverFrontRods')
    rod_records[name]=dict(mark='M574' if name.endswith('DriverLowRod') else 'M576',
        length_mm=length,centerline_length_mm=length,rear_pin_world_mm=list(rear),front_pin_world_mm=list(front),
        start_world_mm=list(rear+axis*25.4),end_world_mm=list(front-axis*25.4),
        rear_receiver=ends[0]['receiver'],front_receiver=ends[1]['receiver'],source_stock_fixed=name.endswith('DriverLowRod'))
assert max(common_lengths)-min(common_lengths)<1e-7


def swept_rod(name,points,bends,initial_axis=X,first_bend_fraction=1/3,first_bend_index=1):
    """Regenerate the whole stock from smooth named waypoints; no clipping."""
    carry(accepted,name);edges=[];poles={}
    for i,(u,v) in enumerate(zip(points,points[1:])):
        assert v.x>u.x,(name,i,'nonmonotonic route')
        if i in bends:
            fraction=first_bend_fraction if i==first_bend_index else 1/3
            handle=(v.x-u.x)*fraction
            pp=[u,u+(initial_axis if i==first_bend_index else X)*handle,v-X*handle,v]
            c=Part.BezierCurve();c.setPoles(pp);edges.append(c.toShape());poles[str(i)]=[list(q) for q in pp]
        else:edges.append(Part.makeLine(u,v))
    wire=Part.Wire(edges);start=points[0]
    rod=wire.makePipeShell([Part.Wire([Part.makeCircle(9.525,start,initial_axis)])],True,False)
    rod.translate(-start);key=specs[name]['definition']
    revise(key,Part.makeCompound([rod]),'Complete estimated rear/center route regenerated at coupled station; 19.05mm solid stock and existing receiving engagement retained.')
    put(name,App.Placement(start,App.Rotation()),'CoupledRearRods');curves[name]=wire
    rod_records[name]=dict(mark=props[key].get('SourcePartMark'),centerline_length_mm=wire.Length,
        path_points_world_mm=[list(q) for q in points],bezier_poles=poles,
        start_world_mm=list(start),end_world_mm=list(points[-1]),initial_axis=list(initial_axis),source_stock_fixed=False)


# M573/M579: retain rear paths and their complete rear joints, relocate the final
# transition with the intermediate receiver. All source hardware stays complete.
longs=read(R/'long_rods_integrated01/report.json')['details']
for side,sign in [('Port',1),('Starboard',-1)]:
    for kind,suffix in [('Low','RearLowRod'),('Foot','CenterFootRod')]:
        name=side+suffix;record=longs[name]
        points=[V(*q) for q in record['path_points_world_mm']]
        for i in range(len(points)-3,len(points)):points[i]+=intermediate_delta
        angle=math.radians(longs['controls']['rear_fork_inboard_yaw_deg'])
        axis=V(math.cos(angle),-sign*math.sin(angle),0)
        swept_rod(name,points,[1,3,5] if kind=='Low' else [1,3],axis,longs['controls']['bend_handle_fraction'])
        for end in ['Rear','Intermediate']:
            for role in ['Fork','Pin','Cotter','Nut']:
                carry(accepted,side+kind+'Long'+end+'Joint'+role,intermediate_delta if end=='Intermediate' else None,'CoupledRearRods')
        rod_records[name]['rear_pin_world_mm']=record['rear_pin_world_mm']
        rod_records[name]['front_pin_world_mm']=list(V(*record['intermediate_pin_world_mm'])+intermediate_delta)

# M575: rear springs/guides/forks remain fixed; only the far transition changes.
high=read(R/'high_integrated01/report.json')['details']
for side in ['Port','Starboard']:
    points=[V(*q) for q in high[side]['rod_points_world_mm']]
    for i in range(len(points)-3,len(points)):points[i]+=intermediate_delta
    swept_rod(side+'RearHighRod',points,[1,3,5,7],X,.45)
    for role in ['Fork','Pin','Cotter','Nut']:carry(accepted,side+'HighIntermediateJoint'+role,intermediate_delta,'CoupledRearRods')

# M581: unchanged rear pitch/exit, new complete final span to translated SH944B.
clutch=read(R/'clutch_swing_integrated02/report.json')['details']
points=[V(*q) for q in clutch['rod_path_points_world_mm']];points[-1]+=intermediate_delta
swept_rod('ClutchRearRod',points,[1,3],V(*clutch['Rear']['fork_axis_world']))
for role in ['Fork','Pin','Cotter','Nut']:carry(accepted,'ClutchRearRodRearJoint'+role,None,'CoupledRearRods')
rod_records['ClutchCenterRod']=dict(mark='SH229A',centerline_length_mm=curves['ClutchCenterRod'].Length,
    printed_length_mm=2362.2,source_stock_fixed=True,rigid_translation_mm=list(intermediate_delta),
    inherited_centerline=str(center_path.relative_to(ROOT)),inherited_centerline_sha256=sha(center_path))

# Move only the mounting bores, restoring original material inside the old bores.
standard_path=H/'transmission_brake_front_study/trial01/standard_context_manifest.json'
standard=read(standard_path)
assert all(sha(ROOT/f)==h for f,h in standard['native_files'].items())
for floor,names,radius in [
    ('hull_floor_3',[n for n in intermediate_names if n.endswith('CapScrew')],6.55),
    ('hull_floor_6',['ClutchSwingMount'+str(i)+'Bolt' for i in range(1,5)],6.5)]:
    if floor not in specs:carry(accepted,floor)
    row=next(r for r in standard['occurrences'] if r['name']==floor);entry=standard['definitions'][row['definition']]
    assert sha(entry['brep_path'])==entry['brep_sha256']
    stock=Part.Shape();stock.read(entry['brep_path']);stock.Placement=pose(row['frame'])
    q=accepted.world(floor);holes=[]
    for name in names:
        old=pose(accepted.rows[name]['frame']).Base;now=pose(specs[name]['frame']).Base
        z=stock.BoundBox.ZMin-1;height=stock.BoundBox.ZLength+2
        filltool=Part.makeCylinder(radius+1e-5,height,V(old.x,old.y,z),Z)
        q=q.fuse(stock.common(filltool))
        q=q.cut(Part.makeCylinder(radius,height,V(now.x,now.y,z),Z))
        holes.append(dict(fastener=name,old_xy=[old.x,old.y],new_xy=[now.x,now.y],radius_mm=radius))
    revise(specs[floor]['definition'],local_shape(q,pose(specs[floor]['frame'])),
        'Restore obsolete mounting holes from original stock and bore the relocated complete mounting stacks; all other floor material retained.')
    floor_changes.append(dict(floor=floor,holes=holes,original_stock_definition=row['definition']))

# Rebuild driver side plates and separate M788 angles on the actual bow floors.
# Seat, four stays and all upper/lower stay bolts remain at source-derived picks.
bow_folder=H/'bow_reconstruction_study/trial02';bow=read(bow_folder/'report.json')
bn=bow_folder/bow['native_file'];assert sha(bn)==bow['native_sha256']
doc=App.openDocument(str(bn))
for name in ['hull_floor_1','hull_floor_2']:
    link=doc.getObject(name);q=link.LinkedObject.Shape.copy();q.Placement=link.LinkPlacement
    revise(specs[name]['definition'],local_shape(q,pose(specs[name]['frame'])),
        'Unperforated bow-study stock with only the regenerated driver floor mounting bores; old driver holes restored.')
App.closeDocument(doc.Name)
controls=accepted.report['details']['foundation']['controls'];t=controls['plate_stock'];outer=controls['nut_seat_y'];inside=outer-t
lower_centers={}
for station in ['Front','Rear']:
    r=next(v for v in parent.report['details']['stays'] if v['name']=='DriverSeatPort'+station+'Stay')
    q=V(*r['lower_center_world_mm']);q.y=0;lower_centers[station]=q
support_records={}
for side,hand in [('Port',1),('Starboard',-1)]:
    name='Driver'+side+'SupportPlate';angle_name='DriverSeat'+side+'SupportAngle'
    _,_,mounts,record=floor_support(bow,controls,main,swing,hand)
    web,angle,base=seat_supports(record,controls,lower_centers,hand)
    upper=record['upper_foot_section_world']
    def height(x):
        for p0,p1 in zip(upper,upper[1:]):
            if p0[0]-1e-7<=x<=p1[0]+1e-7:return p0[1]+(p1[1]-p0[1])*(x-p0[0])/(p1[0]-p0[0])
        raise ValueError('Mount outside angle')
    for index,mount in enumerate(mounts,1):
        contact=V(*mount['contact_world_mm']);normal=V(*mount['normal_world'])
        angle=angle.cut(Part.makeCylinder(6.5,t+2,contact-base-normal,normal))
        floor=mount['floor'];key=specs[floor]['definition'];f=pose(specs[floor]['frame'])
        q=shapes[key].copy();q.Placement=f
        q=q.cut(Part.makeCylinder(6.5,30,contact+normal*10,-normal))
        shapes[key]=local_shape(q,f)
        stem='DriverSeat'+side+'AngleFloor'+str(index)
        oldjoint=next(v for v in parent.report['details']['joints'] if v['stem']==stem)
        oldaxis=V(*oldjoint['axis_world']);oldpoint=V(*oldjoint['point_world_mm'])
        oldcontact=V(*parent.report['details']['supports'][side]['original_floor_mounts'][index-1]['contact_world_mm'])
        rotation=App.Rotation(oldaxis,-normal)
        for suffix in ['Bolt','Lock','Nut']:
            n=stem+suffix;oldf=pose(parent.rows[n]['frame'])
            put(n,App.Placement(contact+rotation.multVec(oldf.Base-oldcontact),rotation.multiply(oldf.Rotation)),'SeatFloorAngles')
        floorjoint=dict(oldjoint,point_world_mm=list(contact+rotation.multVec(oldpoint-oldcontact)),axis_world=list(-normal))
        mount_records.append(floorjoint)
        stem='Driver'+side+'SupportMount'+str(index);point=V(contact.x,hand*inside,height(contact.x)+28)
        tool=Part.makeCylinder(6.5,2*t+2,point-base-Y*hand,Y*hand)
        web=web.cut(tool);angle=angle.cut(tool)
        oldjoint=next(v for v in parent.report['details']['joints'] if v['stem']==stem)
        shift=point-V(*oldjoint['point_world_mm'])
        for suffix in ['Bolt','Lock','Nut']:
            n=stem+suffix;f=pose(parent.rows[n]['frame']);f.Base+=shift;put(n,f,'SeatSupportPlateFasteners')
        mount_records.append(dict(oldjoint,point_world_mm=list(point)))
    revise(specs[name]['definition'],web.removeSplitter(),'Conditional M786/M787 web with relocated complete shaft bores, unchanged stay joints and real regenerated plate/angle mounts; outline estimated.')
    revise(specs[angle_name]['definition'],angle.removeSplitter(),'Separate M788 angle regenerated on actual floor profile with four full-stock floor bolts and four plate bolts; shape and footprint estimated.')
    for n in [name,angle_name]:put(n,App.Placement(base,App.Rotation()),'SeatSupportPlates')
    support_records[side]=record

# Include fixed terminal receivers for independent saved-interface checks.
fixed_receivers=['ClutchSupport_AuxLever1','PortLowHorizontalLever','StarboardLowHorizontalLever',
    'PortCenterFootRocker','StarboardCenterFootRocker','PortHighSpeedBrakeLeverLeft','StarboardHighSpeedBrakeLeverLeft']
for name in fixed_receivers:carry(accepted,name,None,'FixedRearReceivers')
details=dict(main_world_mm=list(main),swing_world_mm=list(swing),main_x_offset_mm=a.main_x_offset,
    intermediate_translation_mm=list(intermediate_delta),driver_translation_from_accepted_mm=list(driver_delta),
    rigid_groups=rigid_groups,rods=rod_records,M576_common_stock_mm=common_lengths[0],
    support_records=support_records,driver_mount_joints=mount_records,floor_hole_changes=floor_changes,
    retained_development_native=str(accepted.native.relative_to(ROOT)),retained_development_native_sha256=sha(accepted.native),
    source_camera_refitted=False,geometry_integrated=False,
    source_review=str(source.relative_to(ROOT)),profile_hypothesis='functional_source',
    scope='Complete coupled driver/intermediate/SH944 station hypothesis, all existing affected front/rear rods, source-sized mounting stacks and connected seat supports. Static only; independent full-context and interface checks pending.',
    limits=['Tentative section shaft-end identities and37in handle datum.','Unprinted station, profiles and rear route lengths.','Remaining driver foot/reverse controls and SH291C/seat adjustment not populated.','No motion or historical accuracy qualification.'])
inputs=[Path(__file__),H/'control_rebuild_io_v2.py',H/'driver_folded_floor_support.py',H/'driver_seat_support_parts.py',H/'bow_reconstruction_parts.py',
    source,H/'driver_station_review/study_receipt.json',profile.folder/'report.json',profile.folder/'isolated/manifest.json',
    parent.folder/'report.json',parent.folder/'isolated/manifest.json',accepted.folder/'report.json',accepted.folder/'isolated/manifest.json',
    H/'driver_station_review/profile_probe01/functional_source/report.json',
    R/'long_rods_integrated01/report.json',R/'high_integrated01/report.json',R/'clutch_swing_integrated02/report.json',
    center_path,standard_path,bow_folder/'report.json',bn]
trial(a.output,parent,shapes,specs,props,details,inputs,curves=curves,changed_definitions=sorted(changed))
print('Coupled station saved:',len(specs),'occurrences;',len(shapes),'definitions;',len(changed),'revised definitions.',flush=True)
