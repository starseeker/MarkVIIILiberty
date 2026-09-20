"""Pure-data roof frames and explicitly provisional louver section interpretation."""
import math


def layout(data, bank):
    from .model import point, datum_values
    if bank not in {'inlet', 'outlet'}:
        raise ValueError('Unknown louver bank ' + bank)
    v = {k: q.value for k, q in data['values'].items()}
    upper_z = datum_values('upper_base', data)['translation'][2]
    back = v['hull_engine_back_x']
    back_z = point(data, 'snl_2', [0, 335])[1]
    roof_front = v['hull_inlet_front_x'] + v['hull_roof_cross_strip']
    slope = (upper_z-back_z)/(roof_front-back)
    angle = math.atan(slope)
    cosine = math.cos(angle)
    front = v['hull_inlet_front_x']
    if bank == 'outlet':
        front -= v['hull_inlet_length'] + v['hull_roof_cross_strip'] + v['hull_engine_cover_length']
    rear = front-v['hull_'+bank+'_length']
    count = int(v['louver_'+bank+'_count'])
    if count != v['louver_'+bank+'_count'] or count < 2:
        raise ValueError('Invalid louver repetition count')
    t, r, height = (v[k] for k in ['louver_blade_thickness', 'louver_bend_radius', 'louver_blade_width'])
    # The 1/2-inch radius is provisionally the inside bend; 2.5-inch width
    # is the total roof-normal extent of a sideways chevron, not developed stock.
    center_y = height/2-(r+t)*math.sqrt(2)
    ymin, ymax = -t/math.sqrt(2), center_y+r+t
    available = v['hull_louver_width']-2*v['louver_edge_margin']
    pitch = (available-(ymax-ymin))/(count-1)
    if height/2 <= (r+t)/math.sqrt(2) or pitch/math.sqrt(2) <= t:
        raise ValueError('Louver section or blade spacing has no passage')
    first = -v['hull_louver_width']/2+v['louver_edge_margin']-ymin
    gap = v['louver_install_gap']
    return dict(bank=bank, length=v['hull_'+bank+'_length']/cosine,
                width=v['hull_louver_width'], slope=slope, cosine=cosine,
                angle_deg=math.degrees(angle), count=count, pitch=pitch, first=first,
                section_ymin=ymin, section_ymax=ymax,
                origin=[rear-gap*math.sin(angle), 0, back_z+(rear-back)*slope+gap*cosine],
                guard_height=v['louver_guard_height']*cosine,
                **{k: x for k, x in v.items() if k.startswith('louver_')})


def arguments(definition, data):
    spec = definition['arguments']
    a = layout(data, spec['bank'])
    a.update(role=spec['role'], hand=spec.get('hand', 0))
    return a


def datum(spec, data):
    a = layout(data, spec['louver_bank'])
    if 'blade_index' in spec:
        index = spec['blade_index']
        if type(index) is not int or not 0 <= index < a['count']:
            raise ValueError('Louver blade datum index out of range')
        return {'translation': [0, a['first']+index*a['pitch'], 0],
                'rotation_deg': [0, 0, 0], 'parent': spec['parent']}
    if 'packing_index' in spec:
        x = 16 if spec['packing_index'] == 0 else a['length']-56
        return {'translation': [x, a['width']/2-20, 86],
                'rotation_deg': [0, 0, 0], 'parent': spec['parent']}
    return {'translation': a['origin'], 'rotation_deg': [0, -a['angle_deg'], 0],
            'parent': spec['parent']}
