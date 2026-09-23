"""Populate the72 catalogue engine-support children on the crossmember candidate."""
import argparse
from pathlib import Path
import subprocess
import sys
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,default=HERE/'engine_suspension_build')
p.add_argument('--controls',type=Path,default=HERE/'engine_suspension_controls.json')
p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--output',str(out),'--controls',str(a.controls.resolve()),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part
    from lib.cad_build import leaves,metadata,shape_signature
    from lib.worker import same_shape,placement_errors
    from engine_suspension_parts import parts
    App.ParamGet('User parameter:BaseApp/Preferences/Document').SetInt('CountBackupFiles',0)
    parent=HERE/'engine_crossmember_build';pn=parent/'DrivetrainWithEngineCrossmembers.FCStd';pr=read(parent/'report.json')
    assert sha(pn)==pr['native_sha256'];c=read(a.controls)['controls'];cc=pr['controls']
    source=read(HERE/'engine_suspension_sources.json')
    for rel,h in source['source_assets'].items():assert sha(ROOT/rel)==h,rel
    inputs={};(out/'inputs').mkdir(exist_ok=True)
    for path in [Path(__file__),HERE/'engine_suspension_parts.py',HERE/'engine_crossmember_parts.py',HERE/'engine_suspension_sources.json',a.controls.resolve()]:
        (out/'inputs'/path.name).write_bytes(path.read_bytes());inputs[str(path.relative_to(ROOT))]=sha(path)
    doc=App.openDocument(str(pn));old={i['id']:i for i in leaves(doc.Root)}
    before={n:(shape_signature(i['shape']),i['shape'].Placement) for n,i in old.items()}
    axis_z=doc.TransmissionCore.Placement.Base.z
    originals={}
    for n,station in [('EngineFrame_RearChannel',cc['rear_x']),('EngineFrame_FrontCleat',cc['front_x'])]:
        s=old[n]['shape'].copy();s.translate(-App.Vector(station,0,cc['floor_top']));originals[n]=s
    print('Constructing remaining61 engine-support components and two receiving revisions.',flush=True)
    definitions,occ,revisions,datums=parts(c,cc,axis_z,originals)
    for n,s in revisions.items():
        target=old[n]['target'];world=old[n]['shape'].Placement.multiply(target.Shape.Placement.inverse())
        s.translate(App.Vector(cc['rear_x'] if n=='EngineFrame_RearChannel' else cc['front_x'],0,cc['floor_top']))
        s.Placement=world.inverse().multiply(s.Placement);target.Tip.Shape=s
        metadata(target,ReconstructionNotes='Receiving revision for provisional three-point engine suspension. Rear upper-flange taper and front cleat upright are estimated; source placement remains unresolved.')
    groups={}
    for name in ['LongitudinalSupports','FrontSuspension','LeftRearSuspension','RightRearSuspension']:
        g=doc.addObject('App::Part',name);doc.EngineMounts.addObject(g);groups[name]=g
        metadata(g,QuantityRole='Nonphysical assembly container',Coverage='partial',Subsystem='Powerplant',ReconstructionNotes='Static support hypothesis; source hardware quantities, estimated castings and joint allocation.')
    identities={
        'left_rail':('M179','SNL242; HB205 handedness conflict'),
        'right_rail':('M178','SNL242; HB205 handedness conflict'),
        'left_bracket':('M182','SNL37; SNL242'),
        'right_bracket':('M183','SNL37; SNL242'),
        'front_bracket':('M184','SNL37 single-point; SNL242 double-point conflict'),
        'rear_packing':('M188','SNL131; HB205; SNL242 wording conflict'),
        'front_packing':('M187','SNL131; HB205; SNL242'),
        'bevel_washer':('M190','SNL267; SNL242'),
        'half_bolt':('1/2x1-3/4in hex bolt','SNL:31:009; SNL242'),
        'half_nut':('1/2in plain nut','SNL:31:009; SNL242'),
        'half_lock':('1/2in lock washer','SNL:31:009; SNL200; SNL242'),
        'rear_bolt':('5/8x2-1/2in hex bolt','SNL:33:001; SNL242'),
        'rear_nut':('5/8in plain nut','SNL:33:001; SNL242'),
        'rear_lock':('5/8in lock washer','SNL:33:001; SNL242'),
        'pivot_bolt':('3/4x2-1/2in hex bolt','SNL:33:010; SNL242'),
        'pivot_nut':('3/4in plain nut','SNL:33:010; SNL242'),
        'pivot_lock':('3/4in lock washer','SNL:33:010; SNL242'),
        'cap':('1/2x1-1/2in hex cap screw','SNL:200:013; SNL242')}
    bodies={}
    for key,s in definitions.items():
        body=doc.addObject('PartDesign::Body','Def_EngineSuspension_'+key);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedSuspension').Shape=s
        metadata(body,DefinitionId='engine_suspension_'+key,OriginalMark=identities[key][0],SourceRecord=identities[key][1],Representation='assembly',Coverage='partial',
            ParameterUpdate='Regenerate engine_suspension_build.py from controls',
            ReconstructionNotes='Source identities/counts and nominal hardware; conditional17in aviation interface. Castings, channels, shims, joint allocation, threads, heads, split washers, stock and all unprinted coordinates are estimates.')
        bodies[key]=body
    for row in occ:
        obj=doc.addObject('App::Link',row['name']);groups[row['assembly']].addObject(obj);obj.setLink(bodies[row['key']])
        obj.LinkPlacement=App.Placement(App.Vector(*row['xyz']),App.Rotation(*row['rotation']))
        metadata(obj,OccurrenceId=row['name'],Subsystem='Powerplant',QuantityRole='One physical component')
    doc.Definitions.Visibility=False;doc.recompute()
    names=[b.Name for b in bodies.values()]+[old[n]['target'].Name for n in revisions]
    native=out/'DrivetrainWithEngineSuspension.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));byid={i['id']:i for i in leaves(doc.Root)};new=[r['name'] for r in occ];changed=list(revisions)
    assert len(byid)==len(old)+len(new)==1909
    for n,(sig,pl) in before.items():
        if n in changed:continue
        assert same_shape(sig,shape_signature(byid[n]['shape'])),n
        t,ang=placement_errors(pl,byid[n]['shape'].Placement);assert t<1e-6 and ang<1e-8,n
    for n in new+changed:assert byid[n]['shape'].isValid() and len(byid[n]['shape'].Solids)==1,n
    Part.makeCompound([doc.getObject(n).Shape for n in names]).exportStep(str(out/'EngineSuspensionDefinitions.step'))
    Part.makeCompound([byid[n]['shape'] for n in new+changed]).exportStep(str(out/'EngineSuspensionInstallation.step'))
    write(out/'definition_order.json',names)
    write(out/'report.json',dict(status='development_hypothesis_not_qualified',native_sha256=sha(native),parent_native_sha256=sha(pn),
        controls=c,crossmember_controls=cc,crankshaft_axis_z=axis_z,datums=datums,input_hashes=inputs,new_ids=new,changed_ids=changed,exchange_ids=new+changed,
        occurrences=occ,native_occurrences=len(byid),new_definitions=len(definitions),unchanged_parent_occurrences=len(old)-len(changed),
        standard_native_hashes=pr['standard_native_hashes'],standard_assembly_modified=False,source_inventory=source['scope'],
        support_catalogue_children_populated=True,historical_mounting_proven=False,engine_mounting_complete=False,complete_engine=False,complete_tank=False,
        artifact_hashes={f.name:sha(f) for f in out.glob('*.step')},headless=not App.GuiUp,freecad=App.Version(),occ=Part.OCC_VERSION))
    assert sha(pn)==pr['native_sha256']
    print('Saved1909 physical occurrences;61 new and2 revised;1846 preserved.',flush=True)
finally:
    runtime.close()
