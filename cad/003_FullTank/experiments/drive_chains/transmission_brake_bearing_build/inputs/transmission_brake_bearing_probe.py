"""Install two brake-bearing cap/bush joints and the corresponding M263 saddles."""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--output',type=Path,default=ROOT/'transmission_brake_bearing_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();stage=a.stage.resolve();out=a.output.resolve();sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import read,write,sha,fingerprint,REPO
if not a.worker:
    out.mkdir(parents=True,exist_ok=True)
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--output',str(out),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part,numpy as np
    from lib.cad_build import leaves,metadata,shape_signature
    from lib.worker import check_build,same_shape,placement_errors
    from transmission_brake_bearing_parts import brake_bearing_parts
    parent=ROOT/'transmission_input_installation_build';prior=read(parent/'report.json');q=read(parent/'qualification.json')
    native_parent=parent/'TransmissionInputInstallationCandidate.FCStd'
    assert q['passed'] and q['rendering_complete'] and q['visually_reviewed']
    assert sha(native_parent)==q['native_sha256']==prior['native_sha256']
    for name,digest in q['receipt_hashes'].items():assert sha(parent/name)==digest,name
    lock=fingerprint();build=check_build(stage/'build')
    names=['transmission_brake_bearing_probe.py','transmission_brake_bearing_parts.py','transmission_brake_bearing_controls.json','transmission_brake_bearing_sources.json',
        'transmission_core_parts.py','transmission_stud_parts.py','transmission_output_calibration.json',
        'transmission_input_installation_build/report.json','transmission_input_installation_build/qualification.json',
        'transmission_input_installation_build/TransmissionInputInstallationCandidate.FCStd']
    hashes={n:sha(ROOT/n) for n in names}
    for n in names:
        if '/' not in n:
            dest=out/'inputs'/n;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/n).read_bytes())
    source=read(ROOT/'transmission_brake_bearing_sources.json');rows={r['key']:r for r in source['physical_inventory']}
    for name,digest in source['source_hashes'].items():assert sha(REPO/name)==digest,name
    c=read(ROOT/'transmission_brake_bearing_controls.json')['controls']
    doc=App.openDocument(str(native_parent));doc.recompute();before=leaves(doc.Root);old={i['id']:i for i in before}
    signatures={i['id']:shape_signature(i['shape']) for i in before};placements={i['id']:i['shape'].Placement for i in before}
    shapes,d=brake_bearing_parts(c,*[old[n]['target'].Shape for n in ['CenterTransmissionCore_bevel_case','PortTransmissionCore_high_drum','PortTransmissionCore_plain_case','InputInstallation_mount_nut0']])
    changed=['CenterTransmissionCore_bevel_case','PortTransmissionCore_high_drum','StarboardTransmissionCore_high_drum']
    for key,name in [('case',changed[0]),('drum',changed[1])]:
        target=old[name]['target'];target.Tip.Shape=shapes[key]
        metadata(target,BrakeBearingRevision='M263 rear saddles and M269 common journal: explicit section-led architecture hypothesis.',ParameterUpdate='Regenerate with transmission_brake_bearing_probe.py and its controls.')
    definitions={k:old[n]['target'] for k,n in [('dowel','PortTransmissionBearing_InnerDowel'),('cotter','InputInstallation_mount_cotter0')]}
    for key in ['bush','cap','stud','nut']:
        row=rows[key];body=doc.addObject('PartDesign::Body','Def_BrakeBearing_'+key);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedPart').Shape=shapes[key]
        metadata(body,DefinitionId='transmission_brake_bearing_'+key,OriginalMark=row['mark'],SourceRecord=row['record_id'],SurveyIds=[row['part_id']],Representation='assembly',Coverage='partial',
            ReconstructionNotes=read(ROOT/'transmission_brake_bearing_controls.json')['interpretation'],ParameterUpdate='Regenerate with transmission_brake_bearing_probe.py and its controls.')
        definitions[key]=body
    metadata(definitions['stud'],USStdThreadLimitsMM=d['US_thread_limits_mm'],SAEThreadLimitsMM=d['SAE_thread_limits_mm'],LengthConflict=source['conflicts'][0])
    new_ids=[];expected={};keys={}
    for hand in ['Port','Starboard']:
        group=doc.addObject('App::Part',hand+'BrakeBearing');doc.TransmissionCore.addObject(group)
        group.Placement=App.Placement(App.Vector(),App.Rotation(App.Vector(1,0,0),180) if hand=='Starboard' else App.Rotation())
        cap_group=doc.addObject('App::Part',hand+'BrakeBearingCapAssembly');group.addObject(cap_group)
        metadata(cap_group,SurveyIds=[source['cap_assembly_identity']],SourceRecord='SNL:56:005',InventoryQuantityRole='assembly identity; cap and dowel counted as separate physical leaves')
        metadata(group,Scope='M265 bush, M266 cap with M300 dowel and two MX14 sets. Integral rear saddle belongs to M263; architecture and fit are inferred.')
        def link(parent,key,suffix='',base=None):
            name=hand+'BrakeBearing_'+key+suffix;obj=doc.addObject('App::Link',name);parent.addObject(obj);obj.setLink(definitions[key]);obj.LinkPlacement=App.Placement(App.Vector(*(base or [0,0,0])),App.Rotation())
            metadata(obj,OccurrenceId=name,Subsystem='Drivetrain',SourceRecord=rows[key]['record_id'])
            new_ids.append(name);keys[name]=key;expected[name]=doc.TransmissionCore.Placement.multiply(group.Placement).multiply(obj.LinkPlacement).multiply(definitions[key].Shape.Placement)
        link(group,'bush');link(cap_group,'cap');link(cap_group,'dowel',base=d['dowel_origin_mm'])
        for n,(y,z) in enumerate(d['stud_axes_yz_mm']):
            for key,x in [('stud',0),('nut',c['nut_seat']),('cotter',d['cotter_axis_mm'])]:link(group,key,str(n),[x,y,z])
    doc.Definitions.Visibility=False;doc.recompute();native=out/'TransmissionBrakeBearingCandidate.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items}
    assert len(items)==len(byid)==len(before)+18==1321
    for i in items:
        name=i['id'];s=i['shape'];assert s.isValid() and len(s.Solids)==1,name
        t,r=placement_errors(s.Placement,expected[name] if name in expected else placements[name]);assert t<1e-6 and r<1e-8,(name,t,r)
        if name not in new_ids+changed:assert same_shape(signatures[name],shape_signature(s)),name
    counts=Counter(pid for name in new_ids for pid in json.loads(byid[name]['target'].SurveyIds))
    assert dict(counts)=={r['part_id']:r['count'] for r in source['physical_inventory']}
    print('Reopened1321 valid leaves;18 new,3 revised,1300 unchanged.',flush=True)
    tank=App.openDocument(build['build']['top_document']);tank.recompute()
    excluded={'hull_engine_back','PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting','hull_port_inner_rear_end','hull_port_rear_wing','hull_starboard_inner_rear_end','hull_starboard_rear_wing'}
    context=[i for i in leaves(tank.Root) if i['id'] not in excluded and i['representation']=='assembly'];physical=items+context
    assert len({i['id'] for i in physical})==len(physical)
    boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].copy().cleaned().BoundBox for i in physical]])
    pairs=set();overlaps=[]
    for name in new_ids+changed:
        s=byid[name]['shape'];b=s.copy().cleaned().BoundBox;bb=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
        near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
        for index in near:
            other=physical[index];pair=tuple(sorted([name,other['id']]))
            if pair[0]==pair[1] or pair in pairs:continue
            pairs.add(pair);volume=s.common(other['shape']).Volume
            if volume>1e-5:overlaps.append(dict(a=name,b=other['id'],volume_mm3=volume))
        write(out/'material_progress.json',dict(last_id=name,pairs=len(pairs),overlaps=overlaps))
    interfaces=[];reused=0
    def gap(a,b,want):
        value=byid[a]['shape'].distToShape(byid[b]['shape'])[0];interfaces.append(dict(a=a,b=b,gap_mm=value,expected_mm=want,passed=abs(value-want)<1e-5))
    for row in prior['interfaces']:
        if row['a'] in changed or row['b'] in changed:gap(row['a'],row['b'],row['expected_mm'])
        else:interfaces.append(dict(row,evidence='unchanged geometry; retained from hash-bound parent report'));reused+=1
    for hand in ['Port','Starboard']:
        pre=hand+'BrakeBearing_';gap(pre+'bush',hand+'TransmissionCore_high_drum',c['running_gap']);gap(pre+'bush',hand+'TransmissionCore_plain_case',c['running_gap'])
        gap(pre+'bush',pre+'cap',0);gap(pre+'bush','CenterTransmissionCore_bevel_case',0)
        gap(pre+'cap','CenterTransmissionCore_bevel_case',2*c['split_gap']);gap(pre+'dowel',pre+'bush',c['dowel_hole_gap'])
        for n in range(2):
            gap(pre+'nut'+str(n),pre+'cap',0);gap(pre+'stud'+str(n),pre+'nut'+str(n),.1)
    write(out/'fit_checks.json',dict(overlaps=overlaps,interfaces=interfaces))
    print('Pairs',len(pairs),'overlaps',overlaps,flush=True);print('Failed interfaces',[r for r in interfaces if not r['passed']],flush=True)
    exchange=out/'TransmissionBrakeBearingParts.step';exchange_ids=new_ids+changed
    Part.makeCompound([byid[n]['shape'] for n in exchange_ids]).exportStep(str(exchange));imp=Part.Shape();imp.read(str(exchange))
    assert imp.isValid() and len(imp.Solids)==len(exchange_ids)
    unmatched=list(imp.Solids);checks=[]
    for name in exchange_ids:
        s=byid[name]['shape'].Solids[0];n=min(range(len(unmatched)),key=lambda n:(s.CenterOfMass-unmatched[n].CenterOfMass).Length);v=unmatched.pop(n)
        ta=s.getTolerance(1);tb=v.getTolerance(1);fuzzy=min(.0001,max(1e-7,ta+tb))
        rm=s.cut(v).Volume;ra=v.cut(s).Volume;missing=s.cut(v,fuzzy);added=v.cut(s,fuzzy)
        checks.append(dict(id=name,native_max_tolerance_mm=ta,step_max_tolerance_mm=tb,comparison_fuzzy_tolerance_mm=fuzzy,tolerance_reporting_roundoff_mm=1e-10,
            raw_missing_mm3=rm,raw_added_mm3=ra,missing_mm3=missing.Volume,added_mm3=added.Volume,
            passed=s.isValid() and v.isValid() and rm<1e-5 and ra<1e-5 and not missing.Faces and not added.Faces and ta<=1e-4 and tb<=max(1e-7,ta)+1e-10))
        write(out/'exchange_progress.json',dict(completed=len(checks),total=len(exchange_ids),failed=[r for r in checks if not r['passed']]))
    assert fingerprint()==lock and check_build(stage/'build')['native_hashes']==build['native_hashes']
    for n,h in hashes.items():assert sha(ROOT/n)==h,n
    passed=not overlaps and all(r['passed'] for r in interfaces+checks)
    report=dict(passed=passed,complete=True,native_occurrences=len(items),new_occurrences=len(new_ids),new_definitions=4,reused_definitions=2,changed_prior_occurrences=3,unchanged_prior_occurrences=len(before)-3,
        new_ids=new_ids,changed_ids=changed,keys_by_id=keys,new_source_counts=dict(counts),material_candidate_pairs=len(pairs),overlaps=overlaps,interfaces=interfaces,
        reused_prior_interfaces=reused,rechecked_interfaces=len(interfaces)-reused,dimensions=d,shaft_axis_world_mm=prior['shaft_axis_world_mm'],input_hashes=hashes,
        authored_fingerprint=lock,tank_native_hashes=build['native_hashes'],native_sha256=sha(native),exchange_sha256=sha(exchange),exchange_roundtrip_checks=checks,
        standard_assembly_modified=False,complete_transmission=False,historical_fit_qualified=False,rendering_complete=False,limitations=source['conflicts']+source['limits'])
    write(out/'report.json',report);print('PASS' if passed else 'FAIL',flush=True);sys.exit(0 if passed else 1)
finally:runtime.close()
