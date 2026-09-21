"""Populate both central bevel-wheel bearing stacks in the retained fixture."""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--output',type=Path,default=ROOT/'transmission_bevel_sleeve_build');p.add_argument('--worker',action='store_true')
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
    from transmission_bevel_sleeve_parts import sleeve_parts
    from transmission_core_parts import cylinder
    lock=fingerprint();build=check_build(stage/'build');parent=ROOT/'transmission_sun_retention_build'
    names=['transmission_bevel_sleeve_probe.py','transmission_bevel_sleeve_parts.py','transmission_bevel_sleeve_controls.json',
        'transmission_bevel_sleeve_sources.json','transmission_core_parts.py','transmission_core_controls.json','transmission_output_calibration.json',
        'transmission_core_build/report.json','transmission_small_build/report.json','transmission_sun_retention_build/report.json','transmission_sun_retention_build/interface_checks.json',
        'transmission_sun_retention_build/visual_review.json','transmission_sun_retention_build/TransmissionSunRetentionCandidate.FCStd']
    hashes={n:sha(ROOT/n) for n in names}
    for n in names:
        if '/' not in n:
            dest=out/'inputs'/n;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/n).read_bytes())
    source=read(ROOT/'transmission_bevel_sleeve_sources.json')
    for n,h in source['inspected_source_hashes'].items():assert sha(REPO/n)==h,n
    prior=read(parent/'report.json');assert prior['passed'] and prior['rendering_complete']
    assert sha(parent/'TransmissionSunRetentionCandidate.FCStd')==prior['native_sha256']
    assert prior['authored_fingerprint']==lock and prior['tank_native_hashes']==build['native_hashes']
    c={k:v['value'] for k,v in read(ROOT/'transmission_bevel_sleeve_controls.json')['controls'].items()}
    core=read(ROOT/'transmission_core_controls.json')['controls'];cal=read(ROOT/'transmission_output_calibration.json')
    doc=App.openDocument(str(parent/'TransmissionSunRetentionCandidate.FCStd'));doc.recompute()
    before=leaves(doc.Root);old={i['id']:i for i in before};signatures={i['id']:shape_signature(i['shape']) for i in before}
    revised_ids={k:'CenterTransmissionCore_'+n for k,n in [('shaft','cross_shaft'),('case','bevel_case'),('cover','bevel_cover')]}
    revised_ids.update(sun='PortSmallPlanetTrain_sun',sun_bush='PortSmallPlanetTrain_sun_bush')
    originals={k:old[n]['target'].Shape.copy() for k,n in revised_ids.items()}
    parts,revised,dimensions=sleeve_parts(c,core,cal,originals['shaft'],originals['case'],originals['cover'],originals['sun'],read(ROOT/'transmission_small_build/report.json')['dimensions'])
    output_y=read(ROOT/'transmission_core_build/report.json')['output_center_y_mm']
    dimensions['registration_difference_from_output_mm']=output_y+(cal['sprocket_center_x_px']-c['source_bevel_center_x_px'])*cal['mm_per_pixel']
    for k,n in revised_ids.items():
        target=old[n]['target'];target.Tip.Shape=revised[k]
        metadata(target,BevelBearingRevision='Separate M259/M261/M262/M310 stacks, printed-size screw/dowels and split receiver bosses. Enlarged smooth shaft journals admit bushes past spline crests.',
            ParameterUpdate='Regenerate with transmission_bevel_sleeve_probe.py using transmission_bevel_sleeve_controls.json.')
    metadata(old[revised_ids['shaft']]['target'],JournalRevision='Assembly-path correction: bevel and M268 journals R35.5, larger central clutch spline; outboard gear/disk splines retained.')
    definitions={};dowel=old['PortTransmissionBearing_InnerDowel']['target'];old_dowel=dowel.Shape.copy()
    for row in source['physical_inventory']:
        key=row['key']
        if key=='dowel':definitions[key]=dowel;continue
        body=doc.addObject('PartDesign::Body','Def_TransmissionBevelSupport_'+key);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedPart').Shape=parts[key]
        metadata(body,DefinitionId='transmission_bevel_support_'+key,OriginalMark=row['mark'],SurveyIds=[row['part_id']],
            SourceRecord=row['record_id'],Representation='assembly',Coverage='partial',
            ParameterUpdate='Regenerate with transmission_bevel_sleeve_probe.py and transmission_bevel_sleeve_controls.json.',
            ReconstructionNotes='Source identities/counts and screw/dowel sizes retained. Diameters, fits, flange holes and casting/bearing profiles inferred. Gear wheels, shims and complete oil routing pending.')
        definitions[key]=body
    new_ids=[];expected={};keys={}
    for hand in ['Port','Starboard']:
        group=doc.addObject('App::Part',hand+'BevelWheelSupports');doc.TransmissionCore.addObject(group)
        group.Placement=App.Placement(App.Vector(),App.Rotation(App.Vector(1,0,0),180) if hand=='Starboard' else App.Rotation())
        metadata(group,Scope='Flanged bevel-wheel sleeve, inner/outer bushes, oil retainer, set screw and cover dowel. Bevel wheel, clutch ring, rivets and shims pending.')
        for key,target in definitions.items():
            name=hand+'BevelWheelSupports_'+key;link=doc.addObject('App::Link',name);group.addObject(link);link.setLink(target)
            link.LinkPlacement=App.Placement(App.Vector(*dimensions['dowel_origin_mm']) if key=='dowel' else App.Vector(),App.Rotation())
            metadata(link,OccurrenceId=name,Subsystem='Drivetrain',SourceRecord=next(r['record_id'] for r in source['physical_inventory'] if r['key']==key))
            new_ids.append(name);keys[name]=key;expected[name]=doc.TransmissionCore.Placement.multiply(group.Placement).multiply(link.LinkPlacement)
    doc.Definitions.Visibility=False;doc.recompute();native=out/'TransmissionBevelSleeveCandidate.FCStd'
    doc.saveAs(str(native));App.closeDocument(doc.Name);doc=App.openDocument(str(native));doc.recompute()
    items=leaves(doc.Root);byid={i['id']:i for i in items};changed=list(revised_ids.values())+['StarboardSmallPlanetTrain_sun','StarboardSmallPlanetTrain_sun_bush']
    assert len(items)==len(byid)==len(before)+12==1129
    for i in items:
        name=i['id'];assert i['shape'].isValid() and len(i['shape'].Solids)==1,name
        if name in expected:
            t,r=placement_errors(i['shape'].Placement,expected[name].multiply(i['target'].Shape.Placement));assert t<1e-6 and r<1e-8,name
        elif name not in changed:assert same_shape(signatures[name],shape_signature(i['shape'])),name
    counts=Counter(pid for name in new_ids for pid in json.loads(byid[name]['target'].SurveyIds))
    assert dict(counts)=={r['part_id']:r['count'] for r in source['physical_inventory']}
    print('Reopened1129 valid leaves:12 new,7 revised,1110 unchanged.',flush=True)
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
        pre=hand+'BevelWheelSupports_'
        for a,b,g in [('inner_bush','sleeve',c['inner_bush_sleeve_gap']),('outer_bush','sleeve',c['outer_bush_running_gap']),
            ('retainer','sleeve',c['retainer_running_gap']),('outer_bush','retainer',0),('screw','inner_bush',c['hole_radial_gap']),
            ('screw','sleeve',c['hole_radial_gap']),('dowel','outer_bush',c['hole_radial_gap'])]:gap(pre+a,pre+b,g)
        gap(pre+'inner_bush',revised_ids['shaft'],c['inner_bush_bore']-c['shaft_journal_radius'])
        gap(pre+'dowel',revised_ids['cover'],c['hole_radial_gap'])
        for what in ['outer_bush','retainer']:
            for receiver in ['case','cover']:gap(pre+what,revised_ids[receiver],0)
    protection={};outside=cylinder(400,-300,300).cut(cylinder(c['boss_radius']+1,-301,301))
    for key in ['case','cover']:
        a=originals[key].common(outside);b=revised[key].common(outside);protection[key]=a.cut(b).Volume+b.cut(a).Volume;assert protection[key]<1e-5
    protection['shaft_removed_mm3']=originals['shaft'].cut(revised['shaft']).Volume;assert protection['shaft_removed_mm3']<1e-5
    bands=[]
    for sign in [-1,1]:
        for key in ['shaft_journal_limits_y_mm','sun_journal_limits_y_mm']:
            low,high=sorted([sign*y for y in dimensions[key]]);bands.append(cylinder(100,low,high))
    bands.append(cylinder(100,*dimensions['central_spline_limits_y_mm']))
    mask=bands[0].multiFuse(bands[1:]);a=originals['shaft'].cut(mask);b=revised['shaft'].cut(mask)
    protection['shaft_outside_revised_bands_mm3']=a.cut(b).Volume+b.cut(a).Volume;assert protection['shaft_outside_revised_bands_mm3']<1e-5
    # Preserve sun teeth, external splines, retaining groove and shoulders.
    mask=cylinder(c['inner_bush_radius']+c['inner_bush_sleeve_gap']+.01,-500,500)
    a=originals['sun'].cut(mask);b=revised['sun'].cut(mask)
    protection['sun_outside_bore_mm3']=a.cut(b).Volume+b.cut(a).Volume;assert protection['sun_outside_bore_mm3']<1e-5
    reused=byid['PortBevelWheelSupports_dowel']['target'].Shape
    reuse_difference=reused.cut(old_dowel).Volume+old_dowel.cut(reused).Volume;assert reuse_difference<1e-5
    print('Material pairs',len(pairs),'overlaps',overlaps,flush=True);print('Failed interfaces',[r for r in interfaces if not r['passed']],flush=True)
    exchange=out/'TransmissionBevelSleeveParts.step';exchange_ids=new_ids+changed
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
    report=dict(complete=True,passed=passed,native_occurrences=len(items),new_occurrences=12,new_definitions=5,reused_definitions=1,
        changed_prior_occurrences=7,unchanged_prior_occurrences=1110,new_source_counts=dict(counts),new_ids=new_ids,changed_ids=changed,keys_by_id=keys,
        material_candidate_pairs=len(pairs),overlaps=overlaps,interfaces=interfaces,protected_material_differences_mm3=protection,reused_dowel_material_difference_mm3=reuse_difference,
        dimensions=dimensions,shaft_axis_world_mm=prior['shaft_axis_world_mm'],input_hashes=hashes,authored_fingerprint=lock,tank_native_hashes=build['native_hashes'],
        native_sha256=sha(native),exchange_sha256=sha(exchange),exchange_roundtrip_checks=exchange_checks,standard_assembly_modified=False,
        complete_transmission=False,historical_fit_qualified=False,complete_bevel_axial_stack_qualified=False,full_parameter_envelope_qualified=False,rendering_complete=False)
    write(out/'report.json',report);print('PASS' if passed else 'FAIL',flush=True);sys.exit(0 if passed else 1)
finally:runtime.close()
