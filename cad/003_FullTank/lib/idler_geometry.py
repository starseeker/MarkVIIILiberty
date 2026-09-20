"""Explicit reconstruction controls for the fixed bracket and moving idler shaft."""
import math


def axis(data):
    from .model import point
    x,z=point(data,'snl_2',[194,339])
    fx,fz=point(data,'snl_2',[144,327])
    angle=math.atan2(fz-z,fx-x)
    return x,z,angle


def values(data):
    v={k:q.value for k,q in data['values'].items()
       if k.startswith(('idler_','wheel_')) or k in
       {'hull_frame_clear','hull_front_thickness','roller_oil_bore'}}
    v['shell_inner']=v['hull_frame_clear']/2
    v['shell_outer']=v['shell_inner']+v['hull_front_thickness']
    v['bracket_inner']=v['wheel_boss_length']/2+v['idler_boss_end_gap']
    v['bracket_outer']=v['shell_outer']+v['idler_guide_projection']
    v['screw_y']=v['shell_outer']+v['idler_screw_axis_offset']
    v['screw_head_start']=v['idler_screw_tip']+v['idler_screw_length']-v['idler_screw_head_stock']
    v['screw_head_center']=v['screw_head_start']+v['idler_screw_head_stock']/2
    v['copper_start']=v['screw_y']+math.sqrt((v['idler_screw_diameter']/2)**2-(v['idler_copper_diameter']/2)**2)
    v['locking_tip']=v['copper_start']+v['idler_copper_length']
    return v


def arguments(definition,data):
    return {**values(data),**definition['arguments']}


def cap_points(a):
    return [(x,z) for x in [a['idler_cap_rear_x'],a['idler_cap_front_x']]
            for z in [-a['idler_cap_z'],a['idler_cap_z']]]


def rivet_points(a):
    rear=a['idler_plate_rear_x']+a['idler_plate_rivet_inset']
    front=a['idler_plate_front_x']-a['idler_plate_rivet_inset']
    return [(rear,z) for z in [-a['idler_plate_rivet_z'],0,a['idler_plate_rivet_z']]]+[
        (front,z) for z in [-a['idler_plate_rivet_front_z'],a['idler_plate_rivet_front_z']]]


def child_datum(spec,data):
    from .wheel_geometry import station
    a=values(data);_,_,angle=axis(data);role=spec['idler_child'];side=spec.get('idler_side',1)
    tr=[0,0,0];rot=[0,0,0] if side==1 else [0,0,180]
    if role in {'wheel_frame','shaft_frame','support_frame'}:
        if role!='support_frame':
            st=station(data);tr=[st['x_offset'],0,st['z_offset']]
        rot=[0,-math.degrees(angle) if role!='wheel_frame' else 0,0]
    elif role in {'bracket','plate','guard'}:tr[1]=side*a['shell_outer']
    elif role=='nut':tr[1]=side*(a['bracket_outer']+a['idler_washer_stock'])
    elif role=='washer':tr[1]=side*a['bracket_outer']
    elif role=='copper':tr[1]=side*a['copper_start']
    elif role=='locking_screw':tr[1]=side*a['locking_tip']
    elif role=='oil_plug':
        tr=[0,side*a['idler_shaft_length']/2,a['idler_oil_height']]
        rot=[0,0,180] if side==1 else [0,0,0]
    elif role=='adjusting_screw':tr[1]=side*a['screw_y']
    elif role=='cap_screw':
        x,z=cap_points(a)[spec['idler_index']]
        tr=[x,side*(a['shell_outer']+a['idler_bracket_foot_stock']),z]
    elif role=='plate_rivet':
        side=1 if spec['parent'].startswith('Port') else -1
        x,z=rivet_points(a)[spec['idler_index']]
        grip=a['hull_front_thickness']+a['idler_plate_stock']
        tr=[x,side*(a['shell_outer']-grip/2),z]
        # Factory head on the shell exterior, upset head on reinforcement plate.
        rot=[0,0,180] if side==1 else [0,0,0]
    else:raise ValueError('Unknown idler child '+role)
    return dict(translation=tr,rotation_deg=rot,parent=spec['parent'])


def clearance(data):
    x,z,angle=axis(data)
    return dict(values=values(data),x=x,z=z,angle_deg=math.degrees(angle))
