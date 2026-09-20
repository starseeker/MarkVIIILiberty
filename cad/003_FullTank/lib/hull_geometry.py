"""Pure-data inputs for the standard hull shell reconstruction."""
from .model import point,datum_values


def arguments(definition,data):
    spec=definition['arguments']
    if spec['hand'] not in {-1,0,1} or type(spec['index']) is not int:
        raise ValueError('Invalid hull handedness/index')
    if spec['role']=='floor' and spec['index'] not in range(1,9):
        raise ValueError('Invalid numbered floor')
    wanted={k for k in data['values'] if k.startswith('hull_')}
    wanted.update(['track_centers','main_turret_width','upper_wall','upper_length',
                   'driver_length','driver_width','driver_wall'])
    v={k:data['values'][k].value for k in sorted(wanted)}
    v['upper_base_x'],_,v['upper_base_z']=datum_values('upper_base',data)['translation']
    origin=point(data,'snl_2',[0,0]);p=point(data,'snl_2',[1,1])
    from .roller_geometry import stations, values, ring_dimensions, ring_station
    rollers=stations(data)
    rv=values(data)
    from .idler_geometry import clearance
    from .lower_support_geometry import hull_holes
    outline=[]
    for q in data['calibrations']['snl_2']['profiles']['hull']:
        x,z=point(data,'snl_2',q)
        # Preserve the source pick; expose the small installed nose clearance
        # correction separately instead of silently changing image calibration.
        if q==[108,310]:x-=v['hull_nose_clearance_setback']
        outline.append([x,z])
    return {**definition['arguments'],'values':v,'image_origin_xz':origin,
            'idler_clearance':clearance(data),
            'lower_support_holes':hull_holes(data),
            'roller_clearance':{'stations':[{k:s[k] for k in ['id','kind','x','z']} for s in rollers],
                'pin_radius':(data['values']['roller_pin_diameter'].value+data['values']['roller_hull_bore_clearance'].value)/2,
                'tube_radius':data['values']['tube_od'].value/2+1,
                'wheel_radius':data['values']['roller_diameter'].value/2+1,
                'wheel_width':data['values']['roller_width'].value+2,
                'wheel_offset':data['values']['roller_center_offset'].value,
                'ring_offset':ring_station(rv),'ring_radius':ring_dimensions(rv)[1]+1,
                'ring_width':rv['roller_ring_axial']+2,
                'clamp_offset':rv['hull_frame_clear']/2+rv['hull_side_thickness']+rv['roller_ubolt_diameter']/2+rv['roller_clamp_gap'],
                'clamp_leg_x':rv['roller_pin_diameter']/2+rv['roller_ubolt_clearance']+rv['roller_ubolt_diameter']/2,
                'clamp_leg_radius':rv['roller_ubolt_diameter']/2+1,
                'clamp_top':rv['roller_ubolt_top'],
                'support_offset':rv['hull_frame_clear']/2+rv['hull_side_thickness'],
                'support_length':rv['roller_support_length'],
                'support_width':rv['roller_support_width'],
                'support_toe':rv['roller_pin_flat_height'],
                'tube_length':data['values']['tube_length'].value+2},
            'pixel_scale_xz':[p[i]-origin[i] for i in range(2)],
            'outline':outline}
