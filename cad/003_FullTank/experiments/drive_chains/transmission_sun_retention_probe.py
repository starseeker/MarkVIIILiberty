"""Install both M290 small-sun rings and verify the mating sleeve/drum revisions."""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--output',type=Path,default=ROOT/'transmission_sun_retention_build');p.add_argument('--worker',action='store_true')
args=p.parse_args();stage=args.stage.resolve();out=args.output.resolve();sys.path.insert(0,str(stage))
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
    from lib.cad_build import leaves,metadata,shape_signature
    from lib.worker import check_build,same_shape,placement_errors
    from transmission_sun_retention_parts import retention_parts
    from transmission_core_parts import cylinder
    lock=fingerprint();build=check_build(stage/'build');parent=ROOT/'transmission_small_support_build'
    names=['transmission_sun_retention_probe.py','transmission_sun_retention_parts.py',
        'transmission_sun_retention_controls.json','transmission_sun_retention_sources.json',
        'transmission_core_parts.py','transmission_bush_controls.json','transmission_output_calibration.json',
        'transmission_core_build/report.json','transmission_small_support_build/report.json',
        'transmission_small_support_build/interface_checks.json','transmission_small_support_build/visual_review.json',
        'transmission_small_support_build/TransmissionSmallSupportCandidate.FCStd']
    hashes={n:sha(ROOT/n) for n in names}
    for n in names:
        if '/' not in n:
            dest=out/'inputs'/n;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/n).read_bytes())
    source=read(ROOT/'transmission_sun_retention_sources.json')
    for n,h in source['inspected_source_hashes'].items():assert sha(REPO/n)==h,n
    prior=read(parent/'report.json');assert prior['passed'] and prior['rendering_complete']
    assert sha(parent/'TransmissionSmallSupportCandidate.FCStd')==prior['native_sha256']
    assert prior['authored_fingerprint']==lock and prior['tank_native_hashes']==build['native_hashes']
    c={k:v['value'] for k,v in read(ROOT/'transmission_sun_retention_controls.json')['controls'].items()}
    rc={k:v['value'] for k,v in read(ROOT/'transmission_bush_controls.json')['controls'].items()}
    doc=App.openDocument(str(parent/'TransmissionSmallSupportCandidate.FCStd'));doc.recompute()
    before=leaves(doc.Root);old={i['id']:i for i in before};signatures={i['id']:shape_signature(i['shape']) for i in before}
    old_sun=old['PortSmallPlanetTrain_sun']['target'].Shape.copy();old_drum=old['PortTransmissionCore_high_drum']['target'].Shape.copy()
    definition=old['PortTransmissionBearing_OuterRing']['target'];original_ring=definition.Shape.copy()
    shapes,dimensions,ungrooved=retention_parts(c,rc,read(ROOT/'transmission_output_calibration.json'),
        read(ROOT/'transmission_core_build/report.json')['output_center_y_mm'],prior['gear_dimensions'],old_sun,old_drum,original_ring)
    changed=[];new_ids=[];expected={}
    for key,name in [('sun','PortSmallPlanetTrain_sun'),('drum','PortTransmissionCore_high_drum')]:
        target=old[name]['target'];target.Tip.Shape=shapes[key]
        metadata(target,SunRetentionRevision='Shared M290 rings in complete sleeve collars; smooth outboard shoulder and drum counterbores. Fits are inferred.',
            ParameterUpdate='Regenerate with transmission_sun_retention_probe.py using transmission_sun_retention_controls.json.',
            ReconstructionNotes='Small planet supports are populated. Brake bearing M265, cap M266 and its M300 dowel remain pending; this revision qualifies only nominal drum/sun retention.')
    for hand in ['Port','Starboard']:
        group=doc.addObject('App::Part',hand+'SunRetention');doc.getObject(hand+'TransmissionCore').addObject(group)
        group.Placement=App.Placement(App.Vector(),App.Rotation(App.Vector(1,0,0),180) if hand=='Starboard' else App.Rotation())
        metadata(group,Scope='One reused M290 retaining ring on M267; nominal groove and drum counterbore. Brake-bearing stack pending.')
        name=hand+'SunRetention_ring';link=doc.addObject('App::Link',name);group.addObject(link);link.setLink(definition)
        link.LinkPlacement=App.Placement(App.Vector(0,dimensions['ring_center_y_mm'],0),App.Rotation(App.Vector(0,1,0),c['ring_gap_phase']))
        metadata(link,OccurrenceId=name,Subsystem='Drivetrain',SourceRecord='SNL:165:013')
        new_ids.append(name);expected[name]=doc.TransmissionCore.Placement.multiply(group.Placement).multiply(link.LinkPlacement)
        changed += [hand+'SmallPlanetTrain_sun',hand+'TransmissionCore_high_drum']
        metadata(doc.getObject(hand+'SmallPlanetTrain'),Scope='Small epicyclic gears, bushed sun sleeve, swept input disk and riveted ring; adjacent support groups populated, brake bearings pending.')
    doc.Definitions.Visibility=False;doc.recompute();native=out/'TransmissionSunRetentionCandidate.FCStd'
    doc.saveAs(str(native));App.closeDocument(doc.Name);doc=App.openDocument(str(native));doc.recompute()
    items=leaves(doc.Root);byid={i['id']:i for i in items}
    assert len(items)==len(byid)==len(before)+2==1117
    for i in items:
        name=i['id'];assert i['shape'].isValid() and len(i['shape'].Solids)==1,name
        if name in expected:
            t,r=placement_errors(i['shape'].Placement,expected[name].multiply(i['target'].Shape.Placement));assert t<1e-6 and r<1e-8,name
        elif name not in changed:assert same_shape(signatures[name],shape_signature(i['shape'])),name
    ring_ids=[i['id'] for i in items if 'P_83e68d86c2852df1' in json.loads(i['target'].SurveyIds)]
    assert len(ring_ids)==6 and len({byid[n]['target'].Name for n in ring_ids})==1
    assert all(byid[n]['target']==byid[new_ids[0]]['target'] for n in ring_ids)
    print('Reopened1117 valid leaves:2 new rings,4 changed mating parts,1111 unchanged.',flush=True)
    tank=App.openDocument(build['build']['top_document']);tank.recompute()
    excluded={'hull_engine_back','PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting','hull_port_inner_rear_end',
        'hull_port_rear_wing','hull_starboard_inner_rear_end','hull_starboard_rear_wing'}
    context=[i for i in leaves(tank.Root) if i['id'] not in excluded and i['representation']=='assembly']
    physical=items+context;assert len({i['id'] for i in physical})==len(physical)
    boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].copy().cleaned().BoundBox for i in physical]])
    pairs=set();overlaps=[]
    for name in new_ids+changed:
        s=byid[name]['shape'];b=s.copy().cleaned().BoundBox;bb=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
        near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
        for index in near:
            other=physical[index];pair=tuple(sorted([name,other['id']]))
            if pair[0]==pair[1] or pair in pairs:continue
            pairs.add(pair);v=s.common(other['shape']).Volume
            if v>1e-5:overlaps.append(dict(a=name,b=other['id'],volume_mm3=v))
        write(out/'material_progress.json',dict(last_id=name,pairs=len(pairs),overlaps=overlaps))
    interfaces=[]
    def gap(a,b,wanted):
        value=byid[a]['shape'].distToShape(byid[b]['shape'])[0]
        interfaces.append(dict(a=a,b=b,gap_mm=value,expected_mm=wanted,passed=abs(value-wanted)<1e-5))
    for row in prior['interfaces']:gap(row['a'],row['b'],row['expected_mm'])
    retention=[]
    for hand in ['Port','Starboard']:
        names=dict(ring=hand+'SunRetention_ring',sun=hand+'SmallPlanetTrain_sun',drum=hand+'TransmissionCore_high_drum')
        gap(names['ring'],names['sun'],rc['ring_axial_gap']);gap(names['ring'],names['drum'],c['drum_ring_radial_gap'])
        origin=doc.TransmissionCore.Placement.Base
        axis=App.Vector(0,1 if hand=='Port' else -1,0)
        for what,others in [('ring',['sun']),('drum',['sun','ring'])]:
            for direction in [-1,1]:
                s=byid[names[what]]['shape'].copy();s.translate(axis*(direction*c['retention_trial_translation']))
                v=sum(s.common(byid[names[k]]['shape']).Volume for k in others)
                retention.append(dict(hand=hand,moving=what,translation_mm=direction*c['retention_trial_translation'],captured_volume_mm3=v,passed=v>1))
        for sign in [-1,1]:
            s=byid[names['drum']]['shape'].copy();s.rotate(origin,axis,sign*c['spline_trial_twist'])
            v=s.common(byid[names['sun']]['shape']).Volume
            retention.append(dict(hand=hand,moving='drum',twist_deg=sign*c['spline_trial_twist'],captured_volume_mm3=v,passed=v>1))
    negative_ring=shapes['ring'].common(ungrooved).Volume
    assert negative_ring>1
    # The change must preserve the tooth band and outside of the original drum.
    band=cylinder(100,prior['gear_dimensions']['gear_band_y_mm'][0],prior['gear_dimensions']['gear_band_y_mm'][1])
    outer=cylinder(200,190,300).cut(cylinder(58,189,301))
    protections={}
    for name,a,b,region in [('sun_teeth',old_sun,shapes['sun'],band),('drum_outer',old_drum,shapes['drum'],outer)]:
        a=a.common(region);b=b.common(region);protections[name]=a.cut(b).Volume+b.cut(a).Volume
        assert protections[name]<1e-5
    reused=byid[new_ids[0]]['target'].Shape;reuse_difference=reused.cut(original_ring).Volume+original_ring.cut(reused).Volume
    assert reuse_difference<1e-5
    print('Material pairs',len(pairs),'overlaps',overlaps,flush=True)
    print('Failed interfaces',[r for r in interfaces if not r['passed']],flush=True)
    print('Failed capture trials',[r for r in retention if not r['passed']],flush=True)
    exchange=out/'TransmissionSunRetentionParts.step';exchange_ids=new_ids+changed
    Part.makeCompound([byid[n]['shape'] for n in exchange_ids]).exportStep(str(exchange))
    imported=Part.Shape();imported.read(str(exchange));assert imported.isValid() and len(imported.Solids)==len(exchange_ids)
    unmatched=list(imported.Solids);exchange_checks=[]
    for name in exchange_ids:
        a=byid[name]['shape'].Solids[0];n=min(range(len(unmatched)),key=lambda n:(a.CenterOfMass-unmatched[n].CenterOfMass).Length);b=unmatched.pop(n)
        ta=a.getTolerance(1);tb=b.getTolerance(1);fuzzy=min(.0001,max(1e-7,ta+tb))
        raw_a=a.cut(b);raw_b=b.cut(a);missing=a.cut(b,fuzzy);extra=b.cut(a,fuzzy)
        exchange_checks.append(dict(id=name,comparison_fuzzy_tolerance_mm=fuzzy,native_max_tolerance_mm=ta,step_max_tolerance_mm=tb,
            raw_missing_mm3=raw_a.Volume,raw_added_mm3=raw_b.Volume,missing_mm3=missing.Volume,added_mm3=extra.Volume,
            missing_faces=len(missing.Faces),added_faces=len(extra.Faces),
            passed=a.isValid() and b.isValid() and not missing.Faces and not extra.Faces and ta<=.0001 and tb<=max(1e-7,ta)*(1+1e-6)))
        write(out/'exchange_progress.json',dict(completed=len(exchange_checks),failed=[r for r in exchange_checks if not r['passed']]))
    passed=not overlaps and all(r['passed'] for r in interfaces+retention+exchange_checks)
    assert fingerprint()==lock and check_build(stage/'build')['native_hashes']==build['native_hashes']
    assert all(sha(ROOT/n)==h for n,h in hashes.items())
    report=dict(complete=True,passed=passed,native_occurrences=len(items),new_occurrences=2,new_definitions=0,reused_definitions=1,
        changed_prior_occurrences=4,unchanged_prior_occurrences=1111,new_source_counts={'P_83e68d86c2852df1':2},all_M290_occurrences=ring_ids,
        new_ids=new_ids,changed_ids=changed,material_candidate_pairs=len(pairs),overlaps=overlaps,interfaces=interfaces,retention_checks=retention,
        ungrooved_sun_negative_overlap_mm3=negative_ring,protected_material_differences_mm3=protections,reused_ring_material_difference_mm3=reuse_difference,
        dimensions=dimensions,gear_dimensions=prior['gear_dimensions'],shaft_axis_world_mm=prior['shaft_axis_world_mm'],
        input_hashes=hashes,authored_fingerprint=lock,tank_native_hashes=build['native_hashes'],native_sha256=sha(native),exchange_sha256=sha(exchange),
        exchange_roundtrip_checks=exchange_checks,standard_assembly_modified=False,complete_transmission=False,historical_fit_qualified=False,
        elastic_ring_installation_qualified=False,full_parameter_envelope_qualified=False,rendering_complete=False)
    write(out/'report.json',report)
    print('PASS' if passed else 'FAIL',flush=True);sys.exit(0 if passed else 1)
finally:runtime.close()
