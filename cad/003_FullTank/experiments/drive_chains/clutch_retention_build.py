"""Add actual plunger-head holes and SH861K wire to the qualified clutch assembly."""
import argparse
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,default=HERE/'clutch_retention_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--output',str(out),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part,numpy as np
    from lib.cad_build import leaves,metadata,shape_signature
    from lib.worker import same_shape,placement_errors,check_build
    from clutch_retention_parts import build
    App.ParamGet('User parameter:BaseApp/Preferences/Document').SetInt('CountBackupFiles',0)
    parent=HERE/'clutch_cone_build';pn=parent/'TransmissionWithClutchCone.FCStd';pq=read(parent/'qualification.json');pr=read(parent/'report.json')
    assert pq['passed'] and pq['accepted_for_main_clutch_development'] and sha(pn)==pq['native_sha256']==pr['native_sha256']
    source=read(HERE/'clutch_retention_sources.json')
    for rel,h in source['source_assets'].items():assert sha(ROOT/rel)==h,rel
    names=['clutch_retention_build.py','clutch_retention_parts.py','clutch_retention_controls.json','clutch_retention_sources.json',
        'clutch_collar_parts.py','air_pressure_pump_parts.py','transmission_input_parts.py','clutch_drive_parts.py']
    hashes={str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in names}
    (out/'inputs').mkdir(exist_ok=True)
    for n in names:(out/'inputs'/n).write_bytes((HERE/n).read_bytes())
    c=read(HERE/'clutch_retention_controls.json')['controls']
    doc=App.openDocument(str(pn));old={i['id']:i for i in leaves(doc.Root)}
    before={n:(shape_signature(i['shape']),i['shape'].Placement) for n,i in old.items()}
    target=old['ClutchCone_Plunger1']['target'];blank=target.Shape.copy();blank.exportBrep(str(out/'inputs/plunger_blank.brep'))
    plunger,wire,spine,occ,d=build(c,pr,blank)
    target.Tip.Shape=plunger
    metadata(target,RetentionRevision='Six tangential head bores for SH861K; regenerate clutch_retention_build.py from controls.')
    for row in occ:
        obj=old[row['name']]['object'];obj.LinkPlacement=App.Placement(App.Vector(*row['xyz']),App.Rotation(App.Vector(1,0,0),row['angle']))
    row=next(r for r in source['records'] if r['record_id']=='SNL:275:024')
    body=doc.addObject('PartDesign::Body','Def_ClutchRetention_wire');doc.Definitions.addObject(body)
    body.newObject('PartDesign::Feature','ReconstructedWire').Shape=wire
    metadata(body,DefinitionId='clutch_retention_wire',OriginalMark='SH861K',SurveyIds=row['part_ids'],SourceRecord=row['record_id'],
        Representation='assembly',Coverage='partial',ParameterUpdate='Regenerate clutch_retention_build.py from controls',
        ReconstructionNotes='30in soft-iron wire; modeled1.5mm diameter and route inferred. No historical gauge conversion or strength qualification.')
    obj=doc.addObject('App::Link','ClutchRetention_Wire');doc.ClutchConeSprings.addObject(obj);obj.setLink(body)
    metadata(obj,OccurrenceId=obj.Name,SurveyIds=row['part_ids'],SourceRecord=row['record_id'],Subsystem='Drivetrain',QuantityRole='One physical component')
    spine.exportBrep(str(out/'inputs/wire_centerline.brep'))
    keys=[target.Name,body.Name]
    doc.Definitions.Visibility=False;doc.recompute();native=out/'TransmissionWithClutchRetention.FCStd'
    doc.saveAs(str(native));App.closeDocument(doc.Name);doc=App.openDocument(str(native))
    items=leaves(doc.Root);byid={i['id']:i for i in items};changed=[r['name'] for r in occ];new=['ClutchRetention_Wire'];affected=changed+new
    assert len(items)==len(byid)==1653
    for n,i in byid.items():
        assert i['shape'].isValid() and len(i['shape'].Solids)==1,n
        if n in before and n not in changed:
            assert same_shape(before[n][0],shape_signature(i['shape'])),n
            t,r=placement_errors(i['shape'].Placement,before[n][1]);assert t<1e-6 and r<1e-8,n
    report=dict(native_sha256=sha(native),parent_native_sha256=sha(pn),parent_qualification_sha256=sha(parent/'qualification.json'),
        input_hashes=hashes,controls=c,datums=d,occurrences=occ,native_occurrences=len(items),new_ids=new,changed_ids=changed,affected_ids=affected,
        unchanged_parent_occurrences=1646,standard_assembly_modified=False,complete_clutch=False,complete_tank=False,
        headless=not App.GuiUp,freecad=App.Version(),occ=Part.OCC_VERSION)
    write(out/'definition_order.json',keys)
    for name,shapes in [('ClutchRetentionDefinitions',[doc.getObject(k).Shape for k in keys]),('ClutchRetentionInstallation',[byid[n]['shape'] for n in affected])]:
        Part.makeCompound(shapes).exportStep(str(out/(name+'.step')))
    report['artifact_hashes']={rel:sha(out/rel) for rel in ['ClutchRetentionDefinitions.step','ClutchRetentionInstallation.step','inputs/plunger_blank.brep','inputs/wire_centerline.brep']}
    write(out/'report.json',report);print('Saved/reopened1653components;one wire,six revised heads,1646preserved.',flush=True)
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
