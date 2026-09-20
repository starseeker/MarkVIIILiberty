"""Install source-length cap studs, castle nuts and formed split pins."""
import argparse
import json
from collections import Counter
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage',type=Path,required=True)
parser.add_argument('--output',type=Path,default=ROOT/'transmission_stud_clearance_build')
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
    from transmission_stud_parts import hardware,receiving_castings,cylinder_x

    lock=fingerprint();build=check_build(stage/'build')
    names=['transmission_stud_probe.py','transmission_stud_parts.py','transmission_stud_controls.json',
           'transmission_stud_research.json','transmission_support_controls.json','transmission_support_parts.py',
           'transmission_output_parts.py','transmission_support_clearance_build/report.json',
           'transmission_lid_clearance_build/report.json','transmission_lid_clearance_build/visual_review.json',
           'transmission_lid_clearance_build/TransmissionLidCandidate.FCStd']
    hashes={n:sha(ROOT/n) for n in names}
    for n in names:
        if '/' not in n:
            p=out/'inputs'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/n).read_bytes())
    source=read(ROOT/'transmission_stud_research.json')
    for name,digest in source['inspected_source_hashes'].items():assert sha(REPO/name)==digest
    c={k:v['value'] for k,v in read(ROOT/'transmission_stud_controls.json')['controls'].items()}
    support={k:v['value'] for k,v in read(ROOT/'transmission_support_controls.json')['controls'].items()}
    dims=read(ROOT/'transmission_support_clearance_build/report.json')['dimensions']
    prior=read(ROOT/'transmission_lid_clearance_build/report.json')
    assert prior['passed'] and prior['rendering_complete']
    assert prior['native_sha256']==hashes[names[-1]] and prior['authored_fingerprint']==lock
    assert prior['tank_native_hashes']==build['native_hashes']
    doc=App.openDocument(str(ROOT/names[-1]));doc.recompute();before=leaves(doc.Root)
    byid={i['id']:i for i in before};signatures={i['id']:shape_signature(i['shape']) for i in before}
    shapes,stack,undrilled_studs=hardware(c,support)
    install={};undrilled_brackets={};frames={}
    for role in ['inner','outer']:
        prefix='PortFixedBearing_'+role+'_';bracket=byid[prefix+'bracket']['target'];cap=byid[prefix+'cap']['target']
        revised,spotfaced,locations,blank=receiving_castings(bracket.Shape,cap.Shape,role,c,support,dims[role],stack)
        bracket.Tip.Shape=revised;cap.Tip.Shape=spotfaced;install[role]=locations;undrilled_brackets[role]=blank
        metadata(bracket,ReconstructionNotes='Source-length cap studs constrain blind receiving bosses. Inferred profiles/allocation in transmission_stud_controls.json; threads not modeled.')
        metadata(cap,ReconstructionNotes='Integral closed-cover hinge retained; stud nut seating faces follow source-length clamp stack. Oil fittings pending.')
    definitions={};expected_counts={}
    for key,shape in shapes.items():
        row=next(r for r in source['physical_inventory'] if (r['mark']==key if key.startswith('MX')
                 else r['record_id']==('SNL:241:014' if key=='nut' else 'SNL:241:015')))
        body=doc.addObject('PartDesign::Body','Def_TransmissionCap_'+key);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedPart').Shape=shape
        metadata(body,DefinitionId='transmission_cap_'+key,OriginalMark=row['mark'],SurveyIds=[row['part_id']],
                 SourceRecord=row['record_id'],Representation='assembly',Coverage='partial',
                 ReconstructionNotes='Printed stud/pin nominal dimensions; inferred nut, cotter form and placement. Helical threads omitted; no load-capacity claim.')
        if key.startswith('MX'):
            for name,value in [('NominalDiameter',c['stud_diameter']),('NominalLength',c[key+'_length']),
                               ('USThreadEndLength',c['US_thread_length']),('SAEThreadEndLength',c['SAE_thread_length'])]:
                body.addProperty('App::PropertyLength',name,'Source');setattr(body,name,value)
            clean=shape.copy().cleaned();assert abs(clean.BoundBox.XLength-row['length_mm'])<1e-6
            cylinders=[f.Surface for f in shape.Faces if isinstance(f.Surface,Part.Cylinder) and abs(abs(f.Surface.Axis.x)-1)<1e-8]
            assert cylinders and all(abs(2*s.Radius-row['diameter_mm'])<1e-6 for s in cylinders)
        definitions[key]=body;expected_counts[row['part_id']]=row['count']
    new=[];changed=[];expected={};stations=[]
    for hand in ['Port','Starboard']:
        for role in ['inner','outer']:
            prefix=hand+'FixedBearing_'+role+'_';item=byid[prefix+'bracket']
            frame=item['shape'].Placement.multiply(item['target'].Shape.Placement.inverse());frames[hand+role]=frame
            owner=doc.getObject(hand+role.title()+'FixedBearing');assert owner is not None
            changed.extend([prefix+'bracket',prefix+'cap'])
            for setting in install[role]:
                suffix='Stud'+str(setting['index']).zfill(2);mark=setting['mark']
                group=doc.addObject('App::Part',hand+role.title()+suffix+'Assembly');owner.addObject(group)
                group.Placement=App.Placement(App.Vector(0,setting['y_mm'],setting['z_mm']),App.Rotation())
                metadata(group,SourceRecord={'MX9':'SNL:241:011','MX10':'SNL:241:016','MX36':'SNL:241:021'}[mark],
                         Scope='One physical stud, castle nut and formed split pin; belongs to fixed bearing')
                for component,key,x in [('Stud',mark,setting['tail_x_mm']),('Nut','nut',stack['cap_seating_x_mm']),
                                         ('Cotter','cotter',stack['cotter_axis_x_mm'])]:
                    name=prefix+suffix+'_'+component;link=doc.addObject('App::Link',name);group.addObject(link)
                    rotation=App.Rotation(App.Vector(1,0,0),180) if component=='Cotter' and hand=='Port' else App.Rotation()
                    link.setLink(definitions[key]);link.LinkPlacement=App.Placement(App.Vector(x,0,0),rotation)
                    metadata(link,OccurrenceId=name,Subsystem='Drivetrain');new.append(name)
                    expected[name]=frame.multiply(group.Placement).multiply(link.LinkPlacement)
                stations.append(dict(hand=hand,role=role,prefix=prefix+suffix+'_',**setting))
    doc.Definitions.Visibility=False;doc.recompute();native=out/'TransmissionStudCandidate.FCStd'
    doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items}
    assert len(items)==len(byid)==912
    for item in items:
        assert item['shape'].isValid() and len(item['shape'].Solids)==1,item['id']
        if item['id'] in new:
            t,r=placement_errors(item['shape'].Placement,expected[item['id']]);assert t<1e-6 and r<1e-8,item['id']
        elif item['id'] not in changed:assert same_shape(signatures[item['id']],shape_signature(item['shape'])),item['id']
    counts=Counter(pid for name in new for pid in json.loads(byid[name]['target'].SurveyIds));assert dict(counts)==expected_counts
    tank=App.openDocument(build['build']['top_document']);tank.recompute()
    replaced={'hull_engine_back','PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting',
              'hull_port_inner_rear_end','hull_port_rear_wing','hull_starboard_inner_rear_end','hull_starboard_rear_wing'}
    context=[i for i in leaves(tank.Root) if i['id'] not in replaced and i['representation']=='assembly']
    physical=items+context;assert len({i['id'] for i in physical})==len(physical)
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
    print('Stud assembly material:',len(pairs),'pairs,',len(overlaps),'overlaps',flush=True)
    def world(shape,pose):
        s=shape.copy();s.Placement=pose.multiply(s.Placement);return s
    interfaces=[]
    for station in stations:
        hand=station['hand'];role=station['role'];prefix=station['prefix']
        stud,nut,cotter=[byid[prefix+suffix]['shape'] for suffix in ['Stud','Nut','Cotter']]
        bearing=hand+'FixedBearing_'+role+'_';cap=byid[bearing+'cap']['shape'];bracket=byid[bearing+'bracket']['shape']
        shift=stud.copy();shift.translate(App.Vector(0,c['radial_witness_shift'],0))
        receiver_hits=[shift.common(s).Volume for s in [cap,bracket]]
        unbored=world(undrilled_studs[station['mark']],expected[prefix+'Stud']).common(cotter).Volume
        nut_seat=nut.distToShape(cap)[0];nut_gap=nut.distToShape(stud)[0];cotter_gap=cotter.distToShape(stud)[0]
        rotated=nut.copy();pivot=frames[hand+role].multVec(App.Vector(0,station['y_mm'],station['z_mm']))
        rotated.rotate(pivot,App.Vector(1,0,0),c['nut_rotation_witness']);rotation_hit=rotated.common(cotter).Volume
        axial_hits=[]
        for sign in [-1,1]:
            shifted=cotter.copy();shifted.translate(App.Vector(0,sign*c['cotter_retention_shift'],0));axial_hits.append(shifted.common(nut).Volume)
        tail=station['tail_x_mm'];thread_end=station['US_thread_front_x_mm'];bore=c['stud_diameter']/2+support['stud_hole_gap']
        stock=cylinder_x(bore+2,tail,thread_end,station['y_mm'],station['z_mm']).cut(cylinder_x(bore,tail-1,thread_end+1,station['y_mm'],station['z_mm']))
        missing_stock=world(stock,frames[hand+role]).cut(bracket).Volume
        blind_gap=stud.distToShape(bracket)[0]
        passed=(max(abs(nut_seat),abs(nut_gap-c['nut_bore_gap']),abs(cotter_gap-c['cotter_hole_gap']))<1e-5
                and abs(blind_gap-c['blind_end_gap'])<1e-5 and missing_stock<1e-5
                and min(receiver_hits)>1 and unbored>1 and rotation_hit>1e-3 and min(axial_hits)>1e-3)
        interfaces.append(dict(station=prefix,mark=station['mark'],nut_seat_mm=nut_seat,nut_stud_gap_mm=nut_gap,
                               cotter_stud_gap_mm=cotter_gap,stud_blind_end_gap_mm=blind_gap,
                               required_two_mm_receiver_wall_missing_mm3=missing_stock,radial_stud_witness_mm3=receiver_hits,
                               undrilled_stud_cotter_overlap_mm3=unbored,nut_rotation_cotter_overlap_mm3=rotation_hit,
                               cotter_two_sided_axial_witness_mm3=axial_hits,passed=passed))
    retained=[]
    for hand in ['Port','Starboard']:
        for role in ['inner','outer']:
            prefix=hand+'FixedBearing_'+role+'_';cap=byid[prefix+'cap']['shape'];bracket=byid[prefix+'bracket']['shape']
            gaps=dict(cap_lining=cap.distToShape(byid[prefix+'lining_front']['shape'])[0],
                      bracket_lining=bracket.distToShape(byid[prefix+'lining_back']['shape'])[0],
                      cap_split=cap.distToShape(bracket)[0],cover=cap.distToShape(byid[prefix+'lid']['shape'])[0],
                      hinge_pin=cap.distToShape(byid[prefix+'cover_pin']['shape'])[0])
            passed=max(abs(gaps[k]-v) for k,v in [('cap_lining',0),('bracket_lining',0),('cap_split',.1),('cover',.15),('hinge_pin',.15)])<1e-5
            retained.append(dict(hand=hand,role=role,gaps_mm=gaps,passed=passed))
    exchange=out/'CapStudsAndReceivers.step';Part.makeCompound([byid[n]['shape'] for n in new+changed]).exportStep(str(exchange))
    imported=Part.Shape();imported.read(str(exchange));assert imported.isValid() and len(imported.Solids)==56
    passed=not overlaps and all(i['passed'] for i in interfaces+retained)
    report=dict(complete=True,passed=passed,native_occurrences=len(items),new_hardware_occurrences=len(new),
                changed_casting_occurrences=len(changed),unchanged_prior_occurrences=len(before)-len(changed),
                new_source_counts=dict(counts),material_candidate_pairs=len(pairs),overlaps=overlaps,
                stud_interfaces=interfaces,retained_bearing_hinge_interfaces=retained,stack=stack,stations=stations,
                material_filter='BRep bounds after removing triangulation caches',input_hashes=hashes,authored_fingerprint=lock,
                tank_native_hashes=build['native_hashes'],native_sha256=sha(native),exchange_sha256=sha(exchange),
                exchange_roundtrip_solids=len(imported.Solids),standard_assembly_modified=False,historical_fit_qualified=False,
                thread_flank_and_axial_retention_qualified=False,inner_stud_corner_allocation_qualified=False,
                inherited_frame_attachment_and_parameter_qualification_incomplete=True,rendering_complete=False)
    write(out/'report.json',report)
    print('Stud fits:',all(i['passed'] for i in interfaces),'retained bearings:',all(i['passed'] for i in retained),flush=True)
    for row in overlaps:print(row,flush=True)
    for row in interfaces:
        if not row['passed']:print('FAILED INTERFACE',row,flush=True)
    one=[i for i in items if i['id'].startswith('PortFixedBearing_inner_')]
    shaded(one,out/'fastened_inner_bearing.svg',(1,1,.6),'Inside bearing | printed-length studs, castle nuts and formed split pins')
    close=[i for i in one if i['id'].endswith(('_cap','_lid','_cover_pin')) or '_Stud' in i['id']]
    shaded(close,out/'cap_fastener_detail.svg',(1,.6,.7),'Bearing cap fastening | inferred nut, cotter and cast boss form; threads omitted')
    joint=[i for i in one if '_Stud02_' in i['id']]
    shaded(joint,out/'castle_nut_and_cotter.svg',(1,1,.7),'MX36 stud, castle nut and formed split pin | source lengths, inferred retention form')
    all_bearings=[i for i in items if 'FixedBearing_' in i['id'] or i['id'].startswith('TransmissionFrame_')]
    shaded(all_bearings,out/'frame_with_cap_fasteners.svg',(1,1,.7),'Frame and fastened bearing caps | central case and mounting hardware pending')
    assert fingerprint()==lock and check_build(stage/'build')['native_hashes']==build['native_hashes']
    assert all(sha(ROOT/n)==digest for n,digest in hashes.items())
    report.update(rendering_complete=True,output_raster_hashes={p.name:sha(p) for p in out.glob('*.png')})
    write(out/'report.json',report)
    sys.exit(0 if passed else 1)
finally:runtime.close()
