"""Install and verify both small-planet support stacks in the native hierarchy."""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--output',type=Path,default=ROOT/'transmission_small_support_build');p.add_argument('--worker',action='store_true')
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
    from lib.cad_build import leaves,metadata,shape_signature,COLORS
    from lib.worker import check_build,same_shape,placement_errors
    from lib.visual_review import shaded
    from transmission_small_support_parts import small_support_parts
    from transmission_small_disk_parts import swept_disk_parts
    from transmission_core_parts import box,cylinder
    lock=fingerprint();build=check_build(stage/'build');parent=ROOT/'transmission_small_build'
    names=['transmission_small_support_probe.py','transmission_small_support_parts.py',
        'transmission_small_support_controls.json','transmission_small_support_sources.json',
        'transmission_pin_parts.py','transmission_stud_parts.py','transmission_core_parts.py',
        'transmission_small_disk_parts.py','transmission_small_disk_controls.json','transmission_small_controls.json',
        'transmission_core_controls.json','transmission_planet_parts.py','transmission_output_calibration.json','transmission_core_build/report.json',
        'transmission_pin_build/report.json','transmission_small_build/report.json',
        'transmission_small_build/visual_review.json','transmission_small_build/interface_checks.json',
        'transmission_small_build/TransmissionSmallCandidate.FCStd']
    hashes={n:sha(ROOT/n) for n in names}
    for n in names:
        if '/' not in n:
            path=out/'inputs'/n;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((ROOT/n).read_bytes())
    source=read(ROOT/'transmission_small_support_sources.json')
    for n,h in source['inspected_source_hashes'].items():assert sha(REPO/n)==h,n
    prior=read(parent/'report.json');assert prior['passed'] and prior['rendering_complete']
    assert sha(parent/'TransmissionSmallCandidate.FCStd')==prior['native_sha256']
    assert prior['authored_fingerprint']==lock and prior['tank_native_hashes']==build['native_hashes']
    c={k:v['value'] for k,v in read(ROOT/'transmission_small_support_controls.json')['controls'].items()}
    doc=App.openDocument(str(parent/'TransmissionSmallCandidate.FCStd'));doc.recompute()
    before=leaves(doc.Root);old={i['id']:i for i in before};signatures={i['id']:shape_signature(i['shape']) for i in before}
    old_case=old['PortTransmissionCore_plain_case']['target'].Shape.copy()
    parts,case,dimensions=small_support_parts(c,prior['dimensions'],old_case)
    target=old['PortTransmissionCore_plain_case']['target'];target.Tip.Shape=case
    metadata(target,SmallSupportRevision='Three M274 pin seats and three alternating M317 ring-bolt seats, with explicit bores and thrust/access faces.',
        ParameterUpdate='Regenerate using transmission_small_support_probe.py and transmission_small_support_controls.json from the saved small-gear candidate.')
    sc={k:v['value'] for k,v in read(ROOT/'transmission_small_controls.json')['controls'].items()}
    dc={k:v['value'] for k,v in read(ROOT/'transmission_small_disk_controls.json')['controls'].items()}
    revised,disk_dimensions=swept_disk_parts(sc,dc,read(ROOT/'transmission_core_controls.json')['controls'],
        read(ROOT/'transmission_output_calibration.json'),read(ROOT/'transmission_core_build/report.json')['output_center_y_mm'],
        prior['dimensions'],old['PortSmallPlanetTrain_rivet0']['target'].Shape)
    for key in ['disk','ring','rivet']:
        target=old['PortSmallPlanetTrain_'+key+('0' if key=='rivet' else '')]['target'];target.Tip.Shape=revised[key]
        metadata(target,DiskRevision='Swept cubic B-spline disk transition and rim at approximate source rivet-center station; original blank/head size and gear teeth retained.',
            ParameterUpdate='Regenerate with transmission_small_support_probe.py using transmission_small_disk_controls.json and inherited small-gear controls.')
    definitions={};old_plug=old['PortPlanetSupports_plug0']['target']
    plug_y=read(ROOT/'transmission_pin_build/report.json')['dimensions']['plug_base_y_mm']+dimensions['plug_base_y_mm']
    plug_place=App.Placement(App.Vector(0,plug_y,0),App.Rotation(App.Vector(1,0,0),180))
    check=old_plug.Shape.copy();check.Placement=plug_place.multiply(check.Placement)
    plug_difference=check.cut(parts['plug']).Volume+parts['plug'].cut(check).Volume;assert plug_difference<1e-5
    for row in source['physical_inventory']:
        key=row['key']
        if key=='plug':definitions[key]=old_plug;continue
        body=doc.addObject('PartDesign::Body','Def_TransmissionSmallSupport_'+key);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedPart').Shape=parts[key]
        metadata(body,DefinitionId='transmission_small_support_'+key,OriginalMark=row['mark'],SurveyIds=[row['part_id']],
            SourceRecord=row['record_id'],Representation='assembly',Coverage='partial',
            ParameterUpdate='Regenerate with transmission_small_support_probe.py using transmission_small_support_controls.json.',
            ReconstructionNotes='Separate physical small-planet support parts; printed cotter/plug/bolt nominal sizes, inferred cast profiles, fits and nut dimensions. Threads and loads unqualified.')
        definitions[key]=body
    new_ids=[];keys={};expected={};stations={}
    for hand in ['Port','Starboard']:
        group=doc.addObject('App::Part',hand+'SmallPlanetSupports');doc.getObject(hand+'TransmissionCore').addObject(group)
        group.Placement=App.Placement(App.Vector(),App.Rotation(App.Vector(1,0,0),180) if hand=='Starboard' else App.Rotation())
        metadata(group,Scope='Three bushed M274 pins, M273 ring and three alternating M317 ring bolts with separate retention hardware.')
        for key in definitions:
            for n in range(1 if key=='pin_ring' else 3):
                isbolt=key.startswith('bolt');radius=0 if key=='pin_ring' else c['bolt_circle_radius'] if isbolt else dimensions['planet_center_radius_mm']
                angle=0 if key=='pin_ring' else n*2*math.pi/3+(math.pi/3 if isbolt else 0)
                name=hand+'SmallPlanetSupports_'+key+('' if key=='pin_ring' else str(n))
                link=doc.addObject('App::Link',name);group.addObject(link);link.setLink(definitions[key])
                place=App.Placement(App.Vector(radius*math.cos(angle),0,radius*math.sin(angle)),App.Rotation(App.Vector(0,1,0),-math.degrees(angle)))
                if key=='plug':place=place.multiply(plug_place)
                link.LinkPlacement=place;metadata(link,OccurrenceId=name,Subsystem='Drivetrain',SourceRecord=next(r['record_id'] for r in source['physical_inventory'] if r['key']==key))
                new_ids.append(name);keys[name]=key;expected[name]=doc.TransmissionCore.Placement.multiply(group.Placement).multiply(place)
                stations[name]=dict(radius_mm=radius,local_angle_rad=angle)
    doc.Definitions.Visibility=False;doc.recompute();native=out/'TransmissionSmallSupportCandidate.FCStd'
    doc.saveAs(str(native));App.closeDocument(doc.Name);doc=App.openDocument(str(native));doc.recompute()
    items=leaves(doc.Root);byid={i['id']:i for i in items};changed=[h+'TransmissionCore_plain_case' for h in ['Port','Starboard']]
    for h in ['Port','Starboard']:
        changed += [h+'SmallPlanetTrain_'+k for k in ['disk','ring']] + [h+'SmallPlanetTrain_rivet'+str(n) for n in range(16)]
    assert len(items)==len(byid)==len(before)+56==1115
    for i in items:
        name=i['id'];assert i['shape'].isValid() and len(i['shape'].Solids)==1,name
        if name in expected:
            t,r=placement_errors(i['shape'].Placement,expected[name].multiply(i['target'].Shape.Placement));assert t<1e-6 and r<1e-8,name
        elif name not in changed:assert same_shape(signatures[name],shape_signature(i['shape'])),name
    counts=Counter(pid for name in new_ids for pid in json.loads(byid[name]['target'].SurveyIds))
    assert dict(counts)=={r['part_id']:r['count'] for r in source['physical_inventory']}
    print('Reopened1115 valid leaves:56 new,38 changed,1021 unchanged.',flush=True)
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
    def gap(a,b,expected):
        value=byid[a]['shape'].distToShape(byid[b]['shape'])[0]
        interfaces.append(dict(a=a,b=b,gap_mm=value,expected_mm=expected,passed=abs(value-expected)<1e-5))
    for row in prior['interfaces']:gap(row['a'],row['b'],row['expected_mm'])
    for hand in ['Port','Starboard']:
        pre=hand+'SmallPlanetSupports_';caseid=hand+'TransmissionCore_plain_case'
        for n in range(3):
            ids={k:pre+k+str(n) for k in ['bronze','steel','pin','nut','cotter','plug','bolt','bolt_nut','bolt_cotter']}
            planet=hand+'SmallPlanetTrain_planet'+str(n);ringid=pre+'pin_ring'
            for a,b,e in [('bronze','steel',.1),('steel','pin',0),('nut','pin',c['nut_bore_gap']),
                ('cotter','pin',c['cotter_hole_gap']),('cotter','nut',c['cotter_slot_gap']/2),('plug','pin',0),
                ('bolt','bolt_nut',c['nut_bore_gap']),('bolt_cotter','bolt',c['cotter_hole_gap']),('bolt_cotter','bolt_nut',c['cotter_slot_gap']/2)]:gap(ids[a],ids[b],e)
            for key,e in [('pin',0),('steel',0),('bronze',c['ring_face_gap']),('bolt_nut',0),('bolt',c['pin_hole_gap'])]:gap(ids[key],ringid,e)
            for key in ['steel','nut','bolt']:gap(ids[key],caseid,0)
            gap(ids['bronze'],planet,0);gap(ids['steel'],planet,c['gear_steel_face_gap'])
    meshes=[];teeth=[]
    for row in prior['mesh_checks']:
        name=row['id'];pre=name.split('planet')[0]
        values={k:byid[name]['shape'].distToShape(byid[pre+k]['shape'])[0] for k in ['sun','ring']}
        meshes.append(dict(id=name,tooth_gaps_mm=values,passed=all(.001<v<.5 for v in values.values())))
    for row in prior['tooth_count_checks']:
        name=row['id'];key='planet' if '_planet' in name else 'sun' if name.endswith('_sun') else 'ring'
        tip=prior['dimensions']['tooth_profiles'][key]['root_radius_mm' if key=='ring' else 'tip_radius_mm']
        count=sum(isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-tip)<1e-6 for f in byid[name]['shape'].Faces)
        teeth.append(dict(row,native_tip_patches=count,passed=count==row['expected_teeth']))
    # Protect the existing inner hub and the rim outside the support envelope.
    protected=cylinder(90,200,510).fuse(cylinder(350,200,510).cut(cylinder(185,199,511)))
    a=old_case.common(protected);b=case.common(protected)
    protected_difference=a.cut(b).Volume+b.cut(a).Volume;assert protected_difference<1e-5
    print('Material pairs',len(pairs),'overlaps',overlaps,flush=True)
    print('Failed interfaces',[r for r in interfaces if not r['passed']],flush=True)
    exchange=out/'TransmissionSmallSupportParts.step';exchange_ids=new_ids+changed
    Part.makeCompound([byid[n]['shape'] for n in exchange_ids]).exportStep(str(exchange))
    imported=Part.Shape();imported.read(str(exchange));assert imported.isValid() and len(imported.Solids)==len(exchange_ids)
    unmatched=list(imported.Solids);exchange_checks=[]
    for name in exchange_ids:
        a=byid[name]['shape'].Solids[0];n=min(range(len(unmatched)),key=lambda n:(a.CenterOfMass-unmatched[n].CenterOfMass).Length);b=unmatched.pop(n)
        raw_missing=a.cut(b);raw_extra=b.cut(a);ta=a.getTolerance(1);tb=b.getTolerance(1)
        # OCC coincident-face cuts can fail at the saved native precision.
        # Bound the fuzzy comparison by both recorded tolerances and the
        # smallest nominal0.1mm interface divided by1000; never edit tolerances.
        fuzzy=min(.0001,max(1e-7,ta+tb))
        missing=a.cut(b,fuzzy);extra=b.cut(a,fuzzy)
        exchange_checks.append(dict(id=name,volume_difference_mm3=abs(a.Volume-b.Volume),center_difference_mm=(a.CenterOfMass-b.CenterOfMass).Length,
            raw_missing_faces=len(raw_missing.Faces),raw_added_faces=len(raw_extra.Faces),raw_missing_mm3=raw_missing.Volume,raw_added_mm3=raw_extra.Volume,
            comparison_fuzzy_tolerance_mm=fuzzy,missing_faces=len(missing.Faces),added_faces=len(extra.Faces),missing_mm3=missing.Volume,added_mm3=extra.Volume,
            native_max_tolerance_mm=ta,step_max_tolerance_mm=tb,
            passed=a.isValid() and b.isValid() and not missing.Faces and not extra.Faces and abs(missing.Volume)<1e-5 and abs(extra.Volume)<1e-5
                and ta<=.0001 and tb<=max(1e-7,ta)*(1+1e-6)))
        write(out/'exchange_progress.json',dict(completed=len(exchange_checks),total=len(exchange_ids),last_id=name,failed=[r for r in exchange_checks if not r['passed']]))
    passed=not overlaps and all(r['passed'] for r in interfaces+meshes+teeth+exchange_checks)
    report=dict(complete=True,passed=passed,native_occurrences=len(items),new_occurrences=56,new_definitions=9,reused_definitions=1,
        changed_prior_occurrences=38,unchanged_prior_occurrences=1021,new_source_counts=dict(counts),new_ids=new_ids,changed_ids=changed,
        keys_by_id=keys,stations_by_id=stations,material_candidate_pairs=len(pairs),overlaps=overlaps,interfaces=interfaces,mesh_checks=meshes,tooth_count_checks=teeth,
        dimensions=dimensions,disk_dimensions=disk_dimensions,gear_dimensions=prior['dimensions'],shaft_axis_world_mm=prior['shaft_axis_world_mm'],
        protected_case_material_difference_mm3=protected_difference,reused_plug_material_difference_mm3=plug_difference,
        input_hashes=hashes,authored_fingerprint=lock,tank_native_hashes=build['native_hashes'],native_sha256=sha(native),exchange_sha256=sha(exchange),
        exchange_roundtrip_solids=len(imported.Solids),exchange_roundtrip_checks=exchange_checks,standard_assembly_modified=False,
        complete_transmission=False,historical_fit_qualified=False,full_parameter_envelope_qualified=False,rendering_complete=False)
    write(out/'report.json',report)
    print('Failed STEP',[r for r in exchange_checks if not r['passed']],flush=True)
    COLORS.update(SmallSupport=(.55,.62,.66),SmallBronze=(.70,.51,.24),SmallGear=(.61,.50,.34),SmallCase=(.42,.56,.49))
    selected=[]
    for i in items:
        name=i['id']
        if not name.startswith(('PortSmallPlanetSupports_','PortSmallPlanetTrain_')) and name!='PortTransmissionCore_plain_case':continue
        color='SmallBronze' if keys.get(name)=='bronze' else 'SmallSupport' if name in keys else 'SmallCase' if 'plain_case' in name else 'SmallGear'
        selected.append(dict(i,system=color))
    shaded([i for i in selected if i['id']!='PortTransmissionCore_plain_case' and i['id'] not in ['PortSmallPlanetTrain_disk','PortSmallPlanetTrain_ring']
        and 'SmallPlanetTrain_rivet' not in i['id']],out/'supported_small_planets.svg',(1,-1,.7),'Small planetary supports | port train with three bushed pins and separate ring fastening')
    section=[];origin=App.Vector(*report['shaft_axis_world_mm'])
    for i in selected:
        b=i['shape'].copy().cleaned().BoundBox
        if b.ZMin>=origin.z:continue
        s=i['shape'].common(box(b.XMin-1,b.XMax+1,b.YMin-1,b.YMax+1,b.ZMin-1,origin.z))
        if not s.Solids:continue
        section.append(dict(i,shape=s,target=SimpleNamespace(Shape=s),definition=i['definition']+'_cut_'+i['id']))
    shaded(section,out/'small_support_cutaway.svg',(1,-1,1.2),'Small train cutaway | separate bushes, pins, plugs, pin ring and opposed ring bolts')
    assert fingerprint()==lock and check_build(stage/'build')['native_hashes']==build['native_hashes']
    assert all(sha(ROOT/n)==h for n,h in hashes.items())
    report.update(rendering_complete=True,output_raster_hashes={p.name:sha(p) for p in out.glob('*.png')});write(out/'report.json',report)
    print('PASS' if passed else 'FAIL',flush=True);sys.exit(0 if passed else 1)
finally:runtime.close()
