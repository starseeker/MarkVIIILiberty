"""Install fixed transmission brackets/caps around the saved output sleeves."""
import argparse
import base64
import json
from collections import Counter
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage',type=Path,required=True)
parser.add_argument('--output',type=Path,default=ROOT/'transmission_support_build')
parser.add_argument('--worker',action='store_true')
args=parser.parse_args();stage=args.stage.resolve();out=args.output.resolve()
sys.path.insert(0,str(stage))
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
    from types import SimpleNamespace
    from lib.cad_build import leaves,metadata,shape_signature
    from lib.worker import check_build,same_shape,placement_errors
    from lib.visual_review import shaded
    from transmission_support_parts import parts

    lock=fingerprint();build=check_build(stage/'build')
    names=['transmission_support_probe.py','transmission_support_parts.py','transmission_support_controls.json',
           'transmission_support_sources.json','transmission_output_parts.py','transmission_output_calibration.json',
           'transmission_bush_build/report.json','transmission_bush_build/retained_interface_checks.json',
           'transmission_bush_build/TransmissionBushCandidate.FCStd']
    hashes={name:sha(ROOT/name) for name in names}
    for name in names:
        if '/' not in name:
            target=out/'inputs'/name;target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes((ROOT/name).read_bytes())
    source=read(ROOT/'transmission_support_sources.json')
    for name,digest in source['inspected_source_hashes'].items():assert sha(REPO/name)==digest
    record=read(ROOT/'transmission_support_controls.json')
    controls={k:v['value'] for k,v in record['controls'].items()}
    calibration=read(ROOT/'transmission_output_calibration.json')
    prior=read(ROOT/'transmission_bush_build/report.json')
    assert prior['passed'] and prior['rendering_complete']
    assert prior['native_sha256']==hashes[names[-1]]
    assert prior['authored_fingerprint']==lock and prior['tank_native_hashes']==build['native_hashes']
    doc=App.openDocument(str(ROOT/names[-1]));doc.recompute();before=leaves(doc.Root)
    signatures={i['id']:shape_signature(i['shape']) for i in before}
    shapes,dimensions=parts(controls,record['conditional_image_picks'],calibration,prior['dimensions']['bushes'])
    identities={'inner_bracket':('M293','SNL:42:003'),'outer_bracket':('M297','SNL:42:008'),
                'inner_cap':('M294','SNL:56:017'),'outer_cap':('M298','SNL:56:026'),
                'lid':('M295','SNL:56:016')}
    definitions={};expected_counts={}
    for name,shape in shapes.items():
        body=doc.addObject('PartDesign::Body','Def_FixedBearing_'+name);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedPart').Shape=shape
        if name in identities:
            mark,record_id=identities[name]
            row=next(r for r in source['rows'] if r['record_id']==record_id)
            ids=row['part_ids'];assert len(ids)==1
            expected_counts[ids[0]]=4 if name=='lid' else 2
        else:
            mark='';record_id='SNL_NOTE:gq';ids=[]
        metadata(body,DefinitionId='transmission_fixed_'+name,OriginalMark=mark,SurveyIds=ids,
                 SourceRecord=record_id,Representation='assembly',Coverage='partial',
                 InSituMaterial='babbitt lining' if not ids else '',
                 ReconstructionNotes='Fixed frame, independent of shaft phase. Inferred dimensions in transmission_support_controls.json; frame attachment and fittings incomplete.')
        definitions[name]=body
    new_ids=[];poses={};fixed_frames={};rotor_frames={}
    assembly=doc.addObject('App::Part','FixedTransmissionBearings');doc.Root.addObject(assembly)
    metadata(assembly,Scope='Four split fixed bearing castings, separate poured lining regions and common oil-box lids; attachment frame and hardware pending')
    for hand in ['Port','Starboard']:
        shaft=next(i for i in before if i['id']==hand+'TransmissionOutput_shaft')
        rotor=shaft['shape'].Placement.multiply(shaft['target'].Shape.Placement.inverse())
        rotor_frames[hand]=rotor
        for setting in prior['dimensions']['installations']:
            role=setting['role'];center=rotor.multVec(App.Vector(0,setting['center_y_mm'],0))
            frame=App.Placement(center,App.Rotation());fixed_frames[hand+role]=frame
            group=doc.addObject('App::Part',hand+role.title()+'FixedBearing');assembly.addObject(group)
            group.Placement=frame
            metadata(group,Scope='Fixed body/cap and in-situ lining. Cup opening world +Z; foot points aft -X.')
            for component in ['bracket','cap','lining_back','lining_front','lid']:
                key='lid' if component=='lid' else role+'_'+component
                local=App.Placement()
                if component=='lid':
                    d=dimensions[role]
                    local.Base=App.Vector(d['cup_back_x_mm'],0,d['cup_top_z_mm']+controls['lid_gap'])
                name=hand+'FixedBearing_'+role+'_'+component
                link=doc.addObject('App::Link',name);group.addObject(link);link.setLink(definitions[key]);link.LinkPlacement=local
                metadata(link,OccurrenceId=name,Subsystem='Drivetrain')
                new_ids.append(name);poses[name]=frame.multiply(local).multiply(definitions[key].Shape.Placement)
    metadata(doc.Root,Scope='Chain/casing/output candidate with fixed bracket/cap castings and in-situ bearing linings; frame, studs and oil fittings still incomplete')
    doc.Definitions.Visibility=False;doc.recompute()
    native=out/'TransmissionSupportCandidate.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items}
    assert len(items)==len(byid)==845
    for item in items:
        assert item['shape'].isValid() and len(item['shape'].Solids)==1,item['id']
        if item['id'] in new_ids:
            translation,rotation=placement_errors(item['shape'].Placement,poses[item['id']])
            assert translation<1e-6 and rotation<1e-8,item['id']
        else:assert same_shape(signatures[item['id']],shape_signature(item['shape'])),item['id']
    counts=Counter(pid for name in new_ids for pid in json.loads(byid[name]['target'].SurveyIds))
    assert dict(counts)==expected_counts
    tank=App.openDocument(build['build']['top_document']);tank.recompute()
    replaced={'hull_engine_back','PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting',
              'hull_port_inner_rear_end','hull_port_rear_wing','hull_starboard_inner_rear_end','hull_starboard_rear_wing'}
    context=[i for i in leaves(tank.Root) if i['id'] not in replaced and i['representation']=='assembly']
    physical=items+context
    assert len({i['id'] for i in physical})==len(physical)
    boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].BoundBox for i in physical]])
    pairs=set();overlaps=[]
    for name in new_ids:
        first=byid[name];b=first['shape'].BoundBox
        bb=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
        near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
        for index in near:
            second=physical[index];pair=tuple(sorted([name,second['id']]))
            if pair[0]==pair[1] or pair in pairs:continue
            pairs.add(pair);intersection=first['shape'].common(second['shape']);volume=intersection.Volume
            if volume>1e-5:
                b=intersection.BoundBox
                overlaps.append(dict(a=name,b=second['id'],volume_mm3=volume,
                                     world_bounds_mm=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]))
    interfaces=[]
    for hand in ['Port','Starboard']:
        for role in ['inner','outer']:
            prefix=hand+'FixedBearing_'+role+'_';frame=fixed_frames[hand+role]
            sleeve=byid[hand+'TransmissionBearing_'+role.title()+'Bush']['shape']
            bracket=byid[prefix+'bracket']['shape'];cap=byid[prefix+'cap']['shape']
            front=byid[prefix+'lining_front']['shape'];back=byid[prefix+'lining_back']['shape']
            radial=[region.distToShape(sleeve)[0] for region in [front,back]]
            captures=[]
            for sign in [-1,1]:
                moved=front.fuse(back);moved.translate(App.Vector(0,sign,0));captures.append(moved.common(sleeve).Volume)
            split=cap.distToShape(bracket)[0]
            lining_seat=[front.distToShape(cap)[0],back.distToShape(bracket)[0]]
            lid_gap=byid[prefix+'lid']['shape'].distToShape(cap)[0]
            upward=frame.Rotation.multVec(App.Vector(0,0,1))
            passed=(all(abs(g-controls['running_gap'])<1e-5 for g in radial)
                    and all(v>1 for v in captures) and abs(split-2*controls['split_gap'])<1e-5
                    and all(g<1e-7 for g in lining_seat) and abs(lid_gap-controls['lid_gap'])<1e-5
                    and (upward-App.Vector(0,0,1)).Length<1e-8)
            interfaces.append(dict(hand=hand,role=role,sleeve_to_lining_gap_mm=radial,
                                   flange_axial_capture_mm3=captures,cap_split_mm=split,
                                   lining_seat_gap_mm=lining_seat,lid_gap_mm=lid_gap,
                                   cup_up_world=list(upward),fixed_center_world=list(frame.Base),passed=passed))
    exchange=out/'FixedBearingParts.step';Part.makeCompound([byid[name]['shape'] for name in new_ids]).exportStep(str(exchange))
    loaded=Part.Shape();loaded.read(str(exchange));assert loaded.isValid() and len(loaded.Solids)==20
    passed=not overlaps and all(r['passed'] for r in interfaces)
    report=dict(complete=True,passed=passed,native_occurrences=len(items),new_occurrences=len(new_ids),
                new_catalogue_occurrences=12,new_in_situ_material_regions=8,new_source_counts=dict(counts),
                unchanged_prior_occurrences=len(before),material_candidate_pairs=len(pairs),overlaps=overlaps,
                interfaces=interfaces,bearing_local_interfaces_passed=all(r['passed'] for r in interfaces),
                dimensions=dimensions,native_sha256=sha(native),exchange_sha256=sha(exchange),
                exchange_roundtrip_solids=len(loaded.Solids),input_hashes=hashes,authored_fingerprint=lock,
                tank_native_hashes=build['native_hashes'],standard_assembly_modified=False,historical_fit_qualified=False,
                complete_frame_attachment=False,complete_cap_assembly=False,rendering_complete=False,visual_review_status='pending')
    write(out/'report.json',report)
    print('Fixed bearings:',len(pairs),'material pairs;',len(overlaps),'overlaps; passed=',passed,flush=True)
    for overlap in overlaps:print(overlap,flush=True)
    port=[i for i in items if i['id'].startswith(('PortTransmissionOutput','PortTransmissionBearing','PortFixedBearing')) or i['id']=='PortChain_TransmissionPinion']
    shaded(port,out/'fixed_bearings_oblique.svg',(1,1,.65),'Fixed transmission bearings | oil cups up, mounting feet aft')
    # Remove cap and its front lining in this inspection only, exposing the bearing saddle.
    opened=[i for i in port if not i['id'].startswith('PortFixedBearing') or i['id'].endswith(('_bracket','_lining_back'))]
    shaded(opened,out/'fixed_bearings_open.svg',(1,1,.8),'Bearing saddles | caps hidden for inspection')
    # Independent fixed frame section: do not unrotate the world by rotor phase.
    local=[];origin=App.Placement(rotor_frames['Port'].Base,App.Rotation())
    slab=Part.makeBox(850,800,.6,App.Vector(-500,-450,-.3));section=[]
    for item in port:
        shape=item['shape'].copy();shape.Placement=origin.inverse().multiply(shape.Placement)
        local.append(dict(item,shape=shape,target=SimpleNamespace(Shape=shape),definition=item['id']+'_fixed_local'))
        cut=shape.common(slab)
        if not cut.isNull() and cut.Faces:section.append(dict(item,shape=cut,target=SimpleNamespace(Shape=cut),definition=item['id']+'_section'))
    shaded(section,out/'fixed_bearings_section.svg',(0,0,1),'Fixed bearing axial section | inferred cast profiles and separate lining',up_direction=(-1,0,0))
    # Image up is aft (-X); this maps the fixed, unphased frame to Plate22.
    width,height=calibration['image_size_px'];scale=calibration['mm_per_pixel']
    bg=base64.b64encode((REPO/calibration['image']).read_bytes()).decode()
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
         f'<image width="{width}" height="{height}" href="data:image/png;base64,{bg}" opacity=".70"/>']
    for item in section:
        if not item['id'].startswith('PortFixedBearing'):continue
        color='#a400bd' if 'lining' in item['id'] else '#005ee8'
        for edge in item['shape'].Edges:
            points=' '.join(f'{calibration["sprocket_center_x_px"]-v.y/scale:.3f},{calibration["shaft_axis_y_px"]+v.x/scale:.3f}' for v in edge.discretize(Deflection=.2))
            svg.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2"/>')
    svg+=['<rect x="20" y="1040" width="1660" height="72" fill="white" opacity=".94"/>',
          '<text x="35" y="1065" font-family="sans-serif" font-size="20">Blue fixed castings; magenta poured lining. Retained four-inch hub scale; image up interpreted as aft.</text>',
          '<text x="35" y="1095" font-family="sans-serif" font-size="18">Approximate webs, caps and cups; vertical profiles, fittings, frame and feet remain incomplete.</text></svg>']
    (out/'source_support_overlay.svg').write_text('\n'.join(svg))
    import fitz
    with fitz.open(stream=(out/'source_support_overlay.svg').read_bytes(),filetype='svg') as drawing:
        drawing[0].get_pixmap().save(str(out/'source_support_overlay.png'))
    installed=[i for i in items if i['id'].startswith('Port') or i['id']=='hull_engine_back']
    shaded(installed,out/'support_case_context.svg',(1,1,.8),'Installed fixed bearing candidate | chain cases and rear bulkhead')
    # Isolate the actual interfering material instead of masking it in a busy assembly view.
    clashes=[];clash_context=[]
    for row in overlaps:
        if not row['a'].startswith('Port'):continue
        first=byid[row['a']];second=next(i for i in physical if i['id']==row['b'])
        intersection=first['shape'].common(second['shape'])
        clashes.append(dict(first,shape=intersection,target=SimpleNamespace(Shape=intersection),
                            definition=row['a']+'_'+row['b']+'_interference'))
        clash_context.extend([first,second])
    if clashes:
        shaded(clashes,out/'support_interference.svg',(1,1,.6),'Rejected interface | actual common material, supporting shapes in wire',context=clash_context)
    assert fingerprint()==lock and check_build(stage/'build')['native_hashes']==build['native_hashes']
    assert all(sha(ROOT/name)==digest for name,digest in hashes.items())
    report['rendering_complete']=True
    report['output_raster_hashes']={p.name:sha(p) for p in sorted(out.glob('*.png'))}
    write(out/'report.json',report)
    sys.exit(0 if passed else 1)
finally:
    runtime.close()
