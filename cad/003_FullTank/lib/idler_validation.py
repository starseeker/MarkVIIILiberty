"""Native bearing/contact measurements for the partial shaft/adjuster installation."""
import math
from .evidence import write


def validate(data,items,out):
    from .idler_geometry import values
    from .roller_validation import bearing_face
    from .cad_build import frame
    a=values(data);by_id={i['id']:i for i in items};seats=[];fits=[]
    targets={i['definition']:i['target'] for i in items if i['id'].startswith(('PortIdler_','StarboardIdler_'))}
    def seat(first,second,label):
        if first not in by_id or second not in by_id:return
        x,y=by_id[first]['shape'],by_id[second]['shape'];gap,area=bearing_face(x,y)
        if gap>1e-5 or area<1:raise ValueError('Idler bearing face missing: '+label+f' gap={gap}, area={area}')
        seats.append(dict(a=first,b=second,interface=label,gap_mm=gap,area_mm2=area))
    def distance(first,second,label,expected=None):
        x,y=by_id[first]['shape'],by_id[second]['shape'];gap=x.distToShape(y)[0]
        if expected is not None and abs(gap-expected)>1e-5:raise ValueError('Idler clearance mismatch: '+label+f' {gap} != {expected}')
        fits.append(dict(a=first,b=second,interface=label,gap_mm=gap,expected_mm=expected))
    for hand in ['Port','Starboard']:
        root=hand+'Idler_Unit000_'
        if root+'ShaftAssembly_Shaft' not in by_id:continue
        for side,letter in [(-1,'A'),(1,'B')]:
            support=root+'Supports_';shaft=root+'ShaftAssembly_';moving=root+'ShaftFittings_'
            seat(shaft+'Nut'+letter,moving+'Washer'+letter,'shaft nut / washer')
            seat(moving+'Washer'+letter,support+'Bracket'+letter,'washer / bracket guide')
            seat(support+'AdjustingScrew'+letter,support+'Bracket'+letter,'adjusting head / front post')
            seat(shaft+'LockingScrew'+letter,moving+'Copper'+letter,'locking screw / copper plug')
            seat(shaft+'OilPlug'+letter,shaft+'Shaft','pipe plug / shaft end')
            for n in range(4):seat(support+'Cap'+letter+str(n),support+'Bracket'+letter,'cap screw / bracket foot')
            distance(shaft+'Bush'+letter,shaft+'Shaft','bush / shaft radial running gap',
                     (a['wheel_bush_id']-a['idler_shaft_diameter'])/2)
            distance(root+'Wheel_Boss',support+'Bracket'+letter,'rotating boss / stationary guide',a['idler_boss_end_gap'])
            distance(moving+'Copper'+letter,support+'AdjustingScrew'+letter,'copper saddle / adjusting screw',0)
            # A coincident curved surface proves seating, not merely a point
            # distance. Translate off the saddle and this native test fails.
            copper=by_id[moving+'Copper'+letter]['shape'];screw=by_id[support+'AdjustingScrew'+letter]['shape']
            area=sum(f.common(g).Area for f in copper.Faces for g in screw.Faces
                     if f.BoundBox.intersect(g.BoundBox))
            if area<1:raise ValueError('Copper plug has no native saddle contact')
            fits[-1]['surface_contact_area_mm2']=area
            outer=(side==1) if hand=='Port' else (side==-1)
            definition='hull_'+hand.lower()+('_front_upper' if outer else '_inner_front_upper')
            hull=next((i['id'] for i in items if i['definition']==definition),None)
            if hull:
                seat(support+'Bracket'+letter,hull,'cast foot / hull plate')
                seat(support+'Plate'+letter,hull,'reinforcement / hull plate')
                if outer:
                    for n in range(5):
                        rivet=support+'PlateRivet'+str(n)
                        seat(rivet,hull,'reinforcement rivet / hull')
                        seat(rivet,support+'Plate'+letter,'reinforcement rivet / backing plate')
        # Fixed support frames must stay at the source datum; shaft displacement
        # is along their screw axis, with no transverse or normal component.
        relative=frame(root+'Supports',data).inverse().multiply(frame(root+'ShaftAssembly',data))
        if abs(relative.Base.y)>1e-7 or abs(relative.Base.z)>1e-7:
            raise ValueError('Idler shaft does not follow the fixed adjustment axis')
    dimensions=[]
    for key,axis,expected in [('idler_shaft','Y',a['idler_shaft_length']),
        ('idler_adjusting_screw','X',a['idler_screw_length']),('idler_adjusting_screw','Z',a['idler_screw_head_af']),
        ('idler_nut','Z',a['idler_nut_af']),('idler_washer','Y',a['idler_washer_stock'])]:
        if key not in targets:continue
        actual=getattr(targets[key].Shape.optimalBoundingBox(False),axis+'Length')
        if abs(actual-expected)>1e-5:raise ValueError('Idler controlled stock dimension failed: '+key+axis)
        dimensions.append(dict(definition=key,axis=axis,actual_mm=actual,expected_mm=expected))
    target=targets['idler_plate_rivet'];d=a['idler_plate_rivet_diameter'];r=.85*d;h=.6*d
    volume=math.pi*(d/2)**2*a['idler_plate_rivet_length']+math.pi*h*(3*r*r+h*h)/6
    if abs(target.Shape.Volume-volume)>1e-4:raise ValueError('Reinforcement rivet stock volume changed')
    report=dict(bearing_faces=seats,clearances=fits,controlled_dimensions=dimensions,
        plate_rivet_stock_volume_error_mm3=target.Shape.Volume-volume,implemented_checks_passed=True,
        thread_forms_qualified=False,inner_plate_retention_complete=False,historical_fit_qualified=False)
    write(out/'reports/idler_mounts.json',report);return report
