"""Independent source quantities and installed standard sponson shell checks."""
from collections import Counter
import itertools
import json
import math
import re
from .evidence import STAGE,database,read,write


def composition(data,ids):
    rows=read(STAGE/'data/sponson_source_rows.json')
    counts=Counter(pid for i in data['occurrences'] if i['id'] in ids
                   for pid in data['definitions'][i['definition']]['survey_ids'])
    report=[]
    with database() as c:
        for mark,record in rows.items():
            found=c.execute('SELECT DISTINCT part_id FROM part_identifiers WHERE identifier=?',(mark,)).fetchall()
            if len(found)!=1:raise ValueError('Ambiguous sponson identity '+mark)
            pid=found[0][0]
            if not c.execute('SELECT 1 FROM part_evidence WHERE part_id=? AND record_id=?',(pid,record)).fetchone():
                raise ValueError('Sponson source quantity belongs to another identity '+mark)
            raw=json.loads(c.execute('SELECT raw_json FROM source_records WHERE record_id=?',(record,)).fetchone()[0])
            qty=raw['qty'].strip();numbers=[qty] if qty.isdigit() else re.findall(r'\((\d+)\)',qty)
            if len(numbers)!=1:raise ValueError('Unresolved sponson source quantity '+mark)
            expected=int(numbers[0])
            if counts[pid]!=expected:raise ValueError('Sponson source quantity mismatch: '+mark)
            report.append({'mark':mark,'record':record,'part_id':pid,'expected':expected,'actual':counts[pid]})
    if sum(x['actual'] for x in report)!=len(ids):raise ValueError('Unexpected sponson plate occurrence')
    return report


def validate(data,items,out):
    plates=[i for i in items if i['definition'].startswith('sponson_') and i['representation']=='assembly']
    if not plates:return {'applicable':False}
    import FreeCAD as App
    import Part
    from .cad_build import frame
    from .model import geometry_arguments
    ids={i['id'] for i in plates};source=composition(data,ids)
    others=[i for i in items if i['representation']=='assembly' and i['id'] not in ids]
    checks=0;maximum=0
    for a,b in itertools.chain(itertools.combinations(plates,2),itertools.product(plates,others)):
        if not a['shape'].BoundBox.intersect(b['shape'].BoundBox):continue
        vol=a['shape'].common(b['shape']).Volume;checks+=1;maximum=max(maximum,vol)
        if vol>1e-5:raise ValueError(f"Sponson material overlap: {a['id']} / {b['id']}: {vol} mm3")
    byid={i['id']:i for i in plates};bounds=App.BoundBox()
    for i in plates:bounds.add(i['shape'].BoundBox)
    width=data['values']['vehicle_width'].value
    if abs(bounds.YMax-width/2)>1e-6 or abs(bounds.YMin+width/2)>1e-6:
        raise ValueError('Standard sponson half-width does not match printed vehicle width')
    cavity_checks=[];opening_checks=[];absent_openings=[];thickness=[]
    for side,h in [('port',1),('starboard',-1)]:
        a=geometry_arguments(data['definitions']['sponson_'+side+'_roof'],data)
        L,D,H=a['length'],a['depth'],a['height'];placement=frame('sponson_'+side+'_standard',data)
        for name,u,v,z in [('aft interior',.65*L,.5*D,.55*H),('front interior',.2*L,.45*D,.55*H),('inboard access',.5*L,30,.55*H)]:
            center=placement.multVec(App.Vector(-u,h*v,z));probe=Part.makeBox(20,20,20,center-App.Vector(10,10,10))
            if any(i['shape'].common(probe).Volume>1e-6 for i in plates):raise ValueError('Filled sponson cavity '+side+' '+name)
            cavity_checks.append(side+' '+name)
        # Independent HB43 assignment: four peep holes left, three right; three ordinary pistol holes left, two right.
        expected={'front_wing':(True,True),'back_side':(True,True),'side':(True,h==1),'back_wing':(h==1,False)}
        centers={'front_wing':(0,.21*D),'back_side':(L,.31*D),'side':(.66*L,D),'back_wing':(.9*L,.74*D)}
        back_length=math.hypot(.2*L,.52*D)
        inward={'front_wing':App.Vector(-1,0,0),'back_side':App.Vector(1,0,0),
                'side':App.Vector(0,-h,0),'back_wing':App.Vector(.52*D/back_length,-h*.2*L/back_length,0)}
        for role,(peep,pistol) in expected.items():
            obj=byid['sponson_'+side+'_'+role]['shape']
            for kind,required,z in [('peep',peep,.74*H),('pistol',pistol,.49*H)]:
                u,v=centers[role];center=placement.multVec(App.Vector(-u,h*v,z))
                center+=inward[role]*(a['sponson_plate_side']/2)
                probe=Part.makeBox(3,3,3,center-App.Vector(1.5,1.5,1.5))
                vol=obj.common(probe).Volume
                if required:
                    if vol>1e-7:raise ValueError('Missing source-required sponson opening '+side+' '+role+' '+kind)
                    opening_checks.append({'side':side,'plate':role,'kind':kind})
                else:
                    if abs(vol-27)>1e-5:raise ValueError('Extra mirrored sponson opening '+side+' '+role+' '+kind)
                    absent_openings.append({'side':side,'plate':role,'kind':kind})
        slope=a['sponson_plate_shoulder_rise']/(.75*D)
        samples=[('roof','sponson_plate_roof',(0,0,1)),('floor','sponson_plate_floor',(0,0,1)),
                 ('side','sponson_plate_side',(0,1,0)),('shield_top_rear','sponson_plate_shield',(0,0,1)),
                 ('sloping_bottom','sponson_plate_forward_floor',(0,-h*slope,1)),
                 ('sloping_side','sponson_plate_aft_floor',(0,-h*slope,1))]
        for role,parameter,normal in samples:
            normal=App.Vector(*normal);normal.normalize()
            distances=[v.Point.dot(normal) for v in byid['sponson_'+side+'_'+role]['shape'].Vertexes]
            measured=max(distances)-min(distances);expected=data['values'][parameter].value
            if abs(measured-expected)>1e-6:raise ValueError('Sponson plate normal thickness mismatch '+side+' '+role)
            thickness.append({'side':side,'plate':role,'expected_mm':expected,'measured_mm':measured})
    result={'applicable':True,'plate_occurrences':len(plates),'source_identity_count':len(source),'source_quantities':source,
            'candidate_material_pairs':checks,'max_overlap_mm3':maximum,'other_physical_components_in_contact_scope':len(others),
            'overall_width_mm':bounds.YLength,'hollow_probes':cavity_checks,'HB43_opening_probes':opening_checks,
            'HB43_absent_opening_probes':absent_openings,'normal_thickness_samples':thickness,'standard_installed_configuration_only':True,
            'complete_sponsons_verified':False,'historical_fit_qualified':False,
            'limitations':['Plate subset excludes rotating shields/mounts, hinges, rail supports, fittings, furnishings and fasteners.',
                'Taper, lower rake, shield infills, aperture sizes/stations and seams remain inferred.',
                'M2764 follows the later SNL right-hand assignment provisionally against the HB port assignment.',
                'HB forward/aft floor thickness mapping remains provisional.']}
    write(out/'reports/sponson_plates.json',result)
    return result
