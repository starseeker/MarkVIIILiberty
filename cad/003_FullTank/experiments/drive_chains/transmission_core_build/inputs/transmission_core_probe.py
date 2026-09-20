"""Install and inspect central transmission shells around the retained output train."""
import argparse
import base64
import json
from collections import Counter
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage',type=Path,required=True)
parser.add_argument('--output',type=Path,default=ROOT/'transmission_core_build')
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
    from lib.cad_build import leaves,metadata,shape_signature,COLORS
    from lib.worker import check_build,same_shape,placement_errors
    from lib.visual_review import shaded
    from transmission_core_parts import core_parts,box,cylinder

    lock=fingerprint();build=check_build(stage/'build')
    names=['transmission_core_probe.py','transmission_core_parts.py','transmission_core_controls.json',
           'transmission_core_sources.json','transmission_output_calibration.json','chain_candidate_controls.json',
           'transmission_output_parts.py','transmission_frame_parts.py','transmission_support_parts.py',
           'transmission_frame_controls.json','transmission_oil_build/report.json',
           'transmission_oil_build/visual_review.json','transmission_oil_build/TransmissionOilCandidate.FCStd']
    hashes={name:sha(ROOT/name) for name in names}
    for name in names:
        if '/' not in name:
            p=out/'inputs'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/name).read_bytes())
    source=read(ROOT/'transmission_core_sources.json')
    for name,digest in source['inspected_source_hashes'].items():assert sha(REPO/name)==digest
    c=read(ROOT/'transmission_core_controls.json')['controls']
    cal=read(ROOT/'transmission_output_calibration.json')
    chain={k:v['value'] for k,v in read(ROOT/'chain_candidate_controls.json')['controls'].items()}
    fc={k:v['value'] for k,v in read(ROOT/'transmission_frame_controls.json')['controls'].items()}
    prior=read(ROOT/'transmission_oil_build/report.json')
    assert prior['passed'] and prior['rendering_complete'] and prior['native_sha256']==hashes[names[-1]]
    assert prior['authored_fingerprint']==lock and prior['tank_native_hashes']==build['native_hashes']
    doc=App.openDocument(str(ROOT/names[-1]));doc.recompute();before=leaves(doc.Root)
    old={i['id']:i for i in before};signatures={i['id']:shape_signature(i['shape']) for i in before}
    rotor_frames={}
    for hand in ['Port','Starboard']:
        item=old[hand+'TransmissionOutput_shaft']
        rotor_frames[hand]=item['shape'].Placement.multiply(item['target'].Shape.Placement.inverse())
    origin=App.Vector(rotor_frames['Port'].Base.x,0,rotor_frames['Port'].Base.z)
    assert abs(rotor_frames['Port'].Base.y+rotor_frames['Starboard'].Base.y)<1e-7
    shaft_half=old['PortTransmissionOutput_shaft']['shape'].copy().cleaned().BoundBox.YMin
    frame=dict(rear=fc['frame_front_x']-origin.x,top=fc['top_web_z']-origin.z,
               bottom=fc['bottom_web_z']-origin.z,height=fc['channel_height'])
    shapes,dimensions=core_parts(c,cal,chain,shaft_half,rotor_frames['Port'].Base.y,frame)
    definitions={}
    for row in source['physical_inventory']:
        key=row['key'];body=doc.addObject('PartDesign::Body','Def_TransmissionCore_'+key)
        doc.Definitions.addObject(body);body.newObject('PartDesign::Feature','ReconstructedPart').Shape=shapes[key]
        metadata(body,DefinitionId='transmission_core_'+key,OriginalMark=row['mark'],SurveyIds=[row['part_id']],
                 SourceRecord=row['record_id'],Representation='assembly',Coverage='partial',
                 ReconstructionNotes='Source-section reconstruction; thickness, cast contours and interfaces partly inferred. See transmission_core_controls.json. Gears, bearings, fasteners and retention remain incomplete.')
        if key in ['bevel_case','bevel_cover']:
            metadata(body,SurfaceConstruction='Degree-three clamped B-spline outline, linear axial extrusion and scaled cavity; analytic input boss.',
                     ProfilePoles=c['bevel_outline_segments'],ParameterUpdate='Regenerate from versioned controls; no automatic live feature proxy.')
        definitions[key]=body
    assembly=doc.addObject('App::Part','TransmissionCore');doc.Root.addObject(assembly)
    assembly.Placement=App.Placement(origin,App.Rotation())
    metadata(assembly,Scope='Central bevel case and cover, single cross shaft, paired planetary cases, carriers and high-speed drums. Static partial reconstruction.')
    expected={};new_ids=[];key_for={}
    for hand in ['Center','Port','Starboard']:
        group=doc.addObject('App::Part',hand+'TransmissionCore');assembly.addObject(group)
        keys=['bevel_case','bevel_cover','cross_shaft'] if hand=='Center' else ['brake_case','plain_case','planet_disk','high_drum']
        for key in keys:
            name=hand+'TransmissionCore_'+key;link=doc.addObject('App::Link',name);group.addObject(link)
            link.setLink(definitions[key])
            rotation=(rotor_frames[hand].Rotation if key=='planet_disk' else
                      App.Rotation(App.Vector(1,0,0),180) if hand=='Starboard' else App.Rotation())
            link.LinkPlacement=App.Placement(App.Vector(),rotation)
            metadata(link,OccurrenceId=name,Subsystem='Drivetrain')
            expected[name]=assembly.Placement.multiply(link.LinkPlacement)
            new_ids.append(name);key_for[name]=key
    doc.Definitions.Visibility=False;doc.recompute();native=out/'TransmissionCoreCandidate.FCStd'
    doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items}
    assert len(items)==len(byid)==len(before)+sum(r['count'] for r in source['physical_inventory'])
    for item in items:
        assert item['shape'].isValid() and len(item['shape'].Solids)==1,item['id']
        if item['id'] in new_ids:
            t,r=placement_errors(item['shape'].Placement,expected[item['id']]);assert t<1e-6 and r<1e-8,item['id']
        else:assert same_shape(signatures[item['id']],shape_signature(item['shape'])),item['id']
    counts=Counter(pid for n in new_ids for pid in json.loads(byid[n]['target'].SurveyIds))
    assert dict(counts)=={r['part_id']:r['count'] for r in source['physical_inventory']}
    print('Reopened',len(items),'single-solid leaves;',len(before),'retained unchanged.',flush=True)
    tank=App.openDocument(build['build']['top_document']);tank.recompute()
    replaced={'hull_engine_back','PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting',
              'hull_port_inner_rear_end','hull_port_rear_wing','hull_starboard_inner_rear_end','hull_starboard_rear_wing'}
    context=[i for i in leaves(tank.Root) if i['id'] not in replaced and i['representation']=='assembly']
    physical=items+context;assert len({i['id'] for i in physical})==len(physical)
    boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].copy().cleaned().BoundBox for i in physical]])
    pairs=set();overlaps=[]
    for name in new_ids:
        a=byid[name]['shape'];b=a.copy().cleaned().BoundBox;bb=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
        near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
        for index in near:
            second=physical[index];pair=tuple(sorted([name,second['id']]))
            if pair[0]==pair[1] or pair in pairs:continue
            pairs.add(pair);intersection=a.common(second['shape']);volume=intersection.Volume
            if volume>1e-5:overlaps.append(dict(a=name,b=second['id'],volume_mm3=volume))
    interfaces=[]
    def distance(a,b,nominal=None):
        gap=byid[a]['shape'].distToShape(byid[b]['shape'])[0]
        interfaces.append(dict(a=a,b=b,gap_mm=gap,expected_mm=nominal,
                               passed=gap>=0 if nominal is None else abs(gap-nominal)<1e-5))
    for hand in ['Port','Starboard']:
        distance('CenterTransmissionCore_cross_shaft',hand+'TransmissionOutput_shaft',c['shaft_end_gap'])
        distance(hand+'TransmissionCore_planet_disk',hand+'TransmissionOutput_shaft')
        distance(hand+'TransmissionCore_planet_disk',hand+'TransmissionBearing_InnerRing',.2*cal['mm_per_pixel'])
        distance(hand+'TransmissionCore_plain_case',hand+'TransmissionCore_brake_case',2*cal['mm_per_pixel'])
        distance(hand+'TransmissionCore_high_drum','CenterTransmissionCore_cross_shaft')
    distance('CenterTransmissionCore_bevel_case','CenterTransmissionCore_bevel_cover',c['bevel_split_gap'])
    for end in ['Top','Bottom']:
        distance('CenterTransmissionCore_bevel_case','TransmissionFrame_'+end+'Channel',0)
    distance('CenterTransmissionCore_bevel_case','TransmissionFrame_MiddleDiaphragm')
    exchange=out/'TransmissionCoreParts.step';Part.makeCompound([byid[n]['shape'] for n in new_ids]).exportStep(str(exchange))
    imported=Part.Shape();imported.read(str(exchange));assert imported.isValid() and len(imported.Solids)==len(new_ids)
    # STEP roundtrip must retain each placed volume and bounding box, not only count.
    native_sorted=sorted([byid[n]['shape'].Solids[0] for n in new_ids],key=lambda s:(round(s.CenterOfMass.y,5),round(s.Volume,2)))
    step_sorted=sorted(imported.Solids,key=lambda s:(round(s.CenterOfMass.y,5),round(s.Volume,2)))
    for a,b in zip(native_sorted,step_sorted):
        assert abs(a.Volume-b.Volume)<max(1e-3,a.Volume*1e-8)
        assert (a.CenterOfMass-b.CenterOfMass).Length<1e-5
    passed=not overlaps and all(r['passed'] for r in interfaces)
    report=dict(complete=True,passed=passed,native_occurrences=len(items),new_occurrences=len(new_ids),unchanged_prior_occurrences=len(before),
        new_source_counts=dict(counts),material_candidate_pairs=len(pairs),overlaps=overlaps,interfaces=interfaces,
        dimensions=dimensions,shaft_axis_world_mm=[origin.x,origin.y,origin.z],output_center_y_mm=rotor_frames['Port'].Base.y,
        new_ids=new_ids,keys_by_id=key_for,expected_placements={n:dict(base=list(p.Base),quaternion=list(p.Rotation.Q)) for n,p in expected.items()},
        input_hashes=hashes,authored_fingerprint=lock,tank_native_hashes=build['native_hashes'],native_sha256=sha(native),
        exchange_sha256=sha(exchange),exchange_roundtrip_solids=len(imported.Solids),standard_assembly_modified=False,
        complete_transmission=False,historical_fit_qualified=False,gear_fit_qualified=False,rendering_complete=False)
    write(out/'report.json',report)
    print('Core material:',len(pairs),'pairs;',len(overlaps),'overlaps. Interface pass:',all(r['passed'] for r in interfaces),flush=True)
    for row in overlaps:print(row,flush=True)
    for row in interfaces:
        if not row['passed']:print('FAILED INTERFACE',row,flush=True)
    COLORS['CoreShell']=(.42,.55,.48);COLORS['CoreRotor']=(.64,.53,.35)
    def colored(item):
        return dict(item,system='CoreRotor' if key_for.get(item['id']) in ['planet_disk','cross_shaft','high_drum'] else 'CoreShell' if item['id'] in new_ids else item['system'])
    selected=[colored(i) for i in items if i['id'] in new_ids or i['id'].startswith(('TransmissionFrame_','PortFixedBearing_','StarboardFixedBearing_',
                'PortTransmissionOutput_','StarboardTransmissionOutput_','PortTransmissionBearing_','StarboardTransmissionBearing_'))
              or i['id'] in ['PortChain_TransmissionPinion','StarboardChain_TransmissionPinion']]
    shaded(selected,out/'transmission_core_oblique.svg',(1,1,.7),'Transmission shells and output train | gears and controls remain unpopulated')
    shaded([i for i in selected if i['id'] in new_ids],out/'core_parts.svg',(1,1,.6),'Seven source identities | separate housings, carrier disks, drums and cross shaft')
    section_items=[]
    for item in selected:
        b=item['shape'].copy().cleaned().BoundBox
        if b.ZMin>=origin.z:continue
        shape=item['shape'].common(box(b.XMin-1,b.XMax+1,b.YMin-1,b.YMax+1,b.ZMin-1,origin.z))
        if shape.isNull() or not shape.Solids:continue
        section_items.append(dict(item,definition=item['definition']+'_section_'+item['id'],shape=shape,target=SimpleNamespace(Shape=shape)))
    shaded(section_items,out/'core_horizontal_cutaway.svg',(1,1,1.2),'Horizontal cutaway | hollow shells, conical carriers, separate cross/output shafts')
    # Direct source overlay of the actual shaft-height section, using unchanged Plate22 scale.
    bg=base64.b64encode((REPO/cal['image']).read_bytes()).decode()
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1724" height="1147">',f'<image width="1724" height="1147" href="data:image/png;base64,{bg}" opacity=".63"/>']
    overlay_colors={'brake_case':'#b1261e','plain_case':'#006eb8','planet_disk':'#e07000','high_drum':'#93279e','cross_shaft':'#00823c','bevel_case':'#286fc0','bevel_cover':'#00a8a0'}
    plane=Part.makePlane(3000,3000,App.Vector(origin.x-1500,-1500,origin.z),App.Vector(0,0,1))
    for name in new_ids:
        if name.startswith('Starboard'):continue
        section=byid[name]['shape'].section(plane)
        for edge in section.Edges:
            points=[]
            for v in edge.discretize(Deflection=.4):
                px=cal['sprocket_center_x_px']-(v.y-rotor_frames['Port'].Base.y)/cal['mm_per_pixel']
                py=cal['shaft_axis_y_px']+(v.x-origin.x)/cal['mm_per_pixel']
                points.append(f'{px:.3f},{py:.3f}')
            svg.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{overlay_colors[key_for[name]]}" stroke-width="1.6"/>')
    svg+=['<rect x="24" y="1070" width="1675" height="66" fill="white"/>',
          '<text x="36" y="1096" font-family="sans-serif" font-size="17">Actual horizontal section. Unchanged local scale; printed high-speed drum diameter overrides scan extent.</text>',
          '<text x="36" y="1120" font-family="sans-serif" font-size="16">Red/blue planetary cases; orange carrier; purple high-speed drum; green cross shaft. Central placement is inferred.</text></svg>']
    path=out/'source_plate22_overlay.svg';path.write_text('\n'.join(svg))
    import fitz
    with fitz.open(stream=path.read_bytes(),filetype='svg') as drawing:drawing[0].get_pixmap().save(str(path.with_suffix('.png')))
    assert fingerprint()==lock and check_build(stage/'build')['native_hashes']==build['native_hashes']
    assert all(sha(ROOT/n)==digest for n,digest in hashes.items())
    report.update(rendering_complete=True,output_raster_hashes={p.name:sha(p) for p in out.glob('*.png')})
    write(out/'report.json',report)
    sys.exit(0 if passed else 1)
finally:runtime.close()
