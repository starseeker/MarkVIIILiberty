"""Develop the stop band and lining with the source-sized coupled drive geometry."""
import argparse
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,default=HERE/'clutch_stop_band_build')
p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--output',str(out),'--worker'],
            env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part,numpy as np
    from lib.cad_build import leaves,metadata,shape_signature
    from lib.worker import same_shape,placement_errors,check_build
    from clutch_stop_brake_parts import receiving_drive,band_parts
    App.ParamGet('User parameter:BaseApp/Preferences/Document').SetInt('CountBackupFiles',0)
    parent=HERE/'clutch_drum_build';pn=parent/'TransmissionWithClutchDrum.FCStd'
    pq=read(parent/'qualification.json');assert pq['passed'] and sha(pn)==pq['native_sha256']
    source=read(HERE/'clutch_stop_brake_sources.json')
    for rel,h in source['source_assets'].items():assert sha(ROOT/rel)==h,rel
    names=['clutch_stop_band_build.py','clutch_stop_brake_parts.py','clutch_stop_brake_controls.json',
        'clutch_stop_brake_sources.json','clutch_drive_parts.py','air_pump_mount_parts.py',
        'air_pressure_pump_parts.py','clutch_cone_parts.py','transmission_input_controls.json']
    (out/'inputs').mkdir(exist_ok=True)
    hashes={str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in names}
    for n in names:(out/'inputs'/n).write_bytes((HERE/n).read_bytes())
    c=read(HERE/'clutch_stop_brake_controls.json')['controls']
    doc=App.openDocument(str(pn));old={i['id']:i for i in leaves(doc.Root)}
    before={n:(shape_signature(i['shape']),i['shape'].Placement) for n,i in old.items()}
    pr=read(HERE/'clutch_drive_build/report.json');mr=read(HERE/'air_pump_mount_build/report.json')
    cover=Part.Shape();cover.read(str(HERE/'air_pump_mount_build/inputs/parent_cover.brep'))
    housing=Part.Shape();housing.read(str(HERE/'air_pump_mount_build/inputs/parent_housing.brep'))
    print('Updating stop drum, belt closure and pump supports.',flush=True)
    drive,mounts,mount_occ,receivers,rd=receiving_drive(pr['controls'],pr['pump_controls'],
        pr['mount_controls'],read(HERE/'transmission_input_controls.json'),cover,housing)
    assert abs(c['drum_diameter']-rd['source_drum_diameter_mm'])<1e-8
    pump_before=doc.AirPressurePump.Placement.Base.z
    for key,shape in drive.items():doc.getObject('Def_ClutchDrive_'+key).Tip.Shape=shape
    for key,shape in mounts.items():doc.getObject('Def_PumpMount_'+key).Tip.Shape=shape
    for row in mount_occ:doc.getObject(row['name']).LinkPlacement=App.Placement(App.Vector(*row['xyz']),App.Rotation())
    for key,name in [('cover','CenterTransmissionCore_bevel_cover'),('housing','InputHousing_housing')]:
        assert same_shape(shape_signature(receivers[key]),shape_signature(old[name]['target'].Shape)),name
    doc.AirPressurePump.Placement=App.Placement(App.Vector(*rd['mounts']['pump_origin']),App.Rotation())
    metadata(doc.Def_ClutchDrive_drum,StopBrakeRevision='HB115 printed9.25in diameter replaces9in estimate; uniform wall and groove update together.')
    metadata(doc.Def_ClutchDrive_belt,StopBrakeRevision='Same54in source length; closure updated for printed stop-drum diameter.')
    print('Constructing band, lining, returned pin eye and17 source-count rivets.',flush=True)
    parts,occ,d,curves,blanks=band_parts(c)
    group=doc.addObject('App::Part','ClutchStopBandAssembly');doc.TransmissionCore.addObject(group)
    metadata(group,Subsystem='Drivetrain',QuantityRole='Nonphysical assembly container',
        ReconstructionNotes='Development band only; M4160 anchor, six anchor rivets and complete operating mechanism remain required.')
    ids={'band':('M4158','SNL:8:022'),'lining':('M4159','SNL:119:022'),
         'fold_rivet':('1/4x3/4in button rivet','SNL:8:024'),'lining_rivet':('3/16x1/2in copper countersunk rivet','SNL:8:026')}
    rows={r['record_id']:r for r in source['records']};bodies={}
    for key,shape in parts.items():
        body=doc.addObject('PartDesign::Body','Def_ClutchStopBand_'+key);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedPart').Shape=shape
        mark,rid=ids[key]
        metadata(body,DefinitionId='clutch_stop_band_'+key,OriginalMark=mark,SurveyIds=rows[rid]['part_ids'],
            SourceRecord=rid,Representation='assembly',Coverage='partial',ParameterUpdate='Regenerate clutch_stop_band_build.py from controls',
            ReconstructionNotes='Development: printed stock/counts, inferred strip return, clock, head profiles and fit. Not a complete installed brake.')
        bodies[key]=body
    for row in occ:
        obj=doc.addObject('App::Link',row['name']);group.addObject(obj);obj.setLink(bodies[row['key']])
        obj.LinkPlacement=App.Placement(App.Vector(*row['xyz']),App.Rotation(*row['rotation']))
        rid=ids[row['key']][1]
        metadata(obj,OccurrenceId=row['name'],SurveyIds=rows[rid]['part_ids'],SourceRecord=rid,
            Subsystem='Drivetrain',QuantityRole='One physical component')
    for name,shape in dict(curves,**{k+'_blank':s for k,s in blanks.items()}).items():
        shape.exportBrep(str(out/'inputs'/(name+'.brep')))
    doc.Definitions.Visibility=False;doc.recompute()
    native=out/'TransmissionWithClutchStopBand.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));items=leaves(doc.Root);byid={i['id']:i for i in items}
    changed=['ClutchDrive_drum','ClutchDrive_belt']+mr['new_ids'];new=[row['name'] for row in occ]
    assert len(items)==len(byid)==1681 and len(changed)==85 and len(new)==19
    dz=rd['mounts']['pump_origin'][2]-pump_before
    for name,i in byid.items():
        assert i['shape'].isValid() and len(i['shape'].Solids)==1,name
        if name in old and name not in changed:
            assert same_shape(before[name][0],shape_signature(i['shape'])),name
            t,angle=placement_errors(i['shape'].Placement,before[name][1]);assert t<1e-6 and angle<1e-8,name
        elif name.startswith('AirPump_'):
            expected=old[name]['shape'].copy();expected.translate(App.Vector(0,0,dz))
            assert same_shape(shape_signature(expected),shape_signature(i['shape'])),name
    report=dict(status='working_candidate_not_qualified',native_sha256=sha(native),parent_native_sha256=sha(pn),
        parent_qualification_sha256=sha(parent/'qualification.json'),input_hashes=hashes,controls=c,datums=d,
        receiving_drive=rd,occurrences=occ,native_occurrences=len(items),new_ids=new,changed_ids=changed,
        affected_ids=changed+new,unchanged_parent_occurrences=1577,pump_height_change_mm=dz,
        standard_assembly_modified=False,complete_brake=False,complete_clutch=False,complete_tank=False,
        headless=not App.GuiUp,freecad=App.Version(),occ=Part.OCC_VERSION)
    keys=[b.Name for b in bodies.values()];write(out/'definition_order.json',keys)
    Part.makeCompound([doc.getObject(k).Shape for k in keys]).exportStep(str(out/'ClutchStopBandDefinitions.step'))
    Part.makeCompound([byid[n]['shape'] for n in new]).exportStep(str(out/'ClutchStopBandInstallation.step'))
    report['artifact_hashes']={p.name:sha(p) for p in out.glob('*.step')}
    write(out/'report.json',report);print('Saved/reopened1681components;19new,85affected,1577preserved.',flush=True)
    standard=check_build(STAGE/'build');td=App.openDocument(standard['build']['top_document'])
    physical=items+[i for i in leaves(td.Root) if i['representation']=='assembly']
    report['standard_native_hashes']=standard['native_hashes']
    boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].copy().cleaned().BoundBox for i in physical]])
    pairs=[];seen=set()
    for name in report['affected_ids']:
        s=byid[name]['shape'];b=s.copy().cleaned().BoundBox;bb=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
        near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
        for idx in near:
            other=physical[idx];pair=tuple(sorted([name,other['id']]))
            if name==other['id'] or pair in seen:continue
            seen.add(pair);pairs.append(dict(a=name,b=other['id'],intersection_mm3=s.common(other['shape']).Volume))
        overlaps=[x for x in pairs if abs(x['intersection_mm3'])>1e-5]
        write(out/'material_progress.json',dict(last=name,pairs=len(pairs),overlaps=overlaps))
        print(name,len(pairs),'pairs',len(overlaps),'overlaps',flush=True)
    report.update(material_pairs=len(pairs),material_passed=not overlaps,overlaps=overlaps,standard_context_checked=True)
    write(out/'material_checks.json',dict(passed=not overlaps,native_sha256=sha(native),pairs=pairs,standard_context_checked=True))
    write(out/'report.json',report)
    assert sha(pn)==pq['native_sha256']
    for rel,h in hashes.items():assert sha(ROOT/rel)==h,rel
    assert not overlaps,overlaps
finally:
    runtime.close()
