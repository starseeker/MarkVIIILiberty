"""Install the transmission frame skeleton and revise provisional bracket webs."""
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
parser.add_argument('--output',type=Path,default=ROOT/'transmission_frame_clearance_build')
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
    from lib.model import load,point
    from transmission_frame_parts import frame_parts,revised_bracket,box

    lock=fingerprint();build=check_build(stage/'build');model=load()
    names=['transmission_frame_probe.py','transmission_frame_parts.py','transmission_frame_controls.json',
           'transmission_frame_research.json','transmission_support_parts.py','transmission_support_controls.json',
           'transmission_output_parts.py','transmission_output_calibration.json',
           'transmission_support_clearance_build/report.json','transmission_support_clearance_build/visual_review.json',
           'transmission_support_clearance_build/TransmissionSupportCandidate.FCStd']
    hashes={name:sha(ROOT/name) for name in names}
    for name in names:
        if '/' not in name:
            target=out/'inputs'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes())
    source=read(ROOT/'transmission_frame_research.json')
    for name,digest in source['inspected_source_hashes'].items():assert sha(REPO/name)==digest
    record=read(ROOT/'transmission_frame_controls.json');c={k:v['value'] for k,v in record['controls'].items()}
    support={k:v['value'] for k,v in read(ROOT/'transmission_support_controls.json')['controls'].items()}
    prior=read(ROOT/'transmission_support_clearance_build/report.json')
    assert prior['complete'] and prior['rendering_complete'] and prior['bearing_local_interfaces_passed']
    assert not prior['passed'] and len(prior['overlaps'])==4
    assert prior['native_sha256']==hashes[names[-1]] and prior['authored_fingerprint']==lock
    assert prior['tank_native_hashes']==build['native_hashes']
    doc=App.openDocument(str(ROOT/names[-1]));doc.recompute();before=leaves(doc.Root)
    old_signatures={i['id']:shape_signature(i['shape']) for i in before};old_byid={i['id']:i for i in before}
    frames={}
    for hand in ['Port','Starboard']:
        for role in ['inner','outer']:
            obj=old_byid[hand+'FixedBearing_'+role+'_bracket']
            frames[hand+role]=obj['shape'].Placement.multiply(obj['target'].Shape.Placement.inverse())
    changes={};changed_ids=[]
    for role in ['inner','outer']:
        target=old_byid['PortFixedBearing_'+role+'_bracket']['target']
        assert target==old_byid['StarboardFixedBearing_'+role+'_bracket']['target']
        revised,check=revised_bracket(target.Shape,role,c,support,prior['dimensions'],frames['Port'+role].Base)
        assert check['retained_saddle_difference_mm3']<1e-5,check
        target.Tip.Shape=revised;changes[role]=check
        metadata(target,ReconstructionNotes='Frame-constrained tapered web and upper/lower mounting pads; projected Plate22 footprint, inferred vertical profile. transmission_frame_controls.json')
        changed_ids.extend(hand+'FixedBearing_'+role+'_bracket' for hand in ['Port','Starboard'])
    shapes,installations,dimensions=frame_parts(c,frames['Portinner'].Base.y,frames['Portouter'].Base.y)
    identities={'top_channel':('M373','SNL:96:020'),'bottom_channel':('M374','SNL:96:019'),
                'middle_diaphragm':('M375','SNL:96:021'),'inner_angle_left':('M377','SNL:96:022'),
                'inner_angle_right':('M376','SNL:96:023'),'outer_angle':('M378','SNL:96:024'),
                'inner_gusset_left':('M380','SNL:96:025'),'inner_gusset_right':('M382','SNL:96:026'),
                'outer_gusset_left':('M384','SNL:97:001'),'outer_gusset_right':('M383','SNL:97:002')}
    definitions={};expected_counts={}
    for name,shape in shapes.items():
        mark,record_id=identities[name];row=next(r for r in source['rows'] if r['record_id']==record_id)
        ids=row['part_ids'];assert len(ids)==1
        body=doc.addObject('PartDesign::Body','Def_TransmissionFrame_'+name);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedPart').Shape=shape
        metadata(body,DefinitionId='transmission_frame_'+name,OriginalMark=mark,SurveyIds=ids,SourceRecord=record_id,
                 Representation='assembly',Coverage='partial',ReconstructionNotes='Conditional frame skeleton; member sections, joint forms and receivers incomplete. Exact controls/source snapshot preserved.')
        definitions[name]=body
        expected_counts[ids[0]]=sum(1 for key,pose in installations.values() if key==name)
    assembly=doc.addObject('App::Part','TransmissionMountingFrame');doc.Root.addObject(assembly)
    metadata(assembly,SourceRecord='SNL:96:015',Scope='Channels, diaphragm, angles and gussets; rivets, packers, holding hardware and brake suspension attachments pending')
    new_ids=[];expected_poses={}
    for suffix,(key,pose) in installations.items():
        name='TransmissionFrame_'+suffix
        link=doc.addObject('App::Link',name);assembly.addObject(link);link.setLink(definitions[key]);link.LinkPlacement=pose
        metadata(link,OccurrenceId=name,Subsystem='Drivetrain');new_ids.append(name)
        expected_poses[name]=pose.multiply(definitions[key].Shape.Placement)
    doc.Definitions.Visibility=False;doc.recompute()
    native=out/'TransmissionFrameCandidate.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items}
    assert len(items)==len(byid)==860
    for item in items:
        assert item['shape'].isValid() and len(item['shape'].Solids)==1,item['id']
        if item['id'] in new_ids:
            translation,rotation=placement_errors(item['shape'].Placement,expected_poses[item['id']])
            assert translation<1e-6 and rotation<1e-8,item['id']
        elif item['id'] not in changed_ids:assert same_shape(old_signatures[item['id']],shape_signature(item['shape'])),item['id']
    counts=Counter(pid for name in new_ids for pid in json.loads(byid[name]['target'].SurveyIds))
    assert dict(counts)==expected_counts
    tank=App.openDocument(build['build']['top_document']);tank.recompute()
    replaced={'hull_engine_back','PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting',
              'hull_port_inner_rear_end','hull_port_rear_wing','hull_starboard_inner_rear_end','hull_starboard_rear_wing'}
    context=[i for i in leaves(tank.Root) if i['id'] not in replaced and i['representation']=='assembly']
    physical=items+context;assert len({i['id'] for i in physical})==len(physical)
    boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].BoundBox for i in physical]])
    pairs=set();overlaps=[]
    for name in new_ids+changed_ids:
        first=byid[name];b=first['shape'].BoundBox;bb=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
        near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
        for index in near:
            second=physical[index];pair=tuple(sorted([name,second['id']]))
            if pair[0]==pair[1] or pair in pairs:continue
            pairs.add(pair);intersection=first['shape'].common(second['shape']);volume=intersection.Volume
            if volume>1e-5:
                b=intersection.BoundBox
                overlaps.append(dict(a=name,b=second['id'],volume_mm3=volume,
                                     world_bounds_mm=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]))
    contacts=[]
    def contact(a,b,expected=0):
        sa,sb=byid[a]['shape'],byid[b]['shape'];gap=sa.distToShape(sb)[0]
        contacts.append(dict(a=a,b=b,gap_mm=gap,expected_gap_mm=expected,passed=abs(gap-expected)<1e-5))
    for side in ['Left','Right']:
        for role in ['Inner','Outer']:
            angle='TransmissionFrame_'+side+role+'Angle'
            for end in ['Top','Bottom']:
                gusset='TransmissionFrame_'+side+role+end+'Gusset'
                contact(angle,gusset);contact(gusset,'TransmissionFrame_'+end+'Channel')
    for side in ['Left','Right']:contact('TransmissionFrame_MiddleDiaphragm','TransmissionFrame_'+side+'InnerAngle')
    bearing_checks=[];case_gaps=[]
    for hand in ['Port','Starboard']:
        for role in ['inner','outer']:
            prefix=hand+'FixedBearing_'+role+'_';bracket=byid[prefix+'bracket']['shape']
            contact(prefix+'bracket',prefix+'lining_back');contact(prefix+'bracket',prefix+'cap',2*support['split_gap'])
            for end in ['Top','Bottom']:
                contact(prefix+'bracket','TransmissionFrame_'+end+'Channel',changes[role]['required_inner_packing_gap_mm'])
            bearing_checks.append(dict(hand=hand,role=role,retained_saddle_difference_mm3=changes[role]['retained_saddle_difference_mm3']))
        case=byid[hand+'Casing_Body']['shape'];bracket=byid[hand+'FixedBearing_outer_bracket']['shape']
        gap=case.distToShape(bracket)[0]
        rivet=byid[hand+'CasingWall_WallRivet'+('05' if hand=='Port' else '01')]['shape']
        case_gaps.append(dict(hand=hand,case_gap_mm=gap,wall_rivet_gap_mm=bracket.distToShape(rivet)[0]))
    exchange=out/'FrameAndRevisedBrackets.step'
    Part.makeCompound([byid[name]['shape'] for name in new_ids+changed_ids]).exportStep(str(exchange))
    exported=Part.Shape();exported.read(str(exchange));assert exported.isValid() and len(exported.Solids)==19
    passed=not overlaps and all(r['passed'] for r in contacts)
    report=dict(complete=True,passed=passed,native_occurrences=len(items),new_frame_occurrences=len(new_ids),
                changed_bracket_occurrences=len(changed_ids),unchanged_prior_occurrences=len(before)-len(changed_ids),
                new_source_counts=dict(counts),material_candidate_pairs=len(pairs),overlaps=overlaps,contacts=contacts,
                retained_bearing_checks=bearing_checks,case_clearances=case_gaps,bracket_changes=changes,frame_dimensions=dimensions,
                native_sha256=sha(native),exchange_sha256=sha(exchange),exchange_roundtrip_solids=len(exported.Solids),
                input_hashes=hashes,authored_fingerprint=lock,tank_native_hashes=build['native_hashes'],
                standard_assembly_modified=False,historical_fit_qualified=False,complete_frame_attachment=False,
                frame_fasteners_and_packing_pending=True,central_bevel_case_clearance_qualified=False,
                rendering_complete=False,visual_review_status='pending')
    write(out/'report.json',report)
    print('Frame:',len(pairs),'material pairs;',len(overlaps),'overlaps; contacts=',all(r['passed'] for r in contacts),flush=True)
    for row in overlaps:print(row,flush=True)
    selected=[i for i in items if i['id'].startswith(('TransmissionFrame_','PortFixedBearing','StarboardFixedBearing',
                                                    'PortTransmissionOutput','StarboardTransmissionOutput','PortTransmissionBearing','StarboardTransmissionBearing'))
              or i['id'] in ['PortChain_TransmissionPinion','StarboardChain_TransmissionPinion']]
    shaded(selected,out/'transmission_frame_oblique.svg',(1,1,.7),'Transmission frame and bearing supports | partial cast and channel geometry')
    frame_only=[i for i in selected if i['id'].startswith(('TransmissionFrame_','PortFixedBearing','StarboardFixedBearing'))]
    shaded(frame_only,out/'frame_supports.svg',(1,.8,.6),'Frame members and revised bearing brackets | fasteners and packing pending')
    installed=selected+[i for i in items if i['id'].startswith('PortCasing') or i['id']=='hull_engine_back']
    shaded(installed,out/'frame_case_context.svg',(1,1,.8),'Frame in casing and bulkhead context | static installation study')
    # Side projection in the unchanged whole-tank source calibration.
    cal=model['calibrations']['snl_2'];origin=point(model,'snl_2',[0,0]);delta=point(model,'snl_2',[1,1]);sx,sz=delta[0]-origin[0],delta[1]-origin[1]
    bg=base64.b64encode((REPO/cal['image']).read_bytes()).decode()
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1900" height="750">',f'<image width="1900" height="750" href="data:image/png;base64,{bg}" opacity=".72"/>']
    for item in frame_only:
        if item['id'].startswith('Starboard'):continue
        color='#085dcc' if item['id'].startswith('TransmissionFrame') else '#bc3500'
        for edge in item['shape'].Edges:
            coords=' '.join(f'{(v.x-origin[0])/sx:.3f},{(v.z-origin[1])/sz:.3f}' for v in edge.discretize(Deflection=.7))
            svg.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="1"/>')
    svg+=['<rect x="920" y="675" width="960" height="55" fill="white"/>',
          '<text x="935" y="697" font-family="sans-serif" font-size="17">Blue frame; orange brackets. Source-calibrated channel planes; inferred cast vertical profiles.</text>',
          '<text x="935" y="719" font-family="sans-serif" font-size="16">Frame fasteners, packing and central bevel case remain unpopulated.</text></svg>']
    (out/'source_frame_overlay.svg').write_text('\n'.join(svg))
    import fitz
    with fitz.open(stream=(out/'source_frame_overlay.svg').read_bytes(),filetype='svg') as drawing:
        drawing[0].get_pixmap().save(str(out/'source_frame_overlay.png'))
    # Both the actual shaft-height section and projection are shown; do not
    # misrepresent the new, vertically separated feet as lying in the section.
    cal=read(ROOT/'transmission_output_calibration.json');scale=cal['mm_per_pixel'];bg=base64.b64encode((REPO/cal['image']).read_bytes()).decode()
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1724" height="1147">',f'<image width="1724" height="1147" href="data:image/png;base64,{bg}" opacity=".65"/>']
    origin=frames['Portouter'].Base;shaft_origin=App.Vector(origin.x,882.65,origin.z)
    for role in ['inner','outer']:
        item=byid['PortFixedBearing_'+role+'_bracket'];shape=item['shape'].copy();shape.translate(-shaft_origin)
        section=shape.common(box(-500,300,-500,400,-.3,.3))
        for obj,color,dash in [(shape,'#777777',' stroke-dasharray="5 4"'),(section,'#005de8','')]:
            for edge in obj.Edges:
                coords=' '.join(f'{cal["sprocket_center_x_px"]-v.y/scale:.3f},{cal["shaft_axis_y_px"]+v.x/scale:.3f}' for v in edge.discretize(Deflection=.5))
                svg.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="1.7"{dash}/>')
    svg+=['<rect x="20" y="1030" width="1680" height="90" fill="white"/>',
          '<text x="35" y="1058" font-family="sans-serif" font-size="19">Blue: native shaft-height section. Gray dashed: full bracket projection, including upper/lower pads.</text>',
          '<text x="35" y="1086" font-family="sans-serif" font-size="18">The broad source foot is interpreted as a projected outline; its exact section/vertical shape remains unresolved.</text>',
          '<text x="35" y="1110" font-family="sans-serif" font-size="17">Shaft centers and calibrated axial footprint retained; rear stem corner rounding and2.5mm end inset are assumptions.</text></svg>']
    (out/'source_bracket_projection.svg').write_text('\n'.join(svg))
    with fitz.open(stream=(out/'source_bracket_projection.svg').read_bytes(),filetype='svg') as drawing:
        drawing[0].get_pixmap().save(str(out/'source_bracket_projection.png'))
    assert fingerprint()==lock and check_build(stage/'build')['native_hashes']==build['native_hashes']
    assert all(sha(ROOT/name)==digest for name,digest in hashes.items())
    report['rendering_complete']=True;report['output_raster_hashes']={p.name:sha(p) for p in out.glob('*.png')};write(out/'report.json',report)
    sys.exit(0 if passed else 1)
finally:
    runtime.close()
