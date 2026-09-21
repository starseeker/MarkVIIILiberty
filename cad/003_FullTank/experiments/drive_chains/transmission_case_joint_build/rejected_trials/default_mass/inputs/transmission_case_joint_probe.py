"""Install fourteen MX8 joints and two M326 seals on the central case split."""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--output',type=Path,default=ROOT/'transmission_case_joint_build');p.add_argument('--worker',action='store_true')
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
    from transmission_case_joint_parts import case_joint_parts
    parent=ROOT/'transmission_brake_bearing_build';prior=read(parent/'report.json');q=read(parent/'qualification.json')
    native_parent=parent/'TransmissionBrakeBearingCandidate.FCStd'
    assert q['passed'] and q['rendering_complete'] and q['visually_reviewed']
    assert sha(native_parent)==q['native_sha256']==prior['native_sha256']
    for name,digest in q['receipt_hashes'].items():assert sha(parent/name)==digest,name
    lock=fingerprint();build=check_build(stage/'build')
    names=['transmission_case_joint_probe.py','transmission_case_joint_parts.py','transmission_case_joint_controls.json','transmission_case_joint_sources.json',
        'transmission_stud_parts.py','transmission_input_calibration.json',
        'transmission_brake_bearing_build/report.json','transmission_brake_bearing_build/qualification.json',
        'transmission_brake_bearing_build/TransmissionBrakeBearingCandidate.FCStd']
    hashes={n:sha(ROOT/n) for n in names}
    for n in names:
        if '/' not in n:
            dest=out/'inputs'/n;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/n).read_bytes())
    source=read(ROOT/'transmission_case_joint_sources.json');rows={r['key']:r for r in source['physical_inventory']}
    for name,digest in source['source_hashes'].items():assert sha(REPO/name)==digest,name
    c=read(ROOT/'transmission_case_joint_controls.json')['controls']
    doc=App.openDocument(str(native_parent));doc.recompute();before=leaves(doc.Root);old={i['id']:i for i in before}
    signatures={i['id']:shape_signature(i['shape']) for i in before};placements={i['id']:i['shape'].Placement for i in before}
    shapes,d=case_joint_parts(c,*[old['CenterTransmissionCore_'+k]['target'].Shape for k in ['bevel_case','bevel_cover']])
    changed=['CenterTransmissionCore_bevel_case','CenterTransmissionCore_bevel_cover']
    for key,name in zip(['case','cover'],changed):
        target=old[name]['target'];target.Tip.Shape=shapes[key]
        metadata(target,CaseJointRevision='Fourteen MX8 joint lands and receivers; source count with inferred pattern.',ParameterUpdate='Regenerate with transmission_case_joint_probe.py and its controls.')
    lower=shapes['gasket_upper'].copy();lower.rotate(App.Vector(),App.Vector(1,0,0),180)
    assert lower.cut(shapes['gasket_lower']).Volume<1e-5 and shapes['gasket_lower'].cut(lower).Volume<1e-5
    assert abs(lower.Volume-shapes['gasket_lower'].Volume)<1e-5
    definitions={k:old[n]['target'] for k,n in [('nut','PortBrakeBearing_nut0'),('cotter','InputInstallation_mount_cotter0')]}
    for key in ['bolt','gasket']:
        row=rows[key];body=doc.addObject('PartDesign::Body','Def_CaseJoint_'+key);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedPart').Shape=shapes['gasket_upper' if key=='gasket' else key]
        metadata(body,DefinitionId='transmission_case_joint_'+key,OriginalMark=row['mark'],SourceRecord=row['record_id'],SurveyIds=[row['part_id']],Representation='assembly',Coverage='partial',
            ReconstructionNotes=read(ROOT/'transmission_case_joint_controls.json')['interpretation'],ParameterUpdate='Regenerate with transmission_case_joint_probe.py and its controls.')
        definitions[key]=body
    metadata(definitions['bolt'],ThreadLimitsMM=d['thread_limits_x_mm'],NominalShankDiameterMM=c['bolt_diameter'],ThreadGeometry='nominal envelope, no helix')
    group=doc.addObject('App::Part','CentralCaseJoint');doc.TransmissionCore.addObject(group)
    metadata(group,Scope='Two M326 seals and fourteen MX8 assemblies. Placement and casting lands inferred.')
    new_ids=[];expected={};keys={}
    def link(parent,key,suffix,base=None,rotation=None):
        name='CentralCaseJoint_'+key+suffix;obj=doc.addObject('App::Link',name);parent.addObject(obj);obj.setLink(definitions[key])
        obj.LinkPlacement=App.Placement(App.Vector(*(base or [0,0,0])),rotation or App.Rotation())
        metadata(obj,OccurrenceId=name,Subsystem='Drivetrain',SourceRecord=rows[key]['record_id'])
        new_ids.append(name);keys[name]=key;expected[name]=doc.TransmissionCore.Placement.multiply(obj.LinkPlacement).multiply(definitions[key].Shape.Placement)
    link(group,'gasket','Upper');link(group,'gasket','Lower',rotation=App.Rotation(App.Vector(1,0,0),180))
    for n,(y,z) in enumerate(d['axes_yz_mm']):
        assembly=doc.addObject('App::Part','CentralCaseBoltAssembly'+str(n));group.addObject(assembly)
        metadata(assembly,SurveyIds=[source['bolt_assembly_identity']],SourceRecord='SNL:27:013',InventoryQuantityRole='assembly identity; bolt, nut, pin counted only as leaves')
        for key,x in [('bolt',0),('nut',c['half_grip']),('cotter',d['cotter_axis_x_mm'])]:link(assembly,key,str(n),[x,y,z])
    doc.Definitions.Visibility=False;doc.recompute();native=out/'TransmissionCaseJointCandidate.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items}
    assert len(items)==len(byid)==len(before)+44==1365
    for i in items:
        name=i['id'];s=i['shape'];assert s.isValid() and len(s.Solids)==1,name
        t,r=placement_errors(s.Placement,expected[name] if name in expected else placements[name]);assert t<1e-6 and r<1e-8,(name,t,r)
        if name not in new_ids+changed:assert same_shape(signatures[name],shape_signature(s)),name
    counts=Counter(pid for name in new_ids for pid in json.loads(byid[name]['target'].SurveyIds))
    assert dict(counts)=={r['part_id']:r['count'] for r in source['physical_inventory']}
    print('Reopened1365 valid leaves;44 new,2 revised,1319 unchanged.',flush=True)
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
    gap('CenterTransmissionCore_bevel_case','CenterTransmissionCore_bevel_cover',c['joint_gap'])
    for suffix in ['Upper','Lower']:
        for case in changed:gap('CentralCaseJoint_gasket'+suffix,case,0)
    for n in range(14):
        gap('CentralCaseJoint_bolt'+str(n),'CenterTransmissionCore_bevel_case',0)
        gap('CentralCaseJoint_nut'+str(n),'CenterTransmissionCore_bevel_cover',0)
        gap('CentralCaseJoint_bolt'+str(n),'CentralCaseJoint_nut'+str(n),.1)
    write(out/'fit_checks.json',dict(overlaps=overlaps,interfaces=interfaces))
    print('Pairs',len(pairs),'overlaps',overlaps,flush=True);print('Failed interfaces',[r for r in interfaces if not r['passed']],flush=True)
    exchange=out/'TransmissionCaseJointParts.step';exchange_ids=new_ids+changed
    Part.makeCompound([byid[n]['shape'] for n in exchange_ids]).exportStep(str(exchange));imp=Part.Shape();imp.read(str(exchange))
    assert imp.isValid() and len(imp.Solids)==len(exchange_ids)
    unmatched=list(imp.Solids);checks=[]
    for name in exchange_ids:
        s=byid[name]['shape'].Solids[0];n=min(range(len(unmatched)),key=lambda n:(s.CenterOfMass-unmatched[n].CenterOfMass).Length);v=unmatched.pop(n)
        ta=s.getTolerance(1);tb=v.getTolerance(1);fuzzy=min(.0001,max(1e-7,ta+tb))
        rm=s.cut(v).Volume;ra=v.cut(s).Volume;missing=s.cut(v,fuzzy);added=v.cut(s,fuzzy)
        checks.append(dict(id=name,native_max_tolerance_mm=ta,step_max_tolerance_mm=tb,comparison_fuzzy_tolerance_mm=fuzzy,tolerance_reporting_roundoff_mm=1e-10,
            raw_missing_mm3=rm,raw_added_mm3=ra,missing_mm3=missing.Volume,added_mm3=added.Volume,
            volume_difference_mm3=abs(s.Volume-v.Volume),center_difference_mm=(s.CenterOfMass-v.CenterOfMass).Length,
            passed=s.isValid() and v.isValid() and abs(s.Volume-v.Volume)<1e-5 and (s.CenterOfMass-v.CenterOfMass).Length<1e-6 and rm<1e-5 and ra<1e-5 and not missing.Faces and not added.Faces and ta<=1e-4 and tb<=max(1e-7,ta)+1e-10))
        write(out/'exchange_progress.json',dict(completed=len(checks),total=len(exchange_ids),failed=[r for r in checks if not r['passed']]))
    assert fingerprint()==lock and check_build(stage/'build')['native_hashes']==build['native_hashes']
    for n,h in hashes.items():assert sha(ROOT/n)==h,n
    passed=not overlaps and all(r['passed'] for r in interfaces+checks)
    report=dict(passed=passed,complete=True,native_occurrences=len(items),new_occurrences=len(new_ids),new_definitions=2,reused_definitions=2,changed_prior_occurrences=2,unchanged_prior_occurrences=len(before)-2,
        new_ids=new_ids,changed_ids=changed,keys_by_id=keys,new_source_counts=dict(counts),material_candidate_pairs=len(pairs),overlaps=overlaps,interfaces=interfaces,
        reused_prior_interfaces=reused,rechecked_interfaces=len(interfaces)-reused,dimensions=d,shaft_axis_world_mm=prior['shaft_axis_world_mm'],input_hashes=hashes,
        authored_fingerprint=lock,tank_native_hashes=build['native_hashes'],native_sha256=sha(native),exchange_sha256=sha(exchange),exchange_roundtrip_checks=checks,
        standard_assembly_modified=False,complete_transmission=False,historical_fit_qualified=False,rendering_complete=False,limitations=source['limits'])
    write(out/'report.json',report);print('PASS' if passed else 'FAIL',flush=True);sys.exit(0 if passed else 1)
finally:runtime.close()
