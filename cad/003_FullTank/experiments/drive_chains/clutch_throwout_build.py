"""Develop installed clutch release bearings, pins, fork levers and main shaft."""
import argparse
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent; STAGE=HERE.parents[1]; ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,default=HERE/'clutch_throwout_build')
p.add_argument('--controls',type=Path,default=HERE/'clutch_throwout_controls.json')
p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--output',str(out),'--controls',str(a.controls.resolve()),'--worker'],
            env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App, Part
    from lib.cad_build import leaves,metadata,shape_signature
    from lib.worker import same_shape,placement_errors
    from clutch_throwout_parts import parts
    App.ParamGet('User parameter:BaseApp/Preferences/Document').SetInt('CountBackupFiles',0)
    parent=HERE/'clutch_stop_band_build';pn=parent/'TransmissionWithClutchStopBand.FCStd'
    checkpoint=read(parent/'development_checkpoint.json')
    assert sha(pn)==checkpoint['native_sha256']
    source=read(HERE/'clutch_throwout_sources.json')
    for rel,h in source['source_assets'].items():assert sha(ROOT/rel)==h,rel
    c=read(a.controls)['controls']
    (out/'inputs').mkdir(exist_ok=True)
    names=['clutch_throwout_build.py','clutch_throwout_parts.py','clutch_throwout_sources.json']
    inputs={str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in names}
    for n in names:(out/'inputs'/n).write_bytes((HERE/n).read_bytes())
    (out/'inputs/clutch_throwout_controls.json').write_bytes(a.controls.read_bytes())
    inputs[str(a.controls.resolve().relative_to(ROOT))]=sha(a.controls)
    doc=App.openDocument(str(pn));old={i['id']:i for i in leaves(doc.Root)}
    before={n:(shape_signature(i['shape']),i['shape'].Placement) for n,i in old.items()}
    print('Constructing throwout bearings, pins, levers and main shaft.',flush=True)
    definitions,occ,datums=parts(c)
    group=doc.addObject('App::Part','ClutchThrowout');doc.TransmissionCore.addObject(group)
    metadata(group,Subsystem='Drivetrain',QuantityRole='Nonphysical assembly container',
        ReconstructionNotes='Partial throwout; two SKF1207 units contain inferred commercial internals. Brackets, retention, auxiliary controls and complete brake pending.')
    groups={'ClutchThrowout':group}
    for side in ['Left','Right']:
        name='ClutchThrowoutBearing'+side;g=doc.addObject('App::Part',name);group.addObject(g);groups[name]=g
        metadata(g,OriginalMark='SKF1207',SourceRecord='SNL:250:027',SourceUnitQuantity='1',
            QuantityRole='One catalogue bearing unit; count physical internal children separately',
            ReconstructionNotes='72x35x17mm envelope. Two rows transferred from modern SKF; internal geometry/count and cage construction inferred.')
    identities={
        'bearing_outer':('SKF1207 inferred outer race','SNL:250:027'),
        'bearing_inner':('SKF1207 inferred inner race','SNL:250:027'),
        'bearing_ball':('SKF1207 inferred ball','SNL:250:027'),
        'bearing_cage':('SKF1207 inferred cage','SNL:250:027'),
        'bearing_pin':('SH943A','SNL:134 pin assembly'),
        'bearing_washer':('SH943C','SNL:250:005'),
        'retainer_washer':('SH943B','SNL:250:006'),
        'pin_nut':('5/8in plain hex nut','SNL:134 pin assembly'),
        'pin_lockwasher':('5/8in lockwasher','SNL:134 pin assembly'),
        'left_lever':('M4162','SNL:250:009'),
        'right_lever':('M4163','SNL:250:010'),
        'pin_lock_screw':('M4175','SNL:202 pin locking screw assembly'),
        'pin_lock_nut':('7/16in plain hex nut','SNL:202 pin locking screw assembly'),
        'shaft':('M4150','SNL:250:015'),
        'operating_lever':('M4164','SNL:250:014'),
        'key':('M4172','SNL:250:011')}
    bodies={}
    for key,shape in definitions.items():
        body=doc.addObject('PartDesign::Body','Def_ClutchThrowout_'+key);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedThrowout').Shape=shape
        mark,rid=identities[key]
        metadata(body,DefinitionId='clutch_throwout_'+key,OriginalMark=mark,SourceRecord=rid,
            Representation='assembly',Coverage='partial',ParameterUpdate='Regenerate clutch_throwout_build.py from controls',
            ReconstructionNotes='Development geometry: see controls/source dossier for printed dimensions, transferred bearing type and inferred interfaces. Thread envelopes only.')
        bodies[key]=body
    for row in occ:
        obj=doc.addObject('App::Link',row['name']);groups[row['assembly']].addObject(obj);obj.setLink(bodies[row['key']])
        obj.LinkPlacement=App.Placement(App.Vector(*row['xyz']),App.Rotation(*row['rotation']))
        metadata(obj,OccurrenceId=row['name'],SourceRecord=identities[row['key']][1],Subsystem='Drivetrain',
            QuantityRole='One physical component; commercial internal count is inferred' if row['assembly']!='ClutchThrowout' else 'One physical component')
    keys=[body.Name for body in bodies.values()]
    doc.Definitions.Visibility=False;doc.recompute()
    native=out/'TransmissionWithClutchThrowout.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));items=leaves(doc.Root);byid={i['id']:i for i in items};new=[r['name'] for r in occ]
    assert len(items)==len(byid)==len(old)+len(new)
    for n,previous in before.items():
        i=byid[n];assert same_shape(previous[0],shape_signature(i['shape'])),n
        t,angle=placement_errors(i['shape'].Placement,previous[1]);assert t<1e-6 and angle<1e-8,n
    for n in new:assert byid[n]['shape'].isValid() and len(byid[n]['shape'].Solids)==1,n
    Part.makeCompound([doc.getObject(k).Shape for k in keys]).exportStep(str(out/'ClutchThrowoutDefinitions.step'))
    Part.makeCompound([byid[n]['shape'] for n in new]).exportStep(str(out/'ClutchThrowoutInstallation.step'))
    write(out/'definition_order.json',keys)
    report=dict(status='development_not_qualified',native_sha256=sha(native),parent_native_sha256=sha(pn),
        input_hashes=inputs,controls=c,datums=datums,occurrences=occ,new_ids=new,native_occurrences=len(items),
        unchanged_parent_occurrences=len(old),standard_assembly_modified=False,complete_throwout=False,
        complete_brake=False,complete_clutch=False,complete_tank=False,headless=not App.GuiUp,
        freecad=App.Version(),occ=Part.OCC_VERSION,artifact_hashes={f.name:sha(f) for f in out.glob('*.step')})
    write(out/'report.json',report)
    print('Saved and reopened',len(items),'physical occurrences;',len(new),'new,',len(old),'preserved.',flush=True)
    assert sha(pn)==checkpoint['native_sha256']
finally:
    runtime.close()
