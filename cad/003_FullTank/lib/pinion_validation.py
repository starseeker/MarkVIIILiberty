"""Source composition and actual native interfaces of the standard pinion units."""
from collections import Counter
import json
import math
from .evidence import STAGE,read,write,database


COUNTS={'pinion_casting':1,'pinion_roller':18,'pinion_pin':18,'pinion_cotter':18,'pinion_pin_plug':18,
        'pinion_shaft':1,'drive_key':1,'pinion_shaft_outer_plug':1,'pinion_shaft_inner_plug':1,
        'wheel_bush':2,'drive_outer_bearing':1,'pinion_inner_bearing':1,'drive_backing_plate':1,
        'drive_bearing_screw':6,'pinion_inner_rivet':6,'drive_backing_rivet':4}
RECORDS={'pinion_casting':'SNL:144:004','pinion_roller':'SNL:144:006','pinion_pin':'SNL:143:009',
        'pinion_cotter':'SNL:143:010','pinion_pin_plug':'SNL:143:011','pinion_shaft':'SNL:215:011',
        'drive_key':'SNL:215:012','pinion_shaft_outer_plug':'SNL:215:013','pinion_shaft_inner_plug':'SNL:215:013',
        'wheel_bush':'SNL:43:011','drive_outer_bearing':'SNL:18:008','pinion_inner_bearing':'SNL:18:007',
        'drive_backing_plate':'SNL:152:021','drive_bearing_screw':'SNL:201:008',
        'pinion_inner_rivet':'SNL:189:008','drive_backing_rivet':'SNL:170:004'}


def composition(data,items):
    rows={r['record_id']:r for r in read(STAGE/'data/pinion_source_rows.json')['rows']}
    result=[];common=[]
    with database() as c:
        for definition,rid in RECORDS.items():
            ids=data['definitions'][definition]['survey_ids']
            if ids!=rows[rid]['part_ids'] or not c.execute('SELECT 1 FROM part_evidence WHERE part_id=? AND record_id=?',(ids[0],rid)).fetchone():
                raise ValueError('Pinion source identity mismatch: '+definition)
        for rid in ['SNL:144:005','SNL:144:006']:
            if 'eighteen' not in c.execute('SELECT description FROM source_records WHERE record_id=?',(rid,)).fetchone()[0]:
                raise ValueError('Pinion rotating BOM count changed')
        for hand in ['Port','Starboard']:
            selected=[i for i in items if i['id'].startswith(hand+'Pinion_')]
            if not selected:continue
            counts=Counter(i['definition'] for i in selected)
            if counts!=COUNTS:raise ValueError('Pinion source composition mismatch: '+hand)
            rotor=sum(i['id'].startswith(hand+'Pinion_Rotor_') for i in selected)
            shaft=sum(i['id'].startswith(hand+'Pinion_ShaftAssembly_') for i in selected)
            if rotor!=73 or shaft!=4:raise ValueError('Pinion assembly hierarchy miscounts source leaves')
            result.append(dict(hand=hand,physical_occurrences=len(selected),rotating_leaves=rotor,shaft_leaves=shaft,counts=dict(counts)))
        if all(any(i['id'].startswith(prefix) for i in items) for prefix in ['PortIdler_','StarboardIdler_','PortDrive_','StarboardDrive_','PortPinion_','StarboardPinion_']):
            for definition in ['wheel_bush','drive_outer_bearing','drive_backing_plate','drive_bearing_screw','pinion_inner_rivet']:
                rid=RECORDS[definition]
                raw=json.loads(c.execute('SELECT raw_json FROM source_records WHERE record_id=?',(rid,)).fetchone()[0])
                wanted=int(raw['qty'].strip('() '));selected=[i for i in items if i['definition']==definition]
                if len(selected)!=wanted:raise ValueError('Shared pinion vehicle quantity mismatch: '+definition)
                targets={(i['target'].Document.FileName,i['target'].Name) for i in selected}
                if len(targets)!=1:raise ValueError('Shared pinion component has multiple native definitions: '+definition)
                common.append(dict(definition=definition,record=rid,source_quantity=wanted,physical_occurrences=len(selected),native_definitions=1))
    return dict(assemblies=result,shared_vehicle_counts=common,remaining_plate_only_rivet_allocation_unresolved=True)


def validate(data,items,out):
    selected=[i for i in items if i['id'].startswith(('PortPinion_','StarboardPinion_'))]
    if not selected:return {'applicable':False}
    import FreeCAD as App
    import Part
    import numpy as np
    from .pinion_geometry import values
    from .drive_mount_geometry import bearing_points,backing_points
    from .cad_build import frame
    from .roller_validation import bearing_face
    a=values(data);m=a['mount'];source=composition(data,items);by_id={i['id']:i for i in items}
    physical=[i for i in items if i['representation']=='assembly']
    boxes=np.array([[s.XMin,s.YMin,s.ZMin,s.XMax,s.YMax,s.ZMax] for s in [i['shape'].BoundBox for i in physical]])
    ids={i['id'] for i in selected};internal=external=0;maximum=0.
    for first in selected:
        box=first['shape'].BoundBox;b=np.array([box.XMin,box.YMin,box.ZMin,box.XMax,box.YMax,box.ZMax])
        near=np.where(np.all(boxes[:,:3]<=b[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=b[:3]-1e-7,axis=1))[0]
        for n in near:
            second=physical[n]
            if second['id'] in ids:
                if second['id']<=first['id']:continue
                internal+=1
            else:external+=1
            volume=first['shape'].common(second['shape']).Volume;maximum=max(maximum,volume)
            if volume>1e-5:raise ValueError(f"Pinion material overlap: {first['id']} / {second['id']}: {volume}")
    seats=[];bores=[];gaps=[];ring_gaps=[];plugs=[]
    def seat(first,second,kind):
        gap,area=bearing_face(by_id[first]['shape'],by_id[second]['shape'])
        if gap>1e-5 or area<1:raise ValueError('Pinion seat missing: '+kind+f' {first} {second} {gap} {area}')
        seats.append(dict(a=first,b=second,kind=kind,gap_mm=gap,area_mm2=area))
    for hand in ['Port','Starboard']:
        unit=hand+'Pinion';rotor=unit+'_Rotor_';shaft=unit+'_ShaftAssembly_';mount=unit+'_Mounts_'
        if shaft+'Shaft' not in by_id:continue
        pose=frame(unit+'_Hand',data)
        for suffix in ['Inner','Outer']:
            seat(shaft+'Shaft',mount+suffix+'Bearing','shaft locating shoulder')
            gap=by_id[shaft+'Shaft']['shape'].distToShape(by_id[mount+'Bush'+suffix]['shape'])[0]
            wanted=(data['values']['wheel_bush_id'].value-a['shaft_diameter'])/2
            if abs(gap-wanted)>1e-5:raise ValueError('Pinion shaft/bush gap changed')
            gaps.append(dict(a=shaft+'Shaft',b=mount+'Bush'+suffix,gap_mm=gap,expected_mm=wanted))
        seat(shaft+'Key',shaft+'Shaft','key / shaft keyway')
        seat(shaft+'Key',mount+'OuterBearing','key / outer bearing')
        for suffix in ['A','B']:
            for n in range(9):
                pin=rotor+'PinAssembly'+suffix+str(n)+'_Pin';roller=rotor+'Roller'+suffix+str(n)
                seat(pin,rotor+'Casting','pin factory head / casting')
                gap=by_id[pin]['shape'].distToShape(by_id[roller]['shape'])[0]
                if abs(gap-a['pin_running_gap'])>1e-5:raise ValueError('Pinion roller/pin gap changed')
                gaps.append(dict(a=pin,b=roller,gap_mm=gap,expected_mm=a['pin_running_gap']))
        for n in range(6):
            seat(mount+'OuterScrew'+str(n),mount+'OuterBearing','outer screw / bearing')
            seat(mount+'InnerRivet'+str(n),mount+'InnerBearing','inner rivet / bearing')
        for n in range(4):seat(mount+'BackingRivet'+str(n),mount+'BackingPlate','backing rivet / backing plate')
        for suffix in ['Inner','Outer']:
            shape=by_id[shaft+suffix+'Plug']['shape'].copy();shape.Placement=pose.inverse().multiply(shape.Placement)
            faces=[f for f in shape.Faces if isinstance(f.Surface,Part.Cylinder)
                   and abs(f.Surface.Radius-a['shaft_plug_shank_diameter']/2)<1e-6
                   and math.hypot(f.Surface.Center.x,f.Surface.Center.z)<1e-5]
            if not faces:raise ValueError('Pinion shaft plug lost its coaxial shank')
            lo=min(f.BoundBox.YMin for f in faces);hi=max(f.BoundBox.YMax for f in faces)
            wanted=(-a['shaft_end'],-a['shaft_end']+a['shaft_plug_insertion']) if suffix=='Inner' else (a['shaft_end']-a['shaft_plug_insertion'],a['shaft_end'])
            if max(abs(lo-wanted[0]),abs(hi-wanted[1]))>1e-5:raise ValueError('Pinion shaft plug insertion changed')
            if suffix=='Inner' and abs(shape.BoundBox.YMin+a['shaft_end'])>1e-5:raise ValueError('Inner plug not flush')
            plugs.append(dict(plug=shaft+suffix+'Plug',insertion_mm=hi-lo,head_cut_flush=suffix=='Inner',thread_and_seal_qualified=False))
        rollers=[i for i in selected if i['id'].startswith(rotor) and i['definition']=='pinion_roller']
        for rim in [i for i in items if i['id'].startswith(hand+'Drive_') and i['definition']=='drive_rim']:
            distance,key=min((r['shape'].distToShape(rim['shape'])[0],r['id']) for r in rollers)
            if distance<.1:raise ValueError('Static pinion/ring clearance below allowance')
            ring_gaps.append(dict(rim=rim['id'],roller=key,gap_mm=distance,continuous_engagement_qualified=False))
        inner='hull_'+hand.lower()+'_inner_rear_end';outer='hull_'+hand.lower()+'_rear_wing'
        if inner not in by_id or outer not in by_id:continue
        for first,second in [(mount+'InnerBearing',inner),(mount+'OuterBearing',outer),(mount+'BackingPlate',outer)]:seat(first,second,'support / owned hull panel')
        for n in range(6):seat(mount+'InnerRivet'+str(n),inner,'inner rivet / M1978')
        for n in range(4):seat(mount+'BackingRivet'+str(n),outer,'backing rivet / M1976')
        for receiver,points,diameter in [(inner,bearing_points(m),m['bearing_screw_diameter']+m['fastener_hole_clearance']),
                (outer,bearing_points(m),m['bearing_screw_diameter']+m['fastener_hole_clearance']),
                (outer,backing_points(m),m['backing_rivet_diameter']+m['fastener_hole_clearance'])]:
            for n,(x,z) in enumerate(points):
                axis=pose.multVec(App.Vector(x,0,z));r=diameter/2
                faces=[f for f in by_id[receiver]['shape'].Faces if isinstance(f.Surface,Part.Cylinder)
                       and abs(f.Surface.Radius-r)<1e-6 and abs(abs(f.Surface.Axis.y)-1)<1e-6
                       and math.hypot(f.Surface.Center.x-axis.x,f.Surface.Center.z-axis.z)<1e-5]
                length=sum(f.Area for f in faces)/(2*math.pi*r)
                if abs(length-m['hull_side_thickness'])>1e-5:raise ValueError('Pinion attachment lacks full cylindrical receiving wall: '+receiver)
                bores.append(dict(receiver=receiver,index=n,diameter_mm=diameter,full_cylinder_length_mm=length))
    targets={i['definition']:i['target'] for i in selected};dimensions=[]
    for definition,axis,wanted in [('pinion_casting','Y',a['casting_length']),('pinion_roller','Y',a['roller_length']),
        ('pinion_roller','X',2*a['roller_radius']),('pinion_pin','Y',a['pin_length']),('pinion_shaft','Y',a['shaft_length']),
        ('pinion_shaft','X',a['shaft_diameter'])]:
        actual=getattr(targets[definition].Shape.optimalBoundingBox(False),axis+'Length')
        if abs(actual-wanted)>1e-5:raise ValueError('Pinion printed dimension changed: '+definition+axis)
        dimensions.append(dict(definition=definition,axis=axis,actual_mm=actual,expected_mm=wanted))
    shape=targets['pinion_casting'].Shape
    reliefs=[f for f in shape.Faces if isinstance(f.Surface,Part.Cylinder)
             and abs(f.Surface.Radius-a['chain_relief_radius'])<1e-6
             and abs(math.hypot(f.Surface.Center.x,f.Surface.Center.z)-a['chain_pitch_radius'])<1e-5]
    if len(reliefs)!=int(a['teeth']):raise ValueError('Central pinion tooth count changed')
    report=dict(applicable=True,source_composition=source,modeled_occurrences=len(selected),
        internal_candidate_pairs=internal,external_candidate_pairs=external,maximum_overlap_mm3=maximum,
        bearing_faces=seats,receiving_hull_bores=bores,clearances=gaps,roller_ring_gaps=ring_gaps,
        shaft_plug_envelopes=plugs,controlled_dimensions=dimensions,central_tooth_count=len(reliefs),
        implemented_checks_passed=True,source_rotating_and_shaft_boms_complete=True,
        continuous_engagement_qualified=False,formed_cotter_retention_qualified=False,
        hydraulic_function_qualified=False,thread_forms_qualified=False,historical_fit_qualified=False)
    write(out/'reports/roller_pinions.json',report);return report


def alternative_wheel_checks(data,items,out):
    """The37-tooth branch must be rejected at the current fixed pinion phase.

    Retain native dimension, paired-rim and old wheel/receiver checks without
    pinions, then explicitly require the full physical installation to fail
    for a measured ring/pinion overlap. No alternative historical count is
    declared false by this one static experiment.
    """
    from .wheel_validation import validate as wheels
    if int(data['values']['drive_teeth'].value)!=37:
        raise ValueError('Expected-rejection trial is defined only for37 teeth')
    pinions=[i for i in items if i['id'].startswith(('PortPinion_','StarboardPinion_'))]
    rings=[i for i in items if i['definition']=='drive_rim']
    if len(pinions)!=196 or len(rings)!=4:
        raise ValueError('Alternative-wheel trial requires both complete pinion installations')
    measured=[]
    for ring in rings:
        hand=ring['id'].split('Drive_',1)[0]
        for pinion in pinions:
            if not pinion['id'].startswith(hand+'Pinion_'):continue
            if not ring['shape'].BoundBox.intersect(pinion['shape'].BoundBox):continue
            volume=ring['shape'].common(pinion['shape']).Volume
            if volume>1e-5:measured.append(dict(rim=ring['id'],pinion=pinion['id'],volume_mm3=volume))
    if {row['rim'] for row in measured}!={i['id'] for i in rings}:
        raise ValueError('Expected37-tooth incompatibility changed; review the trial')
    pinion_ids={i['id'] for i in pinions}
    independent=wheels(data,[i for i in items if i['id'] not in pinion_ids],out/'wheel_scope_without_pinions')
    try:
        wheels(data,items,out/'rejected_full_installation')
    except ValueError as error:
        message=str(error)
        if not any(message.startswith('Wheel material overlap: '+row['rim']+' / '+row['pinion']+':')
                   for row in measured):
            raise
    else:
        raise ValueError('Full installation accepted the measured37-tooth interference')
    report=dict(expected_rejection_verified=True,alternative_teeth=37,
        current_static_installation_accepted=False,measured_overlaps=measured,
        full_installation_error=message,wheel_scope_without_pinions=independent,
        historical_tooth_count_resolved=False,other_phases_or_profiles_qualified=False)
    write(out/'reports/alternative_wheel_rejection.json',report)
    return report
