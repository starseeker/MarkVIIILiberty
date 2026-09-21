"""Populate source-counted bevel wheels, clutch and thrust-bearing assemblies."""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--output',type=Path,default=ROOT/'transmission_bevel_gear_build');p.add_argument('--worker',action='store_true')
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
    from transmission_bevel_gear_parts import support_stack,toothed_blanks,gear_joints,thrust_bearing
    from transmission_core_parts import cylinder,outline_face
    lock=fingerprint();build=check_build(stage/'build');parent=ROOT/'transmission_bevel_sleeve_build'
    names=['transmission_bevel_gear_probe.py','transmission_bevel_gear_parts.py','transmission_bevel_tooth.py',
        'transmission_bevel_gear_controls.json','transmission_bevel_gear_sources.json','transmission_core_parts.py',
        'transmission_core_controls.json','transmission_output_calibration.json','transmission_core_build/report.json',
        'transmission_bevel_sleeve_build/report.json','transmission_bevel_sleeve_build/interface_checks.json',
        'transmission_bevel_sleeve_build/visual_review.json','transmission_bevel_sleeve_build/TransmissionBevelSleeveCandidate.FCStd',
        'transmission_sun_retention_build/report.json','transmission_sun_retention_build/TransmissionSunRetentionCandidate.FCStd']
    hashes={n:sha(ROOT/n) for n in names}
    for n in names:
        if '/' not in n:
            dest=out/'inputs'/n;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/n).read_bytes())
    source=read(ROOT/'transmission_bevel_gear_sources.json');rows={r['key']:r for r in source['physical_inventory']}
    for n,h in source['inspected_source_hashes'].items():assert sha(REPO/n)==h,n
    prior=read(parent/'report.json');assert prior['passed'] and prior['rendering_complete']
    assert sha(parent/'TransmissionBevelSleeveCandidate.FCStd')==prior['native_sha256']
    assert prior['authored_fingerprint']==lock and prior['tank_native_hashes']==build['native_hashes']
    baseline_report=read(ROOT/'transmission_sun_retention_build/report.json')
    assert sha(ROOT/'transmission_sun_retention_build/TransmissionSunRetentionCandidate.FCStd')==baseline_report['native_sha256']
    c={k:v['value'] for k,v in read(ROOT/'transmission_bevel_gear_controls.json')['controls'].items()}
    core=read(ROOT/'transmission_core_controls.json')['controls'];cal=read(ROOT/'transmission_output_calibration.json')
    doc=App.openDocument(str(parent/'TransmissionBevelSleeveCandidate.FCStd'));doc.recompute()
    before=leaves(doc.Root);old={i['id']:i for i in before};signatures={i['id']:shape_signature(i['shape']) for i in before}
    base=App.openDocument(str(ROOT/'transmission_sun_retention_build/TransmissionSunRetentionCandidate.FCStd'));base.recompute()
    baseline={i['id']:i for i in leaves(base.Root)}
    revised={k:'CenterTransmissionCore_'+n for k,n in [('shaft','cross_shaft'),('case','bevel_case'),('cover','bevel_cover')]}
    revised.update({k:'PortBevelWheelSupports_'+k for k in ['sleeve','inner_bush','outer_bush','retainer','screw']})
    originals={k:old[n]['target'].Shape.copy() for k,n in revised.items()}
    parts,d=support_stack(c,prior['dimensions'],core,originals['shaft'],baseline[revised['case']]['target'].Shape,
        baseline[revised['cover']]['target'].Shape,old['PortSmallPlanetTrain_sun']['target'].Shape.BoundBox.YMin,
        old['PortTransmissionCore_high_drum']['target'].Shape.BoundBox.YMin)
    App.closeDocument(base.Name)
    blanks,teeth=toothed_blanks(c,d);joints,jd=gear_joints(c,blanks['wheel'],parts['sleeve'],d)
    parts.update(joints);parts['pinion']=blanks['pinion'];bearing,bd=thrust_bearing(c,d['thrust_limits_y_mm'][0])
    d['registration_difference_from_output_mm']=prior['dimensions']['registration_difference_from_output_mm']
    d['joints']=jd;d['teeth']=teeth;d['thrust_bearing']=bd
    for key,name in revised.items():
        target=old[name]['target'];target.Tip.Shape=parts[key]
        metadata(target,BevelGearRevision='Printed thrust-bearing envelope constrains extended M259/M261/M262/M310 stack. Input boss trimmed to existing case cavity. Rivet receivers replace provisional six-hole pattern.',
            ParameterUpdate='Regenerate with transmission_bevel_gear_probe.py and transmission_bevel_gear_controls.json.')
    for hand in ['Port','Starboard']:
        metadata(doc.getObject(hand+'BevelWheelSupports'),Scope='M259/M261/M262/M310 and screw/dowel support stack revised for 105 x155 x40mm thrust bearing, M260 shim and adjacent sun/drum datums.')
    definitions={}
    for key in ['wheel','clutch_ring','clutch','pinion','shim','rivet_short','rivet_long','rotating_race','stationary_race','cage','ball']:
        internal=key in ['rotating_race','stationary_race','cage','ball'];row=rows['thrust_bearing' if internal else key]
        shape=Part.makeSphere(c['ball_radius']) if key=='ball' else bearing[key] if internal else parts[key]
        body=doc.addObject('PartDesign::Body','Def_TransmissionBevelGear_'+key);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedPart').Shape=shape
        metadata(body,DefinitionId='transmission_bevel_gear_'+key,OriginalMark=row['mark']+(' / inferred '+key if internal else ''),
            SurveyIds=[] if internal else [row['part_id']],SourceRecord=row['record_id'],Representation='assembly',Coverage='partial',
            ParameterUpdate='Regenerate with transmission_bevel_gear_probe.py and transmission_bevel_gear_controls.json.',
            ReconstructionNotes='Printed tooth counts/pitch, bearing envelope and fastener blank sizes retained; other profiles, clearances, tooth corrections and bearing internals inferred.')
        if internal:metadata(body,ParentSurveyId=row['part_id'],InventoryQuantityRole='inferred decomposition of commercial bearing')
        definitions[key]=body
    new_ids=[];expected={};keys={};bearing_groups=[]
    def link(group,name,key,placement=None):
        obj=doc.addObject('App::Link',name);group.addObject(obj);obj.setLink(definitions[key])
        obj.LinkPlacement=placement or App.Placement()
        metadata(obj,OccurrenceId=name,Subsystem='Drivetrain',SourceRecord=definitions[key].SourceRecord)
        new_ids.append(name);keys[name]=key
        # All groups sit beneath TransmissionCore; bearing containers are identity.
        ancestor=group if group.Name.endswith('BevelDrive') else doc.getObject(group.Name.split('ThrustBearing')[0]+'BevelDrive')
        expected[name]=doc.TransmissionCore.Placement.multiply(ancestor.Placement).multiply(obj.LinkPlacement)
    for hand in ['Port','Starboard']:
        group=doc.addObject('App::Part',hand+'BevelDrive');doc.TransmissionCore.addObject(group)
        group.Placement=App.Placement(App.Vector(),App.Rotation(App.Vector(1,0,0),180) if hand=='Starboard' else App.Rotation())
        metadata(group,Scope='M258A wheel, M258B four-dog ring, 12 formed rivets, M260 shim and one decomposed thrust bearing.')
        for key in ['wheel','clutch_ring','shim']:link(group,hand+'BevelDrive_'+key,key)
        for row in jd['rivet_occurrences']:
            link(group,hand+'BevelDrive_'+row['key']+str(row['index']),row['key'],App.Placement(App.Vector(*row['position_mm']),App.Rotation()))
        assembly=doc.addObject('App::Part',hand+'ThrustBearing');group.addObject(assembly);bearing_groups.append(assembly.Name)
        row=rows['thrust_bearing']
        metadata(assembly,SurveyIds=[row['part_id']],SourceRecord=row['record_id'],CatalogueQuantity=1,
            InventoryQuantityRole='commercial bearing assembly',ReconstructionNotes='Printed105 x155 x40mm envelope; two races, cage and16 balls are inferred internals.')
        for key in ['rotating_race','stationary_race','cage']:link(assembly,hand+'ThrustBearing_'+key,key)
        for n in range(c['ball_count']):
            a=2*math.pi*n/c['ball_count'];pos=App.Vector(c['ball_pitch_radius']*math.cos(a),sum(d['thrust_limits_y_mm'])/2,c['ball_pitch_radius']*math.sin(a))
            link(assembly,hand+'ThrustBearing_ball'+str(n).zfill(2),'ball',App.Placement(pos,App.Rotation()))
    group=doc.addObject('App::Part','CenterBevelDrive');doc.TransmissionCore.addObject(group)
    metadata(group,Scope='M247 integral pinion/shaft and M257A clutch in standard ahead engagement. Input-bearing/coupling assembly pending.')
    link(group,'CenterBevelDrive_pinion','pinion')
    link(group,'CenterBevelDrive_clutch','clutch',App.Placement(App.Vector(0,c['forward_clutch_y'],0),App.Rotation()))
    doc.Definitions.Visibility=False;doc.recompute();native=out/'TransmissionBevelGearCandidate.FCStd'
    doc.saveAs(str(native));App.closeDocument(doc.Name);doc=App.openDocument(str(native));doc.recompute()
    items=leaves(doc.Root);byid={i['id']:i for i in items}
    changed=list(revised.values())+['StarboardBevelWheelSupports_'+k for k in ['sleeve','inner_bush','outer_bush','retainer','screw']]
    assert len(items)==len(byid)==len(before)+70==1199
    for i in items:
        name=i['id'];assert i['shape'].isValid() and len(i['shape'].Solids)==1,name
        if name in expected:
            t,r=placement_errors(i['shape'].Placement,expected[name].multiply(i['target'].Shape.Placement));assert t<1e-6 and r<1e-8,name
        elif name not in changed:assert same_shape(signatures[name],shape_signature(i['shape'])),name
    counts=Counter(pid for name in new_ids for pid in json.loads(byid[name]['target'].SurveyIds))
    for name in bearing_groups:counts.update(json.loads(doc.getObject(name).SurveyIds))
    assert dict(counts)=={r['part_id']:r['count'] for r in source['physical_inventory']}
    assert len(new_ids)==70 and len(changed)==13
    print('Reopened1199 valid leaves:70 new,13 revised,1116 unchanged; catalogue bearings counted at assembly level.',flush=True)
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
    for hand in ['Port','Starboard']:
        pre=hand+'BevelDrive_';support=hand+'BevelWheelSupports_';thrust=hand+'ThrustBearing_'
        for a,b,g in [(pre+'wheel',support+'sleeve',0),(pre+'clutch_ring',pre+'wheel',0),
            (thrust+'rotating_race',support+'sleeve',0),(thrust+'stationary_race',pre+'shim',0),
            (pre+'shim',support+'outer_bush',0),(support+'sleeve',hand+'SmallPlanetTrain_sun',c['sleeve_sun_gap']),
            (support+'retainer',hand+'TransmissionCore_high_drum',c['retainer_drum_gap'])]:gap(a,b,g)
        for n in range(c['ball_count']):
            for race in ['rotating_race','stationary_race']:gap(thrust+'ball'+str(n).zfill(2),thrust+race,c['race_ball_gap'])
            gap(thrust+'ball'+str(n).zfill(2),thrust+'cage',c['cage_ball_gap'])
        for role in ['short','long']:
            for n in range(6):
                rivet=pre+'rivet_'+role+str(n)
                for receiver in [pre+'wheel',support+'sleeve']+([pre+'clutch_ring'] if role=='long' else []):
                    # The long rivet's head seats on the clutch ring; its shank
                    # passes through the intermediate wheel with radial clearance.
                    gap(rivet,receiver,c['rivet_hole_gap'] if role=='long' and receiver==pre+'wheel' else 0)
    gap('CenterBevelDrive_clutch',revised['shaft'],(c['clutch_spline_width']-11)/2)
    protection={};mask=cylinder(c['thrust_boss_radius']+1,-230,230)
    cavity=outline_face(core['bevel_outline_segments'],core['bevel_cavity_scale']).extrude(App.Vector(0,226,0));cavity.translate(App.Vector(0,-113,0))
    for key in ['case','cover']:
        region=mask if key=='case' else mask.fuse(cavity)
        a=originals[key].cut(region);b=parts[key].cut(region)
        protection[key+'_outside_bosses_and_cavity_mm3']=a.cut(b).Volume+b.cut(a).Volume
    protection['shaft_removed_mm3']=originals['shaft'].cut(parts['shaft']).Volume
    bands=[]
    for sign in [-1,1]:
        low,high=sorted(sign*y for y in d['journal_limits_y_mm']);bands.append(cylinder(100,low,high))
    mask=bands[0].fuse(bands[1]);a=originals['shaft'].cut(mask);b=parts['shaft'].cut(mask)
    protection['shaft_outside_journals_mm3']=a.cut(b).Volume+b.cut(a).Volume
    assert all(v<1e-5 for v in protection.values()),protection
    print('Material pairs',len(pairs),'overlaps',overlaps,flush=True)
    print('Failed interfaces',[r for r in interfaces if not r['passed']],flush=True)
    write(out/'fit_checks.json',dict(overlaps=overlaps,interfaces=interfaces,protected_material_differences_mm3=protection))
    exchange=out/'TransmissionBevelGearParts.step';exchange_ids=new_ids+changed
    Part.makeCompound([byid[n]['shape'] for n in exchange_ids]).exportStep(str(exchange))
    imported=Part.Shape();imported.read(str(exchange));assert imported.isValid() and len(imported.Solids)==len(exchange_ids)
    unmatched=list(imported.Solids);exchange_checks=[]
    for name in exchange_ids:
        a=byid[name]['shape'].Solids[0];n=min(range(len(unmatched)),key=lambda n:(a.CenterOfMass-unmatched[n].CenterOfMass).Length);b=unmatched.pop(n)
        ta=a.getTolerance(1);tb=b.getTolerance(1);fuzzy=min(.0001,max(1e-7,ta+tb));raw_a=a.cut(b);raw_b=b.cut(a);missing=a.cut(b,fuzzy);extra=b.cut(a,fuzzy)
        exchange_checks.append(dict(id=name,comparison_fuzzy_tolerance_mm=fuzzy,native_max_tolerance_mm=ta,step_max_tolerance_mm=tb,
            raw_missing_mm3=raw_a.Volume,raw_added_mm3=raw_b.Volume,missing_mm3=missing.Volume,added_mm3=extra.Volume,missing_faces=len(missing.Faces),added_faces=len(extra.Faces),
            passed=a.isValid() and b.isValid() and not missing.Faces and not extra.Faces and ta<=.0001 and tb<=max(1e-7,ta)*(1+1e-6)))
        write(out/'exchange_progress.json',dict(completed=len(exchange_checks),total=len(exchange_ids),failed=[r for r in exchange_checks if not r['passed']]))
    passed=not overlaps and all(r['passed'] for r in interfaces+exchange_checks)
    assert fingerprint()==lock and check_build(stage/'build')['native_hashes']==build['native_hashes']
    assert all(sha(ROOT/n)==h for n,h in hashes.items())
    report=dict(complete=True,passed=passed,native_occurrences=len(items),new_occurrences=70,new_definitions=11,
        changed_prior_occurrences=13,unchanged_prior_occurrences=1116,new_source_counts=dict(counts),new_ids=new_ids,changed_ids=changed,keys_by_id=keys,
        bearing_assembly_ids=bearing_groups,bearing_internal_leaf_count=38,material_candidate_pairs=len(pairs),overlaps=overlaps,interfaces=interfaces,
        protected_material_differences_mm3=protection,dimensions=d,shaft_axis_world_mm=prior['shaft_axis_world_mm'],input_hashes=hashes,
        authored_fingerprint=lock,tank_native_hashes=build['native_hashes'],native_sha256=sha(native),exchange_sha256=sha(exchange),
        exchange_roundtrip_checks=exchange_checks,standard_assembly_modified=False,complete_transmission=False,historical_fit_qualified=False,
        complete_input_bearing_stack_qualified=False,full_parameter_envelope_qualified=False,rendering_complete=False)
    write(out/'report.json',report);print('PASS' if passed else 'FAIL',flush=True);sys.exit(0 if passed else 1)
finally:runtime.close()
