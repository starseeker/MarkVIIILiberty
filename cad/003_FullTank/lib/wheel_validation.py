"""Source-scoped wheel counts, native seats and static installed clearance."""
from collections import Counter
import math
import json
from .evidence import STAGE,read,write,database


def composition(data,selected):
    from .track_validation import source_composition
    import re
    checks=[c for c in source_composition(data) if c['template'].startswith(('idler_','drive_'))]
    idler={'wheel_'+k:v for k,v in read(STAGE/'data/wheel_source_rows.json').items()}
    idler.update(read(STAGE/'data/idler_source_rows.json'))
    drive=read(STAGE/'data/drive_source_rows.json');result=[];totals=[]
    with database() as c:
        for family,rows,records in [('Idler',idler,['SNL:274:023','SNL:214:021']),
                                    ('Drive',drive,['SNL:275:005','SNL:215:001'])]:
            if not any(i['id'].startswith(('Port'+family+'_','Starboard'+family+'_')) for i in selected):continue
            for record in records:
                raw=json.loads(c.execute('SELECT raw_json FROM source_records WHERE record_id=?',(record,)).fetchone()[0])
                if int(raw['qty'].strip('() '))!=2:raise ValueError('Whole-vehicle wheel/shaft assembly count changed')
            for hand in ['Port','Starboard']:
                counts=Counter(i['definition'] for i in selected if i['id'].startswith(hand+family+'_'))
                expected=Counter({role:r['per_'+family.lower()] for role,r in rows.items()})
                if counts!=expected:raise ValueError(f'{family} constituent count mismatch: {hand}')
                for role,row in rows.items():
                    ids=data['definitions'][role]['survey_ids']
                    if len(ids)!=1 or not c.execute('SELECT 1 FROM part_evidence WHERE part_id=? AND record_id=?',(ids[0],row['record'])).fetchone():
                        raise ValueError('Wheel source identity mismatch: '+role)
                result.append(dict(hand=hand,family=family,modeled_leaves=sum(counts.values()),counts=dict(counts)))
        if any(i['id'].startswith(('PortIdler_','StarboardIdler_')) for i in selected):
            for role in ['bracket','plate','guard','adjusting_screw','washer','copper','cap_screw']:
                record=idler['idler_'+role]['record']
                raw=json.loads(c.execute('SELECT raw_json FROM source_records WHERE record_id=?',(record,)).fetchone()[0])
                actual=sum(i['definition']=='idler_'+role for i in selected)
                if actual!=int(raw['qty'].strip('() ')):raise ValueError('Whole-vehicle adjuster source count mismatch: '+role)
            raw=json.loads(c.execute('SELECT raw_json FROM source_records WHERE record_id=?',('SNL:170:003',)).fetchone()[0])
            if 'M1962B (5)' not in raw['item'] or 'M1962A (5)' not in raw['item']:
                raise ValueError('Scoped reinforcement rivet allocation changed')
        # Parenthesized quantities on these source rows are whole-vehicle
        # totals, not counts to duplicate independently for each wheel family.
        if len(result)==4:
            for role in ['wheel_boss','wheel_disk','wheel_diaphragm_x','wheel_diaphragm_y','drive_rim']:
                record=drive[role]['record']
                raw=json.loads(c.execute('SELECT raw_json FROM source_records WHERE record_id=?',(record,)).fetchone()[0])
                wanted=int(re.search(r'\((\d+)\)\s*$',raw['item']).group(1))
                actual=sum(i['definition']==role for i in selected)
                if actual!=wanted:raise ValueError('Shared whole-vehicle wheel count mismatch: '+role)
                totals.append(dict(definition=role,source_record=record,actual=actual,expected=wanted))
    from .drive_mount_validation import composition as mount_composition
    mount_counts=mount_composition(data,selected)
    return dict(assemblies=checks,installed=result,whole_vehicle_wheel_totals=totals,drive_mount_counts=mount_counts,
                shared_vehicle_totals_fully_populated=False,
                limitation='M1409 bushes and common rivets also belong to unpopulated pinion/other assemblies.')


def paired_rim_alignment(data,selected):
    """Compare actual groove axes in installed native rings, ignoring axial Y."""
    import Part
    radius=data['values']['drive_groove_radius'].value
    count=int(data['values']['drive_teeth'].value);result=[]
    for hand in ['Port','Starboard']:
        rims=[i for i in selected if i['id'].startswith(hand+'Drive_') and i['definition']=='drive_rim']
        if not rims:continue
        if len(rims)!=2:raise ValueError('Drive phase check needs both rings')
        centers=[]
        for rim in rims:
            points=[(f.Surface.Center.x,f.Surface.Center.z) for f in rim['shape'].Faces
                    if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-radius)<1e-6]
            if len(points)!=count:raise ValueError('Installed drive ring relief count changed')
            centers.append(points)
        error=max(min(math.dist(a,b) for b in centers[1]) for a in centers[0])
        if error>1e-5:raise ValueError('Paired drive teeth staggered across track channels: '+hand)
        result.append(dict(hand=hand,native_reliefs_per_ring=count,max_axis_error_mm=error,passed=True))
    return result


def validate(data,items,out):
    selected=[i for i in items if i['id'].startswith(('PortIdler_','StarboardIdler_','PortDrive_','StarboardDrive_'))]
    if not selected:return {'applicable':False}
    import numpy as np
    from .wheel_geometry import values,station
    from .roller_validation import bearing_face
    source=composition(data,selected);v=values(data)
    alignment=paired_rim_alignment(data,selected)
    physical=[i for i in items if i['representation']=='assembly']
    native_boxes={i['id']:i['shape'].optimalBoundingBox(False) for i in physical}
    def bounds(item):
        b=native_boxes[item['id']]
        return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
    boxes=np.array([bounds(i) for i in physical]);ids={i['id'] for i in selected}
    internal=external=0;maximum=0
    for a in selected:
        b=np.array(bounds(a))
        near=np.where(np.all(boxes[:,:3]<=b[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=b[:3]-1e-7,axis=1))[0]
        for j in near:
            other=physical[j]
            if other['id'] in ids:
                if other['id']<=a['id']:continue
                internal+=1
            else:external+=1
            vol=a['shape'].common(other['shape']).Volume;maximum=max(maximum,vol)
            if vol>1e-5:raise ValueError(f"Wheel material overlap: {a['id']} / {other['id']}: {vol}")
    targets={i['definition']:i['target'] for i in selected};dimensions=[]
    for key,axis,wanted in [('wheel_rim','X',v['idler_diameter']),('wheel_rim','Z',v['idler_diameter']),
                           ('wheel_rim','Y',v['wheel_rim_width']),('wheel_bush','Y',v['wheel_bush_length']),
                           ('wheel_bush','X',v['wheel_bush_od']),('wheel_disk','X',2*v['wheel_disk_radius'])]:
        actual=getattr(targets[key].Shape.optimalBoundingBox(False),axis+'Length')
        if abs(actual-wanted)>1e-5:raise ValueError('Wheel controlled dimension failed: '+key+axis)
        dimensions.append(dict(definition=key,axis=axis,actual_mm=actual,expected_mm=wanted))
    stocks=[]
    for role in ['short','long','rim']:
        target=targets['wheel_rivet_'+role];diameter=v['wheel_rim_rivet_diameter'] if role=='rim' else v['wheel_small_rivet_diameter']
        length=v['wheel_'+role+'_rivet_length'];base=v['wheel_rivet_head_ratio']*diameter;h=v['wheel_rivet_head_height_ratio']*diameter
        volume=math.pi*(diameter/2)**2*length+math.pi*h*(3*base*base+h*h)/6
        if abs(volume-target.Shape.Volume)>1e-4:raise ValueError('Installed rivet stock volume changed')
        stocks.append(dict(role=role,source_stock_length_mm=length,installed_grip_mm=float(target.InstalledGrip),
                           volume_error_mm3=target.Shape.Volume-volume,head_profile_qualified=False))
    # Independently measure installed support material against both heads of
    # one rivet of each size on each axial side, on both idler installations.
    seats=[]
    for prefix in ['PortIdler_','StarboardIdler_','PortDrive_','StarboardDrive_']:
        group=[i for i in selected if i['id'].startswith(prefix)]
        if not group:continue
        for role in ['short','long','rim']:
            rivets=[i for i in group if i['definition']=='wheel_rivet_'+role]
            center=next(i for i in group if i['definition']=='wheel_boss')['shape'].Solids[0].CenterOfMass.y
            for side in [-1,1]:
                rivet=next(i for i in rivets if (i['shape'].Solids[0].CenterOfMass.y-center)*side>0)
                material=[i for i in group if i['definition'] in {'wheel_disk','wheel_rim','drive_rim','wheel_boss','wheel_diaphragm_x','wheel_diaphragm_y'}
                          and native_boxes[rivet['id']].intersect(native_boxes[i['id']])]
                contacts=[]
                for part in material:
                    gap,area=bearing_face(rivet['shape'],part['shape'])
                    if area>1e-4:contacts.append(dict(part=part['id'],area_mm2=area,gap_mm=gap))
                if len(contacts)!=2 or any(c['gap_mm']>1e-5 for c in contacts):
                    raise ValueError('Wheel rivet heads not seated on two joint ends: '+rivet['id']+str(contacts))
                seats.append(dict(rivet=rivet['id'],contacts=contacts))
    disk_seats=[]
    for rim in [i for i in selected if i['definition'] in {'wheel_rim','drive_rim'}]:
        disks=[i for i in selected if i['definition']=='wheel_disk' and i['id'].split('_')[0]==rim['id'].split('_')[0]]
        contacts=[]
        for disk in disks:
            gap,area=bearing_face(rim['shape'],disk['shape'])
            if area>1e-4 and gap<1e-5:contacts.append(dict(disk=disk['id'],gap_mm=gap,area_mm2=area))
        if len(contacts)!=1:raise ValueError('Wheel rim lacks a unique native disk seat: '+rim['id'])
        disk_seats.append(dict(rim=rim['id'],contacts=contacts))
    common_targets=[]
    for role in ['wheel_disk','wheel_boss','wheel_diaphragm_x','wheel_diaphragm_y','wheel_rivet_short','wheel_rivet_long','wheel_rivet_rim','wheel_bush']:
        parts=[i for i in selected if i['definition']==role]
        targets_used={(i['target'].Document.FileName,i['target'].Name) for i in parts}
        if len(targets_used)!=1:raise ValueError('Source-common wheel part split into multiple native definitions: '+role)
        common_targets.append(dict(definition=role,occurrences=len(parts),native_definitions=1))
    drive_dimensions=[]
    if 'drive_rim' in targets:
        import Part
        shape=targets['drive_rim'].Shape
        cylinders=[f.Surface for f in shape.Faces if isinstance(f.Surface,Part.Cylinder)]
        grooves=[c for c in cylinders if abs(c.Radius-v['drive_groove_radius'])<1e-6
                 and abs(math.hypot(c.Center.x,c.Center.z)-v['drive_root_radius']-v['drive_groove_radius'])<1e-5]
        if len(grooves)!=int(v['drive_teeth']):raise ValueError('Native drive rim relief count changed')
        for parameter in ['drive_diameter','drive_inner_diameter']:
            radius=v[parameter]/2
            if not any(abs(c.Radius-radius)<1e-6 and math.hypot(c.Center.x,c.Center.z)<1e-6 for c in cylinders):
                raise ValueError('Native drive cylindrical dimension missing: '+parameter)
            drive_dimensions.append(dict(parameter=parameter,actual_diameter_mm=2*radius))
        width=shape.optimalBoundingBox(False).YLength
        if abs(width-v['wheel_rim_width'])>1e-6:raise ValueError('Drive tooth width changed')
        drive_dimensions.append(dict(parameter='wheel_rim_width',actual_mm=width,native_relief_count=len(grooves)))
    bushes=[i for i in physical if i['definition']=='track_bushing'];gaps=[]
    if bushes:
        bush_boxes=np.array([bounds(i) for i in bushes])
        for rim in [i for i in selected if i['definition']=='wheel_rim']:
            b=np.array(bounds(rim));margin=data['values']['shoe_pitch'].value
            near=np.where(np.all(bush_boxes[:,:3]<=b[3:]+margin,axis=1)&np.all(bush_boxes[:,3:]>=b[:3]-margin,axis=1))[0]
            gap,key=min((rim['shape'].distToShape(bushes[j]['shape'])[0],bushes[j]['id']) for j in near)
            if abs(gap-v['idler_static_gap'])>1e-5:raise ValueError('Native idler rim/bushing gap mismatch: '+rim['id'])
            gaps.append(dict(rim=rim['id'],track_bushing=key,gap_mm=gap))
    drive_gaps=[]
    if bushes:
        for rim in [i for i in selected if i['definition']=='drive_rim']:
            b=np.array(bounds(rim));margin=data['values']['shoe_pitch'].value
            near=np.where(np.all(bush_boxes[:,:3]<=b[3:]+margin,axis=1)&np.all(bush_boxes[:,3:]>=b[:3]-margin,axis=1))[0]
            if not len(near):raise ValueError('No nearby drive track bushings in declared measurement scope')
            gap,key=min((rim['shape'].distToShape(bushes[j]['shape'])[0],bushes[j]['id']) for j in near)
            drive_gaps.append(dict(rim=rim['id'],track_bushing=key,gap_mm=gap,contact_qualified=False))
    roller_gaps=[]
    for hand in ['Port','Starboard']:
        rollers=[i for i in physical if i['id'].startswith(hand+'Rollers_Unit000_') and i['definition']=='roller_lower']
        for rim in [i for i in selected if i['id'].startswith(hand+'Idler_') and i['definition']=='wheel_rim']:
            if not rollers:continue
            gap,key=min((rim['shape'].distToShape(i['shape'])[0],i['id']) for i in rollers)
            if gap<.5:raise ValueError('Front roller/idler clearance below allowance')
            roller_gaps.append(dict(rim=rim['id'],roller=key,gap_mm=gap))
    from .idler_validation import validate as validate_mounts
    mounts=validate_mounts(data,items,out)
    from .drive_mount_validation import validate as validate_drive_mounts
    drive_mounts=validate_drive_mounts(data,items,out)
    report=dict(applicable=True,source_composition=source,modeled_occurrences=len(selected),mount_interfaces=mounts,drive_mount_interfaces=drive_mounts,
        internal_candidate_pairs=internal,external_candidate_pairs=external,other_physical_occurrences=len(physical)-len(selected),
        maximum_overlap_mm3=maximum,controlled_dimensions=dimensions,rivet_stock=stocks,rivet_head_seats=seats,
        rim_bushing_gaps=gaps,drive_rim_bushing_gaps=drive_gaps,foremost_roller_gaps=roller_gaps,
        rim_disk_seats=disk_seats,shared_native_definitions=common_targets,drive_dimensions=drive_dimensions,
        paired_drive_rim_alignment=alignment,
        station=station(data),implemented_checks_passed=True,drive_shaft_source_composition_complete=all(r['complete'] for r in source['assemblies'] if r['template']=='drive_shaft'),
        shaft_source_composition_complete=True,adjustment_geometry_partial=True,continuous_engagement_qualified=False,historical_fit_qualified=False)
    write(out/'reports/wheel_components.json',report);return report
