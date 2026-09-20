"""Source counts, native seats and material checks for partial lower supports."""
from collections import Counter
import json
import re
from .evidence import STAGE,read,write,database


def composition(data, selected):
    sources=read(STAGE/'data/lower_support_source_rows.json');counts=Counter()
    with database() as connection:
        for item in selected:
            definition=data['definitions'][item['definition']]
            ids=definition['survey_ids']
            if len(ids)!=1:raise ValueError('Lower support requires one preserved source identity')
            counts.update(ids)
        result=[];raw_by_mark={}
        for mark,entry in sources.items():
            row=connection.execute('SELECT raw_json FROM source_records WHERE record_id=?',(entry['record'],)).fetchone()
            if not row or not connection.execute('SELECT 1 FROM part_evidence WHERE part_id=? AND record_id=?',
                (entry['survey_id'],entry['record'])).fetchone():raise ValueError('Lower support source identity changed: '+mark)
            raw=json.loads(row[0]);raw_by_mark[mark]=raw
            expected=int(raw['qty'].strip('() '));actual=counts.pop(entry['survey_id'],0)
            if actual!=expected:raise ValueError('Lower support source quantity changed: '+mark)
            result.append(dict(mark=mark,record=entry['record'],expected=expected,actual=actual))
        if counts:raise ValueError('Unaccounted lower support source components')
        bolt_mark=next(mark for mark,entry in sources.items() if entry['record']=='SNL:31:001')
        allocations={mark:int(count) for mark,count in
                     re.findall(r'angle\s+(M\d+[A-Z]?)\s+\((\d+)\)',raw_by_mark[bolt_mark]['item'])}
        if set(allocations)!=set(sources)-{bolt_mark}:
            raise ValueError('Lower support bolt allocation source is incomplete')
        bolt_counts=Counter(i['id'].rsplit('_',1)[0] for i in selected
                            if i['definition']=='lower_support_attachment_bolt')
        for entry in result:
            mark=entry['mark']
            if mark==bolt_mark:continue
            angles=[i for i in selected if sources[mark]['survey_id'] in
                    data['definitions'][i['definition']]['survey_ids']]
            entry['installation_bolt_allocations']=[]
            for angle in angles:
                name=angle['id'].rsplit('_',1)[0];actual=bolt_counts.pop(name,0)
                if actual!=allocations[mark]:
                    raise ValueError('Lower support bolt allocation differs from SNL31: '+name)
                entry['installation_bolt_allocations'].append(
                    dict(installation=name,record='SNL:31:001',expected=allocations[mark],actual=actual))
        if bolt_counts:raise ValueError('Lower support bolt allocation has no matching angle')
    return result


def validate(data,items,out):
    selected=[i for i in items if i['id'].startswith(('PortLowerSupports_','StarboardLowerSupports_'))]
    if not selected:return {'applicable':False}
    import numpy as np
    import math
    import Part
    from .lower_support_geometry import installations,values
    from .roller_validation import bearing_face
    source=composition(data,selected);by_id={i['id']:i for i in items};v=values(data)
    physical=[i for i in items if i['representation']=='assembly']
    def bounds(item):
        b=item['shape'].optimalBoundingBox(False)
        return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
    boxes=np.array([bounds(i) for i in physical]);ids={i['id'] for i in selected}
    tested=0;maximum=0
    for a in selected:
        b=np.array(bounds(a))
        near=np.where(np.all(boxes[:,:3]<=b[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=b[:3]-1e-7,axis=1))[0]
        for index in near:
            other=physical[index]
            if other['id'] in ids and other['id']<=a['id']:continue
            tested+=1;volume=a['shape'].common(other['shape']).Volume;maximum=max(maximum,volume)
            if volume>1e-5:raise ValueError(f"Lower support overlap: {a['id']} / {other['id']}: {volume}")
    seats=[];hull_seats=[];dimensions=[];receivers=[]
    hull=[i for i in items if i['definition'].startswith('hull_')]
    def near(a,b):
        x=np.array(bounds(a));y=np.array(bounds(b))
        return np.all(x[:3]<=y[3:]+1e-7) and np.all(x[3:]>=y[:3]-1e-7)
    def seat(support,mate,kind):
        if mate not in by_id:return
        gap,area=bearing_face(by_id[support]['shape'],by_id[mate]['shape'])
        if gap>1e-6 or area<1:raise ValueError('Lower support bearing face lost: '+support+' / '+mate)
        seats.append(dict(support=support,mate=mate,kind=kind,gap_mm=gap,area_mm2=area))
    for installation in installations(data):
        name=installation['id'];support=name+'_Angle'
        if support not in by_id:raise ValueError('Missing lower support occurrence: '+support)
        spec=data['lower_support_runs'][installation['run']]
        end='B' if installation['end']==1 else 'A'
        for index in spec['stations']:
            prefix=f"{installation['hand']}Rollers_Unit{index:03d}"
            seat(support,prefix+'_PinAssembly_Pin','pin toe')
            for leg in ['A','B']:seat(support,prefix+f'_Clamp{end}_Washer{leg}','washer flange')
        for index in range(spec['bolts']):
            bolt_id=name+f'_Bolt{index:02d}';seat(support,bolt_id,'bolt head')
            if hull:
                bolt=by_id[bolt_id];contacts=[]
                cylinder_faces=[f for f in bolt['shape'].Faces if isinstance(f.Surface,Part.Cylinder)]
                for other in hull:
                    if not near(bolt,other):continue
                    area=sum(f.common(g).Area for f in cylinder_faces for g in other['shape'].Faces
                             if isinstance(g.Surface,Part.Cylinder)
                             and abs(g.Surface.Radius-v['lower_support_bolt_diameter']/2)<1e-6)
                    if area>1:contacts.append(dict(hull=other['id'],cylindrical_contact_area_mm2=area))
                length=sum(r['cylindrical_contact_area_mm2'] for r in contacts)/(math.pi*v['lower_support_bolt_diameter'])
                if length<v['hull_skirt_thickness']-1e-5:
                    raise ValueError('Lower attachment has insufficient modeled receiving wall: '+bolt_id+f' length={length}')
                receivers.append(dict(bolt=bolt_id,receiving_faces=contacts,equivalent_full_cylinder_length_mm=length,
                                      thread_engagement_qualified=False))
        if hull:
            a=by_id[support]['shape'];contacts=[]
            for other in hull:
                if not near(by_id[support],other):continue
                gap,area=bearing_face(a,other['shape'])
                if area>1:contacts.append(dict(hull=other['id'],gap_mm=gap,area_mm2=area))
            if not contacts:raise ValueError('Lower angle is detached from all hull material: '+support)
            hull_seats.append(dict(support=support,contacts=contacts,thread_engagement_qualified=False))
        if installation['run'] in {'05short','05long'}:
            target=by_id[support]['target'].Shape;expected=v['lower_support_'+('short' if installation['run']=='05short' else 'long')+'_length']
            actual=target.optimalBoundingBox(False).XLength
            if abs(actual-expected)>1e-6:raise ValueError('Printed lower support length changed: '+support)
            dimensions.append(dict(support=support,actual_mm=actual,expected_mm=expected))
    bolt=next(i['target'].Shape for i in selected if i['definition']=='lower_support_attachment_bolt')
    length=bolt.optimalBoundingBox(False).YLength
    expected=v['lower_support_bolt_length']+v['lower_support_bolt_head_height']
    if abs(length-expected)>1e-6:raise ValueError('Lower support bolt stock length changed')
    report=dict(applicable=True,component_occurrences=len(selected),source_quantities=source,
        material_candidate_pairs=tested,maximum_overlap_mm3=maximum,bearing_faces=seats,
        hull_seats=hull_seats,receiving_hull_bores=receivers,printed_lengths=dimensions,bolt_overall_length_mm=length,
        implemented_checks_passed=True,historical_fit_qualified=False,retention_complete=False,
        manufacturing_form_qualified=False,thread_engagement_qualified=False,
        limitations=['Rear No8 station ownership and reflected construction variants are inferred.',
                     'Runs 4/8 have cubic transitions fitted to installed pin seats; constant normal stock is not established.',
                     'Tapped receiving shell is a working approximation; HB144 removable plates remain unidentified.'])
    write(out/'reports/lower_supports.json',report)
    return report
