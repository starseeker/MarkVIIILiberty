"""Source-identified mounting contacts and full native receiving walls."""
from collections import Counter
import json
import math
import re
from .evidence import STAGE,read,write,database


def composition(data,items):
    selected=[i for i in items if i['id'].startswith(('PortDrive_','StarboardDrive_'))]
    if not selected:return {'applicable':False}
    rows=read(STAGE/'data/drive_mount_source_rows.json');result=[]
    with database() as c:
        for role,row in rows.items():
            definition='drive_'+role
            raw=json.loads(c.execute('SELECT raw_json FROM source_records WHERE record_id=?',(row['record'],)).fetchone()[0])
            ids=data['definitions'][definition]['survey_ids']
            if ids!=row['survey_ids'] or not c.execute('SELECT 1 FROM part_evidence WHERE part_id=? AND record_id=?',(ids[0],row['record'])).fetchone():
                raise ValueError('Drive mounting source identity mismatch: '+role)
            count=sum(i['definition']==definition for i in selected)
            if count!=2*row['fixture_count']:raise ValueError('Drive mounting count mismatch: '+role)
            expected=raw.get('qty','').strip('() ')
            if role in {'inner_bearing','locking_plate','locking_screw','inner_rivet'} and count!=int(expected):
                raise ValueError('Drive mounting whole-vehicle source count mismatch: '+role)
            if role in {'outer_bearing','backing_plate','bearing_screw'} and 2*count!=int(expected):
                raise ValueError('Shared drive/pinion source allocation changed: '+role)
            result.append(dict(definition=definition,record=row['record'],drive_occurrences=count,
                               source_vehicle_quantity=int(expected) if expected.isdigit() else None))
        allocations=[('bearing_screw','M1407',6),('locking_screw','M1411',1),('inner_rivet','M1977 and bearing M1406',6),
                     ('backing_rivet','M1975A and plate M1552',4),('backing_rivet','M1975B and plate M1552',4)]
        for role,phrase,wanted in allocations:
            raw=json.loads(c.execute('SELECT raw_json FROM source_records WHERE record_id=?',(rows[role]['record'],)).fetchone()[0])
            text=re.sub(r'\s+',' ',raw['item'].replace('\\n',' '))
            if phrase+f' ({wanted})' not in text:raise ValueError('Drive mounting joint allocation changed: '+role)
        for hand in ['port','starboard']:
            for role,record in [('inner_fuel_side','SNL:149:039'),('inner_rear_end','SNL:155:006')]:
                key='hull_'+hand+'_'+role;ids=data['definitions'][key]['survey_ids']
                if len(ids)!=1 or not c.execute('SELECT 1 FROM part_evidence WHERE part_id=? AND record_id=?',(ids[0],record)).fetchone():
                    raise ValueError('Drive receiver identity conflicts with source: '+key)
        # All eight M1477 nuts are now present across two idlers and two drives.
        nuts=sum(i['definition']=='idler_nut' for i in items)
        raw=json.loads(c.execute('SELECT raw_json FROM source_records WHERE record_id="SNL:129:009"').fetchone()[0])
        if any(i['id'].startswith('PortIdler_') for i in items) and nuts!=int(raw['qty']):
            raise ValueError('Common M1477 whole-vehicle nut count mismatch')
    return dict(applicable=True,components=result,common_shaft_nuts=nuts,
        unresolved='Shared outer bearings/backing plates/caps/bushes/key still have unpopulated pinion uses; additional M1552 plate-only rivets unresolved.')


def validate(data,items,out):
    if not any(i['definition']=='drive_shaft' for i in items):return {'applicable':False}
    import FreeCAD as App
    import Part
    from .drive_mount_geometry import values,bearing_points,backing_points
    from .cad_build import frame
    from .roller_validation import bearing_face
    source=composition(data,items);a=values(data);by_id={i['id']:i for i in items}
    seats=[];bores=[];gaps=[];oil=[]
    def seat(first,second,label):
        if first not in by_id or second not in by_id:raise ValueError('Missing drive interface constituent: '+label)
        gap,area=bearing_face(by_id[first]['shape'],by_id[second]['shape'])
        if gap>1e-5 or area<1:raise ValueError('Drive bearing seat missing: '+label+f' {gap}, {area}')
        seats.append(dict(a=first,b=second,interface=label,gap_mm=gap,area_mm2=area))
    for hand in ['Port','Starboard']:
        root=hand+'Drive_Unit000_';shaft=root+'ShaftAssembly_';support=root+'Supports_'
        if shaft+'Shaft' not in by_id:continue
        pose=frame(root+'ShaftAssembly',data)
        for suffix in ['Inner','Outer']:
            seat(shaft+'Nut'+suffix,support+'Bearing'+suffix,'shaft nut / bearing')
            seat(support+'LockingPlate'+suffix,shaft+'Nut'+suffix,'locking plate / nut flat')
            seat(support+'LockingPlate'+suffix,support+'Bearing'+suffix,'locking plate / bearing face')
            seat(support+'LockingScrew'+suffix,support+'LockingPlate'+suffix,'locking cap / locking plate')
            seat(shaft+'Shaft',support+'Bearing'+suffix,'shaft shoulder / bearing barrel')
        seat(shaft+'Key',shaft+'Shaft','key / shaft keyway')
        seat(shaft+'Key',support+'BearingOuter','key / outer bearing')
        seat(shaft+'OilPlug',shaft+'Shaft','oil plug / shaft end')
        for n in range(6):
            seat(support+'BearingScrew'+str(n),support+'BearingOuter','outer cap screw / bearing')
            seat(support+'InnerRivet'+str(n),support+'BearingInner','inner rivet / bearing')
        for n in range(4):seat(support+'BackingRivet'+str(n),support+'BackingPlate','backing rivet / plate')
        for suffix in ['A','B']:
            gap=by_id[shaft+'Shaft']['shape'].distToShape(by_id[shaft+'Bush'+suffix]['shape'])[0]
            wanted=(data['values']['wheel_bush_id'].value-a['shaft_diameter'])/2
            if abs(gap-wanted)>1e-5:raise ValueError('Drive shaft/bush running gap changed')
            gaps.append(dict(shaft=shaft+'Shaft',bush=shaft+'Bush'+suffix,gap_mm=gap,expected_mm=wanted))
        shape=by_id[shaft+'Shaft']['shape'];r=a['shaft_diameter']/2
        for probe in [(0,a['end']-15,0),(0,0,r-1)]:
            if shape.isInside(pose.multVec(App.Vector(*probe)),1e-7,True):raise ValueError('Drive oil lead is filled')
        if not shape.isInside(pose.multVec(App.Vector(25,0,0)),1e-7,True):raise ValueError('Drive shaft witness material absent')
        oil.append(dict(shaft=shaft+'Shaft',axial_and_radial_open=True,hydraulic_function_qualified=False))
        inner='hull_'+hand.lower()+'_inner_fuel_side';outer='hull_'+hand.lower()+'_rear_end'
        if inner not in by_id or outer not in by_id:continue
        for name,receiver in [('BearingInner',inner),('BearingOuter',outer),('BackingPlate',outer)]:
            seat(support+name,receiver,'bearing/backing / source-identified hull receiver')
        for n in range(6):seat(support+'InnerRivet'+str(n),inner,'inner rivet / M1977')
        for n in range(4):seat(support+'BackingRivet'+str(n),outer,'backing rivet / M1975')
        for receiver,points,diameter in [(inner,bearing_points(a),a['bearing_screw_diameter']+a['fastener_hole_clearance']),
                                       (outer,bearing_points(a),a['bearing_screw_diameter']+a['fastener_hole_clearance']),
                                       (outer,backing_points(a),a['backing_rivet_diameter']+a['fastener_hole_clearance'])]:
            shape=by_id[receiver]['shape']
            for index,(x,z) in enumerate(points):
                axis=pose.multVec(App.Vector(x,0,z));r=diameter/2
                faces=[f for f in shape.Faces if isinstance(f.Surface,Part.Cylinder)
                       and abs(f.Surface.Radius-r)<1e-6 and abs(abs(f.Surface.Axis.y)-1)<1e-6
                       and math.hypot(f.Surface.Center.x-axis.x,f.Surface.Center.z-axis.z)<1e-5]
                length=sum(f.Area for f in faces)/(2*math.pi*r)
                if abs(length-a['hull_side_thickness'])>1e-5:raise ValueError('Drive attachment lacks full receiving wall: '+receiver)
                bores.append(dict(receiver=receiver,index=index,diameter_mm=diameter,full_cylinder_length_mm=length))
    targets={i['definition']:i['target'] for i in items};dimensions=[];stocks=[]
    for key,axis,expected in [('drive_shaft','Y',a['shaft_length']),('drive_shaft','X',a['shaft_diameter']),
                            ('drive_key','X',a['key_width']),('drive_key','Y',a['key_length']),('drive_key','Z',a['key_height'])]:
        actual=getattr(targets[key].Shape.optimalBoundingBox(False),axis+'Length')
        if abs(actual-expected)>1e-5:raise ValueError('Drive mounting controlled dimension changed: '+key)
        dimensions.append(dict(definition=key,axis=axis,actual_mm=actual,expected_mm=expected))
    for role,diameter,length in [('inner_rivet',a['bearing_screw_diameter'],a['inner_rivet_length']),
                                ('backing_rivet',a['backing_rivet_diameter'],a['backing_rivet_length'])]:
        target=targets['drive_'+role];radius=.85*diameter;height=.6*diameter
        expected=math.pi*(diameter/2)**2*length+math.pi*height*(3*radius*radius+height*height)/6
        error=target.Shape.Volume-expected
        if abs(error)>1e-4:raise ValueError('Drive rivet stock volume changed')
        stocks.append(dict(definition='drive_'+role,stock_length_mm=length,volume_error_mm3=error))
    report=dict(applicable=True,source_composition=source,bearing_faces=seats,receiving_hull_bores=bores,
        clearances=gaps,oil_leads=oil,controlled_dimensions=dimensions,rivet_stock=stocks,
        implemented_checks_passed=True,source_shaft_boms_complete=True,historical_fit_qualified=False,
        thread_forms_qualified=False,remaining_plate_only_rivets_unresolved=True)
    write(out/'reports/drive_mounts.json',report);return report
