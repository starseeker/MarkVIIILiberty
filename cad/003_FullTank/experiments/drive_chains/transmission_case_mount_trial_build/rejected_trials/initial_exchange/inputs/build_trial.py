"""Durable MX5 installation trial; does not replace the accepted candidate."""
import argparse, base64, json, subprocess, sys
from pathlib import Path
from types import SimpleNamespace
REPO=Path(__file__).resolve().parents[2]
STAGE=REPO/'cad/003_FullTank'
ROOT=STAGE/'experiments/drive_chains'
p=argparse.ArgumentParser();p.add_argument('--worker',action='store_true')
p.add_argument('--output',type=Path,default=Path(__file__).parent/'trial01')
a=p.parse_args();out=a.output.resolve();sys.path[:0]=[str(STAGE),str(ROOT)]
from lib import runtime
from lib.evidence import read,write,sha
if not a.worker:
    out.mkdir(parents=True,exist_ok=True)
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--worker','--output',str(out)],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part,numpy as np,fitz
    from lib.cad_build import leaves,metadata,shape_signature,COLORS
    from lib.worker import same_shape,placement_errors,check_build
    from lib.visual_review import shaded
    from transmission_case_mount_parts import case_mount_parts,moved
    parent=ROOT/'transmission_vertical_build';prior=read(parent/'report.json');q=read(parent/'qualification.json')
    native=parent/'TransmissionVerticalCandidate.FCStd'
    assert q['passed'] and q['rendering_complete'] and q['visually_reviewed']
    assert sha(native)==q['native_sha256']==prior['native_sha256']
    for path,digest in q['receipt_hashes'].items():assert sha(parent/path)==digest,path
    c=read(ROOT/'transmission_case_mount_controls.json')['controls']
    pc={k:v['value'] for k,v in read(ROOT/'transmission_stud_controls.json')['controls'].items()}
    pc['cotter_eye_join_overlap']=.1
    inputs=[ROOT/'transmission_case_mount_parts.py',ROOT/'transmission_case_mount_controls.json',
        ROOT/'transmission_stud_controls.json',ROOT/'transmission_input_installation_parts.py',Path(__file__)]
    hashes={str(p.relative_to(REPO)):sha(p) for p in inputs}
    for path in inputs:
        dest=out/'inputs'/path.name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(path.read_bytes())
    doc=App.openDocument(str(native));doc.recompute();before=leaves(doc.Root);old={i['id']:i for i in before}
    signatures={n:shape_signature(i['shape']) for n,i in old.items()}
    placements={n:i['shape'].Placement for n,i in old.items()}
    origin=doc.TransmissionCore.Placement.Base
    channels={k:old['TransmissionFrame_'+label+'Channel']['target'].Shape for k,label in [('top','Top'),('bottom','Bottom')]}
    defs,revised,installed,d=case_mount_parts(c,old['CenterTransmissionCore_bevel_case']['target'].Shape,
        channels,old['PortFixedBearing_inner_Stud01_Nut']['target'].Shape,pc)
    # Check both original straight cotter legs, independently of a valid BRep.
    legacy=old['PortFixedBearing_inner_Stud01_Cotter']['target'].Shape
    pin_tests=[]
    for name,shape in [('legacy',legacy),('analytic',defs['cotter'])]:
        half=pc['cotter_center_spacing']/2;wire=(pc['cotter_diameter']-pc['cotter_center_spacing'])/2
        for sign in [-1,1]:
            witness=Part.makeCylinder(wire-.01,pc['crown_radius']*2+pc['cotter_head_gap']+pc['cotter_exit_gap']-2,
                App.Vector(0,-pc['crown_radius']-pc['cotter_head_gap']+1,sign*half),App.Vector(0,1,0))
            missing=witness.cut(shape).Volume
            pin_tests.append(dict(definition=name,leg=sign,witness_volume=witness.Volume,missing_mm3=missing,passed=missing<1e-5))
    write(out/'pin_leg_checks.json',pin_tests)
    print('Cotter legs',pin_tests,flush=True)
    changed=['CenterTransmissionCore_bevel_case','TransmissionFrame_TopChannel','TransmissionFrame_BottomChannel']
    for key,n in zip(['case','Upper','Lower'],changed):
        old[n]['target'].Tip.Shape=revised[key]
        metadata(old[n]['target'],CaseMountRevision='Unqualified MX5 local mounting trial: inferred bosses, channel taper and bores.')
    rows=dict(stud=('MX5','P_c5b4d785b6867abb','SNL:241:028'),nut=('', 'P_c3bb5fc9299bfab2','SNL:241:029'),
        cotter=('', 'P_715e37e46e3ce9b8','SNL:242:003'),washer=('MX13','P_6e5a15454080a055','SNL:267:006'))
    bodies={'nut':old['PortFixedBearing_inner_Stud01_Nut']['target']}
    for k in ['stud','cotter','washer']:
        body=doc.addObject('PartDesign::Body','Def_CaseMount_'+k);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedPart').Shape=defs[k]
        mark,pid,record=rows[k];metadata(body,DefinitionId='transmission_case_mount_'+k,OriginalMark=mark,
            SurveyIds=[pid],SourceRecord=record,Representation='assembly',Coverage='trial',
            ParameterUpdate='transmission_case_mount_parts.py; unqualified mounting hypothesis')
        bodies[k]=body
    group=doc.addObject('App::Part','TransmissionCaseMounting');doc.TransmissionCore.addObject(group)
    metadata(group,Scope='Four case studs plus four conditionally allocated bevel washers; unresolved source length and casting profile.')
    new=[];expected={}
    for mount in d['mounts']:
        joint=doc.addObject('App::Part','CaseMount_'+mount['name']);group.addObject(joint)
        metadata(joint,SurveyIds=['P_21218b61a7580c24'],ReferencedSurveyIds=['P_50d2ee4ba9ef6f71'],
            SourceRecord='SNL:241:026',InventoryQuantityRole='Container only; conflicting assembly lengths remain distinct identities')
        for k in ['stud','nut','cotter','washer']:
            name='CaseMount_'+mount['name']+'_'+k
            obj=doc.addObject('App::Link',name);joint.addObject(obj);obj.setLink(bodies[k])
            obj.LinkPlacement=installed[mount['name']+'_'+k].Placement
            metadata(obj,OccurrenceId=name,Subsystem='Drivetrain',SourceRecord=rows[k][2])
            new.append(name);expected[name]=doc.TransmissionCore.Placement.multiply(obj.LinkPlacement)
    doc.Definitions.Visibility=False;doc.recompute();trial=out/'MX5CaseMountTrial.FCStd';doc.saveAs(str(trial));App.closeDocument(doc.Name)
    doc=App.openDocument(str(trial));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items}
    assert len(items)==len(byid)==len(before)+16==1407
    for n,i in byid.items():
        assert i['shape'].isValid() and len(i['shape'].Solids)==1,n
        t,r=placement_errors(i['shape'].Placement,expected[n] if n in expected else placements[n]);assert t<1e-6 and r<1e-8,(n,t,r)
        if n not in new+changed:assert same_shape(signatures[n],shape_signature(i['shape'])),n
    print('Reopened 1407 valid leaves; 16 new, 3 changed, 1388 unchanged.',flush=True)
    report=dict(status='unqualified_installation_trial',native_sha256=sha(trial),parent_native_sha256=sha(native),input_hashes=hashes,
        controls=c,pin_controls=pc,dimensions=d,new_ids=new,changed_ids=changed,native_occurrences=len(items),
        complete_transmission=False,historical_fit_qualified=False,standard_assembly_modified=False,pin_leg_checks=pin_tests)
    write(out/'report.json',report)
    # The whole standard assembly is context; explicit superseded receivers
    # follow the accepted parent candidate's exclusion list.
    build=check_build(STAGE/'build');tank=App.openDocument(build['build']['top_document']);tank.recompute()
    excluded={'hull_engine_back','PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting','hull_port_inner_rear_end',
        'hull_port_rear_wing','hull_starboard_inner_rear_end','hull_starboard_rear_wing'}
    context=[i for i in leaves(tank.Root) if i['id'] not in excluded and i['representation']=='assembly']
    physical=items+context;assert len({i['id'] for i in physical})==len(physical)
    boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].copy().cleaned().BoundBox for i in physical]])
    pairs=set();overlaps=[]
    for n in new+changed:
        shape=byid[n]['shape'];b=shape.copy().cleaned().BoundBox;bb=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
        near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
        for idx in near:
            other=physical[idx];pair=tuple(sorted([n,other['id']]))
            if pair[0]==pair[1] or pair in pairs:continue
            pairs.add(pair);v=shape.common(other['shape']).Volume
            if v>1e-5:overlaps.append(dict(a=n,b=other['id'],volume_mm3=v))
        write(out/'material_progress.json',dict(last_id=n,pairs=len(pairs),overlaps=overlaps))
    interfaces=[]
    def gap(a,b,want):
        value=byid[a]['shape'].distToShape(byid[b]['shape'])[0]
        interfaces.append(dict(a=a,b=b,gap_mm=value,expected_mm=want,passed=abs(value-want)<1e-5))
    for row in prior['interfaces']:
        if row['a'] in changed or row['b'] in changed:gap(row['a'],row['b'],row['expected_mm'])
    for mount in d['mounts']:
        n='CaseMount_'+mount['name'];channel='TransmissionFrame_'+('Top' if mount['channel']=='Upper' else 'Bottom')+'Channel'
        gap(n+'_stud',changed[0],c['receiver_gap']);gap(n+'_stud',channel,c['receiver_gap'])
        gap(n+'_nut',n+'_stud',.15);gap(n+'_cotter',n+'_stud',c['cotter_hole_gap'])
        gap(n+'_nut',n+'_washer',0);gap(n+'_washer',channel,0);gap(changed[0],channel,0)
    report.update(material_pairs=len(pairs),overlaps=overlaps,interfaces=interfaces,
        local_geometry_passed=not overlaps and all(r['passed'] for r in interfaces),standard_native_hashes=build['native_hashes'])
    write(out/'report.json',report)
    print('Material pairs',len(pairs),'overlaps',overlaps,flush=True)
    print('Failed gaps',[r for r in interfaces if not r['passed']],flush=True)
    # Render reopened geometry and fixed calibration without changing CAD.
    view=out/'source_review';view.mkdir(exist_ok=True)
    COLORS.update(Case=(.44,.56,.47),Channel=(.43,.48,.53),Stud=(.76,.50,.20),Nut=(.66,.67,.61),Washer=(.64,.40,.24))
    def draw(names,file,title,direction,clip=None):
        selected=[]
        for n in names:
            s=byid[n]['shape'];s=s.common(clip) if clip is not None else s
            if s.isNull() or not s.Solids:continue
            role='Case' if n==changed[0] else ('Channel' if n in changed[1:] else ('Stud' if n.endswith('_stud') else ('Washer' if n.endswith('_washer') else 'Nut')))
            selected.append(dict(id=n,shape=s,target=SimpleNamespace(Shape=s),definition=n,representation='assembly',system=role))
        shaded(selected,view/(file+'.svg'),direction,title)
    cropped=Part.makeBox(600,520,900,origin+App.Vector(-450,-260,-400))
    draw(new+changed,'mounting_overview','MX5 mounting trial | frame cropped; casting bosses and flange taper inferred',(1,1,1),cropped)
    draw(new+changed,'mounting_rear','MX5 mounting trial | four separate stud, nut, pin and bevel-washer sets',(-1,-1,1),cropped)
    upper=[n for n in new if n.startswith('CaseMount_UpperPort')]+[changed[0],changed[1]]
    clip=Part.makeBox(220,70,90,origin+App.Vector(-300,118,300))
    draw(upper,'upper_joint_section','Upper joint section | source-length stud; inferred blind boss and tapered washer',(-1,-1,.6),clip)
    cal=read(ROOT/'transmission_input_calibration.json');source=REPO/cal['image'];assert sha(source)==cal['image_sha256']
    plane=Part.makePlane(1400,1400,origin+App.Vector(-700,c['stud_half_span'],-700),App.Vector(0,1,0))
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1094" height="921">',
        f'<image width="1094" height="921" href="data:image/png;base64,{base64.b64encode(source.read_bytes()).decode()}" opacity=".65"/>']
    for n in changed+[n for n in new if 'Port' in n]:
        shape=byid[n]['shape'];shape=shape.section(plane) if n in changed else shape
        color='#237b42' if n==changed[0] else ('#28549b' if n in changed else '#a22b17')
        for edge in shape.Edges:
            pts=[f'{cal["origin_px"][0]-(v.x-origin.x)/cal["mm_per_pixel"]:.3f},{cal["origin_px"][1]-(v.z-origin.z)/cal["mm_per_pixel"]:.3f}' for v in edge.discretize(Deflection=.15)]
            svg.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="1.1"/>')
    svg.append('</svg>');path=view/'mounting_overlay.svg';path.write_text('\n'.join(svg))
    with fitz.open(stream=path.read_bytes(),filetype='svg') as f:f[0].get_pixmap().save(str(path.with_suffix('.png')))
    write(view/'render_receipt.json',dict(native_sha256=sha(trial),source_sha256=sha(source),
        calibration_sha256=sha(ROOT/'transmission_input_calibration.json'),rasters={p.name:sha(p) for p in view.glob('*.png')},
        case_section_y_mm=c['stud_half_span'],source_warped=False))
    assert sha(native)==prior['native_sha256']
    for path,digest in hashes.items():assert sha(REPO/path)==digest,path
    assert check_build(STAGE/'build')['native_hashes']==build['native_hashes']
    print('Trial and four review views saved; accepted candidate and standard tank unchanged.',flush=True)
finally:runtime.close()
