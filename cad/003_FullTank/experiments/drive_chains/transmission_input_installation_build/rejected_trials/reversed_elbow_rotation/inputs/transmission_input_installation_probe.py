"""Extend the accepted input assembly with MX25 retention and grease fittings."""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--stage',type=Path,required=True)
p.add_argument('--output',type=Path,default=ROOT/'transmission_input_installation_build')
p.add_argument('--worker',action='store_true')
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
    import Part,numpy as np
    from lib.cad_build import leaves,metadata,shape_signature
    from lib.worker import check_build,same_shape,placement_errors
    from transmission_input_installation_parts import mounting,grease_feed
    parent=ROOT/'transmission_input_build';prior=read(parent/'report.json')
    native_parent=parent/'TransmissionInputCandidate.FCStd'
    assert prior['passed'] and prior['rendering_complete'] and sha(native_parent)==prior['native_sha256']
    assert read(parent/'interface_checks.json')['passed'] and read(parent/'visual_review.json')['passed']
    lock=fingerprint();build=check_build(stage/'build')
    names=['transmission_input_installation_probe.py','transmission_input_installation_parts.py',
        'transmission_input_installation_controls.json','transmission_input_installation_sources.json',
        'transmission_input_parts.py','transmission_stud_parts.py','transmission_core_parts.py',
        'transmission_input_build/report.json','transmission_input_build/interface_checks.json',
        'transmission_input_build/visual_review.json','transmission_input_build/TransmissionInputCandidate.FCStd']
    hashes={n:sha(ROOT/n) for n in names}
    for n in names:
        if '/' not in n:
            dest=out/'inputs'/n;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/n).read_bytes())
    source=read(ROOT/'transmission_input_installation_sources.json');rows={r['key']:r for r in source['physical_inventory']}
    assert all(sha(REPO/n)==h for n,h in source['source_hashes'].items())
    c=read(ROOT/'transmission_input_installation_controls.json')
    doc=App.openDocument(str(native_parent));doc.recompute();before=leaves(doc.Root);old={i['id']:i for i in before}
    signatures={i['id']:shape_signature(i['shape']) for i in before}
    placements={i['id']:i['shape'].Placement for i in before}
    original_ids=dict(cover='CenterTransmissionCore_bevel_cover',housing='InputHousing_housing',
        spacer='InputHousing_spacer',flange_shim='InputHousing_flange_shim00')
    originals={k:old[n]['target'].Shape.copy() for k,n in original_ids.items()}
    parts,md=mounting(c['mount'],originals)
    grease,gd,_=grease_feed(c['grease'],parts['housing'],originals['spacer']);parts.update(grease)
    changed=[original_ids[k] for k in ['cover','housing','spacer']]+['InputHousing_flange_shim'+str(n).zfill(2) for n in range(16)]
    for key,name in original_ids.items():
        old[name]['target'].Tip.Shape=parts[key]
        metadata(old[name]['target'],InstallationRevision='Four MX25 receivers and continuous grease feed; source quantity/nut conflicts retained.',
            ParameterUpdate='Regenerate with transmission_input_installation_probe.py and its controls.')
    group=doc.InputHousingAssembly
    metadata(group,Scope='Input bearings/housing/coupling and cover stud joint with partial grease feed. Pump, support bracket and complete installation remain pending.')
    mount=doc.addObject('App::Part','InputCoverFasteners');group.addObject(mount)
    lube=doc.addObject('App::Part','InputGreaseFeed');group.addObject(lube)
    cup=doc.addObject('App::Part','InputGreaseCup');lube.addObject(cup)
    metadata(mount,QuantityInterpretation=source['conflicts'][:2],PatternBasis='Four cardinal axes inferred on existing R96 circle.')
    metadata(lube,PlacementBasis=c['decisions'][2],PassageBasis=c['decisions'][3])
    row=rows['cup'];metadata(cup,SurveyIds=[row['part_id']],CatalogueQuantity=1,SourceRecord=row['record_id'],
        InventoryQuantityRole='one commercial grease cup; two inferred component solids',Coverage='partial')
    definitions={}
    for key in ['mount_stud','mount_nut','mount_cotter','nipple','elbow','cup_body','cup_cap']:
        internal=key.startswith('cup_');row=rows['cup' if internal else key]
        body=doc.addObject('PartDesign::Body','Def_InputInstallation_'+key);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedPart').Shape=parts[key]
        metadata(body,DefinitionId='input_installation_'+key,OriginalMark=row['mark'],SourceRecord=row['record_id'],
            SurveyIds=[] if internal or row['part_id'] is None else [row['part_id']],Representation='assembly',Coverage='partial',
            ReconstructionNotes='Source nominal dimensions with inferred receivers, shape and placement. Plain thread envelopes; no load/seal qualification.',
            ParameterUpdate='Regenerate with transmission_input_installation_probe.py and its controls.')
        if internal:metadata(body,ParentSurveyId=row['part_id'],InventoryQuantityRole='inferred commercial cup decomposition')
        if key=='mount_nut':metadata(body,ConflictingSurveyIds=[row['conflicting_part_id']],SizeInterpretation=source['conflicts'][1],NominalDiameterMM=12.7)
        if key=='mount_stud':metadata(body,USStdThreadLimitsMM=md['US_thread_limits_mm'],SAEThreadLimitsMM=md['SAE_thread_limits_mm'])
        definitions[key]=body
    new_ids=[];expected={};keys={}
    def link(parent,name,key,placement=None):
        obj=doc.addObject('App::Link',name);parent.addObject(obj);obj.setLink(definitions[key]);obj.LinkPlacement=placement or App.Placement()
        metadata(obj,OccurrenceId=name,Subsystem='Drivetrain',SourceRecord=definitions[key].SourceRecord)
        expected[name]=doc.TransmissionCore.Placement.multiply(obj.LinkPlacement).multiply(definitions[key].Shape.Placement)
        new_ids.append(name);keys[name]=key
    for n,(y,z) in enumerate(md['axes_yz_mm']):
        for key,x in [('mount_stud',0),('mount_nut',c['mount']['nut_seat']),('mount_cotter',md['cotter_station_mm'])]:
            link(mount,'InputInstallation_'+key+str(n),key,App.Placement(App.Vector(x,y,z),App.Rotation()))
    for key in ['nipple','elbow','cup_body','cup_cap']:
        link(cup if key.startswith('cup_') else lube,'InputInstallation_'+key,key)
    doc.Definitions.Visibility=False;doc.recompute();native=out/'TransmissionInputInstallationCandidate.FCStd'
    doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items}
    assert len(items)==len(byid)==len(before)+len(new_ids)==1303
    for i in items:
        n=i['id'];assert i['shape'].isValid() and len(i['shape'].Solids)==1,n
        if n not in new_ids:
            t,r=placement_errors(i['shape'].Placement,placements[n]);assert t<1e-6 and r<1e-8,(n,t,r)
            if n not in changed:assert same_shape(signatures[n],shape_signature(i['shape'])),n
        else:
            t,r=placement_errors(i['shape'].Placement,expected[n]);assert t<1e-6 and r<1e-8,(n,t,r)
    counts=Counter(pid for n in new_ids for pid in json.loads(byid[n]['target'].SurveyIds));counts.update(json.loads(doc.InputGreaseCup.SurveyIds))
    assert dict(counts)=={r['part_id']:r['count'] for r in source['physical_inventory'] if r['part_id']}
    print('Reopened',len(items),'valid leaves;',len(new_ids),'new and',len(changed),'revised. Corrected nut identity remains unreconciled.',flush=True)
    tank=App.openDocument(build['build']['top_document']);tank.recompute()
    excluded={'hull_engine_back','PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting','hull_port_inner_rear_end',
        'hull_port_rear_wing','hull_starboard_inner_rear_end','hull_starboard_rear_wing'}
    context=[i for i in leaves(tank.Root) if i['id'] not in excluded and i['representation']=='assembly'];physical=items+context
    assert len({i['id'] for i in physical})==len(physical)
    boxes=np.array([[v.XMin,v.YMin,v.ZMin,v.XMax,v.YMax,v.ZMax] for v in [i['shape'].copy().cleaned().BoundBox for i in physical]])
    pairs=set();overlaps=[]
    for name in new_ids+changed:
        a=byid[name]['shape'];v=a.copy().cleaned().BoundBox;bb=np.array([v.XMin,v.YMin,v.ZMin,v.XMax,v.YMax,v.ZMax])
        near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
        for index in near:
            other=physical[index];pair=tuple(sorted([name,other['id']]))
            if pair[0]==pair[1] or pair in pairs:continue
            pairs.add(pair);vol=a.common(other['shape']).Volume
            if vol>1e-5:overlaps.append(dict(a=name,b=other['id'],volume_mm3=vol))
        write(out/'material_progress.json',dict(last_id=name,pairs=len(pairs),overlaps=overlaps))
    interfaces=[]
    def gap(a,b,want,tol=1e-5):
        v=byid[a]['shape'].distToShape(byid[b]['shape'])[0]
        interfaces.append(dict(a=a,b=b,gap_mm=v,expected_mm=want,passed=abs(v-want)<tol))
    for row in prior['interfaces']:gap(row['a'],row['b'],row['expected_mm'])
    for n in range(4):
        gap('InputInstallation_mount_nut'+str(n),'InputHousing_housing',0)
        gap('InputInstallation_mount_stud'+str(n),'CenterTransmissionCore_bevel_cover',c['mount']['receiver_gap'])
        gap('InputInstallation_mount_stud'+str(n),'InputInstallation_mount_nut'+str(n),c['mount']['nut_bore_gap'])
    for a,b in [('nipple','elbow'),('elbow','cup_body')]:gap('InputInstallation_'+a,'InputInstallation_'+b,0)
    gap('InputInstallation_nipple','InputHousing_housing',0)
    gap('InputInstallation_cup_body','InputInstallation_cup_cap',c['grease']['socket_gap'])
    print('Affected material pairs',len(pairs),'overlaps',overlaps,flush=True)
    print('Failed interfaces',[r for r in interfaces if not r['passed']],flush=True)
    write(out/'fit_checks.json',dict(overlaps=overlaps,interfaces=interfaces))
    exchange=out/'TransmissionInputInstallationParts.step';exchange_ids=new_ids+changed
    Part.makeCompound([byid[n]['shape'] for n in exchange_ids]).exportStep(str(exchange))
    imp=Part.Shape();imp.read(str(exchange));assert imp.isValid() and len(imp.Solids)==len(exchange_ids)
    unmatched=list(imp.Solids);checks=[]
    for name in exchange_ids:
        a=byid[name]['shape'].Solids[0];n=min(range(len(unmatched)),key=lambda n:(a.CenterOfMass-unmatched[n].CenterOfMass).Length);v=unmatched.pop(n)
        ta=a.getTolerance(1);tb=v.getTolerance(1);fuzzy=min(.0001,max(1e-7,ta+tb))
        raw_missing=a.cut(v).Volume;raw_added=v.cut(a).Volume;missing=a.cut(v,fuzzy);extra=v.cut(a,fuzzy)
        checks.append(dict(id=name,native_max_tolerance_mm=ta,step_max_tolerance_mm=tb,comparison_fuzzy_tolerance_mm=fuzzy,
            raw_missing_mm3=raw_missing,raw_added_mm3=raw_added,missing_mm3=missing.Volume,added_mm3=extra.Volume,
            passed=a.isValid() and v.isValid() and not missing.Faces and not extra.Faces and raw_missing<1e-5 and raw_added<1e-5 and ta<=.0001 and tb<=max(1e-7,ta)*(1+1e-6)))
        write(out/'exchange_progress.json',dict(completed=len(checks),total=len(exchange_ids),failed=[r for r in checks if not r['passed']]))
    assert fingerprint()==lock and check_build(stage/'build')['native_hashes']==build['native_hashes']
    assert all(sha(ROOT/n)==h for n,h in hashes.items())
    passed=not overlaps and all(r['passed'] for r in interfaces+checks)
    report=dict(complete=True,passed=passed,native_occurrences=len(items),new_occurrences=len(new_ids),new_definitions=len(definitions),
        changed_prior_occurrences=len(changed),unchanged_prior_occurrences=len(before)-len(changed),new_ids=new_ids,changed_ids=changed,keys_by_id=keys,
        new_source_counts=dict(counts),unreconciled_inferred_nuts=4,material_candidate_pairs=len(pairs),overlaps=overlaps,interfaces=interfaces,
        dimensions=dict(mount=md,grease=gd),shaft_axis_world_mm=prior['shaft_axis_world_mm'],input_hashes=hashes,
        authored_fingerprint=lock,tank_native_hashes=build['native_hashes'],native_sha256=sha(native),exchange_sha256=sha(exchange),exchange_roundtrip_checks=checks,
        standard_assembly_modified=False,complete_transmission=False,historical_fit_qualified=False,rendering_complete=False,
        limitations=source['conflicts']+c['decisions']+['Pump, B6205 support bracket and complete input installation remain pending.'])
    write(out/'report.json',report);print('PASS' if passed else 'FAIL',flush=True);sys.exit(0 if passed else 1)
finally:runtime.close()
