"""Fit separate cap cleats, packing strips, rivets and detachable fastener sets."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage', type=Path, required=True)
parser.add_argument('--output', type=Path, default=ROOT/'casing_cap_build')
parser.add_argument('--worker', action='store_true')
args = parser.parse_args(); stage = args.stage.resolve(); out = args.output.resolve()
sys.path.insert(0, str(stage))
from lib import runtime
from lib.evidence import read, write, sha, fingerprint, database, REPO
if not args.worker:
    out.mkdir(parents=True, exist_ok=True)
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--output',str(out),'--worker'],
            env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App, Gui = runtime.start_gui()
    import Part
    import numpy as np
    from types import SimpleNamespace
    from collections import Counter
    from lib.cad_build import leaves, metadata
    from lib.worker import check_build
    from lib.wheel_parts import button_rivet
    from lib.visual_review import shaded
    from casing_mount_parts import cutter
    from casing_cap_parts import cap_joint, fasteners
    lock = fingerprint(); build = check_build(stage/'build')
    names = ['casing_cap_probe.py','casing_cap_parts.py','casing_cap_controls.json','casing_cap_fastener_sources.json',
             'casing_mount_parts.py','casing_parts.py','casing_controls.json','casing_source_rows.json',
             'casing_joint_review.json','installed_pitch_route_report.json','casing_shell_passage_build/report.json',
             'casing_wall_mount_build/report.json','casing_wall_mount_build/CasingWallMountCandidate.FCStd']
    paths = [ROOT/name for name in names]; hashes = {name:sha(path) for name,path in zip(names,paths)}
    # Keep exact authored study inputs with the result, including failed runs.
    for name,path in zip(names,paths):
        if '/' not in name:
            destination = out/'inputs'/name; destination.parent.mkdir(parents=True,exist_ok=True)
            destination.write_bytes(path.read_bytes())
    controls = read(ROOT/'casing_cap_controls.json'); a = {k:v['value'] for k,v in controls['controls'].items()}
    for name,expected in read(ROOT/'casing_cap_fastener_sources.json')['inspected_source_hashes'].items():
        assert sha(REPO/name)==expected, 'Changed inspected fastener source: '+name
    casing = {k:v['value'] for k,v in read(ROOT/'casing_controls.json')['controls'].items()}
    sources = read(ROOT/'casing_source_rows.json'); route = read(ROOT/'installed_pitch_route_report.json')
    shell = read(ROOT/'casing_shell_passage_build/report.json'); prior = read(paths[-2])
    assert prior['passed'] and prior['rendering_complete'] and prior['native_sha256']==sha(paths[-1])
    assert prior['authored_fingerprint']==lock and prior['tank_native_hashes']==build['native_hashes']
    tank = App.openDocument(build['build']['top_document']); tank.recompute()
    context = [i for i in leaves(tank.Root) if i['id'] not in
               {'hull_engine_back','PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting'}]
    doc = App.openDocument(str(paths[-1])); doc.recompute(); before = leaves(doc.Root)
    parts, stations, dimensions = cap_joint(a,casing,route,shell)
    removal_checks = []
    for owner in ['Body','Cap']:
        item = next(i for i in before if i['id']=='PortCasing_'+owner)
        tools = [cutter(s,a['rivet_diameter']+a['hole_diameter_clearance']) for s in stations['rivets'] if s['owner']==owner]
        updated = item['target'].Shape.cut(Part.makeCompound(tools)).removeSplitter()
        added = updated.cut(item['target'].Shape).Volume
        removed = item['target'].Shape.Volume-updated.Volume
        assert added<1e-5 and removed>0
        removal_checks.append(dict(definition=item['definition'],added_material_mm3=added,removed_material_mm3=removed))
        item['target'].Tip.Shape = updated
    definitions = {}

    def definition(name,shape,ids,mark='',record=''):
        obj = doc.addObject('PartDesign::Body','Def_CapJoint'+name); doc.Definitions.addObject(obj)
        feature = obj.newObject('PartDesign::Feature','Inferred'+name); feature.Shape = shape
        metadata(obj,DefinitionId='casing_cap_'+name,Representation='assembly',Coverage='partial',
                 SurveyIds=ids,OriginalMark=mark,SourceRecord=record)
        definitions[name] = obj

    for name,part in parts.items():
        definition(name,part['shape'],[sources['parts'][part['mark']]['part_id']],mark=part['mark'])
    records = dict(bolt='SNL:31:002',nut='SNL:128:001',washer='SNL:270:003',short='SNL:167:009',long='SNL:167:010')
    with database() as connection:
        identities = {role:[r[0] for r in connection.execute('select distinct part_id from part_evidence where record_id=?',(record,))]
                      for role,record in records.items()}
    assert all(len(ids)==1 for ids in identities.values())
    for name,shape in fasteners(a).items(): definition(name,shape,identities[name],record=records[name])
    for role in ['short','long']:
        rivet = button_rivet(doc,'Def_CapJoint'+role+'Rivet',a['rivet_diameter'],a[role+'_rivet_length'],
                            casing['sheet_stock']+a['cleat_stock'])
        doc.Definitions.addObject(rivet)
        metadata(rivet,DefinitionId='casing_cap_'+role+'_rivet',Representation='assembly',Coverage='partial',
                 SurveyIds=identities[role],SourceRecord=records[role])
        definitions[role] = rivet
    centers = {}; added_ids = []
    for hand in ['Port','Starboard']:
        cy = next(i for i in before if i['id']==hand+'Chain_RollerPinion')['shape'].Placement.Base.y
        centers[hand] = cy
        group = doc.addObject('App::Part',hand+'CasingCapJoint'); doc.Root.addObject(group)

        def link(name,key,center,axis=(0,1,0)):
            name = hand+'CasingCap_'+name
            obj = doc.addObject('App::Link',name); group.addObject(obj); obj.setLink(definitions[key])
            obj.LinkPlacement = App.Placement(App.Vector(*center)+App.Vector(0,cy,0),App.Rotation(App.Vector(0,1,0),App.Vector(*axis)))
            metadata(obj,OccurrenceId=name,Subsystem='Drivetrain'); added_ids.append(name)

        for name in parts: link(name,name,[0,0,0])
        for s in stations['rivets']: link(s['name'],s['length_role'],s['center'],s['axis'])
        for s in stations['bolts']:
            x,y,z = s['center']; grip = s['grip']
            link(s['name']+'Bolt','bolt',[x+grip/2,y,z],s['axis'])
            link(s['name']+'Washer','washer',[x-grip/2-a['washer_stock'],y,z],s['axis'])
            link(s['name']+'Nut','nut',[x-grip/2-a['washer_stock']-a['nut_stock'],y,z],s['axis'])
    metadata(doc.Root,Scope='Isolated chain/casing candidate with inferred removable-cap cleats and source-allocated hardware')
    doc.Definitions.Visibility = False; doc.recompute(); native = out/'CasingCapCandidate.FCStd'; doc.saveAs(str(native))
    App.closeDocument(doc.Name); doc = App.openDocument(str(native)); doc.recompute(); items = leaves(doc.Root)
    assert len(added_ids)==94 and len(items)==661
    for item in items:
        if not item['shape'].isValid() or len(item['shape'].Solids)!=1: raise ValueError('Invalid cap joint leaf '+item['id'])
    byid = {i['id']:i for i in items}; new = [byid[key] for key in added_ids]
    changed = new+[i for i in items if i['id'] in {h+'Casing_'+o for h in centers for o in ['Body','Cap']}]
    physical = [i for i in context if i['representation']=='assembly']+items
    boxes = np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].BoundBox for i in physical]])
    checked = set(); overlaps = []
    for first in changed:
        b = first['shape'].BoundBox; box = np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
        near = np.where(np.all(boxes[:,:3]<=box[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=box[:3]-1e-7,axis=1))[0]
        for n in near:
            second = physical[n]; pair = tuple(sorted([first['id'],second['id']]))
            if pair[0]==pair[1] or pair in checked: continue
            checked.add(pair); volume = first['shape'].common(second['shape']).Volume
            if volume>1e-5: overlaps.append(dict(a=first['id'],b=second['id'],volume_mm3=volume))
    bores, seats, retention = [], [], []
    for hand,cy in centers.items():
        def shape(key):return byid[hand+'CasingCap_'+key]['shape']
        for s in stations['rivets']:
            receivers = [shape(s['cleat']),byid[hand+'Casing_'+s['owner']]['shape']]
            tool = cutter(s,a['rivet_diameter']+a['hole_diameter_clearance']); tool.translate(App.Vector(0,cy,0))
            remaining = sum(receiver.common(tool).Volume for receiver in receivers)
            distances = [shape(s['name']).distToShape(receiver)[0] for receiver in receivers]
            bores.append(dict(side=hand,joint=s['name'],remaining_material_mm3=remaining,passed=remaining<1e-5))
            seats.append(dict(side=hand,joint=s['name'],receiver_distances_mm=distances,passed=max(distances)<1e-6))
        for s in stations['bolts']:
            keys = [s['body'],s['cap']]+([s['packing']] if s['packing'] else [])
            tool = cutter(s,a['bolt_diameter']+a['hole_diameter_clearance']); tool.translate(App.Vector(0,cy,0))
            remaining = sum(shape(key).common(tool).Volume for key in keys)
            bores.append(dict(side=hand,joint=s['name'],remaining_material_mm3=remaining,passed=remaining<1e-5))
            bolt,nut,washer = [shape(s['name']+suffix) for suffix in ['Bolt','Nut','Washer']]
            contacts = [bolt.distToShape(shape(s['body']))[0],washer.distToShape(shape(s['cap']))[0],nut.distToShape(washer)[0]]
            if s['packing']:
                contacts += [shape(s['packing']).distToShape(shape(key))[0] for key in [s['body'],s['cap']]]
            else:contacts.append(shape(s['body']).distToShape(shape(s['cap']))[0])
            seats.append(dict(side=hand,joint=s['name'],receiver_distances_mm=contacts,passed=max(contacts)<1e-6))
            protrusion = a['bolt_length']-s['grip']-a['washer_stock']-a['nut_stock']
            radial_gap = bolt.distToShape(nut)[0]
            retention.append(dict(side=hand,joint=s['name'],nut_axial_coverage_mm=a['nut_stock'],
                bolt_tip_protrusion_mm=protrusion,thread_envelope_radial_gap_mm=radial_gap,threads_modeled=False,
                passed=protrusion>0 and abs(radial_gap-a['thread_envelope_diameter_clearance']/2)<1e-6))
    mark_counts = Counter(parts[key]['mark'] for key in parts)
    assert {mark:count*2 for mark,count in mark_counts.items()}=={'M1583':8,'M1593':4,'M1584':4}
    assert fingerprint()==lock; check_build(stage/'build')
    passed = not overlaps and all(row['passed'] for row in bores+seats+retention)
    report = dict(complete=True,passed=passed,fixture_occurrences=len(items),new_cap_joint_occurrences=len(new),
        new_vehicle_mark_counts={mark:count*2 for mark,count in mark_counts.items()},bolt_sets=14,
        distinct_fastener_leaves=42,cleat_rivets=36,material_candidate_pairs=len(checked),overlaps=overlaps,
        bore_checks=bores,seat_checks=seats,retention_checks=retention,receiver_material_removal=removal_checks,
        dimensions=dimensions,stations=stations,input_sha256=hashes,native_sha256=sha(native),
        authored_fingerprint=lock,tank_native_hashes=build['native_hashes'],
        standard_assembly_modified=False,full_casing_bom_populated=False,historical_fit_qualified=False,
        source_fastener_schedule_reconciled=False,visual_review_status='pending',rendering_complete=False)
    write(out/'report.json',report)
    print('Cap joints:',len(new),'new leaves;',len(checked),'material pairs;',len(overlaps),'overlaps; passed=',passed,flush=True)
    one = [i for i in items if i['id'].startswith(('PortCasing_','PortCasingCap_','PortCasingWall_'))]
    shaded(one,out/'cap_joints_oblique.svg',(1,1,.8),'Casing cap joints | inferred cleats and separate source-allocated fasteners')
    sx = dimensions['seam_x_mm']; slab = Part.makeBox(150,400,500,App.Vector(sx-75,centers['Port']-200,1000))
    cropped = []
    for item in one:
        shape_ = item['shape'].common(slab)
        if not shape_.isNull():cropped.append(dict(item,shape=shape_,target=SimpleNamespace(Shape=shape_),definition=item['id']+'_crop'))
    shaded(cropped,out/'cap_joint_detail.svg',(-1,1,.65),'Cap joint crop | 3 + 3 side bolts and 1 roof bolt; nominal static fit')
    assert all(sha(p)==hashes[name] for name,p in zip(names,paths))
    report['rendering_complete']=True;write(out/'report.json',report)
    sys.exit(0 if passed else 1)
finally:
    runtime.close()
