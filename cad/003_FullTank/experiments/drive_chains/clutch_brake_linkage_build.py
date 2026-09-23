"""Develop the complete clutch-stop linkage on the saved support candidate."""
import argparse
import ast
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,default=HERE/'clutch_brake_linkage_build')
p.add_argument('--controls',type=Path,default=HERE/'clutch_brake_linkage_controls.json')
p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--output',str(out),'--controls',str(a.controls.resolve()),'--worker'],
            env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part
    from lib.cad_build import leaves,metadata,shape_signature
    from lib.worker import same_shape,placement_errors
    from clutch_brake_linkage_parts import parts
    App.ParamGet('User parameter:BaseApp/Preferences/Document').SetInt('CountBackupFiles',0)
    parent=HERE/'clutch_support_build';pn=parent/'TransmissionWithClutchSupports.FCStd'
    checkpoint=read(parent/'development_checkpoint.json');assert sha(pn)==checkpoint['native_sha256']
    pr=read(parent/'report.json');band=read(HERE/'clutch_stop_band_build/report.json')
    source=read(HERE/'clutch_brake_linkage_sources.json')
    for rel,h in source['source_assets'].items():assert sha(ROOT/rel)==h,rel
    c=read(a.controls)['controls'];sc=dict(pr['controls'],floor_top=pr['datums']['floor_top'])
    names={'clutch_brake_linkage_build.py','clutch_brake_linkage_parts.py'};pending=list(names)
    while pending:
        n=pending.pop()
        for node in ast.walk(ast.parse((HERE/n).read_text())):
            mods=[x.name for x in node.names] if isinstance(node,ast.Import) else [node.module] if isinstance(node,ast.ImportFrom) and node.module else []
            for m in mods:
                f=m+'.py'
                if (HERE/f).is_file() and f not in names:names.add(f);pending.append(f)
    names.add('clutch_brake_linkage_sources.json');(out/'inputs').mkdir(exist_ok=True)
    inputs={}
    for n in sorted(names):
        (out/'inputs'/n).write_bytes((HERE/n).read_bytes());inputs[str((HERE/n).relative_to(ROOT))]=sha(HERE/n)
    (out/'inputs/clutch_brake_linkage_controls.json').write_bytes(a.controls.read_bytes())
    inputs[str(a.controls.resolve().relative_to(ROOT))]=sha(a.controls)
    doc=App.openDocument(str(pn));old={i['id']:i for i in leaves(doc.Root)};origin=doc.TransmissionCore.Placement.Base
    before={n:(shape_signature(i['shape']),i['shape'].Placement) for n,i in old.items()}
    originals={}
    for n in ['ClutchStopBand_band','ClutchStopBand_lining','ClutchSupport_LeftBracket','ClutchThrowout_LeftLever']:
        s=old[n]['shape'].copy();s.translate(-origin);originals[n]=s
    print('Constructing anchor, carrier and complete provisional stop linkage.',flush=True)
    definitions,occ,revisions,datums,spine=parts(c,originals,band['controls'],band['datums'],sc)
    for n,s in revisions.items():
        target=old[n]['target']
        world=old[n]['shape'].Placement.multiply(target.Shape.Placement.inverse())
        core=App.Placement(-origin,App.Rotation()).multiply(world)
        local=s.copy();local.Placement=core.inverse().multiply(local.Placement)
        target.Tip.Shape=local
        metadata(target,ReconstructionNotes='Receiving revision for provisional complete clutch-stop linkage. See clutch_brake_linkage_sources.json; historical mounting and profiles remain unresolved.')
    groups={}
    for name in ['ClutchStopAnchor','ClutchStopLinkage']:
        group=doc.addObject('App::Part',name)
        owner=doc.ClutchStopBandAssembly if name=='ClutchStopAnchor' else doc.TransmissionCore
        owner.addObject(group);groups[name]=group
        metadata(group,QuantityRole='Nonphysical assembly container',ReconstructionNotes=datums['mounting_hypothesis'])
    identities={
        'anchor':('M4160','SNL8; SNL146; HB118'),'anchor_rivet':('1/4x1in button rivet','SNL8; SNL167'),
        'mount_bolt':('1/2x2-7/8in hex bolt','SNL31'),'mount_nut':('1/2in plain nut','SNL31'),
        'mount_lock':('1/2in lock washer','SNL31'),'carrier':('M4153','SNL146; SNL250'),
        'band_pin':('M4157','SNL134-135'),'band_cotter':('1/8x7/8in split pin','SNL135'),
        'eyebolt':('M4156','SNL90'),'eye_adjuster':('SH955B','SNL90; SNL125'),
        'eye_washer':('SH955A','SNL90; SNL267'),'eye_plain_nut':('1/2in plain nut','SNL90'),
        'rod':('M4151','SNL193'),'rod_nut':('SH955D','SNL193; SNL125'),
        'rod_pin':('M4152','SNL135'),'rod_cotter':('1/8x1in split pin','SNL135'),
        'bell':('SH87A','SNL77; SNL250'),'spring':('SH955C','SNL219; SNL250'),
        'bell_pin':('M4165','SNL134'),'bell_nut':('5/8in crown nut','SNL134'),
        'bell_cotter':('5/32x1in split pin','SNL134; SNL141')}
    bodies={}
    for key,s in definitions.items():
        body=doc.addObject('PartDesign::Body','Def_ClutchBrake_'+key);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedBrake').Shape=s
        metadata(body,DefinitionId='clutch_brake_'+key,OriginalMark=identities[key][0],SourceRecord=identities[key][1],
            Representation='assembly',Coverage='partial',ParameterUpdate='Regenerate clutch_brake_linkage_build.py from controls',
            ReconstructionNotes='Source identity/counts and specified fastener sizes; all unprinted profiles, stations, fits, spring and forming details estimated. Static mechanism hypothesis; nominal threads.')
        bodies[key]=body
    for row in occ:
        obj=doc.addObject('App::Link',row['name']);groups[row['assembly']].addObject(obj);obj.setLink(bodies[row['key']])
        obj.LinkPlacement=App.Placement(App.Vector(*row['xyz']),App.Rotation(*row['rotation']))
        metadata(obj,OccurrenceId=row['name'],SourceRecord=identities[row['key']][1],Subsystem='Drivetrain',QuantityRole='One physical component')
    spine.exportBrep(str(out/'spring_centerline.brep'))
    doc.Definitions.Visibility=False;doc.recompute()
    names=[b.Name for b in bodies.values()]+[old[n]['target'].Name for n in revisions]
    native=out/'TransmissionWithClutchBrake.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));byid={i['id']:i for i in leaves(doc.Root)};new=[r['name'] for r in occ];changed=list(revisions)
    assert len(byid)==len(old)+len(new)==1821
    for n,previous in before.items():
        if n in changed:continue
        i=byid[n];assert same_shape(previous[0],shape_signature(i['shape'])),n
        t,angle=placement_errors(i['shape'].Placement,previous[1]);assert t<1e-6 and angle<1e-8,n
    for n in new+changed:assert byid[n]['shape'].isValid() and len(byid[n]['shape'].Solids)==1,n
    Part.makeCompound([doc.getObject(n).Shape for n in names]).exportStep(str(out/'ClutchBrakeDefinitions.step'))
    Part.makeCompound([byid[n]['shape'] for n in new+changed]).exportStep(str(out/'ClutchBrakeInstallation.step'))
    write(out/'definition_order.json',names)
    write(out/'report.json',dict(status='development_hypothesis_not_qualified',native_sha256=sha(native),parent_native_sha256=sha(pn),
        controls=c,band_controls=band['controls'],band_datums=band['datums'],support_controls=sc,datums=datums,
        input_hashes=inputs,new_ids=new,changed_ids=changed,exchange_ids=new+changed,occurrences=occ,
        native_occurrences=len(byid),unchanged_parent_occurrences=len(old)-len(changed),new_definitions=len(definitions),
        standard_native_hashes=pr['standard_native_hashes'],artifact_hashes={f.name:sha(f) for f in out.glob('*.step')},
        standard_assembly_modified=False,historical_mounting_proven=False,complete_brake_inventory_provisional=True,
        qualified_complete_brake=False,complete_throwout=False,complete_clutch=False,complete_tank=False,
        headless=not App.GuiUp,freecad=App.Version(),occ=Part.OCC_VERSION))
    assert sha(pn)==checkpoint['native_sha256']
    print('Saved',len(byid),'occurrences;',len(new),'new pieces;',len(changed),'receiving revisions.',flush=True)
finally:
    runtime.close()
