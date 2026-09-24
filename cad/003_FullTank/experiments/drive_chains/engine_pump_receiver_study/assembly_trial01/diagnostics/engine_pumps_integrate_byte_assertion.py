"""Merge saved pump/driver definitions and checked receiver into one hierarchy.

This preserves the inherited global engine datum for diagnosis. The resulting
development assembly is not accepted into the standard tank while floor and
oil-manifold interfaces remain unresolved.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--receiver',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
if not a.worker:
    with (out/'build.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--receiver',str(a.receiver.resolve()),
            '--output',str(out),'--worker'],env=runtime.environment(out/'runtime'),
            stdout=log,stderr=subprocess.STDOUT).returncode)

def serialized_shapes(path):
    with zipfile.ZipFile(path) as z:
        t=ET.fromstring(z.read('Document.xml'))
        return {o.get('name'):hashlib.sha256(z.read(part.get('file'))).hexdigest()
                for o in t.findall('./ObjectData/Object')
                for part in o.findall('./Properties/Property[@name="Shape"]/Part') if part.get('file')}

try:
    import FreeCAD as App
    from lib.cad_build import leaves,metadata
    from lib.worker import placement_errors
    rr=read(a.receiver/'report.json');checked=read(a.receiver/'independent_checks.json')
    receiver=a.receiver/rr['native_file']
    assert sha(receiver)==rr['native_sha256']==checked['native_sha256']
    assert checked['local_mechanical_passed'],'Receiver must pass local checks before hierarchy integration'
    paths={key:ROOT/row['path'] for key,row in rr['parent_natives'].items()}
    reports={key:read(ROOT/row['path']) for key,row in rr['parent_reports'].items()}
    for key,path in paths.items():assert sha(path)==rr['parent_natives'][key]['sha256']
    dr,wr,orr=reports['drive'],reports['water'],reports['oil']
    def properties(source,target):
        for name in source.PropertiesList:
            if source.getGroupOfProperty(name)!='Reconstruction':continue
            kind=source.getTypeIdOfProperty(name)
            assert kind in ['App::PropertyString','App::PropertyStringList','App::PropertyBool'],(name,kind)
            if name not in target.PropertiesList:target.addProperty(kind,name,'Reconstruction')
            assert target.getTypeIdOfProperty(name)==kind,name
            setattr(target,name,getattr(source,name))
    doc=App.openDocument(str(paths['water']));old={row['id']:row for row in leaves(doc.Root)}
    assert len(old)==2247
    before={n:dict(target=row['target'].Name,placement=App.Placement(row['shape'].Placement)) for n,row in old.items()}
    del old
    driver=App.openDocument(str(paths['drive']))
    for name in read(paths['drive'].parent/'definition_order.json'):
        source=driver.getObject(name);target=doc.getObject(name)
        assert source and target and target.TypeId=='PartDesign::Body'
        target.Tip.Shape=source.Shape.copy();properties(source,target)
    for name in ['EngineLowerDistributionDrive']+[row['name'] for row in dr['assemblies']]+dr['new_ids']:
        source=driver.getObject(name);target=doc.getObject(name)
        assert source and target
        if source.TypeId=='App::Link':target.LinkPlacement=App.Placement(source.LinkPlacement)
        else:target.Placement=App.Placement(source.Placement)
        properties(source,target)
    App.closeDocument(driver.Name)
    doc.EngineWaterPump.Placement.Base=App.Vector(dr['main_apex'],0,-dr['controls']['pump_axis_drop'])
    metadata(doc.EngineWaterPump,InstallationNote='Relocated with the conditional HB45 axis drop; saved component geometry retained')
    rec=App.openDocument(str(receiver));target=doc.getObject(before['EngineCase_lower']['target'])
    target.Tip.Shape=rec.Def_EngineCase_lower.Shape.copy()
    properties(rec.Def_EngineCase_lower,target);App.closeDocument(rec.Name)
    metadata(target,ParameterUpdate='Regenerate engine_pump_receiver_build.py then engine_pumps_integrate.py',
        PumpReceiverCandidateSHA256=rr['native_sha256'])
    oil=App.openDocument(str(paths['oil']))
    pump=doc.addObject('App::Part','EngineOilPump');doc.TankLibertyEngine.addObject(pump)
    properties(oil.EngineOilPump,pump)
    pump.Placement.Base=App.Vector(orr['controls']['pump_axis_x'],0,orr['controls']['pump_mount_z'])
    pump.FrameDescription='Engine-aligned pump frame, physically applied in this development hierarchy; global installation unqualified'
    metadata(pump,QuantityRole='Nonphysical pump assembly container',Subsystem='Powerplant',Coverage='partial',
        SourceNativeSHA256=orr['native_sha256'],InstallationStatus='Local receiver checks pass; global floor and manifold circuit unresolved')
    groups={}
    for name in orr['groups']:
        assert not doc.getObject(name),name
        obj=doc.addObject('App::Part',name);pump.addObject(obj);groups[name]=obj
        obj.Placement=App.Placement(oil.getObject(name).Placement)
        metadata(obj,QuantityRole='Nonphysical oil-pump subassembly container',Subsystem='Powerplant',Coverage='partial')
    definition_names={}
    for key in orr['definition_order']:
        name='Def_EngineOilPump_'+key;assert not doc.getObject(name),name
        source=oil.getObject('Def_'+key);body=doc.addObject('PartDesign::Body',name);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedOilPump').Shape=source.Shape.copy()
        properties(source,body)
        metadata(body,DefinitionId='engine_oil_pump_'+key,OriginalMark=source.SourcePartMark,
            Representation='assembly',Subsystem='Powerplant',Coverage='partial',SourceNativeSHA256=orr['native_sha256'])
        definition_names[key]=body.Name
    for row in orr['occurrences']:
        assert not doc.getObject(row['name']),row['name']
        obj=doc.addObject('App::Link',row['name']);groups[row['assembly']].addObject(obj)
        obj.setLink(doc.getObject(definition_names[row['key']]))
        obj.LinkPlacement=App.Placement(oil.getObject(row['name']).LinkPlacement)
        properties(oil.getObject(row['name']),obj)
        metadata(obj,OccurrenceId=row['name'],Subsystem='Powerplant',QuantityRole='One physical oil-pump constituent')
    construction=doc.addObject('Part::Feature','OilPumpReliefLockCenterline');doc.Definitions.addObject(construction)
    construction.Shape=oil.ReliefLockCenterline.Shape.copy();properties(oil.ReliefLockCenterline,construction)
    construction.Visibility=False;App.closeDocument(oil.Name)
    metadata(doc.TankLibertyEngine,PumpLayoutStatus='Both pumps and revised receiver present; global engine height and oil manifold circuit unresolved',
        PumpLayoutSource='HB printed68 Plate45; conditional aviation mounting; engine_pump_layout_study/source_constraints.json')
    doc.recompute();doc.Definitions.Visibility=False
    native=out/'DrivetrainWithBothPumps.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));current={row['id']:row for row in leaves(doc.Root)}
    assert len(current)==2393
    oil_ids=[row['name'] for row in orr['occurrences']]
    changed={'EngineCase_lower',*dr['new_ids'],*wr['new_ids']}
    preserved=set(before)-changed;assert len(preserved)==2152
    old_hash,new_hash=serialized_shapes(paths['water']),serialized_shapes(native)
    for name in preserved:
        row=before[name];now=current[name]
        assert now['target'].Name==row['target'] and old_hash[row['target']]==new_hash[row['target']],name
        dt,angle=placement_errors(row['placement'],now['shape'].Placement)
        assert dt<1e-7 and angle<1e-8,name
    # All incoming oil shapes must remain the exact saved definition BReps.
    oil_hash=serialized_shapes(paths['oil'])
    assert all(oil_hash['Def_'+key]==new_hash[name] for key,name in definition_names.items())
    report=dict(status='development_hierarchy_global_installation_unqualified',native_file=native.name,native_sha256=sha(native),
        receiver_native_sha256=rr['native_sha256'],receiver_report=str((a.receiver/'report.json').resolve().relative_to(ROOT)),
        parent_natives=rr['parent_natives'],parent_reports=rr['parent_reports'],
        input_hashes={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__)),
                      str((a.receiver/'independent_checks.json').resolve().relative_to(ROOT)):sha(a.receiver/'independent_checks.json')},
        physical_occurrences=len(current),new_oil_occurrences=len(oil_ids),new_oil_definitions=len(definition_names),
        definitions=definition_names,oil_occurrences=orr['occurrences'],changed_parent_ids=sorted(changed),
        preserved_parent_ids=sorted(preserved),preserved_parent_count=len(preserved),
        engine_origin=list(doc.TankLibertyEngine.Placement.Base),oil_pose=list(doc.EngineOilPump.Placement.toMatrix().A),
        water_pose=list(doc.EngineWaterPump.Placement.toMatrix().A),inherited_floor_envelope_gap_mm=checked['inherited_floor_envelope_gap_mm'],
        source_documents_unchanged=all(sha(path)==rr['parent_natives'][key]['sha256'] for key,path in paths.items()),
        standard_assembly_modified=False,installation_qualified=False,hydraulic_circuit_qualified=False,complete_engine=False,complete_tank=False,
        pending=['Independent saved hierarchy/definition/frame verification and context checks',
                 'Receiver STEP qualification and final installed exchange after global registration',
                 'Engine/drivetrain elevation and supports, clutch, transmission, controls and chain interfaces',
                 'Oil manifold circuit, remaining wires/connections and other engine/tank systems'])
    write(out/'report.json',report);print('Saved2393occurrences;2152parentoccurrencesexactlypreserved',flush=True)
finally:
    runtime.close()
