"""Build the connected cone and six spring sets in the qualified transmission."""
import argparse
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,default=HERE/'clutch_cone_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--output',str(out),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part,numpy as np
    from lib.cad_build import leaves,metadata,shape_signature
    from lib.worker import same_shape,placement_errors,check_build
    from clutch_cone_parts import build
    App.ParamGet('User parameter:BaseApp/Preferences/Document').SetInt('CountBackupFiles',0)
    parent=HERE/'clutch_thrust_build';pn=parent/'TransmissionWithClutchThrust.FCStd';pq=read(parent/'qualification.json')
    assert pq['passed'] and pq['accepted_for_main_clutch_development'] and sha(pn)==pq['native_sha256']
    sources=read(HERE/'clutch_cone_sources.json')
    for path,h in sources['source_assets'].items():assert sha(ROOT/path)==h,path
    names=['clutch_cone_build.py','clutch_cone_parts.py','clutch_cone_controls.json','clutch_cone_sources.json',
           'front_clutch_parts.py','air_pressure_pump_parts.py','transmission_input_parts.py']
    hashes={str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in names}
    (out/'inputs').mkdir(exist_ok=True)
    for n in names:(out/'inputs'/n).write_bytes((HERE/n).read_bytes())
    pc=read(parent/'report.json')['parent_controls'];tc=read(parent/'report.json')['controls'];c=read(HERE/'clutch_cone_controls.json')['controls']
    doc=App.openDocument(str(pn));old={i['id']:i for i in leaves(doc.Root)}
    before={n:(shape_signature(i['shape']),i['shape'].Placement) for n,i in old.items()}
    old['ClutchStack_support']['target'].Shape.exportBrep(str(out/'inputs/parent_support.brep'))
    print('Constructing cone, receiving support and spring sets.',flush=True)
    parts,occ,support,spine,datums,blanks=build(c,pc,tc)
    for name,shape in blanks.items():shape.exportBrep(str(out/'inputs'/(name+'_blank.brep')))
    old['ClutchStack_support']['target'].Tip.Shape=support
    metadata(old['ClutchStack_support']['target'],ConeRevision='Inclined cone joint, six cup guides and lubrication port; keyed running interface preserved. I03-clutch-cone.')
    cone=doc.addObject('App::Part','ClutchConeAssembly');doc.TransmissionCore.addObject(cone)
    metadata(cone,SourceRecord='SNL:68:010',QuantityRole='Nonphysical assembly container')
    link=old['ClutchStack_support']['object'];link.getParentGeoFeatureGroup().removeObject(link);cone.addObject(link)
    springs=doc.addObject('App::Part','ClutchConeSprings');doc.TransmissionCore.addObject(springs)
    rows={r['record_id']:r for r in sources['records']}
    identities={'cone':('SH876A','SNL:68:012'),'lining':('SH997C','SNL:68:014'),
        'plug':('Q52A','SNL:68:015'),'support_rivet':('5/16x1-1/8 button rivet','SNL:68:016'),
        'lining_rivet':('3/16x11/16 countersunk copper rivet','SNL:68:017'),
        'plunger':('SH861A','SNL:157:018'),'cup':('SH861C','SNL:164:006'),
        'spring':('SH861F','SNL:219:025'),'ring':('SH849C','SNL:165:002')}
    bodies={}
    for key,shape in parts.items():
        body=doc.addObject('PartDesign::Body','Def_ClutchCone_'+key);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedPart').Shape=shape
        mark,rid=identities[key]
        metadata(body,DefinitionId='clutch_cone_'+key,OriginalMark=mark,SurveyIds=rows[rid]['part_ids'],SourceRecord=rid,
            Representation='assembly',Coverage='partial',ParameterUpdate='Regenerate clutch_cone_build.py from controls',
            ReconstructionNotes='Source quantities; conditional HB dimensions; estimated interfaces and finishing. See I03-clutch-cone.')
        bodies[key]=body
    for row in occ:
        key=row['key'];rid=identities[key][1];obj=doc.addObject('App::Link',row['name'])
        (cone if row['parent']=='Cone' else springs).addObject(obj);obj.setLink(bodies[key])
        obj.LinkPlacement=App.Placement(App.Vector(*row['xyz']),App.Rotation(*row['rotation']))
        metadata(obj,OccurrenceId=row['name'],SurveyIds=rows[rid]['part_ids'],SourceRecord=rid,Subsystem='Drivetrain',QuantityRole='One physical component')
    spine.exportBrep(str(out/'inputs/spring_centerline.brep'))
    doc.Definitions.Visibility=False;doc.recompute();native=out/'TransmissionWithClutchCone.FCStd'
    doc.saveAs(str(native));App.closeDocument(doc.Name);doc=App.openDocument(str(native));doc.recompute()
    items=leaves(doc.Root);byid={i['id']:i for i in items};new=[i['name'] for i in occ];changed=['ClutchStack_support'];affected=changed+new
    assert len(items)==len(byid)==1652
    for n,i in byid.items():
        assert i['shape'].isValid() and len(i['shape'].Solids)==1,n
        if n in before and n not in changed:
            assert same_shape(before[n][0],shape_signature(i['shape'])),n
            t,r=placement_errors(i['shape'].Placement,before[n][1]);assert t<1e-6 and r<1e-8,n
    report=dict(native_sha256=sha(native),parent_native_sha256=sha(pn),parent_qualification_sha256=sha(parent/'qualification.json'),
        input_hashes=hashes,parent_support_sha256=sha(out/'inputs/parent_support.brep'),controls=c,parent_controls=pc,thrust_controls=tc,
        datums=datums,occurrences=occ,native_occurrences=len(items),new_ids=new,changed_ids=changed,affected_ids=affected,
        unchanged_parent_occurrences=1580,standard_assembly_modified=False,complete_clutch=False,complete_tank=False,
        headless=not App.GuiUp,freecad=App.Version(),occ=Part.OCC_VERSION)
    write(out/'report.json',report);print('Saved/reopened1652components;71new,1refined,1580preserved.',flush=True)
    keys=['Def_ClutchCone_'+key for key in parts]+[byid['ClutchStack_support']['target'].Name]
    path=out/'ClutchConeDefinitions.step';Part.makeCompound([doc.getObject(key).Shape for key in keys]).exportStep(str(path));report['definition_step_sha256']=sha(path)
    write(out/'definition_order.json',keys)
    path=out/'ClutchConeInstallation.step';Part.makeCompound([byid[n]['shape'] for n in affected]).exportStep(str(path));report['step_sha256']=sha(path)
    write(out/'report.json',report)
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
            seen.add(pair);v=s.common(other['shape']).Volume;pairs.append(dict(a=name,b=other['id'],intersection_mm3=v))
        overlaps=[x for x in pairs if abs(x['intersection_mm3'])>1e-5]
        write(out/'material_progress.json',dict(last=name,pairs=len(pairs),overlaps=overlaps));print(name,len(pairs),'pairs',len(overlaps),'overlaps',flush=True)
    report.update(material_pairs=len(pairs),material_passed=not overlaps,overlaps=overlaps,standard_context_checked=True)
    write(out/'material_checks.json',dict(passed=not overlaps,native_sha256=sha(native),pairs=pairs,standard_context_checked=True))
    write(out/'report.json',report)
    assert sha(pn)==pq['native_sha256']
    for rel,h in hashes.items():assert sha(ROOT/rel)==h,rel
    assert not overlaps,overlaps
finally:
    runtime.close()
