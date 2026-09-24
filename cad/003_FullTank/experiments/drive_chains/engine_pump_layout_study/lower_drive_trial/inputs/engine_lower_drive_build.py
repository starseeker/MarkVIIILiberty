"""Create a lower-drive development assembly; casing integration remains open."""
import argparse
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,default=HERE/'engine_lower_drive_study')
p.add_argument('--controls',type=Path,default=HERE/'engine_lower_drive_controls.json')
p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--output',str(out),'--controls',str(a.controls.resolve()),'--worker'],
            env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App
    import Part
    from lib.cad_build import leaves,metadata,shape_signature
    from lib.worker import same_shape,placement_errors
    from engine_lower_drive_parts import parts
    parent=HERE/'engine_gear_build';pn=parent/'DrivetrainWithEngineGear.FCStd';pr=read(parent/'report.json')
    assert sha(pn)==pr['native_sha256']
    source=read(HERE/'engine_lower_drive_sources.json');c=read(a.controls)['controls']
    for rel,digest in source['source_assets'].items():assert sha(ROOT/rel)==digest,rel
    inputs={};(out/'inputs').mkdir(exist_ok=True)
    for path in [Path(__file__),a.controls.resolve(),HERE/'engine_lower_drive_parts.py',HERE/'engine_lower_drive_sources.json',
                 HERE/'transmission_bevel_tooth.py',HERE/'engine_crankshaft_parts.py',HERE/'engine_crossmember_parts.py',
                 HERE/'transmission_stud_parts.py',HERE/'transmission_input_installation_parts.py',HERE/'transmission_core_parts.py']:
        inputs[str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)]=sha(path)
        (out/'inputs'/path.name).write_bytes(path.read_bytes())
    write(out/'inputs/parent_report.json',pr)
    doc=App.openDocument(str(pn));old={r['id']:r for r in leaves(doc.Root)};assert len(old)==2153
    before={n:(shape_signature(i['shape']),App.Placement(i['shape'].Placement)) for n,i in old.items()}
    shapes,occ,rows,d=parts(c,pr['datums']['tooth_phase_deg'],
        lambda n,s:print(n,s.isValid(),len(s.Solids),flush=True))
    root=doc.addObject('App::Part','EngineLowerDistributionDrive');doc.TankLibertyEngine.addObject(root)
    root.Placement.Base=App.Vector(pr['datums']['gear_apex'],0,0)
    metadata(root,QuantityRole='Nonphysical assembly container',Subsystem='Powerplant',Coverage='partial',
        ReconstructionNotes='Development study: internal source fits represented; casing interference and missing casting lug/boss unresolved. Not qualified for standard integration.')
    groups={root.Name:root}
    for row in rows:
        obj=doc.addObject('App::Part',row['name']);groups[row['parent']].addObject(obj)
        obj.Placement=App.Placement(App.Vector(*row['xyz']),App.Rotation(*row['rotation']))
        metadata(obj,QuantityRole='Nonphysical clamp-set container',Subsystem='Powerplant',Coverage='partial')
        groups[obj.Name]=obj
    ownership=dict(driver=('LQ156A','SNL:83:033'),bush=('LQ159A','SNL:44:027'),
        housing_flywheel=('LQ160A','SNL:113:011'),housing_distributor=('LQ162A','SNL:113:016'),
        dowel=('LQ163A','SNL:113:017'),bolt=('LQ164A','SNL:25:020'),nut=('LQ89A','SNL:25:021'),
        washer=('LQ113A','SNL:25:023'),cotter=('Unmarked1/16x1/2in split pin','SNL:25:022'),
        retaining_screw=('LQ165A','SNL:206:010'))
    records={r['record_id']:r for r in source['records']};definitions={}
    for key,(mark,rid) in ownership.items():
        body=doc.addObject('PartDesign::Body','Def_EngineLowerDrive_'+key);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedLowerDrive').Shape=shapes[key]
        metadata(body,DefinitionId='engine_lower_drive_'+key,OriginalMark=mark,SurveyIds=records[rid]['part_ids'],
            SourceRecord=rid,Representation='assembly',Coverage='partial',Subsystem='Powerplant',GeometryInputs=c,
            ParameterUpdate='Regenerate engine_lower_drive_build.py from controls and frozen gear parent',
            ReconstructionNotes='Source-owned component study; unprinted shape and position estimates, smooth thread envelopes. Casing and service withdrawal unresolved; not an accepted installed assembly.')
        definitions[key]=body.Name
    for row in occ:
        obj=doc.addObject('App::Link',row['name']);groups[row['assembly']].addObject(obj)
        obj.setLink(doc.getObject(definitions[row['key']]))
        obj.LinkPlacement=App.Placement(App.Vector(*row['xyz']),App.Rotation(*row['rotation']))
        metadata(obj,OccurrenceId=row['name'],Subsystem='Powerplant',QuantityRole='One physical constituent in development study')
    doc.Definitions.Visibility=False;doc.recompute()
    App.ParamGet('User parameter:BaseApp/Preferences/Document').SetInt('CountBackupFiles',0)
    native=out/'DrivetrainWithLowerDriveStudy.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));items=leaves(doc.Root);byid={r['id']:r for r in items}
    assert len(items)==len(byid)==2170
    for name,(signature,pl) in before.items():
        t,ang=placement_errors(pl,byid[name]['shape'].Placement)
        assert same_shape(signature,shape_signature(byid[name]['shape'])) and t<1e-6 and ang<1e-8,name
    new=[r['name'] for r in occ]
    for name in new:
        s=byid[name]['shape'];assert s.isValid() and len(s.Solids)==1,name
    order=list(definitions.values())
    print('Saved and reopened2170physical occurrences; exporting development components.',flush=True)
    Part.setStaticValue('write.surfacecurve.mode',1)
    Part.makeCompound([doc.getObject(n).Shape for n in order]).exportStep(str(out/'LowerDriveDefinitions.step'))
    Part.makeCompound([byid[n]['shape'] for n in new]).exportStep(str(out/'LowerDriveInstallation.step'))
    write(out/'definition_order.json',order)
    write(out/'report.json',dict(status='unqualified_component_study',native_sha256=sha(native),parent_native_sha256=sha(pn),
        input_hashes=inputs,controls=c,datums=d,occurrences=occ,assemblies=rows,new_ids=new,changed_ids=[],
        native_occurrences=len(items),new_definitions=len(definitions),unchanged_parent_occurrences=2153,
        engine_origin=list(doc.TankLibertyEngine.Placement.Base),main_apex=pr['datums']['gear_apex'],
        standard_native_hashes=pr['standard_native_hashes'],standard_assembly_modified=False,
        historically_qualified=False,installation_qualified=False,complete_engine=False,complete_tank=False,
        pending=['Independent saved-native, material, STEP and source-view review','Casing interference and missing housing support',
                 'Reconcile estimated184mm pump axis with inherited154mm aperture','Housing screw boss and oil-pump withdrawal path',
                 'Upper distribution system and remaining engine systems','Standard integration and full-tank coverage'],
        artifact_hashes={f.name:sha(f) for f in out.glob('*.step')},freecad=App.Version(),occ=Part.OCC_VERSION))
    print('Complete component study:17new;2153parent occurrences retained; installation NOT qualified.',flush=True)
finally:
    runtime.close()
