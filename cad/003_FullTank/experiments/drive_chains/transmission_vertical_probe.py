"""Populate the vertical reversing shaft, keyed levers and bearing attachments."""
import argparse,json,subprocess,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--output',type=Path,default=ROOT/'transmission_vertical_build');p.add_argument('--worker',action='store_true')
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
    from transmission_vertical_parts import vertical_parts
    from case_joint_mass import calculator
    parent=ROOT/'transmission_reversing_build';prior=read(parent/'report.json');q=read(parent/'qualification.json')
    native_parent=parent/'TransmissionReversingCandidate.FCStd'
    assert q['passed'] and q['rendering_complete'] and q['visually_reviewed']
    assert sha(native_parent)==q['native_sha256']==prior['native_sha256']
    for name,digest in q['receipt_hashes'].items():assert sha(parent/name)==digest,name
    lock=fingerprint();build=check_build(stage/'build')
    names=['transmission_vertical_probe.py','transmission_vertical_parts.py','transmission_vertical_controls.json','transmission_vertical_sources.json',
        'transmission_stud_parts.py','transmission_core_parts.py','transmission_input_installation_parts.py','transmission_input_parts.py',
        'transmission_input_calibration.json','case_joint_mass.py','case_joint_mass.cpp',
        'transmission_reversing_build/report.json','transmission_reversing_build/qualification.json','transmission_reversing_build/TransmissionReversingCandidate.FCStd']
    hashes={n:sha(ROOT/n) for n in names}
    for n in names:
        if '/' not in n:
            dest=out/'inputs'/n;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/n).read_bytes())
    source=read(ROOT/'transmission_vertical_sources.json');rows={r['key']:r for r in source['physical_inventory']}
    for name,digest in source['source_hashes'].items():assert sha(REPO/name)==digest,name
    c=read(ROOT/'transmission_vertical_controls.json')['controls']
    doc=App.openDocument(str(native_parent));doc.recompute();before=leaves(doc.Root);old={i['id']:i for i in before}
    signatures={i['id']:shape_signature(i['shape']) for i in before};placements={i['id']:i['shape'].Placement for i in before}
    shapes,d=vertical_parts(c,*[old[n]['target'].Shape for n in ['CenterTransmissionCore_bevel_case','ReversingControl_rod']])
    changed=['CenterTransmissionCore_bevel_case','ReversingControl_rod']
    for key,name in [('case',changed[0]),('rod',changed[1])]:
        target=old[name]['target'];target.Tip.Shape=shapes[key]
        metadata(target,VerticalControlRevision='Local bearing lands/receivers and revised linkage-end cross-socket.',ParameterUpdate='Regenerate with transmission_vertical_probe.py and its controls.')
    definitions={'nut':old['PortBrakeBearing_nut0']['target'],'cotter':old['InputInstallation_mount_cotter0']['target']}
    for key in rows:
        if key in definitions:continue
        row=rows[key];body=doc.addObject('PartDesign::Body','Def_Vertical_'+key);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedPart').Shape=shapes[key]
        metadata(body,DefinitionId='transmission_vertical_'+key,OriginalMark=row['mark'],SourceRecord=row['record_id'],SurveyIds=[row['part_id']],Representation='assembly',Coverage='partial',
            ReconstructionNotes=read(ROOT/'transmission_vertical_controls.json')['interpretation'],ParameterUpdate='Regenerate with transmission_vertical_probe.py and its controls.')
        definitions[key]=body
    metadata(definitions['stud'],SourceDiameterMM=12.7,SourceLengthMM=c['stud_length'],SourceUSThreadLengthMM=c['stud_US_thread_length'],SourceSAEThreadLengthMM=c['stud_SAE_thread_length'])
    metadata(definitions['key'],SourceSize='Woodruff No.C',SizeMappingVerified=False)
    group=doc.addObject('App::Part','VerticalReversingControl');doc.ReversingControl.addObject(group)
    metadata(doc.ReversingControl,Scope='Fork/rod/detent and vertical shaft assembly with two bearing attachments; long reverse linkage pending.')
    shaftgroup=doc.addObject('App::Part','VerticalShaftAssembly');group.addObject(shaftgroup)
    metadata(shaftgroup,SurveyIds=[source['assembly_identities']['shaft']],ReferencedSurveyIds=[source['scope_interpretation']['survey_id']],SourceRecord='SNL:215:029',InventoryQuantityRole='assembly identity; shaft/levers/keys counted only as leaves',ScopeInterpretation=source['scope_interpretation'])
    new_ids=[];expected={};keys={}
    def put(name,key,parent,placement=None,record=None):
        obj=doc.addObject('App::Link',name);parent.addObject(obj);obj.setLink(definitions[key])
        if placement is not None:obj.LinkPlacement=placement
        metadata(obj,OccurrenceId=name,Subsystem='Drivetrain',SourceRecord=record or rows[key]['record_id'])
        new_ids.append(name);keys[name]=key;expected[name]=doc.TransmissionCore.Placement.multiply(obj.LinkPlacement).multiply(definitions[key].Shape.Placement)
    for key in ['shaft','upper_lever','lower_lever']:put('VerticalControl_'+key,key,shaftgroup)
    x,y=c['shaft_xy']
    for n,loc in enumerate(d['key_locations']):
        put('VerticalControl_key'+str(n),'key',shaftgroup,App.Placement(App.Vector(x,y,loc['z']),App.Rotation(App.Vector(0,0,1),loc['angle'])))
    for label,z,angle in [('Upper',c['upper_bearing_base_z'],0),('Lower',c['lower_bearing_open_z'],180)]:
        bearinggroup=doc.addObject('App::Part',label+'VerticalBearing');group.addObject(bearinggroup)
        put(label+'Vertical_bearing','bearing',bearinggroup,App.Placement(App.Vector(x,y,z),App.Rotation(App.Vector(1,0,0),angle)))
        for row in [r for r in d['mounts'] if r['label']==label]:
            kind=row['kind'];joint=doc.addObject('App::Part',label+'Vertical_'+kind+'Assembly');bearinggroup.addObject(joint)
            metadata(joint,SurveyIds=[source['assembly_identities'][kind]],InventoryQuantityRole='assembly identity; fastener/nut/pin counted only as leaves',SourceRecord='SNL:28:006' if kind=='bolt' else 'SNL:241:001')
            put(label+'Vertical_'+kind,kind,joint,App.Placement(App.Vector(row['fastener_base_x'],row['y'],row['z']),App.Rotation()))
            for key,xx in [('nut',c['nut_seat_x']),('cotter',d['cotter_axis_x_mm'])]:
                record=rows[key]['record_id'] if kind=='bolt' else {'nut':'SNL:241:004','cotter':'SNL:241:005'}[key]
                put(label+'Vertical_'+kind+'_'+key,key,joint,App.Placement(App.Vector(xx,row['y'],row['z']),App.Rotation(App.Vector(0,0,1),180)),record)
    doc.Definitions.Visibility=False;doc.recompute();native=out/'TransmissionVerticalCandidate.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items}
    assert len(items)==len(byid)==len(before)+19==1391
    for i in items:
        name=i['id'];s=i['shape'];assert s.isValid() and len(s.Solids)==1,name
        t,r=placement_errors(s.Placement,expected[name] if name in expected else placements[name]);assert t<1e-6 and r<1e-8,(name,t,r)
        if name not in new_ids+changed:assert same_shape(signatures[name],shape_signature(s)),name
    counts=Counter(pid for name in new_ids for pid in json.loads(byid[name]['target'].SurveyIds))
    assert dict(counts)=={r['part_id']:r['count'] for r in source['physical_inventory']}
    print('Reopened1391 valid leaves;19 new,2 revised,1370 unchanged.',flush=True)
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
    for label,lever in [('Upper','upper_lever'),('Lower','lower_lever')]:
        bearing=label+'Vertical_bearing'
        gap(bearing,'VerticalControl_shaft',c['journal_gap'])
        gap(bearing,'VerticalControl_'+lever,c['axial_gap'])
        gap(bearing,changed[0],0)
        gap('VerticalControl_shaft','VerticalControl_'+lever,0)
        for kind in ['bolt','stud']:
            fastener=label+'Vertical_'+kind
            gap(bearing,fastener,c['fastener_gap'])
            gap(bearing,fastener+'_nut',0)
            gap(fastener,fastener+'_nut',.1)
            gap(fastener,fastener+'_cotter',c['cotter_gap'])
            gap(fastener,changed[0],0 if kind=='bolt' else c['fastener_gap'])
    for n,lever in enumerate(['upper_lever','lower_lever']):
        gap('VerticalControl_key'+str(n),'VerticalControl_shaft',c['key_gap'])
        gap('VerticalControl_key'+str(n),'VerticalControl_'+lever,c['key_gap'])
    gap('VerticalControl_upper_lever','ReversingControl_rod',c['rod_hole_radius']-c['finger_radius'])
    write(out/'fit_checks.json',dict(overlaps=overlaps,interfaces=interfaces))
    print('Pairs',len(pairs),'overlaps',overlaps,flush=True);print('Failed interfaces',[r for r in interfaces if not r['passed']],flush=True)
    exchange=out/'TransmissionVerticalParts.step';exchange_ids=new_ids+changed
    Part.makeCompound([byid[n]['shape'] for n in exchange_ids]).exportStep(str(exchange));imp=Part.Shape();imp.read(str(exchange))
    assert imp.isValid() and len(imp.Solids)==len(exchange_ids)
    unmatched=list(imp.Solids);checks=[];mass=calculator(out/'runtime/mass_checks')
    for name in exchange_ids:
        s=byid[name]['shape'].Solids[0];n=min(range(len(unmatched)),key=lambda n:(s.CenterOfMass-unmatched[n].CenterOfMass).Length);v=unmatched.pop(n)
        ta=s.getTolerance(1);tb=v.getTolerance(1);fuzzy=min(.0001,max(1e-7,ta+tb))
        rm=s.cut(v).Volume;ra=v.cut(s).Volume;missing=s.cut(v,fuzzy);added=v.cut(s,fuzzy)
        mn=mass(s,name+'_native');ms=mass(v,name+'_step')
        dv=abs(mn['volume_mm3']-ms['volume_mm3']);dc=(App.Vector(*mn['center_mm'])-App.Vector(*ms['center_mm'])).Length
        volume_bound=(s.Area+v.Area)/2*(ta+tb)
        mass_ok=dv<=volume_bound and dc<max(1e-6,ta+tb) and all(0<=m['estimated_relative_error']<1e-9 for m in [mn,ms])
        checks.append(dict(id=name,native_max_tolerance_mm=ta,step_max_tolerance_mm=tb,comparison_fuzzy_tolerance_mm=fuzzy,
            raw_missing_mm3=rm,raw_added_mm3=ra,missing_mm3=missing.Volume,added_mm3=added.Volume,
            adaptive_native=mn,adaptive_step=ms,adaptive_volume_difference_mm3=dv,surface_tolerance_volume_envelope_mm3=volume_bound,adaptive_center_difference_mm=dc,
            passed=s.isValid() and v.isValid() and mass_ok and rm<1e-5 and ra<1e-5 and not missing.Faces and not added.Faces and ta<=1e-4 and tb<=max(1e-7,ta)+1e-10))
        write(out/'exchange_progress.json',dict(completed=len(checks),total=len(exchange_ids),failed=[r for r in checks if not r['passed']]))
    assert fingerprint()==lock and check_build(stage/'build')['native_hashes']==build['native_hashes']
    for n,h in hashes.items():assert sha(ROOT/n)==h,n
    passed=not overlaps and all(r['passed'] for r in interfaces+checks)
    write(out/'report.json',dict(passed=passed,complete=True,native_occurrences=len(items),new_occurrences=19,new_definitions=7,reused_definitions=2,changed_prior_occurrences=2,unchanged_prior_occurrences=len(before)-2,
        new_ids=new_ids,changed_ids=changed,keys_by_id=keys,new_source_counts=dict(counts),material_candidate_pairs=len(pairs),overlaps=overlaps,interfaces=interfaces,
        reused_prior_interfaces=reused,rechecked_interfaces=len(interfaces)-reused,dimensions=d,shaft_axis_world_mm=prior['shaft_axis_world_mm'],input_hashes=hashes,
        authored_fingerprint=lock,tank_native_hashes=build['native_hashes'],native_sha256=sha(native),exchange_sha256=sha(exchange),exchange_roundtrip_checks=checks,
        standard_assembly_modified=False,complete_transmission=False,historical_fit_qualified=False,rendering_complete=False,limitations=source['limits']))
    print('PASS' if passed else 'FAIL',flush=True);sys.exit(0 if passed else 1)
finally:runtime.close()
