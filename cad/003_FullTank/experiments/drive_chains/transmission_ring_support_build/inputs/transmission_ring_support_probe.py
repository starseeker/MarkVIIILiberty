"""Reconcile the actual M318 source station and verify the revised support joint."""
import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage',type=Path,required=True)
parser.add_argument('--output',type=Path,default=ROOT/'transmission_ring_support_build')
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
    from transmission_core_parts import cylinder,box
    from transmission_ring_support_parts import revised_ring_supports
    lock=fingerprint();build=check_build(stage/'build')
    names=['transmission_ring_support_probe.py','transmission_ring_support_parts.py',
           'transmission_ring_support_controls.json','transmission_ring_support_sources.json',
           'transmission_pin_parts.py','transmission_pin_controls.json','transmission_stud_parts.py','transmission_core_parts.py',
           'transmission_pin_build/report.json','transmission_pin_build/visual_review.json','transmission_pin_build/interface_checks.json',
           'transmission_pin_build/TransmissionPinCandidate.FCStd','transmission_planet_build/TransmissionPlanetCandidate.FCStd',
           'transmission_output_calibration.json']
    hashes={n:sha(ROOT/n) for n in names}
    for name in names:
        if '/' not in name:
            p=out/'inputs'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/name).read_bytes())
    source=read(ROOT/'transmission_ring_support_sources.json')
    for name,digest in source['source_hashes'].items():assert sha(REPO/name)==digest,name
    prior=read(ROOT/'transmission_pin_build/report.json')
    assert prior['passed'] and prior['native_sha256']==hashes['transmission_pin_build/TransmissionPinCandidate.FCStd']
    assert prior['authored_fingerprint']==lock and prior['tank_native_hashes']==build['native_hashes']
    c={k:v['value'] for k,v in read(ROOT/'transmission_pin_controls.json')['controls'].items()}
    rc={k:v['value'] for k,v in read(ROOT/'transmission_ring_support_controls.json')['controls'].items()}
    original=App.openDocument(str(ROOT/'transmission_planet_build/TransmissionPlanetCandidate.FCStd'));original.recompute()
    original_carrier=next(i for i in leaves(original.Root) if i['id']=='PortTransmissionCore_planet_disk')['target'].Shape.copy()
    App.closeDocument(original.Name)
    doc=App.openDocument(str(ROOT/'transmission_pin_build/TransmissionPinCandidate.FCStd'));doc.recompute()
    before=leaves(doc.Root);old={i['id']:i for i in before};signatures={i['id']:shape_signature(i['shape']) for i in before}
    previous_carrier=old['PortTransmissionCore_planet_disk']['target'].Shape.copy()
    parts,dimensions=revised_ring_supports(c,rc,prior['gear_dimensions'],original_carrier)
    targets={'carrier':old['PortTransmissionCore_planet_disk']['target'],'pin_ring':old['PortPlanetSupports_pin_ring']['target']}
    targets.update({k:old['PortPlanetSupports_'+k+'0']['target'] for k in ['bolt','bolt_nut','bolt_cotter']})
    for name,target in targets.items():
        target.Tip.Shape=parts[name]
        metadata(target,RingSupportRevision='M318 callout15 station; source-scaled head/nut seats, inferred recessed casting receivers and axial head counterbores. See transmission_ring_support_controls.json.',
            ParameterUpdate='Regenerate with transmission_ring_support_probe.py using transmission_ring_support_controls.json and inherited transmission_pin_controls.json.')
    changed=[];expected={};stations=prior['stations_by_id'].copy()
    for hand in ['Port','Starboard']:
        changed += [hand+'TransmissionCore_planet_disk',hand+'PlanetSupports_pin_ring']
        for n in range(3):
            for key in ['bolt','bolt_nut','bolt_cotter']:
                name=hand+'PlanetSupports_'+key+str(n);link=doc.getObject(name);angle=stations[name]['local_angle_rad']
                place=link.LinkPlacement;place.Base=App.Vector(rc['bolt_circle_radius']*math.cos(angle),0,rc['bolt_circle_radius']*math.sin(angle));link.LinkPlacement=place
                stations[name]=dict(stations[name],radius_mm=rc['bolt_circle_radius'])
                group=doc.getObject(hand+'PlanetSupports')
                expected[name]=doc.TransmissionCore.Placement.multiply(group.Placement).multiply(place)
                changed.append(name)
    doc.Definitions.Visibility=False;doc.recompute();native=out/'TransmissionRingSupportCandidate.FCStd'
    doc.saveAs(str(native));App.closeDocument(doc.Name);doc=App.openDocument(str(native));doc.recompute()
    items=leaves(doc.Root);byid={i['id']:i for i in items}
    assert len(items)==len(byid)==len(before)==1013 and len(changed)==22
    for item in items:
        assert item['shape'].isValid() and len(item['shape'].Solids)==1,item['id']
        if item['id'] not in changed:assert same_shape(signatures[item['id']],shape_signature(item['shape'])),item['id']
        if item['id'] in expected:
            pose=expected[item['id']].multiply(item['target'].Shape.Placement)
            t,r=placement_errors(item['shape'].Placement,pose);assert t<1e-6 and r<1e-8,item['id']
    tank=App.openDocument(build['build']['top_document']);tank.recompute()
    excluded={'hull_engine_back','PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting',
              'hull_port_inner_rear_end','hull_port_rear_wing','hull_starboard_inner_rear_end','hull_starboard_rear_wing'}
    context=[i for i in leaves(tank.Root) if i['id'] not in excluded and i['representation']=='assembly']
    physical=items+context;assert len({i['id'] for i in physical})==len(physical)
    boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].copy().cleaned().BoundBox for i in physical]])
    pairs=set();overlaps=[]
    for name in changed:
        shape=byid[name]['shape'];b=shape.copy().cleaned().BoundBox;bb=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
        near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
        for index in near:
            other=physical[index];pair=tuple(sorted([name,other['id']]))
            if pair[0]==pair[1] or pair in pairs:continue
            pairs.add(pair);volume=shape.common(other['shape']).Volume
            if volume>1e-5:overlaps.append(dict(a=name,b=other['id'],volume_mm3=volume))
    interfaces=[]
    for row in prior['interfaces']:
        gap=byid[row['a']]['shape'].distToShape(byid[row['b']]['shape'])[0]
        interfaces.append(dict(row,gap_mm=gap,passed=abs(gap-row['expected_mm'])<1e-5))
    protected=cylinder(100,400,650)
    a=previous_carrier.common(protected);b=parts['carrier'].common(protected)
    hub_difference=a.cut(b).Volume+b.cut(a).Volume;assert hub_difference<1e-5
    exchange=out/'TransmissionRingSupportParts.step';Part.makeCompound([byid[n]['shape'] for n in changed]).exportStep(str(exchange))
    imported=Part.Shape();imported.read(str(exchange));assert imported.isValid() and len(imported.Solids)==len(changed)
    unmatched=list(imported.Solids);exchange_checks=[]
    tolerance_budget=min(r['expected_mm'] for r in interfaces if r['expected_mm']>0)/1000
    for name in changed:
        a=byid[name]['shape'].Solids[0];index=min(range(len(unmatched)),key=lambda n:(a.CenterOfMass-unmatched[n].CenterOfMass).Length);b=unmatched.pop(index)
        missing=a.cut(b);added=b.cut(a);ta=a.getTolerance(1);tb=b.getTolerance(1)
        exchange_checks.append(dict(id=name,volume_difference_mm3=abs(a.Volume-b.Volume),center_difference_mm=(a.CenterOfMass-b.CenterOfMass).Length,
            native_max_tolerance_mm=ta,step_max_tolerance_mm=tb,native_tolerance_budget_mm=tolerance_budget,
            missing_volume_mm3=missing.Volume,added_volume_mm3=added.Volume,missing_faces=len(missing.Faces),added_faces=len(added.Faces),
            passed=a.isValid() and b.isValid() and ta<=tolerance_budget and tb<=max(1e-7,ta)*(1+1e-6)
                and not missing.Faces and not added.Faces and abs(missing.Volume)<1e-5 and abs(added.Volume)<1e-5))
    passed=not overlaps and all(r['passed'] for r in interfaces+exchange_checks)
    report=dict(complete=True,passed=passed,native_occurrences=len(items),new_occurrences=0,changed_prior_occurrences=len(changed),unchanged_prior_occurrences=len(before)-len(changed),
        material_candidate_pairs=len(pairs),overlaps=overlaps,interfaces=interfaces,dimensions=dimensions,gear_dimensions=prior['gear_dimensions'],
        shaft_axis_world_mm=prior['shaft_axis_world_mm'],protected_carrier_hub_difference_mm3=hub_difference,
        changed_ids=changed,keys_by_id=prior['keys_by_id'],stations_by_id=stations,
        input_hashes=hashes,authored_fingerprint=lock,tank_native_hashes=build['native_hashes'],native_sha256=sha(native),exchange_sha256=sha(exchange),
        exchange_roundtrip_solids=len(imported.Solids),exchange_roundtrip_checks=exchange_checks,
        standard_assembly_modified=False,complete_transmission=False,historical_fit_qualified=False,full_parameter_envelope_qualified=False,
        thread_clamp_qualified=False,rendering_complete=False)
    write(out/'report.json',report)
    print('Material pairs',len(pairs),'overlaps',overlaps,'failed interfaces',[r for r in interfaces if not r['passed']],flush=True)
    print('Failed exchange',[r for r in exchange_checks if not r['passed']],flush=True)
    COLORS.update(RingCarrier=(.43,.56,.49),RingMetal=(.57,.61,.65),RingBronze=(.68,.50,.24),RingGear=(.56,.49,.38))
    selected=[]
    for item in items:
        name=item['id'];key=prior['keys_by_id'].get(name)
        if not name.startswith(('PortPlanetSupports_','PortPlanetTrain_')) and name!='PortTransmissionCore_planet_disk':continue
        color='RingBronze' if key=='bronze' else 'RingCarrier' if key=='pin_ring' or name.endswith('planet_disk') else 'RingMetal' if key else 'RingGear'
        selected.append(dict(item,system=color))
    shaded(selected,out/'supported_planets.svg',(1,1,.7),'Large planetary support | corrected inner ring-bolt station and recessed seats')
    shaded([i for i in selected if not i['id'].startswith('PortPlanetTrain_')],out/'recessed_carrier.svg',(1,1,.7),'Carrier and pin ring | separate source-positioned fastening stacks')
    origin=App.Vector(*report['shaft_axis_world_mm']);section=[]
    for i in selected:
        b=i['shape'].copy().cleaned().BoundBox
        if b.ZMin>=origin.z:continue
        shape=i['shape'].common(box(b.XMin-1,b.XMax+1,b.YMin-1,b.YMax+1,b.ZMin-1,origin.z))
        if shape.isNull() or not shape.Solids:continue
        section.append(dict(i,shape=shape,target=SimpleNamespace(Shape=shape),definition=i['definition']+'_cut_'+i['id']))
    shaded(section,out/'ring_support_cutaway.svg',(1,1,1.2),'Ring support cutaway | revised bolt seats and retained large-planet bearings')
    assert fingerprint()==lock and check_build(stage/'build')['native_hashes']==build['native_hashes']
    assert all(sha(ROOT/n)==digest for n,digest in hashes.items())
    report.update(rendering_complete=True,output_raster_hashes={p.name:sha(p) for p in out.glob('*.png')});write(out/'report.json',report)
    print('PASS' if passed else 'FAIL',flush=True);sys.exit(0 if passed else 1)
finally:runtime.close()
