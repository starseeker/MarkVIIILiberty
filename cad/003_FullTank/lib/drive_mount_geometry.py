"""Derived drive-shaft support interfaces with explicit reconstruction controls."""
import math


def values(data):
    a={k.removeprefix('drive_mount_'):q.value for k,q in data['values'].items()
       if k.startswith('drive_mount_')}
    for key in ['hull_frame_clear','hull_side_thickness','wheel_boss_length',
                'idler_nut_stock','idler_nut_af','roller_oil_bore']:
        a[key]=data['values'][key].value
    a['end']=a['shaft_length']/2
    a['shell']=a['hull_frame_clear']/2
    a['outside']=a['shell']+a['hull_side_thickness']
    a['face']=a['end']-a['end_projection']-a['idler_nut_stock']
    a['shoulder']=a['wheel_boss_length']/2+a['boss_end_gap']
    a['flange_stock']=a['face']-a['outside']
    a['key_end']=a['face']-a['key_end_inset']
    a['key_start']=a['key_end']-a['key_length']
    a['key_bottom']=a['journal_diameter']/2-a['key_height']/2
    a['key_top']=a['journal_diameter']/2+a['key_height']/2
    a['lock_z']=-a['idler_nut_af']/2
    a['lock_center']=a['lock_z']-a['locking_plate_width']/2
    if not a['shoulder']<a['outside']<a['face']<a['end']:
        raise ValueError('Drive shaft length does not accommodate the support stack')
    return a


def arguments(definition,data):
    return {**values(data),**definition['arguments']}


def bearing_points(a):
    return [(a['bearing_bolt_radius']*math.sin(math.radians(30+n*60)),
             a['bearing_bolt_radius']*math.cos(math.radians(30+n*60))) for n in range(6)]


def backing_points(a):
    return [(a['backing_rivet_radius']*math.sin(math.radians(45+n*90)),
             a['backing_rivet_radius']*math.cos(math.radians(45+n*90))) for n in range(4)]


def child_datum(spec,data):
    a=values(data);role=spec['drive_mount_child'];side=spec.get('drive_mount_side',1)
    tr=[0,0,0];rot=[0,0,0]
    if role=='hand_frame':
        # Rotate the complete mounting unit to put the keyed journal outboard.
        rot=[0,0,0] if spec['parent'].startswith('Port') else [180,0,0]
    elif role in {'shaft','key','backing_plate'}:pass
    elif role=='bearing':rot=[0,0,0] if side==1 else [0,0,180]
    elif role in {'nut','locking_plate'}:
        tr[1]=side*a['face'];rot=[0,0,0] if side==1 else [0,0,180]
    elif role=='locking_screw':
        tr=[a['locking_screw_x'],side*(a['face']+a['locking_stock']),side*a['lock_center']]
        rot=[0,0,0] if side==1 else [0,0,180]
    elif role=='oil_plug':tr[1]=a['end'];rot=[0,0,180]
    elif role=='bearing_screw':
        x,z=bearing_points(a)[spec['drive_mount_index']];tr=[x,a['face'],z]
    elif role=='inner_rivet':
        x,z=bearing_points(a)[spec['drive_mount_index']]
        tr=[x,-(a['face']+a['shell'])/2,-z]
    elif role=='backing_rivet':
        x,z=backing_points(a)[spec['drive_mount_index']]
        tr=[x,(a['outside']+a['shell']-a['backing_stock'])/2,z];rot=[0,0,180]
    else:raise ValueError('Unknown drive mounting child '+role)
    return dict(translation=tr,rotation_deg=rot,parent=spec['parent'])


def clearance(data):
    from lib.model import datum_values
    return dict(values=values(data),stations={hand:datum_values(hand+'_drive',data)['translation']
                for hand in ['port','starboard']})
