"""Independent hull part quantities and installed plate/interface checks."""
from collections import Counter
import json
import re
from .evidence import STAGE,database,read,write


def composition(data,ids):
    rows=read(STAGE/'data/hull_source_rows.json')
    counts=Counter(pid for i in data['occurrences'] if i['id'] in ids
                   for pid in data['definitions'][i['definition']]['survey_ids'])
    report=[]
    with database() as c:
        for mark,record in rows.items():
            found=c.execute('SELECT DISTINCT part_id FROM part_identifiers WHERE identifier=?',(mark,)).fetchall()
            if len(found)!=1:raise ValueError('Ambiguous hull identity: '+mark)
            pid=found[0][0]
            if not c.execute('SELECT 1 FROM part_evidence WHERE part_id=? AND record_id=?',(pid,record)).fetchone():
                raise ValueError('Hull quantity row belongs to a different part: '+mark)
            row=c.execute('SELECT description,raw_json FROM source_records WHERE record_id=?',(record,)).fetchone()
            raw=json.loads(row['raw_json']);qty=raw.get('qty','').strip()
            numbers=[qty] if qty.isdigit() else re.findall(r'\((\d+)\)',qty or row['description'])
            if len(numbers)!=1:raise ValueError('Unresolved hull source quantity: '+mark)
            expected=int(numbers[0])
            if counts[pid]!=expected:raise ValueError('Hull SNL quantity mismatch: '+mark)
            report.append({'mark':mark,'record':record,'part_id':pid,'expected':expected,'actual':counts[pid]})
    if sum(x['actual'] for x in report)!=len(ids):raise ValueError('Unexpected hull source identity')
    return report


def validate(data,items,out):
    hull=[i for i in items if i['definition'].startswith('hull_')]
    if not hull:return {'applicable':False}
    import FreeCAD as App
    import Part
    import numpy as np
    ids={i['id'] for i in hull};source=composition(data,ids)
    upper=[i for i in items if i['definition'].startswith('upper_')]
    tracks=[i for i in items if i['definition'].startswith('track_') and i['representation']=='assembly']
    checks=0;maximum=0.0
    candidates=hull+upper+tracks
    def bounds(item):
        b=item['shape'].optimalBoundingBox(False)
        return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
    # Compute native bounds once. Repeatedly requesting every plate/track box
    # made finer source contours unnecessarily expensive and depended on meshes.
    native_bounds={i['id']:bounds(i) for i in candidates}
    boxes=np.array([native_bounds[i['id']] for i in candidates])
    for a in hull:
        box=np.array(native_bounds[a['id']])
        near=np.where(np.all(boxes[:,:3]<=box[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=box[:3]-1e-7,axis=1))[0]
        for index in near:
            b=candidates[index]
            if b['id'] in ids and b['id']<=a['id']:continue
            checks+=1;vol=a['shape'].common(b['shape']).Volume
            maximum=max(maximum,vol)
            if vol>1e-5:raise ValueError(f"Hull material overlap: {a['id']} / {b['id']}: {vol} mm3")
    v={k:q.value for k,q in data['values'].items()};byid={i['id']:i for i in hull}
    gaps=[]
    for side in ['port','starboard']:
        a=byid['hull_'+side+'_inner_skirt_front']['shape'].BoundBox
        b=byid['hull_'+side+'_outer_skirt_front']['shape'].BoundBox
        gap=b.YMin-a.YMax if side=='port' else a.YMin-b.YMax
        if abs(gap-v['hull_frame_clear'])>1e-6:raise ValueError('HB141 lower shell spacing mismatch: '+side)
        gaps.append({'side':side,'clear_mm':gap})
    flat_floor=byid['hull_floor_4']['shape'].BoundBox
    if abs(flat_floor.ZMin-v['hull_ground_clearance'])>1e-6:raise ValueError('Printed hull ground clearance lost')
    probes=[('fighting room',(5600,0,1200)),('engine room',(3000,0,1100)),('front bay',(7800,0,1800)),
            ('fuel compartment',(1000,0,1000)),('port roller housing',(3000,v['track_centers']/2,350)),
            ('starboard roller housing',(3000,-v['track_centers']/2,350))]
    for label,coords in probes:
        probe=Part.makeBox(40,40,40,App.Vector(*coords)-App.Vector(20,20,20))
        if any(i['shape'].common(probe).Volume>1e-6 for i in hull):raise ValueError('Hull cavity filled: '+label)
    # Check both intended roof ventilation apertures at their independent printed widths/lengths.
    roof_front=v['hull_inlet_front_x']+v['hull_roof_cross_strip'];engine_back=v['hull_engine_back_x']
    from .model import point,datum_values
    roof_z=datum_values('upper_base',data)['translation'][2];back_z=point(data,'snl_2',[1480,335])[1]
    inlet_rear=v['hull_inlet_front_x']-v['hull_inlet_length']
    outlet_front=inlet_rear-v['hull_roof_cross_strip']-v['hull_engine_cover_length']
    openings=[]
    for name,front,length in [('inlet',v['hull_inlet_front_x'],v['hull_inlet_length']),('outlet',outlet_front,v['hull_outlet_length'])]:
        cx=front-length/2;zz=back_z+(cx-engine_back)*(roof_z-back_z)/(roof_front-engine_back)
        from .upper_parts import prism
        z_at=lambda x:back_z+(x-engine_back)*(roof_z-back_z)/(roof_front-engine_back)
        x0,x1=front-length+1,front-1;w=v['hull_louver_width']/2-1
        probe=prism([(x0,-w,z_at(x0)-15),(x1,-w,z_at(x1)-15),(x1,w,z_at(x1)-15),(x0,w,z_at(x0)-15)],(0,0,30))
        if any(i['shape'].common(probe).Volume>1e-5 for i in hull):raise ValueError('Roof louver opening obstructed: '+name)
        openings.append({'name':name,'longitudinal_length_mm':length,'width_mm':v['hull_louver_width']})
    result={'applicable':True,'plate_occurrences':len(hull),'source_identity_count':len(source),'source_quantities':source,
            'candidate_material_pairs':checks,'max_overlap_mm3':maximum,'overlap_tolerance_mm3':1e-5,
            'upper_and_track_components_in_contact_scope':len(upper)+len(tracks),'lower_shell_gaps':gaps,
            'floor_ground_clearance_mm':flat_floor.ZMin,'empty_cavity_probes':len(probes),'louver_openings':openings,
            'door_width_source_difference_mm':v['hull_door_printed_opening_width']-(v['hull_door_leaf_width']+2*v['hull_door_gap']),
            'complete_hull_verified':False,'historical_fit_qualified':False,
            'limitations':['Subset source quantities do not constitute a complete hull BOM.',
                'Source outline remains polygonal; internal seams and openings are inferred.',
                'Unmodeled braces, angles, roof strips, mud chutes, fastening and local mating gaps remain open.',
                'HB39/HB43 door scope and inner-shell centering assumption remain unresolved.']}
    write(out/'reports/hull_plates.json',result)
    return result
