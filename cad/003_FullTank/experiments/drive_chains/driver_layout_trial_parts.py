"""Closed-stock height hypotheses for the complete existing driver linkage.

Keep all internal driver geometry/relative poses and the printed M574 stock.
Only M576's unprinted common stock length is recalculated. Support plates,
floor holes and mounts need separate construction on the revised floor.
"""
import copy
import math
from control_rebuild_io_v2 import App, Part, pose

V=App.Vector;X=V(1,0,0);Y=V(0,1,0)


def layout(parent, main_z):
    details=parent.report['details']
    old_main=V(*details['foundation']['shafts']['Main']['center_world_mm'])
    old_rear=V(*details['foundation']['shafts']['Swing']['center_world_mm'])
    low=details['low_speed']['Port']
    fixed=V(*low['endpoints'][0]['pin_world_mm'])
    old_tip=V(*low['endpoints'][1]['pin_world_mm'])
    separation=old_main.x-old_rear.x
    rear_z=main_z+(old_rear.z-old_main.z)
    end_z=rear_z+(old_tip.z-old_rear.z)
    span=1257.3+2*25.4
    end_x=fixed.x+math.sqrt(span**2-(end_z-fixed.z)**2)
    rear=V(end_x-(old_tip.x-old_rear.x),0,rear_z)
    main=V(rear.x+separation,0,main_z)
    delta=main-old_main
    rods={}
    for side in ['Port','Starboard']:
        rods[side+'DriverLowRod']=copy.deepcopy(details['low_speed'][side])
        rods[side+'DriverLowRod']['mark']='M574'
        rods[side+'DriverHighFrontRod']=copy.deepcopy(details['high_controls'][side]['rods']['Front'])
        rods[side+'DriverHighFrontRod']['mark']='M576'
    rods['DriverClutchFrontRod']=copy.deepcopy(details['rods']['Front'])
    moving_rods=set(rods)
    for rod in rods.values():
        for end in rod['endpoints']:
            moving_rods.update(end['stem']+role for role in ['Fork','Pin','Cotter','Nut'])
    shapes={};specs={};properties={};excluded=[]
    def use(name):
        row=parent.rows[name];key=row['definition']
        if key not in shapes:
            shapes[key]=parent.definition(key)
            properties[key]=parent.manifest['definitions'][key]['properties']
        specs[name]=dict(definition=key,frame=row['frame'],owner=row['owners'][-1],role='driver_layout')
        return row
    for name,row in parent.rows.items():
        if 'DriverControlFoundation' not in row['owners']:continue
        if 'DriverSupportPlates' in row['owners'] or 'DriverFloorContext' in row['owners']:
            excluded.append(name);continue
        if name in moving_rods:continue
        use(name);new=pose(row['frame']);new.Base+=delta;specs[name]['frame']=list(new.toMatrix().A)
    lengths=[];rod_records={}
    for name,record in rods.items():
        row=use(name)
        ends=record['endpoints'];p=V(*ends[0]['pin_world_mm']);q=V(*ends[1]['pin_world_mm'])+delta
        axis=q-p;distance=axis.Length;axis.normalize();length=distance-50.8
        if record['mark']=='M574':assert abs(length-1257.3)<1e-7
        else:
            lengths.append(length)
            shapes[row['definition']]=Part.makeCylinder(9.525,length,V(),X)
        specs[name]['frame']=list(App.Placement(p+axis*25.4,App.Rotation(X,axis)).toMatrix().A)
        for i,(end,point,along) in enumerate(zip(ends,[p,q],[axis,-axis])):
            old_axis=V(*end['rod_axis_world'])
            old=App.Placement(V(*end['pin_world_mm']),App.Rotation(old_axis,Y,old_axis.cross(Y),'XYZ'))
            new=App.Placement(point,App.Rotation(along,Y,along.cross(Y),'XYZ'))
            for role in ['Fork','Pin','Cotter','Nut']:
                part=end['stem']+role;oldrow=use(part)
                newpose=new.multiply(old.inverse().multiply(pose(oldrow['frame'])))
                specs[part]['frame']=list(newpose.toMatrix().A)
        rod_records[name]=dict(mark=record['mark'],stock_length_mm=length,pin_span_mm=distance,
                              fixed_pin_world_mm=list(p),driver_pin_world_mm=list(q),axis_world=list(axis))
    assert max(lengths)-min(lengths)<1e-7
    return shapes,specs,properties,dict(main_world_mm=list(main),swing_world_mm=list(rear),
        driver_translation_mm=list(delta),rod_records=rod_records,M576_common_stock_mm=lengths[0],
        omitted_support_and_floor_occurrences=excluded,
        retained_internal_driver_occurrences=len(specs)-len(moving_rods),changed_rod_and_joint_occurrences=len(moving_rods))
