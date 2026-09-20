"""Source counts, curved section, passages and installed louver contact checks."""
from collections import Counter
import itertools
import json
import math
import re
from .evidence import STAGE, database, read, write


def composition(data, ids):
    source=read(STAGE/'data/louver_source_rows.json')
    counts=Counter(pid for i in data['occurrences'] if i['id'] in ids
                   for pid in data['definitions'][i['definition']]['survey_ids'])
    report=[]
    with database() as c:
        for mark, record in source.items():
            found=c.execute('SELECT DISTINCT part_id FROM part_identifiers WHERE identifier=?',(mark,)).fetchall()
            if len(found)!=1:raise ValueError('Ambiguous louver source identity '+mark)
            pid=found[0][0]
            if not c.execute('SELECT 1 FROM part_evidence WHERE part_id=? AND record_id=?',(pid,record)).fetchone():
                raise ValueError('Louver quantity record belongs to another identity '+mark)
            raw=json.loads(c.execute('SELECT raw_json FROM source_records WHERE record_id=?',(record,)).fetchone()[0])
            quantity=raw['qty'].strip()
            if quantity.isdigit():expected=int(quantity)
            else:
                # Selected blank-quantity rows identify a single component and
                # print its vehicle count in parentheses after that mark.
                numbers=re.findall(r'\((\d+)\)',quantity or raw['item'])
                if len(numbers)!=1:raise ValueError('Unresolved louver source quantity '+mark)
                expected=int(numbers[0])
            if counts[pid]!=expected:raise ValueError('Louver source quantity mismatch: '+mark)
            report.append(dict(mark=mark,record=record,part_id=pid,expected=expected,actual=counts[pid]))
    if sum(x['actual'] for x in report)!=len(ids):raise ValueError('Unexpected louver occurrence')
    return report


def validate(data,items,out):
    selected=[i for i in items if i['definition'].startswith('louver_')]
    if not selected:return {'applicable':False}
    import FreeCAD as App
    import Part
    from .cad_build import frame
    from .louver_geometry import layout
    ids={i['id'] for i in selected}; sources=composition(data,ids)
    others=[i for i in items if i['representation']=='assembly' and i['id'] not in ids]
    checks=0;maximum=0;external=0
    for a,b in itertools.chain(itertools.combinations(selected,2),itertools.product(selected,others)):
        if not a['shape'].BoundBox.intersect(b['shape'].BoundBox):continue
        checks+=1;external+=b['id'] not in ids
        volume=a['shape'].common(b['shape']).Volume;maximum=max(maximum,volume)
        if volume>1e-5:raise ValueError(f"Louver material overlap: {a['id']} / {b['id']}: {volume} mm3")
    byid={i['id']:i for i in selected};sections=[];passages=[];guards=[]
    for bank in ['inlet','outlet']:
        a=layout(data,bank);n=a['count'];placement=frame('louver_'+bank,data)
        blade=byid['louver_'+bank+'_blade_000']['target'].Shape
        bb=blade.BoundBox;t=data['values']['louver_blade_thickness'].value
        radius=data['values']['louver_bend_radius'].value; height=data['values']['louver_blade_width'].value
        radii=sorted(face.Surface.Radius for face in blade.Faces if isinstance(face.Surface,Part.Cylinder))
        if len(radii)!=2 or abs(radii[0]-radius)>1e-6 or abs(radii[1]-radius-t)>1e-6:
            raise ValueError('Louver concentric bend radii/normal stock mismatch '+bank)
        if abs(bb.ZLength-height)>1e-6 or abs(bb.XLength-(a['length']-32))>1e-6:
            raise ValueError('Louver blade outside width or length mismatch '+bank)
        # Four straight section-closing edges (both blade ends) measure normal stock.
        end_edges=[e for e in blade.Edges if isinstance(e.Curve,Part.Line) and abs(e.Length-t)<1e-6]
        if len(end_edges)!=4:raise ValueError('Louver normal end thickness mismatch '+bank)
        sections.append(dict(bank=bank,blades=n,inside_radius_mm=radii[0],outside_radius_mm=radii[1],
                             normal_thickness_mm=t,roof_normal_width_mm=bb.ZLength,
                             true_blade_length_mm=bb.XLength,transverse_pitch_mm=a['pitch']))
        # Each gap is sampled midway between adjacent curved crowns, through
        # the roof-normal section; this checks an empty local passage, not airflow.
        tip=height/2-(radius+t)*math.sqrt(2)+radius+t
        for index in range(n-1):
            y=a['first']+index*a['pitch']+tip+(a['pitch']-t)/2
            center=App.Vector(a['length']/2,y,20+height/2)
            probe=Part.makeBox(2,2,2,center-App.Vector(1,1,1));probe.Placement=placement.multiply(probe.Placement)
            for j in [index,index+1]:
                if byid['louver_'+bank+'_blade_'+str(j).zfill(3)]['shape'].common(probe).Volume>1e-6:
                    raise ValueError('Blocked louver passage '+bank+' '+str(index))
            passages.append(bank+' '+str(index))
        for side in ['port','starboard']:
            shape=byid['louver_'+bank+'_guard_'+side]['shape']
            # Vertical projection relative to the installed roof datum plane.
            max_above=max(v.Point.z-a['origin'][2]-a['slope']*(v.Point.x-a['origin'][0]) for v in shape.Vertexes)
            expected=data['values']['louver_guard_height'].value
            if abs(max_above-expected)>1e-6:raise ValueError('Louver guard vertical projection mismatch')
            guards.append(dict(bank=bank,side=side,vertical_projection_mm=max_above))
    result=dict(applicable=True,component_occurrences=len(selected),source_identity_count=len(sources),
                source_quantities=sources,candidate_material_pairs=checks,external_candidate_pairs=external,
                max_overlap_mm3=maximum,other_physical_components_in_contact_scope=len(others),
                blade_sections=sections,open_passage_probes=len(passages),guard_projection_checks=guards,
                standard_configuration_only=True,complete_louvers_verified=False,historical_fit_qualified=False,
                limitations=['Blade count follows later SNL; conflicting HB counts remain open.',
                             'Bend radius reference, sideways chevron orientation and pitches are provisional.',
                             'Frame contours, retaining/packing dimensions and attachment positions are approximate.',
                             'Shared distance pieces, end packings, saddles, cleats, fasteners and rear deflector remain unpopulated.'])
    write(out/'reports/louvers.json',result)
    return result
