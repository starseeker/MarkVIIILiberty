"""Develop engine transverse supports on the preserved drivetrain candidate."""
import argparse
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,default=HERE/'engine_crossmember_build')
p.add_argument('--controls',type=Path,default=HERE/'engine_crossmember_controls.json')
p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--output',str(out),'--controls',str(a.controls.resolve()),'--worker'],
            env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part
    from lib.cad_build import leaves,metadata,shape_signature
    from lib.worker import same_shape,placement_errors,check_build
    from engine_crossmember_parts import parts,box
    V=App.Vector
    App.ParamGet('User parameter:BaseApp/Preferences/Document').SetInt('CountBackupFiles',0)
    parent=HERE/'clutch_brake_linkage_build';pn=parent/'TransmissionWithClutchBrake.FCStd'
    pr=read(parent/'report.json');assert sha(pn)==pr['native_sha256']
    source=read(HERE/'engine_frame_sources.json')
    for rel,h in source['source_assets'].items():assert sha(ROOT/rel)==h,rel
    c=read(a.controls)['controls'];inputs={};(out/'inputs').mkdir(exist_ok=True)
    for path in [Path(__file__),HERE/'engine_crossmember_parts.py',HERE/'engine_frame_sources.json',a.controls.resolve()]:
        (out/'inputs'/path.name).write_bytes(path.read_bytes());inputs[str(path.relative_to(ROOT))]=sha(path)
    doc=App.openDocument(str(pn));old={i['id']:i for i in leaves(doc.Root)}
    before={n:(shape_signature(i['shape']),i['shape'].Placement) for n,i in old.items()}
    assert doc.Root.Placement.isIdentity()
    standard=check_build(STAGE/'build');tank=App.openDocument(standard['build']['top_document'])
    standard_items={i['id']:i for i in leaves(tank.Root)}
    floor_shapes={n:(old[n] if n in old else standard_items[n])['shape'].copy() for n in ['hull_floor_5','hull_floor_6','hull_floor_7']}
    floor_union=floor_shapes['hull_floor_5'].multiFuse([floor_shapes['hull_floor_6'],floor_shapes['hull_floor_7']]).removeSplitter()
    bounds=floor_union.BoundBox
    assert abs(bounds.ZMin-(c['floor_top']-c['floor_stock']))<1e-6 and abs(bounds.ZMax-c['floor_top'])<1e-6
    extents={'hull_floor_5':[c['floor_5_6_seam'],bounds.XMax],
             'hull_floor_6':[c['floor_6_7_seam'],c['floor_5_6_seam']],
             'hull_floor_7':[bounds.XMin,c['floor_6_7_seam']]}
    revised_floor={n:floor_union.common(box(x0,x1,bounds.YMin-1,bounds.YMax+1,bounds.ZMin-1,bounds.ZMax+1)) for n,(x0,x1) in extents.items()}
    print('Constructing source-allocated crossmember and floor joints.',flush=True)
    definitions,occ,datums=parts(c)
    for j in datums['floor_holes']:
        cutter=Part.makeCylinder(j['diameter']/2+c['hole_radial_allowance'],c['floor_stock']+2,V(*j['base'])-V(0,0,1))
        revised_floor[j['floor']]=revised_floor[j['floor']].cut(cutter).removeSplitter()
    group=doc.addObject('App::Part','PowerplantDevelopment');doc.Root.addObject(group)
    metadata(group,Subsystem='Powerplant',QuantityRole='Nonphysical assembly container',Coverage='partial')
    mounts=doc.addObject('App::Part','EngineMounts');group.addObject(mounts)
    groups={}
    for name in ['FrontCrossmember','RearCrossmember','FloorAttachments']:
        g=doc.addObject('App::Part',name);mounts.addObject(g);groups[name]=g
        metadata(g,QuantityRole='Nonphysical assembly container',Coverage='partial',ReconstructionNotes='SNL63/174-175 identities and counts; estimated member profiles and stations.')
    context=doc.addObject('App::Part','EngineFloorReplacementContext');doc.Root.addObject(context)
    metadata(context,QuantityRole='Replacement context; exclude duplicate standard floors on integration',Subsystem='HullStructure')
    identities={
        'front_channel':('M181','SNL:63:015; SNL:175:001'),
        'rear_channel':('M180','SNL63; SNL:175:001'),
        'cleat':('M189','SNL63; SNL171'),
        'left_gusset':('M186','SNL63; SNL:175:001'),
        'right_gusset':('M185','SNL63; SNL:175:001'),
        'front_rivet':('5/8 x 2-1/8in button rivet','SNL63; SNL171'),
        'rear_rivet':('11/16 x 2-1/8in button rivet','SNL63; SNL180-181'),
        'channel_floor_rivet':('11/16 x 1-7/8in button rivet','SNL:174:002; SNL:175:001'),
        'gusset_floor_rivet':('11/16 x 1-7/8in button rivet','SNL:174:002; SNL:175:001')}
    bodies={}
    for key,s in definitions.items():
        body=doc.addObject('PartDesign::Body','Def_EngineFrame_'+key);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedCrossmember').Shape=s
        metadata(body,DefinitionId='engine_frame_'+key,OriginalMark=identities[key][0],SourceRecord=identities[key][1],
            Representation='assembly',Coverage='partial',ParameterUpdate='Regenerate engine_crossmember_build.py from controls',
            ReconstructionNotes='Source identity, counts and nominal rivet blanks; profiles, stock, stations, heads, forming and fits estimated. Parallel flange simplification; no historical mounting qualification.')
        bodies[key]=body
    for row in occ:
        obj=doc.addObject('App::Link',row['name']);groups[row['assembly']].addObject(obj);obj.setLink(bodies[row['key']])
        obj.LinkPlacement=App.Placement(V(*row['xyz']),App.Rotation(*row['rotation']))
        metadata(obj,OccurrenceId=row['name'],Subsystem='Powerplant',QuantityRole='One physical component')
    for n,shape in revised_floor.items():
        assert shape.isValid() and len(shape.Solids)==1,n
        if n in old:
            target=old[n]['target'];world=old[n]['shape'].Placement.multiply(target.Shape.Placement.inverse())
            local=shape.copy();local.Placement=world.inverse().multiply(local.Placement);target.Tip.Shape=local
        else:
            target=doc.addObject('PartDesign::Body','Def_EngineContext_'+n);doc.Definitions.addObject(target)
            target.newObject('PartDesign::Feature','RepartitionedFloor').Shape=shape
            metadata(target,DefinitionId=n,OriginalMark='M193'+n[-1],Representation='assembly',Coverage='partial')
            obj=doc.addObject('App::Link','EngineContext_'+n);context.addObject(obj);obj.setLink(target)
            metadata(obj,OccurrenceId=n,Subsystem='HullStructure',QuantityRole='Replacement floor context; not additional tank plate')
        metadata(target,ReconstructionNotes='Estimated floor seam revised for source-named engine-frame receiving joints. Existing floor envelope/elevation and clutch holes preserved. Replace standard plate on integration.')
    doc.Definitions.Visibility=False;doc.recompute()
    definition_names=[b.Name for b in bodies.values()]+[old['hull_floor_7']['target'].Name,'Def_EngineContext_hull_floor_5','Def_EngineContext_hull_floor_6']
    native=out/'DrivetrainWithEngineCrossmembers.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));byid={i['id']:i for i in leaves(doc.Root)}
    new=[row['name'] for row in occ];contexts=['hull_floor_5','hull_floor_6'];changed=['hull_floor_7'];exchange=new+contexts+changed
    assert len(byid)==len(old)+len(new)+len(contexts)==1848
    for n,(sig,pl) in before.items():
        if n in changed:continue
        assert same_shape(sig,shape_signature(byid[n]['shape'])),n
        t,angle=placement_errors(pl,byid[n]['shape'].Placement);assert t<1e-6 and angle<1e-8,n
    for n in exchange:assert byid[n]['shape'].isValid() and len(byid[n]['shape'].Solids)==1,n
    Part.makeCompound([doc.getObject(n).Shape for n in definition_names]).exportStep(str(out/'EngineCrossmemberDefinitions.step'))
    Part.makeCompound([byid[n]['shape'] for n in exchange]).exportStep(str(out/'EngineCrossmemberInstallation.step'))
    write(out/'definition_order.json',definition_names)
    write(out/'report.json',dict(status='development_hypothesis_not_qualified',native_sha256=sha(native),parent_native_sha256=sha(pn),
        controls=c,datums=datums,floor_extents=extents,input_hashes=inputs,new_ids=new,context_ids=contexts,changed_ids=changed,
        exchange_ids=exchange,occurrences=occ,native_occurrences=len(byid),unchanged_parent_occurrences=1820,
        new_definitions=len(definitions),standard_native_hashes=pr['standard_native_hashes'],
        artifact_hashes={f.name:sha(f) for f in out.glob('*.step')},standard_assembly_modified=False,
        historical_mounting_proven=False,complete_engine_frame=False,complete_tank=False,
        source_inventory=source['inventory'],remaining_scope=source['scope'],headless=not App.GuiUp,freecad=App.Version(),occ=Part.OCC_VERSION))
    assert sha(pn)==pr['native_sha256']
    print('Saved 1848 physical occurrences:25 additions,2 replacement contexts,1 revised context;1820 parent occurrences preserved.',flush=True)
finally:
    runtime.close()
