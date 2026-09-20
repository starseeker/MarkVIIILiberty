"""Independent source quantities and nominal installed upper-shell checks."""
from collections import Counter
import itertools
import json
import re
from .evidence import database,write
from .model import point

# Independent SNL rows, not copied from generated native occurrence metadata.
ROWS={
 'M2346':'SNL:264:017','M2347':'SNL:264:016','M2361':'SNL:151:014',
 'M2348':'SNL:150:015','M2349':'SNL:150:018','M2350':'SNL:150:014','M2351':'SNL:150:016',
 'M2353':'SNL:95:001','M2354':'SNL:133:018','M2355':'SNL:82:004','M2356':'SNL:81:034',
 'M2362':'SNL:150:024','M2363':'SNL:151:003','M2372':'SNL:150:028','M2373':'SNL:150:027',
 'M2406':'SNL:150:019','M2407':'SNL:150:017','M2352':'SNL:147:019',
 'M2387':'SNL:147:014','M2388':'SNL:147:013','M2389':'SNL:147:027'}


def composition(data,ids):
    counts=Counter(pid for i in data['occurrences'] if i['id'] in ids
                   for pid in data['definitions'][i['definition']]['survey_ids'])
    result=[]
    with database() as c:
        for mark,record in ROWS.items():
            matches=c.execute('SELECT DISTINCT part_id FROM part_identifiers WHERE identifier=?',(mark,)).fetchall()
            if len(matches)!=1:raise ValueError('Ambiguous upper part identity: '+mark)
            pid=matches[0][0]
            row=c.execute('SELECT description,raw_json FROM source_records WHERE record_id=?',(record,)).fetchone()
            raw=json.loads(row['raw_json']);numbers=re.findall(r'\((\d+)\)',raw.get('qty','') or row['description'])
            if len(numbers)!=1:raise ValueError('Unresolved upper quantity: '+mark)
            expected=int(numbers[0])
            if counts[pid]!=expected:raise ValueError('Upper SNL quantity mismatch: '+mark)
            result.append({'mark':mark,'record':record,'part_id':pid,'expected':expected,'actual':counts[pid]})
    if sum(x['actual'] for x in result)!=len(ids):raise ValueError('Unexpected upper plate occurrence')
    return result


def validate(data,items,out):
    upper=[i for i in items if i['definition'].startswith('upper_')]
    if not upper:return {'applicable':False}
    import FreeCAD as App
    import Part
    from .cad_build import frame
    ids={i['id'] for i in upper}
    source=composition(data,ids)
    tested=0;maximum=0
    for a,b in itertools.combinations(upper,2):
        if not a['shape'].BoundBox.intersect(b['shape'].BoundBox):continue
        tested+=1
        volume=a['shape'].common(b['shape']).Volume
        maximum=max(maximum,volume)
        if volume>1e-5:raise ValueError(f"Upper plate overlap: {a['id']} / {b['id']}: {volume} mm3")
    v={k:q.value for k,q in data['values'].items()}
    # HB43 explicitly orders side openings rear-to-front differently by hand.
    for side,kinds in [('port',['mount','pistol']),('starboard',['pistol','mount'])]:
        stations=[v['upper_rear_peep_station']]+[v['upper_'+side+'_'+kind+'_station'] for kind in kinds]+[v['upper_forward_peep_station'],v['upper_flap_station']]
        if any(a>=b for a,b in zip(stations,stations[1:])):
            raise ValueError('HB43 handed opening sequence mismatch: '+side)
    voids=[('upper_base',(0,0,v['upper_height']/2)),
           ('upper_driver_base',(v['driver_length']/2,0,v['driver_height']/2)),
           ('upper_lookout_base',(0,0,v['lookout_height']/2))]
    for datum,coords in voids:
        origin=frame(datum,data).multVec(App.Vector(*coords))
        probe=Part.makeBox(20,20,20,origin-App.Vector(10,10,10))
        if any(i['shape'].common(probe).Volume>1e-6 for i in upper):
            raise ValueError('Upper enclosure interior is filled: '+datum)
    # Sample material away from apertures; a 2x2 mm column must contain exactly
    # the printed normal thickness. This catches shell/stock orientation errors.
    probes=[('upper_port_main_flap','upper_base',(v['upper_flap_station'],v['main_turret_width']/2,v['upper_height']*.52),'y',v['upper_wall']),
            ('upper_port_driver_side','upper_driver_base',(v['driver_length']*.8,v['driver_width']/2,60),'y',v['driver_wall']),
            ('upper_port_lookout_side','upper_lookout_base',(0,v['lookout_width']/2,60),'y',v['lookout_wall']),
            ('upper_lookout_roof','upper_lookout_base',(0,100,v['lookout_height']),'z',v['lookout_roof']),
            ('upper_port_main_roof','upper_base',(0,v['main_turret_width']*.35,v['upper_height']),'z',v['upper_roof'])]
    measurements=[];byid={i['id']:i for i in upper}
    for key,datum,coords,axis,expected in probes:
        center=frame(datum,data).multVec(App.Vector(*coords))
        size=App.Vector(2,100,2) if axis=='y' else App.Vector(2,2,100)
        probe=Part.makeBox(size.x,size.y,size.z,center-size*.5)
        measured=byid[key]['shape'].common(probe).Volume/4
        if abs(measured-expected)>1e-5:raise ValueError(f'Wrong plate thickness: {key}: {measured}')
        measurements.append({'occurrence':key,'expected_mm':expected,'measured_mm':measured})
    raw=[point(data,'snl_2',p) for p in data['calibrations']['snl_2']['profiles']['main_enclosure']]
    trace_length=max(p[0] for p in raw)-min(p[0] for p in raw)
    trace_height=max(p[1] for p in raw)-min(p[1] for p in raw)
    report={'applicable':True,'plate_occurrences':len(upper),'source_identity_count':len(source),
            'source_quantities':source,'candidate_contact_pairs':tested,'max_overlap_mm3':maximum,
            'material_overlap_tolerance_mm3':1e-5,'hollow_enclosure_probes':3,'thickness_samples':measurements,
            'standard_closed_configuration_only':True,'HB43_handed_opening_order':True,'source_dimension_comparison':{
                'printed_main_length_mm':v['upper_length'],'traced_main_length_mm':trace_length,
                'length_difference_mm':v['upper_length']-trace_length,
                'printed_main_height_mm':v['upper_height'],'traced_main_height_mm':trace_height,
                'height_difference_mm':v['upper_height']-trace_height,
                'controlling_source':'HB35 printed dimensions; midpoint/base registered to unchanged SNL2 calibration',
                'image_refitted':False},
            'historical_fit_qualified':False,
            'limitations':['Source subset is armor plates/leaves, not complete upper assembly BOM.',
                           'Opening stations, unprinted sizes, seams and joints remain bounded approximations.',
                           'Planar aft roof bend, absent angles/hinges/covers/rivets and lower-hull attachment remain open.']}
    write(out/'reports/upper_plates.json',report)
    return report
