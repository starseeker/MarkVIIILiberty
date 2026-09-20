"""Install the large epicyclic gears and their case/shaft receivers on both sides."""
import argparse
import base64
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
parser.add_argument('--output',type=Path,default=ROOT/'transmission_planet_build')
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
    from transmission_planet_parts import planet_parts,case_and_shaft_receivers
    from transmission_core_parts import box

    lock=fingerprint();build=check_build(stage/'build')
    names=['transmission_planet_probe.py','transmission_planet_parts.py','transmission_planet_controls.json',
           'transmission_planet_sources.json','transmission_core_parts.py','transmission_core_controls.json',
           'transmission_output_calibration.json','transmission_core_build/report.json',
           'transmission_core_build/visual_review.json','transmission_core_build/TransmissionCoreCandidate.FCStd']
    hashes={name:sha(ROOT/name) for name in names}
    for name in names:
        if '/' not in name:
            path=out/'inputs'/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((ROOT/name).read_bytes())
    source=read(ROOT/'transmission_planet_sources.json')
    for name,digest in source['inspected_source_hashes'].items():assert sha(REPO/name)==digest
    c={k:v['value'] for k,v in read(ROOT/'transmission_planet_controls.json')['controls'].items()}
    core=read(ROOT/'transmission_core_controls.json')['controls'];cal=read(ROOT/'transmission_output_calibration.json')
    prior=read(ROOT/'transmission_core_build/report.json')
    assert prior['passed'] and prior['rendering_complete'] and prior['native_sha256']==hashes[names[-1]]
    assert prior['authored_fingerprint']==lock and prior['tank_native_hashes']==build['native_hashes']
    doc=App.openDocument(str(ROOT/names[-1]));doc.recompute();before=leaves(doc.Root)
    old={i['id']:i for i in before};signatures={i['id']:shape_signature(i['shape']) for i in before}
    origin=App.Vector(*prior['shaft_axis_world_mm'])
    replaced_shapes={k:old[('Center' if k=='cross_shaft' else 'Port')+'TransmissionCore_'+k]['target'].Shape.copy()
                     for k in ['brake_case','plain_case','cross_shaft']}
    carrier=old['PortTransmissionCore_planet_disk']
    dimensions_in=dict(carrier_inner_y=carrier['target'].Shape.copy().cleaned().BoundBox.YMin,
        carrier_outer_y=carrier['target'].Shape.copy().cleaned().BoundBox.YMax,
        shaft_half_length=prior['dimensions']['cross_shaft_half_length_mm'],
        output_bush_inner_y=old['PortTransmissionBearing_InnerBush']['shape'].copy().cleaned().BoundBox.YMin,
        brake_case_inner_y=replaced_shapes['brake_case'].BoundBox.YMin,
        plain_case_outer_y=replaced_shapes['plain_case'].BoundBox.YMax,
        brake_case_lip_radius=prior['dimensions']['profiles_radial_axial_mm']['brake_case'][2][0])
    shapes,dimensions=planet_parts(c,core,cal,dimensions_in)
    receivers=case_and_shaft_receivers(replaced_shapes,c,dimensions)
    changed_ids=[]
    for key,shape in receivers.items():
        target=old[('Center' if key=='cross_shaft' else 'Port')+'TransmissionCore_'+key]['target']
        target.Tip.Shape=shape
        metadata(target,ReceiverRevision='Large planetary gear seats and cross-shaft retaining grooves; see transmission_planet_controls.json.')
        changed_ids.extend([i['id'] for i in before if i['target']==target])
    definitions={}
    for row in source['physical_inventory']:
        key=row['key'];body=doc.addObject('PartDesign::Body','Def_TransmissionPlanet_'+key)
        doc.Definitions.addObject(body);body.newObject('PartDesign::Feature','ReconstructedPart').Shape=shapes[key]
        metadata(body,DefinitionId='transmission_planet_'+key,OriginalMark=row['mark'],SurveyIds=[row['part_id']],
                 SourceRecord=row['record_id'],Representation='assembly',Coverage='partial',
                 ReconstructionNotes='Printed gear counts and two-pitch designation; inferred pressure angle, fits, axial stack and receiver details. Pins, bushings and fastening remain pending.',
                 ParameterUpdate='Regenerate from versioned transmission_planet_controls.json; no live feature proxy.')
        if key in dimensions['tooth_profiles']:
            metadata(body,ToothConstruction='Analytic involute samples interpolated by cubic B-splines, axial extrusion; radial root continuation and omitted cutter fillets.',
                     ToothProfile=dimensions['tooth_profiles'][key])
        definitions[key]=body
    new_ids=[];key_for={};expected={};hand_phases={}
    for hand in ['Port','Starboard']:
        hand_rotation=App.Rotation(App.Vector(1,0,0),180) if hand=='Starboard' else App.Rotation()
        rotor=old[hand+'TransmissionCore_planet_disk']
        frame=rotor['shape'].Placement.multiply(rotor['target'].Shape.Placement.inverse())
        local=hand_rotation.inverted().multiply(frame.Rotation)
        vector=local.multVec(App.Vector(1,0,0));phase=math.atan2(vector.z,vector.x)
        hand_phases[hand]=phase
        group=doc.addObject('App::Part',hand+'PlanetTrain');doc.getObject(hand+'TransmissionCore').addObject(group)
        group.Placement=App.Placement(App.Vector(),hand_rotation)
        metadata(group,Scope='Large epicyclic train: three planets, one sun, ring, retainer, washer and two gaskets. Static assembly; pin supports pending.')
        def install(key,suffix='',translation=None,angle=0):
            name=hand+'PlanetTrain_'+key+suffix;link=doc.addObject('App::Link',name);group.addObject(link)
            link.setLink(definitions[key])
            link.LinkPlacement=App.Placement(translation or App.Vector(),App.Rotation(App.Vector(0,1,0),-math.degrees(angle)))
            metadata(link,OccurrenceId=name,Subsystem='Drivetrain')
            expected[name]=doc.TransmissionCore.Placement.multiply(group.Placement).multiply(link.LinkPlacement)
            new_ids.append(name);key_for[name]=key
        install('sun');install('washer')
        install('ring',angle=(c['teeth_sun']+c['teeth_ring'])/c['teeth_ring']*phase)
        install('retainer',translation=App.Vector(0,dimensions['retainer_center_y_mm'],0))
        for n,y in enumerate(dimensions['gasket_y_mm']):install('gasket',str(n),App.Vector(0,y,0))
        for n in range(c['planets_per_side']):
            beta=phase+2*math.pi*n/c['planets_per_side'];r=dimensions['planet_center_radius_mm']
            install('planet',str(n),App.Vector(r*math.cos(beta),0,r*math.sin(beta)),
                    (c['teeth_sun']+c['teeth_planet'])/c['teeth_planet']*beta)
    doc.Definitions.Visibility=False;doc.recompute();native=out/'TransmissionPlanetCandidate.FCStd'
    doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items}
    assert len(items)==len(byid)==len(before)+sum(r['count'] for r in source['physical_inventory'])
    for item in items:
        assert item['shape'].isValid() and len(item['shape'].Solids)==1,item['id']
        if item['id'] in new_ids:
            pose=expected[item['id']].multiply(item['target'].Shape.Placement)
            t,r=placement_errors(item['shape'].Placement,pose);assert t<1e-6 and r<1e-8,item['id']
        elif item['id'] not in changed_ids:assert same_shape(signatures[item['id']],shape_signature(item['shape'])),item['id']
    counts=Counter(pid for n in new_ids for pid in json.loads(byid[n]['target'].SurveyIds))
    assert dict(counts)=={r['part_id']:r['count'] for r in source['physical_inventory']}
    assert len(changed_ids)==5
    print('Reopened',len(items),'valid single-solid leaves;',len(before)-len(changed_ids),'unchanged.',flush=True)
    tank=App.openDocument(build['build']['top_document']);tank.recompute()
    replaced={'hull_engine_back','PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting',
              'hull_port_inner_rear_end','hull_port_rear_wing','hull_starboard_inner_rear_end','hull_starboard_rear_wing'}
    context=[i for i in leaves(tank.Root) if i['id'] not in replaced and i['representation']=='assembly']
    physical=items+context;assert len({i['id'] for i in physical})==len(physical)
    boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].copy().cleaned().BoundBox for i in physical]])
    pairs=set();overlaps=[]
    for name in new_ids+changed_ids:
        shape=byid[name]['shape'];b=shape.copy().cleaned().BoundBox;bb=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
        near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
        for index in near:
            second=physical[index];pair=tuple(sorted([name,second['id']]))
            if pair[0]==pair[1] or pair in pairs:continue
            pairs.add(pair);volume=shape.common(second['shape']).Volume
            if volume>1e-5:overlaps.append(dict(a=name,b=second['id'],volume_mm3=volume))
    print('Material:',len(pairs),'candidate pairs;',len(overlaps),'overlaps.',flush=True)
    interfaces=[];tooth_checks=[];mesh_checks=[]
    def distance(a,b,nominal):
        gap=byid[a]['shape'].distToShape(byid[b]['shape'])[0]
        interfaces.append(dict(a=a,b=b,gap_mm=gap,expected_mm=nominal,passed=abs(gap-nominal)<1e-5))
    for hand in ['Port','Starboard']:
        prefix=hand+'PlanetTrain_';case=hand+'TransmissionCore_'
        distance(prefix+'washer',case+'planet_disk',c['washer_axial_gap'])
        distance(prefix+'washer',hand+'TransmissionBearing_InnerBush',c['washer_axial_gap'])
        distance(prefix+'retainer','CenterTransmissionCore_cross_shaft',c['retainer_groove_gap'])
        distance(prefix+'retainer',prefix+'sun',c['sun_retainer_gap'])
        for key in ['brake_case','plain_case']:distance(prefix+'ring',case+key,c['ring_radial_gap'])
        for n,key in enumerate(['plain_case','brake_case']):
            distance(prefix+'gasket'+str(n),prefix+'ring',0)
            distance(prefix+'gasket'+str(n),case+key,0)
        distance('CenterTransmissionCore_cross_shaft',hand+'TransmissionOutput_shaft',core['shaft_end_gap'])
        distance(case+'planet_disk',hand+'TransmissionBearing_InnerRing',.2*cal['mm_per_pixel'])
        for key,tip in [('sun',dimensions['tooth_profiles']['sun']['tip_radius_mm']),
                        ('planet',dimensions['tooth_profiles']['planet']['tip_radius_mm']),
                        ('ring',dimensions['tooth_profiles']['ring']['root_radius_mm'])]:
            for name in [n for n in new_ids if n.startswith(prefix) and key_for[n]==key]:
                # Each tooth leaves one analytic tip-cylinder patch; count saved geometry.
                count=sum(isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-tip)<1e-6 for f in byid[name]['shape'].Faces)
                tooth_checks.append(dict(id=name,native_tip_patches=count,printed_teeth=c['teeth_'+key],passed=count==c['teeth_'+key]))
        for n in range(c['planets_per_side']):
            name=prefix+'planet'+str(n);planet=byid[name]
            frame=planet['shape'].Placement.multiply(planet['target'].Shape.Placement.inverse())
            center=frame.Base-origin;center_radius=math.hypot(center.x,center.z)
            gaps={key:planet['shape'].distToShape(byid[prefix+key]['shape'])[0] for key in ['sun','ring']}
            mesh_checks.append(dict(id=name,center_radius_mm=center_radius,tooth_gaps_mm=gaps,
                passed=abs(center_radius-dimensions['planet_center_radius_mm'])<1e-6 and all(.001<gap<.5 for gap in gaps.values())))
    protect=dimensions['retainer_center_y_mm']-c['retainer_stock']/2-c['retainer_groove_gap']-.01
    region=box(-100,100,-protect,protect,-100,100)
    old_center=replaced_shapes['cross_shaft'].common(region)
    new_center=byid['CenterTransmissionCore_cross_shaft']['target'].Shape.common(region)
    shaft_change=old_center.cut(new_center).Volume+new_center.cut(old_center).Volume
    assert shaft_change<1e-5
    exchange_ids=new_ids+changed_ids
    exchange=out/'TransmissionPlanetParts.step';Part.makeCompound([byid[n]['shape'] for n in exchange_ids]).exportStep(str(exchange))
    imported=Part.Shape();imported.read(str(exchange));assert imported.isValid() and len(imported.Solids)==len(exchange_ids)
    native_sorted=sorted([byid[n]['shape'].Solids[0] for n in exchange_ids],key=lambda s:(round(s.CenterOfMass.y,5),round(s.Volume,2)))
    step_sorted=sorted(imported.Solids,key=lambda s:(round(s.CenterOfMass.y,5),round(s.Volume,2)))
    for a,b in zip(native_sorted,step_sorted):
        assert abs(a.Volume-b.Volume)<max(1e-3,a.Volume*1e-8)
        assert (a.CenterOfMass-b.CenterOfMass).Length<1e-5
    passed=not overlaps and all(r['passed'] for r in interfaces+tooth_checks+mesh_checks)
    report=dict(complete=True,passed=passed,native_occurrences=len(items),new_occurrences=len(new_ids),changed_prior_occurrences=len(changed_ids),
        unchanged_prior_occurrences=len(before)-len(changed_ids),new_source_counts=dict(counts),material_candidate_pairs=len(pairs),overlaps=overlaps,
        interfaces=interfaces,tooth_count_checks=tooth_checks,mesh_checks=mesh_checks,protected_shaft_difference_mm3=shaft_change,
        dimensions=dimensions,input_dimensions=dimensions_in,shaft_axis_world_mm=list(origin),carrier_local_phases_rad=hand_phases,
        new_ids=new_ids,changed_ids=changed_ids,keys_by_id=key_for,
        expected_placements={n:dict(base=list(p.Base),quaternion=list(p.Rotation.Q)) for n,p in expected.items()},
        input_hashes=hashes,authored_fingerprint=lock,tank_native_hashes=build['native_hashes'],native_sha256=sha(native),
        exchange_sha256=sha(exchange),exchange_roundtrip_solids=len(imported.Solids),standard_assembly_modified=False,
        complete_transmission=False,historical_fit_qualified=False,full_parameter_envelope_qualified=False,rendering_complete=False)
    write(out/'report.json',report)
    for row in overlaps+[r for r in interfaces+tooth_checks+mesh_checks if not r['passed']]:print('FAILED',row,flush=True)
    COLORS.update(PlanetGear=(.69,.55,.31),PlanetShell=(.42,.55,.48),PlanetRetainer=(.53,.57,.61),PlanetGasket=(.55,.37,.28))
    def colored(item):
        key=key_for.get(item['id'])
        system=('PlanetGasket' if key=='gasket' else 'PlanetRetainer' if key in ['washer','retainer'] else
                'PlanetGear' if key in ['sun','planet','ring'] else 'PlanetShell' if 'TransmissionCore_' in item['id'] else item['system'])
        return dict(item,system=system)
    selected=[colored(i) for i in items if i['id'] in new_ids or 'TransmissionCore_' in i['id'] or i['id'].startswith(
        ('TransmissionFrame_','PortFixedBearing_','StarboardFixedBearing_','PortTransmissionOutput_','StarboardTransmissionOutput_',
         'PortTransmissionBearing_','StarboardTransmissionBearing_')) or i['id'] in ['PortChain_TransmissionPinion','StarboardChain_TransmissionPinion']]
    gears=[i for i in selected if i['id'].startswith('PortPlanetTrain_') and key_for.get(i['id']) in ['sun','planet','ring']]
    shaded(gears,out/'large_gears_front.svg',(0,1,0),'Large epicyclic train | 18-tooth sun, three 27-tooth planets, 72-tooth ring')
    shaded(gears,out/'large_gears_oblique.svg',(1,1,.7),'Large planetary gears | inferred stub tooth form; pins and bushings remain pending')
    shaded(selected,out/'transmission_installed.svg',(1,1,.7),'Transmission assembly | large gears and retention fitted inside the cases')
    section_items=[]
    for item in selected:
        b=item['shape'].copy().cleaned().BoundBox
        if b.ZMin>=origin.z:continue
        shape=item['shape'].common(box(b.XMin-1,b.XMax+1,b.YMin-1,b.YMax+1,b.ZMin-1,origin.z))
        if shape.isNull() or not shape.Solids:continue
        section_items.append(dict(item,definition=item['definition']+'_section_'+item['id'],shape=shape,target=SimpleNamespace(Shape=shape)))
    shaded(section_items,out/'transmission_gear_cutaway.svg',(1,1,1.2),'Transmission horizontal cutaway | large gear trains, case seats and retaining interfaces')
    # Source Plate22 is a section, not a silhouette; overlay actual shaft-height sections.
    bg=base64.b64encode((REPO/cal['image']).read_bytes()).decode()
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1724" height="1147">',f'<image width="1724" height="1147" href="data:image/png;base64,{bg}" opacity=".60"/>']
    overlay_colors={'ring':'#b1261e','sun':'#00823c','planet':'#b16a00','gasket':'#8b359d','retainer':'#0086a8','washer':'#00709b'}
    plane=Part.makePlane(3000,3000,App.Vector(origin.x-1500,-1500,origin.z),App.Vector(0,0,1))
    for name in new_ids+changed_ids:
        if name.startswith('Starboard'):continue
        section=byid[name]['shape'].section(plane)
        for edge in section.Edges:
            points=[]
            for v in edge.discretize(Deflection=.3):
                px=cal['sprocket_center_x_px']-(v.y-prior['output_center_y_mm'])/cal['mm_per_pixel']
                py=cal['shaft_axis_y_px']+(v.x-origin.x)/cal['mm_per_pixel']
                points.append(f'{px:.3f},{py:.3f}')
            svg.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{overlay_colors.get(key_for.get(name),"#1764ba")}" stroke-width="1.4"/>')
    svg+=['<rect x="24" y="1070" width="1675" height="66" fill="white"/>',
          '<text x="36" y="1096" font-family="sans-serif" font-size="17">Actual horizontal section: red ring, green sun, ochre planets; blue revised receivers and shaft.</text>',
          '<text x="36" y="1120" font-family="sans-serif" font-size="16">Printed teeth/pitch override scaled radial extent. Three planets are at 120 degrees; drawing may use a composite section.</text></svg>']
    path=out/'source_plate22_overlay.svg';path.write_text('\n'.join(svg))
    import fitz
    with fitz.open(stream=path.read_bytes(),filetype='svg') as drawing:drawing[0].get_pixmap().save(str(path.with_suffix('.png')))
    assert fingerprint()==lock and check_build(stage/'build')['native_hashes']==build['native_hashes']
    assert all(sha(ROOT/n)==digest for n,digest in hashes.items())
    report.update(rendering_complete=True,output_raster_hashes={p.name:sha(p) for p in out.glob('*.png')})
    write(out/'report.json',report)
    print('PASS' if passed else 'FAIL',flush=True)
    sys.exit(0 if passed else 1)
finally:runtime.close()
