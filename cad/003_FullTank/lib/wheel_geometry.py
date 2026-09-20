"""Source-common wheel dimensions and the independently adjusted idler station."""
import math


def values(data):
    return {k:q.value for k,q in data['values'].items()
            if k.startswith(('wheel_', 'idler_', 'drive_')) or k in {'track_channel_spacing','track_bush_outer'}}


def arguments(definition,data):
    return {**values(data),**definition['arguments']}


def station(data):
    from scipy.optimize import brentq
    from .model import point
    from .track_path import solve
    pins=solve(data)['pins'];v=values(data)
    from .idler_geometry import axis
    x,z,angle=axis(data)
    radius=v['idler_diameter']/2+data['values']['track_bush_outer'].value/2
    key=(tuple(map(tuple,pins)),x,z,angle,radius,v['idler_static_gap'],v['idler_adjustment_limit'])
    if data.get('_idler_station_cache',(None,))[0]==key:return data['_idler_station_cache'][1]
    def gap(travel):
        return min(math.hypot(px-x-travel*math.cos(angle),pz-z-travel*math.sin(angle)) for px,pz in pins)-radius-v['idler_static_gap']
    # Move along the independently picked screw axis. This static fit does not
    # qualify historical adjustment travel or track tension.
    limit=v['idler_adjustment_limit']
    travel=brentq(gap,-limit,limit,xtol=1e-10)
    dx,dz=travel*math.cos(angle),travel*math.sin(angle)
    result=dict(x=x+dx,z=z+dz,source_x=x,source_z=z,x_offset=dx,z_offset=dz,
                travel=travel,axis_angle_deg=math.degrees(angle),
                interpretation='provisional narrow rim on track bushing',travel_qualified=False)
    data['_idler_station_cache']=(key,result)
    return result


def datum(spec,data):
    from .parameters import scalar
    st=station(data)
    return dict(translation=[st['x'],scalar(spec['source_point']['y'],data['values']),st['z']],
                rotation_deg=spec['rotation_deg'],parent=spec['parent'])


def joint_points(a):
    """Local +Z diaphragm, revolved about Y; explicit inferred rivet allocation."""
    short=[(a['wheel_short_tangent']*(-1 if i==1 else 1),r)
           for i,r in enumerate([a['wheel_short_radius']+i*a['wheel_short_pitch'] for i in range(3)])]
    long=[(s*a['wheel_long_tangent'],a['wheel_long_radius']) for s in [-1,1]]
    return short,long


def rotate_point(x,z,angle):
    angle=math.radians(angle)
    return x*math.cos(angle)+z*math.sin(angle),z*math.cos(angle)-x*math.sin(angle)


def rivets(a):
    result=[];short,long=joint_points(a)
    face=a['wheel_rim_center']-a['wheel_rim_width']/2+a['wheel_rim_land_stock']
    for side in [-1,1]:
        for n in range(6):
            for role,points,grip in [('short',short,a['wheel_disk_stock']+a['wheel_flange_stock']),
                                      ('long',long,a['wheel_disk_stock']+a['wheel_flange_stock']+a['wheel_boss_flange_stock'])]:
                for j,(x,z) in enumerate(points):
                    x,z=rotate_point(x,z,n*60)
                    result.append(dict(id=f'{role}_{side}_{n}_{j}',role=role,
                        translation=[x,side*(face+a['wheel_disk_stock']-grip/2),z],
                        rotation_deg=[0,0,0] if side==1 else [0,0,180],grip=grip))
        for n in range(24):
            x,z=rotate_point(0,a['wheel_rim_rivet_radius'],7.5+n*15)
            grip=a['wheel_disk_stock']+a['wheel_rim_land_stock']
            result.append(dict(id=f'rim_{side}_{n}',role='rim',translation=[x,side*(face+a['wheel_disk_stock']-grip/2),z],
                               rotation_deg=[0,0,0] if side==1 else [0,0,180],grip=grip))
    return result


def child_datum(spec,data):
    a=values(data);role=spec['wheel_child'];side=spec.get('wheel_side',1)
    face=a['wheel_rim_center']-a['wheel_rim_width']/2+a['wheel_rim_land_stock']
    tr=[0,0,0];rot=[0,0,0] if side==1 else [0,0,180]
    if role in {'rim','drive_rim'}:
        tr[1]=side*a['wheel_rim_center']
        if role=='drive_rim' and side==-1:
            # Axial reversal about Z preserves the +Z groove phase. Reversing
            # about X would stagger the two odd-tooth rings by half a pitch.
            rot=[180,0,0]
    elif role=='disk':
        tr[1]=side*(face+a['wheel_disk_stock']/2)
        # The plate itself is axially symmetric. Keep its staggered drill pattern
        # aligned with the two flanges of the same diaphragm.
        rot=[0,0,0]
    elif role=='bush':tr[1]=side*(a['wheel_boss_length']-a['wheel_bush_length'])/2
    elif role=='diaphragm':rot=[0,spec['wheel_angle'],0]
    elif role=='rivet':
        rivet=next(r for r in rivets(a) if r['id']==spec['wheel_rivet'])
        tr,rot=rivet['translation'],rivet['rotation_deg']
    else:raise ValueError('Unknown wheel child '+role)
    return dict(translation=tr,rotation_deg=rot,parent=spec['parent'])
