"""Scoped source counts, repeated stack equivalence and installed roller contacts."""
from collections import Counter, defaultdict
import itertools
import json
import re

from .evidence import STAGE, database, read, write


def group_id(identifier):
    return '_'.join(identifier.split('_')[:2])


def bearing_face(a,b):
    """Measure planar mating faces; solid common() discards zero-volume contact."""
    import Part
    area=0
    for fa in a.Faces:
        if not isinstance(fa.Surface,Part.Plane):continue
        normal=fa.normalAt(0,0)
        for fb in b.Faces:
            if not isinstance(fb.Surface,Part.Plane):continue
            if normal.cross(fb.normalAt(0,0)).Length>1e-7:continue
            if abs((fa.CenterOfMass-fb.CenterOfMass).dot(normal))>1e-6:continue
            area+=fa.common(fb).Area
    return a.distToShape(b)[0],area


def composition(data, ids):
    selected=[i for i in data['occurrences'] if i['id'] in ids]
    groups=defaultdict(list)
    for item in selected:groups[group_id(item['id'])].append(item)
    counts={'lower':Counter(), 'upper':Counter()}; stations=Counter()
    for group,items in groups.items():
        index=int(group.split('Unit')[1]);kind=data['roller_stations'][index]['kind']
        stations[(group.split('Rollers')[0],kind)]+=1
        scope='upper' if kind=='upper' else 'lower'
        for item in items:counts[scope].update(data['definitions'][item['definition']]['survey_ids'])
    expected_stations=Counter({(hand,kind):count for hand in ['Port','Starboard']
                               for kind,count in [('plain',15),('spring',14),('upper',1)]})
    if stations!=expected_stations:raise ValueError('Roller station count/scope mismatch')
    sources=read(STAGE/'data/roller_source_rows.json');result=[]
    with database() as connection:
        def row(record):
            return json.loads(connection.execute('SELECT raw_json FROM source_records WHERE record_id=?',(record,)).fetchone()[0])
        def identity(role,record):
            ids=data['definitions']['roller_'+role]['survey_ids']
            if len(ids)!=1 or not connection.execute('SELECT 1 FROM part_evidence WHERE part_id=? AND record_id=?',(ids[0],record)).fetchone():
                raise ValueError('Roller source identity mismatch '+role)
            return ids[0]
        for role,(mark,record) in sources.items():
            if role in {'upper','upper_plug','upper_support'}:continue
            pid=identity(role,record);raw=row(record);quantity=raw.get('qty','').strip()
            if quantity.isdigit():expected=int(quantity)
            else:
                numbers=re.findall(r'\((\d+)\)',raw['item'])
                if numbers:expected=int(numbers[-1])
                elif role in {'nut','washer'}:expected=116*2
                elif role=='plug':expected=58
                else:raise ValueError('Unresolved lower roller source count '+role)
            if counts['lower'][pid]!=expected:raise ValueError('Lower roller quantity mismatch: '+mark)
            result.append(dict(scope='SNL lower stations',role=role,record=record,expected=expected,actual=counts['lower'][pid]))
        # HB237 quantities are PER upper assembly. HB142 supplies two assemblies.
        upper_rows={'tube':43,'ring':44,'upper':45,'pin':46,'bush':47,'upper_plug':48,'ubolt':49}
        for role,number in upper_rows.items():
            record=f'HB:nomenclature:237:{number:03d}';pid=identity(role,record)
            expected=2*int(row(record)['quantity'])
            if counts['upper'][pid]!=expected:raise ValueError('Upper roller quantity mismatch: '+role)
            result.append(dict(scope='HB upper stations',role=role,record=record,expected=expected,actual=counts['upper'][pid]))
        for role in ['nut','washer']:
            record=sources[role][1];pid=identity(role,record);expected=8
            if counts['upper'][pid]!=expected:raise ValueError('Upper clamp hardware quantity mismatch: '+role)
            result.append(dict(scope='SNL clamp composition transferred to HB upper stations',role=role,
                               record=record,expected=expected,actual=counts['upper'][pid]))
        record='HB:nomenclature:221:019';pid=identity('upper_support',record)
        expected=int(row(record)['quantity'])
        if counts['upper'][pid]!=expected or counts['lower'][pid]:
            raise ValueError('Upper support quantity/scope mismatch: M2092')
        result.append(dict(scope='HB221 whole-tank upper supports',role='upper_support',record=record,
                           expected=expected,actual=counts['upper'][pid]))
    if sum(r['actual'] for r in result)!=len(selected):raise ValueError('Unaccounted roller component')
    return result


def validate(data,items,out):
    selected=[i for i in items if i['id'].startswith(('PortRollers_','StarboardRollers_'))]
    if not selected:return {'applicable':False}
    import numpy as np
    from .cad_build import frame
    from .worker import placement_errors
    from .roller_geometry import stations, values
    ids={i['id'] for i in selected};source_counts=composition(data,ids)
    # GUI display tessellation can make Shape.BoundBox underestimate a curved
    # solid. Force kernel bounds without triangulation for fit and size checks.
    native_boxes={i['id']:i['shape'].optimalBoundingBox(False) for i in items if i['representation']=='assembly'}
    groups=defaultdict(list)
    for item in selected:groups[group_id(item['id'])].append(item)
    representatives={};equivalent=0;internal_pairs=0;maximum=0
    for key,stack in sorted(groups.items()):
        index=int(key.split('Unit')[1]);kind=data['roller_stations'][index]['kind']
        family=(key.split('Rollers')[0],kind);root=frame(key,data)
        normalized={i['id'][len(key):]:(i['definition'],i['target'],root.inverse().multiply(i['shape'].Placement)) for i in stack}
        if family in representatives:
            original=representatives[family]
            if set(original)!=set(normalized):raise ValueError('Repeated roller stack lost components')
            for suffix,(definition,target,placement) in normalized.items():
                old_definition,old_target,old_placement=original[suffix]
                delta,rotation=placement_errors(placement,old_placement)
                if definition!=old_definition or target!=old_target or delta>1e-6 or rotation>1e-8:
                    raise ValueError('Repeated roller stack differs from contact-tested template: '+key+suffix)
            equivalent+=1
            continue
        representatives[family]=normalized
        for a,b in itertools.combinations(stack,2):
            if not native_boxes[a['id']].intersect(native_boxes[b['id']]):continue
            internal_pairs+=1;volume=a['shape'].common(b['shape']).Volume;maximum=max(maximum,volume)
            if volume>1e-5:raise ValueError(f"Roller internal overlap: {a['id']} / {b['id']}: {volume}")
    # Broad phase uses each installed native bounding box; narrow phase uses OCC.
    others=[i for i in items if i['representation']=='assembly' and i['id'] not in ids]
    candidates=others+selected
    def bounds(item):
        b=native_boxes[item['id']]
        return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
    boxes=np.array([bounds(i) for i in candidates]);external_pairs=interstation_pairs=0
    for a in selected:
        b=np.array(bounds(a))
        nearby=np.where(np.all(boxes[:,:3]<=b[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=b[:3]-1e-7,axis=1))[0]
        for index in nearby:
            other=candidates[index]
            if other['id'] in ids:
                if other['id']<=a['id'] or group_id(other['id'])==group_id(a['id']):continue
                interstation_pairs+=1
            else:external_pairs+=1
            volume=a['shape'].common(other['shape']).Volume;maximum=max(maximum,volume)
            if volume>1e-5:raise ValueError(f"Roller installed overlap: {a['id']} / {other['id']}: {volume}")
    wheels=[i for i in selected if i['definition'] in {'roller_lower','roller_upper'}]
    rails=[i for i in others if i['definition'] in {'track_link_left','track_link_right'}]
    gaps=[]
    if rails:
        rail_boxes=np.array([bounds(i) for i in rails])
        for wheel in wheels:
            b=np.array(bounds(wheel));expansion=data['values']['shoe_pitch'].value
            nearby=np.where(np.all(rail_boxes[:,:3]<=b[3:]+expansion,axis=1)&np.all(rail_boxes[:,3:]>=b[:3]-expansion,axis=1))[0]
            if not len(nearby):raise ValueError('No modeled rail near roller '+wheel['id'])
            gap,identifier=min((wheel['shape'].distToShape(rails[j]['shape'])[0],rails[j]['id']) for j in nearby)
            if gap<data['values']['roller_rail_gap'].value-1e-5:
                raise ValueError('Roller rail clearance below specified allowance '+wheel['id'])
            gaps.append(dict(roller=wheel['id'],rail=identifier,minimum_distance_mm=gap))
    targets={i['definition']:i['target'].Shape for i in selected};v=values(data)
    def length(role,axis,expected):
        actual=getattr(targets['roller_'+role].optimalBoundingBox(False),axis+'Length')
        if abs(actual-expected)>1e-5:raise ValueError('Roller controlled dimension mismatch: '+role+' '+axis)
        return dict(role=role,axis=axis,actual_mm=actual,expected_mm=expected)
    dimensions=[length('lower','X',v['roller_diameter']),length('lower','Y',v['roller_width']),
                length('upper','X',v['roller_diameter']),length('pin','Y',v['roller_pin_length']),
                length('tube','Y',v['tube_length']),length('spring','Y',v['roller_spring_length'])]
    stock_volume=v['roller_ring_stock_length']*v['roller_ring_radial']*v['roller_ring_axial']
    if abs(targets['roller_ring'].Volume-stock_volume)>1e-5:raise ValueError('Roller retaining ring stock volume changed')
    dimensions += [length('upper_support','X',v['roller_support_length']),
                   length('upper_support','Y',v['roller_support_width']),
                   length('upper_support','Z',v['roller_clamp_seat']-v['roller_pin_flat_height'])]
    # Zero overlap alone could hide floating clamps. Check the actual saved
    # native face contacts at the pin toe and all eight upper washers.
    by_id={i['id']:i for i in selected};support_seats=[];shell_proximity=[]
    hull=[i for i in others if i['definition'].startswith('hull_')]
    for support in [i for i in selected if i['definition']=='roller_upper_support']:
        prefix=group_id(support['id']);end=support['id'][-1]
        seat_ids=[prefix+'_PinAssembly_Pin']+[prefix+'_Clamp'+end+'_Washer'+leg for leg in ['A','B']]
        for key in seat_ids:
            other=by_id[key];distance,area=bearing_face(support['shape'],other['shape'])
            if distance>1e-6 or area<1:
                raise ValueError('Upper roller support lost its native bearing face: '+support['id']+' / '+key)
            support_seats.append(dict(support=support['id'],mate=key,gap_mm=distance,contact_area_mm2=area))
        if hull:
            box=native_boxes[support['id']]
            nearby=[i for i in hull if native_boxes[i['id']].XMin<=box.XMax+100
                    and native_boxes[i['id']].XMax>=box.XMin-100
                    and native_boxes[i['id']].YMin<=box.YMax+100
                    and native_boxes[i['id']].YMax>=box.YMin-100
                    and native_boxes[i['id']].ZMin<=box.ZMax+100
                    and native_boxes[i['id']].ZMax>=box.ZMin-100]
            if not nearby:raise ValueError('Upper support has no nearby modeled hull panel')
            distance,key=min((support['shape'].distToShape(i['shape'])[0],i['id']) for i in nearby)
            shell_proximity.append(dict(support=support['id'],nearest_hull=key,distance_mm=distance,
                                        attachment_qualified=False))
    result=dict(applicable=True,station_count=len(groups),component_occurrences=len(selected),source_quantities=source_counts,
                internal_templates_checked=len(representatives),repetitions_proven_equivalent=equivalent,
                internal_candidate_pairs=internal_pairs,external_candidate_pairs=external_pairs,
                interstation_candidate_pairs=interstation_pairs,other_physical_components_in_contact_scope=len(others),
                max_overlap_mm3=maximum,bounding_boxes='OCC optimal bounds with triangulation disabled',
                controlled_dimensions=dimensions,ring_stock_volume_mm3=stock_volume,
                upper_support_seats=support_seats,upper_support_shell_proximity=shell_proximity,
                rail_clearances=gaps,source_stations=stations(data),standard_configuration_only=True,
                historical_fit_qualified=False,continuous_rolling_qualified=False,supports_complete=False,
                limitations=['Source X/Z picks remain independent. Lower00 has an explicit rearward X offset for idler clearance; other X positions stay fixed. Z follows the fixed printed roller diameter and reconstructed rail envelope.',
                             'Spring printed outside diameter is interpreted as inside diameter; literal conflict remains recorded.',
                             'Curved shoulder profiles, upper roller width, spring plates, grooves, fits and fastener details are approximate.',
                             'Four upper angles have checked toe/washer contacts; angle dimensions, attachment holes and upper roof access reliefs are inferred.',
                             'Lower long angles and their 76 short bolts are checked separately; upper covers and unidentified removable retention plates remain unpopulated. Hull load path is not qualified.',
                             'The HB upper plug has its own M1410 identity; no equivalence to lower SNL Q52C is asserted.',
                             'Threads, ground spring ends, oil distribution details and suspension function remain unqualified.'])
    write(out/'reports/rollers.json',result)
    return result
