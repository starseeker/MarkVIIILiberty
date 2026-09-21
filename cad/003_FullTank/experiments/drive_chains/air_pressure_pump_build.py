"""Build and inspect the air-pressure pump; supports and vehicle fit remain pending."""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent
STAGE=HERE.parents[1]
REPO=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,default=HERE/'air_pressure_pump_build')
p.add_argument('--worker',action='store_true')
p.add_argument('--skip-render',action='store_true')
a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        cmd=[sys.executable,__file__,'--worker','--output',str(out)]
        if a.skip_render:cmd.append('--skip-render')
        sys.exit(subprocess.run(cmd,env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)

try:
    App,Gui=runtime.start_gui()
    import Part,numpy as np
    from lib.cad_build import leaves,metadata,COLORS
    from lib.visual_review import shaded
    from air_pressure_pump_parts import build,moved
    controls=read(HERE/'air_pressure_pump_controls.json');c=controls['controls']
    dossier=read(HERE/'air_pressure_pump_sources.json')
    rows={r['record_id']:r for r in dossier['records']}
    paths=[Path(__file__),HERE/'air_pressure_pump_parts.py',HERE/'air_pressure_pump_controls.json',HERE/'air_pressure_pump_sources.json']
    hashes={str(p.relative_to(REPO)):sha(p) for p in paths}
    for path in paths:
        dst=out/'inputs'/path.name;dst.parent.mkdir(exist_ok=True);dst.write_bytes(path.read_bytes())
    for path,h in dossier['source_assets'].items():assert sha(REPO/path)==h,path
    parts,occ,details=build(c)
    print('Constructed',len(parts),'definitions and',len(occ),'physical pump occurrences.',flush=True)
    identity=dict(base=('SH903A','SNL:159:006'),bearing=('SH900A','SNL:159:007'),
        bush=('SH901C','SNL:159:008'),check_nut=('SH901B','SNL:159:009'),
        cylinder=('SH900C','SNL:159:010'),displacement_plug=('SH901E','SNL:159:011'),
        piston=('SH901D','SNL:159:012'),pulley=('SH900B','SNL:159:013'),
        shaft=('SH900D','SNL:209:022'),shaft_nut=('','SNL:209:023'),
        spring_high=('SH901A','SNL:159:015'),spring_low=('SH901A','SNL:159:015'),
        key=('No.5','SNL:159:017'),pipe_plug=('Q52A','SNL:159:018'),
        cylinder_screw=('','SNL:159:019'),bearing_screw=('','SNL:159:020'),air_cover=('SH901F','SNL:159:005'))
    doc=App.newDocument('AirPressurePump')
    root=doc.addObject('App::Part','Root');root.Label='Mark VIII air-pressure pump | approximate reconstruction'
    library=doc.addObject('App::DocumentObjectGroup','Definitions')
    metadata(root,SurveyIds=['P_dd55a02fabc8964b'],Subsystem='FuelPressure',
        Scope='51 pump-core pieces; twelve base fasteners and transmission supports deferred. Internal passages and absolute dimensions approximate.')
    bodies={};groups={}
    for key,shape in parts.items():
        body=doc.addObject('PartDesign::Body','Def_AirPump_'+key);library.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedPart').Shape=shape
        mark,record=identity[key]
        metadata(body,DefinitionId='air_pressure_pump_'+key,OriginalMark=mark,
            SurveyIds=rows[record]['part_ids'],SourceRecord=record,Representation='assembly',Coverage='partial',
            ParameterUpdate='Rebuild air_pressure_pump_build.py from air_pressure_pump_controls.json',
            ReconstructionNotes='Source form/count; estimated dimensions and internal details. No historical machining-fit claim.')
        bodies[key]=body
    for row in occ:
        name=row['parent']
        if name not in groups:
            groups[name]=doc.addObject('App::Part','Pump_'+name);root.addObject(groups[name])
        link=doc.addObject('App::Link','AirPump_'+row['name']);groups[name].addObject(link)
        link.setLink(bodies[row['key']]);link.LinkPlacement=App.Placement(App.Vector(*row['xyz']),App.Rotation(*row['rotation']))
        metadata(link,OccurrenceId=link.Name,Subsystem='FuelPressure',SourceRecord=identity[row['key']][1])
    library.Visibility=False;doc.recompute();native=out/'AirPressurePump.FCStd'
    doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root)
    assert len(items)==51 and len({i['id'] for i in items})==51
    assert all(i['shape'].isValid() and len(i['shape'].Solids)==1 for i in items)
    report=dict(status='pump_core_candidate_supports_pending',native_sha256=sha(native),
        input_hashes=hashes,controls=c,details=details,definition_count=len(parts),physical_occurrences=len(items),
        catalogue_expanded_count=63,deferred_base_fastener_pieces=12,complete_installation=False,
        complete_tank=False,historical_fit_qualified=False,rendering_complete=False)
    write(out/'report.json',report)
    pairs=[];overlaps=[]
    for index,item in enumerate(items):
        s=item['shape'];b=s.copy().cleaned().BoundBox
        for other in items[index+1:]:
            ob=other['shape'].copy().cleaned().BoundBox
            if not b.intersect(ob):continue
            v=s.common(other['shape']).Volume
            pairs.append(dict(a=item['id'],b=other['id'],intersection_mm3=v))
            if v>1e-5:overlaps.append(pairs[-1])
    report.update(material_pairs=len(pairs),overlaps=overlaps,local_geometry_passed=not overlaps,
        counts=dict(Counter(i['definition'] for i in items)))
    write(out/'material_checks.json',dict(pairs=pairs,passed=not overlaps,native_sha256=sha(native)))
    write(out/'report.json',report)
    print('Material checks:',len(pairs),'pairs;',len(overlaps),'overlaps',flush=True)
    if overlaps:print(json.dumps(overlaps,indent=2),flush=True)
    # One STEP solid per reusable shape, in definition coordinates.
    exchange=out/'AirPressurePumpDefinitions.step'
    keys=list(parts)
    Part.makeCompound([doc.getObject('Def_AirPump_'+k).Shape for k in keys]).exportStep(str(exchange))
    write(out/'definition_order.json',keys)
    report['step_sha256']=sha(exchange);write(out/'report.json',report)
    assembly_step=out/'AirPressurePump.step'
    Part.makeCompound([i['shape'] for i in items]).exportStep(str(assembly_step))
    report['assembly_step_sha256']=sha(assembly_step);write(out/'report.json',report)
    if not a.skip_render:
        view=out/'previews';view.mkdir(exist_ok=True)
        COLORS.update(PumpCase=(.45,.56,.46),PumpSteel=(.62,.66,.68),PumpBrass=(.76,.57,.23),PumpSpring=(.38,.41,.44))
        def draw(file,title,direction,clip=None,omit=()):
            selected=[]
            for i in items:
                key=i['definition'].removeprefix('air_pressure_pump_')
                if key in omit:continue
                shape=i['shape'] if clip is None else i['shape'].common(clip)
                if shape.isNull() or not shape.Solids:continue
                system='PumpSpring' if key.startswith('spring') else ('PumpBrass' if key in ['bush','pipe_plug','air_cover'] else ('PumpCase' if key in ['base','cylinder','bearing'] else 'PumpSteel'))
                selected.append(dict(id=i['id'],shape=shape,target=SimpleNamespace(Shape=shape),definition=i['id'],representation='assembly',system=system))
            shaded(selected,view/(file+'.svg'),direction,title)
        draw('isometric','Air-pressure pump | 51 core pieces; dimensions approximate',(1,1,.7))
        draw('internals','Air-pressure pump | cam shaft, pistons, springs and displacement plugs',(1,1,.5),omit=['base','bearing','cylinder','pulley','pipe_plug','air_cover','bearing_screw','cylinder_screw','check_nut','shaft_nut'])
        clip=Part.makeBox(400,400,400,App.Vector(c['station_x'][0],-200,-150))
        draw('bank_section','Air-pressure pump | transverse section through rear cam',(-1,.15,.12),clip=clip,omit=['pulley'])
        draw('end','Air-pressure pump | end view; compare SNL Plate5',(-1,0,0))
        draw('top','Air-pressure pump | top view; compare SNL Plate5',(0,0,1))
        report.update(rendering_complete=True,render_hashes={p.name:sha(p) for p in view.glob('*.png')})
        write(out/'report.json',report)
    for path,h in hashes.items():assert sha(REPO/path)==h,path
    assert sha(native)==report['native_sha256']
    print('Saved native pump, definition STEP and review artifacts.',flush=True)
    assert not overlaps,'Physical pump intersections remain; see material_checks.json'
finally:
    runtime.close()
