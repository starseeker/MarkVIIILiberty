"""Populate both large-planet support stacks and verify their physical receivers."""
import argparse
import base64
from collections import Counter
import json
import math
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage',type=Path,required=True)
parser.add_argument('--output',type=Path,default=ROOT/'transmission_pin_build')
parser.add_argument('--worker',action='store_true')
args=parser.parse_args();stage=args.stage.resolve();out=args.output.resolve();sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import read,write,sha,fingerprint,REPO
if not args.worker:
    out.mkdir(parents=True,exist_ok=True)
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--output',str(out),'--worker'],
                               env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui()
    import Part
    import numpy as np
    from lib.cad_build import leaves,metadata,shape_signature,COLORS
    from lib.worker import check_build,same_shape,placement_errors
    from lib.visual_review import shaded
    from transmission_pin_parts import pin_parts,positioned
    from transmission_core_parts import box,cylinder
    lock=fingerprint();build=check_build(stage/'build')
    names=['transmission_pin_probe.py','transmission_pin_parts.py','transmission_pin_controls.json','transmission_pin_sources.json',
           'transmission_stud_parts.py','transmission_core_parts.py','transmission_output_calibration.json',
           'transmission_planet_build/report.json','transmission_planet_build/visual_review.json',
           'transmission_planet_build/interface_checks.json','transmission_planet_build/TransmissionPlanetCandidate.FCStd']
    hashes={name:sha(ROOT/name) for name in names}
    for name in names:
        if '/' not in name:
            path=out/'inputs'/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((ROOT/name).read_bytes())
    source=read(ROOT/'transmission_pin_sources.json')
    for name,digest in source['source_hashes'].items():assert sha(REPO/name)==digest,name
    c={k:v['value'] for k,v in read(ROOT/'transmission_pin_controls.json')['controls'].items()}
    prior=read(ROOT/'transmission_planet_build/report.json')
    assert prior['passed'] and prior['native_sha256']==hashes[names[-1]]
    assert prior['authored_fingerprint']==lock and prior['tank_native_hashes']==build['native_hashes']
    doc=App.openDocument(str(ROOT/names[-1]));doc.recompute();before=leaves(doc.Root)
    old={i['id']:i for i in before};signatures={i['id']:shape_signature(i['shape']) for i in before}
    origin=App.Vector(*prior['shaft_axis_world_mm']);carrier=old['PortTransmissionCore_planet_disk']
    old_carrier=carrier['target'].Shape.copy();frames={}
    for hand in ['Port','Starboard']:
        item=old[hand+'TransmissionCore_planet_disk'];frames[hand]=item['shape'].Placement.multiply(item['target'].Shape.Placement.inverse())
    shapes,revised,dimensions=pin_parts(c,prior['dimensions'],old_carrier)
    print('Constructed support parts and carrier receivers.',flush=True)
    carrier['target'].Tip.Shape=revised
    metadata(carrier['target'],ReceiverRevision='Three recessed planet-pin bearing seats and three pin-ring bolt bosses with drilled receivers; controls in transmission_pin_controls.json.')
    changed_ids=['PortTransmissionCore_planet_disk','StarboardTransmissionCore_planet_disk']
    definitions={}
    for row in source['physical_inventory']:
        key=row['key'];body=doc.addObject('PartDesign::Body','Def_TransmissionPin_'+key);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedPart').Shape=shapes[key]
        metadata(body,DefinitionId='transmission_pin_'+key,OriginalMark=row['mark'],SurveyIds=[row['part_id']],SourceRecord=row['record_id'],
            Representation='assembly',Coverage='partial',ParameterUpdate='Regenerate from versioned transmission_pin_controls.json.',
            ReconstructionNotes='Source component identity and selected printed hardware sizes; inferred cast contours, sleeve shoulders, pin diameters and axial stack. Smooth thread envelopes, no clamp/load or running-fit qualification.')
        if key=='bronze':metadata(body,IdentityDisposition='M282 selected from SNL43 and HB122; SNL251/252 bronze-bush marks conflict and are retained without merging survey IDs.')
        definitions[key]=body
    new_ids=[];key_for={};expected={};station_for={}
    for hand in ['Port','Starboard']:
        group=doc.addObject('App::Part',hand+'PlanetSupports');doc.getObject(hand+'TransmissionCore').addObject(group)
        group.Placement=App.Placement(App.Vector(),frames[hand].Rotation)
        metadata(group,Scope='Three large-planet pin and bearing stacks with separate M285 pin ring and three M318 fastening stacks. Rotor phase inherited from M286.')
        def install(key,index=None,radius=0,angle=0):
            name=hand+'PlanetSupports_'+key+('' if index is None else str(index));link=doc.addObject('App::Link',name);group.addObject(link);link.setLink(definitions[key])
            link.LinkPlacement=App.Placement(App.Vector(radius*math.cos(angle),0,radius*math.sin(angle)),App.Rotation(App.Vector(0,1,0),-math.degrees(angle)))
            metadata(link,OccurrenceId=name,Subsystem='Drivetrain')
            expected[name]=doc.TransmissionCore.Placement.multiply(group.Placement).multiply(link.LinkPlacement)
            new_ids.append(name);key_for[name]=key;station_for[name]=dict(hand=hand,index=index,radius_mm=radius,local_angle_rad=angle)
        install('pin_ring')
        for n in range(3):
            angle=n*2*math.pi/3
            for key in ['pin','bronze','steel','nut','cotter','plug']:install(key,n,prior['dimensions']['planet_center_radius_mm'],angle)
            for key in ['bolt','bolt_nut','bolt_cotter']:install(key,n,c['bolt_circle_radius'],angle+math.pi/3)
    doc.Definitions.Visibility=False;doc.recompute();native=out/'TransmissionPinCandidate.FCStd'
    doc.saveAs(str(native));App.closeDocument(doc.Name);doc=App.openDocument(str(native));doc.recompute()
    items=leaves(doc.Root);byid={i['id']:i for i in items}
    assert len(items)==len(byid)==len(before)+sum(r['count'] for r in source['physical_inventory'])
    for item in items:
        assert item['shape'].isValid() and len(item['shape'].Solids)==1,item['id']
        if item['id'] in new_ids:
            pose=expected[item['id']].multiply(item['target'].Shape.Placement)
            t,r=placement_errors(item['shape'].Placement,pose);assert t<1e-6 and r<1e-8,item['id']
        elif item['id'] not in changed_ids:assert same_shape(signatures[item['id']],shape_signature(item['shape'])),item['id']
    counts=Counter(pid for n in new_ids for pid in json.loads(byid[n]['target'].SurveyIds))
    assert dict(counts)=={r['part_id']:r['count'] for r in source['physical_inventory']}
    print('Reopened',len(items),'valid single-solid leaves;',len(before)-2,'unchanged.',flush=True)
    tank=App.openDocument(build['build']['top_document']);tank.recompute()
    excluded={'hull_engine_back','PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting',
              'hull_port_inner_rear_end','hull_port_rear_wing','hull_starboard_inner_rear_end','hull_starboard_rear_wing'}
    context=[i for i in leaves(tank.Root) if i['id'] not in excluded and i['representation']=='assembly']
    physical=items+context;assert len({i['id'] for i in physical})==len(physical)
    boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].copy().cleaned().BoundBox for i in physical]])
    pairs=set();overlaps=[]
    for name in new_ids+changed_ids:
        shape=byid[name]['shape'];b=shape.copy().cleaned().BoundBox;bb=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
        near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
        for index in near:
            other=physical[index];pair=tuple(sorted([name,other['id']]))
            if pair[0]==pair[1] or pair in pairs:continue
            pairs.add(pair);volume=shape.common(other['shape']).Volume
            if volume>1e-5:overlaps.append(dict(a=name,b=other['id'],volume_mm3=volume))
    interfaces=[]
    def distance(a,b,expected_gap):
        gap=byid[a]['shape'].distToShape(byid[b]['shape'])[0]
        interfaces.append(dict(a=a,b=b,gap_mm=gap,expected_mm=expected_gap,passed=abs(gap-expected_gap)<1e-5))
    for hand in ['Port','Starboard']:
        prefix=hand+'PlanetSupports_';carrier_id=hand+'TransmissionCore_planet_disk'
        distance(prefix+'pin_ring',carrier_id,0)
        for n in range(3):
            name=lambda key:prefix+key+str(n)
            for a,b,gap in [('bronze','steel',c['bronze_bore_radius']-c['steel_radius']),('steel','pin',0),('nut','pin',c['nut_bore_gap']),('cotter','pin',c['cotter_hole_gap']),('cotter','nut',c['cotter_slot_gap']/2),('plug','pin',0),('bolt_cotter','bolt',c['cotter_hole_gap']),('bolt_cotter','bolt_nut',c['cotter_slot_gap']/2)]:distance(name(a),name(b),gap)
            for key,gap in [('pin',0),('steel',0),('bronze',c['ring_face_gap']),('bolt',0)]:distance(name(key),prefix+'pin_ring',gap)
            for key in ['steel','nut','bolt_nut']:distance(name(key),carrier_id,0)
            distance(name('bronze'),hand+'PlanetTrain_planet'+str(n),0)
            distance(name('steel'),hand+'PlanetTrain_planet'+str(n),c['gear_steel_face_gap'])
        distance(hand+'PlanetTrain_washer',carrier_id,.1)
        distance(hand+'TransmissionBearing_InnerRing',carrier_id,.2*read(ROOT/'transmission_output_calibration.json')['mm_per_pixel'])
    # Receiver edits must not alter the source spline/hub surfaces inside radius100.
    protected=cylinder(100,400,650)
    a=old_carrier.common(protected);b=byid['PortTransmissionCore_planet_disk']['target'].Shape.common(protected)
    protected_change=a.cut(b).Volume+b.cut(a).Volume;assert protected_change<1e-5
    print('Material:',len(pairs),'pairs;',len(overlaps),'overlaps. Interfaces:',all(r['passed'] for r in interfaces),flush=True)
    for row in overlaps+[r for r in interfaces if not r['passed']]:print('FAILED',row,flush=True)
    exchange_ids=new_ids+changed_ids;exchange=out/'TransmissionPinParts.step'
    Part.makeCompound([byid[n]['shape'] for n in exchange_ids]).exportStep(str(exchange))
    imported=Part.Shape();imported.read(str(exchange));assert imported.isValid() and len(imported.Solids)==len(exchange_ids)
    unmatched=list(imported.Solids);exchange_checks=[]
    # Budget native modeling tolerance against the smallest clearance actually
    # claimed by this assembly; additionally reject tolerance inflation on import.
    smallest_gap=min(r['expected_mm'] for r in interfaces if r['expected_mm']>0)
    tolerance_budget=smallest_gap/1000
    for name in exchange_ids:
        a=byid[name]['shape'].Solids[0]
        index=min(range(len(unmatched)),key=lambda n:(a.CenterOfMass-unmatched[n].CenterOfMass).Length)
        b=unmatched.pop(index);dv=abs(a.Volume-b.Volume);dc=(a.CenterOfMass-b.CenterOfMass).Length
        # Report mass-property differences, but inspect the actual material in
        # both directions. Trimmed curved surfaces can retain the same material
        # while native and STEP readers report different integrated properties.
        missing=a.cut(b);added=b.cut(a)
        ta=a.getTolerance(1);tb=b.getTolerance(1)
        exchange_checks.append(dict(id=name,volume_difference_mm3=dv,center_difference_mm=dc,
            strict_mass_property_agreement=dv<max(1e-3,a.Volume*1e-8) and dc<1e-5,
            native_max_tolerance_mm=ta,step_max_tolerance_mm=tb,
            missing_volume_mm3=missing.Volume,added_volume_mm3=added.Volume,
            missing_faces=len(missing.Faces),added_faces=len(added.Faces),
            native_tolerance_budget_mm=tolerance_budget,
            import_tolerance_not_inflated=tb<=max(1e-7,ta)*(1+1e-6),
            passed=a.isValid() and b.isValid() and ta<=tolerance_budget
                   and tb<=max(1e-7,ta)*(1+1e-6)
                   and not missing.Faces and not added.Faces
                   and abs(missing.Volume)<1e-5 and abs(added.Volume)<1e-5))
    if not all(r['passed'] for r in exchange_checks):
        write(out/'exchange_failure.json',exchange_checks)
        raise ValueError('STEP material/tolerance mismatch; see exchange_failure.json')
    passed=not overlaps and all(row['passed'] for row in interfaces)
    report=dict(complete=True,passed=passed,native_occurrences=len(items),new_occurrences=len(new_ids),changed_prior_occurrences=2,unchanged_prior_occurrences=len(before)-2,
        new_source_counts=dict(counts),material_candidate_pairs=len(pairs),overlaps=overlaps,interfaces=interfaces,
        dimensions=dimensions,gear_dimensions=prior['dimensions'],shaft_axis_world_mm=list(origin),protected_carrier_hub_difference_mm3=protected_change,
        new_ids=new_ids,changed_ids=changed_ids,keys_by_id=key_for,stations_by_id=station_for,
        expected_placements={n:dict(base=list(p.Base),quaternion=list(p.Rotation.Q)) for n,p in expected.items()},
        input_hashes=hashes,authored_fingerprint=lock,tank_native_hashes=build['native_hashes'],native_sha256=sha(native),exchange_sha256=sha(exchange),exchange_roundtrip_solids=len(imported.Solids),exchange_roundtrip_checks=exchange_checks,
        exchange_qualification='Bijective nearest-center matching, valid solids, no residual faces/material in either Boolean difference, native tolerance <=0.1% of the smallest specified positive interface gap, no increase in maximum tolerance on import. Mass-property deltas retained separately; no geometric tolerance is changed.',
        standard_assembly_modified=False,complete_transmission=False,historical_fit_qualified=False,full_parameter_envelope_qualified=False,thread_clamp_qualified=False,rendering_complete=False)
    write(out/'report.json',report)
    print('Material:',len(pairs),'pairs;',len(overlaps),'overlaps. Interfaces:',all(r['passed'] for r in interfaces),flush=True)
    for row in overlaps+[r for r in interfaces if not r['passed']]:print('FAILED',row,flush=True)
    COLORS.update(PinMetal=(.57,.61,.65),PinBronze=(.65,.49,.25),PinCarrier=(.43,.56,.49),PinGear=(.65,.54,.32))
    def colored(i):
        key=key_for.get(i['id']);system='PinBronze' if key=='bronze' else 'PinCarrier' if key=='pin_ring' or i['id'] in changed_ids else 'PinMetal' if key else 'PinGear'
        return dict(i,system=system)
    selected=[colored(i) for i in items if i['id'] in new_ids+changed_ids or i['id'].startswith(('PortPlanetTrain_','StarboardPlanetTrain_'))]
    port=[i for i in selected if i['id'].startswith('Port')]
    shaded(port,out/'supported_planets.svg',(1,-1,.7),'Large planetary train | separate pin ring, bushes, pins and fastening')
    shaded([i for i in port if 'PlanetSupports_' in i['id'] or i['id'] in changed_ids],out/'carrier_and_pins.svg',(1,-1,.7),'Carrier and pin-ring connection | gears omitted for inspection')
    section=[]
    for i in selected:
        b=i['shape'].copy().cleaned().BoundBox
        if b.ZMin>=origin.z:continue
        shape=i['shape'].common(box(b.XMin-1,b.XMax+1,b.YMin-1,b.YMax+1,b.ZMin-1,origin.z))
        if shape.isNull() or not shape.Solids:continue
        section.append(dict(i,definition=i['definition']+'_cut_'+i['id'],shape=shape,target=SimpleNamespace(Shape=shape)))
    shaded(section,out/'supported_gears_cutaway.svg',(1,1,1.2),'Planet support cutaway | bearing sleeves and physical carrier receivers')
    # Actual source-height section retains the prior drawing calibration.
    cal=read(ROOT/'transmission_output_calibration.json');yout=read(ROOT/'transmission_core_build/report.json')['output_center_y_mm']
    bg=base64.b64encode((REPO/cal['image']).read_bytes()).decode()
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1724" height="1147">',f'<image width="1724" height="1147" href="data:image/png;base64,{bg}" opacity=".60"/>']
    plane=Part.makePlane(3000,3000,App.Vector(origin.x-1500,-1500,origin.z),App.Vector(0,0,1))
    for i in port:
        if i['id'] not in new_ids+changed_ids:continue
        color='#b87912' if key_for.get(i['id'])=='bronze' else '#b02631' if key_for.get(i['id'])=='pin_ring' else '#1764ba'
        for edge in i['shape'].section(plane).Edges:
            points=[f'{cal["sprocket_center_x_px"]-(v.y-yout)/cal["mm_per_pixel"]:.3f},{cal["shaft_axis_y_px"]+(v.x-origin.x)/cal["mm_per_pixel"]:.3f}' for v in edge.discretize(Deflection=.3)]
            svg.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="1.5"/>')
    svg+=['<rect x="24" y="1070" width="1675" height="66" fill="white"/>',
          '<text x="36" y="1096" font-family="sans-serif" font-size="17">Actual horizontal section: red pin ring, ochre bronze, blue pins/sleeves/receivers. Cast profiles remain inferred.</text>',
          '<text x="36" y="1120" font-family="sans-serif" font-size="16">Three stations at 120 degrees; most pin axes are outside this plane. See separate local-axis section for bearing detail.</text></svg>']
    path=out/'source_plate22_overlay.svg';path.write_text('\n'.join(svg))
    import fitz
    with fitz.open(stream=path.read_bytes(),filetype='svg') as drawing:drawing[0].get_pixmap().save(str(path.with_suffix('.png')))
    assert fingerprint()==lock and check_build(stage/'build')['native_hashes']==build['native_hashes']
    assert all(sha(ROOT/n)==digest for n,digest in hashes.items())
    report.update(rendering_complete=True,output_raster_hashes={p.name:sha(p) for p in out.glob('*.png')});write(out/'report.json',report)
    print('PASS' if passed else 'FAIL',flush=True);sys.exit(0 if passed else 1)
finally:runtime.close()
