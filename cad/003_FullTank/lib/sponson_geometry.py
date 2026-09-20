"""Resolve standard sponson inputs without importing the CAD runtime."""
from .model import point


def arguments(definition,data):
    source=definition['arguments'];h=source['hand']
    if h not in (-1,1):raise ValueError('Sponson hand must be -1 or 1')
    v={k:q.value for k,q in data['values'].items()}
    x0,z1=point(data,'snl_2',[510,270]);x1,z0=point(data,'snl_2',[790,440])
    gap=v['sponson_install_gap']
    wall=(v['track_centers']+v['hull_frame_clear'])/2+v['hull_side_thickness']
    result={k:x for k,x in v.items() if k.startswith('sponson_plate_')}
    result.update(role=source['role'],hand=h,length=x0-x1-2*gap,height=z1-z0-2*gap,
                  depth=v['vehicle_width']/2-wall-gap,
                  peep_length=v['upper_peep_length'],peep_height=v['upper_peep_height'],
                  pistol_length=v['upper_pistol_length'],pistol_height=v['upper_pistol_height'])
    if min(result[k] for k in ['length','height','depth'])<=0:raise ValueError('Sponson envelope has no room')
    return result
