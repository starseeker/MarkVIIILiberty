"""Develop the drum and flywheel with actual attachment and clutch interfaces."""
import argparse
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=HERE/'clutch_drum_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--output',str(out),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part,numpy as np
    from lib.cad_build import leaves,metadata,shape_signature
    from lib.worker import same_shape,placement_errors,check_build
    from clutch_drum_parts import build
    App.ParamGet('User parameter:BaseApp/Preferences/Document').SetInt('CountBackupFiles',0)
    parent=HERE/'clutch_retention_build';pn=parent/'TransmissionWithClutchRetention.FCStd';pq=read(parent/'qualification.json');pr=read(parent/'report.json')
    assert pq['passed'] and pq['accepted_for_main_clutch_development'] and sha(pn)==pq['native_sha256']==pr['native_sha256']
    source=read(HERE/'clutch_drum_sources.json')
    for rel,h in source['source_assets'].items():assert sha(ROOT/rel)==h,rel
    names=['clutch_drum_build.py','clutch_drum_parts.py','clutch_drum_controls.json','clutch_drum_sources.json',
        'transmission_input_parts.py','clutch_drive_parts.py','transmission_planet_parts.py','transmission_core_parts.py']
    hashes={str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in names};(out/'inputs').mkdir(exist_ok=True)
    for n in names:(out/'inputs'/n).write_bytes((HERE/n).read_bytes())
    c=read(HERE/'clutch_drum_controls.json')['controls'];cr=read(HERE/'clutch_cone_build/report.json')
    doc=App.openDocument(str(pn));old={i['id']:i for i in leaves(doc.Root)}
    before={n:(shape_signature(i['shape']),i['shape'].Placement) for n,i in old.items()}
    print('Constructing outer drum, toothed dished flywheel, six screws and two inward wire routes.',flush=True)
    parts,occ,retained,spines,d=build(c,cr,pr)
    original=old['ClutchRetention_Wire']['target'].Shape.copy();original.exportBrep(str(out/'inputs/parent_plunger_wire.brep'))
    original_overlap=original.common(parts['flywheel']).Volume
    print('Prior axial wire route/flywheel overlap',original_overlap,'mm3',flush=True)
    target=old['ClutchRetention_Wire']['target'];target.Tip.Shape=retained;retained_name=target.Name
    metadata(target,DrumRevision='Same30in wire and six head passages; paired tail routed radially inward for dished flywheel clearance. See I03-clutch-drum.')
    drum_group=doc.addObject('App::Part','ClutchOuterDrumAssembly');doc.TransmissionCore.addObject(drum_group)
    flywheel_group=doc.addObject('App::Part','EngineFlywheelAssembly');doc.Root.addObject(flywheel_group);flywheel_group.Placement=doc.TransmissionCore.Placement
    metadata(drum_group,Subsystem='Drivetrain',QuantityRole='Nonphysical assembly container')
    metadata(flywheel_group,Subsystem='Powerplant',QuantityRole='Nonphysical assembly container',ReconstructionNotes='One flywheel; complete crankshaft and retention still required.')
    ids={'drum':('SH866A','SNL:83:034'),'flywheel':('SH868A','SNL:95:015'),'screw':('SH866B','SNL:201:002'),'wire':('SH866C','SNL:276:004')}
    rows={r['record_id']:r for r in source['records']};bodies={}
    for key,shape in parts.items():
        body=doc.addObject('PartDesign::Body','Def_ClutchDrum_'+key);doc.Definitions.addObject(body);body.newObject('PartDesign::Feature','ReconstructedPart').Shape=shape
        mark,rid=ids[key]
        metadata(body,DefinitionId='clutch_drum_'+key,OriginalMark=mark,SurveyIds=rows[rid]['part_ids'],SourceRecord=rid,
            Representation='assembly',Coverage='partial',ParameterUpdate='Regenerate clutch_drum_build.py from controls',
            ReconstructionNotes='Working reconstruction: documented profiles, tooth form and source conflicts. No historical fit or completed engine claim.')
        bodies[key]=body
    for row in occ:
        key=row['key'];rid=ids[key][1];obj=doc.addObject('App::Link',row['name']);(flywheel_group if row['parent']=='Flywheel' else drum_group).addObject(obj);obj.setLink(bodies[key])
        obj.LinkPlacement=App.Placement(App.Vector(*row['xyz']),App.Rotation(*row['rotation']))
        metadata(obj,OccurrenceId=row['name'],SurveyIds=rows[rid]['part_ids'],SourceRecord=rid,Subsystem='Powerplant' if key=='flywheel' else 'Drivetrain',QuantityRole='One physical component')
    for name,spine in spines.items():spine.exportBrep(str(out/'inputs'/(name+'_wire_centerline.brep')))
    keys=[b.Name for b in bodies.values()]+[retained_name]
    doc.Definitions.Visibility=False;doc.recompute();native=out/'TransmissionWithClutchDrum.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name);doc=App.openDocument(str(native))
    items=leaves(doc.Root);byid={i['id']:i for i in items};changed=['ClutchRetention_Wire'];new=[row['name'] for row in occ];affected=changed+new
    assert len(items)==len(byid)==1662
    for name,i in byid.items():
        assert i['shape'].isValid() and len(i['shape'].Solids)==1,name
        if name in before and name not in changed:
            assert same_shape(before[name][0],shape_signature(i['shape'])),name
            t,r=placement_errors(i['shape'].Placement,before[name][1]);assert t<1e-6 and r<1e-8,name
    report=dict(status='working_candidate_not_qualified',native_sha256=sha(native),parent_native_sha256=sha(pn),parent_qualification_sha256=sha(parent/'qualification.json'),
        input_hashes=hashes,controls=c,datums=d,occurrences=occ,native_occurrences=len(items),new_ids=new,changed_ids=changed,affected_ids=affected,unchanged_parent_occurrences=1652,
        original_plunger_wire_flywheel_overlap_mm3=original_overlap,standard_assembly_modified=False,complete_clutch=False,complete_tank=False,
        headless=not App.GuiUp,freecad=App.Version(),occ=Part.OCC_VERSION)
    write(out/'definition_order.json',keys)
    for name,shapes in [('ClutchDrumDefinitions',[doc.getObject(k).Shape for k in keys]),('ClutchDrumInstallation',[byid[n]['shape'] for n in affected])]:Part.makeCompound(shapes).exportStep(str(out/(name+'.step')))
    report['artifact_hashes']={rel:sha(out/rel) for rel in ['ClutchDrumDefinitions.step','ClutchDrumInstallation.step','inputs/parent_plunger_wire.brep','inputs/drum_wire_centerline.brep','inputs/retention_wire_centerline.brep']}
    write(out/'report.json',report);print('Saved/reopened1662components;9new,one rerouted wire,1652preserved.',flush=True)
    standard=check_build(STAGE/'build');td=App.openDocument(standard['build']['top_document']);td.recompute()
    physical=items+[i for i in leaves(td.Root) if i['representation']=='assembly'];report['standard_native_hashes']=standard['native_hashes']
    boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].copy().cleaned().BoundBox for i in physical]])
    pairs=[];seen=set()
    for name in affected:
        s=byid[name]['shape'];b=s.copy().cleaned().BoundBox;bb=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
        near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
        for idx in near:
            other=physical[idx];pair=tuple(sorted([name,other['id']]))
            if name==other['id'] or pair in seen:continue
            seen.add(pair);pairs.append(dict(a=name,b=other['id'],intersection_mm3=s.common(other['shape']).Volume))
        overlaps=[x for x in pairs if abs(x['intersection_mm3'])>1e-5]
        write(out/'material_progress.json',dict(last=name,pairs=len(pairs),overlaps=overlaps));print(name,len(pairs),'pairs',len(overlaps),'overlaps',flush=True)
    report.update(material_pairs=len(pairs),material_passed=not overlaps,overlaps=overlaps,standard_context_checked=True)
    write(out/'material_checks.json',dict(passed=not overlaps,native_sha256=sha(native),pairs=pairs,standard_context_checked=True));write(out/'report.json',report)
    assert sha(pn)==pq['native_sha256']
    for rel,h in hashes.items():assert sha(ROOT/rel)==h,rel
    assert not overlaps,overlaps
finally:
    runtime.close()
