"""Build provisional clutch supports and auxiliary controls on a physical floor copy."""
import argparse
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent; STAGE=HERE.parents[1]; ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,default=HERE/'clutch_support_build')
p.add_argument('--controls',type=Path,default=HERE/'clutch_support_controls.json')
p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--output',str(out),'--controls',str(a.controls.resolve()),'--worker'],
            env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App, Part
    from lib.cad_build import leaves,metadata,shape_signature
    from lib.worker import same_shape,placement_errors,check_build
    from clutch_support_parts import parts
    App.ParamGet('User parameter:BaseApp/Preferences/Document').SetInt('CountBackupFiles',0)
    parent=HERE/'clutch_throwout_build';pn=parent/'TransmissionWithClutchThrowout.FCStd'
    checkpoint=read(parent/'development_checkpoint.json');assert sha(pn)==checkpoint['native_sha256']
    sources=read(HERE/'clutch_support_sources.json')
    for rel,h in sources['source_assets'].items():assert sha(ROOT/rel)==h,rel
    c=read(a.controls)['controls']; inherited=read(parent/'report.json')['controls']
    (out/'inputs').mkdir(exist_ok=True)
    names=['clutch_support_build.py','clutch_support_parts.py','clutch_support_sources.json',
           'clutch_throwout_parts.py','transmission_stud_parts.py','transmission_input_installation_parts.py',
           'transmission_input_parts.py','transmission_support_parts.py','transmission_output_parts.py']
    inputs={str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in names}
    for n in names:(out/'inputs'/n).write_bytes((HERE/n).read_bytes())
    (out/'inputs/clutch_support_controls.json').write_bytes(a.controls.read_bytes())
    inputs[str(a.controls.resolve().relative_to(ROOT))]=sha(a.controls)
    doc=App.openDocument(str(pn));old={i['id']:i for i in leaves(doc.Root)}
    before={n:(shape_signature(i['shape']),i['shape'].Placement) for n,i in old.items()}
    origin=doc.TransmissionCore.Placement.Base
    standard=check_build(STAGE/'build');tank=App.openDocument(standard['build']['top_document'])
    floor_item=next(i for i in leaves(tank.Root) if i['id']=='hull_floor_7')
    original_floor=floor_item['shape'].copy();bb=original_floor.copy().cleaned().BoundBox
    floor_base=App.Vector((bb.XMin+bb.XMax)/2,0,bb.ZMin)
    floor=original_floor.copy();floor.translate(-floor_base)
    # Close the standard documents only after copying their physical geometry.
    for name in list(App.listDocuments()):
        if name!=doc.Name:App.closeDocument(name)
    print('Constructing bracket/auxiliary-control hypothesis.',flush=True)
    main=old['ClutchThrowout_Shaft']['target'].Shape.copy()
    definitions,occ,revisions,datums=parts(c,main,inherited,bb.ZMax-origin.z,bb.ZLength)
    for m in datums['mounts']:
        world=origin+App.Vector(*m['center'])
        tool=Part.makeCylinder(m['diameter']/2+c['cap_hole_clearance'],bb.ZLength+2,
                              App.Vector(world.x,world.y,bb.ZMin-1)-floor_base,App.Vector(0,0,1))
        floor=floor.cut(tool)
    definitions['floor_revision']=floor.removeSplitter()
    for ident,shape in revisions.items():old[ident]['target'].Tip.Shape=shape
    shaft_body=old['ClutchThrowout_Shaft']['target']
    metadata(shaft_body,ReconstructionNotes='SNL134/141 assigns the5/32x1 pin to M4165. Removed unsupported M4150 hole. Added estimated M4162 cup-screw seating flat. Other shaft geometry retained.')
    metadata(old['ClutchThrowout_OperatingLever']['target'],ReconstructionNotes='Operating eye runs rearward and down, following full SNL2 orientation. Arm dimensions/profile are estimates; inherited hub, key and shaft receiver retained.')
    groups={}
    for name,parent_obj in [('ClutchSupports',doc.ClutchThrowout),('ClutchAuxiliary',doc.ClutchThrowout),('HullInterfaceContext',doc.Root)]:
        group=doc.addObject('App::Part',name);parent_obj.addObject(group);groups[name]=group
        metadata(group,QuantityRole='Nonphysical assembly container',ReconstructionNotes=datums['mounting_hypothesis'])
    identities={
        'right_bracket':('M4148','SNL37; SNL200'), 'left_bracket':('SH953A','SNL37; SNL201'),
        'right_cap':('1/2x1-3/4in hex cap screw','SNL200'), 'left_cap':('5/8x1-7/8in hex cap screw','SNL201'),
        'cup_screw':('5/8x7/8in square cup setscrew','SNL204; SNL250'),
        'aux_shaft':('SH953C','SNL37; SNL250'), 'aux_lever':('SH953B','SNL37'),
        'taper_pin':('No6x3in taper pin','SNL37; SNL142'),
        'fork':('SH953E','SNL87; SNL250'), 'fork_pin':('SH953F','SNL136'),
        'fork_cotter':('1/8x7/8in split pin','SNL136; SNL140'),
        'rod':('SH953D','SNL193'), 'rod_nut':('3/4in plain hex nut','SNL129; SNL193'),
        'floor_revision':('M1937 development revision','SNL148:026; inherited H01 plate'),
        'existing_key':('M4172','SNL37; SNL250')}
    bodies={'existing_key':doc.getObject('Def_ClutchThrowout_key')}
    for key,shape in definitions.items():
        body=doc.addObject('PartDesign::Body','Def_ClutchSupport_'+key);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedSupport').Shape=shape
        metadata(body,DefinitionId='clutch_support_'+key,OriginalMark=identities[key][0],SourceRecord=identities[key][1],
            Representation='assembly',Coverage='partial',ParameterUpdate='Regenerate clutch_support_build.py from controls',
            ReconstructionNotes='Provisional floor attachment and auxiliary arrangement. Source quantities/specified sizes retained; unprinted forms/stations/stock estimated. See source dossier. Nominal thread envelopes.')
        bodies[key]=body
    occ.append(dict(key='floor_revision',name='hull_floor_7',xyz=list(floor_base),rotation=[0,0,0,1],assembly='HullInterfaceContext'))
    for row in occ:
        obj=doc.addObject('App::Link',row['name']);groups[row['assembly']].addObject(obj);obj.setLink(bodies[row['key']])
        obj.LinkPlacement=App.Placement(App.Vector(*row['xyz']),App.Rotation(*row['rotation']))
        metadata(obj,OccurrenceId=row['name'],SourceRecord=identities[row['key']][1],
            Subsystem='HullStructure' if row['key']=='floor_revision' else 'Drivetrain',QuantityRole='One physical component')
    metadata(doc.hull_floor_7,ContextRevisionOf='hull_floor_7',IntegrationRule='Replace original floor7 when integrating; never add a second floor.')
    doc.Definitions.Visibility=False;doc.recompute()
    keys=[body.Name for key,body in bodies.items() if key!='existing_key']+[old[n]['target'].Name for n in revisions]
    native=out/'TransmissionWithClutchSupports.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));items=leaves(doc.Root);byid={i['id']:i for i in items};new=[r['name'] for r in occ]
    assert len(items)==len(byid)==len(old)+len(new)
    changed=list(revisions)
    for n,previous in before.items():
        if n in changed:continue
        i=byid[n];assert same_shape(previous[0],shape_signature(i['shape'])),n
        t,angle=placement_errors(i['shape'].Placement,previous[1]);assert t<1e-6 and angle<1e-8,n
    for n in new+changed:assert byid[n]['shape'].isValid() and len(byid[n]['shape'].Solids)==1,n
    installed=new+changed
    Part.makeCompound([doc.getObject(k).Shape for k in keys]).exportStep(str(out/'ClutchSupportDefinitions.step'))
    Part.makeCompound([byid[n]['shape'] for n in installed]).exportStep(str(out/'ClutchSupportInstallation.step'))
    write(out/'definition_order.json',keys)
    write(out/'report.json',dict(status='development_hypothesis_not_qualified',native_sha256=sha(native),parent_native_sha256=sha(pn),
        input_hashes=inputs,controls=c,inherited_controls=inherited,datums=datums,occurrences=occ,new_ids=new,
        new_mechanism_ids=[n for n in new if n!='hull_floor_7'],context_revision_ids=['hull_floor_7'],changed_ids=changed,
        exchange_ids=installed,native_occurrences=len(items),unchanged_parent_occurrences=len(old)-len(changed),
        standard_native_hashes=standard['native_hashes'],standard_assembly_modified=False,complete_throwout=False,
        complete_brake=False,complete_clutch=False,complete_tank=False,historical_mounting_proven=False,
        floor_base=list(floor_base),floor_original_signature=shape_signature(original_floor),
        headless=not App.GuiUp,freecad=App.Version(),occ=Part.OCC_VERSION,
        artifact_hashes={f.name:sha(f) for f in out.glob('*.step')}))
    print('Saved',len(items),'occurrences;',len(new)-1,'new mechanism parts, one floor revision, two parent revisions.',flush=True)
    assert sha(pn)==checkpoint['native_sha256']
finally:
    runtime.close()
