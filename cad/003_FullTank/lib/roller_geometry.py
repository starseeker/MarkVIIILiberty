"""Source station picks, fixed-diameter rail clearance and roller geometry inputs."""
import math


def values(data):
    names=['roller_diameter','roller_width','roller_bore_clearance','roller_waist_radius',
           'roller_flange_width','roller_center_offset','tube_length','tube_od','tube_id',
           'hull_frame_clear','hull_side_thickness','track_channel_spacing']
    return {k:q.value for k,q in data['values'].items() if k in names or k.startswith('roller_')}


def capsule_boundary(x,a,b,r,upper):
    """Vertical extrema of a 2D line-segment capsule at a fixed X."""
    sign=1 if upper else -1; candidates=[]
    for px,pz in [a,b]:
        if abs(x-px)<=r:candidates.append(pz+sign*math.sqrt(max(0,r*r-(x-px)**2)))
    dx,dz=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dz)
    if abs(dx)>1e-10:
        slope=dz/dx;z=a[1]+slope*(x-a[0])+sign*r*math.sqrt(1+slope*slope)
        fraction=((x-a[0])*dx+(z-a[1])*dz)/(length*length)
        if 0<=fraction<=1:candidates.append(z)
    return (max(candidates) if upper else min(candidates)) if candidates else None


def stations(data):
    from .track_path import solve
    from .model import point
    path=solve(data);v=values(data)
    key=(tuple(map(tuple,path['pins'])),v['roller_diameter'],v['roller_rail_gap'],
         data['values']['track_eye_radius'].value,str(data['roller_stations']),
         tuple(data['values'][s['x_adjustment_parameter']].value for s in data['roller_stations'] if s.get('x_adjustment_parameter')))
    if data.get('_roller_station_cache',(None,))[0]==key:return data['_roller_station_cache'][1]
    r=v['roller_diameter']/2+data['values']['track_eye_radius'].value+v['roller_rail_gap']
    pins=path['pins'];result=[]
    for spec in data['roller_stations']:
        x,source_z=point(data,'snl_2',spec['pixel']);upper=spec['kind']=='upper'
        source_x=x
        # Coupled front-wheel fit. Keep the independent source pick visible;
        # do not silently move the traced point or rescale the track.
        x_offset=data['values'][spec['x_adjustment_parameter']].value if spec.get('x_adjustment_parameter') else 0
        x+=x_offset
        candidates=[]
        for index,(a,b) in enumerate(zip(pins,pins[1:]+pins[:1])):
            tx=(b[0]-a[0])/path['pitch_mm']
            if (tx<-.25 if upper else tx>.25):
                z=capsule_boundary(x,a,b,r,not upper)
                if z is not None:candidates.append((z,index))
        if not candidates:raise ValueError('No track rail near roller station '+spec['id'])
        z,index=(min(candidates) if upper else max(candidates))
        result.append({**spec,'x':x,'z':z,'source_x':source_x,'x_offset':x_offset,
                       'source_z':source_z,'z_offset':z-source_z,'contact_unit':index})
    data['_roller_station_cache']=(key,result)
    return result


def datum(spec,data):
    st=next(s for s in stations(data) if s['id']==spec['roller_station'])
    from .lower_support_geometry import station_angle
    index=next(i for i,s in enumerate(data['roller_stations']) if s['id']==st['id'])
    return {'translation':[st['x'],0,st['z']],'rotation_deg':[0,-station_angle(data,index),0],'parent':spec['parent']}


def arguments(definition,data):
    return {**values(data),**definition['arguments']}


def ring_dimensions(a):
    mean=(a['roller_ring_stock_length']+a['roller_ring_gap'])/(2*math.pi)
    radial=a['roller_ring_radial'];axial=a['roller_ring_axial']
    return mean-radial/2,mean+radial/2,axial,360*a['roller_ring_stock_length']/(2*math.pi*mean)


def ring_station(a):
    return a['roller_center_offset']+a['roller_width']/2+a['roller_axial_gap']+a['roller_ring_axial']/2
