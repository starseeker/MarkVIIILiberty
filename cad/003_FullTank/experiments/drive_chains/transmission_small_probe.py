"""Populate the small planetary gears and riveted input disks on both sides."""
import argparse
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
parser.add_argument('--output',type=Path,default=ROOT/'transmission_small_build')
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
    from transmission_small_parts import small_parts
    from transmission_core_parts import box
    lock=fingerprint();build=check_build(stage/'build')
    parent='transmission_ring_support_build'
    names=['transmission_small_probe.py','transmission_small_parts.py','transmission_small_controls.json','transmission_small_sources.json',
        'transmission_planet_parts.py','transmission_core_parts.py','transmission_core_controls.json','transmission_output_calibration.json',
        'transmission_core_build/report.json',parent+'/report.json',parent+'/visual_review.json',parent+'/interface_checks.json',
        parent+'/TransmissionRingSupportCandidate.FCStd']
    hashes={n:sha(ROOT/n) for n in names}
    for n in names:
        if '/' not in n:
            p=out/'inputs'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/n).read_bytes())
    source=read(ROOT/'transmission_small_sources.json')
    for n,digest in source['inspected_source_hashes'].items():assert sha(REPO/n)==digest,n
    prior=read(ROOT/parent/'report.json');prior_native=ROOT/names[-1]
    assert prior['passed'] and prior['rendering_complete'] and prior['native_sha256']==sha(prior_native)
    assert prior['authored_fingerprint']==lock and prior['tank_native_hashes']==build['native_hashes']
    c={k:v['value'] for k,v in read(ROOT/'transmission_small_controls.json')['controls'].items()}
    core=read(ROOT/'transmission_core_controls.json')['controls'];cal=read(ROOT/'transmission_output_calibration.json')
    output_y=read(ROOT/'transmission_core_build/report.json')['output_center_y_mm']
    doc=App.openDocument(str(prior_native));doc.recompute();before=leaves(doc.Root);old={i['id']:i for i in before}
    signatures={i['id']:shape_signature(i['shape']) for i in before}
    shaft_id='CenterTransmissionCore_cross_shaft';old_shaft=old[shaft_id]['target'].Shape.copy()
    parts,shaft,dimensions=small_parts(c,core,cal,output_y,old_shaft)
    old[shaft_id]['target'].Tip.Shape=shaft
    metadata(old[shaft_id]['target'],JournalRevision='Remove spline crests only at the two small sun bush journals; inherited root radius retained.',
        ParameterUpdate='Regenerate using transmission_small_probe.py and transmission_small_controls.json, from the saved ring-support candidate.')
    definitions={}
    for row in source['physical_inventory']:
        k=row['key'];body=doc.addObject('PartDesign::Body','Def_TransmissionSmall_'+k);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedPart').Shape=parts[k]
        metadata(body,DefinitionId='transmission_small_'+k,OriginalMark=row['mark'],SurveyIds=[row['part_id']],SourceRecord=row['record_id'],
            Representation='assembly',Coverage='partial',ParameterUpdate='Regenerate with transmission_small_probe.py using transmission_small_controls.json.',
            ReconstructionNotes='Printed small sun/ring teeth and rivet sizes; derived planet count; inferred cast profiles, axial stations, bores and fits. M276 printed tooth-row conflict retained. Small planet pin supports remain pending.')
        if k in dimensions['tooth_profiles']:metadata(body,ToothProfile=dimensions['tooth_profiles'][k])
        definitions[k]=body
    new_ids=[];keys={};expected={}
    for hand in ['Port','Starboard']:
        group=doc.addObject('App::Part',hand+'SmallPlanetTrain');doc.getObject(hand+'TransmissionCore').addObject(group)
        rotation=App.Rotation(App.Vector(1,0,0),180) if hand=='Starboard' else App.Rotation()
        group.Placement=App.Placement(App.Vector(),rotation)
        metadata(group,Scope='Small sun/bush, three planets and separate disk/ring joined by sixteen rivets. Planet support stacks pending.')
        def install(key,suffix='',radius=0,angle=0,clock=0):
            name=hand+'SmallPlanetTrain_'+key+suffix;link=doc.addObject('App::Link',name);group.addObject(link);link.setLink(definitions[key])
            link.LinkPlacement=App.Placement(App.Vector(radius*math.cos(angle),0,radius*math.sin(angle)),App.Rotation(App.Vector(0,1,0),-math.degrees(clock)))
            metadata(link,OccurrenceId=name,Subsystem='Drivetrain')
            new_ids.append(name);keys[name]=key;expected[name]=doc.TransmissionCore.Placement.multiply(group.Placement).multiply(link.LinkPlacement)
        for key in ['sun','sun_bush','ring','disk']:install(key)
        for n in range(3):
            angle=2*math.pi*n/3
            install('planet',str(n),dimensions['planet_center_radius_mm'],angle,
                (c['teeth_sun']+c['teeth_planet'])/c['teeth_planet']*angle+math.pi/c['teeth_planet'])
        for n in range(c['rivet_count_per_side']):install('rivet',str(n),c['rivet_circle_radius'],2*math.pi*n/c['rivet_count_per_side'])
    doc.Definitions.Visibility=False;doc.recompute();native=out/'TransmissionSmallCandidate.FCStd'
    doc.saveAs(str(native));App.closeDocument(doc.Name);doc=App.openDocument(str(native));doc.recompute()
    items=leaves(doc.Root);byid={i['id']:i for i in items};changed=[shaft_id]
    assert len(items)==len(byid)==len(before)+46==1059
    for i in items:
        name=i['id'];assert i['shape'].isValid() and len(i['shape'].Solids)==1,name
        if name in expected:
            p=expected[name].multiply(i['target'].Shape.Placement);t,r=placement_errors(i['shape'].Placement,p);assert t<1e-6 and r<1e-8,name
        elif name not in changed:assert same_shape(signatures[name],shape_signature(i['shape'])),name
    counts=Counter(pid for name in new_ids for pid in json.loads(byid[name]['target'].SurveyIds))
    assert dict(counts)=={r['part_id']:r['count'] for r in source['physical_inventory']}
    print('Reopened1059 valid single-solid leaves;46new,1changed,1012unchanged.',flush=True)
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
    print('Material pairs',len(pairs),'overlaps',overlaps,flush=True)
    interfaces=[];meshes=[];teeth=[]
    def gap(a,b,expected):
        value=byid[a]['shape'].distToShape(byid[b]['shape'])[0]
        interfaces.append(dict(a=a,b=b,gap_mm=value,expected_mm=expected,passed=abs(value-expected)<1e-5))
    for row in prior['interfaces']:gap(row['a'],row['b'],row['expected_mm'])
    for hand in ['Port','Starboard']:
        pre=hand+'SmallPlanetTrain_'
        gap(pre+'sun_bush',shaft_id,c['sun_bush_inner_radius']-c['shaft_journal_radius'])
        gap(pre+'sun_bush',pre+'sun',c['sun_bush_outer_gap'])
        gap(pre+'disk',pre+'ring',0)
        gap(pre+'disk',shaft_id,c['spline_side_gap'])
        gap(pre+'sun',hand+'TransmissionCore_high_drum',c['spline_side_gap'])
        for n in range(c['rivet_count_per_side']):
            for key in ['disk','ring']:gap(pre+'rivet'+str(n),pre+key,0)
        for n in range(3):
            name=pre+'planet'+str(n);s=byid[name]['shape']
            values={k:s.distToShape(byid[pre+k]['shape'])[0] for k in ['sun','ring']}
            meshes.append(dict(id=name,tooth_gaps_mm=values,passed=all(.001<v<.5 for v in values.values())))
        for key in ['sun','planet','ring']:
            tip=dimensions['tooth_profiles'][key]['root_radius_mm' if key=='ring' else 'tip_radius_mm']
            for name in [n for n in new_ids if n.startswith(pre) and keys[n]==key]:
                count=sum(isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-tip)<1e-6 for f in byid[name]['shape'].Faces)
                teeth.append(dict(id=name,native_tip_patches=count,expected_teeth=c['teeth_'+key],passed=count==c['teeth_'+key]))
    # Material outside the two intentional journal intervals must be unchanged.
    protected=old_shaft.copy()
    lo,hi=dimensions['shaft_journal_y_mm']
    for sign in [-1,1]:
        a,b=sorted([sign*lo,sign*hi]);protected=protected.cut(box(-100,100,a-.001,b+.001,-100,100))
    loss=protected.cut(shaft).Volume;added=shaft.cut(old_shaft).Volume;assert loss<1e-5 and added<1e-5
    exchange=out/'TransmissionSmallParts.step';exchange_ids=new_ids+changed
    Part.makeCompound([byid[n]['shape'] for n in exchange_ids]).exportStep(str(exchange))
    imported=Part.Shape();imported.read(str(exchange));assert imported.isValid() and len(imported.Solids)==len(exchange_ids)
    unmatched=list(imported.Solids);exchange_checks=[]
    for name in exchange_ids:
        a=byid[name]['shape'].Solids[0];n=min(range(len(unmatched)),key=lambda n:(a.CenterOfMass-unmatched[n].CenterOfMass).Length);b=unmatched.pop(n)
        missing=a.cut(b);extra=b.cut(a);ta=a.getTolerance(1);tb=b.getTolerance(1)
        exchange_checks.append(dict(id=name,volume_difference_mm3=abs(a.Volume-b.Volume),center_difference_mm=(a.CenterOfMass-b.CenterOfMass).Length,
            missing_faces=len(missing.Faces),added_faces=len(extra.Faces),missing_mm3=missing.Volume,added_mm3=extra.Volume,
            native_max_tolerance_mm=ta,step_max_tolerance_mm=tb,
            passed=a.isValid() and b.isValid() and not missing.Faces and not extra.Faces and abs(missing.Volume)<1e-5 and abs(extra.Volume)<1e-5
                and ta<=.0001 and tb<=max(1e-7,ta)*(1+1e-6)))
    passed=not overlaps and all(r['passed'] for r in interfaces+meshes+teeth+exchange_checks)
    report=dict(complete=True,passed=passed,native_occurrences=len(items),new_occurrences=46,changed_prior_occurrences=1,unchanged_prior_occurrences=1012,
        new_source_counts=dict(counts),new_ids=new_ids,changed_ids=changed,keys_by_id=keys,material_candidate_pairs=len(pairs),overlaps=overlaps,
        interfaces=interfaces,mesh_checks=meshes,tooth_count_checks=teeth,dimensions=dimensions,shaft_axis_world_mm=prior['shaft_axis_world_mm'],
        protected_shaft_loss_mm3=loss,shaft_added_material_mm3=added,input_hashes=hashes,authored_fingerprint=lock,tank_native_hashes=build['native_hashes'],
        native_sha256=sha(native),exchange_sha256=sha(exchange),exchange_roundtrip_solids=len(imported.Solids),exchange_roundtrip_checks=exchange_checks,
        standard_assembly_modified=False,complete_transmission=False,historical_fit_qualified=False,full_parameter_envelope_qualified=False,rendering_complete=False)
    write(out/'report.json',report)
    for r in [r for r in interfaces+meshes+teeth+exchange_checks if not r['passed']]:print('FAILED',r,flush=True)
    COLORS.update(SmallGear=(.64,.51,.31),SmallMetal=(.52,.59,.62),SmallBush=(.69,.51,.24))
    selected=[dict(i,system='SmallBush' if keys[i['id']]=='sun_bush' else 'SmallGear' if keys[i['id']] in ['sun','planet','ring'] else 'SmallMetal')
        for i in items if i['id'].startswith('PortSmallPlanetTrain_')]
    gears=[i for i in selected if keys[i['id']] in ['sun','planet','ring']]
    shaded(gears,out/'small_gears_front.svg',(0,1,0),'Small planetary train | 30-tooth sun, three inferred 24-tooth planets, 78-tooth ring')
    shaded(selected,out/'small_train_oblique.svg',(1,-1,.7),'Small planetary assembly | separate sleeve, bush, input disk and sixteen ring rivets')
    origin=App.Vector(*prior['shaft_axis_world_mm']);section=[]
    context_ids=['CenterTransmissionCore_cross_shaft','PortTransmissionCore_high_drum','PortTransmissionCore_plain_case']
    for i in selected+[byid[n] for n in context_ids]:
        b=i['shape'].copy().cleaned().BoundBox
        if b.ZMin>=origin.z:continue
        s=i['shape'].common(box(b.XMin-1,b.XMax+1,max(-1,b.YMin-1),b.YMax+1,b.ZMin-1,origin.z))
        if s.isNull() or not s.Solids:continue
        section.append(dict(i,shape=s,target=SimpleNamespace(Shape=s),definition=i['definition']+'_cut_'+i['id']))
    shaded(section,out/'small_train_cutaway.svg',(1,-1,1.2),'Small train cutaway | shaft journals, bushed sun sleeve, riveted disk and retained case')
    assert fingerprint()==lock and check_build(stage/'build')['native_hashes']==build['native_hashes']
    assert all(sha(ROOT/n)==digest for n,digest in hashes.items())
    report.update(rendering_complete=True,output_raster_hashes={p.name:sha(p) for p in out.glob('*.png')});write(out/'report.json',report)
    print('PASS' if passed else 'FAIL',flush=True);sys.exit(0 if passed else 1)
finally:runtime.close()
