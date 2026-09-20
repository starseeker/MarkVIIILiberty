"""Populate four oil-cover hinges in the saved partial transmission candidate."""
import argparse
import base64
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage',type=Path,required=True)
parser.add_argument('--output',type=Path,default=ROOT/'transmission_lid_clearance_build')
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
    from lib.cad_build import leaves,metadata,shape_signature
    from lib.worker import check_build,same_shape,placement_errors
    from lib.visual_review import shaded
    from transmission_lid_parts import hinge

    lock=fingerprint();build=check_build(stage/'build')
    names=['transmission_lid_probe.py','transmission_lid_parts.py','transmission_lid_controls.json',
           'transmission_lid_sources.json','transmission_support_controls.json','transmission_support_parts.py',
           'transmission_output_parts.py','transmission_support_clearance_build/report.json',
           'transmission_frame_clearance_build/report.json','transmission_frame_clearance_build/sensitivity_checks.json',
           'transmission_frame_clearance_build/visual_review.json','transmission_frame_clearance_build/TransmissionFrameCandidate.FCStd']
    hashes={n:sha(ROOT/n) for n in names}
    for n in names:
        if '/' not in n:
            p=out/'inputs'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/n).read_bytes())
    source=read(ROOT/'transmission_lid_sources.json')
    for name,digest in source['inspected_source_hashes'].items():assert sha(REPO/name)==digest
    c={k:v['value'] for k,v in read(ROOT/'transmission_lid_controls.json')['controls'].items()}
    support={k:v['value'] for k,v in read(ROOT/'transmission_support_controls.json')['controls'].items()}
    dims=read(ROOT/'transmission_support_clearance_build/report.json')['dimensions']
    prior=read(ROOT/'transmission_frame_clearance_build/report.json')
    assert prior['passed'] and prior['rendering_complete'] and not prior['complete_frame_attachment']
    assert prior['native_sha256']==hashes[names[-1]] and prior['authored_fingerprint']==lock
    assert prior['tank_native_hashes']==build['native_hashes']
    doc=App.openDocument(str(ROOT/names[-1]));doc.recompute();before=leaves(doc.Root)
    byid={i['id']:i for i in before};signatures={i['id']:shape_signature(i['shape']) for i in before}
    lid_target=byid['PortFixedBearing_inner_lid']['target'];old_lid=lid_target.Shape.copy()
    generated={};dimensions={};undrilled={}
    for role in ['inner','outer']:
        cap=byid['PortFixedBearing_'+role+'_cap']['target']
        shapes,d,blank=hinge(cap.Shape,old_lid,dims[role],support,c)
        generated[role]=shapes;dimensions[role]=d;undrilled[role]=blank
        cap.Tip.Shape=shapes['cap']
        metadata(cap,ReconstructionNotes='Integral rear oil-cover hinge lugs; printed pin size, inferred hinge form. transmission_lid_controls.json. Cap studs/oil fittings still pending.')
    assert generated['inner']['lid'].cut(generated['outer']['lid']).Volume<1e-5
    assert generated['outer']['lid'].cut(generated['inner']['lid']).Volume<1e-5
    lid_target.Tip.Shape=generated['inner']['lid']
    metadata(lid_target,ReconstructionNotes='Common closed cover with integral central hinge knuckle; inferred segment widths and profile. Motion not qualified.')
    pin_row=next(r for r in source['rows'] if r['record_id']=='SNL:56:020')
    ids=pin_row['part_ids'];assert len(ids)==1
    definition=doc.addObject('PartDesign::Body','Def_TransmissionOilCoverPin');doc.Definitions.addObject(definition)
    definition.newObject('PartDesign::Feature','ReconstructedPin').Shape=generated['inner']['pin']
    metadata(definition,DefinitionId='transmission_oil_cover_pin',OriginalMark='',SurveyIds=ids,
             SourceRecord='SNL:56:020;SNL:56:029',Representation='assembly',Coverage='partial',
             ReconstructionNotes='Steel3/16 by2-1/2in pin. Straight cylinder; axial retention/end treatment undocumented.')
    changed=[];new=[];expected={};frames={}
    for hand in ['Port','Starboard']:
        for role in ['inner','outer']:
            prefix=hand+'FixedBearing_'+role+'_';item=byid[prefix+'cap']
            frame=item['shape'].Placement.multiply(item['target'].Shape.Placement.inverse())
            frames[hand+role]=frame
            group=doc.getObject(hand+role.title()+'FixedBearing');assert group is not None
            name=prefix+'cover_pin';link=doc.addObject('App::Link',name);group.addObject(link);link.setLink(definition)
            link.LinkPlacement=App.Placement(App.Vector(*dimensions[role]['hinge_axis_in_cap_mm']),App.Rotation())
            metadata(link,OccurrenceId=name,Subsystem='Drivetrain');new.append(name)
            expected[name]=frame.multiply(link.LinkPlacement)
            changed.extend([prefix+'cap',prefix+'lid'])
    doc.Definitions.Visibility=False;doc.recompute()
    native=out/'TransmissionLidCandidate.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items}
    assert len(items)==len(byid)==len(before)+4
    for item in items:
        assert item['shape'].isValid() and len(item['shape'].Solids)==1,item['id']
        if item['id'] in new:
            t,r=placement_errors(item['shape'].Placement,expected[item['id']]);assert t<1e-6 and r<1e-8
            assert json.loads(item['target'].SurveyIds)==ids
            pin_shape=item['target'].Shape
            surfaces=[f.Surface for f in pin_shape.Faces if isinstance(f.Surface,Part.Cylinder)]
            assert len(surfaces)==1 and abs(2*surfaces[0].Radius-c['pin_diameter'])<1e-6
            assert abs(pin_shape.Volume-math.pi*(c['pin_diameter']/2)**2*c['pin_length'])<1e-6
            assert abs(pin_shape.copy().cleaned().BoundBox.YLength-c['pin_length'])<1e-6
        elif item['id'] not in changed:assert same_shape(signatures[item['id']],shape_signature(item['shape'])),item['id']
    tank=App.openDocument(build['build']['top_document']);tank.recompute()
    replaced={'hull_engine_back','PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting',
              'hull_port_inner_rear_end','hull_port_rear_wing','hull_starboard_inner_rear_end','hull_starboard_rear_wing'}
    context=[i for i in leaves(tank.Root) if i['id'] not in replaced and i['representation']=='assembly']
    physical=items+context;assert len({i['id'] for i in physical})==len(physical)
    # Discard tessellation caches: a display mesh may underbound a cylinder.
    boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].copy().cleaned().BoundBox for i in physical]])
    pairs=set();overlaps=[]
    for name in new+changed:
        a=byid[name]['shape'];b=a.copy().cleaned().BoundBox;bb=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
        near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
        for index in near:
            second=physical[index];pair=tuple(sorted([name,second['id']]))
            if pair[0]==pair[1] or pair in pairs:continue
            pairs.add(pair);volume=a.common(second['shape']).Volume
            if volume>1e-5:overlaps.append(dict(a=name,b=second['id'],volume_mm3=volume))
    interfaces=[]
    for hand in ['Port','Starboard']:
        for role in ['inner','outer']:
            prefix=hand+'FixedBearing_'+role+'_';pin=byid[prefix+'cover_pin']['shape']
            cap=byid[prefix+'cap']['shape'];lid=byid[prefix+'lid']['shape']
            gaps=[pin.distToShape(s)[0] for s in [cap,lid]]
            witness=pin.copy();witness.translate(App.Vector(c['radial_witness_shift'],0,0))
            shifted=[witness.common(s).Volume for s in [cap,lid]]
            negatives=[]
            for component in ['cap','lid']:
                blank=undrilled[role][component].copy()
                pose=frames[hand+role]
                if component=='lid':pose=pose.multiply(App.Placement(App.Vector(dims[role]['cup_back_x_mm'],0,dims[role]['cup_top_z_mm']+support['lid_gap']),App.Rotation()))
                blank.Placement=pose.multiply(blank.Placement);negatives.append(pin.common(blank).Volume)
            cap_lid=cap.distToShape(lid)[0]
            lining_gap=cap.distToShape(byid[prefix+'lining_front']['shape'])[0]
            split=cap.distToShape(byid[prefix+'bracket']['shape'])[0]
            passed=(all(abs(g-c['pin_radial_gap'])<1e-5 for g in gaps)
                    and all(v>1 for v in shifted+negatives) and cap_lid>=support['lid_gap']-1e-5
                    and lining_gap<1e-5 and abs(split-2*support['split_gap'])<1e-5)
            interfaces.append(dict(hand=hand,role=role,pin_bore_gaps_mm=gaps,cap_lid_gap_mm=cap_lid,
                                   shifted_pin_overlaps_mm3=shifted,undrilled_receiver_overlaps_mm3=negatives,
                                   cap_lining_seat_gap_mm=lining_gap,cap_bracket_split_mm=split,passed=passed))
    exchange=out/'OilCoverHinges.step';Part.makeCompound([byid[n]['shape'] for n in new+changed]).exportStep(str(exchange))
    imported=Part.Shape();imported.read(str(exchange));assert imported.isValid() and len(imported.Solids)==12
    passed=not overlaps and all(i['passed'] for i in interfaces)
    report=dict(complete=True,passed=passed,native_occurrences=len(items),new_pin_occurrences=4,
                changed_cap_and_lid_occurrences=8,unchanged_prior_occurrences=len(before)-8,
                new_source_counts={ids[0]:4},material_candidate_pairs=len(pairs),overlaps=overlaps,
                hinge_interfaces=interfaces,dimensions=dimensions,input_hashes=hashes,authored_fingerprint=lock,
                tank_native_hashes=build['native_hashes'],native_sha256=sha(native),exchange_sha256=sha(exchange),
                exchange_roundtrip_solids=len(imported.Solids),standard_assembly_modified=False,
                material_filter='BRep bounds after removing triangulation caches',
                printed_pin_dimensions_verified='Analytic cylinder diameter, exact solid volume and cleaned axial bounds',
                historical_fit_qualified=False,pin_axial_retention_qualified=False,lid_motion_qualified=False,
                frame_attachment_and_parameter_qualification_inherited_incomplete=True,rendering_complete=False)
    write(out/'report.json',report)
    print('Oil cover hinges:',len(pairs),'material pairs;',len(overlaps),'overlaps; interfaces=',all(i['passed'] for i in interfaces),flush=True)
    for row in overlaps:print(row,flush=True)
    for row in interfaces:print(row,flush=True)
    selected=[i for i in items if i['id'].startswith('PortFixedBearing_outer_')]
    shaded(selected,out/'oil_cover_hinge.svg',(1,1,.8),'Closed oil-cover hinge | source-size steel pin, inferred integral lugs')
    opened=[i for i in selected if not i['id'].endswith('_lid')]
    shaded(opened,out/'hinge_receivers.svg',(1,.6,1),'Hinge receiving lugs | cover omitted for inspection; standard placement unchanged')
    bearing_only=[i for i in items if i['id'].startswith(('PortFixedBearing','StarboardFixedBearing'))]
    shaded(bearing_only,out/'four_closed_bearings.svg',(1,1,.6),'Four fixed bearings with closed hinged covers | studs and oil fittings pending')
    # Source crop is only an illustration comparison, never a dimensional calibration.
    source_path=REPO/'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/original_scans/MarkVIII011.jpg'
    source_data=base64.b64encode(source_path.read_bytes()).decode()
    native_data=base64.b64encode((out/'oil_cover_hinge.png').read_bytes()).decode()
    svg=('<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900">'
         '<rect width="1600" height="900" fill="#f6f4ed"/>'
         '<text x="30" y="36" font-family="sans-serif" font-size="24">Oil-cup cover hinge | handbook illustration and closed native candidate</text>'
         '<svg x="30" y="80" width="610" height="690" viewBox="240 680 510 535">'
         f'<image width="1849" height="1343" href="data:image/jpeg;base64,{source_data}"/></svg>'
         f'<image x="630" y="160" width="950" height="535" href="data:image/png;base64,{native_data}"/>'
         '<text x="30" y="800" font-family="sans-serif" font-size="19">HB20 Plate11 shows the rear hinge and an open lid. Native model remains closed; views are not registered.</text>'
         '<text x="30" y="831" font-family="sans-serif" font-size="19">Only the steel pin diameter and length are printed:3/16 x2-1/2in (SNL56). Lug and cover forms are inferred.</text>'
         '<text x="30" y="862" font-family="sans-serif" font-size="19">Cast blends, pin axial retention, cap studs/nuts, oil fittings and passages remain incomplete.</text></svg>')
    (out/'source_hinge_comparison.svg').write_text(svg)
    import fitz
    with fitz.open(stream=svg.encode(),filetype='svg') as drawing:drawing[0].get_pixmap().save(str(out/'source_hinge_comparison.png'))
    assert fingerprint()==lock and check_build(stage/'build')['native_hashes']==build['native_hashes']
    assert all(sha(ROOT/n)==digest for n,digest in hashes.items())
    report.update(rendering_complete=True,output_raster_hashes={p.name:sha(p) for p in out.glob('*.png')})
    write(out/'report.json',report)
    sys.exit(0 if passed else 1)
finally:
    runtime.close()
