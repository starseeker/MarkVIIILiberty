"""Populate cap lubrication fittings and test inferred passages in saved native CAD."""
import argparse
import json
from collections import Counter
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage',type=Path,required=True)
parser.add_argument('--output',type=Path,default=ROOT/'transmission_oil_build')
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
    from transmission_oil_parts import fittings,cap_lubrication,cylinder_z
    from transmission_stud_parts import cylinder_x
    from transmission_support_parts import box

    lock=fingerprint();build=check_build(stage/'build')
    names=['transmission_oil_probe.py','transmission_oil_parts.py','transmission_oil_controls.json',
           'transmission_oil_sources.json','transmission_stud_parts.py','transmission_support_parts.py',
           'transmission_output_parts.py','transmission_support_controls.json',
           'transmission_support_clearance_build/report.json','transmission_stud_clearance_build/report.json',
           'transmission_stud_clearance_build/visual_review.json',
           'transmission_stud_clearance_build/TransmissionStudCandidate.FCStd']
    hashes={n:sha(ROOT/n) for n in names}
    for n in names:
        if '/' not in n:
            p=out/'inputs'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/n).read_bytes())
    source=read(ROOT/'transmission_oil_sources.json')
    for name,digest in source['inspected_source_hashes'].items():assert sha(REPO/name)==digest
    c={k:v['value'] for k,v in read(ROOT/'transmission_oil_controls.json')['controls'].items()}
    support={k:v['value'] for k,v in read(ROOT/'transmission_support_controls.json')['controls'].items()}
    dims=read(ROOT/'transmission_support_clearance_build/report.json')['dimensions']
    prior=read(ROOT/'transmission_stud_clearance_build/report.json')
    assert prior['passed'] and prior['rendering_complete'] and prior['native_sha256']==hashes[names[-1]]
    assert prior['authored_fingerprint']==lock and prior['tank_native_hashes']==build['native_hashes']
    doc=App.openDocument(str(ROOT/names[-1]));doc.recompute();before=leaves(doc.Root)
    byid={i['id']:i for i in before};signatures={i['id']:shape_signature(i['shape']) for i in before}
    shapes,fd,ft=fittings(c);dimensions={};passage_tools={};old_shapes={}
    for role in ['inner','outer']:
        prefix='PortFixedBearing_'+role+'_';cap=byid[prefix+'cap']['target'];lining=byid[prefix+'lining_front']['target']
        old_shapes[role]=dict(cap=cap.Shape.copy(),lining=lining.Shape.copy())
        new,d,t=cap_lubrication(cap.Shape,lining.Shape,dims[role],support,c)
        cap.Tip.Shape=new['cap'];lining.Tip.Shape=new['lining_front'];shapes['wool_'+role]=new['wool']
        dimensions[role]=d;passage_tools[role]=t
        metadata(cap,ReconstructionNotes='Source cap fastening and closed hinge retained. Front cup inlet and low oil gallery are inferred in transmission_oil_controls.json; exact cast profile/threads unresolved.')
        metadata(lining,ReconstructionNotes='In-situ poured lining with inferred feed gallery to sleeve running surface; historical brasses/babbitt conflict retained.')
    definitions={}
    for key,shape in shapes.items():
        row=next(r for r in source['physical_inventory'] if r['key']==('wool' if key.startswith('wool_') else key))
        body=doc.addObject('PartDesign::Body','Def_CapLubrication_'+key);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedPart').Shape=shape
        metadata(body,DefinitionId='cap_lubrication_'+key,OriginalMark=row['mark'],SurveyIds=[row['part_id']],
                 SourceRecord=row['record_id'],Representation='assembly',Coverage='partial',
                 ReconstructionNotes=row['representation_note']+' See transmission_oil_controls.json for inferred dimensions.')
        if key.startswith('wool_'):
            metadata(body,MaterialRepresentation='Porous wool envelope; excludes cap intrusions. No fiber, density or permeability simulation.',SourceQuantityUnit='oz')
            body.addProperty('App::PropertyFloat','SourceQuantityPerCup','Source');body.SourceQuantityPerCup=c['packing_quantity_oz']
        else:
            metadata(body,ThreadRepresentation='Smooth envelopes only; sealing, thread form and axial clamp unqualified.')
        definitions[key]=body
    new_ids=[];changed=[];expected={};frames={}
    for hand in ['Port','Starboard']:
        for role in ['inner','outer']:
            prefix=hand+'FixedBearing_'+role+'_';item=byid[prefix+'cap']
            frame=item['shape'].Placement.multiply(item['target'].Shape.Placement.inverse());frames[hand+role]=frame
            owner=doc.getObject(hand+role.title()+'FixedBearing');assert owner is not None
            changed.extend([prefix+'cap',prefix+'lining_front'])
            group=doc.addObject('App::Part',hand+role.title()+'CapOilFitting');owner.addObject(group)
            group.Placement=App.Placement(App.Vector(*dimensions[role]['inlet_origin_mm']),App.Rotation())
            metadata(group,Scope='SH664A elbow, SH664B nut and SH664C sleeve; inferred unhanded front-cup installation')
            for key in ['elbow','nut','sleeve','wool']:
                name=prefix+'Oil_'+key;link=doc.addObject('App::Link',name)
                parent=owner if key=='wool' else group;parent.addObject(link)
                link.setLink(definitions['wool_'+role if key=='wool' else key])
                link.LinkPlacement=App.Placement();metadata(link,OccurrenceId=name,Subsystem='Drivetrain')
                new_ids.append(name);expected[name]=frame if key=='wool' else frame.multiply(group.Placement)
    doc.Definitions.Visibility=False;doc.recompute();native=out/'TransmissionOilCandidate.FCStd'
    doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items}
    assert len(items)==len(byid)==928
    for item in items:
        assert item['shape'].isValid() and len(item['shape'].Solids)==1,item['id']
        if item['id'] in new_ids:
            t,r=placement_errors(item['shape'].Placement,expected[item['id']]);assert t<1e-6 and r<1e-8,item['id']
        elif item['id'] not in changed:assert same_shape(signatures[item['id']],shape_signature(item['shape'])),item['id']
    counts=Counter(pid for name in new_ids for pid in json.loads(byid[name]['target'].SurveyIds))
    assert dict(counts)=={row['part_id']:row['count'] for row in source['physical_inventory']}
    tank=App.openDocument(build['build']['top_document']);tank.recompute()
    replaced={'hull_engine_back','PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting',
              'hull_port_inner_rear_end','hull_port_rear_wing','hull_starboard_inner_rear_end','hull_starboard_rear_wing'}
    context=[i for i in leaves(tank.Root) if i['id'] not in replaced and i['representation']=='assembly']
    physical=items+context;assert len({i['id'] for i in physical})==len(physical)
    boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].copy().cleaned().BoundBox for i in physical]])
    pairs=set();overlaps=[]
    for name in new_ids+changed:
        a=byid[name]['shape'];b=a.copy().cleaned().BoundBox;bb=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
        near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
        for index in near:
            second=physical[index];pair=tuple(sorted([name,second['id']]))
            if pair[0]==pair[1] or pair in pairs:continue
            pairs.add(pair);volume=a.common(second['shape']).Volume
            if volume>1e-5:overlaps.append(dict(a=name,b=second['id'],volume_mm3=volume))
    print('Oil candidate material:',len(pairs),'pairs,',len(overlaps),'overlaps.',flush=True)
    def world(shape,pose):
        result=shape.copy();result.Placement=pose.multiply(result.Placement);return result
    interfaces=[];retained=[]
    for hand in ['Port','Starboard']:
        for role in ['inner','outer']:
            prefix=hand+'FixedBearing_'+role+'_';frame=frames[hand+role]
            cap=byid[prefix+'cap']['shape'];lining=byid[prefix+'lining_front']['shape']
            elbow,nut,sleeve,wool=[byid[prefix+'Oil_'+k]['shape'] for k in ['elbow','nut','sleeve','wool']]
            fitpose=expected[prefix+'Oil_elbow'];d=dimensions[role]
            witness=world(ft['witness'],fitpose).fuse(wool).fuse(world(passage_tools[role]['passage_witness'],frame)).removeSplitter()
            assert witness.isValid() and len(witness.Solids)==1
            blocked=witness.common(Part.makeCompound([cap,lining,elbow,nut,sleeve])).Volume
            negatives=dict(undrilled_cap=witness.common(world(old_shapes[role]['cap'],frame)).Volume,
                           undrilled_lining=witness.common(world(old_shapes[role]['lining'],frame)).Volume,
                           solid_elbow=witness.common(world(ft['blank'],fitpose)).Volume)
            contacts=dict(elbow_cap=elbow.distToShape(cap)[0],nut_elbow=nut.distToShape(elbow)[0],
                          sleeve_elbow=sleeve.distToShape(elbow)[0],sleeve_nut=sleeve.distToShape(nut)[0])
            spigot=world(cylinder_x(c['elbow_radius'],-3,-2.5).cut(cylinder_x(c['flow_radius'],-4,-2)),fitpose)
            gap=spigot.distToShape(cap)[0]
            jig=world(cylinder_z(c['tube_od']/2,c['sleeve_bottom'],c['nut_top']+1,fd['connector_x_mm']),fitpose)
            tube_gaps=dict(sleeve=jig.distToShape(sleeve)[0],nut=jig.distToShape(nut)[0])
            seat_hits=[]
            for dz,receiver in [(-.5,elbow),(.5,nut)]:
                moved=sleeve.copy();moved.translate(App.Vector(0,0,dz));seat_hits.append(moved.common(receiver).Volume)
            removed={k:world(old_shapes[role][k],frame).cut(s).Volume for k,s in [('cap',cap),('lining',lining)]}
            added={k:s.cut(world(old_shapes[role][k],frame)).Volume for k,s in [('cap',cap),('lining',lining)]}
            passed=(blocked<1e-5 and min(negatives.values())>1 and max(contacts.values())<1e-5
                    and abs(gap-c['spigot_radial_gap'])<1e-5 and abs(tube_gaps['sleeve']-c['tube_radial_gap'])<1e-5
                    and abs(tube_gaps['nut']-c['nut_tube_gap'])<1e-5 and min(seat_hits)>1
                    and min(removed.values())>1 and max(added.values())<1e-5)
            interfaces.append(dict(hand=hand,role=role,contacts_mm=contacts,spigot_radial_gap_mm=gap,
                tube_jig_gaps_mm=tube_gaps,sleeve_two_sided_capture_mm3=seat_hits,
                connected_passage_witness_solids=len(witness.Solids),passage_blockage_mm3=blocked,
                negative_obstruction_mm3=negatives,removed_material_mm3=removed,added_material_mm3=added,
                wool_envelope_mm3=wool.Volume,wool_source_quantity_oz=c['packing_quantity_oz'],passed=passed))
            gaps=dict(cap_lining=cap.distToShape(lining)[0],cap_split=cap.distToShape(byid[prefix+'bracket']['shape'])[0],
                      cover=cap.distToShape(byid[prefix+'lid']['shape'])[0],hinge_pin=cap.distToShape(byid[prefix+'cover_pin']['shape'])[0])
            stud_seats=[];protected_differences=[]
            oldcap=world(old_shapes[role]['cap'],frame)
            for station in [s for s in prior['stations'] if s['hand']==hand and s['role']==role]:
                stud_seats.append(byid[station['prefix']+'Nut']['shape'].distToShape(cap)[0])
                protected=world(cylinder_x(support['ear_radius']+1,-1,60,station['y_mm'],station['z_mm']),frame)
                oldregion=oldcap.common(protected);region=cap.common(protected)
                protected_differences.append(oldregion.cut(region).Volume+region.cut(oldregion).Volume)
            retained_pass=(max(abs(gaps[k]-v) for k,v in [('cap_lining',0),('cap_split',.1),('cover',.15),('hinge_pin',.15)])<1e-5
                           and max(stud_seats)<1e-5 and max(protected_differences)<1e-5)
            retained.append(dict(hand=hand,role=role,gaps_mm=gaps,stud_nut_seats_mm=stud_seats,
                                  stud_receiver_material_difference_mm3=protected_differences,passed=retained_pass))
    exchange=out/'CapLubricationAndPassages.step';Part.makeCompound([byid[n]['shape'] for n in new_ids+changed]).exportStep(str(exchange))
    imported=Part.Shape();imported.read(str(exchange));assert imported.isValid() and len(imported.Solids)==24
    passed=not overlaps and all(i['passed'] for i in interfaces+retained)
    report=dict(complete=True,passed=passed,native_occurrences=len(items),new_fitting_occurrences=12,new_porous_material_regions=4,
        changed_cap_lining_occurrences=len(changed),unchanged_prior_occurrences=len(before)-len(changed),new_source_counts=dict(counts),
        material_candidate_pairs=len(pairs),overlaps=overlaps,oil_interfaces=interfaces,retained_bearing_hinge_stud_interfaces=retained,
        fitting_dimensions=fd,cap_dimensions=dimensions,input_hashes=hashes,authored_fingerprint=lock,tank_native_hashes=build['native_hashes'],
        native_sha256=sha(native),exchange_sha256=sha(exchange),exchange_roundtrip_solids=len(imported.Solids),
        standard_assembly_modified=False,historical_fit_qualified=False,thread_seal_clamp_qualified=False,oil_performance_qualified=False,
        full_feed_lines_populated=False,passage_scope='Connected free-volume witness from fitting inlet through porous cup region and cap/lining gallery; excludes wool from solid blockage only because it represents permeable packing. No flow simulation.',
        rendering_complete=False)
    write(out/'report.json',report)
    print('Oil interfaces:',all(i['passed'] for i in interfaces),'retained:',all(i['passed'] for i in retained),flush=True)
    for row in overlaps:print(row,flush=True)
    for row in interfaces+retained:
        if not row['passed']:print('FAILED INTERFACE',row,flush=True)
    COLORS['OilInspection']=(.7,.56,.28);COLORS['WoolInspection']=(.65,.66,.52)
    def colored(item):
        return dict(item,system='WoolInspection' if item['id'].endswith('Oil_wool') else 'OilInspection' if '_Oil_' in item['id'] else item['system'])
    one=[colored(i) for i in items if i['id'].startswith('PortFixedBearing_inner_')]
    cap_only=[i for i in one if i['id'].endswith(('_cap','_lid','_cover_pin')) or '_Stud' in i['id'] or '_Oil_' in i['id']]
    shaded(cap_only,out/'lubricated_cap_detail.svg',(1,.8,.8),'Cap oil fitting | source identities, inferred fitting shape and inlet position')
    fittings_only=[i for i in one if '_Oil_' in i['id'] and not i['id'].endswith('wool')]
    shaded(fittings_only,out/'oil_fitting.svg',(1,1,.6),'SH664A elbow, SH664B nut and SH664C sleeve | quarter-inch OD tube interface')
    def section(selected,plane_y):
        result=[]
        for item in selected:
            bb=item['shape'].copy().cleaned().BoundBox
            tool=box(bb.XMin-1,bb.XMax+1,bb.YMin-1,plane_y,bb.ZMin-1,bb.ZMax+1)
            shape=item['shape'].common(tool)
            if shape.isNull() or not shape.Solids:continue
            key=item['definition']+'_section_'+item['id'];result.append(dict(item,definition=key,shape=shape,target=SimpleNamespace(Shape=shape)))
        return result
    fitting_y=expected['PortFixedBearing_inner_Oil_elbow'].Base.y
    shaded(section(fittings_only,fitting_y),out/'oil_fitting_section.svg',(1,1,.5),'Section | cone sleeve seats, nut shoulder and open elbow bore; threads omitted')
    bearing_y=frames['Portinner'].Base.y
    selected=[i for i in one if i['id'].endswith(('_cap','_lining_front','Oil_wool'))]
    shaded(section(selected,bearing_y),out/'bearing_oil_section.svg',(1,1,.3),'Section | low cup-to-bearing gallery; wool shown as a permeable envelope')
    all_bearings=[colored(i) for i in items if 'FixedBearing_' in i['id'] or i['id'].startswith('TransmissionFrame_')]
    shaded(all_bearings,out/'frame_with_oil_fittings.svg',(1,1,.7),'Four cap oil fittings installed | feed lines and mechanical lubricator pending')
    assert fingerprint()==lock and check_build(stage/'build')['native_hashes']==build['native_hashes']
    assert all(sha(ROOT/n)==digest for n,digest in hashes.items())
    report.update(rendering_complete=True,output_raster_hashes={p.name:sha(p) for p in out.glob('*.png')})
    write(out/'report.json',report)
    sys.exit(0 if passed else 1)
finally:runtime.close()
