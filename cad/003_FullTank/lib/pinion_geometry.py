"""Owned parameters and standard installation frames for the roller pinions."""
import math
from .drive_mount_geometry import values as mounting_values,bearing_points,backing_points


def values(data):
    a={k.removeprefix('pinion_'):q.value for k,q in data['values'].items() if k.startswith('pinion_')}
    m=mounting_values(data);a['mount']=m
    a['bank_center']=data['values']['wheel_rim_center'].value
    a['roller_circle']=a['boss_envelope_radius']-a['boss_radius']
    a['chain_pitch_radius']=a['chain_pitch']/(2*math.sin(math.pi/a['teeth']))
    a['flange_stock']=a['casting_length']/2-a['bank_center']-a['roller_length']/2-a['roller_end_gap']
    a['pin_start']=a['casting_length']/2+a['head_stock']-a['pin_length']
    a['roller_axis_on_pin']=a['bank_center']-a['pin_start']
    a['cotter_wire_radius']=(a['cotter_nominal_diameter']-a['cotter_center_spacing'])/2
    a['pin_bore_radius']=a['pin_diameter']/2+a['pin_running_gap']
    a['roller_bore_radius']=a['pin_bore_radius']
    a['counterbore_radius']=m['barrel_radius']+a['counterbore_gap']
    a['counterbore_bottom']=m['shoulder']-a['counterbore_gap']
    a['bush_center']=m['shoulder']-a['bush_end_gap']-data['values']['wheel_bush_length'].value/2
    a['casting_bore_radius']=data['values']['wheel_bush_od'].value/2+a['casting_bush_gap']
    a['shaft_end']=a['shaft_length']/2
    if min(a['flange_stock'],a['cotter_wire_radius'],a['shaft_end']-m['outside'])<=0:
        raise ValueError('Pinion support stack has no positive section')
    return a


def arguments(definition,data):
    return {**values(data),**definition['arguments']}


def station(data,hand):
    from .model import point,datum_values
    a=values(data)
    x,z=point(data,'snl_2',[a['source_pixel_x'],a['source_pixel_z']])
    drive=datum_values(('port' if hand==1 else 'starboard')+'_drive',data)['translation']
    dx,dz=x-drive[0],z-drive[2];length=math.hypot(dx,dz)
    return [x+dx/length*a['axis_static_offset'],drive[1],z+dz/length*a['axis_static_offset']]


def datum(spec,data):
    a=values(data);m=a['mount'];role=spec['pinion_child']
    side=spec.get('pinion_side',1);hand=spec.get('pinion_hand',1)
    translation=[0,0,0];rotation=[0,0,0]
    if role=='station':translation=station(data,hand)
    elif role=='hand_frame':rotation=[0,0,0] if hand==1 else [180,0,0]
    elif role=='rotor_frame':rotation=[0,hand*a['static_phase'],0]
    elif role in {'identity','casting','shaft','key','backing_plate','outer_bearing'}:pass
    elif role in {'roller','pin_assembly'}:
        angle=spec['pinion_index']*40;t=math.radians(angle)
        y=a['bank_center'] if role=='roller' else a['pin_start']
        translation=[a['roller_circle']*math.sin(t),side*y,a['roller_circle']*math.cos(t)]
        if role=='pin_assembly':rotation=[0,angle,0] if side==1 else [180,-angle,0]
    elif role=='pin':pass
    elif role=='cotter':translation[1]=a['cotter_from_inner_end']
    elif role=='pin_plug':translation[1]=a['pin_length']
    elif role=='shaft_outer_plug':translation[1]=a['shaft_end']
    elif role=='shaft_inner_plug':translation[1]=-a['shaft_end'];rotation=[180,0,0]
    elif role=='inner_bearing':rotation=[180,0,0]
    elif role=='bush':translation[1]=side*a['bush_center']
    elif role in {'bearing_screw','inner_rivet'}:
        x,z=bearing_points(m)[spec['pinion_index']]
        y=m['face'] if role=='bearing_screw' else -(a['shaft_end']+m['shell'])/2
        translation=[x,y,z]
    elif role=='backing_rivet':
        x,z=backing_points(m)[spec['pinion_index']]
        translation=[x,(m['outside']+m['shell']-m['backing_stock'])/2,z];rotation=[180,0,0]
    else:raise ValueError('Unknown pinion child datum '+role)
    return dict(parent=spec['parent'],translation=translation,rotation_deg=rotation)


def clearance(data):
    return dict(values=values(data),stations={label:station(data,hand)
                for label,hand in [('port',1),('starboard',-1)]})
