"""Install output sleeves/dowels and source-counted shaft rings in saved context."""
import argparse
import base64
import json
from collections import Counter
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage',type=Path,required=True)
parser.add_argument('--output',type=Path,default=ROOT/'transmission_bush_build')
parser.add_argument('--worker',action='store_true')
args=parser.parse_args(); stage=args.stage.resolve();out=args.output.resolve()
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
    from transmission_bush_parts import parts

    lock=fingerprint();build=check_build(stage/'build')
    names=['transmission_bush_probe.py','transmission_bush_parts.py','transmission_bush_controls.json',
           'transmission_bush_sources.json','transmission_output_parts.py','transmission_output_controls.json',
           'transmission_output_calibration.json','transmission_output_build/report.json',
           'casing_front_build/report.json','casing_front_build/CasingFrontCandidate.FCStd']
    hashes={name:sha(ROOT/name) for name in names}
    for name in names:
        if '/' not in name:
            target=out/'inputs'/name;target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes((ROOT/name).read_bytes())
    source=read(ROOT/'transmission_bush_sources.json')
    for name,digest in source['inspected_source_hashes'].items():assert sha(REPO/name)==digest
    controls_record=read(ROOT/'transmission_bush_controls.json')
    controls={k:v['value'] for k,v in controls_record['controls'].items()}
    rotor={k:v['value'] for k,v in read(ROOT/'transmission_output_controls.json')['controls'].items()}
    calibration=read(ROOT/'transmission_output_calibration.json')
    prior=read(ROOT/'casing_front_build/report.json')
    assert prior['passed'] and prior['rendering_complete']
    assert prior['native_sha256']==hashes[names[-1]]
    assert prior['authored_fingerprint']==lock and prior['tank_native_hashes']==build['native_hashes']
    doc=App.openDocument(str(ROOT/names[-1]));doc.recompute();before=leaves(doc.Root)
    original_signatures={i['id']:shape_signature(i['shape']) for i in before}
    shaft_target=next(i['target'] for i in before if i['id']=='PortTransmissionOutput_shaft')
    assert shaft_target==next(i['target'] for i in before if i['id']=='StarboardTransmissionOutput_shaft')
    old_shaft=shaft_target.Shape.copy()
    shaft_dimensions=read(ROOT/'transmission_output_build/report.json')['dimensions']
    revised,shapes,dimensions=parts(old_shaft,shaft_dimensions,rotor,controls,
                                   controls_record['conditional_image_picks'],calibration)
    assert revised.cut(old_shaft).Volume<1e-5
    assert old_shaft.Volume>revised.Volume
    shaft_target.Tip.Shape=revised
    metadata(shaft_target,ReconstructionNotes='Output shaft with inferred retaining grooves and blind sleeve-dowel pockets; exact inputs preserved.')
    definitions={};source_by_role={}
    for role,mark,record in [('inner_bush','M296','SNL:44:018'),('outer_bush','M299','SNL:44:022'),
                             ('dowel','M300','SNL:44:019'),('ring','M290','SNL:165:013')]:
        row=next(r for r in source['rows'] if r['record_id']==record)
        assert len(row['part_ids'])==1
        source_by_role[role]=row['part_ids'][0]
        body=doc.addObject('PartDesign::Body','Def_Output_'+role);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedPart').Shape=shapes[role]
        metadata(body,DefinitionId='transmission_output_'+role,OriginalMark=mark,SurveyIds=row['part_ids'],
                 SourceRecord=record,Representation='assembly',Coverage='partial',
                 ReconstructionNotes='Conditional drawing scale; shaft-mounted sleeve hypothesis; source dimensions and assumptions in transmission_bush_controls.json')
        definitions[role]=body
    expected_poses={};new_ids=[];rotor_poses={}
    def instance(group,hand,suffix,role,local):
        name=hand+'TransmissionBearing_'+suffix
        pose=rotor_poses[hand].multiply(local)
        obj=doc.addObject('App::Link',name);group.addObject(obj);obj.setLink(definitions[role]);obj.LinkPlacement=pose
        metadata(obj,OccurrenceId=name,Subsystem='Drivetrain')
        expected_poses[name]=pose.multiply(definitions[role].Shape.Placement);new_ids.append(name)
    for hand in ['Port','Starboard']:
        shaft=next(i for i in before if i['id']==hand+'TransmissionOutput_shaft')
        rotor_poses[hand]=shaft['shape'].Placement.multiply(shaft['target'].Shape.Placement.inverse())
        group=doc.getObject(hand+'TransmissionOutput')
        for setting in dimensions['installations']:
            role=setting['role'];name=role.title();axial=setting['center_y_mm']
            assembly=doc.addObject('App::Part',hand+name+'OutputSleeve');group.addObject(assembly)
            metadata(assembly,SourceRecord='SNL:44:016' if role=='inner' else 'SNL:44:020',
                     Scope='One source bush and one M300 dowel; fixed housing and lining separate')
            instance(assembly,hand,name+'Bush',role+'_bush',App.Placement(App.Vector(0,axial,0),App.Rotation()))
            instance(assembly,hand,name+'Dowel','dowel',App.Placement(App.Vector(setting['dowel_start_x_mm'],axial,0),App.Rotation()))
        for suffix,axial in zip(['OuterRing','InnerRing'],dimensions['ring_stations_local_y_mm']):
            instance(group,hand,suffix,'ring',App.Placement(App.Vector(0,axial,0),App.Rotation()))
    metadata(doc.Root,Scope='Chain/casing/output rotors with separate sleeves, dowels and retaining rings; fixed bearing supports and linings pending')
    doc.Definitions.Visibility=False;doc.recompute()
    native=out/'TransmissionBushCandidate.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items}
    assert len(items)==len(byid)==825
    changed=set(new_ids)|{h+'TransmissionOutput_shaft' for h in ['Port','Starboard']}
    for item in items:
        assert item['shape'].isValid() and len(item['shape'].Solids)==1,item['id']
        if item['id'] in new_ids:
            translation,rotation=placement_errors(item['shape'].Placement,expected_poses[item['id']])
            assert translation<1e-6 and rotation<1e-8,item['id']
        elif item['id'] not in changed:
            assert same_shape(original_signatures[item['id']],shape_signature(item['shape'])),item['id']
    counts=Counter(pid for name in new_ids for pid in json.loads(byid[name]['target'].SurveyIds))
    assert dict(counts)=={source_by_role['inner_bush']:2,source_by_role['outer_bush']:2,
                          source_by_role['dowel']:4,source_by_role['ring']:4}
    tank=App.openDocument(build['build']['top_document']);tank.recompute()
    replaced={'hull_engine_back','PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting',
              'hull_port_inner_rear_end','hull_port_rear_wing','hull_starboard_inner_rear_end','hull_starboard_rear_wing'}
    context=[i for i in leaves(tank.Root) if i['id'] not in replaced and i['representation']=='assembly']
    physical=items+context
    assert len({i['id'] for i in physical})==len(physical)
    boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].BoundBox for i in physical]])
    pairs=set();overlaps=[]
    for name in sorted(changed):
        first=byid[name];b=first['shape'].BoundBox
        box=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
        near=np.where(np.all(boxes[:,:3]<=box[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=box[:3]-1e-7,axis=1))[0]
        for index in near:
            second=physical[index];pair=tuple(sorted([name,second['id']]))
            if pair[0]==pair[1] or pair in pairs:continue
            pairs.add(pair);volume=first['shape'].common(second['shape']).Volume
            if volume>1e-5:overlaps.append(dict(a=name,b=second['id'],volume_mm3=volume))
    journal_checks=[];dowel_checks=[];ring_checks=[]
    for hand in ['Port','Starboard']:
        shaft=byid[hand+'TransmissionOutput_shaft']['shape'];pose=rotor_poses[hand]
        uncut=old_shaft.copy();uncut.Placement=pose.multiply(uncut.Placement)
        for setting in dimensions['installations']:
            role=setting['role'];prefix=hand+'TransmissionBearing_'+role.title()
            bush=byid[prefix+'Bush'];pin=byid[prefix+'Dowel']['shape']
            gap=shaft.distToShape(bush['shape'])[0]
            journal_checks.append(dict(hand=hand,role=role,radial_gap_mm=gap,
                                       passed=abs(gap-controls['journal_radial_gap'])<1e-5))
            twisted=bush['target'].Shape.copy();twisted.rotate(App.Vector(),App.Vector(0,1,0),controls['dowel_twist_witness'])
            local_pose=pose.multiply(App.Placement(App.Vector(0,setting['center_y_mm'],0),App.Rotation()))
            twisted.Placement=local_pose.multiply(twisted.Placement)
            pulled=bush['shape'].copy();pulled.translate(pose.Rotation.multVec(App.Vector(0,controls['dowel_axial_witness'],0)))
            twist_capture=pin.common(twisted).Volume;axial_capture=pin.common(pulled).Volume
            shaft_clearance=pin.distToShape(shaft)[0];bush_clearance=pin.distToShape(bush['shape'])[0]
            negative=shaft.common(twisted).Volume
            # Restoring the undrilled shaft must reject the installed pin.
            uncut_clash=pin.common(uncut).Volume
            passed=(abs(shaft_clearance-controls['dowel_hole_radial_gap'])<1e-5
                    and abs(bush_clearance-controls['dowel_hole_radial_gap'])<1e-5
                    and twist_capture>1 and axial_capture>1 and negative<1e-5 and uncut_clash>1)
            dowel_checks.append(dict(hand=hand,role=role,shaft_clearance_mm=shaft_clearance,bush_clearance_mm=bush_clearance,
                                     twist_capture_mm3=twist_capture,axial_capture_mm3=axial_capture,
                                     no_dowel_twist_negative_mm3=negative,undrilled_shaft_negative_mm3=uncut_clash,passed=passed))
        for suffix in ['OuterRing','InnerRing']:
            ring=byid[hand+'TransmissionBearing_'+suffix]['shape']
            captures=[]
            for sign in [-1,1]:
                moved=ring.copy();moved.translate(pose.Rotation.multVec(App.Vector(0,sign*controls['retention_translation_witness'],0)))
                captures.append(moved.common(shaft).Volume)
            gap=ring.distToShape(shaft)[0];negative=ring.common(uncut).Volume
            ring_checks.append(dict(hand=hand,role=suffix,groove_clearance_mm=gap,axial_capture_mm3=captures,
                                    ungrooved_shaft_negative_mm3=negative,
                                    passed=gap>0 and all(v>1 for v in captures) and negative>1))
    passed=not overlaps and all(r['passed'] for r in journal_checks+dowel_checks+ring_checks)
    report=dict(complete=True,passed=passed,native_occurrences=len(items),new_occurrences=len(new_ids),
                new_source_counts=dict(counts),unchanged_prior_occurrences=811,
                material_candidate_pairs=len(pairs),overlaps=overlaps,journal_checks=journal_checks,
                dowel_checks=dowel_checks,ring_checks=ring_checks,dimensions=dimensions,
                shaft_change_removes_material_only=True,shaft_removed_volume_mm3=old_shaft.Volume-revised.Volume,
                native_sha256=sha(native),input_hashes=hashes,authored_fingerprint=lock,tank_native_hashes=build['native_hashes'],
                interface_hypothesis=controls_record['interface_hypothesis'],
                fixed_bearing_supports_and_linings_populated=False,complete_axial_stack_qualified=False,
                standard_assembly_modified=False,historical_fit_qualified=False,
                rendering_complete=False,visual_review_status='pending')
    write(out/'report.json',report)
    print('Output sleeves/rings:',len(pairs),'material pairs;',len(overlaps),'overlaps; passed=',passed,flush=True)
    port=[i for i in items if i['id'].startswith(('PortTransmissionOutput','PortTransmissionBearing'))
          or i['id']=='PortChain_TransmissionPinion']
    shaded(port,out/'output_bush_oblique.svg',(1,1,.65),'Output sleeves, dowels and retaining rings | partial bearing interfaces')
    local=[]
    for item in port:
        shape=item['shape'].copy();shape.Placement=rotor_poses['Port'].inverse().multiply(shape.Placement)
        local.append(dict(item,shape=shape,target=SimpleNamespace(Shape=shape),definition=item['id']+'_local'))
    slab=Part.makeBox(700,700,.6,App.Vector(-350,-430,-.3));section=[]
    for item in local:
        cut=item['shape'].common(slab)
        if not cut.isNull() and cut.Faces:
            section.append(dict(item,shape=cut,target=SimpleNamespace(Shape=cut),definition=item['id']+'_section'))
    shaded(section,out/'output_bush_section.svg',(0,0,1),'Native axial section | sleeve dowels and inferred shaft grooves',up_direction=(1,0,0))
    width,height=calibration['image_size_px'];scale=calibration['mm_per_pixel']
    bg=base64.b64encode((REPO/calibration['image']).read_bytes()).decode()
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
         f'<image width="{width}" height="{height}" href="data:image/png;base64,{bg}" opacity=".75"/>']
    for item in section:
        color='#0062d6' if item['id'].endswith('shaft') else '#b24400' if item['id'].endswith('drum') else '#00864c'
        for edge in item['shape'].Edges:
            points=' '.join(f'{calibration["sprocket_center_x_px"]-v.y/scale:.3f},{calibration["shaft_axis_y_px"]-v.x/scale:.3f}' for v in edge.discretize(Deflection=.2))
            svg.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2"/>')
    svg+=['<rect x="20" y="1040" width="1660" height="72" fill="white" opacity=".94"/>',
          '<text x="35" y="1065" font-family="sans-serif" font-size="20">Blue shaft; orange drum; green sleeves/rings/sprocket. Four-inch hub scale retained.</text>',
          '<text x="35" y="1095" font-family="sans-serif" font-size="18">Dowel direction, profiles and groove dimensions inferred; fixed brackets and lining remain pending.</text></svg>']
    (out/'source_bush_overlay.svg').write_text('\n'.join(svg))
    import fitz
    with fitz.open(stream=(out/'source_bush_overlay.svg').read_bytes(),filetype='svg') as drawing:
        drawing[0].get_pixmap().save(str(out/'source_bush_overlay.png'))
    assert fingerprint()==lock;check_build(stage/'build')
    assert all(sha(ROOT/name)==digest for name,digest in hashes.items())
    report['rendering_complete']=True;write(out/'report.json',report)
    sys.exit(0 if passed else 1)
finally:
    runtime.close()
